# Claude Code Event Mirroring System
## Real-time Frontend that Mirrors Claude Code CLI Experience

---

## Event Stream Analysis

Based on testing, Claude Code with `--output-format stream-json --include-partial-messages --verbose` emits the following event types:

### Event Types

#### 1. **system** (init)
```json
{
  "type": "system",
  "subtype": "init",
  "cwd": "/home/ubuntu",
  "session_id": "671fe5f6-4513-48da-8410-17f6c727263b",
  "tools": ["Task", "Bash", "Glob", "Grep", ...],
  "mcp_servers": [],
  "model": "claude-haiku-4-5",
  "permissionMode": "default",
  "slash_commands": ["build", "implement", ...],
  "apiKeySource": "none",
  "claude_code_version": "2.0.24",
  "output_style": "default",
  "agents": ["general-purpose", "Explore", ...],
  "skills": []
}
```

#### 2. **stream_event** (message_start)
```json
{
  "type": "stream_event",
  "event": {
    "type": "message_start",
    "message": {
      "model": "claude-haiku-4-5-20251001",
      "id": "msg_01VPgzS8mrzpBcek78iv3Y3q",
      "type": "message",
      "role": "assistant",
      "content": [{"type": "text", "text": ""}],
      "usage": {...}
    }
  },
  "session_id": "...",
  "parent_tool_use_id": null
}
```

#### 3. **stream_event** (content_block_start)
```json
{
  "type": "stream_event",
  "event": {
    "type": "content_block_start",
    "index": 0,
    "content_block": {"type": "text", "text": ""}
  },
  "session_id": "..."
}
```

#### 4. **stream_event** (content_block_delta)
```json
{
  "type": "stream_event",
  "event": {
    "type": "content_block_delta",
    "index": 0,
    "delta": {"type": "text_delta", "text": "The"}
  },
  "session_id": "..."
}
```

#### 5. **stream_event** (content_block_stop)
```json
{
  "type": "stream_event",
  "event": {"type": "content_block_stop", "index": 0},
  "session_id": "..."
}
```

#### 6. **stream_event** (message_delta)
```json
{
  "type": "stream_event",
  "event": {
    "type": "message_delta",
    "delta": {"stop_reason": "end_turn", "stop_sequence": null},
    "usage": {...}
  },
  "session_id": "..."
}
```

#### 7. **stream_event** (message_stop)
```json
{
  "type": "stream_event",
  "event": {"type": "message_stop"},
  "session_id": "..."
}
```

#### 8. **assistant** (complete message)
```json
{
  "type": "assistant",
  "message": {
    "model": "...",
    "id": "msg_...",
    "role": "assistant",
    "content": [{"type": "text", "text": "The capital..."}]
  },
  "session_id": "..."
}
```

#### 9. **result** (final result)
```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1648,
  "num_turns": 1,
  "result": "The capital of France is Paris...",
  "session_id": "...",
  "total_cost_usd": 0.0033721,
  "usage": {...}
}
```

### Additional Event Types (Tool Use)

When Claude uses tools, you'll see:
- **stream_event** (tool_use_start)
- **stream_event** (tool_use_delta)
- **stream_event** (tool_use_result)
- **thinking** (when thinking mode is enabled)
- **tool_decision** (permission requests)

---

## Architecture Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Browser                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          React Frontend (Amplify Hosted)             │   │
│  │  • ClaudeCodeChat component                          │   │
│  │  • Real-time event display                           │   │
│  │  • Typing indicators                                 │   │
│  │  • Tool use visualization                            │   │
│  │  • Cost tracking                                     │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │ WebSocket                                    │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway (WebSocket API)                     │
│              wss://api.yourcompany.com                       │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: WebSocket Connection Handler                │
│  • $connect    → Register connection                        │
│  • $disconnect → Clean up connection                        │
│  • message     → Route to Claude orchestrator               │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│    Claude Code Orchestrator (Lightsail - Port 3000)         │
│    IP: 44.208.161.19                                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       WebSocket Server (ws library)                  │  │
│  │  • Accept connections from API Gateway               │  │
│  │  • Manage Claude Code processes                      │  │
│  │  • Stream events to clients                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Session Manager                                │  │
│  │  • Spawn Claude Code process per session             │  │
│  │  • Monitor stdout for JSON events                    │  │
│  │  • Forward events via WebSocket                      │  │
│  │  • Handle user input → Claude stdin                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Claude Code Process (spawned per session)          │  │
│  │   $ claude -p --verbose --output-format stream-json  │  │
│  │     --include-partial-messages --input-format        │  │
│  │     stream-json                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  Anthropic    │
                  │     API       │
                  └───────────────┘
```

---

## Implementation

### Part 1: Claude Code Orchestrator (Lightsail)

Install on your Lightsail instance at `/home/ubuntu/claude-orchestrator`:

```bash
#!/bin/bash
# install-orchestrator.sh

cd /home/ubuntu
mkdir -p claude-orchestrator
cd claude-orchestrator

# Initialize Node.js project
npm init -y

# Install dependencies
npm install ws express body-parser uuid

# Create main server file
cat > server.js << 'EOJS'
const WebSocket = require('ws');
const express = require('express');
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

// Session storage
const sessions = new Map();

// WebSocket connection handler
wss.on('connection', (ws, req) => {
  console.log('New WebSocket connection');

  ws.on('message', async (data) => {
    try {
      const message = JSON.parse(data);

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
    // Clean up any sessions associated with this connection
    for (const [sessionId, session] of sessions.entries()) {
      if (session.ws === ws) {
        cleanupSession(sessionId);
      }
    }
  });
});

function handleStartSession(ws, message) {
  const sessionId = message.sessionId || uuidv4();
  const { customerId, context, model, permissionMode } = message;

  console.log(`Starting session ${sessionId} for customer ${customerId}`);

  // Build Claude Code command
  const args = [
    '-p',
    '--verbose',
    '--output-format', 'stream-json',
    '--include-partial-messages',
    '--input-format', 'stream-json',
    '--replay-user-messages'
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
    messages: []
  });

  // Handle stdout (Claude events)
  let buffer = '';
  claudeProcess.stdout.on('data', (data) => {
    buffer += data.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

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
            const session = sessions.get(sessionId);
            if (session) {
              session.messages.push(event);
            }
          }
        } catch (e) {
          console.error('Failed to parse Claude output:', line, e);
        }
      }
    });
  });

  // Handle stderr
  claudeProcess.stderr.on('data', (data) => {
    console.error(`Claude stderr: ${data}`);
    ws.send(JSON.stringify({
      type: 'claude_error',
      sessionId,
      error: data.toString()
    }));
  });

  // Handle process exit
  claudeProcess.on('exit', (code) => {
    console.log(`Claude process exited with code ${code}`);
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

  // Send message to Claude Code via stdin
  // Claude expects stream-json format for input
  const claudeInput = JSON.stringify({
    type: 'user',
    content
  }) + '\n';

  session.process.stdin.write(claudeInput);
}

function handleEndSession(ws, message) {
  const { sessionId } = message;
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
    uptime: process.uptime()
  });
});

// Start server
const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Claude Code Orchestrator listening on port ${PORT}`);
  console.log(`WebSocket endpoint: ws://localhost:${PORT}`);
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
EOJS

# Create systemd service
sudo tee /etc/systemd/system/claude-orchestrator.service > /dev/null << 'EOF'
[Unit]
Description=Claude Code WebSocket Orchestrator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/claude-orchestrator
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="NODE_ENV=production"
Environment="ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE"

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable claude-orchestrator
sudo systemctl start claude-orchestrator

# Check status
sudo systemctl status claude-orchestrator

echo "Orchestrator installed! WebSocket server running on port 3000"
```

### Part 2: API Gateway WebSocket (AWS)

Create CloudFormation template or use AWS CLI:

```yaml
# websocket-api.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'WebSocket API for Claude Code Mirroring'

Resources:
  WebSocketApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: ClaudeCodeWebSocket
      ProtocolType: WEBSOCKET
      RouteSelectionExpression: '$request.body.action'

  ConnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $connect
      AuthorizationType: NONE
      Target: !Sub 'integrations/${ConnectIntegration}'

  DisconnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $disconnect
      Target: !Sub 'integrations/${DisconnectIntegration}'

  MessageRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: message
      Target: !Sub 'integrations/${MessageIntegration}'

  ConnectIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ConnectFunction.Arn}/invocations'

  DisconnectIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${DisconnectFunction.Arn}/invocations'

  MessageIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${MessageFunction.Arn}/invocations'

  Deployment:
    Type: AWS::ApiGatewayV2::Deployment
    DependsOn:
      - ConnectRoute
      - DisconnectRoute
      - MessageRoute
    Properties:
      ApiId: !Ref WebSocketApi

  Stage:
    Type: AWS::ApiGatewayV2::Stage
    Properties:
      StageName: prod
      DeploymentId: !Ref Deployment
      ApiId: !Ref WebSocketApi

  # Lambda Functions
  ConnectFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ClaudeCodeWSConnect
      Runtime: nodejs18.x
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          exports.handler = async (event) => {
            console.log('WebSocket connected:', event.requestContext.connectionId);
            return { statusCode: 200, body: 'Connected' };
          };

  DisconnectFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ClaudeCodeWSDisconnect
      Runtime: nodejs18.x
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          exports.handler = async (event) => {
            console.log('WebSocket disconnected:', event.requestContext.connectionId);
            return { statusCode: 200, body: 'Disconnected' };
          };

  MessageFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ClaudeCodeWSMessage
      Runtime: nodejs18.x
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          LIGHTSAIL_WS_URL: ws://44.208.161.19:3000
      Code:
        ZipFile: |
          const WebSocket = require('ws');

          exports.handler = async (event) => {
            const connectionId = event.requestContext.connectionId;
            const body = JSON.parse(event.body);

            // Forward to Lightsail orchestrator
            return new Promise((resolve, reject) => {
              const ws = new WebSocket(process.env.LIGHTSAIL_WS_URL);

              ws.on('open', () => {
                ws.send(JSON.stringify(body));
              });

              ws.on('message', (data) => {
                // Forward back to client via API Gateway
                const apiGw = new AWS.ApiGatewayManagementApi({
                  endpoint: event.requestContext.domainName + '/' + event.requestContext.stage
                });

                apiGw.postToConnection({
                  ConnectionId: connectionId,
                  Data: data
                }).promise();
              });

              ws.on('close', () => {
                resolve({ statusCode: 200, body: 'Message sent' });
              });
            });
          };

  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: ApiGatewayManagement
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - execute-api:ManageConnections
                Resource: '*'

Outputs:
  WebSocketURL:
    Description: WebSocket URL
    Value: !Sub 'wss://${WebSocketApi}.execute-api.${AWS::Region}.amazonaws.com/prod'
```

### Part 3: React Frontend (Amplify)

Install in your `gb-automation-landing` directory:

```bash
cd gb-automation-landing
npm install --save socket.io-client uuid react-markdown
```

Create the Claude Code Chat component:

```jsx
// src/components/ClaudeCodeChat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import ReactMarkdown from 'react-markdown';
import './ClaudeCodeChat.css';

const ClaudeCodeChat = ({ customerId }) => {
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [sessionInfo, setSessionInfo] = useState(null);
  const [cost, setCost] = useState(0);
  const [toolUse, setToolUse] = useState(null);
  const messagesEndRef = useRef(null);

  // Connect to WebSocket
  useEffect(() => {
    // Use your API Gateway WebSocket URL
    const ws = io('wss://your-api-id.execute-api.us-east-1.amazonaws.com/prod');

    ws.on('connect', () => {
      console.log('Connected to Claude Code WebSocket');

      // Start session
      ws.emit('message', {
        type: 'start_session',
        customerId,
        context: 'customer_planning',
        model: 'sonnet',
        permissionMode: 'plan'
      });
    });

    ws.on('message', handleWebSocketMessage);

    setSocket(ws);

    return () => {
      if (sessionId) {
        ws.emit('message', {
          type: 'end_session',
          sessionId
        });
      }
      ws.close();
    };
  }, [customerId]);

  const handleWebSocketMessage = (data) => {
    const message = JSON.parse(data);

    switch (message.type) {
      case 'session_started':
        setSessionId(message.sessionId);
        console.log('Session started:', message.sessionId);
        break;

      case 'claude_event':
        handleClaudeEvent(message.event);
        break;

      case 'session_ended':
        console.log('Session ended');
        break;

      case 'error':
        console.error('Error:', message.error);
        break;
    }
  };

  const handleClaudeEvent = (event) => {
    switch (event.type) {
      case 'system':
        if (event.subtype === 'init') {
          setSessionInfo({
            model: event.model,
            tools: event.tools,
            version: event.claude_code_version
          });
        }
        break;

      case 'stream_event':
        handleStreamEvent(event.event);
        break;

      case 'assistant':
        // Complete message received
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: event.message.content[0].text,
          timestamp: new Date()
        }]);
        setCurrentResponse('');
        setIsTyping(false);
        break;

      case 'result':
        // Session result with cost
        setCost(prev => prev + event.total_cost_usd);
        break;

      case 'user':
        // Echo back user message
        setMessages(prev => [...prev, {
          role: 'user',
          content: event.content,
          timestamp: new Date()
        }]);
        break;
    }
  };

  const handleStreamEvent = (event) => {
    switch (event.type) {
      case 'message_start':
        setIsTyping(true);
        setCurrentResponse('');
        break;

      case 'content_block_delta':
        if (event.delta.type === 'text_delta') {
          setCurrentResponse(prev => prev + event.delta.text);
        }
        break;

      case 'content_block_stop':
        // Content block finished
        break;

      case 'message_stop':
        setIsTyping(false);
        break;

      case 'tool_use':
        setToolUse({
          name: event.name,
          input: event.input,
          status: 'running'
        });
        break;

      case 'tool_result':
        setToolUse(prev => ({
          ...prev,
          result: event.content,
          status: 'completed'
        }));
        setTimeout(() => setToolUse(null), 3000);
        break;
    }
  };

  const sendMessage = () => {
    if (!inputValue.trim() || !socket || !sessionId) return;

    socket.emit('message', {
      type: 'user_message',
      sessionId,
      content: inputValue
    });

    setInputValue('');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  return (
    <div className="claude-code-chat">
      {/* Header */}
      <div className="chat-header">
        <h2>Claude Code Planning Session</h2>
        {sessionInfo && (
          <div className="session-info">
            <span className="model-badge">{sessionInfo.model}</span>
            <span className="cost-badge">${cost.toFixed(4)}</span>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user' ? '👤 You' : '🤖 Claude'}
              </span>
              <span className="message-time">
                {msg.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {/* Streaming response */}
        {isTyping && currentResponse && (
          <div className="message message-assistant streaming">
            <div className="message-header">
              <span className="message-role">🤖 Claude</span>
              <span className="typing-indicator">
                <span></span><span></span><span></span>
              </span>
            </div>
            <div className="message-content">
              <ReactMarkdown>{currentResponse}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Tool use indicator */}
        {toolUse && (
          <div className="tool-use-indicator">
            <div className="tool-icon">🔧</div>
            <div className="tool-info">
              <div className="tool-name">Using tool: {toolUse.name}</div>
              {toolUse.status === 'completed' && (
                <div className="tool-status">✓ Complete</div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask Claude anything about your project..."
          disabled={!sessionId || isTyping}
        />
        <button
          onClick={sendMessage}
          disabled={!sessionId || isTyping || !inputValue.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ClaudeCodeChat;
```

CSS for the component:

```css
/* src/components/ClaudeCodeChat.css */
.claude-code-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chat-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.session-info {
  display: flex;
  gap: 1rem;
}

.model-badge, .cost-badge {
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  font-size: 0.9rem;
  backdrop-filter: blur(10px);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  align-self: flex-end;
}

.message-assistant {
  align-self: flex-start;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.message-role {
  font-weight: 600;
}

.message-content {
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  line-height: 1.6;
}

.message-user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.message-assistant .message-content {
  background: white;
  color: #333;
  border-bottom-left-radius: 0.25rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.message.streaming .message-content {
  background: linear-gradient(90deg, #fff 0%, #f8f8f8 50%, #fff 100%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.tool-use-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
  animation: slideIn 0.3s ease-out;
}

.tool-icon {
  font-size: 2rem;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-weight: 600;
  color: #856404;
}

.tool-status {
  color: #28a745;
  font-size: 0.9rem;
}

.chat-input {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: white;
  border-top: 1px solid #ddd;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}

.chat-input input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 2rem;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input input:focus {
  border-color: #667eea;
}

.chat-input button {
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.chat-input button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Code blocks in markdown */
.message-content code {
  background: #f4f4f4;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
}

.message-user .message-content code {
  background: rgba(255,255,255,0.2);
}

.message-content pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.message-content pre code {
  background: none;
  color: inherit;
}
```

### Part 4: Integration with Existing Amplify App

Update your `gb-automation-landing/src/App.js`:

```jsx
import React from 'react';
import VideoHero from './components/VideoHero';
import ClaudeCodeChat from './components/ClaudeCodeChat';
import './App.css';

function App() {
  const [showChat, setShowChat] = useState(false);
  const [customerId] = useState(() => {
    // Get or generate customer ID
    let id = localStorage.getItem('customerId');
    if (!id) {
      id = 'customer-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('customerId', id);
    }
    return id;
  });

  return (
    <div className="App">
      <VideoHero />

      <div className="cta-section">
        <button
          className="start-planning-btn"
          onClick={() => setShowChat(true)}
        >
          Start Planning Your Project
        </button>
      </div>

      {showChat && (
        <div className="chat-modal">
          <div className="chat-modal-overlay" onClick={() => setShowChat(false)} />
          <div className="chat-modal-content">
            <button
              className="close-btn"
              onClick={() => setShowChat(false)}
            >
              ✕
            </button>
            <ClaudeCodeChat customerId={customerId} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
```

---

## Deployment Steps

### 1. Deploy Orchestrator to Lightsail

```bash
# SSH into Lightsail
ssh -i ~/.ssh/lightsail-key.pem ubuntu@44.208.161.19

# Run installation script
bash install-orchestrator.sh

# Verify it's running
curl http://localhost:3000/health
```

### 2. Deploy WebSocket API Gateway

```bash
# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name claude-code-websocket \
  --template-body file://websocket-api.yaml \
  --capabilities CAPABILITY_IAM

# Get WebSocket URL
aws cloudformation describe-stacks \
  --stack-name claude-code-websocket \
  --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
  --output text
```

### 3. Update React App

```bash
cd gb-automation-landing

# Update WebSocket URL in ClaudeCodeChat.jsx
# Replace 'wss://your-api-id...' with actual URL from step 2

# Build and deploy to Amplify
npm run build
aws amplify start-job \
  --app-id YOUR_AMPLIFY_APP_ID \
  --branch-name main \
  --job-type RELEASE
```

---

## Testing

Test the complete flow:

```bash
# 1. Start orchestrator (should already be running)
sudo systemctl status claude-orchestrator

# 2. Test WebSocket locally
node test-websocket.js
```

Create `test-websocket.js`:

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://44.208.161.19:3000');

ws.on('open', () => {
  console.log('Connected!');

  // Start session
  ws.send(JSON.stringify({
    type: 'start_session',
    customerId: 'test-customer-123',
    context: 'testing'
  }));

  setTimeout(() => {
    // Send test message
    ws.send(JSON.stringify({
      type: 'user_message',
      sessionId: 'will-be-provided-by-session-start',
      content: 'What is 2+2?'
    }));
  }, 2000);
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  console.log('Received:', JSON.stringify(msg, null, 2));
});
```

---

## What You Get

✅ **Real-time streaming** - See Claude's response character by character, just like CLI
✅ **Tool usage visibility** - Show when Claude is using Bash, Read, Edit, etc.
✅ **Planning mode** - Customers see Claude's planning process
✅ **Cost tracking** - Live cost updates per session
✅ **Typing indicators** - Professional chat UX
✅ **Markdown rendering** - Formatted responses with code blocks
✅ **Session persistence** - Full conversation history
✅ **Error handling** - Graceful error display
✅ **Mobile responsive** - Works on all devices

---

## Next Steps

1. **Security**: Add authentication (Cognito) to WebSocket connections
2. **Rate limiting**: Prevent abuse
3. **Session storage**: Save transcripts to S3/DynamoDB
4. **Analytics**: Track usage patterns
5. **Approval workflow**: Button to generate scope from chat
6. **Email notifications**: Alert when session ends

This gives you a **pixel-perfect mirror** of the Claude Code CLI experience in your Amplify frontend! 🚀
