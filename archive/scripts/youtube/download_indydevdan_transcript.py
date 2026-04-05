#!/usr/bin/env python3
"""Download IndyDevDan transcript."""

from youtube_transcript_api import YouTubeTranscriptApi

video_id = "1ECn5zrVUB4"

print(f"Downloading transcript for video {video_id}...")

try:
    # Try different methods
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try to get English transcript
    try:
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()
    except:
        # Get any available transcript
        transcript_data = transcript_list.find_generated_transcript(['en']).fetch()

    # Clean and combine
    transcript_clean = " ".join([entry['text'] for entry in transcript_data])

    # Save
    filename = f"transcript_{video_id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(transcript_clean)

    print(f"✓ Saved transcript to {filename}")
    print(f"  Length: {len(transcript_clean)} characters")
    print(f"  Entries: {len(transcript_data)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
