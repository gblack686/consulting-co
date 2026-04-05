# HEARTBEAT.md — Scout 📺 Periodic Tasks (Greg Trading)

## Watched Playlist
- **Kyle Doops Trading Show** — `PLmOv2_vzOoGcDGeu-HHfifExgbvmPLO3l`
- See `AGENTS.md` for full playlist config

## Relevance Scoring for Trading Content
Flag a video HIGH_RELEVANCE (>= 7/10) if it covers:
- Hyper Liquid platform updates, new features, or funding rate mechanics
- Perps trading strategies, liquidation maps, or OI analysis
- Specific entry/exit levels or risk management frameworks
- Macro events likely to affect crypto perps

---

## Daily at 2:00 AM PST — Playlist Scan (via cron)

Handled by cron job — Scout is invoked by `openclaw cron` at 2 AM PST.
Scout checks the Kyle Doops playlist for new episodes since the last scan.

## Heartbeat Check (every 30 min, during waking hours)

1. Check `digests/latest.md` — if updated today, respond HEARTBEAT_OK
2. If not updated and time is after 02:30 AM PST: flag missed scan to Sebastian
3. Otherwise: respond HEARTBEAT_OK
2. Cross-reference with `scan-log.md` → extract transcripts for new videos only
3. Summarize each new video (relevance score 0–10 with trading context)
4. If any video scores >= 7/10: append `[HIGH_RELEVANCE]` entry to `digests/digest-{today}.md`
5. Update `scan-log.md` with latest scanned video ID per channel
6. If nothing new: respond HEARTBEAT_OK

## Daily Digest — 06:30 AM PST (before Sebastian's morning brief)

1. Compile all new content from past 24 hours across all channels
2. Write to `digests/digest-{YYYY-MM-DD}.md`
3. Top section: HIGH_RELEVANCE videos with key trade insights
4. Bottom section: all other new videos with TL;DR
5. Write `digests/latest.md` (symlink-style overwrite) — Sebastian reads this during morning brief

## Weekly Deep Scan — Sunday 11:00 PM PST

1. Full scan of all whitelisted channels (last 7 days)
2. Extract and summarize any videos missed during daily scans
3. Write `digests/weekly-{YYYY-MM-DD}.md` — weekly digest for Greg's review
4. Prune `scan-log.md` entries older than 30 days

---

# Quiet hours: 00:00 - 06:00 America/Los_Angeles
# During quiet hours, respond HEARTBEAT_OK — no active scanning
