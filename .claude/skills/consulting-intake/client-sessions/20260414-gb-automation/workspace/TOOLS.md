# TOOLS.md - GB Automation

## Primary Stack

### AI & Automation
| Tool | Purpose | API Status | Integration |
|------|---------|------------|-------------|
| Claude Code | Development, automation | Active | Primary |
| OpenClaw | Agent orchestration | Active | Primary |
| OpenRouter | LLM routing | Active | Configured |

### Communication
| Tool | Purpose | API Status | Integration |
|------|---------|------------|-------------|
| Slack | Internal comms, notifications | Active | Webhooks |
| LinkedIn | Outreach, content, networking | Manual | Browser automation |
| Email (Gmail) | Formal communications | Active | API |

### Content & Design
| Tool | Purpose | API Status | Integration |
|------|---------|------------|-------------|
| Obsidian | Knowledge base, notes | Local | File system |
| Canva | Graphics, thumbnails | Manual | Export |
| ComfyUI | AI image generation | Active | API |

### Business Operations
| Tool | Purpose | API Status | Integration |
|------|---------|------------|-------------|
| Linear | Project management | Active | API |
| GitHub | Code, version control | Active | CLI (gh) |
| Stripe | Payments | TBD | API |

### Research
| Tool | Purpose | API Status | Integration |
|------|---------|------------|-------------|
| Browser (Playwright) | Web research, automation | Active | Agent |
| YouTube | Tutorial research | Active | Transcript agent |

## API Keys Required

| Service | Env Var | Status |
|---------|---------|--------|
| OpenRouter | `OPENROUTER_API_KEY` | Required |
| Slack | `SLACK_BOT_TOKEN` | Required |
| Linear | `LINEAR_API_KEY` | Configured |
| GitHub | `GH_TOKEN` | Configured |

## Model Configuration

| Role | Model | Provider |
|------|-------|----------|
| Brain (complex reasoning) | claude-opus-4-5 | Anthropic |
| Muscle (fast tasks) | claude-sonnet-4-5 | Anthropic |
| Cheap (high volume) | claude-haiku-4-5 | Anthropic |

## Budget

| Category | Monthly Budget |
|----------|---------------|
| AI API costs | $200 |
| Tools & subscriptions | $100 |
| Ads (when active) | $500 |
| Total | $800 |
