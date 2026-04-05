# Pi Coding Agent Extensions — Research Report
**Date:** March 2026
**Scope:** Top/most popular extensions, skills, tools, and community packages for the Pi coding agent (pi-mono / shittycodingagent.ai)

---

## Background: What Is Pi?

Pi (also called the "shitty coding agent") is an open-source, minimal terminal coding harness built by Mario Zechner (badlogic). The core agent ships with only four built-in tools: read, write, edit, and bash. Everything else is added via composable extensions, skills, prompt templates, and themes written in TypeScript — shareable as npm packages or git repos.

- **GitHub:** https://github.com/badlogic/pi-mono — **24,300+ stars**
- **Website:** https://shittycodingagent.ai
- **npm:** `@mariozechner/pi-coding-agent`
- **Design philosophy:** "If you want the agent to do something it doesn't do yet, you ask the agent to extend itself." Extensions hook into agent lifecycle events; the LLM never sees the extension machinery.

---

## Ecosystem Overview

The Pi extension ecosystem has four types of packages:

| Type | Purpose |
|------|---------|
| **Extensions** | TypeScript modules that modify agent behavior via lifecycle hooks (context, tool_call, session_start, etc.) |
| **Skills** | Reusable prompt templates / tool wrappers for specific tasks (git, browser, search) |
| **Themes** | TUI visual customization |
| **Prompt Templates** | Frontmatter-driven model/skill/thinking configuration |

All packages install via:
```bash
pi install npm:<package-name>
pi install git:github.com/<user>/<repo>
```

---

## Section 1: Highest-Starred Extension Collections

### 1. oh-my-pi — 2,000+ stars, 174 forks
**GitHub:** https://github.com/can1357/oh-my-pi
**What it does:** A comprehensive fork/wrapper of Pi that bundles an entire tool harness into one install. Positioned as an "everything included" distribution.

Key capabilities added:
- **LSP integration** — 40+ language servers, format-on-write, inline diagnostics
- **Hash-anchored edits** — reliable code modifications across different models
- **Python tool** — persistent IPython kernel with helpers
- **SSH tool** — remote command execution
- **Browser automation** — Puppeteer with stealth scripts
- **Parallel subagent task tool** — isolated execution backends
- **Web search** — Exa, Brave, Jina, Perplexity providers
- **AI-powered conventional commits** with changelog generation
- **Image generation** — via Gemini or OpenRouter
- **MCP server support**
- **Universal config discovery** across 8 coding tools (Claude Code, Cursor, Windsurf, etc.)
- **Time Traveling Streamed Rules (TTSR)** — context-efficient pattern matching
- **Model roles system** — default, smol, slow, plan, commit

**Why it's popular:** Single install to get a fully-featured agent. Particularly valued by developers who want LSP diagnostics, browser automation, and subagents without configuring each separately.

---

### 2. mitsuhiko/agent-stuff — 1,600 stars, 107 forks
**GitHub:** https://github.com/mitsuhiko/agent-stuff
**Author:** Armin Ronacher (creator of Flask, Jinja2, Click — a major figure in the Python ecosystem)

**Extensions included:**
| Extension | What it does |
|-----------|-------------|
| answer.ts | Interactive Q&A interface for sequential questioning |
| context.ts | Displays skill inventory, token usage, loaded resources |
| control.ts | Manages controllable agent sessions (multi-agent) |
| files.ts | File browser with git status and session file tracking |
| go-to-bed.ts | Late-night safety guard — requires explicit confirmation after midnight |
| loop.ts | Iterative coding loop with optional auto-continuation |
| multi-edit.ts | Batch edits replacing default edit tool with patch support |
| notify.ts | Desktop notifications on agent completion |
| prompt-editor.ts | Mode selector with persistence and history |
| review.ts | Code review with diff display and optional fix loops |
| session-breakdown.ts | 7/30/90-day cost and usage analytics |
| todos.ts | File-backed todo management |
| uv.ts | Python/uv workflow helpers |
| whimsical.ts | Replaces "thinking" message with random whimsical phrases |

**Skills (19 total) — highlights:**
- GitHub (gh CLI recipes for PRs, CI, issues)
- Web automation (Chrome DevTools Protocol)
- Austrian public transit/rail APIs
- Reverse engineering (Ghidra integration)
- OpenSCAD design
- Tmux integration

**Why it's popular:** Ronacher's reputation brings credibility; the extensions represent best-practice patterns for building Pi extensions; widely referenced as a reference implementation in tutorials and blog posts.

---

### 3. badlogic/pi-skills — 823 stars, 85 forks (official skills repo)
**GitHub:** https://github.com/badlogic/pi-skills
**Author:** Mario Zechner (Pi's creator) — official/semi-official skills

**Skills included:**
| Skill | What it does |
|-------|-------------|
| brave-search | Web search and content extraction via Brave Search API |
| browser-tools | Interactive browser automation via Chrome DevTools Protocol |
| gccli | Google Calendar CLI — events and availability |
| gdcli | Google Drive CLI — file management and sharing |
| gmcli | Gmail CLI — email, drafts, and labels |
| transcribe | Speech-to-text via Groq Whisper API |
| vscode | VS Code integration for diffs and file comparison |
| youtube-transcript | Fetch YouTube video transcripts |

**Why it's popular:** Official source, compatible with Claude Code / Codex CLI / Amp / Droid in addition to Pi. Treated as the canonical reference for skill format.

---

## Section 2: Most-Starred Standalone Extensions

### 4. pi-web-access — 187 stars, 23 forks
**GitHub:** https://github.com/nicobailon/pi-web-access
**What it does:** Full web research suite for Pi — the most comprehensive single extension for internet access.

Capabilities:
- **Web search** via Perplexity or Gemini with synthesized answers and source citations; batch queries, recency filtering, domain restrictions
- **Content fetching** — readable markdown from any page, with smart fallbacks (Readability → Jina Reader → Gemini); handles JavaScript-heavy and blocked sites
- **PDF extraction** — text extraction from local and remote PDFs
- **GitHub integration** — clones repos locally instead of scraping; supports commit SHAs and private repos
- **YouTube** — full transcripts with timestamps, visual descriptions, chapter markers via Gemini
- **Local video analysis** — MP4/MOV/WebM up to 50MB; frame extraction with ffmpeg/yt-dlp
- **Browser curator UI** — Ctrl+Shift+S launches a manual result curation interface
- Zero-config when signed into a Chromium browser; fallback to API keys

**Why it's popular:** Combines search, fetch, video understanding, and PDF reading into one package. Referenced repeatedly in tutorials as the go-to web access solution.

---

### 5. awesome-pi-agent — 257 stars (curated list)
**GitHub:** https://github.com/qualisero/awesome-pi-agent
**What it does:** Community-maintained awesome list — not an extension itself but the primary discovery hub for the ecosystem. Most popular repo in the pi-agent GitHub topic.

Covers: extensions, skills, tools, themes, providers, utilities.

---

### 6. tmustier/pi-extensions — 102 stars, 8 forks
**GitHub:** https://github.com/tmustier/pi-extensions
**What it does:** 12-extension collection with a mix of productivity and entertainment.

| Extension | What it does |
|-----------|-------------|
| /readfiles | In-terminal file browser — navigate files, view diffs, select code, send to agent without leaving Pi |
| tab-status | Terminal tab shows ✅ done / 🚧 stuck / 🛑 timed out |
| ralph-wiggum | Manages long-running tasks without reducing model attention |
| agent-guidance | Switch between Claude/Codex/Gemini with model-specific guidance files |
| /usage | Cost, tokens, messages by provider/model dashboard |
| /paste | Paste editable text with optional keybinding |
| /code | Pick code blocks/snippets from assistant messages to copy, insert, or run |
| arcade | Mini-games (sPIce-invaders, picman, ping, tetris, mario-not) activated during test runs |
| weather | Weather info in session |
| extending-pi | Documentation guide for extension authors |
| skill-creator | Guided skill creation helper |
| import-cc-codex | Import Claude Code / Codex configurations |

**Why it's popular:** Practical productivity tools + the /readfiles file browser is widely cited as one of the most useful UI additions. Arcade extension gained attention for its novelty.

---

### 7. hjanuschka/shitty-extensions — 64 stars, 9 forks
**GitHub:** https://github.com/hjanuschka/shitty-extensions
**npm:** `shitty-extensions`
**What it does:** Community extension pack — 15 extensions and 1 skill.

| Extension | What it does |
|-----------|-------------|
| branch-sessions | Organizes Pi sessions by git branch — each branch gets its own conversation history |
| clipboard | Copy text to system clipboard via OSC52 (works over SSH, iTerm2, Kitty, Alacritty, WezTerm) |
| oracle | Get second opinions from alternative AI models without leaving the session; model picker with quick number keys |
| memory-mode | Save instructions to AGENTS.md with AI-assisted integration; project-local, project-wide, or global scope |
| plan-mode | Claude Code-style read-only exploration mode; /plan toggle, /todos, Shift+P shortcut, --plan CLI flag |
| handoff | Transfer context to a new focused session via `/handoff <goal>` |
| usage-bar | Provider usage stats with reset countdowns; supports Claude, Copilot, Gemini, Codex, Kiro, z.ai |
| ultrathink | Rainbow "ultrathink" animated text with Knight Rider shimmer (Ctrl+U) |
| status-widget | Persistent provider outage/incident indicator in footer |
| cost-tracker | Spending analysis from session logs; `/cost` (30-day) or `/cost <days>` |
| speedreading | RSVP speed reader with Optimal Recognition Point highlighting |
| loop | Conditional loops (ported from mitsuhiko) |
| branch-sessions | Git branch session isolation |
| flicker-corp | Fullscreen flicker effect |
| resistance | "Mysterious resistance transmission" |
| funny-working-message | Randomized "Working..." spinner text |

**Why it's popular:** Named "shitty-extensions" in homage to Pi's branding; covers real workflow needs (branch sessions, clipboard, oracle, plan-mode) that users wanted from Claude Code.

---

## Section 3: Notable Specialized Extensions (by GitHub topic)

### From the pi-agent GitHub Topic (sorted by stars):

| Repo | Stars | What it does |
|------|-------|-------------|
| splitrail | 130 | Cross-platform token usage tracker and cost monitor (Rust; works with Pi, Claude Code, Codex, Cursor) |
| juno-code | 52 | Task execution with automatic progress tracking and git commits (works with Pi, Claude Code, Codex, Cursor) |
| pi-supervisor | 20 | Extension that oversees the coding agent and steers it toward defined objectives |
| pi-schedule-prompt | 18 | Schedule and execute prompts at specific times/intervals |
| pi-prompt-suggester | 17 | Recommends the user's probable next prompt |
| pi-messenger-bridge | 14 | Bridges Telegram, WhatsApp, Slack, Discord into Pi sessions |
| pi-rewind | 9 | Checkpoint and restoration with diff preview and undo |
| pi-manage-todo-list | 8 | Structured task management with live progress widgets |
| pi-tasks | 7 | Multi-step work tracking with dependency management |

### From the pi-extension GitHub Topic (sorted by stars):

| Repo | Stars | What it does |
|------|-------|-------------|
| pi-packages | 31 | Extensions, skills, prompt templates, and themes collection |
| pi-superpowers-plus | 25 | AI tool enhancements |
| pi-agent-teams | 24 | Experimental agent swarm — Claude-style agent teams in Pi |
| pi-tool-display | 21 | OpenCode-style tool output rendering |
| pi-supervisor | 20 | Coding agent supervisor/steering |
| pi-gitnexus | 19 | GitNexus knowledge graph integration |
| pi-schedule-prompt | 18 | Timed/deferred prompt execution |
| pi-superpowers | 15 | Skills and superpowers collection |
| pi-messenger-bridge | 14 | Multi-platform messaging bridge |
| pi-listen | 12 | Hold-to-talk voice input via Deepgram streaming STT |

---

## Section 4: Curated Extension Collections

### tomsej/pi-ext — 18 stars
**GitHub:** https://github.com/tomsej/pi-ext
Extensions: Leader Key palette, Session Switcher, Model Switcher, Custom Footer, Pi Web Access bundled, Code Review (/review), Todos, Context (/context), Ghostty integration
Skills: commit, github, librarian
Themes: catppuccin-mocha

### ben-vargas/pi-packages — 31 stars
Mixed collection of extensions, skills, templates, and themes.

### rhubarb-pi (qualisero) — part of awesome-pi-agent author's work
Includes: notifications, session emoji, session color, safe-git

---

## Section 5: Orchestration and Multi-Agent Extensions

### agent-teams / pi-agent-teams — 24 stars
Manages specialized agent groups via YAML configuration; role-based multi-agent collaboration inspired by Claude's agent teams.

### agent-chains (from PI Agent Revolution article)
Creates sequential pipelines — "assembly lines" where each agent focuses on one step, passing refined output to the next.

### till-done (from PI Agent Revolution article)
Enforces structured task completion: agent must create a task list, each task progresses todo → in-progress → done, with evidence required before marking complete.

### sub-agent-support (from PI Agent Revolution article)
Spawns isolated child agents for parallel task execution, displaying progress in persistent TUI widgets.

### PiSwarm — listed in awesome-pi-agent
Parallel GitHub issue and PR processing using Pi agent and Git worktrees.

### task-factory — listed in awesome-pi-agent
Queue-first work orchestrator for Pi with planning, execution skills, and web UI.

---

## Section 6: Official/First-Party Extensions (built-in with pi-mono)

From the pi-mono coding-agent docs:

| Extension | Purpose |
|-----------|---------|
| cost-tracker | Session spending analysis |
| memory-mode | Save instructions to AGENTS.md |
| plan-mode | Read-only exploration mode |
| status-widget | Provider status in footer |
| handoff | Context transfer to new sessions |
| usage-bar | Usage statistics display |
| oracle | Second opinions from other models |

---

## Section 7: Web Research Extensions

### DeepWiki / Perplexity / Google Search (jfanals gist)
**GitHub Gist:** https://gist.github.com/jfanals/c8101d0a1afb683a3ef3b44708c53bc2

Three extensions adding grounded web research to Pi:

| Extension | API Required | What it does |
|-----------|-------------|-------------|
| DeepWiki | None (free) | Query GitHub repos via DeepWiki MCP — ask, structure, read actions |
| Perplexity Search | PERPLEXITY_API_KEY | Web search with synthesized answers and source citations |
| Google Search | GOOGLE_API_KEY | Grounded search via Gemini; 1,500 free searches/day (flash model) |

All three feature custom TUI rendering that collapses results to 3-line previews (expandable via Ctrl+O).

---

## Section 8: Developer Workflow Extensions

### pi-powerline-footer / nicobailon-pi-powerline-footer
Powerline-style status bar showing: directory, git branch, token usage, cost, context window utilization, active model.

### pi-rewind-hook
Git-based checkpoints enabling conversation branching and undo. Rewind file changes to any prior state.

### pi-ssh-remote
Redirects file operations to a remote host via SSH — enables using Pi locally while editing remote files.

### pi-canvas
Interactive TUI canvases: calendar view, document viewer, flight tracker.

### pi-notification-extension / pi-notify-pp
Telegram and system bell alerts on agent completion. pi-notify-pp adds tool stats and error tracking to notifications.

### pi-listen — 12 stars
Hold-to-talk voice input for Pi CLI using Deepgram streaming STT with live transcription.

### pi-gui — listed in awesome-pi-agent
Visual interface GUI extension (non-TUI).

### pi-mobile
Android client for Pi coding agent with session management over Tailscale.

### pi-dcp (dynamic context pruning)
Silently trims oversized tool results to conserve context tokens.

---

## Section 9: YouTube and Blog Coverage

**No dedicated YouTube extension review series was found.** The Pi coding agent does have YouTube coverage but it focuses on the agent itself rather than individual extensions.

Known video coverage:
- Maximilian Schwarzmüller produced a YouTube introduction to Pi (linked from the official docs/dragansr review)
- **YouTube link found:** https://www.youtube.com/watch?v=4p2uQ4FQtis (Pi coding agent tutorial, date unconfirmed)

**Blog posts covering extensions:**
| Source | URL | Focus |
|--------|-----|-------|
| Armin Ronacher (mitsuhiko) | https://lucumr.pocoo.org/2026/1/31/pi/ | Philosophy of self-extending agents; /answer, /todos, /review, /control, /files |
| Nader (OpenClaw) | https://nader.substack.com/p/how-to-build-a-custom-agent-framework | Extension lifecycle hooks; context pruning and compaction safeguards |
| Atal Upadhyay | https://atalupadhyay.wordpress.com/2026/02/24/pi-agent-revolution... | Best extensions for orchestration: agent-chains, till-done, sub-agent-support, orchestrator, learning |
| jprokay | https://jprokay.com/post/018-pi-coding-agent | Task Tracker (SQLite), Operations Dashboard (Sentry/Cloudflare/Railway/Supabase), multi-agent analysis |
| JoelClaw | https://joelclaw.com/extending-pi-with-custom-tools | Inngest Monitor extension pattern; widgets + silent messages architecture |
| DraganSr | https://blog.dragansr.com/2026/03/ai-tool-pi-coding-agent.html | General Pi overview with extension system |

---

## Section 10: Community Discussion

**Reddit:** No Pi-specific subreddit exists. Discussions appear in r/vibecoding (Pi has 226+ mentions per aitooldiscovery analysis), r/ChatGPT, and r/ArtificialIntelligence, but no dedicated extension review threads were indexed in web search.

**Hacker News:** Thread at https://news.ycombinator.com/item?id=46787507 — focused on Pi's architecture and extensibility philosophy. Key quote from user: "wrote a git branch stack visualizer for pi, in pi in like 5 minutes."

**Discord:** Pi has an active Discord community where packages are shared (referenced in official docs as a discovery mechanism alongside npm).

**X/Twitter:** Mario Zechner actively posts updates. Recent post: "I think pi is the most 'steerable' coding harness out there" after contributor Thomas Mustier added dequeuing to the extension system.

---

## Summary: Most Recommended Extensions by Use Case

| Use Case | Top Choice | Alt |
|----------|-----------|-----|
| All-in-one distribution | oh-my-pi (2k+ stars) | — |
| Web research | pi-web-access (187 stars) | DeepWiki/Perplexity gist |
| Multi-agent / orchestration | agent-chains, till-done, pi-agent-teams | PiSwarm |
| Official skills (search, calendar, gmail) | pi-skills (823 stars) | — |
| Community extension pack | mitsuhiko/agent-stuff (1.6k stars) | shitty-extensions |
| Cost tracking | splitrail (130 stars, multi-tool) | cost-tracker (shitty-extensions) |
| File browsing in TUI | /readfiles (tmustier/pi-extensions) | files.ts (agent-stuff) |
| Plan mode | plan-mode (shitty-extensions) | — |
| Branch session isolation | branch-sessions (shitty-extensions) | — |
| Second opinions | oracle (shitty-extensions) | — |
| UI / footer | pi-powerline-footer, pi-ext custom footer | — |
| Voice input | pi-listen | — |
| Notifications | pi-notification-extension, notify.ts (agent-stuff) | — |

---

## Sources

- [Pi Coding Agent (shittycodingagent.ai)](https://shittycodingagent.ai/)
- [pi-mono GitHub](https://github.com/badlogic/pi-mono) — 24.3k stars
- [awesome-pi-agent](https://github.com/qualisero/awesome-pi-agent)
- [oh-my-pi](https://github.com/can1357/oh-my-pi) — 2k+ stars
- [mitsuhiko/agent-stuff](https://github.com/mitsuhiko/agent-stuff) — 1.6k stars
- [badlogic/pi-skills](https://github.com/badlogic/pi-skills) — 823 stars
- [nicobailon/pi-web-access](https://github.com/nicobailon/pi-web-access) — 187 stars
- [tmustier/pi-extensions](https://github.com/tmustier/pi-extensions) — 102 stars
- [hjanuschka/shitty-extensions](https://github.com/hjanuschka/shitty-extensions) — 64 stars
- [tomsej/pi-ext](https://github.com/tomsej/pi-ext) — 18 stars
- [DeepWiki/Perplexity/Google Search gist](https://gist.github.com/jfanals/c8101d0a1afb683a3ef3b44708c53bc2)
- [GitHub pi-agent topic](https://github.com/topics/pi-agent)
- [GitHub pi-extension topic](https://github.com/topics/pi-extension)
- [Armin Ronacher — Pi: The Minimal Agent](https://lucumr.pocoo.org/2026/1/31/pi/)
- [Nader — How to Build a Custom Agent Framework with PI](https://nader.substack.com/p/how-to-build-a-custom-agent-framework)
- [Atal Upadhyay — PI Agent Revolution](https://atalupadhyay.wordpress.com/2026/02/24/pi-agent-revolution-building-customizable-open-source-ai-coding-agents-that-outperform-claude-code/)
- [jprokay — pi: The Coding Agent For Your Workflow](https://jprokay.com/post/018-pi-coding-agent)
- [JoelClaw — Extending Pi with Custom Tools](https://joelclaw.com/extending-pi-with-custom-tools)
- [DraganSr — AI tool: PI coding agent](https://blog.dragansr.com/2026/03/ai-tool-pi-coding-agent.html)
- [pi-coding-agent GitHub topic](https://github.com/topics/pi-coding-agent)
- [Hacker News thread](https://news.ycombinator.com/item?id=46787507)
