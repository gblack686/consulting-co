#!/bin/zsh
export PATH="/Users/greg/.bun/bin:/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export ANTHROPIC_API_KEY=$(python3 -c "import json; c=json.load(open('/Users/greg/.openclaw/openclaw.json')); print(c['env']['ANTHROPIC_API_KEY'])")

cd ~/overstory-hello-world

# List all tmux sessions on overstory socket
echo "=== TMUX SESSIONS ==="
/opt/homebrew/bin/tmux -L overstory list-sessions 2>&1

# Capture every pane
echo "=== PANE CAPTURES ==="
for s in $(/opt/homebrew/bin/tmux -L overstory list-sessions -F '#{session_name}' 2>/dev/null); do
  echo "--- session: $s ---"
  /opt/homebrew/bin/tmux -L overstory capture-pane -t "$s" -p 2>&1
done

# Check agent identity files
echo "=== AGENT FILES ==="
find .overstory/agents -type f 2>&1

# Check if there's a worktree
echo "=== WORKTREES ==="
ls -la .overstory/worktrees/ 2>&1
git worktree list 2>&1

# Check claude version
echo "=== CLAUDE VERSION ==="
claude --version 2>&1
