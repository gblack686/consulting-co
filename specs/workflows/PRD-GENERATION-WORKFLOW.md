# Product Requirement Document (PRD) Generation Workflow
## Zero-Friction Claude Code Integration for Customer Planning

---

## User Journey Walkthrough

### Step 1: Customer Lands on Your Site
```
[Amplify Landing Page]
  ↓
[Customer clicks: "Get Your Custom Product Spec"]
  ↓
[Modal opens with Claude Code PRD Generator]
```

### Step 2: Initial Brief (Auto-Start)
```
Claude (auto-message):
"Hi! I'm Claude, and I'll help you create a comprehensive product
requirement document for your application. Let's start with the basics:

What's your app idea in a few sentences? What problem does it solve?"

[Customer types their vision]
```

### Step 3: Interactive Planning Phase
```
Customer: "I want to build a fitness tracking app that uses AI to
create personalized workout plans based on user goals and progress."

Claude (in planning mode):
"Great idea! Let me create a structured PRD for your AI fitness app.
I'll need to understand several key areas:

1. User Types & Personas
2. Core Features & Workflows
3. Data Models & Entities
4. API Endpoints & Integrations
5. User Experience Flow
6. Success Metrics

Let's dive into User Types first. Who will use this app?
- Beginners starting their fitness journey?
- Advanced athletes?
- Personal trainers?
- All of the above?"

[Live PRD Preview appears on right side showing sections]
```

### Step 4: Iterative Refinement
```
[Each user response updates the PRD in real-time]

Customer: "Mainly beginners, but also intermediate users.
No trainers for now."

[PRD updates automatically:]
━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT REQUIREMENT DOCUMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ 1. User Personas
   • Beginner (Primary)
     - New to fitness
     - Needs guidance
     - Low confidence

   • Intermediate (Secondary)
     - Some experience
     - Wants structure
     - Seeks improvement

⏳ 2. Core Features (In Progress)
   ...

Claude: "Perfect! Now let's detail the core features.
What should users be able to do on day 1?"

Customer: "Log workouts, see AI-generated plans, track progress"

[PRD section expands with detailed features]

✓ 2. Core Features
   • Workout Logging
     - Quick entry form
     - Exercise library
     - Rep/set tracking
     - Time tracking

   • AI Plan Generation
     - Goal-based algorithm
     - Progressive overload
     - Rest day scheduling
     - Adaptation based on progress

   • Progress Tracking
     - Visual charts
     - Milestone badges
     - Before/after photos
     - Performance metrics

Claude: "Excellent! Let's define the data model. What information
do we need to store for each user?"
```

### Step 5: Technical Deep Dive
```
[Claude transitions to technical specifications]

Claude: "Now that we have the features defined, let's map out
the technical requirements. I'll detail:

• Database Schema
• API Endpoints
• Authentication Flow
• Third-party Integrations

Let's start with the database..."

[PRD adds technical sections automatically]

━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. DATA MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Users Table:
  - id (UUID, PK)
  - email (String, unique)
  - name (String)
  - fitness_level (Enum: beginner, intermediate)
  - goals (JSON)
  - created_at (Timestamp)

Workouts Table:
  - id (UUID, PK)
  - user_id (UUID, FK)
  - date (Date)
  - exercises (JSON Array)
  - duration_minutes (Integer)
  - calories_burned (Integer)

Plans Table:
  - id (UUID, PK)
  - user_id (UUID, FK)
  - generated_at (Timestamp)
  - weeks (Integer)
  - schedule (JSON)
  - ai_parameters (JSON)
```

### Step 6: UI/UX Specification
```
Customer: "The workout logging should be super fast"

Claude: "Great requirement! I'll design a streamlined UX flow:

━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. USER FLOWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workout Logging Flow (< 30 seconds):
  1. User opens app
  2. Big "Log Workout" button visible
  3. Template selector (or "Quick Log")
  4. Pre-filled with last workout
  5. Swipe to adjust reps
  6. Tap "Done"
  7. Immediate confetti animation
  8. "Streak: 5 days!" message

Speed optimization:
  • Offline-first architecture
  • Instant feedback
  • Background sync
  • Haptic feedback

Should we add voice input for hands-free logging during workouts?"

Customer: "Yes! That would be amazing"

[PRD updates with voice feature]
```

### Step 7: API Endpoint Mapping
```
Claude: "Let me document all the API endpoints you'll need:

━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. API SPECIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Authentication:
  POST   /api/auth/register
  POST   /api/auth/login
  POST   /api/auth/refresh
  POST   /api/auth/logout

Users:
  GET    /api/users/me
  PUT    /api/users/me
  GET    /api/users/me/stats

Workouts:
  GET    /api/workouts
  POST   /api/workouts
  GET    /api/workouts/:id
  PUT    /api/workouts/:id
  DELETE /api/workouts/:id

AI Plans:
  POST   /api/plans/generate
  GET    /api/plans/:id
  PUT    /api/plans/:id/feedback

Progress:
  GET    /api/progress/charts
  GET    /api/progress/milestones
  POST   /api/progress/photos

Each endpoint includes:
  • Request/Response schemas
  • Authentication requirements
  • Rate limits
  • Error codes
  • Example payloads
```

### Step 8: Success Metrics & Analytics
```
Claude: "Finally, let's define how we'll measure success:

━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. SUCCESS METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━

User Engagement:
  • DAU/MAU ratio > 0.3
  • Avg workouts/week: 3+
  • Plan completion rate: >60%
  • 7-day retention: >40%

Technical Performance:
  • API response time: <200ms (p95)
  • App launch time: <2s
  • Crash rate: <0.1%
  • Offline sync success: >99%

Business Metrics:
  • Free-to-paid conversion: >5%
  • Monthly churn: <8%
  • NPS score: >50

Are these the right metrics for your goals?"
```

### Step 9: Final Review & Export
```
[Claude presents complete PRD]

Claude: "Your PRD is complete! Here's what we've documented:

✓ User Personas (2 types)
✓ Core Features (12 features, 3 MVPs)
✓ Data Model (6 tables, relationships mapped)
✓ API Endpoints (23 endpoints, fully specified)
✓ User Flows (4 primary flows, optimized for speed)
✓ Success Metrics (12 KPIs defined)
✓ Technical Stack Recommendations
✓ Timeline Estimate (12-16 weeks)
✓ Budget Estimate ($45k-65k)

[Buttons appear:]
[📄 Download PDF] [📧 Email to Team] [✏️ Make Changes] [✅ Approve & Continue]

Would you like me to:
1. Add more features?
2. Create user stories from this PRD?
3. Generate a development timeline?
4. Estimate cloud infrastructure costs?"
```

---

## Enhanced UI Features

### Real-Time PRD Preview Panel

```
┌─────────────────────────────────────────────────────────────┐
│                    PRD Generator                            │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│   CHAT INTERFACE         │    LIVE PRD PREVIEW             │
│   (Left 45%)             │    (Right 55%)                  │
│                          │                                  │
│  🤖 Claude:              │  ┌─────────────────────────┐    │
│  "What's your app        │  │ TABLE OF CONTENTS       │    │
│   idea?"                 │  │ ─────────────────────── │    │
│                          │  │ ✓ 1. Overview           │    │
│  👤 You:                 │  │ ✓ 2. User Personas      │    │
│  "Fitness tracking       │  │ ⏳ 3. Features          │    │
│   with AI plans"         │  │ ⬜ 4. Data Model        │    │
│                          │  │ ⬜ 5. API Spec          │    │
│  🤖 Claude:              │  │ ⬜ 6. UX Flows          │    │
│  "Great! Let's define    │  │ ⬜ 7. Metrics           │    │
│   user personas..."      │  └─────────────────────────┘    │
│                          │                                  │
│  [Typing...]             │  ┌─────────────────────────┐    │
│                          │  │ 3. CORE FEATURES        │    │
│  💬 [Type message...]    │  │ ─────────────────────── │    │
│  [Send]                  │  │                         │    │
│                          │  │ • Workout Logging       │    │
│                          │  │   - Quick entry         │    │
│                          │  │   - Exercise library    │    │
│                          │  │   - Rep/set tracking   │    │
│                          │  │                         │    │
│                          │  │ • AI Plan Generation    │    │
│                          │  │   - Goal-based          │    │
│                          │  │   - Progressive load    │    │
│                          │  │                         │    │
│                          │  │ [Updates in real-time]  │    │
│                          │  └─────────────────────────┘    │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

### Quick Action Buttons

```
[During conversation, contextual buttons appear:]

When discussing features:
  [+ Add Feature] [✓ Mark as MVP] [🔄 Alternative Approach]

When discussing data model:
  [📊 Visualize Schema] [⚡ Suggest Indexes] [🔗 Add Relationship]

When discussing APIs:
  [📋 Copy OpenAPI Spec] [🧪 Generate Test Cases] [📚 Add Example]

When discussing timeline:
  [📅 Export to Calendar] [💰 Estimate Cost] [👥 Suggest Team Size]

At any time:
  [💾 Save Progress] [📤 Share Link] [🎨 Customize Template]
```

### Interactive Feature Checklist

```
┌──────────────────────────────────────┐
│  FEATURE PRIORITIZATION              │
├──────────────────────────────────────┤
│  Drag to reorder by priority:        │
│                                      │
│  ☐ MVP Features (Ship in v1)        │
│    1. ⬆️⬇️ User Registration         │
│    2. ⬆️⬇️ Workout Logging           │
│    3. ⬆️⬇️ AI Plan Generation        │
│    4. ⬆️⬇️ Progress Charts           │
│                                      │
│  ☐ Phase 2 Features                 │
│    5. ⬆️⬇️ Social Sharing            │
│    6. ⬆️⬇️ Voice Logging             │
│    7. ⬆️⬇️ Nutrition Tracking        │
│                                      │
│  ☐ Future Enhancements              │
│    8. ⬆️⬇️ Wearable Integration      │
│    9. ⬆️⬇️ Personal Trainer Matching │
│                                      │
│  [Update PRD with new order]        │
└──────────────────────────────────────┘
```

### Section Navigation

```
┌────────────────────────────────────┐
│  JUMP TO SECTION                   │
├────────────────────────────────────┤
│  Click to discuss or review:       │
│                                    │
│  ✓ Overview          [Review]     │
│  ✓ Personas          [Review]     │
│  ⏳ Features          [Continue]   │
│  ⬜ Data Model        [Start]      │
│  ⬜ API Spec          [Start]      │
│  ⬜ UX Flows          [Start]      │
│  ⬜ Tech Stack        [Start]      │
│  ⬜ Metrics           [Start]      │
│  ⬜ Timeline          [Start]      │
│  ⬜ Budget            [Start]      │
│                                    │
│  Progress: 3/10 sections (30%)    │
│  [⬛⬛⬛⬜⬜⬜⬜⬜⬜⬜]               │
└────────────────────────────────────┘
```

---

## Implementation

### React Component: PRDGenerator.jsx

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import ReactMarkdown from 'react-markdown';
import './PRDGenerator.css';

const PRDGenerator = ({ customerId, initialBrief }) => {
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [prdDocument, setPrdDocument] = useState({
    sections: [],
    completedSections: [],
    progress: 0
  });
  const [activeSection, setActiveSection] = useState(null);

  // PRD Template Sections - AWS FOCUSED
  const PRD_SECTIONS = [
    { id: 'overview', title: 'Product Overview', icon: '📋' },
    { id: 'personas', title: 'User Personas', icon: '👥' },
    { id: 'features', title: 'Core Features', icon: '⚡' },
    { id: 'datamodel', title: 'AWS Data Model', icon: '🗄️', aws: true },
    { id: 'architecture', title: 'AWS Architecture', icon: '☁️', aws: true },
    { id: 'api', title: 'API Design (Gateway/AppSync)', icon: '🔌', aws: true },
    { id: 'ux', title: 'UX Flows', icon: '🎨' },
    { id: 'techstack', title: 'AWS Tech Stack', icon: '🛠️', aws: true },
    { id: 'metrics', title: 'Success Metrics', icon: '📊' },
    { id: 'costs', title: 'AWS Cost Estimate', icon: '💰', aws: true },
    { id: 'timeline', title: 'Timeline', icon: '📅' }
  ];

  // Specialized prompt for PRD generation - AWS FOCUSED
  const PRD_SYSTEM_PROMPT = `You are an AWS-focused product requirement document (PRD) generation specialist.
Your goal is to help the customer create a comprehensive, detailed PRD for applications built EXCLUSIVELY on AWS services.

CRITICAL CONSTRAINT:
**ONLY recommend AWS services and AWS-native solutions. DO NOT suggest non-AWS alternatives.**

AWS SERVICE CATEGORIES TO USE:
- Compute: Lambda, ECS/Fargate, EC2, App Runner, Amplify
- Storage: S3, DynamoDB, RDS (Aurora), DocumentDB, ElastiCache
- API: API Gateway, AppSync (GraphQL)
- Auth: Cognito, IAM
- AI/ML: Bedrock, SageMaker, Rekognition, Comprehend, Textract, Transcribe
- Analytics: Athena, QuickSight, Kinesis, OpenSearch
- Integration: EventBridge, SNS, SQS, Step Functions
- Frontend: Amplify Hosting, CloudFront
- Monitoring: CloudWatch, X-Ray
- Security: WAF, Shield, KMS, Secrets Manager
- CI/CD: CodePipeline, CodeBuild, CodeDeploy

PROCESS:
1. Start by understanding their product vision
2. Systematically work through each section:
   - User Personas
   - Core Features (prioritized as MVP, Phase 2, Future)
   - AWS Data Model (DynamoDB tables, RDS schemas, S3 buckets)
   - AWS Architecture (specific services with explanations)
   - API Design (API Gateway + Lambda, or AppSync)
   - UX Flows (step-by-step user journeys)
   - AWS Tech Stack (MANDATORY - only AWS services)
   - Success Metrics (quantified KPIs)
   - AWS Cost Estimate (per service, monthly)
   - Timeline Estimate (broken into phases)

3. After each user response, output the updated section in markdown format
4. Use clear headings, bullet points, and tables
5. Be specific with AWS service names and features
6. Always explain WHY you chose each AWS service
7. Suggest AWS best practices (Well-Architected Framework)

TECH STACK RULES:
- Database: ONLY DynamoDB, Aurora, RDS, or DocumentDB
- Backend: ONLY Lambda, ECS/Fargate, or App Runner
- Frontend: ONLY Amplify, S3+CloudFront
- Auth: ONLY Cognito
- AI: ONLY AWS AI/ML services (Bedrock, SageMaker, etc.)
- APIs: ONLY API Gateway or AppSync
- Queue/Messaging: ONLY SQS, SNS, EventBridge
- Storage: ONLY S3
- CDN: ONLY CloudFront

When suggesting architecture, use format:
"For [feature], use [AWS Service] because [reason]"

Example:
"For user authentication, use AWS Cognito because it provides:
- Built-in user pools with MFA
- Social login integration
- JWT token management
- Seamless integration with API Gateway
- Pay-per-user pricing"

STYLE:
- Friendly but professional
- AWS-focused and cloud-native
- Proactive (suggest what's missing)
- Detail-oriented with AWS specifics
- Ask ONE focused question at a time
- Celebrate progress ("Great! Section complete ✓")
- Always mention AWS service names explicitly

OUTPUT FORMAT:
Use markdown with clear section headers:
## 1. Product Overview
## 2. User Personas
## 3. Core Features
## 4. AWS Data Model
## 5. AWS Architecture Diagram (textual)
## 6. API Design (API Gateway/AppSync)
## 7. UX Flows
## 8. AWS Tech Stack (MANDATORY)
## 9. Success Metrics
## 10. AWS Cost Estimate
## 11. Timeline Estimate

Current context: ${initialBrief}

Let's create an AWS-powered PRD!`;

  useEffect(() => {
    // Connect to orchestrator
    const ws = io('ws://44.208.161.19:3000');

    ws.on('connect', () => {
      console.log('Connected to PRD Generator');

      // Start session with specialized prompt
      ws.emit('message', {
        type: 'start_session',
        customerId,
        context: 'prd_generation',
        model: 'sonnet', // Use Sonnet for better planning
        permissionMode: 'plan',
        systemPrompt: PRD_SYSTEM_PROMPT,
        initialMessage: `I want to build: ${initialBrief}`
      });
    });

    ws.on('message', handleWebSocketMessage);
    setSocket(ws);

    return () => ws.close();
  }, [customerId, initialBrief]);

  const handleWebSocketMessage = (data) => {
    const message = JSON.parse(data);

    switch (message.type) {
      case 'session_started':
        setSessionId(message.sessionId);
        break;

      case 'claude_event':
        handleClaudeEvent(message.event);
        break;
    }
  };

  const handleClaudeEvent = (event) => {
    switch (event.type) {
      case 'stream_event':
        if (event.event.type === 'content_block_delta') {
          const text = event.event.delta.text;
          setCurrentResponse(prev => prev + text);

          // Parse PRD sections from streaming text
          updatePRDDocument(currentResponse + text);
        }
        break;

      case 'assistant':
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: event.message.content[0].text,
          timestamp: new Date()
        }]);
        setCurrentResponse('');
        setIsTyping(false);
        break;
    }
  };

  const updatePRDDocument = (text) => {
    // Parse markdown sections from Claude's response
    const sections = [];
    const regex = /^##\s+(\d+)\.\s+(.+)$/gm;
    let match;

    while ((match = regex.exec(text)) !== null) {
      const sectionNumber = parseInt(match[1]);
      const sectionTitle = match[2];

      // Extract section content until next section
      const startPos = match.index + match[0].length;
      const nextMatch = regex.exec(text);
      const endPos = nextMatch ? nextMatch.index : text.length;
      const content = text.substring(startPos, endPos).trim();

      sections.push({
        number: sectionNumber,
        title: sectionTitle,
        content,
        completed: content.length > 50 // Mark as complete if substantial content
      });
    }

    setPrdDocument({
      sections,
      completedSections: sections.filter(s => s.completed),
      progress: sections.length > 0 ? (sections.filter(s => s.completed).length / PRD_SECTIONS.length) * 100 : 0
    });
  };

  const sendMessage = () => {
    if (!inputValue.trim() || !socket || !sessionId) return;

    socket.emit('message', {
      type: 'user_message',
      sessionId,
      content: inputValue
    });

    setMessages(prev => [...prev, {
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }]);

    setInputValue('');
    setIsTyping(true);
  };

  const jumpToSection = (sectionId) => {
    const section = PRD_SECTIONS.find(s => s.id === sectionId);
    if (section) {
      const message = `Let's work on the ${section.title} section now.`;
      setInputValue(message);
      sendMessage();
    }
  };

  const exportPRD = (format) => {
    const fullPRD = prdDocument.sections.map(s =>
      `## ${s.number}. ${s.title}\n\n${s.content}`
    ).join('\n\n');

    if (format === 'markdown') {
      const blob = new Blob([fullPRD], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'product-requirements.md';
      a.click();
    } else if (format === 'pdf') {
      // Use a service or library to convert markdown to PDF
      // For now, open print dialog
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`
        <html>
          <head><title>Product Requirements Document</title></head>
          <body>${marked(fullPRD)}</body>
        </html>
      `);
      printWindow.print();
    }
  };

  return (
    <div className="prd-generator">
      {/* Header */}
      <div className="prd-header">
        <h1>📋 Product Requirement Document Generator</h1>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${prdDocument.progress}%` }}
          />
          <span className="progress-text">
            {Math.round(prdDocument.progress)}% Complete
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="prd-content">
        {/* Left: Chat Interface */}
        <div className="chat-panel">
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
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Describe your requirements..."
              disabled={!sessionId || isTyping}
            />
            <button onClick={sendMessage} disabled={!sessionId || isTyping}>
              Send
            </button>
          </div>
        </div>

        {/* Right: PRD Preview & Navigation */}
        <div className="prd-panel">
          {/* Section Navigator */}
          <div className="section-navigator">
            <h3>Table of Contents</h3>
            {PRD_SECTIONS.map((section, idx) => {
              const isCompleted = prdDocument.completedSections.some(
                s => s.title.toLowerCase().includes(section.title.toLowerCase())
              );
              const isCurrent = activeSection === section.id;

              return (
                <div
                  key={section.id}
                  className={`section-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
                  onClick={() => jumpToSection(section.id)}
                >
                  <span className="section-icon">
                    {isCompleted ? '✓' : section.icon}
                  </span>
                  <span className="section-title">
                    {idx + 1}. {section.title}
                  </span>
                  <button className="section-action">
                    {isCompleted ? 'Review' : 'Start'}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Live PRD Preview */}
          <div className="prd-preview">
            <div className="preview-header">
              <h3>📄 Live Preview</h3>
              <div className="export-buttons">
                <button onClick={() => exportPRD('markdown')}>
                  📥 Download MD
                </button>
                <button onClick={() => exportPRD('pdf')}>
                  📄 Export PDF
                </button>
              </div>
            </div>

            <div className="preview-content">
              {prdDocument.sections.map((section, idx) => (
                <div key={idx} className="prd-section">
                  <h2>
                    {section.number}. {section.title}
                    {section.completed && <span className="section-badge">✓</span>}
                  </h2>
                  <ReactMarkdown>{section.content}</ReactMarkdown>
                </div>
              ))}

              {prdDocument.sections.length === 0 && (
                <div className="preview-empty">
                  <p>Your PRD will appear here as Claude builds it...</p>
                  <p>Start by answering Claude's questions!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PRDGenerator;
```

### CSS: PRDGenerator.css

```css
.prd-generator {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}

.prd-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.prd-header h1 {
  margin: 0 0 1rem 0;
  font-size: 1.75rem;
}

.progress-bar {
  position: relative;
  height: 24px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ade80 0%, #22c55e 100%);
  transition: width 0.5s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-weight: 600;
  font-size: 0.875rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.prd-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-panel {
  flex: 0 0 45%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e7eb;
  background: white;
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
  max-width: 85%;
  animation: slideIn 0.3s ease-out;
}

.message-user {
  align-self: flex-end;
}

.message-assistant {
  align-self: flex-start;
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
  background: #f3f4f6;
  color: #111827;
  border-bottom-left-radius: 0.25rem;
}

.chat-input {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.chat-input input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #e5e7eb;
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

.prd-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.section-navigator {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  max-height: 300px;
  overflow-y: auto;
}

.section-navigator h3 {
  margin: 0 0 1rem 0;
  color: #111827;
  font-size: 1.125rem;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
}

.section-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.section-item.completed {
  background: #d1fae5;
  border-left: 3px solid #10b981;
}

.section-item.current {
  background: #dbeafe;
  border-left: 3px solid #3b82f6;
}

.section-icon {
  font-size: 1.25rem;
}

.section-item.completed .section-icon {
  color: #10b981;
  font-weight: bold;
}

.section-title {
  flex: 1;
  font-weight: 500;
  color: #374151;
}

.section-action {
  padding: 0.25rem 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.section-action:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.prd-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.preview-header h3 {
  margin: 0;
  color: #111827;
  font-size: 1.125rem;
}

.export-buttons {
  display: flex;
  gap: 0.5rem;
}

.export-buttons button {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.export-buttons button:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: #fafafa;
}

.prd-section {
  background: white;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.prd-section h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #111827;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.section-badge {
  padding: 0.25rem 0.5rem;
  background: #d1fae5;
  color: #10b981;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.preview-empty {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
}

.preview-empty p {
  font-size: 1.125rem;
  margin: 0.5rem 0;
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
```

---

## Key Features

✅ **Zero Friction** - Chat naturally, PRD builds automatically
✅ **Real-Time Preview** - See document update as you talk
✅ **Section Navigator** - Jump to any section instantly
✅ **Progress Tracking** - Visual progress bar
✅ **Export Options** - Download as MD or PDF
✅ **Contextual Actions** - Smart buttons appear based on conversation
✅ **Streaming UI** - Character-by-character text just like CLI
✅ **Planning Mode** - Claude uses planning mode for structured thinking
✅ **Specialized Prompt** - Custom system prompt for PRD generation
✅ **Interactive** - Drag sections, add features, suggest changes

This gives your customers a **magical** experience - they just talk to Claude, and a comprehensive PRD appears! 🎉
