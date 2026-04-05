---
model: opus
description: Unified TAC scanner - scans IndyDevDan YouTube + disler GitHub for new content, clones repos, processes videos, extracts TAC
argument-hint: "[days] - e.g., '7' for last 7 days, or 'video abc123' for single video"
allowed-tools: Bash(date:*), Bash(mkdir:*), Bash(python:*), Bash(git:*), Bash(gh:*), Task, Write, Read, Glob, Grep
---

# Unified TAC Scanner

## Purpose

One command to scan all IndyDevDan/disler content sources:
1. **YouTube** (@indydevdan) - scan for new videos, download transcripts, extract TAC
2. **GitHub** (disler) - scan for new/updated repos, clone to `Desktop/tac/`, extract TAC

## Quick Usage

```bash
# Scan everything from last 7 days
/youtube-tac-extract 7

# Scan everything from last 30 days
/youtube-tac-extract 30

# Process a single video
/youtube-tac-extract video abc123
```

## Variables

- **DAYS_BACK**: $1 (number of days to look back, default: 7)
- **TAC_DIR**: `C:\Users\gblac\OneDrive\Desktop\tac`
- **SKILL_DIR**: `.claude/skills/youtube-video-archiver`
- **OBSIDIAN_VAULT**: `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation`
- **AI_AGENT_KB**: `{OBSIDIAN_VAULT}/AI-Agent-KB`
- **GITHUB_CONFIG**: `.claude/obsidian/github-watchlist-config.json`
- **TIMESTAMP**: Current datetime

## Watched Sources

### YouTube Channel
| Handle | Channel | Content |
|--------|---------|---------|
| @indydevdan | IndyDevDan | Claude Code, ADWs, TAC courses |

### GitHub Users
| User | Focus |
|------|-------|
| disler | TAC course repos, agent examples |
| coleam00 | Archon, MCP servers, AI coding |

## Unified Workflow

### Step 0: Setup

```bash
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_DIR=".claude/context/tac-scan/${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"
mkdir -p "C:/Users/gblac/OneDrive/Desktop/tac"
```

### Step 1: YouTube Scan

Scan @indydevdan for new videos:

```bash
cd ".claude/skills/youtube-video-archiver"
python youtube_watchlist.py scan --days {DAYS_BACK}
```

**Outputs**:
- New videos list
- Report at `youtube/YYYY-MM-DD-youtube-watchlist.md`

**Save to**: `{OUTPUT_DIR}/youtube_scan.json`

### Step 2: GitHub Scan

Scan disler + coleam00 for new repos and commits:

```bash
python .claude/obsidian/github_watchlist.py --days {DAYS_BACK}
```

**Outputs**:
- Repos with new commits
- Report at `github-watchlist/YYYY-MM-DD-github-activity.md`

**Save to**: `{OUTPUT_DIR}/github_scan.json`

### Step 3: Clone New Repos

For each NEW repo from disler (not already in tac directory):

```bash
# Check if repo exists
if [ ! -d "C:/Users/gblac/OneDrive/Desktop/tac/{REPO_NAME}" ]; then
    cd "C:/Users/gblac/OneDrive/Desktop/tac"
    git clone https://github.com/disler/{REPO_NAME}.git
fi
```

For existing repos with new commits:

```bash
cd "C:/Users/gblac/OneDrive/Desktop/tac/{REPO_NAME}"
git pull origin main
```

**Log cloned/updated repos to**: `{OUTPUT_DIR}/repos_synced.md`

### Step 4: Process YouTube Videos

For each new video found in Step 1:

#### 4a. Download Transcript (Fallback Chain)

Try these methods in order. Stop at the first that succeeds:

**Method 1: Python API (fastest)**
```bash
cd ".claude/skills/youtube-video-archiver"
python archive_single_video.py {VIDEO_ID}
```

**Method 2: yt-dlp subtitles**
```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download -o "{OUTPUT_DIR}/{VIDEO_ID}" "https://www.youtube.com/watch?v={VIDEO_ID}"
```

**Method 3: Browser extraction (reliable fallback — requires `--chrome`)**

Use the bowser youtube-transcript command to extract via your real Chrome browser:
```
/bowser:youtube-transcript {VIDEO_ID} {OUTPUT_DIR}
```

This navigates to the video in your signed-in Chrome, expands the description (capturing GitHub links), opens the transcript panel, and extracts all segments via JavaScript. Bypasses all bot detection and API limits.

**Method 4: Description-only fallback**

If no transcript method works, use the YouTube Data API to fetch the full description. Many IndyDevDan videos have detailed descriptions with enough content for TAC extraction:
```bash
cd ".claude/skills/youtube-video-archiver"
python scripts/youtube_scraper.py --video-id {VIDEO_ID}
```

#### 4b. Extract TAC Entities

Use Task agent to analyze transcript:

```
Analyze this YouTube video transcript from IndyDevDan and extract TAC:

VIDEO: {TITLE}
TRANSCRIPT: {TRANSCRIPT}

Extract:

## TECHNIQUES
- Name, category, description, implementation steps, source quote

## AUTOMATIONS (ADWs, agents, scripts, hooks)
- Name, type, purpose, components

## CONCEPTS
- Name, definition, why it matters

Output as JSON with arrays: techniques[], automations[], concepts[]
```

#### 4c. Create AI-Agent-KB Notes

For each entity, create note in appropriate folder:

| Type | Folder |
|------|--------|
| technique | `AI-Agent-KB/09-Techniques/` |
| adw | `AI-Agent-KB/01-ADWs/` |
| agent | `AI-Agent-KB/02-Agents/` |
| concept | `AI-Agent-KB/10-Concepts/` |
| hook | `AI-Agent-KB/08-Hooks/` |
| command | `AI-Agent-KB/08-Commands/` |

**Note template**:
```markdown
---
title: "{NAME}"
type: {TYPE}
source: youtube
source_video: "[[{VIDEO_TITLE}]]"
source_channel: "[[IndyDevDan]]"
date_extracted: {DATE}
tags: [{TYPE}, youtube-extracted, indydevdan]
---

# {NAME}

## Overview
{DESCRIPTION}

## Implementation
{IMPLEMENTATION}

## Source
> {QUOTE}

From [[{VIDEO_TITLE}]] by [[IndyDevDan]]
```

#### 4d. Mark Video Processed

```python
watchlist.mark_processed(video_id)
```

### Step 5: Extract TAC from Repos

For each new/updated repo, run TAC extraction:

```bash
cd "C:/Users/gblac/OneDrive/Desktop/consulting-co"
python tac-learning-system/extractor/tac_extractor.py {REPO_NAME}
```

This extracts:
- Commands from `.claude/commands/`
- Agents from `.claude/agents/`
- ADWs from `adws/`
- Concepts from README and ai_docs

**Save extraction to**: `tac-learning-system/{REPO_NAME}/extraction.json`

### Step 5.5: Archive to TAC Plugin Catalog

For each new/updated repo, update the TAC experts plugin catalog:

```bash
# Call the pipeline hook (wrapper around archive-repo.py)
bash "C:/Users/gblac/OneDrive/Desktop/tac/tac-experts-plugin/scripts/tac-pipeline-hook.sh" \
    "C:/Users/gblac/OneDrive/Desktop/tac/{REPO_NAME}"

# Or call archive-repo.py directly with lesson override
python "C:/Users/gblac/OneDrive/Desktop/tac/tac-experts-plugin/scripts/archive-repo.py" \
    "C:/Users/gblac/OneDrive/Desktop/tac/{REPO_NAME}" --lesson auto
```

This updates:
- `tac-experts-plugin/apps/README.md` — app catalog entry
- `tac-experts-plugin/docs/advanced-lessons.md` — lesson reference
- `tac-experts-plugin/data/tags.md` — lesson-specific tags
- `tac-experts-plugin/commands/experts/tac/tac-learning-expertise.md` — expertise entry

**Log archive results to**: `{OUTPUT_DIR}/plugin_archive.md`

### Step 6: Sync Repo TAC to Obsidian

For extracted entities from repos:

```bash
# Use ecosystem sync command
/ecosystem:copy-to-obsidian
```

Or manually create notes for each extracted entity following the same templates.

### Step 7: Generate Summary Report

Create unified report:

```markdown
# TAC Scan Report - {TIMESTAMP}

## Summary

| Source | Items Found | New | Processed |
|--------|-------------|-----|-----------|
| YouTube | {N} videos | {N} | {N} |
| GitHub | {N} repos | {N} | {N} |

## YouTube - New Videos Processed

| Video | TAC Extracted |
|-------|---------------|
| {TITLE} | {N} techniques, {N} automations, {N} concepts |

## GitHub - Repos Synced

| Repo | Status | TAC Extracted |
|------|--------|---------------|
| {REPO} | cloned/updated | {N} commands, {N} agents, {N} ADWs |

## New AI-Agent-KB Notes Created

### From YouTube
- [[Technique Name]] (technique)
- [[ADW Name]] (adw)

### From GitHub
- [[Command Name]] (command)
- [[Agent Name]] (agent)

## Files

- YouTube scan: {OUTPUT_DIR}/youtube_scan.json
- GitHub scan: {OUTPUT_DIR}/github_scan.json
- Repos synced: {OUTPUT_DIR}/repos_synced.md
```

**Save to**: `{OUTPUT_DIR}/SCAN_REPORT.md`

## Single Video Mode

If argument starts with "video":

```bash
/youtube-tac-extract video abc123
```

Skip Steps 1-3, 5-6 and only run Step 4 for the specified video.

## Configuration Files

### YouTube Whitelist
**File**: `.claude/skills/youtube-video-archiver/channel_whitelist.json`

```json
{
  "channels": [
    {
      "handle": "@indydevdan",
      "channel_id": "UC_x36zCEGilGpB1m-V4gmjg",
      "description": "IndyDevDan - Claude Code, ADWs"
    }
  ]
}
```

### GitHub Watchlist
**File**: `.claude/obsidian/github-watchlist-config.json`

```json
{
  "users": ["disler", "coleam00"],
  "organizations": ["dynamous-community"]
}
```

### TAC Directory
**Path**: `C:\Users\gblac\OneDrive\Desktop\tac\`

All disler repos get cloned here for local access and TAC extraction.

## Examples

```bash
# Full scan - last 7 days (DEFAULT)
/youtube-tac-extract 7

# Quick daily check
/youtube-tac-extract 1

# Monthly deep scan
/youtube-tac-extract 30

# Process specific video
/youtube-tac-extract video C5USs51zYu8

# Process YouTube URL
/youtube-tac-extract video https://www.youtube.com/watch?v=C5USs51zYu8
```

## State Tracking

### YouTube State
**File**: `.claude/skills/youtube-video-archiver/.youtube_watchlist_state.json`

Tracks processed video IDs to avoid reprocessing.

### GitHub State
**File**: `{OBSIDIAN_VAULT}/github-watchlist/.state.json`

Tracks last scan time and processed commits.

### TAC Directory
Repos in `Desktop/tac/` are considered "known" - only new repos get cloned.

## Expected Output

After running `/youtube-tac-extract 7`:

```
============================================================
TAC SCAN - 2026-02-02
============================================================

YOUTUBE SCAN (@indydevdan)
------------------------------------------------------------
Scanning last 7 days...
Found 3 videos
  [NEW]  Claude Code ADWs Part 6 - Advanced Patterns
  [NEW]  MCP Server Deep Dive
  [SKIP] Building Agents (already processed)

GITHUB SCAN (disler)
------------------------------------------------------------
Scanning last 7 days...
Found 2 repos with activity
  [NEW]  tac-9 (cloning...)
  [UPD]  claude-code-hooks-mastery (pulling...)

PROCESSING
------------------------------------------------------------
Processing video: Claude Code ADWs Part 6...
  Downloading transcript...
  Extracting TAC...
  Found: 4 techniques, 2 ADWs, 3 concepts
  Creating notes...

Processing video: MCP Server Deep Dive...
  Downloading transcript...
  Extracting TAC...
  Found: 2 techniques, 1 tool, 2 concepts
  Creating notes...

Extracting TAC from repo: tac-9...
  Found: 8 commands, 3 agents, 2 ADWs

SUMMARY
============================================================
YouTube: 2 videos processed, 15 TAC entities extracted
GitHub: 2 repos synced, 13 TAC entities extracted

Reports saved to:
  .claude/context/tac-scan/2026-02-02_10-30-00/SCAN_REPORT.md
```

## Quick Reference

| What | Where |
|------|-------|
| YouTube whitelist | `.claude/skills/youtube-video-archiver/channel_whitelist.json` |
| GitHub config | `.claude/obsidian/github-watchlist-config.json` |
| TAC repos | `C:\Users\gblac\OneDrive\Desktop\tac\` |
| AI-Agent-KB | `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\` |
| Scan reports | `.claude/context/tac-scan/` |
