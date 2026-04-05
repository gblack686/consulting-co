# GitHub Watchlist Integration - Quick Reference

## Overview

The GitHub Watchlist integration monitors GitHub organizations and user accounts for push activity, generating automated daily reports in your Obsidian vault.

## Files Created

### Configuration & Scripts
- `.claude/obsidian/github_watchlist.py` - Main scraper script
- `.claude/obsidian/github-watchlist-config.json` - Configuration file

### Slash Commands
- `.claude/commands/github-scrape.md` - Daily scrape command
- `.claude/commands/github-scrape-week.md` - Weekly scrape command

### Obsidian Vault
- `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/github-watchlist/` - Reports directory
- `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/github-watchlist/README.md` - Documentation

## Current Configuration

**Watching**:
- Organization: `dynamous-community`
- Users: `disler`, `coleam00`

**Filters**:
- Excludes forks: ✅
- Excludes archived: ✅
- Language filter: All languages

**Report Settings**:
- Group by repository: ✅
- Include commit messages: ✅
- Max commits per repo: 10

## Usage

### Option 1: Slash Commands (Recommended)
```
/github-scrape          # Daily scrape (since last run)
/github-scrape-week     # Past 7 days
```

### Option 2: Direct Command
```bash
# Daily scrape
python .claude/obsidian/github_watchlist.py

# Custom timeframe
python .claude/obsidian/github_watchlist.py --days 7
python .claude/obsidian/github_watchlist.py --days 30
```

## Adding More Organizations/Users

Edit `.claude/obsidian/github-watchlist-config.json`:

```json
{
  "organizations": [
    "dynamous-community",
    "another-org"
  ],
  "users": [
    "disler",
    "coleam00",
    "another-user"
  ]
}
```

## Report Output

Reports are saved to:
```
C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/github-watchlist/YYYY-MM-DD-github-activity.md
```

Each report includes:
- Summary statistics
- Activity grouped by organization/user
- Repository details with commit history
- Direct links to commits and repositories

## Example Output

**Test Run (Dec 8, 2025)**:
- Repositories with activity: 3
- Total commits: 7
- Report: `2025-12-08-github-activity.md`

**Activity Found**:
- `disler/fork-repository-skill` - 1 commit
- `coleam00/Linear-Coding-Agent-Harness` - 1 commit
- `coleam00/MongoDB-RAG-Agent` - 5 commits

## Automation Options

### Windows Task Scheduler
Create a daily task to run:
```batch
python C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\obsidian\github_watchlist.py
```

### Cron (Linux/Mac)
```cron
0 9 * * * python /path/to/github_watchlist.py
```

### Manual
Run `/github-scrape` whenever you want an update

## State Tracking

The scraper maintains state in:
```
C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/github-watchlist/.state.json
```

This tracks:
- Last scrape timestamp
- Repository metadata

The state file ensures you don't get duplicate commits in reports when running daily scrapes.

## Advanced Configuration

### Filter by Programming Language
```json
"filters": {
  "languages": ["Python", "TypeScript", "Go"]
}
```

### Adjust Report Detail
```json
"notification_settings": {
  "include_commit_messages": false,  // Hide commit details
  "max_commits_per_repo": 5          // Show fewer commits
}
```

## Prerequisites

1. **GitHub CLI**: Must be installed and authenticated
   ```bash
   gh --version  # Check installation
   gh auth login # Authenticate
   ```

2. **Python 3.7+**: Required for scraper script

## Troubleshooting

**No activity found**: Check if the time range is correct or if repositories actually had pushes

**API rate limit**: Reduce scrape frequency or use GitHub authentication

**Command not found**: Ensure GitHub CLI is installed and in PATH

## Integration with Obsidian

Reports use frontmatter for easy querying:
```yaml
---
type: github-watchlist-report
date: 2025-12-08
total_repos: 3
total_commits: 7
tags:
  - github
  - watchlist
  - automation
---
```

Use Dataview queries to find reports:
```dataview
LIST
FROM "github-watchlist"
WHERE type = "github-watchlist-report"
SORT date DESC
```

## Next Steps

1. **Schedule Automation**: Set up Task Scheduler or cron for daily runs
2. **Customize Filters**: Adjust config for specific languages or repo types
3. **Add More Accounts**: Edit config to monitor additional orgs/users
4. **Integrate Notifications**: Extend script to send Slack/Discord alerts

---

*Created: 2025-12-08*
*Status: ✅ Tested and Working*
