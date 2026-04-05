---
name: youtube-scan-channel
description: "YouTube: Scan Channel - Scan a YouTube channel for recent videos (last N days). Extracts transcripts for new content only. Outputs digest."
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["google-chrome", "chromium"], "env": []}}}
---

# YouTube: Scan Channel

Scan a YouTube channel for videos published in the last N days.
For each new video (not already in `scan-log.md`), extract the transcript and generate a summary.
Delivers a digest of new content.

## Allowed Tools
`Bash, Write, Read, WebFetch`

## Input
- Channel URL or handle: `https://youtube.com/@IndyDevDan` or `@IndyDevDan`
- Days back (default: 7): how far back to scan
- Trigger: `/youtube-scan @IndyDevDan 7`

## Workflow

### Phase 1: Scan
1. Load channel page via browser
2. Navigate to "Videos" tab → sort by "Latest"
3. Collect all videos published within the last `{days}` days:
   - Video ID, title, publish date, duration
4. Cross-reference with `scan-log.md` → filter to only new videos
5. If no new videos: report `No new videos since last scan` and exit

### Phase 2: Extract
For each new video (process sequentially to avoid rate limits):
1. Call `youtube-extract-transcript` skill for this video ID
2. If transcript available: call `youtube-summarize-video` skill
3. Wait 3s between videos

### Phase 3: Digest
1. Write digest to `summaries/digest-{date}-{channel_handle}.md`:
```markdown
# YouTube Digest — @{channel} — {date}

New videos: {count}

## {title} ({publish_date})
- ID: {video_id}
- Duration: {duration}
- Key points: ...
- Transcript: transcripts/{date}-{id}.md
```
2. Update `scan-log.md` with latest video ID scanned per channel

## Output
```
📺 Channel scan complete: @IndyDevDan
   New videos: 3 / 12 checked
   Transcripts extracted: 3
   Digest saved: summaries/digest-2026-02-21-IndyDevDan.md
```

## Error Handling
- Channel not found → report and exit
- Private video → skip, log as `PRIVATE`
- Age-restricted → skip, log as `AGE_RESTRICTED`
- Rate limited → pause 60s, continue from where stopped
