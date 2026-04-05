#!/bin/bash
# Veo 3.1 GCS Quick Setup Script

set -e

echo "🎬 Veo 3.1 with Google Cloud Storage - Quick Setup"
echo "=================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo "✅ gcloud CLI installed"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    exit 1
fi
echo "✅ Python installed"

# Install Python packages
echo ""
echo "📦 Installing Python packages..."
pip install google-cloud-storage requests --quiet
echo "✅ Packages installed"

# Authenticate
echo ""
echo "🔐 Authenticating with Google Cloud..."
echo "This will open a browser window for authentication..."
gcloud auth application-default login

# Get or set project
echo ""
echo "📋 Setting up GCP project..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$CURRENT_PROJECT" ]; then
    echo "No project set. Please enter your GCP project ID:"
    read -r PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    echo "Current project: $CURRENT_PROJECT"
    echo "Use this project? (y/n)"
    read -r USE_PROJECT
    if [ "$USE_PROJECT" != "y" ]; then
        echo "Enter new project ID:"
        read -r PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    else
        PROJECT_ID=$CURRENT_PROJECT
    fi
fi

echo "✅ Project set: $PROJECT_ID"

# Create bucket
echo ""
echo "🪣 Creating GCS bucket..."
BUCKET_NAME="veo-video-gen-$(date +%s)"
echo "Bucket name: $BUCKET_NAME"

gsutil mb gs://$BUCKET_NAME/
echo "✅ Bucket created: gs://$BUCKET_NAME/"

# Set lifecycle
echo ""
echo "⏰ Setting up auto-cleanup (7-day retention)..."
cat > /tmp/lifecycle.json <<EOF
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

gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME/
rm /tmp/lifecycle.json
echo "✅ Lifecycle policy set"

# Save to .env
echo ""
echo "💾 Saving configuration..."

ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

# Add or update variables
if grep -q "VEO_GCS_BUCKET" "$ENV_FILE"; then
    sed -i.bak "s|VEO_GCS_BUCKET=.*|VEO_GCS_BUCKET=$BUCKET_NAME|" "$ENV_FILE"
else
    echo "VEO_GCS_BUCKET=$BUCKET_NAME" >> "$ENV_FILE"
fi

if grep -q "GCP_PROJECT_ID" "$ENV_FILE"; then
    sed -i.bak "s|GCP_PROJECT_ID=.*|GCP_PROJECT_ID=$PROJECT_ID|" "$ENV_FILE"
else
    echo "GCP_PROJECT_ID=$PROJECT_ID" >> "$ENV_FILE"
fi

echo "✅ Configuration saved to $ENV_FILE"

# Test upload
echo ""
echo "🧪 Running test upload..."

# Create test file
echo "Test image for Veo 3.1" > /tmp/veo_test.txt

python3 <<EOF
import os
os.environ['VEO_GCS_BUCKET'] = '$BUCKET_NAME'
os.environ['GCP_PROJECT_ID'] = '$PROJECT_ID'

import sys
sys.path.insert(0, 'C:/Users/gblac/.claude/global/skills/veo-agent/scripts')

from upload_to_gcs import upload_to_gcs

gcs_uri = upload_to_gcs(
    local_path='/tmp/veo_test.txt',
    bucket_name='$BUCKET_NAME',
    destination_blob_name='test/veo_test.txt'
)
print(f"\n✅ Test upload successful!")
print(f"GCS URI: {gcs_uri}")
EOF

# Cleanup test file
gsutil rm gs://$BUCKET_NAME/test/veo_test.txt
rm /tmp/veo_test.txt

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Your configuration:"
echo "  GCP Project: $PROJECT_ID"
echo "  GCS Bucket: $BUCKET_NAME"
echo ""
echo "Environment variables saved to: $ENV_FILE"
echo ""
echo "Next steps:"
echo "  1. Generate video:"
echo "     python scripts/interpolate_frames_gcs.py \\"
echo "       frame1.png frame2.png \"Prompt\" \\"
echo "       --bucket $BUCKET_NAME"
echo ""
echo "  2. See full guide:"
echo "     cat .claude/context/VEO_GCS_SETUP_GUIDE.md"
echo ""
