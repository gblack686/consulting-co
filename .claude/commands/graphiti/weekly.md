---
description: Generate a weekly Obsidian summary for the past 7 days
---

Generate a weekly summary by querying Neo4j/Graphiti for the past 7 days of activity.

Run a custom query to gather:

1. **Total Conversations**: Count of all episodes in the past week
2. **Total Entities**: Count of entities created in the past week
3. **Most Active Days**: Which days had the most conversations
4. **Top Concepts**: Most connected entities across the week
5. **Weekly Trends**: Knowledge density trend over the 7 days
6. **Project Activity**: Breakdown by project name

Create a beautiful markdown summary saved to:
`~/obsidian-vault/weekly-notes/[week-of-YYYY-MM-DD]-claude-activity.md`

Include:
- Week-over-week comparison (if previous week data exists)
- Highlighted insights and patterns
- Recommendations for next week
