# Voiceflow Scoping Agent - Setup Guide

Complete step-by-step guide to deploy the technical scoping agent for Google Meet.

## Prerequisites

- ✅ Voiceflow account (free tier or higher)
- ✅ Google Meet account
- ✅ AWS account with KMS access
- ✅ Node.js 18+ (for TypeScript SDK)
- ✅ Backend API (for webhook integration)

## Step 1: Create Voiceflow Agent

### 1.1 Create New Project

1. Go to [creator.voiceflow.com](https://creator.voiceflow.com)
2. Click **"Create Project"**
3. Select **"Agent"** as project type
4. Name: `Technical Project Scoping Agent`
5. Click **"Create"**

### 1.2 Import Template

The `scoping-agent-template.json` file provides the conversation flow. You have two options:

**Option A: Manual Recreation (Recommended for customization)**

1. In Voiceflow Creator, use the template as reference
2. Create 7 sections (Greeting, Project Basics, Technical, Scope, Resources, Success, Summary)
3. Add steps for each question
4. Set up variables for each data point
5. Configure validation rules

**Option B: Import JSON (If supported)**

1. Some Voiceflow versions support JSON import
2. Export from template: `scoping-agent-template.json`
3. Look for import option in Voiceflow Creator
4. Follow prompts to map variables and flows

### 1.3 Configure Variables

In Voiceflow Canvas, set up these variables:

```
project_name (string, required)
client_name (string, required)
timeline (string, required)
budget (string, required)
tech_stack (string, required)
integrations (string, optional)
scale_requirements (string, optional)
security_requirements (string, optional)
mvp_features (string, required)
nice_to_have_features (string, optional)
out_of_scope (string, optional)
team_size (string, optional)
existing_infrastructure (string, optional)
technical_debt (string, optional)
third_party_dependencies (string, optional)
success_metrics (string, required)
launch_date (string, required)
post_launch_support (string, optional)
stakeholder_signoff (string, optional)
final_comments (string, optional)
```

### 1.4 Test Conversation Flow

1. Click **"Test"** in Voiceflow Creator
2. Go through entire conversation
3. Verify all questions are asked
4. Check variable collection
5. Test different answer paths
6. Verify summary is accurate

### 1.5 Publish Agent

1. Click **"Publish"** button
2. Select version to publish
3. Note the **Agent ID** (you'll need this)
4. Copy this format: `your-agent-id`

## Step 2: Store API Credentials in AWS KMS

### 2.1 Create Voiceflow API Key

1. In Voiceflow, go to **Settings > API Credentials**
2. Generate new API key
3. Copy the key (you won't see it again)

### 2.2 Store in AWS Secrets Manager

```bash
# Store Voiceflow API key
aws secretsmanager create-secret \
  --name gbautomation/core/voiceflow-api-key \
  --description "Voiceflow API Key for scoping agents" \
  --secret-string "your_api_key_here" \
  --region us-east-1 \
  --tags Key=Organization,Value=gbautomation Key=Service,Value=voiceflow
```

Or use the script in `.claude/context/`:

```bash
chmod +x .claude/context/store-credentials-to-kms.sh
./.claude/context/store-credentials-to-kms.sh
```

### 2.3 Verify Storage

```bash
aws secretsmanager get-secret-value \
  --secret-id gbautomation/core/voiceflow-api-key \
  --region us-east-1 \
  --query 'SecretString' \
  --output text
```

Should return your API key without any issues.

## Step 3: Configure Backend Webhooks

### 3.1 Backend API Setup

Add these endpoints to your backend:

```typescript
// backend/routes/scoping.ts
import express from 'express';

const router = express.Router();

// Webhook: Agent completed scoping
router.post('/api/scoping/complete', async (req, res) => {
  const { agentId, userId, scopingData, transcript, duration, timestamp } = req.body;

  // Store in database
  await db.scoping_sessions.create({
    voiceflow_agent_id: agentId,
    user_id: userId,
    scoping_data: scopingData,
    transcript,
    duration,
    status: 'completed',
    created_at: new Date(timestamp)
  });

  // Generate document
  const document = await generateScopingDocument(scopingData);

  // Send to stakeholders
  await sendDocumentToStakeholders(scopingData.stakeholder_signoff, document);

  res.json({ success: true, documentId: document.id });
});

// Webhook: Agent abandoned (incomplete)
router.post('/api/scoping/abandoned', async (req, res) => {
  const { agentId, userId, completedSections, timestamp } = req.body;

  // Store incomplete session
  await db.scoping_sessions.create({
    voiceflow_agent_id: agentId,
    user_id: userId,
    completed_sections: completedSections,
    status: 'abandoned',
    created_at: new Date(timestamp)
  });

  // Follow up
  await sendFollowUpEmail(userId);

  res.json({ success: true });
});

export default router;
```

### 3.2 Update Webhooks in Voiceflow Agent

1. In Voiceflow Creator, go to **Agent Settings > Webhooks**
2. Add completion webhook:
   ```
   URL: https://your-backend.com/api/scoping/complete
   Method: POST
   Trigger: On agent completion
   ```
3. Add abandonment webhook:
   ```
   URL: https://your-backend.com/api/scoping/abandoned
   Method: POST
   Trigger: On agent abandon
   ```
4. Test webhooks with sample payloads

## Step 4: Setup SDK Integration

### 4.1 Install Dependencies

```bash
npm install axios typescript dotenv
```

### 4.2 Create Environment File

```bash
# .env or .env.local
VOICEFLOW_API_KEY=sk-xxx-yyy-zzz
VOICEFLOW_AGENT_ID=agent-id-here
VOICEFLOW_BASE_URL=https://general-runtime.voiceflow.com
```

### 4.3 Copy SDK Files

```bash
# Copy to your project
cp voiceflow-scoper.ts src/integrations/
cp google-meet-integration.ts src/integrations/

# Or use via npm (if published)
npm install @voiceflow/scoping-agent
```

### 4.4 Initialize in Your App

```typescript
// src/services/scoping.ts
import { VoiceflowScoper } from './integrations/voiceflow-scoper';

const scoper = new VoiceflowScoper(
  process.env.VOICEFLOW_API_KEY!,
  process.env.VOICEFLOW_AGENT_ID!
);

export default scoper;
```

## Step 5: Integrate with Google Meet

Choose one of these patterns:

### Pattern A: Chrome Extension (Recommended)

1. Create `manifest.json`:
   ```json
   {
     "manifest_version": 3,
     "name": "Voiceflow Scoping Agent",
     "version": "1.0",
     "permissions": [
       "scripting",
       "activeTab"
     ],
     "action": {
       "default_popup": "popup.html"
     },
     "content_scripts": [
       {
         "matches": ["https://meet.google.com/*"],
         "js": ["content.js"]
       }
     ]
   }
   ```

2. Create `content.js` (inject Voiceflow into Meet):
   ```javascript
   import { GoogleMeetChromeExtension } from './google-meet-integration.ts';

   const extension = new GoogleMeetChromeExtension();
   extension.initialize(
     process.env.VOICEFLOW_API_KEY,
     process.env.VOICEFLOW_AGENT_ID
   );
   ```

3. Load extension in Chrome:
   - Go to `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select this directory

### Pattern B: Backend Integration

```typescript
// POST /api/meetings/:meetingId/scoping
router.post('/api/meetings/:meetingId/scoping', async (req, res) => {
  const { participantId, participantName } = req.body;

  const session = await startScopingSession(
    req.params.meetingId,
    process.env.VOICEFLOW_API_KEY,
    process.env.VOICEFLOW_AGENT_ID
  );

  await session.onParticipantJoined(participantId, participantName);

  res.json({ sessionId: session.id });
});
```

### Pattern C: Embedded Chat Widget

Use Voiceflow's native chat widget:

```html
<script src="https://cdn.voiceflow.com/chat.js"></script>
<script>
  window.voiceflowChat.load({
    verify: { projectID: 'YOUR_PROJECT_ID' },
    url: 'https://general-runtime.voiceflow.com',
    versionID: 'production'
  });
</script>
```

## Step 6: Test Deployment

### 6.1 Unit Tests

```bash
# Create test file
cat > tests/voiceflow-scoper.test.ts << 'EOF'
import { VoiceflowScoper } from '../voiceflow-scoper';

describe('VoiceflowScoper', () => {
  let scoper: VoiceflowScoper;

  beforeEach(() => {
    scoper = new VoiceflowScoper(
      process.env.VOICEFLOW_API_KEY!,
      process.env.VOICEFLOW_AGENT_ID!
    );
  });

  test('should initialize session', async () => {
    const response = await scoper.initializeSession('test-user-1');
    expect(response.state).toBeDefined();
  });

  test('should send message', async () => {
    await scoper.initializeSession('test-user-2');
    const response = await scoper.sendMessage('test-user-2', 'Test project');
    expect(response.trace).toBeDefined();
  });

  test('should collect scoping data', async () => {
    await scoper.initializeSession('test-user-3');
    const data = await scoper.getScopingData('test-user-3');
    expect(data).toBeDefined();
  });
});
EOF

npm test
```

### 6.2 Integration Test

```bash
# Test with real Google Meet
1. Create test meeting
2. Add test participants
3. Run through scoping conversation
4. Verify data collected
5. Check webhook received data
6. Validate generated document
```

### 6.3 End-to-End Test Script

```bash
# tests/e2e-scoping.sh
#!/bin/bash

echo "Starting E2E test..."

# 1. Initialize session
SESSION=$(curl -X POST http://localhost:3000/api/scoping/init \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user","meetingId":"test-meet"}')

echo "Session: $SESSION"

# 2. Send messages
curl -X POST http://localhost:3000/api/scoping/message \
  -H "Content-Type: application/json" \
  -d '{"userId":"test-user","message":"My project"}'

# 3. Get data
DATA=$(curl http://localhost:3000/api/scoping/data?userId=test-user)

echo "Collected data: $DATA"

# 4. Verify
if [ -z "$DATA" ]; then
  echo "FAILED: No data collected"
  exit 1
fi

echo "PASSED: E2E test successful"
```

## Step 7: Go Live

### 7.1 Production Checklist

- [ ] API key securely stored in AWS KMS
- [ ] Webhook URLs configured in Voiceflow
- [ ] Backend endpoints deployed and tested
- [ ] Google Meet integration working
- [ ] Error logging configured
- [ ] Database backups enabled
- [ ] GDPR/privacy policies updated
- [ ] User testing completed
- [ ] Documentation created for support team

### 7.2 Monitoring

```typescript
// Monitor agent usage
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration
    });
  });
  next();
});
```

### 7.3 Performance Optimization

```typescript
// Cache agent responses
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 3600 });

// Cache scoping data lookups
const cachedScopingData = cache.get(`scoping:${userId}`);
if (cachedScopingData) return cachedScopingData;
```

## Troubleshooting

### Issue: Agent not initializing

**Solution:**
```bash
# 1. Verify agent is published
voiceflow test --projectId YOUR_AGENT_ID

# 2. Check API key is valid
curl -H "Authorization: YOUR_API_KEY" \
  https://general-runtime.voiceflow.com/health

# 3. Verify network connectivity
ping general-runtime.voiceflow.com
```

### Issue: Webhooks not firing

**Solution:**
1. Check webhook URL is accessible from internet
2. Add logging to webhook endpoint
3. Test webhook manually in Voiceflow
4. Check firewall/security groups

### Issue: Google Meet integration not loading

**Solution:**
1. Check Chrome extension permissions
2. Verify Content Security Policy
3. Test in incognito window
4. Check browser console for errors

## Next Steps

1. **Run through full setup** (20-30 minutes)
2. **Test with practice call** (10 minutes)
3. **Refine conversation** (based on feedback)
4. **Train support team** (on using system)
5. **Launch to users** (beta group first)
6. **Monitor and optimize** (ongoing)

## Support Resources

- Voiceflow Docs: https://docs.voiceflow.com
- API Reference: https://docs.voiceflow.com/reference/api-overview
- Google Meet Dev: https://developers.google.com/meet
- This directory: `/voiceflow/`

## Questions?

Refer back to:
- **VOICEFLOW_SKILL.md** - Architecture and API details
- **README.md** - Quick reference
- **voiceflow-scoper.ts** - SDK examples
- **google-meet-integration.ts** - Integration patterns

---

**Setup Time Estimate:** 2-3 hours for initial deployment + 1-2 weeks for refinement

