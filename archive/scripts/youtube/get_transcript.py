#!/usr/bin/env python3
"""
Extract YouTube transcript using youtube-transcript-api
"""
import sys
import json

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("Installing youtube-transcript-api...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api", "-q"])
    from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    """Fetch transcript from YouTube video"""
    try:
        # Use the static method directly
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine all text segments
        full_text = "\n".join([item['text'] for item in transcript])
        return full_text
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    video_id = "9ipM_vDwflI"
    transcript = get_transcript(video_id)

    if transcript:
        print(transcript)
    else:
        sys.exit(1)
