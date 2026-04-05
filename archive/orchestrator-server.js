const WebSocket = require('ws');
const express = require('express');
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

// Session storage
const sessions = new Map();

console.log('Claude Code Orchestrator starting...');

// WebSocket connection handler
wss.on('connection', (ws, req) => {
  const clientIp = req.socket.remoteAddress;
  console.log('New WebSocket connection from', clientIp);

  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data);
      console.log('Received message:', message.type);

      switch (message.type) {
        case 'start_session':
          handleStartSession(ws, message);
          break;
        case 'user_message':
          handleUserMessage(ws, message);
          break;
        case 'end_session':
          handleEndSession(ws, message);
          break;
        default:
          ws.send(JSON.stringify({ type: 'error', error: 'Unknown message type' }));
      }
    } catch (error) {
      console.error('Error handling message:', error);
      ws.send(JSON.stringify({ type: 'error', error: error.message }));
    }
  });

  ws.on('close', () => {
    console.log('WebSocket connection closed');
    // Clean up any sessions associated with this connection
    for (const [sessionId, session] of sessions.entries()) {
      if (session.ws === ws) {
        console.log('Cleaning up session:', sessionId);
        cleanupSession(sessionId);
      }
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

function handleStartSession(ws, message) {
  const sessionId = message.sessionId || uuidv4();
  const { customerId, context, model, permissionMode, initialPrompt } = message;

  console.log(`Starting session ${sessionId} for customer ${customerId}`);

  // Build Claude Code command
  const args = [
    initialPrompt || "Hello! I'm ready to help you plan your project. What would you like to build?", // Initial prompt
    '-p',
    '--verbose',
    '--output-format', 'stream-json',
    '--include-partial-messages'
  ];

  if (model) {
    args.push('--model', model);
  }

  if (permissionMode) {
    args.push('--permission-mode', permissionMode);
  } else {
    // Default to plan mode for customer-facing
    args.push('--permission-mode', 'plan');
  }

  console.log('Spawning claude with args:', args.slice(1).join(' ')); // Don't log the prompt

  // Spawn Claude Code process
  const claudeProcess = spawn('claude', args, {
    cwd: '/home/ubuntu',
    env: { ...process.env }
  });

  // Store session
  sessions.set(sessionId, {
    sessionId,
    customerId,
    ws,
    process: claudeProcess,
    startTime: new Date(),
    messages: [],
    buffer: '',
    isFirstMessage: false // We already sent initial prompt via args
  });

  // Handle stdout (Claude events)
  claudeProcess.stdout.on('data', (data) => {
    const session = sessions.get(sessionId);
    if (!session) return;

    session.buffer += data.toString();
    const lines = session.buffer.split('\n');
    session.buffer = lines.pop(); // Keep incomplete line in buffer

    lines.forEach(line => {
      if (line.trim()) {
        try {
          const event = JSON.parse(line);

          // Forward event to WebSocket client
          ws.send(JSON.stringify({
            type: 'claude_event',
            sessionId,
            event
          }));

          // Store significant events
          if (event.type === 'assistant' || event.type === 'user') {
            session.messages.push(event);
          }
        } catch (e) {
          console.error('Failed to parse Claude output:', line.substring(0, 100));
        }
      }
    });
  });

  // Handle stderr
  claudeProcess.stderr.on('data', (data) => {
    const errorMsg = data.toString();
    console.error(`Claude stderr [${sessionId}]:`, errorMsg);
    ws.send(JSON.stringify({
      type: 'claude_error',
      sessionId,
      error: errorMsg
    }));
  });

  // Handle process exit
  claudeProcess.on('exit', (code) => {
    console.log(`Claude process exited with code ${code} for session ${sessionId}`);
    ws.send(JSON.stringify({
      type: 'session_ended',
      sessionId,
      exitCode: code
    }));
    cleanupSession(sessionId);
  });

  // Send session started confirmation
  ws.send(JSON.stringify({
    type: 'session_started',
    sessionId,
    timestamp: new Date().toISOString()
  }));

  console.log(`Session ${sessionId} started successfully`);
}

function handleUserMessage(ws, message) {
  const { sessionId, content } = message;
  const session = sessions.get(sessionId);

  if (!session) {
    ws.send(JSON.stringify({
      type: 'error',
      error: 'Session not found'
    }));
    return;
  }

  console.log(`User message in session ${sessionId}:`, content.substring(0, 50));

  // Send message to Claude Code via stdin
  // Using text format for input (simpler and more reliable)
  session.process.stdin.write(content + '\n');
}

function handleEndSession(ws, message) {
  const { sessionId } = message;
  console.log('Ending session:', sessionId);
  cleanupSession(sessionId);
  ws.send(JSON.stringify({
    type: 'session_ended',
    sessionId
  }));
}

function cleanupSession(sessionId) {
  const session = sessions.get(sessionId);
  if (session) {
    try {
      session.process.kill('SIGTERM');
      console.log(`Killed process for session ${sessionId}`);
    } catch (e) {
      console.error('Error killing process:', e);
    }
    sessions.delete(sessionId);
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    activeSessions: sessions.size,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Session info endpoint
app.get('/sessions', (req, res) => {
  const sessionInfo = Array.from(sessions.entries()).map(([id, session]) => ({
    sessionId: id,
    customerId: session.customerId,
    startTime: session.startTime,
    messageCount: session.messages.length
  }));

  res.json({
    count: sessions.size,
    sessions: sessionInfo
  });
});

// Start server
const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Claude Code Orchestrator listening on port ${PORT}`);
  console.log(`WebSocket endpoint: ws://0.0.0.0:${PORT}`);
  console.log(`Health check: http://0.0.0.0:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, cleaning up...');
  for (const sessionId of sessions.keys()) {
    cleanupSession(sessionId);
  }
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, cleaning up...');
  for (const sessionId of sessions.keys()) {
    cleanupSession(sessionId);
  }
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

console.log('Server initialized, waiting for connections...');
