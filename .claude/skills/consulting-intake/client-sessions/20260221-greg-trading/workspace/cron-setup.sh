#!/bin/bash
# Cron Job Setup for Greg Trading — Sebastian
# Run these commands on the OpenClaw server to install all scheduled tasks

# 1. Morning Brief — 7:00 AM PST daily
openclaw cron add \
  --name "Morning Brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --skill "morning-brief" \
  --mode main \
  --delivery announce

# 2. Discord Signal Scrape — every 15 minutes
openclaw cron add \
  --name "Discord Signal Scrape" \
  --every "15m" \
  --skill "scrape-discord" \
  --mode isolated \
  --delivery none

# 3. Feed Monitor (volume spikes, indicator alerts) — every 15 minutes
openclaw cron add \
  --name "Feed Monitor" \
  --every "15m" \
  --skill "monitor-feeds" \
  --mode isolated \
  --delivery none

# 4. Position Monitor (stop-loss & drawdown checks) — every 15 minutes
openclaw cron add \
  --name "Position Monitor" \
  --every "15m" \
  --skill "monitor-positions" \
  --mode isolated \
  --delivery none

# 5. Nightly Backtest Run — 2:00 AM PST (low-traffic time)
openclaw cron add \
  --name "Nightly Backtest" \
  --cron "0 2 * * *" \
  --tz "America/Los_Angeles" \
  --skill "run-backtest" \
  --mode isolated \
  --delivery none

# 6. Weekly Dataset Scout — Sunday 10:00 PM PST (results ready for Monday morning brief)
openclaw cron add \
  --name "Dataset Scout Weekly" \
  --cron "0 22 * * 0" \
  --tz "America/Los_Angeles" \
  --skill "scout-datasets" \
  --mode isolated \
  --delivery none

# 7. Weekly Trade Journal Summary — Monday 7:00 AM PST (included in morning brief)
openclaw cron add \
  --name "Trade Journal Weekly" \
  --cron "0 7 * * 1" \
  --tz "America/Los_Angeles" \
  --skill "trade-journal" \
  --mode main \
  --delivery announce

echo "✅ All cron jobs installed for Sebastian (Greg Trading)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "To also install Scout (YouTube) cron jobs, run:"
echo "  just cron-youtube"
echo "  — or —"
echo "  bash agents/youtube/cron-setup-youtube.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Verify all: openclaw cron list"
