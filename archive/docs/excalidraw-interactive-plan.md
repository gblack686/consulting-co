# Comprehensive Plan: Voice-Driven Excalidraw Diagrams with AI

## Executive Summary

Build a voice-controlled diagram generation system integrated into your existing CompCorrect AI React frontend, allowing users to speak commands that are converted into real-time Excalidraw diagrams through Claude AI interpretation.

---

## Architecture Overview

```
User Voice Input (Browser)
    ↓
ElevenLabs Speech-to-Text API
    ↓
AWS Lambda (Voice Processing)
    ↓
ECS Container (Claude AI + MCP Client)
    ↓ WebSocket
MCP Excalidraw Server (EC2)
    ↓ WebSocket via API Gateway
React Frontend (Excalidraw Component)
    ↓
ElevenLabs Text-to-Speech
    ↓
Audio Confirmation to User
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Voice Input** | ElevenLabs API | Professional quality, consistent with voice output |
| **Voice Output** | ElevenLabs TTS | Provide audio feedback about diagram creation |
| **MCP Server Host** | AWS EC2 | Persistent WebSocket connections, no cold starts |
| **Communication** | WebSocket (API Gateway) | Real-time diagram updates as AI generates |
| **Frontend Framework** | React 18 (existing) | Already in use, Excalidraw has native support |
| **Amplify Integration** | Yes | Deploy to existing Amplify infrastructure |
| **AG-UI Protocol** | No (skipped) | MCP provides sufficient standardization |

---

## Research Findings & Resources

### MCP Excalidraw Servers (Available Now)

#### 1. **MCP Excalidraw by yctimlin** ⭐ Recommended
- **GitHub**: https://github.com/yctimlin/mcp_excalidraw
- **Features**:
  - Real-time diagram creation and manipulation
  - Live canvas accessible via web browser
  - WebSocket-based synchronization
  - Comprehensive element control (rectangles, circles, arrows, text)
  - Advanced features: grouping, alignment, locking
  - NPM and Docker deployment options
  - Designed for Claude Desktop and LLMs
  - Production-ready

#### 2. **Excalidraw MCP Server by i-tozer**
- **GitHub**: https://github.com/i-tozer/excalidraw-mcp
- **OpenMCP Directory**: https://www.openmcpdirectory.com/servers/i-tozer-excalidraw
- **Features**:
  - CRUD operations (Create, Read, Update, Delete)
  - Export to SVG, PNG, JSON
  - File-based storage
  - TypeScript with MCP SDK

### Excalidraw Integration Documentation

- **Official React Integration**: https://docs.excalidraw.com/docs/@excalidraw/excalidraw/integration
- **NPM Package**: `@excalidraw/excalidraw`
- **Embedding Guide**: Full programmatic control via React component

### AG-UI Research (For Future Reference)

**AG-UI Protocol**: https://docs.ag-ui.com/introduction
- Open, event-based protocol for AI agent ↔ UI communication
- Supports real-time communication and multimodal inputs
- Best for multi-agent coordination and framework-agnostic platforms

**Why We're Skipping AG-UI**:
- Single agent workflow (Claude only)
- MCP already provides agent-to-tool standardization
- WebSocket provides real-time updates
- Would add complexity without benefits for this use case

**When AG-UI Would Be Valuable**:
1. Multiple AI agents coordinating on same UI
2. Framework-agnostic agent platforms
3. Complex human-in-the-loop workflows with bidirectional state

---

## Component Breakdown

### 1. Frontend Components (React)

#### A. Excalidraw Diagram Editor
**File**: `src/components/DiagramEditor/DiagramEditor.js`

**Responsibilities**:
- Embed Excalidraw React component
- Manage WebSocket connection to MCP server
- Receive AI-generated diagram elements
- Update canvas in real-time
- Export diagrams (SVG, PNG, JSON)

**NPM Dependencies**:
```bash
npm install @excalidraw/excalidraw
```

**Key Features**:
- `excalidrawAPI` ref for programmatic control
- `updateScene()` method to add AI-generated elements
- Real-time WebSocket event handling

#### B. Voice Input Component
**File**: `src/components/VoiceInput/VoiceInput.js`

**Responsibilities**:
- Capture audio from browser microphone
- Send audio to ElevenLabs Speech-to-Text API
- Display transcript to user
- Send text command to AWS backend

**ElevenLabs API**: Speech-to-Text endpoint
- API Docs: https://elevenlabs.io/docs/api-reference/text-to-speech

#### C. Voice Output Component
**File**: `src/components/VoiceOutput/VoiceOutput.js`

**Responsibilities**:
- Receive diagram descriptions from backend
- Convert to speech using ElevenLabs TTS
- Play audio feedback to user

**ElevenLabs API**: Text-to-Speech endpoint

---

### 2. Backend Services (AWS)

#### A. Voice Processing Lambda
**Purpose**: Process voice input and initiate diagram generation

**Flow**:
1. Receive audio/text from frontend
2. If audio: Call ElevenLabs STT
3. Send text command to Claude via ECS
4. Return session ID to frontend

**AWS Services**:
- Lambda function (Python 3.12)
- API Gateway REST endpoint: `POST /voice-command`
- Cognito authorization (existing)

#### B. AI Orchestration Service (ECS)
**Purpose**: Host Claude AI with MCP client

**Components**:
- ECS Fargate task
- Claude API integration
- MCP client library
- WebSocket connection to MCP Excalidraw Server

**Flow**:
1. Receive voice command text
2. Claude interprets command (e.g., "draw a flowchart with 3 boxes")
3. Claude uses MCP tools to generate Excalidraw elements
4. Stream updates via WebSocket to frontend

**Why ECS over Lambda**:
- Persistent WebSocket connections
- No cold start delays
- Better for long-running AI operations

#### C. MCP Excalidraw Server (EC2)
**Purpose**: Convert AI commands to Excalidraw diagram elements

**Deployment**:
- EC2 t3.medium instance
- Docker container running MCP server (yctimlin's version)
- WebSocket server on port 3000
- Application Load Balancer for high availability

**MCP Tools Available**:
- `create_rectangle`
- `create_circle`
- `create_arrow`
- `create_text`
- `group_elements`
- `align_elements`
- And more...

#### D. WebSocket API (API Gateway)
**Purpose**: Real-time communication frontend ↔ MCP server

**Configuration**:
- API Gateway WebSocket API
- Route: `$connect`, `$disconnect`, `$default`
- Integration: HTTP proxy to EC2 MCP server
- Authorization: Cognito (existing)

---

### 3. AWS Amplify Integration

#### Existing Infrastructure
- Cognito User Pool: `us-east-1_p43SCKKVc`
- API Gateway: `https://c0tlhvjm3i.execute-api.us-east-1.amazonaws.com/dev`
- Region: `us-east-1`

#### New Amplify Configuration

**amplify/backend/api/voice-diagram-api/schema.graphql** (if using AppSync):
```graphql
type DiagramSession {
  id: ID!
  userId: String!
  command: String!
  status: String!
  diagramData: AWSJSON
  createdAt: AWSDateTime!
}
```

**Or REST API Extension** (recommended for this use case):
- Add new endpoints to existing API Gateway
- Reuse Cognito authorizer

#### Frontend Hosting
- Amplify Hosting for React app
- Build command: `npm run build`
- Environment variables for API endpoints

---

## Implementation Phases

### Phase 1: Excalidraw Embedding (Week 1)
**Goal**: Get Excalidraw working in React app

**Tasks**:
1. Install `@excalidraw/excalidraw` package
2. Create `DiagramEditor` component
3. Test programmatic element creation
4. Add new tab/view in existing App.js
5. Deploy to Amplify dev environment

**Success Criteria**: User can see embedded Excalidraw and test buttons add shapes

---

### Phase 2: MCP Server Deployment (Week 1-2)
**Goal**: Deploy MCP Excalidraw server on AWS

**Tasks**:
1. Launch EC2 instance (t3.medium, us-east-1)
2. Install Docker and deploy yctimlin/mcp_excalidraw
3. Configure security groups (port 3000, WebSocket)
4. Set up Application Load Balancer
5. Test MCP API endpoints manually

**Success Criteria**: Can send HTTP requests to MCP server and get diagram elements back

---

### Phase 3: WebSocket Communication (Week 2)
**Goal**: Real-time frontend ↔ MCP server communication

**Tasks**:
1. Create API Gateway WebSocket API
2. Configure routes to proxy to EC2
3. Add Cognito authorization
4. Implement WebSocket client in React
5. Test bidirectional messaging

**Success Criteria**: Frontend receives real-time updates from MCP server

---

### Phase 4: Voice Input (ElevenLabs) (Week 2-3)
**Goal**: Capture voice and convert to text

**Tasks**:
1. Sign up for ElevenLabs API (https://elevenlabs.io)
2. Create `VoiceInput` component
3. Implement browser audio capture
4. Send audio to ElevenLabs STT API
5. Display transcript to user

**Success Criteria**: User speaks, sees text transcript in real-time

---

### Phase 5: AI Orchestration (Claude + MCP) (Week 3-4)
**Goal**: Claude interprets voice commands and generates diagrams

**Tasks**:
1. Create ECS Fargate task definition
2. Build Docker image with Claude API + MCP client
3. Implement command interpreter (voice text → diagram intent)
4. Connect to MCP server via WebSocket
5. Handle streaming responses

**Example Flow**:
```
User: "Draw a database connected to an API server"
  ↓
Claude: Interprets as 2 rectangles + 1 arrow
  ↓
MCP Server: Generates Excalidraw JSON elements
  ↓
Frontend: Renders in real-time
```

**Success Criteria**: Voice command → diagram appears on canvas

---

### Phase 6: Voice Output (ElevenLabs TTS) (Week 4)
**Goal**: Audio confirmation of diagram creation

**Tasks**:
1. Create `VoiceOutput` component
2. Send diagram description to ElevenLabs TTS
3. Play audio response to user
4. Add voice selection (different AI voices)

**Example**:
```
User: "Add a red warning box"
AI Voice: "I've added a red rectangle labeled 'Warning' to your diagram"
```

**Success Criteria**: User hears audio feedback after diagram updates

---

### Phase 7: Integration & Polish (Week 4-5)
**Goal**: Complete end-to-end workflow

**Tasks**:
1. Error handling (API failures, invalid commands)
2. Loading states and progress indicators
3. Diagram export (SVG, PNG)
4. Save/load diagram sessions to DynamoDB
5. Cost monitoring (ElevenLabs, Claude, AWS)
6. Performance optimization

**Success Criteria**: Production-ready feature

---

## AWS Services Required

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| **EC2 (t3.medium)** | MCP Excalidraw Server | ~$30/month |
| **ECS Fargate** | Claude AI orchestration | ~$40/month |
| **API Gateway** | REST + WebSocket APIs | ~$3.50/1M requests |
| **Lambda** | Voice processing | ~$0.20/1M requests |
| **Application Load Balancer** | EC2 high availability | ~$16/month |
| **Amplify Hosting** | Frontend hosting | Free tier → $15/month |
| **ElevenLabs API** | Voice input/output | ~$22/month (Creator plan) |
| **Anthropic Claude API** | AI diagram generation | Pay per token (~$0.50/1K diagrams) |

**Total Estimated**: ~$120-150/month for moderate usage

---

## Security Considerations

1. **API Keys**: Store in AWS Secrets Manager
   - ElevenLabs API key
   - Anthropic API key

2. **Authentication**: Existing Cognito (reuse)
   - All API calls require JWT token
   - WebSocket connections authorized on connect

3. **CORS**: Configure for Amplify domain
   ```javascript
   allowOrigins: ['https://your-app.amplifyapp.com']
   ```

4. **Rate Limiting**: 
   - API Gateway: 10 requests/second per user
   - ElevenLabs: Track usage, alert at 80%

5. **Data Privacy**:
   - Voice audio not stored (processed in-memory)
   - Diagram data encrypted in DynamoDB
   - Compliance with audio recording laws

---

## Example Voice Commands

| User Command | AI Interpretation | Diagram Output |
|--------------|-------------------|----------------|
| "Draw a flowchart with start, process, and end" | 3 boxes (rounded, rectangle, rounded) + 2 arrows | Vertical flowchart |
| "Add a database connected to an API" | 2 shapes (cylinder, rectangle) + 1 arrow | Simple architecture |
| "Create a red warning box in the top right" | 1 rectangle (red fill, positioned) | Alert box |
| "Connect user to server with bidirectional arrow" | 2 circles + 1 double-arrow | Network diagram |
| "Make a 3-tier architecture diagram" | 3 groups (frontend, backend, database) | Layered architecture |

---

## Code Snippets

### React Excalidraw Component

```jsx
import React, { useState, useCallback } from 'react';
import { Excalidraw } from '@excalidraw/excalidraw';

function DiagramEditor({ websocketUrl }) {
  const [excalidrawAPI, setExcalidrawAPI] = useState(null);
  
  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(websocketUrl);
    
    ws.onmessage = (event) => {
      const elements = JSON.parse(event.data);
      if (excalidrawAPI) {
        excalidrawAPI.updateScene({ elements });
      }
    };
    
    return () => ws.close();
  }, [websocketUrl, excalidrawAPI]);
  
  return (
    <div style={{ height: '600px' }}>
      <Excalidraw excalidrawAPI={(api) => setExcalidrawAPI(api)} />
    </div>
  );
}
```

### ElevenLabs Voice Input

```javascript
async function captureVoiceCommand() {
  // Capture audio from browser
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const audioChunks = [];
  
  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };
  
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    
    // Send to ElevenLabs STT
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    const response = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
      method: 'POST',
      headers: { 'xi-api-key': ELEVENLABS_API_KEY },
      body: formData
    });
    
    const { text } = await response.json();
    return text; // "Draw a flowchart with 3 boxes"
  };
  
  mediaRecorder.start();
  // Stop after 5 seconds or on button release
  setTimeout(() => mediaRecorder.stop(), 5000);
}
```

---

## Testing Strategy

### Unit Tests
- Excalidraw element generation
- Voice command parsing
- WebSocket message handling

### Integration Tests
- End-to-end voice → diagram flow
- WebSocket reconnection
- API error handling

### User Acceptance Tests
- Voice recognition accuracy
- Diagram generation speed
- Audio feedback clarity

---

## Monitoring & Observability

**CloudWatch Dashboards**:
1. Voice processing latency
2. Claude API response time
3. WebSocket connection count
4. Diagram generation success rate
5. ElevenLabs API usage

**Alarms**:
- MCP server health check failures
- Claude API error rate > 5%
- WebSocket disconnections > 10/minute
- ElevenLabs quota at 80%

---

## Future Enhancements (Out of Scope)

1. **Multi-user collaboration**: Real-time co-editing of diagrams
2. **Diagram templates**: Pre-built templates for common diagrams
3. **AI suggestions**: Proactive diagram improvements
4. **Export to Miro/Figma**: Integration with other tools
5. **Mobile app**: iOS/Android voice diagramming
6. **AG-UI integration**: If expanding to multi-agent system

---

## References & Links

### Documentation
- **Excalidraw React**: https://docs.excalidraw.com/docs/@excalidraw/excalidraw/integration
- **MCP Protocol**: https://modelcontextprotocol.io
- **ElevenLabs API**: https://elevenlabs.io/docs
- **AWS API Gateway WebSocket**: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html
- **AWS Amplify**: https://docs.amplify.aws/

### GitHub Repositories
- **MCP Excalidraw (yctimlin)**: https://github.com/yctimlin/mcp_excalidraw
- **MCP Excalidraw (i-tozer)**: https://github.com/i-tozer/excalidraw-mcp
- **AG-UI Protocol**: https://docs.ag-ui.com (for future reference)

### Tools & Services
- **OpenMCP Directory**: https://www.openmcpdirectory.com
- **ElevenLabs Pricing**: https://elevenlabs.io/pricing
- **Anthropic Claude**: https://www.anthropic.com/api

---

## Next Steps

1. **Set up ElevenLabs account** and get API key
2. **Choose MCP server** (recommend yctimlin's version)
3. **Create new Git branch**: `feature/voice-diagrams`
4. **Start with Phase 1**: Embed Excalidraw in existing React app
5. **Iterate and test** each phase before moving to next

---

This plan gives you a complete roadmap from concept to production. The architecture is scalable, uses proven tools (MCP, Excalidraw, ElevenLabs), and integrates with your existing AWS infrastructure. The estimated timeline is 4-5 weeks for full implementation.