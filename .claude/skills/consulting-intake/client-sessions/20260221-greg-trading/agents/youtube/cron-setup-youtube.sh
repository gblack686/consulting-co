#!/bin/bash
# Cron Job Setup — Scout YouTube Agent (Greg Trading)
# Run on the OpenClaw server after: just deploy-agents && just register-agents
#
# Playlist: Kyle Doops Trading Show
# Playlist ID: PLmOv2_vzOoGcDGeu-HHfifExgbvmPLO3l
#
# Transcripts land in: ~/.openclaw/workspace-youtube/transcripts/
# Digests land in:     ~/.openclaw/workspace-youtube/digests/
# Sebastian reads:     ~/.openclaw/workspace-youtube/digests/latest.md (morning brief)

PLAYLIST_ID="PLmOv2_vzOoGcDGeu-HHfifExgbvmPLO3l"
PLAYLIST_URL="https://www.youtube.com/playlist?list=$PLAYLIST_ID"

# 1. Daily playlist scan — 2:00 AM PST
#    Checks playlist for new episodes since last scan
#    Extracts transcripts, generates summaries, writes digests/latest.md
openclaw cron add \
  --name "Kyle Doops Daily Scan" \
  --cron "0 2 * * *" \
  --tz "America/Los_Angeles" \
  --agent youtube \
  --skill "youtube-scan-channel" \
  --input "{\"playlist\":\"$PLAYLIST_URL\",\"days\":1,\"output_digest\":\"digests/latest.md\"}" \
  --mode isolated \
  --delivery none

echo ""
echo "✅ Scout cron job installed (Greg Trading)"
echo "   Schedule: Daily at 2:00 AM PST"
echo "   Playlist: Kyle Doops Trading Show"
echo "   Playlist ID: $PLAYLIST_ID"
echo "   Output: ~/.openclaw/workspace-youtube/digests/latest.md"
echo "   Verify: openclaw cron list --agent youtube"
