---
name: onboarding
description: "Infrastructure: Onboarding - Harden OpenClaw config, validate API keys, set up Pi extensions, configure spending caps, and run health checks"
metadata: {"openclaw": {"requires": {"env": []}}}
---

# Onboarding

## Purpose

Harden a deployed OpenClaw instance by applying production config, validating every API key, setting up Pi extensions, configuring spending caps, and running health checks. Safe to run multiple times — every step checks before changing.

## Variables

- `AGENT_NAME`: {agent_name}
- `TELEGRAM_CHAT_ID`: {telegram_chat_id}
- `CHANNELS`: {channel_list}
- `MODEL_TIER`: {model_tier}

## Instructions

- IMPORTANT: Back up config before ANY change: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%s)`
- IMPORTANT: Check before setting — use `openclaw config get <key>` first. Skip if already correct.
- IMPORTANT: Never store secrets in this file or any workspace markdown. Use `openclaw config set env.KEY 'value'` only.
- IMPORTANT: Batch all config changes, then restart gateway ONCE at the end.
- IMPORTANT: If `openclaw config set` fails for deeply nested keys, fall back to Python JSON patch (see Phase 1 fallback).
- Delivery: Report written to `~/.openclaw/workspace/ONBOARDING_REPORT.md` + test message via Telegram if configured.

## Relevant Files

- `~/.openclaw/openclaw.json` — the config file being hardened
- `~/.openclaw/workspace/IDENTITY.md` — agent identity reference
- `~/.openclaw/workspace/SOUL.md` — agent persona definition
- `~/.openclaw/workspace/ONBOARDING_REPORT.md` — output report (created/overwritten by this skill)

## Workflow

### Phase 1: Config Hardening

Back up config first:

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%s)
```

For each setting below, run `openclaw config get <key>` to check current value. If it differs from the target, run `openclaw config set <key> <value>`. Log each as `CHANGED` or `ALREADY_SET`.

#### Context Pruning (prevents context window overflow)

```bash
openclaw config set agents.defaults.contextPruning.mode 'cache-ttl'
openclaw config set agents.defaults.contextPruning.ttl '1h'
openclaw config set agents.defaults.contextPruning.keepLastAssistants 3
openclaw config set agents.defaults.contextPruning.softTrimRatio 0.3
openclaw config set agents.defaults.contextPruning.minPrunableToolChars 50000
```

#### Compaction (memory flush safeguard)

```bash
openclaw config set agents.defaults.compaction.mode 'safeguard'
openclaw config set agents.defaults.compaction.memoryFlush.enabled true
openclaw config set agents.defaults.compaction.memoryFlush.softThresholdTokens 6000
```

#### Logging (redact secrets from tool output logs)

```bash
openclaw config set logging.redactSensitive 'tools'
```

#### Loop Detection (circuit breaker for runaway agents)

```bash
openclaw config set tools.loopDetection.enabled true
openclaw config set tools.loopDetection.historySize 30
openclaw config set tools.loopDetection.warningThreshold 10
openclaw config set tools.loopDetection.criticalThreshold 20
openclaw config set tools.loopDetection.globalCircuitBreakerThreshold 30
```

#### Session Maintenance (auto-prune old sessions)

```bash
openclaw config set session.maintenance.mode 'enforce'
openclaw config set session.maintenance.pruneAfter '30d'
openclaw config set session.maintenance.maxEntries 500
openclaw config set session.reset.mode '{session_reset_mode}'
openclaw config set session.reset.atHour {session_reset_hour}
```

#### Gateway (dashboard + reload)

```bash
openclaw config set gateway.controlUi.allowInsecureAuth true
openclaw config set gateway.reload.mode 'hybrid'
openclaw config set gateway.reload.debounceMs 300
```

#### Security: Restrict Elevated Exec (CRITICAL)

The wildcard `*` in `tools.elevated.allowFrom.telegram` allows ANY Telegram user to run bash commands. Restrict to owner only:

```bash
# Check current value
openclaw config get tools.elevated.allowFrom.telegram
# If it shows ["*"], restrict it:
openclaw config set tools.elevated.allowFrom.telegram '["{telegram_chat_id}"]'
```

#### Damage Control Plugin

```bash
openclaw config set plugins.entries.damage-control.enabled true
```

#### Fallback: Python JSON Patch

If `openclaw config set` fails for deeply nested keys (returns error or doesn't update), use this fallback:

```python
import json, shutil, time
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
shutil.copy(config_path, f"{config_path}.bak.{int(time.time())}")
with open(config_path) as f:
    config = json.load(f)

# Example: set a nested key
config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("contextPruning", {})["mode"] = "cache-ttl"

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
```

### Phase 2: API Key Validation

For each configured provider, verify the key works by hitting its API. Use the agent's runtime env vars (injected by OpenClaw), not `openclaw config get` (which redacts values).

```bash
#!/bin/bash
echo "=== API Key Validation ==="

# OpenRouter
if [ -n "$OPENROUTER_API_KEY" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    https://openrouter.ai/api/v1/models)
  echo "OpenRouter: HTTP $STATUS"
else
  echo "OpenRouter: MISSING"
fi

# Anthropic
if [ -n "$ANTHROPIC_API_KEY" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    https://api.anthropic.com/v1/models)
  echo "Anthropic: HTTP $STATUS"
else
  echo "Anthropic: MISSING"
fi

# OpenAI
if [ -n "$OPENAI_API_KEY" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    https://api.openai.com/v1/models)
  echo "OpenAI: HTTP $STATUS"
else
  echo "OpenAI: MISSING"
fi

# GitHub
if [ -n "$GITHUB_TOKEN" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    https://api.github.com/user)
  echo "GitHub: HTTP $STATUS"
else
  echo "GitHub: MISSING"
fi

# Supabase
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_KEY" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "apikey: $SUPABASE_KEY" \
    "$SUPABASE_URL/rest/v1/")
  echo "Supabase: HTTP $STATUS"
else
  echo "Supabase: MISSING"
fi

# Telegram Bot
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
  echo "Telegram Bot: HTTP $STATUS"
else
  echo "Telegram Bot: MISSING"
fi

# Discord Bot
if [ -n "$DISCORD_BOT_TOKEN" ]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
    https://discord.com/api/v10/users/@me)
  echo "Discord Bot: HTTP $STATUS"
else
  echo "Discord Bot: MISSING"
fi
```

Record each result as `OK` (2xx), `FAILED` (non-2xx), or `MISSING` (env var not set).

### Phase 3: Pi Extensions

Check if the Pi extensions core stack is configured:

```bash
# Check extensions directory
ls ~/.openclaw/workspace/extensions/ 2>/dev/null || echo "MISSING: extensions directory"

# Check for core stack files
for ext in minimal.ts theme-cycler.ts cross-agent.ts pi-pi.ts; do
  if [ -f ~/.openclaw/workspace/extensions/$ext ]; then
    echo "$ext: PRESENT"
  else
    echo "$ext: MISSING"
  fi
done

# Check config
openclaw config get extensions.core 2>/dev/null || echo "extensions.core: NOT_SET"
```

If extensions directory or files are missing, log as `MANUAL_ACTION` — the consulting-intake deploy step copies these. Do NOT attempt to download or create extension files.

If `extensions.core` config is not set:

```bash
openclaw config set extensions.core '["minimal", "theme-cycler", "cross-agent", "pi-pi"]'
openclaw config set extensions.dir './extensions'
```

### Phase 4: Spending Caps (Advisory)

These require browser login — cannot be automated. Generate reminders based on which keys exist:

- **OpenRouter**: If `OPENROUTER_API_KEY` is set → remind to set monthly limit at `https://openrouter.ai/settings/limits`
  - Suggested cap: `$5/mo` (CHEAP tier), `$20/mo` (MID tier), `$50/mo` (PRO tier)
- **Anthropic**: If `ANTHROPIC_API_KEY` is set → remind to set limit at `https://console.anthropic.com/settings/limits`
- **OpenAI**: If `OPENAI_API_KEY` is set → remind to set limit at `https://platform.openai.com/settings/organization/limits`

Log each as `MANUAL_ACTION` in the report.

### Phase 5: Health Checks

Restart gateway once (after all config changes from Phase 1), then validate:

```bash
# Restart gateway to pick up config changes
openclaw gateway restart
sleep 3

# 1. Doctor check
openclaw doctor --non-interactive 2>&1

# 2. Gateway health
curl -s http://localhost:18789/health

# 3. Channels
openclaw channels list

# 4. Config validation
openclaw config validate 2>&1

# 5. Skills loaded
openclaw skills list

# 6. Test message (if Telegram configured)
openclaw message send --channel telegram --target {telegram_chat_id} \
  --message "Onboarding complete — {agent_name} is hardened and ready."
```

Record each check as `PASS` or `FAIL` with details.

### Phase 6: Generate Report

Write the full report to `~/.openclaw/workspace/ONBOARDING_REPORT.md`:

## Report

```markdown
## Onboarding Report — {agent_name}

**Date**: {timestamp UTC}
**OpenClaw Version**: {version}
**Model Tier**: {model_tier}
**Instance**: {hostname}

### Phase 1: Config Hardening

| Setting | Status | Value |
|---------|--------|-------|
| contextPruning.mode | {CHANGED/ALREADY_SET} | cache-ttl |
| contextPruning.ttl | {status} | 1h |
| contextPruning.keepLastAssistants | {status} | 3 |
| contextPruning.softTrimRatio | {status} | 0.3 |
| compaction.mode | {status} | safeguard |
| compaction.memoryFlush.enabled | {status} | true |
| logging.redactSensitive | {status} | tools |
| loopDetection.enabled | {status} | true |
| loopDetection.historySize | {status} | 30 |
| session.maintenance.mode | {status} | enforce |
| session.maintenance.pruneAfter | {status} | 30d |
| gateway.controlUi.allowInsecureAuth | {status} | true |
| gateway.reload.mode | {status} | hybrid |
| tools.elevated.allowFrom.telegram | {status} | ["{telegram_chat_id}"] |
| plugins.damage-control | {status} | enabled |

### Phase 2: API Key Validation

| Provider | Status | Details |
|----------|--------|---------|
| OpenRouter | {OK/FAILED/MISSING} | {HTTP code or note} |
| Anthropic | {OK/FAILED/MISSING} | {details} |
| OpenAI | {OK/FAILED/MISSING} | {details} |
| GitHub | {OK/FAILED/MISSING} | {details} |
| Supabase | {OK/FAILED/MISSING} | {details} |
| Telegram Bot | {OK/FAILED/MISSING} | {details} |
| Discord Bot | {OK/FAILED/MISSING} | {details} |

### Phase 3: Pi Extensions

| Component | Status |
|-----------|--------|
| extensions/ directory | {PRESENT/MISSING} |
| minimal.ts | {PRESENT/MISSING} |
| theme-cycler.ts | {PRESENT/MISSING} |
| cross-agent.ts | {PRESENT/MISSING} |
| pi-pi.ts | {PRESENT/MISSING} |
| extensions.core config | {SET/NOT_SET} |

### Phase 4: Spending Caps

- [ ] OpenRouter: Set monthly limit at https://openrouter.ai/settings/limits (suggested: ${cap}/mo)
- [ ] Anthropic: Set monthly limit at https://console.anthropic.com/settings/limits
- [ ] OpenAI: Set monthly limit at https://platform.openai.com/settings/organization/limits

### Phase 5: Health Checks

| Check | Result | Details |
|-------|--------|---------|
| openclaw doctor | {PASS/FAIL} | {score or issues} |
| Gateway /health | {PASS/FAIL} | {response} |
| Channels list | {PASS/FAIL} | {active channels} |
| Config validate | {PASS/FAIL} | {warnings} |
| Skills loaded | {PASS/FAIL} | {count} skills |
| Telegram test msg | {PASS/FAIL/SKIPPED} | {details} |

### Manual Actions Required

{List all items marked MANUAL_ACTION, MISSING, or FAIL that need human intervention}

### Next Steps

- Review spending caps and set limits in browser
- Monitor gateway.log for 24 hours: `tail -f ~/.openclaw/logs/gateway.log`
- Run `/onboarding` again after resolving any FAIL items
```
