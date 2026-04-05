# Worktree Manager Skill

Manage isolated git worktrees for parallel ADW execution.

## Invocation

```
/worktree-manager
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `worktree_base` | `../adw-workspaces` | Worktree storage location |
| `branch_prefix` | `adw/` | Branch naming prefix |
| `auto_cleanup` | `true` | Auto-cleanup after merge |

## Core Capabilities

| Capability | Command | Description |
|------------|---------|-------------|
| Create | `python scripts/create_worktree.py <name>` | Create isolated worktree |
| List | `python scripts/list_worktrees.py` | List active worktrees |
| Merge | `python scripts/merge_worktree.py <name>` | Merge to main |
| Cleanup | `python scripts/cleanup_worktree.py <name>` | Remove worktree |

## Quick Start

```bash
# Create a new worktree for feature work
python .claude/skills/worktree-manager/scripts/create_worktree.py user-auth

# List all active worktrees
python .claude/skills/worktree-manager/scripts/list_worktrees.py

# Merge completed work to main
python .claude/skills/worktree-manager/scripts/merge_worktree.py user-auth

# Cleanup after merge
python .claude/skills/worktree-manager/scripts/cleanup_worktree.py user-auth
```

## Branch Strategy

```
main
├── adw/feature-1  (worktree 1)
├── adw/feature-2  (worktree 2)
└── adw/bugfix-3   (worktree 3)
```

## Worktree Lifecycle

```
1. Create: git worktree add ../adw-{name} -b adw/{name}
2. Work: Claude executes in isolated worktree
3. Review: Check changes before merging
4. Merge: git checkout main && git merge adw/{name}
5. Cleanup: git worktree remove ../adw-{name}
```

## Benefits

- **Isolation**: Each ADW works in a separate branch
- **Parallel**: Multiple ADWs can run simultaneously
- **Safety**: Main branch is never directly modified
- **Review**: Changes can be reviewed before merge

## Source Files

- `scripts/create_worktree.py` - Create worktree
- `scripts/list_worktrees.py` - List worktrees
- `scripts/merge_worktree.py` - Merge to main
- `scripts/cleanup_worktree.py` - Remove worktree
- `scripts/worktree_ops.py` - Core operations
- `config/settings.json` - Configuration
