# Obsidian Second Brain Build Session

> Based on Ben AI's "Claude Cowork + Obsidian Will Change How You Work Forever" (2026-03-24)
> Adapted for GBAutomation's existing Claude Code + Obsidian stack

---

## Prerequisites

- Obsidian installed (free at obsidian.md)
- Claude Code or Claude Cowork with filesystem access
- An existing vault OR willingness to create one
- ~45 minutes for initial setup, ongoing 5-10 min/day for maintenance

---

## Phase 1: Core Vault Architecture (15 min)

### Step 1.1 — Choose Your Structure

Ben recommends two templates depending on your setup:

**Agency / Professional Team:**

```
vault-root/
  claude.md                    # AI routing file (THE most important file)
  contacts/                    # People: clients, partners, team, vendors
    clients/                   # One file per client
    team/                      # Team member profiles + skills
    stakeholders/              # Investors, advisors, board
  daily/                       # Daily logs, session notes
    2026-03-26.md              # Today's log
  departments/                 # Functional areas with SOPs
    engineering/
    marketing/
    operations/
    community/
  intelligence/                # Research, transcripts, decisions
    market-research/
    competitor-analysis/
    transcripts/               # Meeting & call transcripts
    decisions/                 # Decision log (date + rationale)
  onboarding/                  # Templates for new team/clients
    team-member-template.md
    client-onboarding-template.md
  projects/                    # Active work
    project-template.md
  resources/                   # Reusable assets
    prompts/                   # Prompt library
    templates/                 # Document templates
    frameworks/                # Mental models, methodologies
    brand/                     # Voice, style, visual identity
      brand-voice.md
      icp.md                   # Ideal Customer Profile
      style-rules.md
    output-examples/           # Gold-standard outputs for reference
  tasks/                       # Action items, to-do lists
    backlog.md
    this-week.md
```

**Solopreneur (Simpler):**

```
vault-root/
  claude.md
  os/                          # Personal operating system
    about-me.md                # Who you are, background, expertise
    preferences.md             # Communication style, tool prefs, rules
    goals.md                   # Current quarter goals
  projects/
  resources/
  tasks/
```

**Key principle from Ben**: Start simple. Do NOT over-optimize the folder structure upfront. Let it grow naturally based on what you actually need.

### Step 1.2 — Create the Folders

In Obsidian, create the top-level folders. Don't worry about populating them yet — that comes in Phase 2.

---

## Phase 2: The claude.md Routing File (10 min)

This is the **single most important file** in the entire system. It acts as a system prompt layer that tells any AI agent how to navigate your vault.

### Step 2.1 — Create `claude.md` at vault root

```markdown
# Vault Navigation Guide

This is [Your Name]'s business knowledge vault. Use this file to understand
the structure and find information efficiently.

## Structure

### /contacts
People I work with. One markdown file per person.
- `/contacts/clients/` — Active and past clients. Each file has: name, company,
  engagement dates, key goals, communication preferences, session history.
- `/contacts/team/` — Team members with roles, skills, availability.

### /daily
Daily logs in YYYY-MM-DD.md format. Contains:
- What happened today (meetings, decisions, wins, blockers)
- Session notes from AI interactions
- Action items generated during the day

### /departments
Functional area documentation and SOPs.
- Each subfolder has a README.md explaining the department's scope
- SOPs are named descriptively: `content-repurposing-sop.md`

### /intelligence
Research, analysis, and institutional knowledge.
- `/intelligence/transcripts/` — Meeting and call transcripts
- `/intelligence/decisions/` — Decision log. Each entry: date, decision,
  rationale, alternatives considered, outcome (updated later)
- `/intelligence/market-research/` — Industry analysis, competitor notes

### /onboarding
Templates and checklists for bringing new people up to speed.

### /projects
Active work. One folder per project with:
- `README.md` — project overview, goals, status
- Supporting docs as needed

### /resources
Reusable assets that don't belong to a specific project.
- `/resources/brand/brand-voice.md` — Tone, style rules, examples
- `/resources/brand/icp.md` — Ideal Customer Profile
- `/resources/prompts/` — Prompt library organized by use case
- `/resources/templates/` — Document templates
- `/resources/output-examples/` — Gold-standard outputs for reference

### /tasks
Action items and to-do tracking.
- `this-week.md` — Current week priorities
- `backlog.md` — Everything else

## Rules

1. When I ask you to remember something, update the relevant file in this vault
2. When referencing brand voice, always read `/resources/brand/brand-voice.md` first
3. Daily logs go in `/daily/YYYY-MM-DD.md`
4. Decisions get logged in `/intelligence/decisions/` with date and rationale
5. New client information goes in `/contacts/clients/{client-name}.md`
6. When creating content, check `/resources/brand/icp.md` for audience targeting
```

### Step 2.2 — Customize for Your Business

Replace generic descriptions with your actual business context. The more specific your routing file, the better Claude navigates your vault.

**Ben's insight**: This file is the architectural keystone. Every minute invested here pays dividends across every future session.

---

## Phase 3: Seed Your Vault With Existing Knowledge (15 min)

Don't start from zero — you already have knowledge scattered across tools. Pull it in.

### Step 3.1 — Personal Operating System

Create `os/about-me.md` (or `contacts/me.md` for agency structure):

```markdown
# About Me

## Role
[Your title, company, what you do]

## Expertise
- [Domain 1]
- [Domain 2]

## Current Focus
[What you're working on this quarter]

## Communication Style
- [Preferences: direct/casual, length, formatting]
- [Things you never want: em dashes, emojis, etc.]

## Tools I Use Daily
- [Tool 1 — what for]
- [Tool 2 — what for]
```

### Step 3.2 — Brand Voice (if applicable)

Create `resources/brand/brand-voice.md`:

```markdown
# Brand Voice

## Tone
[Professional but approachable / Technical but accessible / etc.]

## Rules
- Always: [things to always do]
- Never: [things to never do]
- Formatting: [bullet points vs paragraphs, heading style, etc.]

## Examples
### Good output example:
[Paste a real example of content you liked]

### Bad output example:
[Paste something that missed the mark and explain why]
```

### Step 3.3 — Active Projects

Create one file per active project in `/projects/`:

```markdown
# [Project Name]

## Status: [Active / On Hold / Planning]
## Started: [Date]
## Goal: [One sentence]

## Context
[2-3 paragraphs of background]

## Key Decisions Made
- [Date]: [Decision] — because [rationale]

## Current Blockers
- [Blocker 1]

## Next Steps
- [ ] [Action item]
```

### Step 3.4 — Import Existing Docs

Pull from wherever your knowledge currently lives:
- **Google Docs** → export as markdown, drop in relevant folder
- **Notion** → export workspace as markdown
- **Existing CLAUDE.md / MEMORY.md** → split into granular vault files
- **Meeting transcripts** → drop into `/intelligence/transcripts/`
- **Client notes** → one file per client in `/contacts/clients/`

---

## Phase 4: Connect to Claude (5 min)

### Option A: Claude Cowork (Desktop App)

1. Open Claude Cowork
2. Go to Settings → Knowledge Vault
3. Point it to your Obsidian vault folder
4. Claude now has persistent access to all vault files

### Option B: Claude Code (CLI)

Claude Code already reads the filesystem. Two approaches:

**Approach 1 — Symlink vault into your project:**
```bash
# On Windows (run as admin)
mklink /D "C:\your-project\.obsidian-vault" "C:\Users\you\obsidian\YourVault"
```

**Approach 2 — Reference in CLAUDE.md:**
Add to your project's `CLAUDE.md`:
```markdown
## Obsidian Vault
Business knowledge vault at: C:\Users\you\OneDrive\Desktop\obsidian\YourVault
Read claude.md in the vault root for navigation instructions.
```

### Option C: Codex or Other Agents

Any agent with filesystem access can read the same vault. That's the portability advantage — switch providers without losing context.

---

## Phase 5: Daily Usage Patterns

### Morning Kickoff (2 min)

Open Claude and ask:
> "Read my vault. What should I focus on today based on my current projects, this week's tasks, and any recent decisions?"

Claude reads `/tasks/this-week.md`, `/projects/*/README.md`, and `/daily/` recent entries to give a contextual answer.

### During Work — Bidirectional Updates

When you make a decision:
> "Update the decision log: We decided to use Stripe instead of LemonSqueezy for payments because of their invoicing API. Log this in the decisions folder."

When you learn a preference:
> "Update my brand voice rules: Never use the word 'leverage' — use 'use' instead."

When you finish a meeting:
> "Here's the transcript from today's client call with [Name]. Save it to the transcripts folder and update the client's contact file with key takeaways."

### Content Creation With Full Context

> "Write a LinkedIn post about [topic]. Use my brand voice from the vault, reference my ICP for targeting, and check if I've posted about this topic recently in my daily logs."

Claude reads 3-4 vault files, synthesizes, and writes on-brand content without you re-explaining anything.

### End of Day Log (2 min)

> "Create today's daily log. Summarize what we worked on, decisions made, and any action items. Save to /daily/2026-03-26.md"

---

## Phase 6: Skills That Reference the Vault

This is where the compounding effect kicks in. Skills reference vault files, so every new skill benefits from all existing knowledge.

### Example: Newsletter Writer Skill

```markdown
# Newsletter Writer

## References
- Brand voice: /resources/brand/brand-voice.md
- ICP: /resources/brand/icp.md
- Topic queue: /tasks/content-backlog.md
- Past newsletters: /projects/newsletter/archive/

## Process
1. Read the topic queue, pick the next topic
2. Read the ICP to understand audience pain points
3. Read brand voice rules
4. Draft the newsletter
5. Check against output examples in /resources/output-examples/
6. Save draft to /projects/newsletter/drafts/
```

### Example: Client Research Skill

```markdown
# Client Research

## References
- Client file: /contacts/clients/{client-name}.md
- ICP: /resources/brand/icp.md
- Past session notes: /intelligence/transcripts/

## Process
1. Read the client's existing file for context
2. Research their company, recent news, LinkedIn activity
3. Update the client file with new findings
4. Flag any alignment with our ICP
5. Suggest talking points for next session
```

### The Compounding Effect

Each skill you build is faster than the last because:
- Brand voice? Already documented.
- ICP? Already in the vault.
- Client context? Already captured from previous sessions.
- Style rules? Already enforced.

**Ben's key insight**: The marginal cost of new automations drops over time. Your first skill takes an hour. Your twentieth takes 10 minutes because 90% of the context files already exist.

---

## Phase 7: The Competitive Moat Argument

Ben frames this as a strategic business asset, not just a productivity tool:

```
Month 1:  Basic vault, a few docs, some skills
Month 3:  Dozens of decisions logged, client histories, refined brand voice
Month 6:  Hundreds of entries, nuanced preferences, proven workflows
Month 12: Deep institutional knowledge that no competitor can replicate
```

A competitor who starts the same tool 6 months later is not behind by a tool — they're behind by 6 months of accumulated intelligence. The vault IS the moat.

### For Consulting Clients (GBAutomation angle)

This reframes the deliverable:
- You're not just selling agents and skills
- You're selling a **growing knowledge base** that makes their AI more effective over time
- Every session adds to the vault
- The longer they use it, the more valuable it becomes
- This is a retention argument AND an upsell argument

---

## Phase 8: Maintenance and Evolution

### Weekly Review (10 min)

- Scan `/tasks/` — anything stale? Archive or update
- Check `/intelligence/decisions/` — any outcomes to log?
- Review `/daily/` entries — any recurring patterns to turn into SOPs?
- Prune or merge files that have grown redundant

### Monthly Evolution

- Review folder structure — does it still serve you?
- Add new folders only when you genuinely need them
- Build new skills that leverage existing vault content
- Update `claude.md` routing file if structure changed

### Anti-Patterns to Avoid

1. **Over-engineering upfront** — Don't build 20 empty folders. Start with 4-5 and grow.
2. **Treating it as documentation** — It's a living knowledge base, not a wiki. Update it during work, not after.
3. **Manual-only updates** — Use bidirectional writes. Tell Claude to update files as decisions happen.
4. **Ignoring the routing file** — If `claude.md` is stale, Claude navigates poorly. Keep it current.
5. **Perfectionism** — A messy vault that gets used beats a perfect vault that doesn't exist.

---

## Quick Start Checklist

- [ ] Create vault in Obsidian (or use existing)
- [ ] Create top-level folders (start with 4-6 max)
- [ ] Write `claude.md` routing file at vault root
- [ ] Create `about-me.md` with role, expertise, preferences
- [ ] Create `brand-voice.md` with tone and rules
- [ ] Add 2-3 active project files
- [ ] Connect vault to Claude (Cowork, Code, or Codex)
- [ ] Test: ask Claude "What should I focus on today?"
- [ ] Test: tell Claude to update a preference and verify the file changed
- [ ] Create your first skill that references vault files
- [ ] Start daily logging (even just 2 sentences per day)

---

## GBAutomation-Specific Mapping

What you already have and where it maps:

| Ben's Concept | Your Existing Equivalent | Gap |
|---------------|------------------------|-----|
| `claude.md` routing | `CLAUDE.md` at repo root | Need vault-specific version in Obsidian |
| `/contacts/clients/` | `.claude/skills/consulting-intake/client-sessions/` | Mirror to Obsidian |
| `/intelligence/transcripts/` | `.claude/context/` (transcripts, research) | Mirror to Obsidian |
| `/resources/prompts/` | `.claude/skills/` (20+ skills) | Already strong |
| `/daily/` logs | `.claude/session-summaries/` | Mirror to Obsidian |
| `/departments/` SOPs | Not formalized | Build as you grow team |
| `/tasks/` | `TODO.md` at repo root | Could be more granular |
| Bidirectional updates | `MEMORY.md` (monolithic) | Break into granular files |
| Graph view | Obsidian vault exists but under-connected | Add wiki links between docs |

### Immediate Next Steps for GBAutomation

1. Create a `claude.md` in `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\` that routes to existing vault content
2. Build a sync skill that mirrors key `.claude/context/` files into the Obsidian vault
3. Break `MEMORY.md` into: `preferences.md`, `decisions.md`, `tool-quirks.md`, `client-rules.md`
4. Start daily logging in Obsidian `/daily/YYYY-MM-DD.md`
5. Template this whole pattern as a client deliverable in consulting-intake

---

*Source: Ben AI (Ben van Sprundel) — https://www.youtube.com/watch?v=qo4YZvC1q5I*
*Processed: 2026-03-26*
