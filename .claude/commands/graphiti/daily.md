---
description: Generate today's Obsidian daily summary from Graphiti and Langfuse data
---

Generate today's daily Obsidian summary by running:

```bash
python .claude/scripts/generate_daily_summary.py
```

Then display the generated summary from:
`~/obsidian-vault/daily-notes/[today's date]-claude-activity.md`

Show me:
1. The summary statistics (conversations, entities, knowledge density)
2. Top 3 most connected concepts
3. Key entities discovered today
4. The file path where it was saved
