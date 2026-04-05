# Voiceflow Google Meet Technical Scoping Agent Skill

## Overview

This skill enables you to create conversational AI agents for Google Meet that help plan and scope technical projects by collecting structured information through guided conversations.

## Important Clarification: What's Possible Programmatically

**Current Voiceflow API Limitations:**
- ❌ **Cannot create agents from code** - Voiceflow's public API doesn't provide agent creation endpoints
- ❌ **Cannot build workflows programmatically** - Agent design must be done in Voiceflow Creator UI
- ✅ **Can interact with agents** - Dialog Manager API for running conversations
- ✅ **Can deploy agents** - Custom channels and integrations
- ✅ **Can manage conversations** - Transcripts, analytics, state management
- ✅ **Can integrate with Google Meet** - Via custom interfaces and webhooks

## Architecture: Hybrid Approach

The recommended approach is:

1. **Design Phase (Manual)**: Build your scoping agent in Voiceflow Creator UI using best practices
2. **Deployment Phase (Programmatic)**: Use Voiceflow APIs to deploy and manage the agent
3. **Integration Phase (Programmatic)**: Use Dialog Manager API to integrate with Google Meet
4. **Analytics Phase (Programmatic)**: Use Analytics API to extract insights from scoping calls

## Workflow: Technical Project Scoping Agent

### Agent Objectives
- Collect required information before ending the call
- Guide conversations through structured sections
- Validate completeness of information
- Generate scoping documents automatically

### Required Information to Collect

```
Scoping Call Checklist:
├── Project Basics
│   ├── Project name
│   ├── Client/stakeholder
│   ├── Timeline/deadline
│   └── Budget constraints
├── Technical Requirements
│   ├── Technology stack preferences
│   ├── Integration needs
│   ├── Scale/performance requirements
│   └── Data/security requirements
├── Scope & Deliverables
│   ├── MVP definition
│   ├── Must-have features
│   ├── Nice-to-have features
│   └── Out-of-scope items
├── Resources & Constraints
│   ├── Team size available
│   ├── Existing infrastructure/systems
│   ├── Known technical debt
│   └── Third-party dependencies
└── Success Criteria
    ├── Key metrics
    ├── Launch date
    ├── Post-launch support
    └── Stakeholder sign-off
```

### Conversation Flow Design

Build this flow in Voiceflow Creator:

```
START
  ↓
[Greeting & Intro]
  "Hi! I'm your technical scoping assistant. Let's plan your project together."
  ↓
[Loop through each section]
  ├─→ [Ask Section Questions]
  │    └─→ [Collect answers with validation]
  │         ├─→ [If incomplete] → [Ask clarifying questions]
  │         └─→ [If complete] → [Move to next section]
  ├─→ [Summarize collected info]
  └─→ [Confirmation prompts]
  ↓
[Completion Check]
  ├─→ [All sections complete?]
  │    ├─→ [YES] → [Generate summary] → [END]
  │    └─→ [NO] → [Ask which section to revisit] → [Loop]
  ↓
[Export results]
  ├─→ [Save transcript]
  ├─→ [Generate scoping document]
  └─→ [Send to stakeholders]
```

## Getting Started

### Step 1: Create Agent in Voiceflow Creator

1. Go to [creator.voiceflow.com](https://creator.voiceflow.com)
2. Create a new "Agent" project
3. Import template: `scoping-agent-template.json` (provided in this directory)
4. Customize questions and sections for your needs
5. Publish the agent and note the Agent ID

### Step 2: Set Up Google Meet Integration

Use the Voiceflow Dialog Manager API with Google Meet via:

Option A: Custom Chat Widget
- Embed Voiceflow chat widget in Google Meet side panel
- Use Chrome extensions like "Custom Chat"

Option B: Direct API Integration
- Use Voiceflow's Dialog Manager API
- Create Google Meet companion app that calls Dialog Manager

Option C: Third-Party Integration (Recommended for MVP)
- Use Make.com or n8n to connect Voiceflow → Google Meet
- Trigger agent on meeting start
- Send transcripts to Slack/Email

### Step 3: Configure Webhooks & Callbacks

In your Voiceflow agent, set up webhooks to:

1. **On Completion**: POST scoping data to your backend
   ```
   POST /api/scoping/complete
   {
     agentId: string
     userId: string
     scopingData: object
     transcript: string
   }
   ```

2. **On Abandonment**: Track incomplete scoping calls
   ```
   POST /api/scoping/abandoned
   {
     agentId: string
     userId: string
     completedSections: string[]
   }
   ```

## Programmatic Integration (Node.js/Python Examples)

### Interact with Voiceflow Agent (Dialog Manager API)

**Node.js:**
```javascript
const axios = require('axios');

class VoiceflowScoper {
  constructor(apiKey, agentId) {
    this.apiKey = apiKey;
    this.agentId = agentId;
    this.baseURL = 'https://general-runtime.voiceflow.com';
    this.sessionId = null;
  }

  async initializeSession(userId) {
    const response = await axios.post(
      `${this.baseURL}/state/user/${userId}/interact`,
      {},
      {
        headers: { Authorization: this.apiKey },
        params: { projectID: this.agentId }
      }
    );
    return response.data;
  }

  async sendMessage(userId, userMessage) {
    const response = await axios.post(
      `${this.baseURL}/state/user/${userId}/interact`,
      { action: { type: 'text', payload: userMessage } },
      {
        headers: { Authorization: this.apiKey },
        params: { projectID: this.agentId }
      }
    );
    return response.data;
  }

  async getScopingData(userId) {
    const response = await axios.get(
      `${this.baseURL}/state/user/${userId}`,
      {
        headers: { Authorization: this.apiKey },
        params: { projectID: this.agentId }
      }
    );
    return response.data.variables;
  }
}

// Usage
const scoper = new VoiceflowScoper(
  process.env.VOICEFLOW_API_KEY,
  process.env.VOICEFLOW_AGENT_ID
);

// In Google Meet context
async function runScopingCall(meetingId, participantId) {
  await scoper.initializeSession(participantId);

  // Agent guides the conversation automatically
  // You listen for state changes and extract data

  const scopingData = await scoper.getScopingData(participantId);
  return scopingData;
}
```

**Python:**
```python
import requests
import json

class VoiceflowScoper:
    def __init__(self, api_key: str, agent_id: str):
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = "https://general-runtime.voiceflow.com"

    def initialize_session(self, user_id: str):
        headers = {"Authorization": self.api_key}
        params = {"projectID": self.agent_id}
        response = requests.post(
            f"{self.base_url}/state/user/{user_id}/interact",
            headers=headers,
            params=params
        )
        return response.json()

    def send_message(self, user_id: str, message: str):
        headers = {"Authorization": self.api_key}
        params = {"projectID": self.agent_id}
        payload = {"action": {"type": "text", "payload": message}}
        response = requests.post(
            f"{self.base_url}/state/user/{user_id}/interact",
            json=payload,
            headers=headers,
            params=params
        )
        return response.json()

    def get_scoping_data(self, user_id: str):
        headers = {"Authorization": self.api_key}
        params = {"projectID": self.agent_id}
        response = requests.get(
            f"{self.base_url}/state/user/{user_id}",
            headers=headers,
            params=params
        )
        return response.json().get("variables", {})

# Usage
scoper = VoiceflowScoper(
    api_key=os.getenv("VOICEFLOW_API_KEY"),
    agent_id=os.getenv("VOICEFLOW_AGENT_ID")
)

async def run_scoping_call(meeting_id: str, participant_id: str):
    await scoper.initialize_session(participant_id)
    data = scoper.get_scoping_data(participant_id)
    return data
```

## Google Meet Integration Patterns

### Pattern 1: Meeting Recording + Post-Processing
```
Google Meet Recording → Voiceflow Transcripts API → NLP Analysis → Scoping Document
```

### Pattern 2: Real-Time Chat Widget
```
Google Meet → Chrome Extension → Voiceflow Chat Widget → Dialog Manager API
```

### Pattern 3: Dedicated Companion Tab
```
Google Meet Call → Open Voiceflow in companion tab → Dialog Manager API
Participant answers questions in tab while video is on
```

### Pattern 4: Voice-First (Phone Integration)
```
Scheduled before/after Google Meet → Voiceflow Phone Agent → Phone number dial-in
Transcripts stored in Voiceflow → Analytics API
```

## Example: Generate Scoping Document from Agent Data

**After agent collects info:**

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

async function generateScopingDoc(scopingData: any) {
  const prompt = `Generate a technical scoping document from the following collected information:

Project Name: ${scopingData.projectName}
Client: ${scopingData.client}
Timeline: ${scopingData.timeline}
Budget: ${scopingData.budget}

Technical Requirements:
${scopingData.techRequirements}

Scope & Deliverables:
${scopingData.deliverables}

Resources:
${scopingData.resources}

Success Criteria:
${scopingData.successCriteria}

Format as a professional scoping document with sections for:
- Executive Summary
- Project Overview
- Technical Architecture
- Scope & Deliverables
- Success Metrics
- Timeline & Milestones
- Resource Requirements
- Risk Assessment`;

  const response = await client.messages.create({
    model: "claude-3-5-sonnet-20241022",
    max_tokens: 2000,
    messages: [{ role: "user", content: prompt }]
  });

  return response.content[0].type === "text" ? response.content[0].text : "";
}
```

## Best Practices

1. **Conversation Design**
   - Keep questions clear and specific
   - Provide examples and clarifications
   - Use conditional logic to skip irrelevant questions
   - Periodically summarize collected information

2. **Information Validation**
   - Confirm understanding before moving forward
   - Ask follow-up questions if answers are vague
   - Detect contradictions and resolve them
   - Require explicit confirmation of final summary

3. **Fallback Handling**
   - Have escalation paths to human agents
   - Provide "I don't know" options
   - Allow going back to previous sections
   - Save progress in case of disconnection

4. **Google Meet Specific**
   - Keep UI minimal to not distract from meeting
   - Use side-by-side layout if possible
   - Sync with meeting duration
   - Save transcript alongside recording

## Testing Your Agent

### Before Google Meet Deployment

1. **Test in Voiceflow Simulator**
   - Run through all conversation paths
   - Test edge cases and fallbacks
   - Verify all questions are asked
   - Check data validation

2. **API Testing**
   ```bash
   # Test agent interaction
   curl -X POST https://general-runtime.voiceflow.com/state/user/test123/interact \
     -H "Authorization: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"action": {"type": "text", "payload": "Hello"}}' \
     -G -d "projectID=YOUR_AGENT_ID"
   ```

3. **Full Integration Test**
   - Run 5+ practice scoping calls
   - Collect real feedback
   - Iterate on questions
   - Measure average call duration

## Resources

- **Voiceflow Docs**: https://docs.voiceflow.com
- **Dialog Manager API**: https://docs.voiceflow.com/reference/api-overview
- **Voiceflow GitHub Examples**: https://github.com/voiceflow
- **Google Meet API**: https://developers.google.com/meet

## Next Steps

1. Create agent in Voiceflow Creator using `scoping-agent-template.json`
2. Publish agent and get Agent ID
3. Set up Voiceflow API credentials (stored in AWS KMS)
4. Integrate Dialog Manager API into your application
5. Deploy Google Meet integration (choose pattern above)
6. Run pilot scoping calls and collect feedback
7. Iterate on conversation design based on results
