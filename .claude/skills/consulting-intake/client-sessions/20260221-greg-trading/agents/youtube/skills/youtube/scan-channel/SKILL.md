---
name: youtube-scan-channel
description: "YouTube: Scan Channel - Scan a YouTube channel for recent videos (last N days). Extracts transcripts for new content only. Outputs digest with trading relevance scores."
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["google-chrome", "chromium"], "env": []}}}
---

# YouTube: Scan Channel

Scan a YouTube channel for videos published in the last N days.
For each new video (not already in `scan-log.md`), extract the transcript and generate a summary.
Scores each video for trading relevance (0–10). Delivers a digest of new content.

## Allowed Tools
`Bash, Write, Read, WebFetch`

## Input
- Channel URL or handle: `@HyperliquidX`
- Days back (default: 1)
- Optional: `output_digest` path override for digest file
- Trigger: `/youtube-scan @HyperliquidX 1`

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
   - Scoring context for Greg: Hyper Liquid perps, funding rates, liquidation maps, risk management
3. Wait 3s between videos

### Phase 3: Digest
1. Write or append to digest file (`digests/digest-{date}-{channel_handle}.md` or `output_digest` if set):
```markdown
# YouTube Digest — @{channel} — {date}

New videos: {count}

## {title} ({publish_date}) [Relevance: {score}/10]
- ID: {video_id}
- Duration: {duration}
- Key points: ...
- Transcript: transcripts/{date}-{id}.md
- [HIGH_RELEVANCE] ← only if score >= 7
```
2. If any video scored >= 7/10: also append to `digests/latest.md` (HIGH_RELEVANCE section)
3. Update `scan-log.md` with latest video ID scanned per channel

## Output
```
📺 Channel scan complete: @HyperliquidX
   New videos: 2 / 8 checked
   Transcripts extracted: 2
   High relevance: 1 (flagged for Sebastian)
   Digest saved: digests/digest-2026-02-22-HyperliquidX.md
```

## Error Handling
- Channel not found → report and exit
- Private video → skip, log as `PRIVATE`
- Age-restricted → skip, log as `AGE_RESTRICTED`
- Rate limited → pause 60s, continue from where stopped
