---
name: youtube-extract-transcript
description: "YouTube: Extract Transcript - Pull full transcript from a YouTube video via headless Chrome. Saves to memory/transcripts/{date}-{id}.md"
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["google-chrome", "chromium"], "env": []}}}
---

# YouTube: Extract Transcript

Extract the full transcript from a YouTube video using browser automation.
Saves the result to `transcripts/YYYY-MM-DD-{video_id}.md` in the Scout agent workspace.

## Allowed Tools
`Bash, Write, Read, WebFetch`

## Input
- Video ID or full YouTube URL
  - Examples: `dQw4w9WgXcQ`, `https://youtube.com/watch?v=dQw4w9WgXcQ`

## Workflow

### Phase 1: Prepare
1. Extract video ID from input (strip URL if needed)
2. Check if `transcripts/` already contains this video ID — if yes, skip and report
3. Set output path: `transcripts/{YYYY-MM-DD}-{video_id}.md`

### Phase 2: Extract
1. Launch headless Chrome via `openclaw browser` or subprocess
2. Navigate to `https://youtube.com/watch?v={video_id}`
3. Activate transcript panel:
   - Click "..." (more actions) → "Show transcript"
   - If auto-generated only: proceed with it, note in metadata
4. Extract all transcript segments with timestamps
5. If extraction fails (no transcript available): log to `scan-log.md` as `NO_TRANSCRIPT` and exit cleanly

### Phase 3: Save
1. Write transcript to `transcripts/{date}-{video_id}.md`:
```markdown
---
video_id: {video_id}
url: https://youtube.com/watch?v={video_id}
title: {title}
channel: {channel_name}
extracted: {ISO timestamp}
transcript_type: auto-generated | manual
---

# {title}

{timestamp} {text}
{timestamp} {text}
...
```
2. Append entry to `scan-log.md`

## Output
```
✅ Transcript saved: transcripts/2026-02-21-dQw4w9WgXcQ.md
   Video: "Never Gonna Give You Up" — Rick Astley
   Segments: 42
   Type: auto-generated
```

## Error Handling
- Chrome not found → report missing prerequisite, link to install guide
- No transcript available → log `NO_TRANSCRIPT` to scan-log, continue
- Network error → retry once, then log failure
- Rate limited → wait 30s, retry once
