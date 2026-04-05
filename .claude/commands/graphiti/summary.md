---
description: Generate an Obsidian daily summary for a specific date (format: YYYY-MM-DD)
---

Generate a daily Obsidian summary for the date specified by the user.

If the user didn't provide a date, ask them: "What date would you like to generate a summary for? (format: YYYY-MM-DD)"

Once you have the date, run:

```bash
python .claude/scripts/generate_daily_summary.py [DATE]
```

Then display:
1. Summary statistics for that date
2. Number of conversations and entities
3. Most connected concepts
4. The file path where it was saved

Example: `/obsidian-summary 2025-11-13`
