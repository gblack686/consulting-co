# NIH GitHub Repo Sync Configuration

## Overview

Daily automated sync from personal GitHub (gblack686) to NIH GitHub (blackga-nih) with full commit history preservation and daily summary logs.

## Accounts

| Account | Purpose | PAT Secret (AWS) |
|---------|---------|------------------|
| `gblack686` | Source (personal) | `github-pat-gblack686` |
| `blackga-nih` | Destination (NIH) | `nih-github-pat` |

## Synced Repositories

### nci-oa-agent

| Property | Value |
|----------|-------|
| Source | `gblack686/nci-oa-agent` |
| Destination | `blackga-nih/nci-oa-agent` |
| Schedule | Daily at 6 AM UTC |
| Workflow | `.github/workflows/daily-sync.yml` |
| Summary logs | `.sync-logs/YYYY-MM-DD-sync-summary.md` |

## How It Works

1. **Mirror Clone** - Full clone of source repo with all branches/tags
2. **Force Push** - Mirror pushed to destination (preserves full history)
3. **Summary Generation** - Markdown file created with:
   - Commits from last 24 hours
   - Author information
   - Branch count
4. **Summary Commit** - Log file committed to `.sync-logs/` folder

## GitHub Secrets (in blackga-nih/nci-oa-agent)

| Secret | Purpose |
|--------|---------|
| `SOURCE_PAT` | Read access to gblack686/nci-oa-agent |
| `DEST_PAT` | Write access to blackga-nih/nci-oa-agent |

## Manual Trigger

1. Go to: https://github.com/blackga-nih/nci-oa-agent/actions
2. Click "Daily Mirror + Summary"
3. Click "Run workflow" → "Run workflow"

## AWS Secrets Manager

Retrieve PATs:
```bash
# NIH GitHub PAT
aws secretsmanager get-secret-value --secret-id nih-github-pat --region us-east-1 --query SecretString --output text

# gblack686 PAT
aws secretsmanager get-secret-value --secret-id github-pat-gblack686 --region us-east-1 --query SecretString --output text
```

## Workflow File

Location: `blackga-nih/nci-oa-agent/.github/workflows/daily-sync.yml`

```yaml
name: Daily Mirror + Summary
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

permissions:
  contents: write

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Clone source (full mirror)
        run: |
          git clone --mirror https://x-access-token:${{ secrets.SOURCE_PAT }}@github.com/gblack686/nci-oa-agent.git source-mirror

      - name: Push mirror to this repo
        run: |
          cd source-mirror
          git remote add dest https://x-access-token:${{ secrets.DEST_PAT }}@github.com/${{ github.repository }}.git
          git push dest --mirror --force

      - name: Checkout for summary generation
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: main
          token: ${{ secrets.DEST_PAT }}

      - name: Generate daily summary
        run: |
          # Creates .sync-logs/YYYY-MM-DD-sync-summary.md
          # ... (see actual workflow file for full script)

      - name: Commit and push summary
        run: |
          git config user.name "Sync Bot"
          git config user.email "sync-bot@users.noreply.github.com"
          git add .sync-logs/
          git diff --staged --quiet || git commit -m "📋 Daily sync summary - $(date +%Y-%m-%d)"
          git push
```

## Adding More Repos

To sync additional repos from gblack686 to blackga-nih:

1. Create the destination repo on blackga-nih
2. Run initial mirror sync (see setup scripts in scratchpad)
3. Copy the workflow file to the new repo
4. Add `SOURCE_PAT` and `DEST_PAT` secrets to the new repo

## Troubleshooting

### Workflow fails on "Push mirror to this repo"
- Check that `DEST_PAT` has `repo` scope
- Verify PAT hasn't expired

### No summary file generated
- Check if there were commits in the last 24 hours
- Verify checkout step succeeded

### Email notifications for failures
- Check Actions tab: https://github.com/blackga-nih/nci-oa-agent/actions
- Review job logs for specific error

## Setup Date

- **Initial setup**: 2026-01-28
- **PAT stored**: `nih-github-pat` (ghp_2JrI...)
- **First successful sync**: 2026-01-28 20:18 UTC
