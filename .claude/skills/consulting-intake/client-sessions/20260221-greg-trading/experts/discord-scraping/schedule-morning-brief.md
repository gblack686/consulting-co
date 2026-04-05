---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: schedule-morning-brief
tags: [expert-file, command, discord-scraping, scheduling]
---

# Schedule Morning Brief — Configure or Test Daily Brief Delivery

> Configure the morning brief schedule, content sections, or test delivery on-demand.

## Purpose

Change when the morning brief fires, modify which sections are included, or trigger a test brief to see what it looks like.

## Allowed Tools
`Read, Write, Edit, Bash`

## Workflow

### Test Morning Brief (On-Demand)
1. Run the `morning-brief` skill manually (outside of cron)
2. Collect from all 5 data sources (portfolio, market, Discord, YouTube, news)
3. Compose the full brief
4. Send via Telegram to Greg (clearly labeled as a test)
5. Report: which sections loaded successfully, which had errors

### Change Brief Schedule
1. Read current cron configuration: `openclaw cron list`
2. Identify "Morning Brief" cron job
3. **[APPROVAL GATE]** — confirm new time with Greg before changing
4. Update: `openclaw cron update --name "Morning Brief" --cron "{new_expression}" --tz "America/Los_Angeles"`
5. Verify with `openclaw cron list`

### Add/Remove Brief Sections
1. Read `morning-brief/SKILL.md` for current sections
2. Propose section change (add: on-chain data? remove: YouTube? add: earnings calendar?)
3. **[APPROVAL GATE]** — confirm changes with Greg
4. Edit SKILL.md Phase 2 (Compose Brief) to include/exclude section
5. Test with on-demand brief run

### Troubleshoot Brief Failures
| Symptom | Fix |
|---------|-----|
| Brief not sending | Check cron is enabled; check Telegram bot token |
| Portfolio section empty | Check Hyper Liquid API key; check account has positions |
| Discord section empty | Check `memory/discord-signals/{today}.json` exists |
| Brief arrives late | Check server timezone vs. cron expression; check server load |

## Output Format
```
Morning brief test: {date} {time}
Sections loaded: {count}/{total}
Failed sections: {list}
Brief length: {char_count} chars
Delivery: {success|failed}
```
