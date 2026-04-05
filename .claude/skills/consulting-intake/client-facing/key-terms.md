# Key Terms: OpenClaw & AI Agent Glossary

A quick reference so you know what we're talking about during the session. No need to memorize — just scan before the call.

---

## Your Agent

| Term | What It Means |
|------|--------------|
| **OpenClaw** | The platform that runs your AI agent 24/7. Think of it as the operating system for your personal AI. |
| **Agent** | Your AI assistant. It has a name, personality, memory, and skills. It runs on your infrastructure. |
| **Gateway** | The service that keeps your agent online and connected to messaging channels. Runs on your device. |
| **Session** | A conversation with your agent. Sessions can reset daily or persist indefinitely. |
| **Workspace** | The folder on your device where all your agent's configuration lives. |

## Personality & Memory

| Term | What It Means |
|------|--------------|
| **SOUL.md** | Your agent's values and communication style. Like a constitution — it guides every decision. |
| **Vibe** | How your agent communicates. Professional? Casual? Terse? Detailed? You decide. |
| **MEMORY.md** | Long-term facts your agent should never forget. Mission statement, key preferences, big decisions. |
| **Identity** | Your agent's name, personality type, and signature emoji. |

## Skills & Automation

| Term | What It Means |
|------|--------------|
| **Skill** | A specific task your agent knows how to do. Like a recipe — step-by-step instructions for one workflow. |
| **Domain** | A "department" of your work (e.g., Content, Business, Personal). Each domain gets its own expert system. |
| **Workflow** | A repeatable process within a domain (e.g., "write weekly newsletter" is a workflow in the Content domain). |
| **Cron job** | A scheduled task that runs automatically. "Every morning at 7am, send my briefing." |
| **Heartbeat** | A periodic check-in. Your agent wakes up every 30 minutes and runs through a checklist. |
| **Trigger** | What starts a workflow: a time (cron), an event (webhook), a check-in (heartbeat), or you asking (on-demand). |

## Autonomy & Safety

| Term | What It Means |
|------|--------------|
| **Approval gate** | A point where the agent stops and asks you before continuing. For high-stakes actions. |
| **Blast radius** | What happens if something goes wrong. Low blast = try again. High blast = needs your approval first. |
| **Autonomy level** | How independent your agent is. Ranges from "ask me everything" to "just get it done." |
| **allowFrom** | The list of phone numbers allowed to talk to your agent. Security measure. |

## Expert Systems

| Term | What It Means |
|------|--------------|
| **Expert system** | A comprehensive knowledge package for one domain. Includes workflows, tool configs, patterns, and learning history. |
| **expertise.md** | The "mental model" — everything your expert knows about a domain. Gets smarter over time. |
| **Self-improve** | After each run, the expert analyzes what worked and updates its own knowledge. |
| **Plan-Build-Improve** | The cycle for adding new capabilities: plan the change, build it, learn from the result. |

## Infrastructure

| Term | What It Means |
|------|--------------|
| **VPS** | Virtual Private Server — a cloud computer that runs 24/7. Common choice for running OpenClaw. |
| **SSH** | Secure Shell — how we connect to your server to install and manage things. |
| **API** | Application Programming Interface — how your agent talks to other tools (Gmail, Notion, YouTube, etc.). |
| **API key** | A password that lets your agent access a tool's API. Stored securely, never shared. |
| **MCP server** | Model Context Protocol — a way for AI tools to connect to services. Some tools have ready-made MCP servers. |
| **Model** | The AI brain powering your agent. Options range from fast/cheap (Haiku) to powerful/expensive (Opus). |

## Models (Quick Reference)

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **Haiku** | Fast | $ | Simple tasks (file moves, data extraction) |
| **Sonnet** | Balanced | $$ | Most tasks (writing, research, scheduling) |
| **Opus** | Thorough | $$$ | Complex judgment (strategy, quality review) |

---

*Don't worry about remembering all of this. Your agent will know these terms — and so will the expert systems we build for you.*
