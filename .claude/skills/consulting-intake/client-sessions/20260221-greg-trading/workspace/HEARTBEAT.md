# HEARTBEAT.md — Sebastian Periodic Tasks

# Fires every 15 minutes (trading-priority tasks)
# General tasks every 30 minutes

## Every 15 Minutes — Trading Checks

- Check Hyper Liquid open positions: verify every position has a stop-loss set. Alert Greg via Telegram if any position is missing one.
- Scrape monitored Discord channels for new trade signals since last check. Parse and log any quality signals. Alert Greg for high-quality signals.
- Check volume spike conditions on configured data feeds. If volume threshold crossed: alert Greg with ticker + context.
- If it's between 00:00–06:00 PST (quiet hours), respond HEARTBEAT_OK instead of sending alerts.

## Every 30 Minutes — General

- Check if any overnight backtest jobs are queued — start them if idle.
- Review if any cron jobs failed in the last cycle — log and alert Greg if so.
- If nothing to report: respond HEARTBEAT_OK

# Quiet hours: 00:00 - 06:00 America/Los_Angeles
# During quiet hours, respond HEARTBEAT_OK — no Telegram messages to Greg
