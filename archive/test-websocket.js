// Test WebSocket Client for Claude Code Orchestrator
const WebSocket = require('ws');

const LIGHTSAIL_IP = '44.208.161.19';
const PORT = 3000;

console.log('Connecting to Claude Code Orchestrator...');
console.log(`ws://${LIGHTSAIL_IP}:${PORT}`);

const ws = new WebSocket(`ws://${LIGHTSAIL_IP}:${PORT}`);

let sessionId = null;

ws.on('open', () => {
  console.log('✓ Connected!');
  console.log('');

  // Start session
  console.log('Starting session...');
  ws.send(JSON.stringify({
    type: 'start_session',
    customerId: 'test-customer-123',
    context: 'testing',
    model: 'haiku',
    permissionMode: 'plan'
  }));
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);

  switch (msg.type) {
    case 'session_started':
      sessionId = msg.sessionId;
      console.log('✓ Session started:', sessionId);
      console.log('');

      // Wait a moment, then send a test message
      setTimeout(() => {
        console.log('Sending test question: "What is 2+2?"');
        console.log('');
        ws.send(JSON.stringify({
          type: 'user_message',
          sessionId: sessionId,
          content: 'What is 2+2?'
        }));
      }, 1000);
      break;

    case 'claude_event':
      const event = msg.event;

      switch (event.type) {
        case 'system':
          if (event.subtype === 'init') {
            console.log('✓ Claude initialized');
            console.log(`  Model: ${event.model}`);
            console.log(`  Version: ${event.claude_code_version}`);
            console.log('');
          }
          break;

        case 'stream_event':
          if (event.event.type === 'message_start') {
            console.log('Claude is responding...');
            process.stdout.write('  ');
          } else if (event.event.type === 'content_block_delta') {
            // Print streaming text character by character
            process.stdout.write(event.event.delta.text);
          } else if (event.event.type === 'message_stop') {
            console.log('');
            console.log('');
          }
          break;

        case 'assistant':
          // Complete message
          console.log('✓ Complete response received');
          break;

        case 'result':
          console.log('✓ Session result:');
          console.log(`  Duration: ${event.duration_ms}ms`);
          console.log(`  Cost: $${event.total_cost_usd.toFixed(6)}`);
          console.log(`  Turns: ${event.num_turns}`);
          console.log('');

          // End session after receiving result
          setTimeout(() => {
            console.log('Ending session...');
            ws.send(JSON.stringify({
              type: 'end_session',
              sessionId: sessionId
            }));

            setTimeout(() => {
              console.log('✓ Test complete!');
              ws.close();
              process.exit(0);
            }, 500);
          }, 1000);
          break;
      }
      break;

    case 'claude_error':
      console.error('Claude error:', msg.error);
      break;

    case 'session_ended':
      console.log('✓ Session ended');
      break;

    case 'error':
      console.error('Error:', msg.error);
      break;

    default:
      console.log('Unknown message type:', msg.type);
  }
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
  process.exit(1);
});

ws.on('close', () => {
  console.log('Connection closed');
});

// Timeout after 60 seconds
setTimeout(() => {
  console.error('Test timed out');
  ws.close();
  process.exit(1);
}, 60000);
