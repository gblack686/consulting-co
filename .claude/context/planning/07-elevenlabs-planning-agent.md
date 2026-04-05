# Plan 7: ElevenLabs Vibe-Coding Planning Agent

## Overview
A voice-powered AI planning assistant using ElevenLabs Conversational AI that guides developers through requirements gathering, leverages project-type-specific knowledge bases, and produces comprehensive project plans with dynamic completeness thresholds based on scope (POC/MVP/Production).

---

## Phase 1: Core Voice Interface

### 1.1 ElevenLabs Integration
- [ ] Set up ElevenLabs account
- [ ] Enable Conversational AI API access
- [ ] Select/customize voice:
  - Professional but approachable
  - Clear enunciation for technical terms
  - Consider multiple voice options
- [ ] Configure conversation settings:
  - Response latency targets
  - Interruption handling
  - Silence detection

### 1.2 Floating Button Component
- [ ] Design button UI:
  - Minimized state (floating icon)
  - Expanded state (active conversation)
  - Recording indicator
  - Transcript view toggle
- [ ] Build React/Vue component
- [ ] Add keyboard shortcuts
- [ ] Mobile-responsive design
- [ ] Positioning options (corner selection)

### 1.3 Voice Pipeline
- [ ] **Speech-to-Text**
  - ElevenLabs built-in STT
  - Or Whisper fallback
  - Real-time transcription display
- [ ] **AI Processing**
  - Send transcript to Claude/GPT
  - Context-aware responses
  - Conversation history management
- [ ] **Text-to-Speech**
  - ElevenLabs voice synthesis
  - Streaming audio playback
  - Queue management

---

## Phase 2: Conversation Flow Design

### 2.1 Initial Greeting & Discovery
- [ ] **Opening Prompt**
  ```
  "Hey! I'm your planning assistant. What are you building today?
  Give me a quick overview and I'll help you think through the details."
  ```
- [ ] **Follow-Up Questions**
  - "Who is this for?"
  - "What problem does it solve?"
  - "Any existing solutions you're improving on?"
  - "What's your timeline looking like?"

### 2.2 Scope Selection
- [ ] **Scope Selector Interface**
  - POC (Proof of Concept)
  - MVP (Minimum Viable Product)
  - Production
- [ ] **Voice Command Support**
  - "Let's keep this as a POC"
  - "I need a full MVP"
  - "This is going to production"
- [ ] **Scope Impact Explanation**
  ```
  "Got it - for an MVP, we'll need to cover core functionality,
  basic error handling, and essential user flows. Production
  would add security, scalability, and monitoring. Want me to
  walk through what's needed?"
  ```

### 2.3 Requirements Gathering Flow
- [ ] **Functional Requirements**
  - Core features
  - User stories
  - Use cases
- [ ] **Technical Requirements**
  - Platform/framework preferences
  - Integration needs
  - Performance requirements
- [ ] **Non-Functional Requirements**
  - Security considerations
  - Scalability expectations
  - Compliance needs

---

## Phase 3: Project-Type Knowledge Bases

### 3.1 Knowledge Base Architecture
- [ ] Design KB schema:
  ```yaml
  knowledge_base:
    project_type: string
    description: text
    common_requirements: list
    tech_stack_options: list
    architecture_patterns: list
    pitfalls_to_avoid: list
    reference_projects: list
    expert_sources: list
  ```
- [ ] Storage: SQLite + Vector embeddings
- [ ] RAG retrieval system

### 3.2 Core Knowledge Bases
- [ ] **Mobile App KB**
  - React Native vs Flutter vs Native
  - App store requirements
  - Push notifications
  - Offline support
  - Authentication patterns

- [ ] **Web Application KB**
  - Framework selection (Next.js, Remix, etc.)
  - State management options
  - API design patterns
  - Deployment strategies
  - SEO considerations

- [ ] **AI/ML Application KB**
  - Model selection guidance
  - Training vs inference
  - API integration patterns
  - Cost optimization
  - Prompt engineering

- [ ] **Backend/API KB**
  - REST vs GraphQL
  - Database selection
  - Authentication/authorization
  - Scaling patterns
  - Monitoring/logging

- [ ] **Trading Bot KB** (custom)
  - Exchange APIs
  - Risk management
  - Backtesting requirements
  - Real-time data handling
  - Regulatory considerations

### 3.3 Sean Kochel Frontend Design KB
- [ ] **Content Scraping**
  - Download YouTube videos/transcripts
  - Extract design principles
  - Categorize by topic:
    - Component architecture
    - State management
    - Performance optimization
    - UX patterns
    - Accessibility
- [ ] **Embedding & Indexing**
  - Create vector embeddings
  - Build semantic search
  - Tag with timestamps for source reference
- [ ] **Integration**
  - Surface relevant clips during planning
  - Quote specific advice
  - Link to source videos

---

## Phase 4: Intelligent Suggestion System

### 4.1 Suggestion Generation
- [ ] **Context-Aware Suggestions**
  - Based on project type
  - Based on stated requirements
  - Based on similar projects
- [ ] **Suggestion Categories**
  - "Must have" for scope
  - "Recommended"
  - "Nice to have"
  - "Future consideration"

### 4.2 User Interaction
- [ ] **Voice Approval**
  - "Yes, add that"
  - "No, skip it"
  - "Tell me more about that"
  - "Add it but lower priority"
- [ ] **Batch Suggestions**
  - Present 3-5 at a time
  - Allow bulk approve/reject
  - Explain reasoning

### 4.3 Learning Loop
- [ ] Track accepted vs rejected suggestions
- [ ] Improve suggestion relevance over time
- [ ] User preference profiles

---

## Phase 5: Progress Tracking & Completeness

### 5.1 Progress Bar Implementation
- [ ] **Visual Design**
  - Horizontal progress bar
  - Percentage display
  - Section breakdown
  - Color coding (red/yellow/green)

### 5.2 Completeness Calculation
- [ ] **Section Weights**
  - Overview/Vision: 10%
  - User Stories: 15%
  - Functional Requirements: 25%
  - Technical Requirements: 20%
  - Architecture: 15%
  - Timeline/Milestones: 10%
  - Risks/Mitigations: 5%

### 5.3 Dynamic Thresholds
- [ ] **POC Threshold: 50%**
  - Basic vision
  - Core user story
  - Key technical decisions
  - "Good enough to prototype"

- [ ] **MVP Threshold: 75%**
  - Complete user stories
  - Full functional requirements
  - Technical architecture
  - Basic risk assessment
  - "Ready to build core product"

- [ ] **Production Threshold: 100%**
  - All sections complete
  - Security review
  - Scalability plan
  - Monitoring strategy
  - Deployment plan
  - "Ready for production deployment"

### 5.4 Threshold Feedback
- [ ] **Below Threshold**
  ```
  "You're at 45% - need 50% for POC. Missing: technical
  architecture decisions and at least one user story.
  Want me to help fill those gaps?"
  ```
- [ ] **At Threshold**
  ```
  "Nice! You've hit 75% - that's MVP-ready! Want to keep
  going toward production-grade, or export what we have?"
  ```

---

## Phase 6: Plan Export & Integration

### 6.1 Export Formats
- [ ] **Markdown Document**
  - Structured headers
  - Checkbox task lists
  - Code blocks for tech specs
  - Mermaid diagrams

- [ ] **JSON/YAML**
  - Machine-readable format
  - Import into project management tools
  - Use as Claude Code agent input

- [ ] **Notion/Linear Integration**
  - Direct export to workspace
  - Create epics and stories
  - Maintain linking

### 6.2 Claude Code Integration
- [ ] Generate `.claude/` project context
- [ ] Create agent task files
- [ ] Export as implementable plan
- [ ] "Hand off to Claude Code" button

### 6.3 Version History
- [ ] Save plan versions
- [ ] Compare iterations
- [ ] Restore previous versions
- [ ] Collaboration support

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│      Floating Button │ Progress Bar │ Transcript View       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Voice Pipeline                              │
│        Microphone → ElevenLabs STT → Transcript             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Conversation Engine                          │
│   Context Manager │ Claude/GPT │ Knowledge Base RAG         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Plan Builder                               │
│    Requirement Tracker │ Completeness Calculator │ Export   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Response Synthesis                          │
│        Suggestion Generator │ ElevenLabs TTS → Audio        │
└─────────────────────────────────────────────────────────────┘
```

---

## Conversation Example

```
Agent: "Hey! What are you building today?"

User: "I want to build a mobile app for tracking workouts"

Agent: "Cool! A workout tracking app. Is this for personal use,
       or are you thinking about releasing it? And do you have
       a platform preference - iOS, Android, or both?"

User: "I want to release it on both platforms"

Agent: "Got it - cross-platform release. For that, I'd suggest
       React Native or Flutter. React Native has a larger ecosystem,
       Flutter has better performance. Any preference?"

User: "Let's go with React Native"

Agent: "Perfect. Now, what's the core feature? Just logging
       workouts, or do you want things like exercise libraries,
       progress charts, or social features?"

User: "Logging workouts and progress charts to start"

Agent: "Sounds like a solid MVP scope. I'm adding those as core
       requirements. You're at 35% completeness now. Should I
       suggest some common features for workout apps that you
       might want to consider?"

User: "Yes please"

Agent: "Here are three suggestions: First, rest timers between
       sets - really common ask. Second, exercise history so users
       can see their previous weights. Third, offline support since
       gyms often have bad signal. Want any of these?"

User: "Add the first two, skip offline for now"

Agent: "Added. You're now at 52% - that's POC-ready! Want to
       keep building toward MVP, or export what we have?"
```

---

## Dependencies
- ElevenLabs Conversational AI API
- Claude/GPT API for reasoning
- Vector database (ChromaDB/Pinecone)
- React/Vue for UI components
- YouTube transcript extraction
- SQLite for local storage

---

## Deliverables
- [ ] Floating button voice interface
- [ ] ElevenLabs integration
- [ ] Project-type knowledge bases
- [ ] Sean Kochel design KB
- [ ] Suggestion engine
- [ ] Progress bar with dynamic thresholds
- [ ] Plan export system
- [ ] Claude Code integration

---

## Success Metrics
- Time to generate MVP-ready plan
- User approval rate on suggestions
- Plan completeness accuracy
- Voice recognition accuracy
- User satisfaction scores
