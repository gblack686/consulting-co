# Voiceflow Google Meet Technical Scoping Agent

Build conversational AI agents that guide technical project scoping calls in Google Meet. Collect required information, validate completeness, and automatically generate scoping documents.

## Overview

This directory contains everything you need to deploy a Voiceflow-powered scoping agent for Google Meet:

- **VOICEFLOW_SKILL.md** - Comprehensive guide on what's possible with Voiceflow APIs and architecture patterns
- **voiceflow-scoper.ts** - TypeScript SDK for interacting with Voiceflow agents
- **google-meet-integration.ts** - Google Meet integration patterns and Chrome extension example
- **scoping-agent-template.json** - Agent configuration template ready to import into Voiceflow Creator

## Quick Start

### 1. Create Agent in Voiceflow Creator

1. Go to [creator.voiceflow.com](https://creator.voiceflow.com)
2. Create a new "Agent" project
3. Use `scoping-agent-template.json` as a reference (import or manually recreate)
4. Customize questions for your specific needs
5. Publish and note the **Agent ID**

### 2. Get API Credentials

Your Voiceflow API key should be stored in AWS KMS. Retrieve it:

```bash
aws secretsmanager get-secret-value \
  --secret-id gbautomation/core/voiceflow-api-key \
  --region us-east-1 \
  --query 'SecretString' \
  --output text
```

Or add to your `.env`:
```
VOICEFLOW_API_KEY=your_api_key_here
VOICEFLOW_AGENT_ID=your_agent_id_here
```

### 3. Install Dependencies

```bash
npm install axios typescript
# or
pip install requests
```

### 4. Start Using the SDK

**Node.js/TypeScript:**
```typescript
import { VoiceflowScoper, GoogleMeetScopingIntegration } from './voiceflow-scoper';

const scoper = new VoiceflowScoper(
  process.env.VOICEFLOW_API_KEY!,
  process.env.VOICEFLOW_AGENT_ID!
);

// Initialize session
await scoper.initializeSession('participant_123', {
  meetingId: 'meet-abc-xyz',
  participantName: 'John Doe'
});

// Send message
const response = await scoper.sendMessage('participant_123', 'Hello');

// Get collected data
const scopingData = await scoper.getScopingData('participant_123');
```

**Python:**
```python
from voiceflow_scoper import VoiceflowScoper

scoper = VoiceflowScoper(
    api_key=os.getenv("VOICEFLOW_API_KEY"),
    agent_id=os.getenv("VOICEFLOW_AGENT_ID")
)

await scoper.initialize_session("participant_123")
response = await scoper.send_message("participant_123", "Hello")
data = scoper.get_scoping_data("participant_123")
```

## Architecture Patterns

### Pattern 1: Real-Time Chat Widget (Recommended for MVP)

Embed Voiceflow chat widget directly in Google Meet side panel:

```
Google Meet Browser
├── Main Video Area
└── Voiceflow Chat Panel (Right Side)
    ├── Agent Messages
    ├── User Input
    └── Auto-Submit Answers
```

**Implementation:**
- Use Google Meet Chrome Extension API
- Inject Voiceflow chat widget in meeting page
- Bind user responses to Voiceflow Dialog Manager API

See `google-meet-integration.ts` → `GoogleMeetChromeExtension` class

### Pattern 2: Dedicated Companion Tab

Open Voiceflow in separate browser tab alongside Google Meet:

```
Tab 1: Google Meet                  Tab 2: Voiceflow Scoper
├── Video Conference                ├── Project Scoping Chat
├── Participant List                ├── Question Progress
└── Chat/Messages                   └── Submit Answers
```

**Implementation:**
- Simple HTTP API to start scoping session
- Participant IDs linked to Google Meet via browser session
- Responses saved to backend

### Pattern 3: Voice-First via Phone

Schedule scoping calls as dedicated phone conversations:

```
Pre-scheduled Phone Call
├── Voiceflow Voice Agent
├── Real-Time Transcription
└── Transcript/Summary Saved
```

**Implementation:**
- Use Voiceflow's phone integration
- Schedule before/after Google Meet
- Transcripts captured via Voiceflow Transcripts API

### Pattern 4: Post-Meeting Recording Analysis

Analyze Google Meet recording with Voiceflow:

```
Google Meet Recording
├── Upload to Cloud Storage
├── Extract Transcript
├── Voiceflow Processing
└── Auto-Generate Scoping Doc
```

## File Reference

### VOICEFLOW_SKILL.md
- Explains API limitations (what IS and ISN'T possible programmatically)
- Documents scoping agent workflow
- Provides Node.js and Python integration examples
- Lists best practices for conversation design
- Includes resource links

### voiceflow-scoper.ts
Main SDK classes:

- **VoiceflowScoper** - Core agent interaction
  - `initializeSession()` - Start new conversation
  - `sendMessage()` - Send user input
  - `getScopingData()` - Extract collected information
  - `isComplete()` - Check if required data is collected

- **GoogleMeetScopingIntegration** - Meet-specific helpers
  - `registerParticipant()` - Add meeting attendee
  - `unregisterParticipant()` - Remove attendee and collect data
  - `processUserInput()` - Handle meeting messages
  - `checkMeetingCompletion()` - Get overall status
  - `exportMeetingResults()` - Export for reporting

- **ScopingDocumentGenerator** - Create output documents
  - `generateMarkdown()` - Create .md report
  - `generateJSON()` - Create structured JSON

### google-meet-integration.ts
Integration examples:

- **GoogleMeetScopingSession** - Main orchestrator
  - Manages participant lifecycle
  - Routes messages to Voiceflow
  - Emits events (joined, left, completed, error)

- **GoogleMeetChromeExtension** - Browser extension implementation
  - Creates chat UI in Google Meet
  - Injects into page dynamically
  - Handles real-time participant tracking

- Example `startScopingSession()` function

### scoping-agent-template.json
Pre-configured agent with:
- 7 conversation sections
- 20+ guided questions
- Variable definitions
- Validation rules
- Webhook endpoints
- Conversation flow logic

Customize by:
1. Importing into Voiceflow Creator
2. Editing questions/sections
3. Adjusting validation rules
4. Setting webhook URLs

## Integration with Your Stack

### Backend API Setup

Expected endpoints for webhooks:

```typescript
// POST /api/scoping/complete
{
  agentId: string;
  userId: string;
  scopingData: {
    projectName: string;
    client: string;
    timeline: string;
    budget: string;
    techStack: string[];
    mvpFeatures: string[];
    // ... all collected fields
  };
  transcript: string;
  duration: number; // minutes
  timestamp: string; // ISO 8601
}

// POST /api/scoping/abandoned
{
  agentId: string;
  userId: string;
  completedSections: string[];
  lastQuestion: string;
  timestamp: string;
}
```

### Database Schema

```sql
-- Scoping sessions
CREATE TABLE scoping_sessions (
  id UUID PRIMARY KEY,
  meeting_id VARCHAR(100),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status VARCHAR(20), -- 'active', 'completed', 'abandoned'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Collected scoping data
CREATE TABLE scoping_data (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES scoping_sessions(id),
  participant_id VARCHAR(100),
  project_name TEXT,
  client TEXT,
  timeline TEXT,
  budget TEXT,
  tech_stack JSONB,
  mvp_features JSONB,
  constraints JSONB,
  success_metrics JSONB,
  raw_data JSONB, -- Full response
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Considerations

### API Keys

- ✅ Store in AWS KMS (already configured)
- ✅ Never commit to git
- ✅ Rotate periodically
- ❌ Don't share or expose in client code

### Data Privacy

- Voiceflow automatically encrypts conversations in transit
- Transcripts are stored by Voiceflow
- PII (project names, client details) should be encrypted at rest
- Implement data retention policies

### Authentication

Google Meet integration should:
- Verify participant identity before starting scoping
- Use OAuth 2.0 with Google
- Verify meeting ownership/participant list
- Log all scoping session activities

Example:
```typescript
// Verify user is actually in the Google Meet
const participant = await verifyGoogleMeetParticipant(
  meetingId,
  userId,
  googleTokens
);
```

## Troubleshooting

### Agent not responding

1. Verify Agent ID in `VOICEFLOW_AGENT_ID`
2. Check API key has correct permissions
3. Ensure agent is published in Voiceflow Creator
4. Test with Voiceflow CLI: `voiceflow test`

### Messages not being saved

1. Check webhook URLs in agent config
2. Verify backend endpoints are reachable
3. Enable Voiceflow request logging
4. Check for network errors in browser console

### Google Meet integration not loading

1. Verify Chrome extension manifest (if using extension approach)
2. Check for content security policy violations
3. Ensure Meet API permissions granted
4. Test in isolated window first

## Testing

### Unit Tests (TypeScript)
```bash
npm install --save-dev jest ts-jest @types/jest
npm test
```

### Integration Tests
```bash
# Test with real Voiceflow agent
npm run test:integration
```

### End-to-End Test
1. Create test meeting in Google Meet
2. Add participants
3. Run through full scoping conversation
4. Verify data collection
5. Check webhook received data
6. Validate generated document

## Next Steps

1. **Create Agent** - Import template into Voiceflow Creator
2. **Configure Webhooks** - Update webhook URLs to your backend
3. **Deploy SDK** - Install `voiceflow-scoper.ts` in your app
4. **Choose Integration** - Pick one pattern from Architecture section
5. **Run Pilot** - Test with 3-5 practice scoping calls
6. **Iterate** - Refine questions based on feedback
7. **Go Live** - Deploy to production

## Resources

- **Voiceflow Documentation**: https://docs.voiceflow.com
- **Dialog Manager API**: https://docs.voiceflow.com/reference/api-overview
- **Google Meet API**: https://developers.google.com/meet
- **Google Meet Chat API**: https://developers.google.com/meet/chat/api
- **Voiceflow CLI**: https://docs.voiceflow.com/docs/voiceflow-cli

## Support

For issues with:
- **Voiceflow Agent Design**: Check VOICEFLOW_SKILL.md
- **SDK Integration**: Review examples in voiceflow-scoper.ts
- **Google Meet Integration**: See google-meet-integration.ts
- **API Errors**: Check Voiceflow dashboard and logs

## License

This skill is part of the consulting-co project.

---

**Last Updated:** 2025-12-13
