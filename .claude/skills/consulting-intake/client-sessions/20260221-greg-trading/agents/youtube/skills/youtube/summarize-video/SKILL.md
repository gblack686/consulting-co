---
name: youtube-summarize-video
description: "YouTube: Summarize Video - Generate structured summary with key points, timestamps, and trading-relevant actionable insights from a saved transcript."
user-invocable: true
metadata: {"openclaw": {"requires": {"env": []}}}
---

# YouTube: Summarize Video

Generate a structured summary from a saved transcript.
Takes either a video ID (looks up `transcripts/`) or a direct transcript path.
Output includes key points, notable quotes, timestamps, and trading-actionable insights.
Relevance score is calibrated for Hyper Liquid perps trading context.

## Allowed Tools
`Read, Write`

## Input
- Video ID: `abc123xyz`
- Or transcript path: `transcripts/2026-02-22-abc123xyz.md`
- Trigger: `/youtube-summarize abc123xyz`

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
4. **Actionable trading insights** (3–5) — what Greg can apply to Hyper Liquid strategy
5. **Topics covered** — comma-separated (e.g. funding rates, liquidations, TA patterns)
6. **Relevance score** (0–10) — calibrated for Hyper Liquid perps trading:
   - 8–10: Direct HyperLiquid strategy, specific entry/exit levels, risk frameworks
   - 5–7: General crypto TA or macro context useful for positioning
   - 1–4: General crypto content, low direct trading applicability
   - 0: Not trading-relevant

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

## Trading Insights
1. {insight}
2. {insight}

## Topics
{topics}
```

## Output
```
✅ Summary saved: summaries/2026-02-22-{video_id}.md
   Relevance: {score}/10
   Key points: {n}
   Topics: {topics}
```

## Error Handling
- Transcript too short (< 200 words) → summarize anyway, flag as `SHORT_TRANSCRIPT`
- Non-English transcript → note language in frontmatter, attempt summary anyway
