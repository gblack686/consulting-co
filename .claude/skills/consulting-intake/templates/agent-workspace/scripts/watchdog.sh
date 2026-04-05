#!/bin/bash
# OpenClaw Watchdog — detects stuck gateway and auto-recovers
# Install: launchd plist runs this every 5 minutes
# Checks: health endpoint, log staleness, stuck browser, model timeout
# Alerts: Telegram notification on recovery actions

export PATH="/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:$PATH"

HEALTH_URL="http://localhost:18789/health"
LOG_FILE="$HOME/.openclaw/logs/gateway.log"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$(grep TELEGRAM_BOT_TOKEN ~/.openclaw/openclaw.json 2>/dev/null | head -1 | sed 's/.*: *"\(.*\)".*/\1/')}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-6777263736}"
STALE_MINUTES=15
WATCHDOG_LOG="$HOME/.openclaw/logs/watchdog.log"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" >> "$WATCHDOG_LOG"; }
alert() {
  local msg="🔧 Watchdog: $1"
  log "ALERT: $1"
  if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${msg}" > /dev/null 2>&1
  fi
}

# --- Check 1: Gateway health endpoint ---
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$HEALTH_URL" 2>/dev/null)
if [ "$HEALTH" != "200" ]; then
  log "FAIL: health endpoint returned $HEALTH"
  alert "Gateway health check failed (HTTP $HEALTH). Restarting..."
  openclaw gateway restart 2>&1 >> "$WATCHDOG_LOG"
  sleep 5
  RETRY=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$HEALTH_URL" 2>/dev/null)
  if [ "$RETRY" = "200" ]; then
    alert "Gateway recovered after restart."
  else
    alert "Gateway still unhealthy after restart (HTTP $RETRY). Manual intervention needed."
  fi
  exit 0
fi

# --- Check 2: Log staleness (no activity for STALE_MINUTES) ---
if [ -f "$LOG_FILE" ]; then
  LAST_MOD=$(stat -f %m "$LOG_FILE" 2>/dev/null || stat -c %Y "$LOG_FILE" 2>/dev/null)
  NOW=$(date +%s)
  DIFF=$(( (NOW - LAST_MOD) / 60 ))
  if [ "$DIFF" -gt "$STALE_MINUTES" ]; then
    log "WARN: gateway log stale for ${DIFF}m (threshold: ${STALE_MINUTES}m)"
    # Don't auto-restart for staleness alone — could just be idle
    # But alert so Greg knows
    alert "Gateway log idle for ${DIFF} minutes. Sebastian may be stuck or just quiet."
  fi
fi

# --- Check 3: Stuck browser processes (high CPU for >10 min) ---
CHROME_PIDS=$(pgrep -f "openclaw/browser" 2>/dev/null)
if [ -n "$CHROME_PIDS" ]; then
  for PID in $CHROME_PIDS; do
    CPU=$(ps -p "$PID" -o %cpu= 2>/dev/null | tr -d ' ')
    if [ -n "$CPU" ]; then
      CPU_INT=${CPU%.*}
      if [ "${CPU_INT:-0}" -gt 50 ]; then
        log "WARN: browser PID $PID at ${CPU}% CPU"
        # Check if it's been running long
        ELAPSED=$(ps -p "$PID" -o etime= 2>/dev/null | tr -d ' ')
        alert "Browser PID $PID stuck at ${CPU}% CPU (uptime: $ELAPSED). Killing..."
        kill "$PID" 2>/dev/null
        sleep 2
        kill -9 "$PID" 2>/dev/null 2>&1
      fi
    fi
  done
fi

# --- Check 4: Z.AI model timeout (session file not updated) ---
ACTIVE_SESSION=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | head -1)
if [ -n "$ACTIVE_SESSION" ]; then
  SESS_MOD=$(stat -f %m "$ACTIVE_SESSION" 2>/dev/null || stat -c %Y "$ACTIVE_SESSION" 2>/dev/null)
  LOCK_FILE="${ACTIVE_SESSION}.lock"
  if [ -f "$LOCK_FILE" ]; then
    LOCK_MOD=$(stat -f %m "$LOCK_FILE" 2>/dev/null || stat -c %Y "$LOCK_FILE" 2>/dev/null)
    NOW=$(date +%s)
    LOCK_AGE=$(( (NOW - LOCK_MOD) / 60 ))
    if [ "$LOCK_AGE" -gt 10 ]; then
      log "WARN: session lock file stale for ${LOCK_AGE}m — possible model timeout"
      alert "Session lock stale for ${LOCK_AGE}m. Model call may be hanging. Consider: openclaw gateway restart"
    fi
  fi
fi

log "OK: all checks passed"
