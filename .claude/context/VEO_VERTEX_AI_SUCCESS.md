# Veo 3.1 Frame Interpolation - SUCCESS!

**Date**: December 13, 2025
**Status**: ✅ WORKING

---

## Summary

Successfully generated a parallax animation video using Veo 3.1 frame interpolation through the **Vertex AI API endpoint**.

## The Problem

Initial attempts using the Gemini API endpoint failed with errors:
- ❌ `bytesBase64 isn't supported by this model`
- ❌ `gcsUri isn't supported by this model`

**Root Cause**: Wrong API endpoint. The Gemini API endpoint (`generativelanguage.googleapis.com`) doesn't support Veo 3.1's full feature set, including frame interpolation.

## The Solution

Switch to **Vertex AI API endpoint**:

### Correct Endpoint
```
https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:predictLongRunning
```

### Key Differences from Gemini API

| Aspect | Gemini API | Vertex AI |
|--------|-----------|-----------|
| **Endpoint** | generativelanguage.googleapis.com | aiplatform.googleapis.com |
| **Authentication** | API Key | OAuth 2.0 Bearer Token (service account) |
| **Model ID** | veo-3.1-generate-preview | veo-3.1-generate-001 |
| **Frame Interpolation** | ❌ Not supported | ✅ Fully supported |
| **GCS URIs** | ❌ Not supported | ✅ Required for images |
| **Best For** | Simple text-to-video | Enterprise, full features |

---

## Working Implementation

### 1. Upload Frames to GCS
```python
from google.cloud import storage

client = storage.Client(project='gblackautomation')
bucket = client.bucket('gblackautomation-veo-videos')

blob = bucket.blob('veo-images/option7_start.png')
blob.upload_from_filename('option7_start.png')

first_gcs_uri = 'gs://gblackautomation-veo-videos/veo-images/option7_start.png'
last_gcs_uri = 'gs://gblackautomation-veo-videos/veo-images/option7_end.png'
```

### 2. Get OAuth Token
```python
from google.auth.transport.requests import Request
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'C:/Users/gblac/.gcp/veo-agent-key.json'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())
access_token = credentials.token
```

### 3. Call Vertex AI API
```python
import requests

url = (
    f'https://us-central1-aiplatform.googleapis.com/v1/'
    f'projects/gblackautomation/locations/us-central1/'
    f'publishers/google/models/veo-3.1-generate-001:predictLongRunning'
)

data = {
    'instances': [{
        'prompt': 'NEURAL-01 robot, smooth hammer motion, parallax camera',
        'image': {'gcsUri': first_gcs_uri, 'mimeType': 'image/png'},
        'lastFrame': {'gcsUri': last_gcs_uri, 'mimeType': 'image/png'}
    }],
    'parameters': {
        'storageUri': 'gs://gblackautomation-veo-videos/generated-videos/',
        'sampleCount': 1,
        'aspectRatio': '16:9'
    }
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, json=data, timeout=30)
result = response.json()
operation_name = result['name']
```

### 4. Check GCS Bucket for Output

Instead of polling the operation (which uses a non-standard UUID format), check the output bucket:

```python
bucket = client.bucket('gblackautomation-veo-videos')
blobs = list(bucket.list_blobs(prefix='generated-videos/'))

# Video appears at: gs://.../generated-videos/{ID}/sample_0.mp4
```

### 5. Download Video
```python
blob = bucket.blob('generated-videos/16127965426663688663/sample_0.mp4')
blob.download_to_filename('option7_parallax_veo.mp4')
```

---

## Results

**Generated Video**: `option7_parallax_veo.mp4` (2.97 MB)

**Details**:
- First frame: `option7_start.png` (robot with hammer mid-swing)
- Last frame: `option7_end.png` (robot with hammer lowered)
- Prompt: NEURAL-01 Generalist robot at workbench from side angle, smooth hammer motion from mid-swing to lowered position, subtle parallax camera movement
- Duration: ~8 seconds
- Aspect ratio: 16:9
- Resolution: 720p
- Model: veo-3.1-generate-001
- Generation time: ~1-3 minutes

**GCS URIs**:
- First frame: `gs://gblackautomation-veo-videos/veo-images/option7_start.png`
- Last frame: `gs://gblackautomation-veo-videos/veo-images/option7_end.png`
- Output video: `gs://gblackautomation-veo-videos/generated-videos/16127965426663688663/sample_0.mp4`

---

## Why Operation Polling Failed

The Vertex AI Veo operations use a non-standard format:
- **Operation name**: `projects/.../publishers/google/models/veo-3.1-generate-001/operations/{UUID}`
- **Standard operations endpoint**: Expects numeric IDs, not UUIDs
- **Error**: `The Operation ID must be a Long, but was instead: 1173415e-80ca-45cf-9d14-b0f975456414`

**Workaround**: Instead of polling the operation, check the GCS output bucket directly. Veo writes the video to `storageUri` when complete.

---

## Complete Workflow

### Quick Start
```bash
# 1. Upload frames to GCS
python scripts/upload_to_gcs.py option7_start.png --bucket gblackautomation-veo-videos
python scripts/upload_to_gcs.py option7_end.png --bucket gblackautomation-veo-videos

# 2. Generate video (uses service account auth)
python scripts/interpolate_frames_vertex.py \
  option7_start.png option7_end.png \
  "Smooth parallax motion" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos

# 3. Wait 1-5 minutes, then check bucket
gsutil ls gs://gblackautomation-veo-videos/generated-videos/

# 4. Download video
python scripts/download_from_gcs.py \
  gs://gblackautomation-veo-videos/generated-videos/{ID}/sample_0.mp4 \
  --output my_video.mp4
```

---

## Key Learnings

### 1. Two Different Google Video APIs

**Gemini API** (`generativelanguage.googleapis.com`):
- ✅ Simple API key authentication
- ✅ Easy to use for basic tasks
- ❌ Limited feature set
- ❌ No frame interpolation support
- ✅ Good for: Quick prototyping, simple text-to-video

**Vertex AI** (`aiplatform.googleapis.com`):
- ✅ Full Veo 3.1 feature set
- ✅ Frame interpolation support
- ✅ Enterprise features (IAM, quotas, monitoring)
- ❌ Requires OAuth 2.0 / service account
- ❌ More complex setup
- ✅ Good for: Production, advanced features, frame interpolation

### 2. Authentication Methods

**API Key** (Gemini API):
```python
url = f"{BASE_URL}?key={API_KEY}"
```

**OAuth Bearer Token** (Vertex AI):
```python
headers = {"Authorization": f"Bearer {access_token}"}
```

### 3. GCS is Required for Vertex AI

Vertex AI Veo requires:
- **Input images**: Must be GCS URIs (not inline base64)
- **Output videos**: Written to GCS bucket specified in `storageUri`
- **Format**: `gs://bucket-name/path/to/file.png`

---

## Files Created

### Scripts
- `C:/Users/gblac/.claude/global/skills/veo-agent/scripts/interpolate_frames_vertex.py` - Working Vertex AI implementation
- `C:/Users/gblac/.claude/global/skills/veo-agent/scripts/upload_to_gcs.py` - Upload helper
- `C:/Users/gblac/.claude/global/skills/veo-agent/scripts/download_from_gcs.py` - Download helper

### Output
- `option7_parallax_veo.mp4` (2.97 MB) - Generated video
- `option7_parallax_veo.json` - Metadata

### GCS Bucket
- **Bucket**: `gblackautomation-veo-videos`
- **Region**: us-central1
- **Input images**: `gs://.../veo-images/`
- **Generated videos**: `gs://.../generated-videos/`

---

## Next Steps

### Update Veo Agent Skill
Update `C:/Users/gblac/.claude/global/skills/veo-agent/SKILL.md` to:
- Document Vertex AI endpoint requirement
- Explain difference between Gemini API and Vertex AI
- Provide working examples with service account auth
- Note that operation polling doesn't work (use bucket checking instead)

### Integration
- ✅ Video ready for parallax animation on project overview page
- Add to consulting-page-01.html as background video
- Implement parallax scrolling effect with video

### Cleanup
Consider GCS lifecycle policy to auto-delete old videos:
```bash
gsutil lifecycle set lifecycle.json gs://gblackautomation-veo-videos/
```

---

## Troubleshooting

### Error: "gcsUri isn't supported by this model"
**Cause**: Using Gemini API endpoint
**Fix**: Switch to Vertex AI endpoint

### Error: "bytesBase64 isn't supported"
**Cause**: Using Gemini API endpoint
**Fix**: Switch to Vertex AI endpoint and use GCS URIs

### Error: "The Operation ID must be a Long, but was instead: {UUID}"
**Cause**: Trying to poll operation with standard operations endpoint
**Fix**: Check GCS bucket directly for output video instead of polling

### Error: "Permission denied on GCS bucket"
**Cause**: Service account lacks permissions
**Fix**: Grant Storage Object Admin role to service account

---

## References

- [Vertex AI Video Generation](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames)
- [Veo 3.1 Model Card](https://ai.google.dev/gemini-api/docs/models/veo)
- [Service Account Authentication](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [Google Cloud Storage Python Client](https://cloud.google.com/python/docs/reference/storage/latest)

---

**Status**: ✅ Fully working implementation
**Generated**: option7_parallax_veo.mp4 (2.97 MB)
**API**: Vertex AI `veo-3.1-generate-001`
**Endpoint**: `us-central1-aiplatform.googleapis.com`
