---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: scrape-discord
tags: [expert-file, command, discord-scraping]
---

# Scrape Discord — Run or Debug the Signal Scraper

> Execute the Discord signal scraper or diagnose why it's not working.

## Purpose

Run the Discord scraper manually, test signal parsing with sample messages, add new channels to monitor, or debug scraping issues.

## Allowed Tools
`Read, Write, Edit, Bash, Glob, Grep`

## Workflow

### Run Scrape Manually
1. Read `TOOLS.md` for Discord bot token and channel IDs
2. Invoke `scrape-discord` skill in isolated mode:
   - Test by calling the skill logic directly for 1 channel
3. Review parsed signals and quality scores
4. Report: signals found, any errors

### Add a New Discord Channel to Monitor
1. Read `memory/feed-rules.json`
2. Add new channel ID to the monitored_channels array:
   ```json
   {
     "monitored_channels": [
       {"channel_id": "...", "name": "...", "active": true}
     ]
   }
   ```
3. Test: run scraper against new channel for last 20 messages
4. Confirm signals parse correctly

### Debug Scraping Issues
| Symptom | Diagnosis Steps |
|---------|----------------|
| No signals parsed | Check bot token valid; check channel access permissions; test API call manually |
| Too many false positives | Lower quality threshold; tighten signal regex patterns |
| Too few signals caught | Check if signal format changed in Discord; lower quality threshold |
| Rate limit errors | Check request frequency; add delay between channel fetches |
| Telegram alerts not sending | Check TELEGRAM_BOT_TOKEN; verify chat ID in config |

### Adjust Signal Scoring
1. Read current scoring logic in `scrape-discord/SKILL.md`
2. Propose threshold adjustment based on signal quality feedback
3. **[APPROVAL GATE]** — get Greg's OK before changing thresholds
4. Update SKILL.md with new threshold values
5. Log change in `expertise.md` Part 7

## Output Format
```
Scrape test: {channel_name}
Messages checked: {count}
Signals parsed: {count} (high-quality: {count})
Errors: {count}
```
