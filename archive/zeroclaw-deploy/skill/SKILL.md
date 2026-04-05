---
name: zeroclaw-deploy
description: "Deploy and manage ZeroClaw instances for consulting clients via AWS CDK. Handles full lifecycle: deploy, configure, monitor, troubleshoot, destroy. Use when deploying a new client instance, checking instance health, deploying skills, viewing logs, or running remote commands on ZeroClaw."
---

# ZeroClaw Deploy & Manage

## Overview

One-command CDK deployment of ZeroClaw (Rust AI agent gateway) instances for consulting clients. Each client gets an EC2 instance running ZeroClaw daemon + customer gateway proxy, with a **built-in web dashboard** and WebSocket API.

## When to Use This Skill

- "Deploy ZeroClaw for a new client"
- "Check ZeroClaw status" / "Is the instance healthy?"
- "Deploy a skill to ZeroClaw"
- "View ZeroClaw logs"
- "Restart ZeroClaw services"
- "Run a command on the ZeroClaw instance"
- "Destroy a client's ZeroClaw stack"
- "What's the gateway token?"
- "Run an E2E test on ZeroClaw"

## Architecture

```
Client Browser
    ↕ http://<ip>:18789/?token=xxx (Built-in Dashboard)
    ↕ WebSocket ws://<ip>:3050?token=xxx (Custom frontend via proxy)
Customer Gateway Proxy (Node.js, port 3050)
    ↕ WebSocket ws://127.0.0.1:18789/ws/chat?token=xxx&session_id=yyy
ZeroClaw Gateway (Rust binary, port 18789, <5MB RAM, serves dashboard + WS)
    ↕ HTTPS to OpenRouter API
LLM (DeepSeek/Gemini/Claude via OpenRouter)
```

## Current Instance

| Field | Value |
|-------|-------|
| Instance ID | `i-0487dd1848f73cb3e` |
| Public IP | `13.223.130.153` |
| Client | `greg-trading` |
| Stack | `ZeroClaw-greg-trading` |
| Gateway Token | `0cd8108d-e545-4924-9c24-80baf84a5726` |
| **Dashboard** | `http://13.223.130.153:18789/?token=0cd8108d-e545-4924-9c24-80baf84a5726` |
| Health URL | `http://13.223.130.153:3050/health` |
| WebSocket (proxy) | `ws://13.223.130.153:3050?token=0cd8108d-e545-4924-9c24-80baf84a5726` |
| WebSocket (direct) | `ws://13.223.130.153:18789/ws/chat?token=0cd8108d-e545-4924-9c24-80baf84a5726` |
| Model | `deepseek/deepseek-chat` (cheap tier) |
| S3 Bucket | `zeroclaw-bundle-greg-trading-274487662938` |
| SSM Command | `aws ssm start-session --target i-0487dd1848f73cb3e` |

## Commands

All commands use the justfile at `zeroclaw-deploy/justfile`.

### Deploy a New Client

```bash
# Fetches OpenRouter key from Secrets Manager automatically
just -f zeroclaw-deploy/justfile deploy client=<name> tier=cheap

# Model tiers:
#   cheap = deepseek/deepseek-chat ($0.27/M input)
#   mid   = google/gemini-2.0-flash-001
#   pro   = google/gemini-2.5-pro-preview
```

CDK context params:
- `client` — Client project name (kebab-case, e.g., "jane-content")
- `openrouterKey` — Fetched from `gbautomation/core/openrouter-api-key` in Secrets Manager
- `gatewayToken` — Auto-generated UUID if not provided
- `modelTier` — `cheap` | `mid` | `pro` (default: `cheap`)

### Monitor & Operate

```bash
# Quick health check (no auth needed)
just -f zeroclaw-deploy/justfile health

# Full status (services, doctor, skills, disk, memory)
just -f zeroclaw-deploy/justfile status

# ZeroClaw doctor
just -f zeroclaw-deploy/justfile doctor

# View ZeroClaw daemon logs
just -f zeroclaw-deploy/justfile logs

# View proxy logs
just -f zeroclaw-deploy/justfile proxy-logs

# View bootstrap log (right after deploy)
just -f zeroclaw-deploy/justfile setup-log

# SSM interactive shell
just -f zeroclaw-deploy/justfile ssh

# Restart services
just -f zeroclaw-deploy/justfile restart

# Run arbitrary command
just -f zeroclaw-deploy/justfile run cmd="zeroclaw skills list"
```

### Skill Deployment

```bash
# Deploy a skill from zeroclaw-deploy/skills/
just -f zeroclaw-deploy/justfile deploy-skill skill=customer-planning

# List deployed skills
just -f zeroclaw-deploy/justfile skills
```

To add a new skill:
1. Create `zeroclaw-deploy/skills/<skill-name>/SKILL.md`
2. Run `just -f zeroclaw-deploy/justfile deploy-skill skill=<skill-name>`
3. Run `just -f zeroclaw-deploy/justfile restart`

### Testing

```bash
# E2E WebSocket test (sends message, validates response)
just -f zeroclaw-deploy/justfile e2e
```

### Stack Management

```bash
# Show CloudFormation outputs
just -f zeroclaw-deploy/justfile outputs

# List all ZeroClaw stacks
just -f zeroclaw-deploy/justfile stacks

# Dry run (synth only)
just -f zeroclaw-deploy/justfile synth client=test-client

# Destroy a stack
just -f zeroclaw-deploy/justfile destroy client=greg-trading
```

## CDK Stack Resources

| Resource | Purpose |
|----------|---------|
| EC2 Instance (t3.medium) | Runs ZeroClaw daemon + proxy |
| Elastic IP | Static IP for client access |
| Security Group | Ports 22, 3050, 18789 |
| IAM Role | S3 read + SSM managed instance |
| S3 Bucket | Config bundle (config.toml, workspace, skills, proxy) |
| BucketDeployment | Lambda uploads bundle to S3 |

## Configuration

### ZeroClaw Config (config.toml)

Template: `zeroclaw-deploy/config/config.toml.tmpl`

Key sections:
- Top-level: `default_provider`, `default_model`, `api_key`, `api_url`
- `[gateway]`: port 18789, `paired_tokens` array
- `[agent]`: max iterations, history, compaction
- `[browser]`: agent_browser backend, headless
- `[autonomy]`: full level, allowed commands (**all fields required**)
- `[web_fetch]`, `[web_search]`: enabled

### Critical Gotcha

The `[autonomy]` section in config.toml requires **ALL** fields when any field is set. Missing a single field causes ZeroClaw to crash on startup with `missing field <name>`. Always include every field from the schema.

### Environment Variables

ZeroClaw needs these env vars in the systemd service (not just config.toml):
- `OPENROUTER_API_KEY` — Required for runtime LLM calls
- `ZEROCLAW_API_KEY` — Alias (both set for compatibility)
- `HOME=/home/ubuntu`

### Proxy (server.js)

Location: `zeroclaw-deploy/proxy/server.js`
- WebSocket endpoint: `ws://127.0.0.1:18789/ws/chat` (NOT root `/`)
- Auth: token-based via query param `?token=xxx`
- Rate limit: 30 messages per 60 seconds per customer
- Cost tracking: estimated from response length (chars/4), DeepSeek pricing

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Health check fails | `just restart` — services may need restart |
| OpenRouter 400 | Don't use `openrouter/` prefix in model IDs |
| API key not set | Check systemd env: `just run cmd="systemctl show zeroclaw -p Environment"` |
| Config crash on start | `[autonomy]` missing fields — check `zeroclaw config schema` |
| Skills not found | Skills in wrong path — must be `/home/ubuntu/.zeroclaw/workspace/skills/` |
| Proxy wrong WS path | Must be `/ws/chat` — check `ZEROCLAW_WS_URL` env var |
| SSM returns root paths | Use `sudo -u ubuntu HOME=/home/ubuntu` prefix |

## Cost

| Component | Monthly |
|-----------|---------|
| EC2 t3.medium | ~$30 |
| EBS 20GB GP3 | ~$1.60 |
| Elastic IP | Free (attached) |
| S3 | Negligible |
| **Total** | **~$32/month per client** |
| + LLM costs | Variable (DeepSeek cheap tier ~$0.27/M input) |

## File Structure

```
zeroclaw-deploy/
├── justfile                    ← Operations commands
├── package.json                ← CDK dependencies
├── tsconfig.json
├── cdk.json
├── bin/
│   └── zeroclaw-deploy.ts      ← CDK app entry
├── lib/
│   └── zeroclaw-stack.ts       ← Main CDK stack
├── config/
│   └── config.toml.tmpl        ← ZeroClaw config template
├── workspace/                  ← Default workspace files
│   ├── SOUL.md, USER.md, IDENTITY.md
│   ├── MEMORY.md, AGENTS.md, TOOLS.md
│   └── HEARTBEAT.md
├── skills/                     ← Consulting skills
│   ├── customer-planning/SKILL.md
│   ├── customer-qa/SKILL.md
│   └── scope-generator/SKILL.md
└── proxy/
    ├── server.js               ← Customer gateway proxy
    └── package.json
```

## Expert Knowledge

For deeper ZeroClaw expertise (config schema, WS protocol details, full troubleshooting):
- Expertise YAML: `.claude/commands/experts/openclaw/expertise.yaml`
- Expert commands: `/experts:openclaw:status`, `/experts:openclaw:question`, etc.
