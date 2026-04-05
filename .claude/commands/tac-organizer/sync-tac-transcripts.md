# Sync TAC Transcripts

> Fetch YouTube transcripts from IndyDevDan channel and match them to TAC lesson directories.

## Purpose

Download video transcripts and match them to the correct TAC lesson folder in `TAC-Learning-System/quizzes-and-diagrams/`.

## Variables

- `TARGET_DIR`: `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\TAC-Learning-System\quizzes-and-diagrams`
- `CHANNEL_ID`: `UC_x36zCEGilGpB1m-V4gmjg` (IndyDevDan)
- `SERVICE_ACCOUNT`: AWS Secret `gbautomation/core/google-service-account`
- `APIFY_TOKEN`: AWS Secret `gbautomation/core/apify-token` ($0.007/transcript)

## Workflow

### Step 1: Get IndyDevDan Channel Videos

Use YouTube Data API with service account to fetch video list:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'service_account.json',
    scopes=['https://www.googleapis.com/auth/youtube.readonly']
)
youtube = build('youtube', 'v3', credentials=credentials)

# Get videos
request = youtube.search().list(
    part='snippet',
    channelId='UC_x36zCEGilGpB1m-V4gmjg',
    type='video',
    order='date',
    maxResults=50
)
videos = request.execute()
```

### Step 2: Match Video to Lesson Folder

Use title/description keywords to match videos to lesson folders:

| Lesson Folder | Search Keywords |
|---------------|-----------------|
| `tac-1` | "Hello Agentic Coding" |
| `tac-2` | "12 Leverage Points" |
| `tac-3` | "Success is Planned" |
| `tac-4` | "AFK Agents" |
| `tac-5` | "Close The Loops" |
| `tac-6` | "Let Your Agents Focus" |
| `tac-7` | "ZTE Secret of Agentic Engineering" |
| `tac-8` | "Agentic Layer" |
| `elite-context-engineering` | "Elite Context Engineering", "R&D Framework" |
| `agentic-prompt-engineering` | "Seven Levels", "Agentic Prompt" |
| `building-specialized-agents` | "5 Agent PATTERNS", "Domain-Specific Agents" |
| `multi-agent-orchestration` | "One Agent to RULE", "O Agent" |
| `orchestrator-agent-with-adws` | "Agentic Workflows BEYOND", "ADW" |
| `agent-experts` | "Agent Experts", "Agents That ACTUALLY Learn" |
| `software-delivery-adw` | "Software Delivery ADW" |

**Matching Logic:**
1. Search YouTube API with lesson keywords
2. Verify video exists on IndyDevDan channel
3. Extract video_id for transcript download

### Step 3: Check Existing Transcript

Before downloading, check if transcript exists:

```python
import os

target_path = f"{TARGET_DIR}/{lesson_folder}/transcript.txt"
if os.path.exists(target_path):
    with open(target_path, 'r') as f:
        existing = f.read()
    print(f"Existing: {len(existing)} chars")
    # Compare quality before overwriting
```

### Step 4: Download Transcript

**Choose ONE of these methods:**

#### Option A: Apify (Recommended - $0.007/transcript)

Use the `/youtube-transcript-apify` skill for clean, deduplicated transcripts:

```python
import requests
import json
import time
import boto3
import html

def get_apify_token():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    secret = client.get_secret_value(SecretId='gbautomation/core/apify-token')
    return secret['SecretString']

def fetch_transcript_apify(video_id):
    token = get_apify_token()
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    # Start run
    run_url = f'https://api.apify.com/v2/acts/karamelo~youtube-transcripts/runs?token={token}'
    response = requests.post(run_url, json={'urls': [video_url]})
    run_data = response.json()['data']
    run_id, dataset_id = run_data['id'], run_data['defaultDatasetId']

    # Wait for completion
    status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={token}'
    while True:
        status = requests.get(status_url).json()['data']['status']
        if status == 'SUCCEEDED': break
        if status in ['FAILED', 'ABORTED']: raise Exception(f"Failed: {status}")
        time.sleep(2)

    # Get results
    results = requests.get(f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}').json()
    captions = results[0].get('captions', [])
    transcript = html.unescape(' '.join(captions))
    return transcript, results[0].get('title', 'Unknown')
```

#### Option B: yt-dlp (Free)

```bash
python -m yt_dlp --skip-download --write-auto-sub --sub-lang en \
  -o "%(id)s.%(ext)s" "https://youtube.com/watch?v={VIDEO_ID}"
```

### Step 5: Parse VTT to Plain Text (Only for Option B)

Skip this step if using Apify (Option A).

Remove timestamps, deduplicate lines:

```python
import re

def parse_vtt_to_text(vtt_content):
    lines = vtt_content.split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        # Skip metadata
        if not line or line.startswith('WEBVTT') or '-->' in line:
            continue
        if re.match(r'^\d+$', line):
            continue
        # Remove VTT tags
        line = re.sub(r'<[^>]+>', '', line)
        if line:
            text_lines.append(line)

    # Deduplicate consecutive lines
    deduped = []
    prev = ''
    for line in text_lines:
        if line != prev:
            deduped.append(line)
            prev = line

    return ' '.join(deduped)
```

### Step 6: Enhance Transcript (Optional)

Add metadata header to match existing format:

```python
def format_transcript(text, lesson_num, video_title):
    header = f"""TAC Lesson {lesson_num} - Transcript
Source: IndyDevDan TAC Course
Video: "{video_title}"

{'='*80}

"""
    return header + text
```

### Step 7: Save to Lesson Folder

```python
target_path = f"{TARGET_DIR}/{lesson_folder}/transcript.txt"
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(formatted_transcript)
```

### Step 8: Update TRANSCRIPT_INDEX.md

Add entry to index if new:

```markdown
| {lesson_num} | {folder} | {video_id}_transcript.txt | {video_title} |
```

## Quality Considerations

1. **Existing transcripts may be higher quality** - Manual transcriptions are more accurate
2. **Auto-generated has duplicates** - YouTube captions often repeat for timing
3. **Compare before overwriting** - Only replace if new is significantly better
4. **Missing transcripts priority** - Focus on lessons without transcripts first

## Known Lesson-Video Mappings

| Video ID | Title | Lesson Folder |
|----------|-------|---------------|
| `zTcDwqopvKE` | Agent Experts: Finally, Agents That ACTUALLY Learn | `agent-experts` |
| `Kf5-HWJPTIE` | Elite Context Engineering with Claude Code | `elite-context-engineering` |
| `p0mrXfwAbCg` | The One Agent to RULE them ALL | `multi-agent-orchestration` |

## Transcript Status

**All 14 video lessons have transcripts (100% coverage)**

| Lesson | Folder | Status |
|--------|--------|--------|
| 1-12 | tac-1 through multi-agent-orchestration | ✅ External source (high quality) |
| 13 | orchestrator-agent-with-adws | ✅ YouTube transcript |
| 14 | agent-experts | ✅ YouTube transcript |

**Note**: `software-delivery-adw` is a reference implementation repository, not a video lesson (no transcript expected)

## Report

After syncing, generate report:

```markdown
## Transcript Sync Report

### Updated
- {lesson}: {video_id} ({chars} chars)

### Skipped (existing is better)
- {lesson}: existing {existing_chars} vs new {new_chars}

### Missing (no video found)
- {lesson}: No matching video on IndyDevDan channel

### New Videos (not yet mapped)
- {video_id}: {title} - needs lesson folder assignment
```
