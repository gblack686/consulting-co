# ADW Dispatch Skill

Route ADWs (Autonomous Developer Workflows) to local Haiku or GitHub Actions Opus based on task complexity.

## Invocation

```
/adw-dispatch
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `haiku_threshold` | `5000` | Max tokens for local Haiku execution |
| `opus_threshold` | `20000` | Min tokens to trigger GitHub Actions Opus |
| `default_mode` | `auto` | `local`, `github`, or `auto` |
| `github_workflow` | `adw-plan-build-review.yml` | Workflow to trigger |
| `worktree_enabled` | `true` | Use git worktrees for isolation |

## Core Capabilities

| Capability | Command | Description |
|------------|---------|-------------|
| Auto Route | `python scripts/auto_route.py "task"` | Auto-route by complexity |
| Dispatch Local | `python scripts/dispatch_local.py "task"` | Run via local Haiku |
| Dispatch GitHub | `python scripts/dispatch_github.py "task"` | Trigger GitHub Actions |
| Estimate | `python scripts/estimate_complexity.py "task"` | Estimate token count |

## Quick Start

```bash
# Auto-route based on complexity (recommended)
python .claude/skills/adw-dispatch/scripts/auto_route.py "Add user authentication"

# Force local execution
python .claude/skills/adw-dispatch/scripts/dispatch_local.py "Fix typo in README"

# Force GitHub Actions (Opus)
python .claude/skills/adw-dispatch/scripts/dispatch_github.py "Implement new feature X"

# Check complexity estimate
python .claude/skills/adw-dispatch/scripts/estimate_complexity.py "Refactor database layer"
```

## Decision Tree

```
Task Received
    │
    ├─ Est. tokens < 5000? ──────> LOCAL HAIKU (~$0.005)
    │
    ├─ Files touched <= 2? ──────> LOCAL HAIKU
    │
    ├─ Est. tokens > 20000? ─────> GITHUB ACTIONS OPUS (free)
    │
    ├─ Is ADW? ──────────────────> GITHUB ACTIONS OPUS
    │
    └─ Default ──────────────────> LOCAL HAIKU (responsiveness)
```

## Cost Comparison

| Execution Mode | Model | Est. Cost | Use Case |
|----------------|-------|-----------|----------|
| Local Haiku | claude-haiku-4-5 | ~$0.005/task | Quick tasks, chat |
| GitHub Actions | claude-opus-4-5 | $0.00 (Max sub) | Complex ADWs |

## Source Files

- `scripts/auto_route.py` - Auto-routing logic
- `scripts/dispatch_local.py` - Local Haiku execution
- `scripts/dispatch_github.py` - GitHub Actions trigger
- `scripts/estimate_complexity.py` - Complexity estimation
- `scripts/adw_ops.py` - Core operations module
- `config/settings.json` - Configuration
