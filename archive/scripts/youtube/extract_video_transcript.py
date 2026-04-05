"""
Extract transcript from video URLs (YouTube, Vimeo, etc.)
Requires: pip install youtube-transcript-api yt-dlp
"""

from youtube_transcript_api import YouTubeTranscriptApi
import re
import sys

def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        # Try to get transcript (auto-generated or manual)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manual captions first
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            # Fall back to auto-generated
            transcript = transcript_list.find_generated_transcript(['en'])

        # Fetch and format transcript
        transcript_data = transcript.fetch()

        # Combine all text
        full_text = '\n'.join([entry['text'] for entry in transcript_data])
        return full_text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_video_transcript.py <video_url>")
        print("Example: python extract_video_transcript.py https://www.youtube.com/watch?v=VIDEO_ID")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_youtube_id(url)

    if not video_id:
        print("Could not extract video ID from URL")
        print("Make sure it's a valid YouTube URL")
        sys.exit(1)

    print(f"Extracting transcript for video ID: {video_id}")
    transcript = get_transcript(video_id)

    # Save to file
    output_file = f"transcript_{video_id}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transcript)

    print(f"\nTranscript saved to: {output_file}")
    print("\n--- Preview ---")
    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)

if __name__ == "__main__":
    main()
