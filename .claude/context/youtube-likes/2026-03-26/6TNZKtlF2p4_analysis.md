---
title: "Every Claude Code Command in 13 minutes! (10x your productivity)"
creator: Duncan Rogoff
channel: "Duncan Rogoff | AI Automation"
channel_url: https://www.youtube.com/channel/UC37JpWP5PxLSma2lh79HU9A
video_url: https://www.youtube.com/watch?v=6TNZKtlF2p4
video_id: 6TNZKtlF2p4
upload_date: 2026-03-18
date_accessed: 2026-03-26
duration: "13:45"
view_count: 10375
like_count: 375
type: deep-dive-analysis
tags:
  - claude-code
  - slash-commands
  - productivity
  - cli-reference
  - tier-ranking
  - power-user
  - multi-agent
  - hooks
  - skills
  - mcp
---

# Every Claude Code Command -- Ranked and Tiered

## Executive Summary

Duncan Rogoff, a former art director turned AI agency operator, presents a comprehensive tier-ranking of every Claude Code slash command. The video organizes commands into 10 tiers from "non-negotiable setup" through "deprecated," giving viewers a clear priority map for which commands matter most. Rogoff runs a six-figure AI agency and a 2,000-member community (Buildroom), so the perspective leans practical and business-oriented rather than academic.

The most valuable insight is the tiering itself: most Claude Code users only scratch the surface with /init and /help, but the real leverage comes from Tier 3-4 commands like /fork, /btw, /hooks, /loop, and /skills. These are the commands that turn Claude Code from a chat-with-code tool into an autonomous development platform. Rogoff emphasizes session hygiene (clearing, compacting, model-switching) as a cost-saving discipline, which aligns with high-volume consulting usage.

The video is a solid reference catalog but stays shallow on each command (13 minutes across 60+ commands means roughly 13 seconds each). It is best used as a discovery checklist -- identifying commands you did not know existed -- rather than a deep tutorial on any single one.

## Complete Command Ranking by Tier

### Tier 1: Non-Negotiable Setup (Must-Have for Everyone)

| Command | Purpose | Notes |
|---------|---------|-------|
| /login | Authenticate with Anthropic account | First thing to run; password-based auth |
| /doctor | Diagnose installation health | Flags broken config before you start working |
| /init | Create/update CLAUDE.md | **The single most important command.** Gives Claude persistent project context, memory, tool preferences, folder rules, style guides |
| /config and /settings | Open settings UI | Theme, default model, output preferences, auto-cleanup behavior |
| /help | List all available commands | Gateway to everything else |

**Power-user note:** /init is already the backbone of the consulting-co workflow via CLAUDE.md. The video confirms this is universally considered the highest-priority command.

### Tier 2: Session Management (Core Daily Drivers)

| Command | Purpose | Notes |
|---------|---------|-------|
| /clear, /reset, /new | Wipe conversation history | Use when Claude hallucinates, feels slow, or context is bloated. Saves tokens. |
| /model | Switch models mid-session | Haiku = quick/cheap; Sonnet = daily driver; Opus = complex/multi-agent. Switch without restarting. |
| /cost | Check token spend | Direct cost visibility inside the CLI |
| /usage | Display plan limits and rate-limit status | Know when you are close to being locked out |
| /permissions and /allowed-tools | Control what Claude can do | Restrict file writes, terminal access, protect secrets/passwords |
| /compact | Compress conversation without full wipe | Keeps important context pieces; lighter than /clear |
| /context | Visualize full context window | See how full the window is; warns when approaching limits |
| /plan | Enter planning mode | Claude thinks through the problem before acting. Great for back-and-forth before committing to execution. |

**Power-user note:** /compact is underrated. In long consulting sessions with multiple file edits, compacting mid-session preserves continuity without the cost of a full context window. /plan is essential before any multi-step build task.

### Tier 3: Building and Code Review

| Command | Purpose | Notes |
|---------|---------|-------|
| /diff | Interactive viewer for uncommitted changes | Quick audit of what changed before committing |
| /rewind and /checkpoint | Roll back codebase to a previous point | Safety net when Claude goes off-track |
| /fork | Branch into parallel exploration paths | Test two solutions simultaneously; nothing gets lost; merge the best parts |
| /memory | Edit CLAUDE.md directly | Add persistent rules, corrections, preferences that survive across sessions |
| /security-review | Scan for vulnerabilities | Catches leaked credentials, login problems, security holes before shipping |
| /simplify | Reduce complexity of output | Clean up over-engineered code into simpler, optimized form |
| /tasks | View background tasks | See what is running in parallel |
| /btw | Ask a side question without polluting main context | **Highly useful.** Interrupt flow for a quick question, then resume the main thread |
| /debug | Troubleshoot session issues | Read logs, pinpoint errors, diagnose problems |

**Power-user note:** /fork is a standout for consulting work. When prototyping client solutions, fork to test two architectures, then merge. /btw is perfect for checking a reference without derailing a long coding session. /security-review should be part of every pre-delivery checklist.

### Tier 4: Power User and Agent Commands

| Command | Purpose | Notes |
|---------|---------|-------|
| /mcp | Connect to MCP servers | Plug into Notion, Slack, Google Drive, Linear, or any MCP-compatible platform |
| /bash | Batch job execution | Split large jobs into smaller separate tasks; each lands as its own PR |
| /loop | Repeat a prompt at intervals | Poll deployments, babysit PRs, schedule check-ins (e.g., every 5/10/15 min) |
| /claude-api | Load reference to Anthropic SDK | Auto-detects SDK imports; useful for building tools that call Claude programmatically |
| /plugin | Install/remove/manage plugins | Extend Claude Code functionality beyond built-in features |
| /agents | Configure multi-agent workflows | Set up and manage agent teams operating together |
| /hooks | Automated triggers on events | Run a checker on file save, ping when a task finishes, trigger actions on any event |
| /reload-plugins | Hot-reload active plugins | Apply changes without restarting the session |
| /skills | Browse and install skills | Access 60,000+ skills in the ecosystem; specialized capabilities on demand |

**Power-user note:** This tier is where consulting leverage multiplies. /mcp connections to Linear and Google Drive are already core to the consulting-co stack. /hooks enable the write-guard, bash-logger, and telemetry hooks already in use. /loop is potentially valuable for monitoring long-running deploys or watching the Linear agent harness. /skills at 60K+ in the ecosystem suggests checking for pre-built skills before building custom ones.

### Tier 5: Workflow and Output

| Command | Purpose | Notes |
|---------|---------|-------|
| /export | Export session as plain text | Save conversation for later reference or sharing |
| /copy | Copy last response to clipboard | Quick grab of code blocks or answers |
| /pr-comments | Fetch PR comments from GitHub | Review feedback without leaving the terminal |
| GitHub App install | Install Claude GitHub integration | Enables PR review, auto-commenting |
| Slack App install | Install Claude Slack integration | OAuth-based Slack connection |

**Power-user note:** /export is useful for building session archives for client deliverables. /pr-comments integrates with the existing GitHub-based consulting workflow.

### Tier 6: IDE and Environment

| Command | Purpose | Notes |
|---------|---------|-------|
| /ide | IDE integration settings | Connect to VS Code or other editors |
| /add-dir | Add additional working directories | Multi-directory project support |
| /desktop | Desktop app integration | Move between terminal and desktop Claude |
| /terminal-setup | Configure terminal settings | Key bindings, Shift+Enter support |
| /keybindings | Customize keyboard shortcuts | Terminal-specific shortcut config |
| /sandbox | Toggle sandbox mode | Isolated environment where Claude cannot affect the real filesystem |

**Power-user note:** /add-dir is relevant for the consulting-co setup which spans multiple directories (consulting-co, obsidian vault, gbautomation-marketplace-linear). /sandbox is worth toggling on when testing risky operations.

### Tier 7: Personalization and Cosmetics

| Command | Purpose | Notes |
|---------|---------|-------|
| /theme | Set color theme | Dark, light, colorblind-accessible options |
| /color | Color customization | Fine-grained color control |
| /status-line | Toggle status bar | Shows session info at bottom of terminal |
| /vim | Toggle vim keybindings | Switch between normal and editing modes |

### Tier 8: Informational

| Command | Purpose | Notes |
|---------|---------|-------|
| /status | Show version, account, connectivity | Quick health check |
| /stats | Visual breakdown of session history and streaks | Usage patterns over time |
| /insights | Generate report on usage patterns and friction points | Identifies bottlenecks in your workflow |
| /release-notes | Show recent version changes | Stay current with new features |
| /effort | Set effort level (low to max) | Lower = faster/cheaper; higher = deeper thinking |
| /fast | Quick, lighter responses | Reduces cost; good for simple queries |
| /privacy | View privacy settings and plan details | Data handling transparency |

**Power-user note:** /effort is a hidden gem for cost management. Setting effort to low for simple file reads or renames, then cranking to max for architecture decisions, could meaningfully reduce token burn across a consulting day. /insights is worth running weekly to identify workflow friction.

### Tier 9: Situational and Rarely Used

| Command | Purpose | Notes |
|---------|---------|-------|
| /rename | Rename the session | Organizational convenience |
| /resume and /continue | Reopen a previous session by ID | Pick up where you left off |
| /remote-control | Enable remote control of Claude | Useful for remote employee/agent scenarios |
| /remote-env | Set default remote environment | Configure remote execution defaults |
| /feedback and /bug | Submit feedback or bug reports | Direct line to Anthropic support |
| /extra-usage | View extra capacity limits | Check bonus allocation |
| /passes | Gift usage passes | Share with eligible accounts for a week |
| /chrome | Configure browser agent | Enable Claude to take browser actions |
| /mobile | iOS/Android QR download | Get Claude on mobile |
| /upgrade | Upgrade plan tier | Billing management |
| /logout | Sign out | End authenticated session |
| /exit and /quit | Close Claude Code | Terminal exit |

**Power-user note:** /resume is valuable for consulting -- pick up a client session from earlier in the day without re-explaining context. /chrome could integrate with the existing browser-automation skills.

### Tier 10: Deprecated

| Command | Purpose | Notes |
|---------|---------|-------|
| /review | Code review (deprecated) | Use /security-review or /diff instead |
| /stickers | Order physical stickers | Novelty; not functional |

## Key Insights and Takeaways

1. **Session hygiene is cost management.** Regularly using /clear, /compact, and /model switches prevents token waste. In a consulting context with multiple client sessions per day, this discipline compounds.

2. **/fork enables risk-free experimentation.** For client deliverables where you need to compare approaches (e.g., two architecture options for a client build), fork lets you try both without losing either.

3. **/btw preserves context integrity.** Side questions during long builds are inevitable. Using /btw instead of interrupting the main thread keeps Claude on track.

4. **/effort is an underused cost lever.** Most users leave effort at default. Explicitly setting low for routine tasks and max for complex reasoning could reduce daily token cost by 20-40%.

5. **/loop is a lightweight scheduler.** Instead of building custom polling scripts, /loop can watch deployments, retry failing tests, or check API status on an interval directly inside Claude Code.

6. **The Skills ecosystem is large (60,000+).** Before building a custom skill from scratch, check /skills for an existing one. This applies directly to the consulting-intake workflow -- there may be pre-built intake, scheduling, or CRM skills available.

7. **/hooks are the automation backbone.** Event-driven triggers (on save, on task completion) are already in use in the consulting-co stack but likely have untapped potential for client-facing automations.

## Commands You May Not Already Know About

| Command | Why It Matters |
|---------|---------------|
| /fork | Parallel solution exploration with merge capability -- not the same as git branching |
| /btw | Side-channel questions without polluting main context |
| /loop | Built-in polling/scheduling without external cron or Task Scheduler |
| /effort | Granular control over reasoning depth and cost |
| /insights | Automated workflow analysis -- identifies your own friction points |
| /fast | Quick-mode toggle for lightweight responses |
| /passes | Gift usage passes to client accounts for a week |
| /export | Session-to-text for client documentation and deliverables |
| /simplify | Post-build cleanup pass to reduce code complexity |
| /chrome | Native browser agent configuration (beyond the current WSL agent-browser setup) |

## Application to Consulting Power-User Workflow

### Daily Workflow Optimization
- **Start of day:** /doctor to verify setup, /status to check limits
- **Per-client session:** /init review, /plan before building, /fork for architecture decisions
- **Mid-session:** /compact when context bloats, /btw for side lookups, /effort low for file operations
- **Pre-delivery:** /security-review, /simplify, /diff for final audit
- **End of session:** /export for client archive, /cost for billing reconciliation

### Multi-Agent Consulting Stack
- /agents + /hooks form the foundation of the Linear coding agent harness
- /mcp connections bridge Claude Code to Linear, Google Drive, Slack -- all active in the current stack
- /loop could replace some Task Scheduler polling jobs (email watcher check-ins, deploy monitoring)
- /skills ecosystem should be audited for consulting-intake and client-research pre-built options

### Cost Management
- /model switching (Haiku for drafts, Sonnet for builds, Opus for architecture) is the primary lever
- /effort adds a second lever within a given model
- /cost + /usage provide real-time visibility
- /compact over /clear preserves context while reducing token load
