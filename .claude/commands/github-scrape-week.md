Run the GitHub watchlist scraper for the past 7 days to generate a weekly activity report for all configured organizations and users. The report will be saved to the Obsidian vault at `github-watchlist/YYYY-MM-DD-github-activity.md`.

Execute:
```bash
python .claude/obsidian/github_watchlist.py --days 7
```

After the scraper completes, provide a summary of:
- Total repositories with activity over the past 7 days
- Total commits found
- Path to the generated report
