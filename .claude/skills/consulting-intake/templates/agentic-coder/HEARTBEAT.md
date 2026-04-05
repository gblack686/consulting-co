# Agentic Coder — Heartbeat Tasks

## Periodic Checks (runs during heartbeat cycle)

Validate workspace health: check that all loaded skills parse correctly, SOUL.md has 4 sections, no hardcoded API keys in skill files

Check for stale memory: if memory/ has entries older than 30 days with no pattern extraction, trigger review-memory skill

Monitor skill count: if total loaded skills exceed 30, announce a warning about token overhead (~720 tokens/turn) and suggest consolidation

Verify cron health: run `openclaw cron list` and check for failed or stuck jobs, announce any issues found
