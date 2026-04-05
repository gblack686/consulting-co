# Veo 3.1 with Google Cloud Storage - Complete Setup Guide

## Overview

This guide walks you through the complete setup for using Veo 3.1 with Google Cloud Storage for frame interpolation and video generation.

**Date**: December 13, 2025

---

## Prerequisites

1. **Google Cloud Platform Account**
   - Sign up at: https://cloud.google.com/
   - Free tier includes $300 credit

2. **Google Cloud SDK (gcloud)**
   - Download: https://cloud.google.com/sdk/docs/install
   - Verify installation: `gcloud --version`

3. **Python Packages**
   ```bash
   pip install google-cloud-storage requests
   ```

4. **API Keys**
   - Gemini API key from: https://aistudio.google.com/apikey
   - Set in .env: `GEMINI_API_KEY=your_key_here`

---

## Step 1: Google Cloud Authentication

### Option A: Application Default Credentials (Recommended)

```bash
# Login to Google Cloud
gcloud auth application-default login
```

This opens a browser window for authentication.

### Option B: Service Account (For Production)

```bash
# Create service account
gcloud iam service-accounts create veo-agent \
    --display-name="Veo Video Generation Agent"

# Download key file
gcloud iam service-accounts keys create ~/veo-agent-key.json \
    --iam-account=veo-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/veo-agent-key.json
```

---

## Step 2: Create Google Cloud Storage Bucket

### Create Bucket

```bash
# Set project ID
export GCP_PROJECT_ID=your-project-id
gcloud config set project $GCP_PROJECT_ID

# Create bucket (replace with unique name)
export VEO_GCS_BUCKET=veo-video-generation-$(date +%s)
gsutil mb gs://$VEO_GCS_BUCKET/

# Verify bucket created
gsutil ls gs://$VEO_GCS_BUCKET/
```

### Set Bucket Lifecycle (Auto-delete after 7 days)

```bash
# Create lifecycle config
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 7
        }
      }
    ]
  }
}
EOF

# Apply lifecycle
gsutil lifecycle set lifecycle.json gs://$VEO_GCS_BUCKET/
```

### Set Bucket Permissions

```bash
# Make bucket private (recommended)
gsutil iam ch allUsers:objectViewer gs://$VEO_GCS_BUCKET/

# Or keep private (you control access)
# No additional commands needed - default is private
```

---

## Step 3: Set Environment Variables

Add to your `.env` file:

```bash
# Google Cloud
export GCP_PROJECT_ID=your-project-id
export VEO_GCS_BUCKET=your-bucket-name

# Gemini API
export GEMINI_API_KEY=your-gemini-api-key

# Optional: Service account key
export GOOGLE_APPLICATION_CREDENTIALS=~/veo-agent-key.json
```

Or in Windows `.env`:
```
GCP_PROJECT_ID=your-project-id
VEO_GCS_BUCKET=your-bucket-name
GEMINI_API_KEY=your-gemini-api-key
```

---

## Step 4: Test the Setup

### Test 1: Upload Image to GCS

```bash
cd "C:/Users/gblac/OneDrive/Desktop/consulting-co"

python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/upload_to_gcs.py" \
  option7_start.png \
  --bucket $VEO_GCS_BUCKET
```

**Expected Output**:
```
✅ Upload successful!
📦 GCS URI: gs://your-bucket/veo-images/option7_start.png
```

### Test 2: List Bucket Contents

```bash
gsutil ls gs://$VEO_GCS_BUCKET/veo-images/
```

### Test 3: Download from GCS

```bash
python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/download_from_gcs.py" \
  gs://$VEO_GCS_BUCKET/veo-images/option7_start.png \
  --output test_download.png
```

---

## Step 5: Generate Video (Full Workflow)

### Upload Frames and Generate Video

```bash
cd "C:/Users/gblac/OneDrive/Desktop/consulting-co"

# Generate video from Option 7 frames
python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/interpolate_frames_gcs.py" \
  option7_start.png \
  option7_end.png \
  "NEURAL-01 Generalist robot at workbench from side angle, smooth hammer motion from mid-swing to lowered position, subtle parallax camera movement, cream background with shallow depth of field, professional cinematic look" \
  --bucket $VEO_GCS_BUCKET \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --output option7_parallax_video.mp4
```

**What Happens**:
1. ✅ Uploads option7_start.png to GCS
2. ✅ Uploads option7_end.png to GCS
3. ✅ Calls Veo 3.1 API with GCS URIs
4. ✅ Polls for completion (1-5 minutes)
5. ✅ Returns GCS URI for generated video
6. ✅ Saves metadata JSON

### Download Generated Video

```bash
# Using metadata file
python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/download_from_gcs.py" \
  --metadata option7_parallax_video.json \
  --output option7_parallax_video.mp4

# Or directly with GCS URI
python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/download_from_gcs.py" \
  gs://$VEO_GCS_BUCKET/generated-videos/video-abc123.mp4 \
  --output my_video.mp4
```

---

## Complete Workflow Scripts

### Script 1: Upload Images

`scripts/upload_to_gcs.py`
- Uploads local files to GCS
- Returns GCS URIs
- Supports batch upload

### Script 2: Generate Video

`scripts/interpolate_frames_gcs.py`
- Auto-uploads local files (or uses existing GCS URIs)
- Calls Veo 3.1 API
- Polls for completion
- Returns video GCS URI

### Script 3: Download Video

`scripts/download_from_gcs.py`
- Downloads from GCS to local filesystem
- Supports metadata file input
- Shows file size and progress

---

## Workflow Examples

### Example 1: Quick Parallax Animation

```bash
# One command - auto-handles everything
python scripts/interpolate_frames_gcs.py \
  start.png end.png \
  "Smooth transition" \
  --bucket my-veo-bucket
```

### Example 2: Using Existing GCS URIs

```bash
# If files already in GCS
python scripts/interpolate_frames_gcs.py \
  gs://my-bucket/frame1.png \
  gs://my-bucket/frame2.png \
  "Transition prompt"
```

### Example 3: Batch Processing

```bash
# Upload multiple frames
python scripts/upload_to_gcs.py \
  frame1.png frame2.png frame3.png frame4.png \
  --bucket my-bucket \
  --prefix video-series/

# Generate videos
for i in {1..3}; do
  python scripts/interpolate_frames_gcs.py \
    gs://my-bucket/video-series/frame${i}.png \
    gs://my-bucket/video-series/frame$((i+1)).png \
    "Continuation of scene" \
    --output video_part${i}.mp4
done
```

---

## Cost Estimation

### Google Cloud Storage

- **Storage**: $0.020 per GB per month
- **Operations**: $0.005 per 1,000 operations
- **Typical usage**: < $1/month for hobby projects

### Veo 3.1 API

- Check current pricing at: https://ai.google.dev/pricing
- Free tier may be available

### Example Monthly Cost (Light Use)

- 100 videos @ 8 seconds each
- ~200 images uploaded
- ~100 videos downloaded
- **Estimated total**: $2-5/month

---

## Troubleshooting

### Error: "Permission Denied"

```bash
# Re-authenticate
gcloud auth application-default login

# Check permissions
gsutil iam get gs://$VEO_GCS_BUCKET/
```

### Error: "Bucket not found"

```bash
# List all buckets
gsutil ls

# Verify bucket name
echo $VEO_GCS_BUCKET
```

### Error: "google-cloud-storage not installed"

```bash
pip install google-cloud-storage
```

### Error: "Invalid API key"

```bash
# Verify API key
echo $GEMINI_API_KEY

# Get new key from: https://aistudio.google.com/apikey
```

### Video Expired (2-day retention)

```bash
# Check video still exists
gsutil ls gs://generated-videos-bucket/your-video.mp4

# If expired, regenerate video
```

---

## Cleanup

### Delete Test Files

```bash
# Delete specific files
gsutil rm gs://$VEO_GCS_BUCKET/veo-images/test*.png

# Delete entire bucket
gsutil -m rm -r gs://$VEO_GCS_BUCKET/**
gsutil rb gs://$VEO_GCS_BUCKET/
```

### Revoke Credentials

```bash
gcloud auth application-default revoke
```

---

## Production Best Practices

### 1. Use Service Accounts

Don't use personal credentials in production. Create service accounts with limited permissions.

### 2. Enable Bucket Versioning

```bash
gsutil versioning set on gs://$VEO_GCS_BUCKET/
```

### 3. Set Up Monitoring

```bash
# Enable logging
gsutil logging set on -b gs://my-logs-bucket gs://$VEO_GCS_BUCKET/
```

### 4. Implement Error Handling

Wrap API calls in try/except blocks with exponential backoff.

### 5. Automate Cleanup

Use lifecycle policies to auto-delete old files.

---

## Quick Reference Commands

**Upload**:
```bash
python scripts/upload_to_gcs.py image.png --bucket $VEO_GCS_BUCKET
```

**Generate Video**:
```bash
python scripts/interpolate_frames_gcs.py \
  start.png end.png "Prompt" --bucket $VEO_GCS_BUCKET
```

**Download**:
```bash
python scripts/download_from_gcs.py gs://bucket/video.mp4 --output video.mp4
```

**Check Bucket**:
```bash
gsutil ls -lh gs://$VEO_GCS_BUCKET/
```

---

## Next Steps

1. ✅ Complete setup (authentication, bucket creation)
2. ✅ Test upload/download workflow
3. ✅ Generate your first video
4. 📝 Document your GCS bucket name
5. 🎬 Create parallax animation from Option 7 frames
6. 🚀 Integrate into your project overview page

---

## Support Resources

- [Google Cloud Storage Docs](https://cloud.google.com/storage/docs)
- [Veo 3.1 API Docs](https://ai.google.dev/gemini-api/docs/video)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [Python Client Library](https://cloud.google.com/python/docs/reference/storage/latest)

---

**Setup Complete!** 🎉

You're now ready to generate videos with Veo 3.1 using the full GCS workflow.
