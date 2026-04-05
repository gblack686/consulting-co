#!/usr/bin/env python3
"""Quick script to download YouTube transcript."""

from youtube_transcript_api import YouTubeTranscriptApi

video_id = "C5USs51zYu8"

print(f"Downloading transcript for video {video_id}...")

api = YouTubeTranscriptApi()
transcript_data = api.fetch(video_id, languages=['en'])

# Access attributes on FetchedTranscriptSnippet objects
transcript_clean = " ".join([entry.text for entry in transcript_data])

# Save
filename = f"transcript_{video_id}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(transcript_clean)

print(f"✓ Saved transcript to {filename}")
print(f"  Length: {len(transcript_clean)} characters")
print(f"  Entries: {len(transcript_data)}")
