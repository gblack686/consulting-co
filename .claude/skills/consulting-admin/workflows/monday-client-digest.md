# Monday Client Digest

Weekly digest of all active consulting clients. Runs every Monday at 8am PT.

## Clients

1. **Greg Trading** (greg-trading) — Algorithmic trading, agent: Sebastian, channel: Telegram
2. **Erica Creations** (erica-creations) — Pottery/workshops/e-commerce, agent: Luna, channel: WhatsApp
3. **Fish Group** (michael-fisch) — Accounting consulting, agent: Finn, channel: Claude Code CLI

## Workflow

1. Read each client session folder in `.claude/skills/consulting-intake/client-sessions/` for latest state
2. Check git log for recent commits touching each client's files (last 7 days)
3. Summarize per client:
   - Last activity date
   - Open deliverables or blockers
   - Next scheduled session/follow-up
   - Deployment status (if known from session files)
4. Compile into a single digest markdown file
5. Save to `.claude/context/clients/weekly-digest-{YYYY-MM-DD}.md`

## Output Format

```markdown
# Client Digest — Week of {date}

## Greg Trading (Sebastian)
- **Status**: [Active/Paused/Blocked]
- **Last Activity**: {date} — {description}
- **Open Items**: {list}
- **Next**: {next action or follow-up}

## Erica Creations (Luna)
- **Status**: [Active/Paused/Blocked]
- **Last Activity**: {date} — {description}
- **Open Items**: {list}
- **Next**: {next action or follow-up}

## Fish Group (Finn)
- **Status**: [Active/Paused/Blocked]
- **Last Activity**: {date} — {description}
- **Open Items**: {list}
- **Next**: {next action or follow-up}

## This Week's Priority
1. {highest priority item across all clients}
2. {second priority}
3. {third priority}
```
