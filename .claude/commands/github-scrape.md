Run the GitHub watchlist scraper to generate a daily activity report for all configured organizations and users. The report will be saved to the Obsidian vault at `github-watchlist/YYYY-MM-DD-github-activity.md`.

Execute:
```bash
python .claude/obsidian/github_watchlist.py
```

After the scraper completes, provide a summary of:
- Total repositories with activity
- Total commits found
- Path to the generated report
