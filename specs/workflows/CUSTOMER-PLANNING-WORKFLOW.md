# Customer Planning Workflow Design
## Automated Scope of Work Generation & Approval System

### Executive Summary
Transform your Lightsail Claude Code instance into a customer-facing consultation and scope generation system that:
1. Answers customer questions via Claude API
2. Facilitates interactive planning sessions
3. Generates detailed scopes of work
4. Manages customer approval workflows
5. Tracks revisions and maintains history

---

## Architecture Overview

```
┌──────────────┐
│   Customer   │
│   Portal     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              API Gateway (HTTPS Endpoint)                │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│         Request Router Lambda (Node.js/Python)           │
│  • Authenticate customer                                 │
│  • Route to appropriate handler                          │
│  • Rate limiting & validation                            │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┬────────────────┐
       ▼                 ▼                 ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Q&A       │  │  Planning   │  │  Scope      │  │  Approval   │
│  Handler    │  │   Session   │  │ Generation  │  │   Handler   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│          Claude Code Orchestrator (Lightsail)            │
│  IP: 44.208.161.19                                       │
│  • SSH API wrapper service                               │
│  • Session management                                    │
│  • Log aggregation                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                  Storage & State                         │
│  • S3: Scope documents, transcripts                      │
│  • DynamoDB: Session state, approvals                    │
│  • SES: Email notifications                              │
└──────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Customer Portal (Frontend)

**Technology**: React + Next.js or simple HTML/JavaScript
**Hosting**: AWS Amplify or S3 + CloudFront
**Features**:
- Customer authentication (Cognito)
- Chat interface for Q&A
- Planning session interface
- Scope document review
- Approval/revision workflow
- History & downloads

**Key Pages**:
```
/login              → Customer authentication
/dashboard          → Active projects & history
/ask                → Q&A chat interface
/plan/:sessionId    → Planning session workspace
/scope/:scopeId     → Scope document review
/approve/:scopeId   → Approval workflow
```

### 2. API Gateway & Request Router

**Endpoints**:
```
POST   /api/v1/auth/login           → Authenticate customer
POST   /api/v1/ask                  → Submit question
POST   /api/v1/planning/start       → Start planning session
POST   /api/v1/planning/message     → Send planning message
GET    /api/v1/planning/:id/status  → Get session status
POST   /api/v1/scope/generate       → Generate scope from session
GET    /api/v1/scope/:id            → Get scope document
POST   /api/v1/scope/:id/approve    → Approve scope
POST   /api/v1/scope/:id/revise     → Request revisions
GET    /api/v1/history              → Get customer history
```

**Authentication Flow**:
1. Customer logs in via Cognito or JWT
2. Token included in all subsequent requests
3. Lambda validates token before processing
4. Customer ID used for session/document ownership

### 3. Claude Code Orchestrator Service

**Purpose**: Bridge between AWS services and Claude Code CLI on Lightsail
**Implementation**: Node.js/Python service running on Lightsail
**Port**: 3000 (HTTP API)

**Service Features**:
```javascript
// Example API structure
class ClaudeCodeOrchestrator {

  // Start a new Claude Code session
  async startSession(customerId, projectType) {
    // 1. Create new session directory
    // 2. Initialize Claude Code in headless mode
    // 3. Return session ID
  }

  // Send message to active session
  async sendMessage(sessionId, message) {
    // 1. Write message to session stdin
    // 2. Monitor stdout for response
    // 3. Return streaming response
  }

  // Get session transcript
  async getTranscript(sessionId) {
    // 1. Read .claude/debug/[sessionId].txt
    // 2. Parse and format transcript
    // 3. Return structured conversation
  }

  // Generate scope document
  async generateScope(sessionId, template) {
    // 1. Analyze session transcript
    // 2. Use Claude to extract requirements
    // 3. Fill scope template
    // 4. Return formatted document
  }

  // Stream responses in real-time
  async streamResponse(sessionId) {
    // WebSocket or Server-Sent Events
    // Stream Claude's response as it generates
  }
}
```

**Installation on Lightsail**:
```bash
# Install service dependencies
cd /home/ubuntu
mkdir claude-orchestrator
cd claude-orchestrator
npm init -y
npm install express body-parser ssh2 ws dotenv

# Create service
cat > server.js << 'EOF'
const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Session management
const sessions = new Map();

// Start new Claude Code session
app.post('/api/session/start', async (req, res) => {
  const { customerId, context } = req.body;
  const sessionId = `${customerId}-${Date.now()}`;

  // Start Claude Code in headless mode with print mode
  const claude = spawn('claude', ['-p', '--continue'], {
    cwd: '/home/ubuntu',
    env: { ...process.env }
  });

  sessions.set(sessionId, {
    process: claude,
    customerId,
    startTime: new Date(),
    messages: []
  });

  res.json({ sessionId });
});

// Send message to session
app.post('/api/session/message', async (req, res) => {
  const { sessionId, message } = req.body;
  const session = sessions.get(sessionId);

  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  // Write message to Claude stdin
  session.process.stdin.write(message + '\n');

  // Collect response
  let response = '';
  session.process.stdout.on('data', (data) => {
    response += data.toString();
  });

  // Return response after timeout or completion
  setTimeout(() => {
    session.messages.push({ role: 'user', content: message });
    session.messages.push({ role: 'assistant', content: response });
    res.json({ response });
  }, 2000);
});

// Get session transcript
app.get('/api/session/:id/transcript', async (req, res) => {
  const { id } = req.params;
  const session = sessions.get(id);

  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  res.json({ messages: session.messages });
});

// Generate scope document
app.post('/api/scope/generate', async (req, res) => {
  const { sessionId, template } = req.body;
  const session = sessions.get(sessionId);

  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  // Use Claude to analyze session and generate scope
  const prompt = `
Based on the following conversation, generate a detailed scope of work:

${session.messages.map(m => `${m.role}: ${m.content}`).join('\n\n')}

Use this template structure:
${template}
  `.trim();

  session.process.stdin.write(prompt + '\n');

  // Collect scope document
  let scope = '';
  session.process.stdout.on('data', (data) => {
    scope += data.toString();
  });

  setTimeout(() => {
    res.json({ scope });
  }, 5000);
});

app.listen(3000, () => {
  console.log('Claude Code Orchestrator running on port 3000');
});
EOF

# Create systemd service
sudo cat > /etc/systemd/system/claude-orchestrator.service << 'EOF'
[Unit]
Description=Claude Code Orchestrator Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/claude-orchestrator
ExecStart=/usr/bin/node server.js
Restart=always
Environment=ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable claude-orchestrator
sudo systemctl start claude-orchestrator
```

### 4. Lambda Handlers

#### Q&A Handler
```python
# lambda_handlers/qa_handler.py
import json
import boto3
import requests

def lambda_handler(event, context):
    """
    Handle simple Q&A requests without starting a full session
    """
    body = json.loads(event['body'])
    question = body['question']
    customer_id = event['requestContext']['authorizer']['customerId']

    # Call Claude Code orchestrator
    response = requests.post('http://44.208.161.19:3000/api/session/start', json={
        'customerId': customer_id,
        'context': 'qa'
    })
    session_id = response.json()['sessionId']

    # Send question
    response = requests.post('http://44.208.161.19:3000/api/session/message', json={
        'sessionId': session_id,
        'message': question
    })
    answer = response.json()['response']

    # Store in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CustomerQA')
    table.put_item(Item={
        'customerId': customer_id,
        'timestamp': str(datetime.now()),
        'question': question,
        'answer': answer,
        'sessionId': session_id
    })

    return {
        'statusCode': 200,
        'body': json.dumps({
            'answer': answer,
            'sessionId': session_id
        })
    }
```

#### Planning Session Handler
```python
# lambda_handlers/planning_handler.py
import json
import boto3
import requests

def lambda_handler(event, context):
    """
    Manage multi-turn planning sessions
    """
    body = json.loads(event['body'])
    action = body['action']  # 'start', 'message', 'status'
    customer_id = event['requestContext']['authorizer']['customerId']

    if action == 'start':
        # Start new planning session
        response = requests.post('http://44.208.161.19:3000/api/session/start', json={
            'customerId': customer_id,
            'context': 'planning'
        })
        session_id = response.json()['sessionId']

        # Initialize in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('PlanningSessions')
        table.put_item(Item={
            'sessionId': session_id,
            'customerId': customer_id,
            'status': 'active',
            'startTime': str(datetime.now()),
            'messages': []
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'sessionId': session_id})
        }

    elif action == 'message':
        # Send message to existing session
        session_id = body['sessionId']
        message = body['message']

        response = requests.post('http://44.208.161.19:3000/api/session/message', json={
            'sessionId': session_id,
            'message': message
        })

        # Update DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('PlanningSessions')
        table.update_item(
            Key={'sessionId': session_id},
            UpdateExpression='SET messages = list_append(messages, :m)',
            ExpressionAttributeValues={
                ':m': [{
                    'timestamp': str(datetime.now()),
                    'role': 'user',
                    'content': message
                }, {
                    'timestamp': str(datetime.now()),
                    'role': 'assistant',
                    'content': response.json()['response']
                }]
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps(response.json())
        }
```

#### Scope Generation Handler
```python
# lambda_handlers/scope_handler.py
import json
import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    """
    Generate scope of work from planning session
    """
    body = json.loads(event['body'])
    session_id = body['sessionId']
    customer_id = event['requestContext']['authorizer']['customerId']

    # Load scope template from S3
    s3 = boto3.client('s3')
    template_obj = s3.get_object(Bucket='customer-scopes', Key='templates/default.md')
    template = template_obj['Body'].read().decode('utf-8')

    # Generate scope via Claude Code
    response = requests.post('http://44.208.161.19:3000/api/scope/generate', json={
        'sessionId': session_id,
        'template': template
    })
    scope_content = response.json()['scope']

    # Create scope ID
    scope_id = f"{customer_id}-{int(datetime.now().timestamp())}"

    # Save to S3
    s3.put_object(
        Bucket='customer-scopes',
        Key=f"scopes/{scope_id}.md",
        Body=scope_content.encode('utf-8'),
        ContentType='text/markdown'
    )

    # Save metadata to DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ScopeDocuments')
    table.put_item(Item={
        'scopeId': scope_id,
        'customerId': customer_id,
        'sessionId': session_id,
        'status': 'pending_approval',
        'createdAt': str(datetime.now()),
        's3Key': f"scopes/{scope_id}.md",
        'version': 1
    })

    # Send email notification
    ses = boto3.client('ses')
    ses.send_email(
        Source='noreply@yourcompany.com',
        Destination={'ToAddresses': [get_customer_email(customer_id)]},
        Message={
            'Subject': {'Data': 'Your Scope of Work is Ready for Review'},
            'Body': {
                'Text': {
                    'Data': f'Please review your scope document: https://portal.yourcompany.com/scope/{scope_id}'
                }
            }
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'scopeId': scope_id,
            'status': 'pending_approval'
        })
    }
```

### 5. Data Models

#### DynamoDB Tables

**PlanningSessions**:
```
{
  "sessionId": "customer123-1699123456",
  "customerId": "customer123",
  "status": "active|completed|abandoned",
  "startTime": "2025-11-08T12:00:00Z",
  "endTime": "2025-11-08T13:30:00Z",
  "messages": [
    {
      "timestamp": "2025-11-08T12:01:00Z",
      "role": "user|assistant",
      "content": "..."
    }
  ],
  "metadata": {
    "projectType": "web_app",
    "estimatedBudget": 50000
  }
}
```

**ScopeDocuments**:
```
{
  "scopeId": "customer123-1699123456",
  "customerId": "customer123",
  "sessionId": "customer123-1699123456",
  "status": "pending_approval|approved|revision_requested|rejected",
  "version": 1,
  "createdAt": "2025-11-08T13:30:00Z",
  "approvedAt": null,
  "s3Key": "scopes/customer123-1699123456.md",
  "revisionHistory": [
    {
      "version": 1,
      "timestamp": "2025-11-08T13:30:00Z",
      "changes": "Initial version"
    }
  ],
  "approvalData": {
    "approvedBy": null,
    "approvalDate": null,
    "signature": null,
    "comments": null
  }
}
```

**CustomerQA**:
```
{
  "qaId": "customer123-qa-1699123456",
  "customerId": "customer123",
  "timestamp": "2025-11-08T11:00:00Z",
  "question": "What is your pricing model?",
  "answer": "...",
  "sessionId": "customer123-1699123456",
  "helpful": true|false|null
}
```

### 6. Workflow States

#### Planning Session Flow
```
1. START
   ↓
2. Customer asks initial questions
   ↓
3. Claude asks clarifying questions
   ↓
4. Interactive back-and-forth
   ↓
5. Claude summarizes understanding
   ↓
6. Customer confirms/corrects
   ↓
7. READY FOR SCOPE GENERATION
```

#### Scope Approval Flow
```
1. SCOPE GENERATED (status: pending_approval)
   ↓
2. Customer notified via email
   ↓
3. Customer reviews scope
   ↓
   ├─→ APPROVE → status: approved → Contract generation
   ├─→ REVISE → status: revision_requested → Back to planning
   └─→ REJECT → status: rejected → Session closed
```

---

## Scope of Work Template

```markdown
# Scope of Work
**Client**: {{customer_name}}
**Date**: {{date}}
**Project**: {{project_title}}
**Version**: {{version}}

## 1. Project Overview
{{project_summary}}

## 2. Objectives
{{objectives_list}}

## 3. Deliverables
{{deliverables_list}}

## 4. Timeline
| Phase | Duration | Deliverables |
|-------|----------|-------------|
{{timeline_table}}

## 5. Technical Requirements
{{technical_requirements}}

## 6. Assumptions & Constraints
{{assumptions}}

## 7. Budget Estimate
| Item | Cost |
|------|------|
{{budget_table}}
**Total**: {{total_cost}}

## 8. Success Criteria
{{success_criteria}}

## 9. Next Steps
{{next_steps}}

## 10. Terms & Conditions
{{terms}}

---

**Approval**

Client Signature: ________________
Date: ________________

Consultant Signature: ________________
Date: ________________
```

---

## Implementation Phases

### Phase 1: MVP (2-3 weeks)
- [ ] Set up Claude Code orchestrator service on Lightsail
- [ ] Create basic HTTP API for session management
- [ ] Build simple Lambda handlers for Q&A and planning
- [ ] Set up DynamoDB tables
- [ ] Create basic React chat interface
- [ ] Deploy to staging environment

### Phase 2: Scope Generation (1-2 weeks)
- [ ] Implement scope template system
- [ ] Build scope generation Lambda
- [ ] Create S3 bucket structure
- [ ] Add PDF export functionality
- [ ] Build scope review UI

### Phase 3: Approval Workflow (1-2 weeks)
- [ ] Implement approval state machine
- [ ] Add email notifications (SES)
- [ ] Build revision request system
- [ ] Add signature capture
- [ ] Implement version control

### Phase 4: Polish & Production (1 week)
- [ ] Add monitoring & logging (CloudWatch)
- [ ] Implement rate limiting
- [ ] Add session timeout handling
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation

---

## Security Considerations

1. **API Authentication**: Use AWS Cognito or JWT tokens
2. **Rate Limiting**: Prevent abuse via API Gateway throttling
3. **Data Encryption**:
   - At rest: S3 server-side encryption
   - In transit: HTTPS/TLS
4. **API Key Protection**: Move to AWS Secrets Manager
5. **Network Security**:
   - Close unnecessary ports on Lightsail
   - Use security groups
   - Consider VPN for Lightsail access
6. **Audit Logging**: CloudTrail for all AWS API calls

---

## Monitoring & Alerts

**CloudWatch Metrics**:
- API Gateway request count
- Lambda execution time
- Error rates
- Claude Code orchestrator health
- Session duration
- Scope generation time

**Alerts**:
- High error rate (>5%)
- Long response time (>10s)
- Orchestrator service down
- DynamoDB throttling
- S3 storage approaching limits

---

## Cost Estimate

| Service | Usage | Monthly Cost |
|---------|-------|-------------|
| Lightsail | 1 instance | $3.50 |
| API Gateway | 100K requests | $0.35 |
| Lambda | 100K invocations | $0.20 |
| DynamoDB | 10GB, 100K r/w | $2.50 |
| S3 | 50GB storage | $1.15 |
| SES | 1000 emails | $0.10 |
| CloudWatch | Basic monitoring | $3.00 |
| **Total** | | **~$10.80/month** |

*Note: Anthropic API costs billed separately based on usage*

---

## Next Steps

1. **Review this document** with your team
2. **Choose implementation approach**:
   - Full build (all phases)
   - MVP first, iterate
   - Hybrid (some manual steps)
3. **Set up AWS infrastructure**:
   - Create DynamoDB tables
   - Set up S3 buckets
   - Deploy Lambda functions
4. **Install orchestrator service** on Lightsail
5. **Build frontend** (React app)
6. **Test end-to-end** with sample customer
7. **Deploy to production**

**Estimated Timeline**: 5-8 weeks for full implementation
**Estimated Cost**: $10-15/month infrastructure + API costs

---

**Questions or need help with implementation?**
Contact: [Your contact info]
