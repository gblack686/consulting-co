---
name: youtube-summarize-video
description: "YouTube: Summarize Video - Generate structured summary with key points, timestamps, and actionable insights from a saved transcript."
user-invocable: true
metadata: {"openclaw": {"requires": {"env": []}}}
---

# YouTube: Summarize Video

Generate a structured summary from a saved transcript.
Takes either a video ID (looks up `transcripts/`) or a direct transcript path.
Output includes key points, notable quotes, timestamps, and actionable insights.

## Allowed Tools
`Read, Write`

## Input
- Video ID: `dQw4w9WgXcQ`
- Or transcript path: `transcripts/2026-02-21-dQw4w9WgXcQ.md`
- Trigger: `/youtube-summarize dQw4w9WgXcQ`

## Workflow

### Phase 1: Load
1. Locate transcript file (by video ID or path)
2. If not found: prompt user to run `youtube-extract-transcript` first
3. Read frontmatter (title, channel, date) and full transcript text

### Phase 2: Analyze
Produce:
1. **1-sentence TL;DR** — what is this video about in plain English
2. **Key points** (5–10 bullets) — the most important ideas, with timestamps
3. **Notable quotes** (2–3) — exact quotes with timestamps
4. **Actionable insights** (3–5) — what can you do or learn from this video
5. **Topics covered** — comma-separated list of main topics/keywords
6. **Relevance score** (0–10) — how relevant is this to the user's current goals

### Phase 3: Save
Write to `summaries/{date}-{video_id}.md`:
```markdown
---
video_id: {video_id}
title: {title}
channel: {channel}
summary_date: {ISO timestamp}
relevance: {0-10}
topics: [topic1, topic2, ...]
---

# {title} — Summary

**TL;DR:** {one sentence}

## Key Points
- [{timestamp}] {point}
- [{timestamp}] {point}

## Notable Quotes
> "{quote}" — [{timestamp}]

## Actionable Insights
1. {insight}
2. {insight}

## Topics
{topics}
```

## Output
```
✅ Summary saved: summaries/2026-02-21-dQw4w9WgXcQ.md
   Relevance: 8/10
   Key points: 7
   Topics: AI agents, Claude Code, TAC methodology
```

## Error Handling
- Transcript too short (< 200 words) → summarize anyway, flag as `SHORT_TRANSCRIPT`
- Non-English transcript → note language in frontmatter, attempt summary anyway
