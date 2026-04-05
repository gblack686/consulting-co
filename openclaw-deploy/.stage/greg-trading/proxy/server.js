/**
 * Customer Gateway Proxy
 *
 * Sits between the customer portal (React frontend) and the OpenClaw
 * gateway running on localhost:18789. Handles:
 *   - Token validation (simple link tokens for MVP)
 *   - Gateway protocol handshake (connect.challenge -> connect -> hello-ok)
 *   - Translates frontend messages into gateway req frames (chat.send, sessions.list, etc.)
 *   - Translates gateway events back into frontend-friendly messages
 *   - Agent identity tracking (registry, lifecycle, cost accumulation)
 *   - Rate limiting per customer
 *
 * Deploy on EC2 as a systemd service.
 * Port: 3050
 */

const http = require('http');
const express = require('express');
const { WebSocketServer, WebSocket } = require('ws');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

// ---------- Config ----------
const PORT = process.env.PORT || 3050;
const OPENCLAW_WS_URL = process.env.OPENCLAW_WS_URL || 'ws://127.0.0.1:18789';
const OPENCLAW_AUTH_TOKEN = process.env.OPENCLAW_AUTH_TOKEN || '';
const TOKENS_FILE = process.env.TOKENS_FILE || path.join(__dirname, 'tokens.json');
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_MESSAGES = 30;

// ---------- Token Store ----------
let tokens = {};

function loadTokens() {
  try {
    if (fs.existsSync(TOKENS_FILE)) {
      tokens = JSON.parse(fs.readFileSync(TOKENS_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('[Proxy] Failed to load tokens:', err.message);
    tokens = {};
  }
}

function saveTokens() {
  try {
    fs.writeFileSync(TOKENS_FILE, JSON.stringify(tokens, null, 2));
  } catch (err) {
    console.error('[Proxy] Failed to save tokens:', err.message);
  }
}

function generateToken(customerId, meta = {}) {
  const token = uuidv4();
  tokens[token] = {
    customerId,
    createdAt: new Date().toISOString(),
    expiresAt: meta.expiresAt || null,
    ...meta,
  };
  saveTokens();
  return token;
}

function validateToken(token) {
  if (!token) return null;
  const entry = tokens[token];
  if (!entry) return null;
  if (entry.expiresAt && new Date(entry.expiresAt) < new Date()) return null;
  return entry;
}

loadTokens();

// ---------- Rate Limiter ----------
const rateLimitMap = new Map();

function checkRateLimit(customerId) {
  const now = Date.now();
  let entry = rateLimitMap.get(customerId);
  if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW_MS) {
    entry = { windowStart: now, count: 0 };
    rateLimitMap.set(customerId, entry);
  }
  entry.count++;
  return entry.count <= RATE_LIMIT_MAX_MESSAGES;
}

// ---------- Internal Event Filtering ----------
const INTERNAL_EVENTS = new Set([
  'tick', 'connect.challenge',
]);

const INTERNAL_SESSION_PREFIXES = [
  'telegram:', 'discord:', 'cron:',
];

// ---------- Express App (health + admin) ----------
const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    connections: wss ? wss.clients.size : 0,
  });
});

app.post('/admin/tokens', (req, res) => {
  const { customerId, expiresInHours } = req.body;
  if (!customerId) return res.status(400).json({ error: 'customerId required' });
  const expiresAt = expiresInHours
    ? new Date(Date.now() + expiresInHours * 3600000).toISOString()
    : null;
  const token = generateToken(customerId, { expiresAt });
  res.json({ token, customerId, expiresAt });
});

app.get('/admin/tokens', (req, res) => {
  res.json(tokens);
});

// ---------- Dashboard Static Files ----------
const dashboardDir = path.join(__dirname, 'dashboard');
if (fs.existsSync(dashboardDir)) {
  app.use(express.static(dashboardDir));
  // SPA fallback: serve index.html for non-API routes
  app.get('*', (req, res) => {
    res.sendFile(path.join(dashboardDir, 'index.html'));
  });
  console.log('[Proxy] Serving dashboard from', dashboardDir);
}

// ---------- HTTP Server + WebSocket ----------
const server = http.createServer(app);
const wss = new WebSocketServer({ server });
const activeConnections = new Map();

wss.on('connection', (clientWs, req) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const token = url.searchParams.get('token');

  const tokenData = validateToken(token);
  if (!tokenData) {
    clientWs.send(JSON.stringify({ type: 'error', message: 'Invalid or expired token' }));
    clientWs.close(4001, 'Unauthorized');
    return;
  }

  const { customerId } = tokenData;
  console.log(`[Proxy] Customer connected: ${customerId}`);

  // --- Per-connection state ---
  let openclawWs;
  try {
    openclawWs = new WebSocket(OPENCLAW_WS_URL);
  } catch (err) {
    clientWs.send(JSON.stringify({ type: 'error', message: 'Failed to connect to backend' }));
    clientWs.close(4002, 'Backend unavailable');
    return;
  }

  const connId = uuidv4();
  let gatewayReady = false;
  let requestIdCounter = 0;
  let sessionKey = null; // current active session on the gateway
  const pendingRequests = new Map(); // reqId -> { method, resolve }

  // --- Agent Registry (per-connection) ---
  const agentRegistry = new Map(); // agentId -> AgentData
  let agentIdCounter = 0;
  let orchestratorTotals = { total_cost: 0, input_tokens: 0, output_tokens: 0 };

  function resolveAgent(payload) {
    const rawId = payload.agentId || payload.runId || payload.data?.agentId || 'default';
    const agentId = String(rawId);

    if (agentRegistry.has(agentId)) {
      return agentRegistry.get(agentId);
    }

    // New agent — register it
    agentIdCounter++;
    const name = payload.data?.agentName || payload.agentName || `Agent-${agentIdCounter}`;
    const model = payload.data?.model || payload.model || 'claude-sonnet';
    const agent = {
      id: agentId,
      name,
      status: 'idle',
      model,
      inputTokens: 0,
      outputTokens: 0,
      totalCost: 0,
      task: payload.data?.task || '',
      createdAt: Date.now(),
    };
    agentRegistry.set(agentId, agent);

    toClient({ type: 'agent_created', agent: { ...agent } });
    console.log(`[Proxy] Agent registered: ${agentId} (${name})`);
    emitOrchestratorUpdated();
    return agent;
  }

  function updateAgentStatus(agentId, status) {
    const agent = agentRegistry.get(agentId);
    if (!agent) return;
    agent.status = status;
    toClient({ type: 'agent_updated', agent: { ...agent } });
  }

  function accumulateUsage(agentId, usage) {
    if (!usage) return;
    const agent = agentRegistry.get(agentId);
    const inputTok = usage.input_tokens || usage.inputTokens || 0;
    const outputTok = usage.output_tokens || usage.outputTokens || 0;
    if (agent) {
      agent.inputTokens += inputTok;
      agent.outputTokens += outputTok;
      // Rough cost estimate: $3/M input, $15/M output (Sonnet pricing)
      agent.totalCost += (inputTok * 3 + outputTok * 15) / 1_000_000;
      toClient({ type: 'agent_updated', agent: { ...agent } });
    }
    orchestratorTotals.input_tokens += inputTok;
    orchestratorTotals.output_tokens += outputTok;
    orchestratorTotals.total_cost += (inputTok * 3 + outputTok * 15) / 1_000_000;
    emitOrchestratorUpdated();
  }

  function emitOrchestratorUpdated() {
    let activeCount = 0;
    for (const a of agentRegistry.values()) {
      if (a.status === 'executing' || a.status === 'waiting') activeCount++;
    }
    toClient({
      type: 'orchestrator_updated',
      orchestrator: {
        ...orchestratorTotals,
        agent_count: agentRegistry.size,
        active_count: activeCount,
      },
    });
  }

  activeConnections.set(connId, { clientWs, openclawWs, customerId });

  // --- Gateway request helper ---
  function gwSend(method, params = {}) {
    const reqId = String(++requestIdCounter);
    const frame = { type: 'req', id: reqId, method, params };
    if (openclawWs.readyState === WebSocket.OPEN) {
      openclawWs.send(JSON.stringify(frame));
    }
    return reqId;
  }

  // --- Send to customer helper ---
  function toClient(msg) {
    if (clientWs.readyState === WebSocket.OPEN) {
      clientWs.send(JSON.stringify(msg));
    }
  }

  // --- Gateway connect handshake ---
  function sendGatewayConnect() {
    const reqId = String(++requestIdCounter);
    openclawWs.send(JSON.stringify({
      type: 'req',
      id: reqId,
      method: 'connect',
      params: {
        minProtocol: 3,
        maxProtocol: 3,
        client: {
          id: 'gateway-client',
          displayName: `Customer Portal (${customerId})`,
          version: '1.0.0',
          platform: 'linux',
          mode: 'backend',
        },
        caps: ['tool-events'],
        auth: OPENCLAW_AUTH_TOKEN ? { token: OPENCLAW_AUTH_TOKEN } : undefined,
        role: 'operator',
        scopes: ['operator.admin'],
      },
    }));
    pendingRequests.set(reqId, { method: 'connect' });
    console.log(`[Proxy] Sent gateway connect for ${customerId}`);
  }

  // --- Handle gateway -> customer messages ---
  openclawWs.on('open', () => {
    console.log(`[Proxy] Upstream open for ${customerId}, waiting for challenge...`);
  });

  openclawWs.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());

      // --- Protocol: events ---
      if (msg.type === 'event') {
        if (msg.event === 'connect.challenge') {
          sendGatewayConnect();
          return;
        }
        if (INTERNAL_EVENTS.has(msg.event)) return;

        const p = msg.payload || {};

        // --- Agent stream events ---
        if (msg.event === 'agent') {
          const stream = p.stream;
          const phase = p.data?.phase;

          // Resolve agent identity for all agent events
          const agent = resolveAgent(p);
          const agentId = agent.id;
          const agentName = agent.name;

          // Accumulate usage if present
          if (p.data?.usage) {
            accumulateUsage(agentId, p.data.usage);
          }

          // Streaming text from assistant — use as typing indicator only
          if (stream === 'assistant' && p.data?.delta) {
            toClient({ type: 'chat_typing', isTyping: true });
            return;
          }

          // Thinking blocks
          if (stream === 'thinking' && p.data?.thinking) {
            toClient({
              type: 'thinking_block',
              data: {
                id: p.runId,
                thinking: p.data.thinking,
                timestamp: p.ts,
                agentId,
                agentName,
              },
            });
            return;
          }

          // Tool use events
          if (stream === 'tool_use') {
            toClient({
              type: 'tool_use_block',
              data: {
                id: p.data?.toolUseId || p.runId,
                tool_name: p.data?.name || p.data?.toolName || 'unknown',
                tool_input: p.data?.input || p.data?.toolInput,
                timestamp: p.ts,
                agentId,
                agentName,
              },
            });
            return;
          }

          // Lifecycle: agent start/end
          if (stream === 'lifecycle') {
            if (phase === 'start') {
              updateAgentStatus(agentId, 'executing');
              toClient({ type: 'chat_typing', isTyping: true });
            }
            if (phase === 'end') {
              updateAgentStatus(agentId, 'complete');
              toClient({ type: 'chat_stream', chunk: '', is_complete: true });
              toClient({ type: 'chat_typing', isTyping: false });
            }
            toClient({
              type: 'agent_log',
              data: {
                message: phase === 'start' ? `${agentName} thinking...` : `${agentName} finished`,
                level: phase === 'end' ? 'SUCCESS' : 'info',
                agentId,
                agentName,
              },
            });
            return;
          }

          // Generic agent event — log it
          toClient({
            type: 'agent_log',
            data: { message: `${agentName}:${stream || 'unknown'}`, level: 'info', agentId, agentName },
          });
          return;
        }

        // --- Chat events (final/delta messages) ---
        if (msg.event === 'chat') {
          const state = p.state; // "delta" or "final"
          const content = p.message?.content;
          if (!content) return;

          // Extract text from content blocks
          const text = Array.isArray(content)
            ? content.filter(b => b.type === 'text').map(b => b.text).join('')
            : typeof content === 'string' ? content : '';

          // Try to resolve agent for chat messages too
          const chatAgentId = p.agentId || p.runId || null;
          const chatAgent = chatAgentId ? agentRegistry.get(String(chatAgentId)) : null;

          if (state === 'final' && text) {
            toClient({
              type: 'orchestrator_chat',
              data: {
                sender: 'orchestrator',
                content: text,
                timestamp: p.message?.timestamp || Date.now(),
                agentId: chatAgent?.id || null,
                agentName: chatAgent?.name || null,
              },
            });
          }
          return;
        }

        // --- Health events — skip flooding ---
        if (msg.event === 'health' || msg.event === 'cron') return;

        // --- Generic events ---
        toClient({
          type: 'agent_log',
          data: {
            message: msg.event,
            content: msg.event,
            level: 'info',
          },
        });
        return;
      }

      // --- Protocol: responses ---
      if (msg.type === 'res') {
        const pending = pendingRequests.get(msg.id);
        pendingRequests.delete(msg.id);
        const method = pending?.method || 'unknown';

        // Connect response
        if (method === 'connect') {
          if (msg.ok) {
            gatewayReady = true;
            console.log(`[Proxy] Gateway ready for ${customerId}`);
            toClient({ type: 'connection_established', customerId });
          } else {
            console.error(`[Proxy] Gateway connect REJECTED:`, msg.error?.message);
            toClient({ type: 'error', message: msg.error?.message || 'Gateway connect failed' });
          }
          return;
        }

        // sessions.list response
        if (method === 'sessions.list') {
          const sessions = (msg.payload?.sessions || [])
            .filter(s => !INTERNAL_SESSION_PREFIXES.some(p => (s.key || '').startsWith(p)))
            .map(s => ({
              id: s.key,
              title: s.label || s.derivedTitle || s.key,
              status: s.active ? 'active' : 'idle',
              createdAt: s.createdAt,
              updatedAt: s.lastActivityAt,
            }));
          toClient({ type: 'session_list', sessions });
          return;
        }

        // chat.send response (accepted / final)
        if (method === 'chat.send') {
          if (!msg.ok) {
            toClient({ type: 'error', message: msg.error?.message || 'Chat send failed' });
          }
          return;
        }

        // chat.history response
        if (method === 'chat.history') {
          const entries = msg.payload?.entries || [];
          for (const entry of entries) {
            if (entry.role === 'assistant') {
              toClient({
                type: 'orchestrator_chat',
                data: {
                  sender: 'orchestrator',
                  content: entry.content || '',
                  timestamp: entry.ts,
                },
              });
            }
          }
          return;
        }

        // Generic response — log if error
        if (!msg.ok) {
          console.warn(`[Proxy] Request ${method} failed:`, msg.error?.message);
        }
        return;
      }

      // --- Anything else: try to forward if customer-visible ---
      if (msg.type === 'chat_stream' || msg.type === 'chat_typing') {
        toClient(msg);
        return;
      }

    } catch (err) {
      console.error(`[Proxy] Parse error:`, err.message);
    }
  });

  openclawWs.on('close', (code, reason) => {
    console.log(`[Proxy] OpenClaw closed for ${customerId} code=${code} reason=${reason?.toString() || 'none'}`);
    toClient({ type: 'error', message: 'Backend disconnected' });
  });

  openclawWs.on('error', (err) => {
    console.error(`[Proxy] OpenClaw error for ${customerId}:`, err.message);
  });

  // --- Handle customer -> gateway messages ---
  clientWs.on('message', (data) => {
    if (!checkRateLimit(customerId)) {
      toClient({ type: 'error', message: 'Rate limit exceeded. Please wait.' });
      return;
    }
    if (!gatewayReady) {
      toClient({ type: 'error', message: 'Gateway not ready yet, please wait.' });
      return;
    }

    try {
      const msg = JSON.parse(data.toString());

      switch (msg.type) {
        // Customer sends a chat message
        case 'user_message': {
          const key = sessionKey || `customer:${customerId}`;
          const reqId = gwSend('chat.send', {
            sessionKey: key,
            message: msg.content || '',
            idempotencyKey: uuidv4(),
          });
          pendingRequests.set(reqId, { method: 'chat.send' });

          // Echo back as agent_log
          toClient({
            type: 'agent_log',
            data: { message: `You: ${(msg.content || '').slice(0, 80)}`, level: 'info' },
          });
          break;
        }

        // Start a new session
        case 'start_session': {
          sessionKey = `customer:${customerId}:${Date.now()}`;
          toClient({
            type: 'session_started',
            sessionId: sessionKey,
            title: msg.skill || 'Planning Session',
            sessionType: msg.sessionType || 'planning',
          });

          // If there's an initial message, send it
          if (msg.initialMessage) {
            const reqId = gwSend('chat.send', {
              sessionKey,
              message: msg.initialMessage,
              idempotencyKey: uuidv4(),
            });
            pendingRequests.set(reqId, { method: 'chat.send' });
          }
          break;
        }

        // Load/switch to existing session
        case 'load_session': {
          sessionKey = msg.sessionId;
          const reqId = gwSend('chat.history', {
            sessionKey: msg.sessionId,
            limit: 50,
          });
          pendingRequests.set(reqId, { method: 'chat.history' });
          break;
        }

        // List sessions
        case 'list_sessions': {
          const reqId = gwSend('sessions.list', {
            includeLastMessage: true,
            includeDerivedTitles: true,
            limit: 50,
          });
          pendingRequests.set(reqId, { method: 'sessions.list' });
          break;
        }

        default:
          console.log(`[Proxy] Unknown client message type: ${msg.type}`);
      }
    } catch (err) {
      console.error(`[Proxy] Client message parse error:`, err.message);
    }
  });

  clientWs.on('close', () => {
    console.log(`[Proxy] Customer disconnected: ${customerId}`);
    activeConnections.delete(connId);
    if (openclawWs.readyState === WebSocket.OPEN) {
      openclawWs.close();
    }
  });

  clientWs.on('error', (err) => {
    console.error(`[Proxy] Client error for ${customerId}:`, err.message);
  });
});

// ---------- Start ----------
server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Proxy] Customer Gateway Proxy running on port ${PORT}`);
  console.log(`[Proxy] OpenClaw backend: ${OPENCLAW_WS_URL}`);
  console.log(`[Proxy] Tokens loaded: ${Object.keys(tokens).length}`);
});
