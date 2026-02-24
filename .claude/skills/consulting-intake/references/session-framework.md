# Consulting Session Framework: 30 Questions → OpenClaw Files

## Question-to-File Mapping

Every question in the 90-minute session maps to a specific OpenClaw workspace file.

---

## Phase 1: Identity & Soul (15 min)

### For USER.md
| # | Question | Extracts |
|---|----------|----------|
| 1 | "What should your agent call you?" | name, nickname, pronouns |
| 2 | "What timezone are you in, and what are your working hours?" | timezone, availability window |
| 3 | "What are you currently working on — your top 2-3 active projects?" | projects context |

### For SOUL.md — Core Truths
| # | Question | Extracts |
|---|----------|----------|
| 4 | "When your agent does something for you, what does 'done well' feel like? Give me an example of when AI nailed it, and when it completely missed." | quality bar, communication preferences |
| 5 | "How do you want your agent to handle uncertainty — should it ask you, make its best guess, or try and report back?" | autonomy boundaries. Follow-up: "What should it NEVER do without asking?" |

### For SOUL.md — Vibe
| # | Question | Extracts |
|---|----------|----------|
| 6 | "Do you want your agent to feel like a professional assistant, a casual friend, a sharp executive, or something else?" | vibe setting. Follow-up: "Should it use emoji? Be terse or detailed?" |

### For IDENTITY.md
| # | Question | Extracts |
|---|----------|----------|
| 7 | "Let's name your agent. What feels right — something human, something playful, something serious?" | name, creature type, emoji, vibe |

### For MEMORY.md — Mission
| # | Question | Extracts |
|---|----------|----------|
| 8 | "In one sentence, what are you trying to build with your life right now?" | mission statement raw material |
| 9 | "What do you want to be true in 90 days that isn't true today?" | measurable goal |
| 10 | "If your agent did one thing perfectly every night while you sleep, what would move the needle most?" | first autonomous task candidate |

---

## Phase 2: Tools & Infrastructure (15 min)

### For TOOLS.md
| # | Question | Extracts |
|---|----------|----------|
| 11 | "What devices will your agent live on — Mac Mini, laptop, VPS, Raspberry Pi?" | hardware spec, local model capability |
| 12 | "Walk me through the apps you use every day — productivity, communication, calendar, notes, anything." | tool inventory per app. Follow-up: "Does it have an API?" |
| 13 | "Do you have any existing API keys or subscriptions — Anthropic, OpenAI, Brave, X, OpenRouter?" | model selection, credentials. **OpenRouter is the recommended default** — one key gives access to 300+ models. If they don't have one, send them to openrouter.ai/keys. Follow-up: "Monthly budget for AI?" |

### For openclaw.json
| # | Question | Extracts |
|---|----------|----------|
| 14 | "How do you want to communicate with your agent — WhatsApp, Telegram, Discord, iMessage, or just the dashboard?" | channel config. Follow-ups: "Anyone else have access?" and "Sensitive data on device?" |

### For model routing
| # | Question | Extracts |
|---|----------|----------|
| 15 | "How do you think about cost vs. quality? And roughly what's your monthly AI budget?" | Selects model tier — see `references/model-tiers.md` for full model IDs and pricing. Map answer to tier: **Cheap** (< $20/mo): DeepSeek V3 brain + GLM-4 coder. **Mid** ($20–100/mo): Gemini Flash brain + DeepSeek V3 coder. **Pro** (> $100/mo): Gemini 2.5 Pro orchestrator + DeepSeek R1 for reasoning domains + DeepSeek V3 for coding domains — intelligent routing, no Claude tax. |

---

## Phase 3: Domain Discovery & Workflows (30 min)

### Domain identification
| # | Question | Extracts |
|---|----------|----------|
| 16 | "If you had to organize everything you do into 3-5 departments — like departments at a company — what would they be?" | domain names. Fallback: "Think job titles. If you hired 3 people, what would each own?" |

### Per domain (repeat for top 2-3)
| # | Question | Extracts |
|---|----------|----------|
| 17 | "What's the most annoying recurring task in [domain]?" | first skill candidate |
| 18 | "Walk me through that task step by step. Pretend you're training someone on day one." | SKILL.md body (the SOP). Interrupt: "Wait — how did you get from X to Y?" |
| 19 | "What triggers this task — a time of day, an email arriving, a metric changing, or you just deciding?" | trigger type: cron, webhook, heartbeat, on-demand |
| 20 | "When this task is done, what does the output look like? Where does it go?" | delivery config: announce, webhook, none |
| 21 | "What decisions do YOU make during this task vs. what's mechanical?" | approval gates vs. autonomous. Follow-up: "Give me 2-3 rules of thumb." |
| 22 | "If this went wrong, what would happen? Who would notice?" | blast radius → autonomy level |

### For HEARTBEAT.md
| # | Question | Extracts |
|---|----------|----------|
| 23 | "What should your agent check on every 30 minutes when it's idle?" | periodic tasks. Follow-up: "What time should it go quiet?" |

### For morning brief (first cron job)
| # | Question | Extracts |
|---|----------|----------|
| 24 | "What do you want to see first thing in the morning? Imagine your perfect briefing." | morning brief contents: weather, news, tasks, analytics |

---

## Phase 4: Autonomy & Safety (10 min)

### For AGENTS.md
| # | Question | Extracts |
|---|----------|----------|
| 25 | "On a scale of 'ask me everything' to 'just get it done,' where do you want your agent?" | safe-autonomously vs. requires-asking sections |
| 26 | "Should your agent ever send messages on your behalf — emails, tweets, texts?" | SOUL.md boundaries |
| 27 | "Who should be allowed to talk to your agent? Just you, or family/team too?" | openclaw.json allowFrom |
| 28 | "How should sessions work — remember everything forever, or reset daily?" | session reset mode, idle timeout, memory architecture |

---

## Phase 5: Synthesis & Mission Statement (10 min)

| # | Question | Extracts |
|---|----------|----------|
| 29 | Read back draft mission statement: "[Agent Name] is a [vibe] [creature] that [primary function] across [domains], so that [User Name] can [desired outcome]. It operates [autonomy level] with [check-in frequency], focusing on [top priorities]." | Final mission for SOUL.md + MEMORY.md |
| 30 | "Does this feel right? What would you change?" Follow-up: "If your agent read this before every task, would it make better decisions?" | Refined mission statement |

---

## Transcript Insight Sources

These questions are informed by patterns from the OpenClaw creator ecosystem:

| Creator | Video | Key Pattern Applied |
|---------|-------|-------------------|
| Alex Finn | "5 Things to Do Immediately" | Brain dump, mission statement, expectations |
| Ras Mic | "Recursively Improve Your Agent" | Skills = SOPs, step-by-step specificity |
| Dave Swift | "My OpenClaw Is Forgetting Everything" | Obsidian vault, memory architecture |
| Alex Finn | "100 Hours in 35 Minutes" | Brains & muscles, reverse prompting, security |
