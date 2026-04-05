## Quick Links
- **Booking link (60-min AI Agent Build with Greg)**: https://calendar.app.google/esY5F8R6YUckRGWB9

## Always save file generated .md files in .claude/context/{group}/*.md unless told otherwise

## Obsidian Directory - C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation

## Always use a template when creating new files in obsidian. Look for other files in the folder for template types. Templates can be found in desktop/obsidian/gbautomation/obsidian-docs/Template-Library-Index.md 

## Choose random ports rather than 3000. Random ports in range 3025-3099

## Linear-Coding-Agent-Harness (GBAutomation Marketplace)

### Location
`C:\Users\gblac\OneDrive\Desktop\gbautomation-marketplace-linear`

### Critical Fix: OAuth Token Issue
The Claude CLI uses its own stored credentials by default. Setting `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` in `.env` will OVERRIDE the CLI's valid internal auth with potentially expired tokens, causing "Invalid API key" errors.

**Solution**: Comment out both OAuth-related env vars in `.env`:
```
# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...  # Commented out
# ANTHROPIC_API_KEY=sk-ant-oat01-...        # Commented out
```

### How to Start the Agent
```bash
cd "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear"
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations"
```

For unlimited iterations (full project completion):
```bash
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations"
```

For testing with limited iterations:
```bash
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations" --max-iterations 5
```

### Linear Project
- Project: GBAutomation Marketplace Ecosystem
- URL: https://linear.app/ai-agent-mastery-gb/project/gbautomation-marketplace-ecosystem-e489c8c8b733
- Total Issues: 116 (AI-5 through AI-120)
- META Issue: AI-120 (tracks overall progress)

---

## Scheduling Automation (Windows)

### Claude Desktop / Cowork Scheduler — NOT suitable for this
- Cowork scheduled tasks: **macOS only**, cadences are hourly/daily/weekly/on weekdays (no custom intervals)
- Released Feb 25, 2026. Requires Desktop app open + computer awake.
- Docs: https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork

### Windows Task Scheduler — use this instead
For recurring Python scripts (e.g. consulting-admin scan every 30 min, 9am–5pm ET):

```powershell
$action = New-ScheduledTaskAction -Execute "C:\path\to\run_scan.bat"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Hours 8) -At 9am -Daily
Register-ScheduledTask -TaskName "GBAutomation-Client-Scan" -Action $action -Trigger $trigger
```

Or via taskschd.msc: Triggers → Daily at 9am → Repeat every 30 min for 8 hours.

### consulting-admin email_watcher — general inbox watcher
- State file: `consulting-admin/state/email_watcher.json` (seen Gmail message IDs)
- Classifies ALL new inbox emails with Claude: client_update / prospect / vendor / admin / spam / other
- Action handlers registered in `HANDLERS` dict in `email_watcher.py` (easy to extend)
- client_update + prospect → Telegram notify + Gmail draft reply
- vendor/admin/spam → mark seen, no action
- Telegram secret: `gbautomation/telegram/bot` → `{bot_token, chat_id}` in Secrets Manager
- Run: `python -m scripts.email_watcher` (dry run: `--dry-run`)
- Bat wrapper: `consulting-admin/watch_email.bat` → logs to `logs/email_watcher.log`
- Schedule via Task Scheduler: every 30 min, 9am–5pm, weekdays

