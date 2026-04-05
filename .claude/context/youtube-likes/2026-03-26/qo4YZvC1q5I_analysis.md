---
title: "Claude Cowork + Obsidian Will Change How You Work Forever"
creator: Ben van Sprundel
channel: Ben AI
video_url: https://www.youtube.com/watch?v=qo4YZvC1q5I
video_id: qo4YZvC1q5I
date_accessed: 2026-03-26
upload_date: 2026-03-24
duration: "21:54"
views: 28182
likes: 841
type: deep-dive-analysis
tags:
  - second-brain
  - obsidian
  - claude-cowork
  - claude-code
  - business-os
  - knowledge-management
  - ai-agents
  - claude-skills
  - mcp
  - ai-consulting
  - personal-knowledge-management
  - automation
---

# Claude Cowork + Obsidian Will Change How You Work Forever

## Executive Summary

Ben van Sprundel (Ben AI) presents a compelling case for combining Obsidian as a personal knowledge vault with Claude Cowork (and Claude Code / Codex) to create a persistent "second brain" that AI agents can read from and write back to. The core thesis is that modern AI agents have become excellent at reasoning and execution, but they still lack **context** -- the persistent, structured knowledge about you, your business, your clients, your brand voice, and your operational decisions that makes their output actually useful. By maintaining a well-organized Obsidian vault and pointing Claude Cowork at it via a `claude.md` instruction file, you give every AI session instant access to your full business context without re-explaining anything.

The video walks through five key advantages of this setup (persistent context, bidirectional updates, skills amplification, cross-tool portability, and team scalability), explains the technical mechanism (Claude reads markdown files from the vault via its file system access), proposes a specific folder structure for both solopreneurs and agencies, and shows how to bootstrap the system quickly using Obsidian community plugins. Ben frames this not as a productivity hack but as a compounding strategic asset -- every decision logged, every correction saved, every preference documented accumulates into an intelligence layer that grows more valuable over time, creating a durable competitive moat.

What makes this video particularly relevant is that Ben is running an AI agency and accelerator, so his perspective maps closely to an AI consulting business model. He explicitly addresses the agency use case with client-specific folders, onboarding docs, and department-level SOPs -- a structure that parallels what GBAutomation already has in `.claude/skills/consulting-intake/client-sessions/`.

---

## Key Topics and Concepts

### 1. The Context Gap in AI Agents
- AI models (Claude, GPT, Codex) are increasingly capable at reasoning and task execution
- The bottleneck is no longer intelligence -- it is **context**
- Without persistent context, every conversation starts from zero: you re-explain your situation, project, workflows, preferences
- A second brain solves this by giving agents access to structured, always-current knowledge

### 2. The "Second Brain" Concept
- An Obsidian vault serves as the structured knowledge layer
- Contains markdown files organized by domain: business strategy, brand, team, projects, meetings, clients
- Obsidian's graph view visualizes relationships between documents (wiki-style linking)
- The vault is local-first (no cloud dependency), but readable by Claude Cowork, Claude Code, and Codex

### 3. The Five Advantages

**Advantage 1: Persistent Full-Context Conversations**
- Claude Cowork connects to the Obsidian vault (called a "Knowledge Vault")
- Any new session can immediately access all stored business context
- Example: "What should I focus on today?" -- Claude pulls from project priorities, meeting notes, and calendar context
- Example: "Write a LinkedIn post based on topics from this week's team meetings" -- Claude reads meeting transcripts, applies brand voice skill, outputs on-brand content

**Advantage 2: Bidirectional Knowledge Updates**
- Claude can not only read from the vault but **write back** to it
- When you make a decision, set a rule, or update a preference, you tell Claude to update the relevant file
- Example: "I never use em dashes in content" -> Claude updates the style/preferences file
- This means the knowledge base stays current without manual maintenance

**Advantage 3: Skills Amplification**
- Claude Skills are step-by-step instructions + code for specific processes/tasks
- Skills reference files inside the vault: ICP documents, brand voice profiles, templates, hook libraries
- With a rich vault, building new skills is dramatically faster because the context files already exist
- Example: A newsletter writer skill references the ICP, brand voice, and topic queue -- all stored in the vault
- Ben adds a meta-layer: skills themselves contain pointers (file paths) to where they find their reference docs

**Advantage 4: Cross-Tool Portability**
- The vault is just a folder of markdown files -- it works with any tool that can read the filesystem
- Claude Cowork, Claude Code, Codex, and any MCP-connected agent can all access the same knowledge base
- Switching between tools or providers does not mean losing your context

**Advantage 5: Team Scalability**
- Multiple team members can access the same vault (shared drive or git-synced)
- New team members get instant onboarding: the vault contains SOPs, brand guidelines, project context
- Strategy documents stay in sync -- updates propagate to everyone
- Engineers, marketers, and operators all work from the same source of truth

### 4. How It Works Technically
- Obsidian is a free, local-first markdown editor with a visual overlay (graph view, backlinks, folders)
- No API needed, no cloud sync required -- Claude reads files directly from disk
- A `claude.md` file at the vault root acts as a **system prompt layer**: it tells Claude how to navigate the vault, where to find specific types of information, and how to structure retrievals
- Claude Cowork's "Knowledge Vault" feature connects to the Obsidian folder
- When asked a question, Claude: (1) reads the `claude.md` routing file, (2) navigates to relevant vault files, (3) retrieves and synthesizes information, (4) answers with full context

### 5. Why Start Now (Compounding Intelligence)
- Multiple trends converging: better LLM reasoning, MCPs for software integration, scheduled tasks for autonomous operation
- Ben reports using AI agents as his primary interface for: Gmail, Google research, CRM, content creation
- The value is not in the tool -- it is in the **accumulated intelligence**: every decision logged, every correction saved, every preference documented
- After 6 months of compounding, a competitor starting fresh is not just behind by a tool -- they are behind by months of institutional knowledge
- This is framed as the "actual mode" of upcoming years for running a business

### 6. Recommended Vault Structure

**For Agencies / Professional Teams:**

```
vault-root/
  claude.md              # Routing instructions for AI agents
  contacts/              # Stakeholders, organization, operator, brand
  daily/                 # Daily logs, session notes, meeting transcripts
  departments/           # Community, engineering, partnerships, operations
    community/           # SOPs for community management
    engineering/         # Technical documentation
  intelligence/          # Transcripts, decisions, research, market insights
  onboarding/            # Team member and client onboarding
  projects/              # Active projects, client work, video production
  resources/             # Reusable assets: prompts, templates, frameworks, output examples
  tasks/                 # To-do lists, team member responsibilities
```

**For Solopreneurs (Simpler):**

```
vault-root/
  claude.md
  os/                    # Personal operating system: who you are, preferences, rules
  projects/              # What you're working on
  resources/             # Templates, prompts, reference material
  tasks/                 # Action items
```

Key principle: **start simple, grow naturally**. Do not over-optimize structure upfront. Let it evolve as your needs become clear.

---

## Detailed Workflow Breakdown

### Initial Setup Flow
1. Download Obsidian (free) and create a new vault
2. Choose to connect with Claude Cowork (the vault appears as a knowledge source)
3. Optionally install community plugins to help populate the vault faster
4. Create the `claude.md` file that acts as the routing/instruction layer
5. Begin populating with existing knowledge: business info, brand docs, project notes

### Daily Usage Pattern
1. Open a new Claude Cowork session -- it automatically has vault context
2. Ask strategic questions ("What should I focus on today?") that draw on project priorities and meeting history
3. Execute tasks using Skills that reference vault documents (write content, draft emails, analyze data)
4. When decisions are made or preferences change, tell Claude to update the relevant vault file
5. Scheduled tasks (Claude Cowork's scheduled task feature) can run autonomously against the vault

### Knowledge Routing via claude.md
- The `claude.md` file is the critical bridge between the AI agent and the vault
- It contains: folder descriptions, file naming conventions, instructions for how to find specific types of information
- Acts as a persistent system prompt that shapes every interaction
- Example directives: "Brand voice rules are in `resources/brand-voice.md`", "Meeting transcripts are in `daily/YYYY-MM-DD/`", "ICP details are in `intelligence/icp.md`"

---

## Key Insights and Takeaways

1. **Context is the last mile for AI agents.** Models are smart enough; the bottleneck is giving them the right information about your specific situation. A structured vault solves this.

2. **Bidirectional read/write is the game-changer.** The vault is not static documentation -- it is a living knowledge base that Claude actively maintains. This eliminates the "stale docs" problem.

3. **Skills + vault = compounding automation.** Each new skill you build leverages all the context already in the vault. The marginal cost of new automations drops over time.

4. **Markdown is the universal interchange format.** By keeping everything in plain markdown, you avoid lock-in to any specific AI provider or tool. Claude Code, Codex, or any future agent can read the same files.

5. **Start simple, do not over-engineer.** Ben explicitly warns against over-optimizing the folder structure. Start with a few folders, let it grow organically based on actual usage.

6. **The competitive moat is in the accumulated knowledge, not the tool.** Six months of logged decisions, preferences, and business context cannot be replicated by a competitor who just signs up for the same tool.

7. **Scheduled tasks unlock autonomous operation.** Combined with persistent context, Claude can run scheduled processes (content pipelines, research sweeps, reporting) without human prompting for each instance.

8. **The `claude.md` file is the architectural keystone.** It determines how effectively the AI navigates your vault. Investing in a well-structured routing file pays dividends across every session.

---

## Tools and Technologies Mentioned

| Tool | Role | Notes |
|------|------|-------|
| **Obsidian** | Knowledge vault / second brain | Free, local-first, markdown-based, graph view for relationships |
| **Claude Cowork** | Primary AI interface | Connects to Obsidian vault, scheduled tasks, skills execution |
| **Claude Code** | CLI-based AI agent | Can read Obsidian vault via filesystem access |
| **Codex** | Alternative AI agent | Also reads from the same vault (cross-tool portability) |
| **Claude Skills** | Process automation | Step-by-step instructions that reference vault documents |
| **MCPs** | Software connectors | Allow agents to interact with external tools (Gmail, CRM, etc.) |
| **Prompt Cowboy** | Prompting tool | Mentioned in Ben's tool stack |
| **Wispr Flow** | Voice-to-text | Mentioned in Ben's tool stack |
| **n8n** | Workflow automation | Mentioned in Ben's tool stack |
| **Relevance AI** | AI platform | Mentioned in Ben's tool stack |
| **Make.com** | Automation platform | Mentioned in Ben's tool stack |
| **Apify** | Web scraping | Mentioned in Ben's tool stack |
| **ElevenLabs** | Voice AI | Mentioned in Ben's tool stack |

---

## Application to AI Consulting with Claude Code and Obsidian

### What GBAutomation Already Has That Maps to This

Ben's system maps remarkably well to what is already built in the consulting-co repo. Here is the correspondence:

| Ben's Concept | GBAutomation Equivalent |
|---------------|------------------------|
| `claude.md` vault routing file | `CLAUDE.md` at repo root + `.claude/` folder structure |
| Obsidian vault with business context | `.claude/context/` folder with client research, transcripts, credentials |
| Skills referencing vault docs | `.claude/skills/` with 20+ skills referencing context files |
| Client-specific folders | `.claude/skills/consulting-intake/client-sessions/` |
| Daily logs and meeting notes | `.claude/session-summaries/` |
| Brand/voice documents | Style guide templates in consulting-intake |
| Intelligence/research folder | `.claude/context/research/`, `.claude/context/linkedin-research/` |

### Gaps and Opportunities

1. **Obsidian as the visual layer**: The consulting-co repo already has the *content* that Ben describes, but it lives in `.claude/context/` as flat files. Symlinking or mirroring key folders into the Obsidian vault at `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation` would add the graph view, backlinks, and visual navigation that Ben demonstrates. This is partially built (`.claude/skills/obsidian-vault/` exists).

2. **Bidirectional updates**: Ben emphasizes Claude writing back to the vault when decisions change. GBAutomation's `CLAUDE.md` and `MEMORY.md` serve this purpose but are monolithic. Breaking preferences, rules, and operational decisions into separate vault files (as Ben suggests) would make updates more granular and less prone to merge conflicts.

3. **The `claude.md` routing file pattern**: Ben's approach of a single routing file that tells Claude where to find everything is exactly what `CLAUDE.md` does, but the consulting-co version could benefit from more explicit file-path pointers (e.g., "Client ICP templates are at `.claude/skills/consulting-intake/templates/`" rather than relying on the agent to discover them).

4. **Scheduled tasks for client management**: Ben mentions Claude Cowork's scheduled task feature for autonomous operations. GBAutomation already has this via Windows Task Scheduler + `consulting-admin/email_watcher`. The next evolution would be scheduled vault-maintenance tasks: daily summaries written to the vault, stale project detection, client follow-up reminders.

5. **Team onboarding via vault**: If GBAutomation scales to subcontractors or partners, the vault becomes the onboarding mechanism. New team members get context instantly by reading the vault rather than sitting through knowledge transfer sessions.

6. **Compounding intelligence as a selling point**: Ben's framing of the second brain as a competitive moat is directly applicable to client pitches. When onboarding a new consulting client, the deliverable is not just agents and skills -- it is a *growing knowledge base* that makes their AI more effective over time. This is a retention and upsell argument.

### Recommended Next Steps

1. **Mirror key `.claude/context/` folders into the Obsidian vault** so the same content is browsable in Obsidian's graph view and accessible to Claude Code via the filesystem.

2. **Create a `claude.md` file in the Obsidian vault root** that acts as a routing index, pointing to key folders and explaining the structure (separate from the repo-level `CLAUDE.md` which is dev-focused).

3. **Break `MEMORY.md` into granular vault files**: `preferences.md`, `decisions-log.md`, `tool-quirks.md`, `client-rules.md` -- so Claude can update individual concerns without touching unrelated content.

4. **Build a "vault-sync" skill** that reconciles the consulting-co `.claude/context/` tree with the Obsidian vault, handling any structural differences.

5. **Document this pattern as a client deliverable template** in the consulting-intake system -- every new client gets an Obsidian vault + `claude.md` routing file as part of their onboarding package.
