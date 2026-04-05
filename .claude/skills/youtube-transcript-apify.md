# YouTube Transcript via Apify

> Download YouTube video transcripts using Apify's karamelo/youtube-transcripts actor.

## Purpose

Fetch clean, deduplicated transcripts from YouTube videos using Apify's pay-per-use API. Returns plain text without VTT formatting issues.

## Cost

- **$0.007/transcript** (FREE tier)
- No subscription required
- $5/month credit on FREE plan (~700 transcripts)

## AWS Secret

`gbautomation/core/apify-token`

## Usage

```
/youtube-transcript-apify <video_url_or_id> [output_path]
```

## Arguments

- `video_url_or_id`: YouTube video URL or video ID (e.g., `zTcDwqopvKE` or `https://youtube.com/watch?v=zTcDwqopvKE`)
- `output_path`: Optional path to save transcript (defaults to stdout)

## Implementation

```python
import requests
import json
import time
import boto3
import re
import html

def get_apify_token():
    """Retrieve Apify token from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = client.get_secret_value(SecretId='gbautomation/core/apify-token')
    return secret['SecretString']

def extract_video_id(url_or_id):
    """Extract video ID from URL or return as-is if already an ID."""
    if len(url_or_id) == 11 and not url_or_id.startswith('http'):
        return url_or_id

    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from: {url_or_id}")

def fetch_transcript_apify(video_url_or_id, timeout=120):
    """
    Fetch YouTube transcript via Apify karamelo/youtube-transcripts actor.

    Returns dict with:
        - title: Video title
        - video_id: YouTube video ID
        - channel: Channel name
        - published: Publication date
        - transcript: Plain text transcript
        - char_count: Character count
    """
    token = get_apify_token()
    video_id = extract_video_id(video_url_or_id)
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    # Start Apify run
    run_url = f'https://api.apify.com/v2/acts/karamelo~youtube-transcripts/runs?token={token}'
    payload = {'urls': [video_url]}

    response = requests.post(run_url, json=payload)
    if response.status_code != 201:
        raise Exception(f"Failed to start Apify run: {response.text}")

    run_data = response.json()['data']
    run_id = run_data['id']
    dataset_id = run_data['defaultDatasetId']

    # Wait for completion
    status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={token}'
    start_time = time.time()

    while time.time() - start_time < timeout:
        status_response = requests.get(status_url)
        status = status_response.json()['data']['status']

        if status == 'SUCCEEDED':
            break
        elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
            raise Exception(f"Apify run failed with status: {status}")

        time.sleep(2)
    else:
        raise Exception(f"Apify run timed out after {timeout}s")

    # Fetch results
    results_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}'
    results = requests.get(results_url).json()

    if not results:
        raise Exception("No results returned from Apify")

    item = results[0]

    # Extract and clean transcript
    captions = item.get('captions', [])
    if isinstance(captions, list):
        if captions and isinstance(captions[0], str):
            raw_text = ' '.join(captions)
        elif captions and isinstance(captions[0], dict):
            raw_text = ' '.join([c.get('text', '') for c in captions])
        else:
            raw_text = ''
    else:
        raw_text = str(captions)

    # Clean HTML entities
    transcript = html.unescape(raw_text)

    return {
        'title': item.get('title', 'Unknown'),
        'video_id': item.get('videoId', video_id),
        'channel': item.get('channelName', 'Unknown'),
        'published': item.get('datePublished', 'Unknown'),
        'transcript': transcript,
        'char_count': len(transcript)
    }

def format_transcript_with_header(result):
    """Format transcript with metadata header."""
    header = f"""YouTube Video Transcript
========================
Title: {result['title']}
Channel: {result['channel']}
Video ID: {result['video_id']}
Published: {result['published']}
Characters: {result['char_count']}

{'='*80}

"""
    return header + result['transcript']


# CLI Usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript_apify.py <video_url_or_id> [output_path]")
        sys.exit(1)

    video_input = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Fetching transcript for: {video_input}")
    result = fetch_transcript_apify(video_input)

    formatted = format_transcript_with_header(result)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print(f"Saved to: {output_path} ({result['char_count']} chars)")
    else:
        print(formatted)
```

## Example

```bash
# Fetch transcript and save to file
python youtube_transcript_apify.py zTcDwqopvKE ./transcript.txt

# Fetch transcript to stdout
python youtube_transcript_apify.py "https://youtube.com/watch?v=zTcDwqopvKE"
```

## Output Format

```
YouTube Video Transcript
========================
Title: Agent Experts: Finally, Agents That ACTUALLY Learn
Channel: IndyDevDan
Video ID: zTcDwqopvKE
Published: 2025-12-15T14:01:49.000Z
Characters: 19098

================================================================================

Agents of today have many problems. Most of them can be solved with great context...
```

## Comparison with yt-dlp

| Feature | Apify | yt-dlp |
|---------|-------|--------|
| Cost | $0.007/transcript | Free |
| Deduplication | Clean (no VTT rolling) | Requires post-processing |
| Speed | ~10-15s | ~5-10s |
| Reliability | 99.96% success | Varies |
| Output | Plain text JSON | VTT file |

## When to Use

- **Use Apify**: Missing transcripts, batch processing, when quality matters
- **Use yt-dlp**: Free tier exhausted, already have VTT parsing pipeline
