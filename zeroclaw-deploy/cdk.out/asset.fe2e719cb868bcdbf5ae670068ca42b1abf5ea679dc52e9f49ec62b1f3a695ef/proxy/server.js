/**
 * Customer Gateway Proxy — ZeroClaw Edition
 *
 * Simplified proxy between the customer portal (React frontend) and
 * ZeroClaw gateway. No RPC handshake needed — ZeroClaw uses a direct
 * message-based WebSocket protocol.
 *
 * Customer portal ↔ ws://<ip>:3050?token=xxx
 * Proxy ↔ ws://127.0.0.1:18789?token=xxx&session_id=yyy
 *
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
const ZEROCLAW_WS_URL = process.env.ZEROCLAW_WS_URL || 'ws://127.0.0.1:18789';
const ZEROCLAW_AUTH_TOKEN = process.env.ZEROCLAW_AUTH_TOKEN || '';
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
    backend: 'zeroclaw',
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
  const connId = uuidv4();
  let sessionId = null;
  let zeroclawWs = null;
  let responseBuffer = '';

  console.log(`[Proxy] Customer connected: ${customerId}`);

  // --- Per-connection cost tracking ---
  let orchestratorTotals = { total_cost: 0, input_tokens: 0, output_tokens: 0 };

  // --- Send to customer helper ---
  function toClient(msg) {
    if (clientWs.readyState === WebSocket.OPEN) {
      clientWs.send(JSON.stringify(msg));
    }
  }

  // --- Connect to ZeroClaw gateway for a session ---
  function connectToZeroClaw(sid) {
    if (zeroclawWs && zeroclawWs.readyState === WebSocket.OPEN) {
      zeroclawWs.close();
    }

    sessionId = sid;
    const params = new URLSearchParams();
    if (ZEROCLAW_AUTH_TOKEN) params.set('token', ZEROCLAW_AUTH_TOKEN);
    params.set('session_id', sessionId);
    const wsUrl = `${ZEROCLAW_WS_URL}?${params.toString()}`;

    try {
      zeroclawWs = new WebSocket(wsUrl);
    } catch (err) {
      toClient({ type: 'error', message: 'Failed to connect to backend' });
      return;
    }

    zeroclawWs.on('open', () => {
      console.log(`[Proxy] ZeroClaw connected for ${customerId} session=${sessionId}`);
      toClient({ type: 'connection_established', customerId, sessionId });
    });

    zeroclawWs.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());
        handleZeroClawMessage(msg);
      } catch (err) {
        console.error(`[Proxy] Parse error from ZeroClaw:`, err.message);
      }
    });

    zeroclawWs.on('close', (code, reason) => {
      console.log(`[Proxy] ZeroClaw closed for ${customerId} code=${code}`);
      if (clientWs.readyState === WebSocket.OPEN) {
        toClient({ type: 'error', message: 'Backend disconnected' });
      }
    });

    zeroclawWs.on('error', (err) => {
      console.error(`[Proxy] ZeroClaw error for ${customerId}:`, err.message);
    });

    activeConnections.set(connId, { clientWs, zeroclawWs, customerId, sessionId });
  }

  // --- Handle ZeroClaw -> Customer messages ---
  function handleZeroClawMessage(msg) {
    switch (msg.type) {
      // Streaming text chunks
      case 'chunk': {
        responseBuffer += msg.content || '';
        toClient({ type: 'chat_typing', isTyping: true });
        toClient({
          type: 'chat_stream',
          chunk: msg.content || '',
          is_complete: false,
        });
        break;
      }

      // Tool call notification
      case 'tool_call': {
        toClient({
          type: 'tool_use_block',
          data: {
            id: msg.id || uuidv4(),
            tool_name: msg.name || 'unknown',
            tool_input: msg.input || {},
            timestamp: Date.now(),
          },
        });
        break;
      }

      // Tool result
      case 'tool_result': {
        toClient({
          type: 'agent_log',
          data: {
            message: `Tool ${msg.name || 'unknown'}: ${(msg.output || '').slice(0, 200)}`,
            level: msg.error ? 'error' : 'info',
          },
        });
        break;
      }

      // Thinking blocks
      case 'thinking': {
        toClient({
          type: 'thinking_block',
          data: {
            thinking: msg.content || '',
            timestamp: Date.now(),
          },
        });
        break;
      }

      // Response complete
      case 'done': {
        const fullResponse = msg.full_response || responseBuffer;
        toClient({
          type: 'orchestrator_chat',
          data: {
            sender: 'orchestrator',
            content: fullResponse,
            timestamp: Date.now(),
          },
        });
        toClient({ type: 'chat_stream', chunk: '', is_complete: true });
        toClient({ type: 'chat_typing', isTyping: false });

        // Accumulate usage if provided
        if (msg.usage) {
          const inputTok = msg.usage.input_tokens || 0;
          const outputTok = msg.usage.output_tokens || 0;
          orchestratorTotals.input_tokens += inputTok;
          orchestratorTotals.output_tokens += outputTok;
          // Rough cost: use DeepSeek pricing ($0.27/M input, $1.10/M output)
          orchestratorTotals.total_cost += (inputTok * 0.27 + outputTok * 1.10) / 1_000_000;
          toClient({
            type: 'orchestrator_updated',
            orchestrator: { ...orchestratorTotals },
          });
        }

        responseBuffer = '';
        break;
      }

      // Error from gateway
      case 'error': {
        toClient({ type: 'error', message: msg.message || 'Backend error' });
        break;
      }

      default: {
        // Forward unknown types as agent logs
        toClient({
          type: 'agent_log',
          data: { message: `zeroclaw:${msg.type}`, level: 'info' },
        });
      }
    }
  }

  // --- Start default session on connect ---
  const defaultSessionId = `customer:${customerId}:${Date.now()}`;
  connectToZeroClaw(defaultSessionId);

  // --- Handle customer -> gateway messages ---
  clientWs.on('message', (data) => {
    if (!checkRateLimit(customerId)) {
      toClient({ type: 'error', message: 'Rate limit exceeded. Please wait.' });
      return;
    }

    try {
      const msg = JSON.parse(data.toString());

      switch (msg.type) {
        // Customer sends a chat message
        case 'user_message': {
          if (!zeroclawWs || zeroclawWs.readyState !== WebSocket.OPEN) {
            toClient({ type: 'error', message: 'Not connected to backend' });
            return;
          }
          responseBuffer = '';
          zeroclawWs.send(JSON.stringify({
            type: 'message',
            content: msg.content || '',
          }));
          toClient({
            type: 'agent_log',
            data: { message: `You: ${(msg.content || '').slice(0, 80)}`, level: 'info' },
          });
          break;
        }

        // Start a new session
        case 'start_session': {
          const newSessionId = `customer:${customerId}:${Date.now()}`;
          connectToZeroClaw(newSessionId);
          toClient({
            type: 'session_started',
            sessionId: newSessionId,
            title: msg.skill || 'Planning Session',
            sessionType: msg.sessionType || 'planning',
          });
          if (msg.initialMessage) {
            // Wait for connection to open, then send
            const waitAndSend = () => {
              if (zeroclawWs.readyState === WebSocket.OPEN) {
                zeroclawWs.send(JSON.stringify({
                  type: 'message',
                  content: msg.initialMessage,
                }));
              } else {
                setTimeout(waitAndSend, 100);
              }
            };
            waitAndSend();
          }
          break;
        }

        // Load/switch to existing session
        case 'load_session': {
          connectToZeroClaw(msg.sessionId);
          break;
        }

        // List sessions — not supported in ZeroClaw direct mode
        case 'list_sessions': {
          toClient({
            type: 'session_list',
            sessions: sessionId ? [{
              id: sessionId,
              title: 'Current Session',
              status: 'active',
              createdAt: new Date().toISOString(),
            }] : [],
          });
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
    if (zeroclawWs && zeroclawWs.readyState === WebSocket.OPEN) {
      zeroclawWs.close();
    }
  });

  clientWs.on('error', (err) => {
    console.error(`[Proxy] Client error for ${customerId}:`, err.message);
  });
});

// ---------- Start ----------
server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Proxy] Customer Gateway Proxy (ZeroClaw) running on port ${PORT}`);
  console.log(`[Proxy] ZeroClaw backend: ${ZEROCLAW_WS_URL}`);
  console.log(`[Proxy] Tokens loaded: ${Object.keys(tokens).length}`);
});
