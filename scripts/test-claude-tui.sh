#!/bin/zsh
export PATH="/Users/greg/.bun/bin:/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export ANTHROPIC_API_KEY=$(python3 -c "import json; c=json.load(open('/Users/greg/.openclaw/openclaw.json')); print(c['env']['ANTHROPIC_API_KEY'])")

# Kill any existing test session
/opt/homebrew/bin/tmux -L test kill-server 2>/dev/null

# Start a tmux server and launch claude interactively
/opt/homebrew/bin/tmux -L test new-session -d -s claude-test -x 120 -y 40
/opt/homebrew/bin/tmux -L test send-keys -t claude-test "cd ~/overstory-hello-world && claude" Enter

# Wait for TUI to render
sleep 15

# Capture what's on screen
echo "=== PANE CONTENT ==="
/opt/homebrew/bin/tmux -L test capture-pane -t claude-test -p 2>&1

# Also dump as hex to catch unicode chars
echo "=== HEX DUMP OF PANE ==="
/opt/homebrew/bin/tmux -L test capture-pane -t claude-test -p 2>&1 | head -30 | xxd | head -40
