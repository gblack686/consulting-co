# OpenClaw Consulting: Claude Code Pipeline Architecture

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSULTING SESSION (90 min)                   │
│              Client + Consultant + AI Assistant                  │
│                                                                 │
│  Questions from framework → Client answers → Transcript         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼ transcript.md
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    CLAUDE CODE PIPELINE                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              TAC CODING EXPERT (the meta-brain)            │  │
│  │                                                           │  │
│  │  Has: TAC expertise, expert-building patterns,            │  │
│  │       SKILL.md format, OpenClaw workspace spec            │  │
│  │                                                           │  │
│  │  Knows HOW to build experts. Used throughout.             │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │          STEP 1: TRANSCRIPT PARSER                         │  │
│  │                                                           │  │
│  │  Reads transcript → extracts:                              │  │
│  │  • Mission statement                                      │  │
│  │  • Client profile (USER.md data)                          │  │
│  │  • Soul/vibe preferences (SOUL.md data)                   │  │
│  │  • Identity choices (IDENTITY.md data)                    │  │
│  │  • Tool inventory (TOOLS.md data)                         │  │
│  │  • Autonomy boundaries (AGENTS.md data)                   │  │
│  │  • Domains (3-5 discovered)                               │  │
│  │  • Workflows per domain (2-4 each)                        │  │
│  │  • Triggers, outputs, approval gates per workflow          │  │
│  │                                                           │  │
│  │  Output: session_output/ directory with structured JSON    │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │          STEP 2: WORKSPACE BUILDER                         │  │
│  │                                                           │  │
│  │  Writes the static workspace files:                        │  │
│  │  • SOUL.md, USER.md, IDENTITY.md, MEMORY.md               │  │
│  │  • AGENTS.md, TOOLS.md, HEARTBEAT.md                      │  │
│  │  • openclaw.json (model, channels, session config)         │  │
│  │                                                           │  │
│  │  These don't need plan-build-improve —                     │  │
│  │  they're direct transforms from session data.              │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │          STEP 3: DOMAIN EXPERT FACTORY                     │  │
│  │          (one cycle per domain discovered)                  │  │
│  │                                                           │  │
│  │  For each domain (e.g., "content", "business", "personal"):│  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  PLAN  →  BUILD  →  IMPROVE  →  VALIDATE            │  │  │
│  │  │                                                     │  │  │
│  │  │  PLAN: TAC Coding Expert analyzes domain            │  │  │
│  │  │    • What workflows belong to this domain?          │  │  │
│  │  │    • What tools/APIs does it need?                  │  │  │
│  │  │    • What expertise does this expert need?          │  │  │
│  │  │    • What domain-specific commands are needed?      │  │  │
│  │  │    • Research APIs (browser agent dispatched)       │  │  │
│  │  │    • Find tutorials (youtube agent dispatched)      │  │  │
│  │  │                                                     │  │  │
│  │  │  BUILD: Generate full expert directory               │  │  │
│  │  │    • _index.md                                      │  │  │
│  │  │    • expertise.md                                   │  │  │
│  │  │    • question.md                                    │  │  │
│  │  │    • plan.md                                        │  │  │
│  │  │    • plan_build_improve.md                          │  │  │
│  │  │    • self-improve.md                                │  │  │
│  │  │    • {domain-specific}.md commands                  │  │  │
│  │  │    • skills/{workflow}/SKILL.md (OpenClaw format)   │  │  │
│  │  │    • cron job definitions                           │  │  │
│  │  │                                                     │  │  │
│  │  │  IMPROVE: Self-improve expertise after build        │  │  │
│  │  │    • Capture API research findings                  │  │  │
│  │  │    • Record YouTube tutorial patterns               │  │  │
│  │  │    • Update expertise.md with learnings             │  │  │
│  │  │                                                     │  │  │
│  │  │  VALIDATE: Quality check                            │  │  │
│  │  │    • All 8 expert files present?                    │  │  │
│  │  │    • SKILL.md frontmatter valid?                    │  │  │
│  │  │    • Cron expressions valid?                        │  │  │
│  │  │    • Cross-references consistent?                   │  │  │
│  │  │    • Score >= 80%? If not, loop back to BUILD       │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  Repeats for EACH domain. Runs in parallel where possible. │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │          STEP 4: ASSEMBLY & DEPLOYMENT                     │  │
│  │                                                           │  │
│  │  Merges all domain experts + workspace files into:         │  │
│  │                                                           │  │
│  │  client-workspace/                                        │  │
│  │  ├── workspace/         (OpenClaw workspace files)        │  │
│  │  │   ├── SOUL.md                                          │  │
│  │  │   ├── USER.md                                          │  │
│  │  │   ├── IDENTITY.md                                      │  │
│  │  │   ├── MEMORY.md                                        │  │
│  │  │   ├── AGENTS.md                                        │  │
│  │  │   ├── TOOLS.md                                         │  │
│  │  │   ├── HEARTBEAT.md                                     │  │
│  │  │   └── skills/                                          │  │
│  │  │       ├── content/                                     │  │
│  │  │       │   ├── write-newsletter/SKILL.md                │  │
│  │  │       │   └── schedule-posts/SKILL.md                  │  │
│  │  │       ├── business/                                    │  │
│  │  │       │   └── update-pipeline/SKILL.md                 │  │
│  │  │       └── morning-brief/SKILL.md                       │  │
│  │  │                                                        │  │
│  │  ├── experts/           (Claude Code expert systems)      │  │
│  │  │   ├── content/                                         │  │
│  │  │   │   ├── _index.md                                    │  │
│  │  │   │   ├── expertise.md                                 │  │
│  │  │   │   ├── question.md                                  │  │
│  │  │   │   ├── plan.md                                      │  │
│  │  │   │   ├── plan_build_improve.md                        │  │
│  │  │   │   ├── self-improve.md                              │  │
│  │  │   │   └── schedule-content.md  (domain-specific cmd)   │  │
│  │  │   ├── business/                                        │  │
│  │  │   │   ├── _index.md                                    │  │
│  │  │   │   ├── expertise.md                                 │  │
│  │  │   │   ├── question.md                                  │  │
│  │  │   │   ├── plan.md                                      │  │
│  │  │   │   ├── plan_build_improve.md                        │  │
│  │  │   │   ├── self-improve.md                              │  │
│  │  │   │   └── sync-pipeline.md     (domain-specific cmd)   │  │
│  │  │   └── personal/                                        │  │
│  │  │       └── ...                                          │  │
│  │  │                                                        │  │
│  │  ├── openclaw.json      (gateway config)                  │  │
│  │  └── cron-setup.sh      (cron job install commands)       │  │
│  │                                                           │  │
│  │  + Deploy via SSH to client's OpenClaw instance            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Standard Components (What WE Provide)

These are pre-built and included in every client engagement. They're the factory, not the product.

### 1. TAC Coding Expert (The Meta-Brain)

**What it is**: An expert system with full TAC methodology baked in. It knows how to build other experts. It's the consulting firm's secret sauce — the intelligence that turns a transcript into a working agent ecosystem.

**Used during**: Every step of the pipeline. It's the brain that:
- Classifies domains from transcript text
- Selects appropriate TAC patterns for each workflow
- Writes expert files using the correct structure
- Applies the 12 leverage points to each skill
- Ensures plan-build-improve cycles follow TAC-7 ZTE

```
.claude/commands/experts/tac-coding/
├── _index.md
│   Domain: TAC-informed code generation and expert system construction
│   Specialty: Building domain experts, writing SKILL.md files,
│              OpenClaw workspace configuration
│
├── expertise.md
│   Part 1: Expert System Architecture
│     - The 8-file expert pattern (_index, expertise, question,
│       plan, plan_build_improve, self-improve, + domain commands)
│     - File relationships and cross-references
│     - Frontmatter schema for each file type
│
│   Part 2: OpenClaw Workspace Specification
│     - SOUL.md format (Core Truths, Boundaries, Vibe, Continuity)
│     - USER.md format (Name, Timezone, Projects, Context)
│     - IDENTITY.md format (Name, Creature, Vibe, Emoji, Avatar)
│     - MEMORY.md format (Mission, Goals, Long-term facts)
│     - AGENTS.md format (Session behavior, memory protocol, boundaries)
│     - TOOLS.md format (Infrastructure, devices, credentials)
│     - HEARTBEAT.md format (Periodic task list)
│
│   Part 3: SKILL.md Specification
│     - Required frontmatter (name, description)
│     - Optional keys (user-invocable, disable-model-invocation, etc.)
│     - metadata must be SINGLE-LINE JSON (parser requirement)
│     - metadata.openclaw.requires gating (bins, env, config, os)
│     - Skill loading precedence (workspace > ~/.openclaw > bundled)
│     - Token impact (~24 tokens per skill overhead)
│
│   Part 4: TAC Pattern Library (applied to skill construction)
│     - TAC-2: Adopt Agent's Perspective → expertise.md structure
│     - TAC-3: Template Engineering → SKILL.md as template
│     - TAC-5: Feedback Loops → self-improve.md pattern
│     - TAC-6: One Agent One Purpose → focused skill design
│     - TAC-7: ZTE Workflow → plan_build_improve.md structure
│     - TAC-9: Context Engineering → what goes in expertise.md
│     - TAC-10: Self-Improving Prompts → self-improve cycle
│
│   Part 5: Cron Job Specification
│     - Three schedule types: one-shot (at), interval (every), cron
│     - Execution modes: main session vs. isolated
│     - Delivery modes: announce, webhook, none
│     - CLI syntax for openclaw cron add
│     - Timezone handling (IANA format)
│
│   Part 6: Transcript Parsing Patterns
│     - Domain extraction heuristics
│     - Workflow identification markers
│     - Trigger/output/gate extraction
│     - Ambiguity resolution strategies
│
│   Part 7: Quality Scoring Rubric
│     - Per-expert structural checklist (8 files present?)
│     - Per-skill validation (frontmatter, steps, triggers)
│     - Cross-reference consistency
│     - Security review checklist
│     - Scoring thresholds (>= 80% to ship)
│
├── question.md
│   Categories:
│     1. Expert structure questions → Part 1
│     2. OpenClaw config questions → Part 2
│     3. SKILL.md format questions → Part 3
│     4. TAC pattern questions → Part 4
│     5. Cron/scheduling questions → Part 5
│     6. Transcript parsing questions → Part 6
│
├── plan.md
│   Given a domain spec from transcript parser:
│   1. Load expertise Parts 1-5
│   2. Classify domain workflows by TAC pattern
│   3. Determine which domain-specific commands are needed
│   4. Identify API research needs (dispatch browser agent)
│   5. Identify tutorial research needs (dispatch youtube agent)
│   6. Output: domain-plan.md with file list and content outlines
│
├── plan_build_improve.md
│   Full ACT-LEARN-REUSE cycle per domain:
│   PLAN → BUILD → IMPROVE → VALIDATE
│   Dispatches sub-agents for research during PLAN
│   Writes all 8+ expert files during BUILD
│   Updates own expertise after IMPROVE
│   Quality scores during VALIDATE (loop if < 80%)
│
├── self-improve.md
│   After each domain build:
│   - What patterns worked well
│   - What transcript signals were ambiguous
│   - New API integration patterns discovered
│   - Updated quality scoring heuristics
│
├── parse-transcript.md          ← domain-specific command
│   Reads transcript.md, extracts structured data
│   Output: session_output/ with all JSON files
│
├── build-workspace.md           ← domain-specific command
│   Transforms session_output into OpenClaw workspace files
│   Output: workspace/ directory
│
├── build-domain-expert.md       ← domain-specific command
│   Builds one complete expert directory for a domain
│   Input: domain spec from session_output
│   Output: experts/{domain}/ with all 8 files
│
└── validate-package.md          ← domain-specific command
    Validates the complete client package
    Structural + content + security checks
    Output: quality_report.md with scores
```

### 2. Browser Research Component

**What it is**: Not an expert — a utility dispatched by the TAC Coding Expert during the PLAN phase when it needs API documentation for a client's tools.

```
Dispatched via Task(subagent_type: "playwright-bowser-agent")

Prompt template:
  "Research the API for {tool_name}. Find:
   1. Official API docs URL
   2. Auth method (API key, OAuth, none)
   3. Key endpoints for {specific_actions}
   4. MCP server availability (search 'mcp-server-{tool}')
   5. OpenClaw plugin (search clawhub.com for {tool})
   Return structured JSON."

Used during: PLAN phase of domain expert factory
Output feeds into: expertise.md Part N (domain-specific tools section)
```

### 3. YouTube Research Component

**What it is**: Not an expert — a utility dispatched during PLAN to find working patterns from the OpenClaw creator ecosystem.

```
Dispatched via Task(subagent_type: "youtube-transcript-agent")

Prompt template:
  "Search YouTube for 'OpenClaw {tool_name} integration' or
   'OpenClaw {workflow_type} setup'. Extract:
   1. Configuration steps mentioned
   2. API keys or credentials needed
   3. Common pitfalls
   4. Working prompts or skill examples
   Save to .claude/context/tac-scan/"

Used during: PLAN phase of domain expert factory
Output feeds into: expertise.md (domain-specific patterns section)
```

---

## What Gets Built Per Domain (The Product)

Each domain discovered in the consulting transcript produces a full expert system. Here's what a **Content** domain expert looks like:

### Example: Content Domain Expert

```
experts/content/
│
├── _index.md
│   ---
│   type: expert
│   name: "content"
│   domain: [content-creation, youtube, newsletter, social-media]
│   specialty: "Content Production & Distribution"
│   status: active
│   created: {date}
│   updated: {date}
│   tags: [expert, domain-expertise, content, openclaw]
│   ---
│
│   # Content Expert
│
│   ## Domain Overview
│   Content production and distribution automation for {client_name}.
│   Covers YouTube content pipeline, newsletter writing, and social
│   media scheduling across {tools_list}.
│
│   ## Expert Type
│   **Domain Expert** - Deep expertise in content workflows
│   specific to {client_name}'s tools and preferences.
│
│   ## Key Capabilities
│   - Research trending topics in {client_interests}
│   - Draft YouTube scripts matching {client_style}
│   - Write and schedule newsletters via {tool}
│   - Schedule social posts across {platforms}
│   - Track content analytics via {analytics_tool}
│
│   ## Expert Files
│   | File | Purpose |
│   |------|---------|
│   | expertise | Complete content workflow mental model |
│   | question | Query content processes |
│   | plan | Plan new content workflows |
│   | plan_build_improve | Full ACT-LEARN-REUSE cycle |
│   | self-improve | Update expertise after runs |
│   | schedule-content | Automated content scheduling |
│   | research-topics | Trending topic discovery |
│
│   ## OpenClaw Skills (deployed)
│   | Skill | Trigger | Delivery |
│   |-------|---------|----------|
│   | write-newsletter | cron Wed 8pm | telegram announce |
│   | research-trends | cron daily 6am | heartbeat |
│   | schedule-posts | on-demand | telegram announce |
│
│   ## Tools & APIs
│   | Tool | API | Auth | Status |
│   |------|-----|------|--------|
│   | YouTube | YouTube Data API v3 | OAuth | configured |
│   | ConvertKit | REST API | API key | configured |
│   | Buffer | REST API | OAuth | needs setup |
│
├── expertise.md
│   ---
│   type: expert-file
│   parent: "[[content/_index]]"
│   file-type: expertise
│   human_reviewed: false
│   tags: [expert-file, mental-model, content]
│   last_updated: {date}
│   ---
│
│   # Content Expert - Complete Mental Model
│
│   ## Part 1: Content Architecture
│   {Client_name}'s content workflow:
│   - Primary channel: YouTube ({frequency})
│   - Secondary: Newsletter ({frequency})
│   - Distribution: {social_platforms}
│   - Analytics: {tools}
│
│   Content style preferences:
│   - Tone: {from SOUL.md vibe}
│   - Length: {preferences}
│   - Topics: {from USER.md interests}
│
│   ## Part 2: YouTube Workflow
│   ### Research Phase
│   1. Check trending topics in {niche} via {tool}
│   2. Cross-reference with {analytics} for audience interest
│   3. Output: topic_suggestions.md with 5 ranked ideas
│
│   ### Scripting Phase
│   1. Select topic from suggestions (APPROVAL GATE)
│   2. Research topic depth via web search
│   3. Draft script following {client_style} template
│   4. Output: script draft to {delivery_channel}
│
│   ### Production Phase
│   ...
│
│   ## Part 3: Newsletter Workflow
│   1. Trigger: cron Wednesday 8pm {timezone}
│   2. Pull recent content from {sources}
│   3. Draft newsletter matching {style_guide}
│   4. Send draft for review (APPROVAL GATE)
│   5. Publish via {tool} API
│
│   ## Part 4: Social Media Workflow
│   ...
│
│   ## Part 5: Analytics Integration
│   - YouTube Analytics API endpoints used
│   - Newsletter open rate tracking
│   - Social engagement metrics
│   - Weekly report format
│
│   ## Part 6: Tool Configuration
│   | Tool | Base URL | Auth Header | Key Endpoints |
│   |------|----------|-------------|---------------|
│   | YouTube | googleapis.com/youtube/v3 | Bearer {token} | search, videos, analytics |
│   | ConvertKit | api.convertkit.com/v3 | api_key param | broadcasts, subscribers |
│
│   ## Part 7: Patterns & Learnings
│   ### Patterns That Work
│   - {populated after first self-improve cycle}
│
│   ### Patterns To Avoid
│   - {populated after first self-improve cycle}
│
│   ### Known Issues
│   - {populated after first self-improve cycle}
│
├── question.md
│   ---
│   type: expert-file
│   parent: "[[content/_index]]"
│   file-type: command
│   command-name: question
│   tags: [expert-file, command, read-only]
│   ---
│
│   # Content Expert - Question Mode
│
│   > Answer questions about content workflows without making changes.
│
│   ## Purpose
│   Query content production processes, tool configurations,
│   and scheduling without modifying any files.
│
│   ## Allowed Tools
│   `Read, Glob, Grep, Bash(read-only)`
│
│   ## Question Categories
│
│   ### 1. YouTube Questions
│   Examples: "How does the script drafting work?"
│   Resolution: Read expertise.md Part 2
│
│   ### 2. Newsletter Questions
│   Examples: "When does the newsletter go out?"
│   Resolution: Read expertise.md Part 3
│
│   ### 3. Social Media Questions
│   Examples: "Which platforms are we posting to?"
│   Resolution: Read expertise.md Part 4
│
│   ### 4. Analytics Questions
│   Examples: "How do I check last week's performance?"
│   Resolution: Read expertise.md Part 5
│
│   ### 5. Tool/API Questions
│   Examples: "What's the ConvertKit API key?"
│   Resolution: Read expertise.md Part 6
│
│   ### 6. Troubleshooting Questions
│   Examples: "The newsletter didn't send last week"
│   Resolution: Read expertise.md Part 7, check cron logs
│
├── plan.md
│   (Standard plan template — analyze request against expertise,
│    produce implementation plan in specs/)
│
├── plan_build_improve.md
│   (Standard PBI template — plan→build→self-improve
│    with human-in-the-loop gates)
│
├── self-improve.md
│   (Standard self-improve template — after runs, update
│    expertise.md Part 7 with new patterns/learnings)
│
├── schedule-content.md          ← DOMAIN-SPECIFIC COMMAND
│   ---
│   type: expert-file
│   parent: "[[content/_index]]"
│   file-type: command
│   command-name: schedule-content
│   model: sonnet
│   tags: [expert-file, command, automation, content]
│   ---
│
│   # Content Expert - Schedule Content
│
│   > Automated content scheduling across all channels.
│
│   ## Purpose
│   Create and schedule content across YouTube, newsletter,
│   and social media channels.
│
│   ## Allowed Tools
│   `Read, Write, Edit, Bash, Glob, Grep`
│
│   ## Workflow
│
│   ### Phase 1: Load Context
│   1. Read expertise.md for current content calendar
│   2. Read MEMORY.md for mission statement alignment
│   3. Check recent analytics for topic performance
│
│   ### Phase 2: Generate Content Plan
│   1. Research trending topics in {niche}
│   2. Cross-reference with audience analytics
│   3. Propose 5 content ideas with rationale
│   4. **[APPROVAL GATE]** Client selects topics
│
│   ### Phase 3: Draft Content
│   1. Write YouTube script outline
│   2. Draft newsletter body
│   3. Generate social media posts (3 platforms)
│   4. **[APPROVAL GATE]** Client reviews drafts
│
│   ### Phase 4: Schedule
│   1. Create cron jobs for newsletter send
│   2. Queue social posts via {tool} API
│   3. Add production tasks to calendar
│   4. Announce schedule to {delivery_channel}
│
│   ## Report Format
│   ```
│   # Content Scheduled
│   ## This Week
│   - YouTube: {topic} (shoot: {date})
│   - Newsletter: {subject} (send: Wed 8pm)
│   - Social: {N} posts queued ({platforms})
│   ## Approval Needed
│   - {items requiring review}
│   ```
│
└── research-topics.md           ← DOMAIN-SPECIFIC COMMAND
    (Trending topic discovery workflow)
```

---

## Pipeline Commands (How It Runs)

### The CLI Flow

```bash
# Step 1: Parse the consulting transcript
/experts:tac-coding:parse-transcript transcript.md

# Step 2: Build workspace files (SOUL, USER, IDENTITY, etc.)
/experts:tac-coding:build-workspace session_output/

# Step 3: Build domain experts (one per domain, can run parallel)
/experts:tac-coding:build-domain-expert session_output/domains/content.json
/experts:tac-coding:build-domain-expert session_output/domains/business.json
/experts:tac-coding:build-domain-expert session_output/domains/personal.json

# Step 4: Validate the complete package
/experts:tac-coding:validate-package client-workspace/

# Step 5: Deploy to client's OpenClaw instance
/experts:tac-coding:deploy client-workspace/ --host 1.2.3.4 --key ~/.ssh/client.pem
```

### Inside build-domain-expert (the core loop)

```
┌──────────────────────────────────────────────────────┐
│  /experts:tac-coding:build-domain-expert content.json │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  PLAN (ACT)                                    │  │
│  │                                                │  │
│  │  1. Load content.json (workflows, tools, prefs)│  │
│  │  2. Load TAC expertise (pattern selection)     │  │
│  │  3. Classify workflows by TAC pattern:         │  │
│  │     • write-newsletter → TAC-3 (template)     │  │
│  │     • research-trends  → TAC-6 (one purpose)  │  │
│  │     • schedule-posts   → TAC-5 (feedback loop)│  │
│  │  4. Identify missing info:                     │  │
│  │     • ConvertKit API → dispatch browser agent │  │
│  │     • Newsletter style → dispatch youtube     │  │
│  │       (search "OpenClaw newsletter workflow")  │  │
│  │  5. Output: domain-plan.md                     │  │
│  └─────────────────────┬──────────────────────────┘  │
│                        ▼                              │
│  ┌────────────────────────────────────────────────┐  │
│  │  BUILD (ACT)                                   │  │
│  │                                                │  │
│  │  Write 8 expert files:                         │  │
│  │  1. _index.md (domain overview + command list) │  │
│  │  2. expertise.md (7-part mental model)         │  │
│  │  3. question.md (6 question categories)        │  │
│  │  4. plan.md (planning workflow)                │  │
│  │  5. plan_build_improve.md (full PBI cycle)     │  │
│  │  6. self-improve.md (learning workflow)         │  │
│  │  7+ domain-specific commands                   │  │
│  │                                                │  │
│  │  Write OpenClaw skills:                        │  │
│  │  For each workflow:                            │  │
│  │  • skills/{domain}/{workflow}/SKILL.md         │  │
│  │  • Cron job definition (if scheduled)          │  │
│  │  • HEARTBEAT.md entry (if periodic)            │  │
│  └─────────────────────┬──────────────────────────┘  │
│                        ▼                              │
│  ┌────────────────────────────────────────────────┐  │
│  │  IMPROVE (LEARN)                               │  │
│  │                                                │  │
│  │  1. Review what was built vs. plan             │  │
│  │  2. Capture API research findings →            │  │
│  │     expertise.md Part 6 (tool config)          │  │
│  │  3. Capture YouTube tutorial patterns →        │  │
│  │     expertise.md Part 7 (patterns)             │  │
│  │  4. Update TAC Coding Expert's own             │  │
│  │     self-improve with domain learnings         │  │
│  └─────────────────────┬──────────────────────────┘  │
│                        ▼                              │
│  ┌────────────────────────────────────────────────┐  │
│  │  VALIDATE                                      │  │
│  │                                                │  │
│  │  Structural:                                   │  │
│  │  □ All 8 expert files present                  │  │
│  │  □ _index.md lists all commands                │  │
│  │  □ expertise.md has all 7 parts                │  │
│  │  □ Frontmatter valid on all files              │  │
│  │                                                │  │
│  │  Skills:                                       │  │
│  │  □ SKILL.md frontmatter parses                 │  │
│  │  □ metadata is single-line JSON                │  │
│  │  □ Description: "{category}: {Name} - ..."     │  │
│  │  □ Steps are actionable (no placeholders)      │  │
│  │  □ Approval gates match AGENTS.md              │  │
│  │                                                │  │
│  │  Cron:                                         │  │
│  │  □ Expressions valid                           │  │
│  │  □ Timezone matches USER.md                    │  │
│  │  □ Delivery channel configured                 │  │
│  │                                                │  │
│  │  Score: ___/100                                │  │
│  │  If < 80 → loop back to BUILD with fixes      │  │
│  │  If >= 80 → domain COMPLETE                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## How Domains Get Their Specific Commands

The standard 6 files (_index, expertise, question, plan, plan_build_improve, self-improve) are the same structure for every domain. What makes each domain unique is:

1. **expertise.md content** — tailored to the client's specific workflows, tools, and preferences
2. **Domain-specific commands** — additional .md files based on what the domain needs

### Command Selection Logic (in TAC Coding Expert)

```
For each domain, analyze workflows and generate commands:

IF domain has scheduled outputs (newsletters, reports):
  → Generate: schedule-{type}.md command

IF domain has research/discovery workflows:
  → Generate: research-{topic}.md command

IF domain has sync/integration workflows:
  → Generate: sync-{tool}.md command

IF domain has content production:
  → Generate: draft-{content-type}.md command

IF domain has analytics/reporting:
  → Generate: report-{metric}.md command

IF domain has maintenance/cleanup tasks:
  → Generate: maintenance.md command

ALWAYS generate for every domain:
  → _index.md, expertise.md, question.md
  → plan.md, plan_build_improve.md, self-improve.md
```

### Example Domain-Specific Commands by Domain Type

| Domain Type | Likely Commands | Trigger Pattern |
|-------------|----------------|-----------------|
| **Content** | schedule-content, research-topics, draft-script | cron + on-demand |
| **Business** | sync-pipeline, generate-invoice, report-kpis | cron + webhook |
| **Personal** | morning-brief, optimize-calendar, track-habits | cron daily |
| **Development** | run-tests, deploy-staging, code-review | webhook + on-demand |
| **Finance** | reconcile-accounts, track-expenses, generate-report | cron weekly |
| **Marketing** | analyze-campaigns, schedule-ads, track-conversions | cron + on-demand |
| **Customer Success** | check-tickets, update-crm, send-followups | heartbeat |

---

## Agent Configs for Research Utilities

### Browser Research (dispatched during PLAN)

```yaml
dispatch: Task(subagent_type: "playwright-bowser-agent")
model: sonnet
max_turns: 15

prompt_template: |
  Research the {tool_name} API for OpenClaw integration.

  Find and return:
  1. Official API documentation URL
  2. Authentication method (API key, OAuth, Bearer token)
  3. Base URL for API calls
  4. Key endpoints needed for: {specific_actions}
  5. Rate limits or usage restrictions
  6. Check if MCP server exists: search npm for "mcp-server-{tool}"
  7. Check clawhub.com for OpenClaw plugin: "{tool}"

  Return as structured JSON:
  {
    "tool": "{tool_name}",
    "api_docs": "URL",
    "auth": { "method": "api_key|oauth|bearer", "header": "..." },
    "base_url": "...",
    "endpoints": [
      { "name": "...", "method": "GET|POST", "path": "...", "purpose": "..." }
    ],
    "rate_limits": "...",
    "mcp_server": "package_name or null",
    "clawhub_plugin": "plugin_name or null",
    "setup_notes": "..."
  }
```

### YouTube Research (dispatched during PLAN)

```yaml
dispatch: Task(subagent_type: "youtube-transcript-agent")
model: haiku
max_turns: 20

prompt_template: |
  Search YouTube for OpenClaw tutorials about: {topic}

  Search queries to try:
  - "OpenClaw {tool_name} integration"
  - "OpenClaw {tool_name} setup"
  - "OpenClaw {workflow_type} automation"

  For the most relevant video found:
  1. Extract full transcript
  2. Extract description (especially links)
  3. Summarize:
     - Configuration steps mentioned
     - API keys or credentials needed
     - Prompts used (copy verbatim if shown)
     - Skill examples (copy if shown)
     - Common pitfalls warned about
     - Model recommendations for this task

  Save to: .claude/context/tac-scan/{video_id}_*.txt
  Return: summary JSON with actionable findings
```

---

## Summary: What Ships to the Client

| Layer | What It Is | Where It Lives |
|-------|-----------|---------------|
| **OpenClaw Workspace** | SOUL, USER, IDENTITY, MEMORY, AGENTS, TOOLS, HEARTBEAT | `~/.openclaw/workspace/` on client instance |
| **OpenClaw Skills** | SKILL.md per workflow (cron triggers, delivery config) | `~/.openclaw/workspace/skills/{domain}/` |
| **OpenClaw Config** | Model routing, channels, allowlists, session rules | `~/.openclaw/openclaw.json` |
| **Cron Jobs** | Scheduled tasks (morning brief, syncs, reports) | `~/.openclaw/cron/jobs.json` |
| **Claude Code Experts** | Full expert system per domain (for ongoing self-improvement) | `.claude/commands/experts/{domain}/` |

The **experts** are the gift that keeps giving. After deployment, the client (or their OpenClaw) can run:
- `/experts:content:question "How does my newsletter skill work?"`
- `/experts:content:plan_build_improve "Add Instagram Reels to my content pipeline"`
- `/experts:content:self-improve` (after discovering new patterns)

The experts ARE the consulting engagement made permanent. They encode everything we learned about the client's domain into a self-improving knowledge system.
