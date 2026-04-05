#!/bin/zsh
export PATH="/Users/greg/.bun/bin:/usr/local/bin:/opt/homebrew/bin:/Users/greg/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Load API key from OpenClaw config
export ANTHROPIC_API_KEY=$(python3 -c "import json; c=json.load(open('/Users/greg/.openclaw/openclaw.json')); print(c['env']['ANTHROPIC_API_KEY'])")

# Fresh tmux server
/opt/homebrew/bin/tmux -L overstory kill-server 2>/dev/null
/opt/homebrew/bin/tmux -L overstory new-session -d -s ov-server

cd ~/overstory-hello-world

# Clean stale agent registrations
rm -rf .overstory/agents/hello-builder .overstory/agents/hw-agent-1 .overstory/agents/hw-build .overstory/agents/hw2 .overstory/agents/hw3 2>/dev/null

# Sling the hello world builder
ov sling overstory-hello-world-d8bc --capability builder --name hw-final 2>&1
