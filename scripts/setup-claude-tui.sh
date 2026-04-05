#!/bin/zsh
export PATH="/Users/greg/.bun/bin:/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export ANTHROPIC_API_KEY=$(python3 -c "import json; c=json.load(open('/Users/greg/.openclaw/openclaw.json')); print(c['env']['ANTHROPIC_API_KEY'])")

# Use the existing test session
# Send Enter to select Dark mode theme
/opt/homebrew/bin/tmux -L test send-keys -t claude-test Enter
sleep 5

# Capture what's on screen now
echo "=== AFTER THEME SELECT ==="
/opt/homebrew/bin/tmux -L test capture-pane -t claude-test -p 2>&1

# If there's another dialog, send Enter again
/opt/homebrew/bin/tmux -L test send-keys -t claude-test Enter
sleep 5

echo "=== AFTER SECOND ENTER ==="
/opt/homebrew/bin/tmux -L test capture-pane -t claude-test -p 2>&1

# Send /exit to quit claude cleanly
/opt/homebrew/bin/tmux -L test send-keys -t claude-test "/exit" Enter
sleep 3

echo "=== FINAL ==="
/opt/homebrew/bin/tmux -L test capture-pane -t claude-test -p 2>&1

# Kill test tmux
/opt/homebrew/bin/tmux -L test kill-server 2>/dev/null
echo "Done - Claude first-run setup complete"
