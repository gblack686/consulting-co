# TAC Command Index — consulting-co/.claude/commands/

Auto-generated pattern catalog. Forge scans this before creating any command/workflow.

## Command Groups

| Group | Path | Purpose |
|-------|------|---------|
| adw | adw/ | Autonomous software delivery workflow |
| agp | agp/ | Agent governance protocol |
| bowser | bowser/ | Browser automation commands |
| check-subscriptions | check-subscriptions.md | Subscription status check |
| codebase-knowledge-extract | codebase-knowledge-extract/ | Extract knowledge from codebases |
| consulting | consulting/ | Client workflow commands |
| ecosystem | ecosystem/ | Multi-agent ecosystem management |
| experts | experts/ | Expert system commands |
| github-scrape | github-scrape.md | GitHub data scraping |
| github-scrape-week | github-scrape-week.md | Weekly GitHub scraping |

## Command File Pattern

Each command follows the TAC command structure:

```markdown
# Command Name

Brief description of what this command does.

## Usage
How to invoke this command.

## Steps
1. Step one
2. Step two
3. Step three

## Output
What this command produces.

## Validation
How to verify the output is correct.
```

## PRP Methodology (Plan-Implement-Validate)

Every domain should have these three command files:
- `question.md` — Plan the approach
- `plan.md` — Execute the plan
- `self-improve.md` — Validate and improve

## Key Patterns

- **Question first**: Always plan before executing
- **Self-improve loop**: Every command validates its own output
- **Evidence-based**: Commands reference actual files and patterns
- **Repeatable**: Commands produce consistent output given consistent input
