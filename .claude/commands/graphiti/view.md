---
description: View an existing Obsidian daily summary (defaults to today)
---

View an Obsidian daily summary file.

If the user provided a date, use that. Otherwise, show today's summary.

Read the file from:
`~/obsidian-vault/daily-notes/[YYYY-MM-DD]-claude-activity.md`

Display:
1. The full summary in a readable format
2. Highlight the key metrics
3. Show the most interesting entities discovered
4. List the most connected concepts

If the file doesn't exist, let the user know and offer to generate it using `/obsidian-daily` or `/obsidian-summary`.
