# Can You Create Voiceflow Workflows Programmatically?

## Short Answer

**No**, Voiceflow does not currently provide APIs to create or modify agent workflows programmatically. Agent design must be done through the Voiceflow Creator UI.

However, **Yes**, you can:
- ✅ Deploy agents programmatically via Dialog Manager API
- ✅ Interact with agents via API
- ✅ Manage agent state and conversations
- ✅ Extract results and analytics programmatically

---

## Detailed Analysis

### What IS Possible Programmatically

#### 1. **Deploy Agents to Custom Channels**
You can send existing agents to any custom interface using the Dialog Manager API:

```typescript
// Send agent to custom chat interface
await voiceflow.interact(userId, {
  action: { type: "text", payload: userMessage }
});

// Deploy to voice channel
// Deploy to SMS/WhatsApp channel
// Deploy to custom web app
```

#### 2. **Manage Conversations**
Control the dialogue flow and state:

```typescript
// Start conversation
await voiceflow.initializeSession(userId);

// Send messages
await voiceflow.sendMessage(userId, "user input");

// Get state
const state = await voiceflow.getState(userId);

// Reset conversation
await voiceflow.clearSession(userId);
```

#### 3. **Extract Results**
Access all collected data via API:

```typescript
// Get scoping data
const data = await voiceflow.getScopingData(userId);
// Returns: { projectName, client, timeline, budget, ... }

// Get transcript
const transcript = await voiceflow.getTranscript(userId);

// Get analytics
const analytics = await voiceflow.getAnalytics(agentId);
```

#### 4. **Handle Webhooks**
React to conversation events programmatically:

```json
// On completion webhook
POST /your-backend/api/scoping/complete
{
  "agentId": "...",
  "userId": "...",
  "scopingData": { ... },
  "transcript": "...",
  "timestamp": "..."
}
```

---

### What is NOT Possible Programmatically

#### ❌ **Cannot Create/Modify Agents via API**

```typescript
// This does NOT exist
const agent = await voiceflow.createAgent({
  name: "My Scoping Agent",
  steps: [...]
});
// → Voiceflow doesn't provide this endpoint
```

**Why?**
- Agent design is complex and requires UI/UX decisions
- Visual flow/canvas requires interactive design
- No standard format for serializing Voiceflow workflows
- Would increase API complexity significantly

#### ❌ **Cannot Programmatically Build Conversation Flows**

```typescript
// This does NOT work
const flow = {
  steps: [
    { type: "speak", text: "What's your project name?" },
    { type: "listen", variable: "project_name" }
  ]
};

await voiceflow.createWorkflow(flow);
// → Not supported
```

#### ❌ **Cannot Dynamically Modify Agent Canvas**

Once published, you cannot change questions, logic, or flow via API.
You must:
1. Edit in Voiceflow Creator
2. Publish new version
3. Update agent ID in your code

---

## Recommended Architecture

### The Hybrid Approach

**Design Phase (Manual + Voiceflow Creator)**
```
Your Requirements
    ↓
Use scoping-agent-template.json as starting point
    ↓
Import into Voiceflow Creator
    ↓
Customize questions/logic in UI
    ↓
Publish and get Agent ID
```

**Deployment Phase (Programmatic + APIs)**
```
Voiceflow Agent (Published)
    ↓
Dialog Manager API
    ↓
Your Backend (TypeScript/Python SDK)
    ↓
Google Meet Integration
    ↓
Database & Document Generation
```

### Why This Approach Works

1. **Flexibility** - UI design is best for conversation modeling
2. **Maintainability** - Changes visible in Voiceflow dashboard
3. **Scalability** - APIs handle millions of conversations
4. **Integration** - Custom backend logic between agent and systems
5. **Analytics** - Centralized tracking and monitoring

---

## Alternative Solutions You Might Consider

### If You Need Programmatic Workflow Creation

#### Option 1: Use Voiceflow as Backend, Build Custom UI
```
Custom Chat UI (React/Vue)
    ↓
Your Backend API
    ↓
Voiceflow Dialog Manager API
    ↓
Business Logic in Your Code
```

**Pros:** Full control, custom UX
**Cons:** More complex, need to build conversation logic

#### Option 2: Use Voiceflow's Native Chat Widget
```
Google Meet
    ↓
Voiceflow Chat Widget (embedded)
    ↓
Auto-managed by Voiceflow
```

**Pros:** Simplest to implement
**Cons:** Limited customization

#### Option 3: Use Lower-Level APIs (Custom Development)
Build your own conversation engine using:
- OpenAI API
- Anthropic (Claude) API
- LangChain framework

```python
# Pseudo-code
class ScopingAgent:
    async def process(self, user_message):
        response = await claude.call(
            system=self.system_prompt,
            history=self.conversation_history,
            message=user_message
        )

        # Parse response for data extraction
        extracted_data = parse_structured_output(response)

        # Validate
        if self.is_complete(extracted_data):
            return "COMPLETE"

        return response
```

**Pros:** Maximum flexibility and control
**Cons:** Need to implement NLP, validation, state management

---

## Current Voiceflow API Capabilities

### Available Endpoints

```
Dialog Manager
├── POST   /state/user/{userId}/interact          ✅
├── GET    /state/user/{userId}                   ✅
├── PUT    /state/user/{userId}                   ✅
├── PATCH  /state/user/{userId}                   ✅
└── DELETE /state/user/{userId}                   ✅

Knowledge Base
├── POST   /knowledge-base/docs                   ✅
├── GET    /knowledge-base/docs                   ✅
├── DELETE /knowledge-base/docs/{docId}           ✅
└── GET    /knowledge-base/search                 ✅

Transcripts
├── GET    /transcripts/{sessionId}               ✅
├── POST   /transcripts/{sessionId}               ✅
└── DELETE /transcripts/{sessionId}               ✅

Analytics
├── GET    /analytics/sessions                    ✅
├── GET    /analytics/conversations               ✅
└── GET    /analytics/metrics                     ✅

Project Management
├── GET    /projects/{projectId}                  ✅
├── GET    /projects/{projectId}/version          ✅
└── ... (others)                                  ✅

NOT AVAILABLE:
├── POST /projects                                ❌
├── POST /agents                                  ❌
├── PUT  /agents/{agentId}/canvas                 ❌
├── POST /agents/{agentId}/steps                  ❌
└── (No agent creation/modification)              ❌
```

---

## How This Skill Works Around This Limitation

### The Solution: Pre-built Template + Smart Integration

```json
// 1. Template (scoping-agent-template.json)
{
  "name": "Technical Project Scoping Agent",
  "sections": 7,
  "questions": 30+,
  "variables": 19,
  "webhooks": 2
}
    ↓ (Import manually into Voiceflow)
    ↓

// 2. Published Agent + Agent ID
VOICEFLOW_AGENT_ID=abc123xyz
    ↓ (Use in your app)
    ↓

// 3. Programmatic Integration
VoiceflowScoper SDK (TypeScript/Python)
    ├── Initialize sessions
    ├── Send/receive messages
    ├── Extract results
    └── Generate documents
    ↓

// 4. Google Meet Integration
GoogleMeetScopingIntegration
    ├── Register participants
    ├── Route messages
    ├── Track completion
    └── Export results
    ↓

// 5. Automation
Document generation + webhooks + analytics
```

### This Approach Provides

✅ **Pre-built conversation flow** - No need to code from scratch
✅ **Easy customization** - Edit in Voiceflow UI
✅ **Programmatic integration** - Use SDKs for deployment
✅ **Scalable** - Handle many concurrent sessions
✅ **Maintainable** - Changes in one place (Voiceflow)
✅ **Production-ready** - Error handling and monitoring included

---

## Future Possibilities

### What Could Enable Programmatic Agent Creation

If Voiceflow releases these APIs:

1. **Agent Builder API**
```typescript
const agent = await voiceflow.agents.create({
  name: "Scoping Agent",
  steps: [
    { type: "message", text: "...", next: "step2" },
    { type: "input", variable: "name", next: "step3" }
  ]
});
```

2. **Workflow Definition Language**
```yaml
agent:
  name: "Scoping Agent"
  steps:
    - id: greeting
      type: message
      text: "Hello!"
      next: project_basics
    - id: project_basics
      type: form
      fields: [projectName, client, timeline]
      next: summary
```

3. **Template Instantiation API**
```typescript
const agent = await voiceflow.templates.instantiate(
  "scoping-agent",
  { customQuestions: [...] }
);
```

---

## Conclusion

### For Your Use Case

**Build a Voiceflow scoping agent for Google Meet:**

1. **Design in Voiceflow Creator** (use template as reference)
2. **Deploy via Dialog Manager API** (programmatically)
3. **Integrate with Google Meet** (custom UI or extension)
4. **Automate backend logic** (document generation, webhooks, etc.)

This skill provides everything you need for this architecture.

### If You Need Programmatic Workflow Creation

You have three options:
1. **Wait for Voiceflow to release Agent APIs** (not available currently)
2. **Build custom conversation logic** with Claude/OpenAI APIs
3. **Use rule-based system** with templating and variable substitution

---

## Resources

- **Voiceflow API Docs:** https://docs.voiceflow.com/reference/api-overview
- **Dialog Manager API:** https://docs.voiceflow.com/reference/api-reference
- **Feature Requests:** Submit at https://feedback.voiceflow.com
- **This Skill:** See README.md and SETUP.md in this directory

---

**Last Updated:** 2025-12-13
**Voiceflow API Version:** Latest (as of Dec 2025)
