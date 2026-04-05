#!/bin/bash
# Observability System Quick Commands
# Save as: OBSERVABILITY_COMMANDS.sh

echo "📚 Observability System Quick Commands"
echo "======================================="
echo ""

# START OBSERVABILITY SERVER
echo "🚀 START SERVER (Required)"
echo "  $ cd observability/apps/server && npm run dev"
echo ""

# START DASHBOARD
echo "📊 START DASHBOARD (Optional)"
echo "  $ cd observability/apps/client && npm run dev"
echo "  → Visit http://localhost:5173"
echo ""

# TEST INTEGRATION
echo "✅ TEST INTEGRATION"
echo "  In Claude Code (in consulting-co project):"
echo "  $ find . -name '*.md' -type f | head -5"
echo ""
echo "  Expected: PreToolUse and PostToolUse events"
echo ""

# CHECK SERVER
echo "🔍 CHECK SERVER STATUS"
echo "  $ curl http://localhost:4000/events"
echo ""

# VIEW EVENTS
echo "📋 VIEW RECENT EVENTS (SQLite)"
echo "  $ cd observability/apps/server"
echo "  $ sqlite3 events.db \"SELECT * FROM events LIMIT 10;\""
echo ""

# QUERY LATENCIES
echo "⏱️  QUERY TOOL LATENCIES"
echo "  $ sqlite3 observability/apps/server/events.db"
echo "  > SELECT hook_event_type, json_extract(payload, '$.latency_ms') as latency"
echo "  > FROM events WHERE hook_event_type = 'PostToolUse' ORDER BY latency DESC;"
echo ""

# RESET DATABASE
echo "🔄 RESET DATABASE"
echo "  $ rm observability/apps/server/events.db"
echo "  (Database will be recreated on next event)"
echo ""

# STOP SERVICES
echo "⛔ STOP SERVICES"
echo "  Server:    Ctrl+C in server terminal"
echo "  Dashboard: Ctrl+C in client terminal"
echo ""

# VIEW HOOK LOGS
echo "🔧 DEBUG HOOKS"
echo "  Check if hooks are executable:"
echo "  $ ls -la consulting-co/.claude/hooks/*.py | grep '^-rwx'"
echo ""

# TAIL LOGS
echo "📜 VIEW HOOK OUTPUT"
echo "  Server logs:  Check terminal running 'npm run dev'"
echo "  Claude logs:  Check Claude Code UI for errors"
echo ""

echo "======================================="
echo "For more details, see:"
echo "  - OBSERVABILITY_QUICK_START.md"
echo "  - OBSERVABILITY_INTEGRATION_COMPLETE.md"
echo ""
