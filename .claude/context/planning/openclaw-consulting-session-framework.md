# OpenClaw Installation Consulting: 90-Minute Session Framework

## Overview
A structured discovery session that live-authors the client's OpenClaw workspace files. Every question maps to a specific file that OpenClaw reads at session start.

## Deliverable Map

```
~/.openclaw/workspace/
├── SOUL.md              ← Phase 1 Q4-6 (core truths, boundaries, vibe)
├── USER.md              ← Phase 1 Q1-3 (name, timezone, projects)
├── IDENTITY.md          ← Phase 1 Q7 (agent name, creature, emoji)
├── MEMORY.md            ← Phase 1 Q8-10 (mission, goals, preferences)
├── AGENTS.md            ← Phase 4 Q25-28 (autonomy, session, safety)
├── TOOLS.md             ← Phase 2 Q11-13 (devices, APIs, infrastructure)
├── HEARTBEAT.md         ← Phase 3 Q23 (periodic check tasks)
└── skills/
    ├── {domain-1}/
    │   └── {workflow-1}/
    │       └── SKILL.md ← Phase 3 Q17-22
    ├── {domain-2}/
    │   └── {workflow-2}/
    │       └── SKILL.md
    └── morning-brief/
        └── SKILL.md     ← Phase 3 Q24
```

Plus `openclaw.json` with: model config, channel setup, allowlists, cron jobs, session reset rules.

---

## Phase 1: Identity & Soul (15 min)
*Populates: SOUL.md, USER.md, IDENTITY.md, MEMORY.md*

### For USER.md:
1. **"What should your agent call you?"** (name, nickname, pronouns)
2. **"What timezone are you in, and what are your working hours?"** (timezone, availability window for cron jobs)
3. **"What are you currently working on — your top 2-3 active projects?"** (projects context)

### For SOUL.md — Core Truths:
4. **"When your agent does something for you, what does 'done well' feel like? Give me an example of when AI nailed it for you, and when it completely missed."**
   - Surfaces quality bar and communication preferences
   - Maps to "Core Truths" section of SOUL.md

5. **"How do you want your agent to handle uncertainty — should it ask you, make its best guess, or try and report back?"**
   - Maps to SOUL.md autonomy boundaries
   - Follow-up: "What should it NEVER do without asking?"

### For SOUL.md — Vibe:
6. **"Do you want your agent to feel like a professional assistant, a casual friend, a sharp executive, or something else?"**
   - Direct vibe setting
   - Follow-up: "Should it use emoji? Be terse or detailed? Match your energy or balance it?"

### For IDENTITY.md:
7. **"Let's name your agent. What feels right — something human, something playful, something serious?"**
   - Name, creature type, emoji, vibe
   - This is the BOOTSTRAP.md flow done collaboratively

### For MEMORY.md — Mission:
8. **"In one sentence, what are you trying to build with your life right now?"** (mission statement raw material)
9. **"What do you want to be true in 90 days that isn't true today?"** (measurable goal)
10. **"If your agent did one thing perfectly every night while you sleep, what would move the needle most?"** (first autonomous task candidate)

---

## Phase 2: Tools & Infrastructure (15 min)
*Populates: TOOLS.md, model configuration, channel setup*

### For TOOLS.md:
11. **"What devices will your agent live on — Mac Mini, laptop, VPS, Raspberry Pi?"**
    - Hardware spec determines local model capability

12. **"Walk me through the apps you use every day — productivity, communication, calendar, notes, anything."**
    - Each app = potential MCP connection or API integration
    - Follow-up for each: "Do you know if it has an API, or should your agent figure that out?"

13. **"Do you have any existing API keys or subscriptions — Anthropic, OpenAI, Brave, X?"**
    - Model selection (brain) and credentials setup
    - "What's your monthly budget for AI API costs?"

14. **"How do you want to communicate with your agent — WhatsApp, Telegram, Discord, iMessage, or just the dashboard?"**
    - Channel configuration for openclaw.json
    - Follow-up: "Should anyone else have access, or is this strictly personal?"
    - Security: "Do you use this device for anything sensitive?"

### For model routing (brains & muscles):
15. **"How do you think about cost vs. quality? Would you rather spend more for the best results, or optimize for cheap and good-enough?"**
    - Opus brain vs. cheaper brain, local models vs. API
    - Maps to brains & muscles architecture

---

## Phase 3: Domain Discovery & Workflows (30 min)
*Populates: skills/ directory, HEARTBEAT.md, cron jobs*

### Domain identification:
16. **"If you had to organize everything you do into 3-5 departments — like departments at a company — what would they be?"**
    - Each domain = a skills subdirectory and eventually an Expert
    - If they struggle: "Think job titles. If you hired 3 people, what would each own?"

### Per domain (repeat for top 2-3):

17. **"What's the most annoying recurring task in [domain]?"**
    - First skill candidate

18. **"Walk me through that task step by step. Pretend you're training someone on day one."**
    - This IS the SKILL.md body — written live
    - Interrupt when they skip: "Wait — how did you get from X to Y?"

19. **"What triggers this task — a time of day, an email arriving, a metric changing, or you just deciding?"**
    - Determines: cron job, webhook trigger, heartbeat task, or on-demand
    - Maps to OpenClaw scheduling: one-shot (`at`), interval (`every`), cron expression

20. **"When this task is done, what does the output look like? Where does it go?"**
    - Delivery config: announce to Telegram? Write to file? Update dashboard?
    - Maps to cron delivery modes: `announce`, `webhook`, `none`

21. **"What decisions do YOU make during this task vs. what's mechanical?"**
    - Decision points = approval gates
    - Mechanical = fully autonomous
    - Follow-up: "For the decisions, give me 2-3 rules of thumb you use."

22. **"If this went wrong, what would happen? Who would notice?"**
    - Blast radius → determines autonomy level
    - High-blast = approval gates; low-blast = autonomous

### For HEARTBEAT.md:
23. **"What should your agent check on every 30 minutes when it's idle?"**
    - New emails? Calendar? Social mentions? Analytics?
    - Follow-up: "What time should it go quiet — when do you sleep?"

### For morning brief (first cron job):
24. **"What do you want to see first thing in the morning? Imagine your perfect briefing."**
    - Weather, news, tasks, analytics, calendar?
    - Maps to: `openclaw cron add --name "Morning brief" --cron "0 7 * * *" --tz "..." --session isolated --announce`

---

## Phase 4: Autonomy & Safety (10 min)
*Populates: AGENTS.md boundaries, openclaw.json allowlists, session config*

25. **"On a scale of 'ask me everything' to 'just get it done,' where do you want your agent?"**
    - AGENTS.md safe-autonomously vs. requires-asking sections

26. **"Should your agent ever send messages on your behalf — emails, tweets, texts?"**
    - SOUL.md boundaries section

27. **"Who should be allowed to talk to your agent? Just you, or family/team too?"**
    - openclaw.json `allowFrom` configuration

28. **"How should sessions work — remember everything forever, or reset daily?"**
    - Session config: `reset.mode` and idle timeout
    - Memory architecture: daily logs vs. MEMORY.md curation

---

## Phase 5: Synthesis & Mission Statement (10 min)

29. **Read back a draft mission statement.** Template:
    > "[Agent Name] is a [vibe] [creature] that [primary function] across [domains], so that [User Name] can [desired outcome]. It operates [autonomy level] with [check-in frequency], focusing on [top priorities]."

30. **"Does this feel right? What would you change?"**
    - The refinement IS the final SOUL.md + MEMORY.md mission content
    - Follow-up: "If your agent read this before every single task, would it make better decisions?"

---

## Transcript Insights Applied

### From Alex Finn (5 Things to Do Immediately):
- Brain dump → Phase 1 structured extraction
- Connect tools → Phase 2 tool inventory
- Mission control → Post-session deliverable (agent-built)
- Mission statement → Phase 5 synthesis
- Set expectations → Phase 4 autonomy boundaries

### From Ras Mic (Recursive Improvement):
- Skills = SOPs → Phase 3 step-by-step workflow extraction
- "Tell it exactly what to do" → Phase 3 Q18 (day-one training format)
- Document successes as skills → Post-session plan-build-improve cycle
- Connect only tools you actually use → Phase 2 Q12 (daily apps only)

### From Dave Swift (Memory Fix):
- Obsidian vault integration → Phase 2 optional add-on
- File structure design → Phase 3 domain-based organization
- Security considerations → Phase 4 Q26-27
- Agent indexing → Post-session configuration

### From Alex Finn (100 Hours in 35 Min):
- Local > VPS → Phase 2 Q11 (device selection)
- Brains & muscles → Phase 2 Q15 (cost vs. quality)
- Reverse prompting → Consulting technique throughout
- Morning brief → Phase 3 Q24 (first cron job)
- Security boundaries → Phase 4 (full section)
