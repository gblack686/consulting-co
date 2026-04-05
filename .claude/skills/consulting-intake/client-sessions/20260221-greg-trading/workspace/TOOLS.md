# TOOLS.md — Greg's Infrastructure
# Skills define HOW tools work. This file is for Greg's specifics.

## Device

- **Type**: Laptop
- **OS**: Windows (Lenovo)
- **Location**: Los Angeles, CA
- **Note**: OpenClaw runs locally on this machine. Keep the laptop on and connected for overnight cron jobs and heartbeat tasks.

## Primary Tools

| Tool | Purpose | API Available | Auth Method | Notes |
|------|---------|---------------|-------------|-------|
| Hyper Liquid | Primary trading platform | Yes | API key + secret | REST + WebSocket |
| Discord | Trade signal channel monitoring | Yes | Bot token | Read-only bot |
| Telegram | Agent communication (primary) | Yes | Bot token | Delivery channel |
| GitHub | Strategy code versioning | Yes | PAT token | Backtester code |
| YouTube Data API | Daily video scraping | Yes | API key | Quota limits apply |
| iMessage | Possible secondary channel | Limited | mac-only | Confirm viability |

## API Credentials

| Service | Auth Method | Env Var | Status |
|---------|-------------|---------|--------|
| Hyper Liquid | API Key + Secret | `HYPERLIQUID_API_KEY`, `HYPERLIQUID_SECRET` | Pending |
| Discord Bot | Bot Token | `DISCORD_BOT_TOKEN` | Pending |
| Telegram Bot | Bot Token | `TELEGRAM_BOT_TOKEN` | Pending |
| YouTube Data API | API Key | `YOUTUBE_API_KEY` | Pending |
| GitHub | Personal Access Token | `GITHUB_PAT` | Pending |

**Note**: Greg will provide all API keys. Confirm glm47 model provider credentials (Zhipu AI API key or other provider).

## Model Routing

| Role | Model | Use Case |
|------|-------|----------|
| Brain (primary) | glm47 | Complex reasoning, strategy analysis, critical decisions |
| Muscle (subagents) | glm47-lite | Routine tasks: scraping, formatting, simple lookups |

**⚠️ Verify**: Confirm "glm47" model identifier with Greg — may be Zhipu AI's GLM-4 or phonetic transcription of another model.

## MCP Servers

| Server | Package | Status |
|--------|---------|--------|
| Hyper Liquid MCP | TBD — check ClawHub | Pending research |
| Discord MCP | TBD | Pending research |

## Local Paths

| Purpose | Path |
|---------|------|
| Strategy code (backtesters) | TBD — confirm with Greg |
| Historical data cache | `~/.openclaw/data/market-history/` |
| Trade journal | `~/.openclaw/workspace/memory/trade-journal/` |
| Chart output | `~/.openclaw/workspace/charts/` |

## Notes

- OpenClaw runs locally on Greg's Lenovo Windows laptop — ensure machine stays on overnight for cron jobs
- Discord scraping requires a dedicated bot with read permissions on target channels — Greg to set up
- Hyper Liquid API supports paper trading mode — confirm paper trading endpoint vs. live endpoint
