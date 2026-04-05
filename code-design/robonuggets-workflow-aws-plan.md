# AI Video Generation Workflow - Production Implementation Plan

## Overview

Recreate the RoboNuggets AI video generation workflow (from transcript) with Obsidian as the UI, AWS backend, and production-ready features. The workflow generates cinematic video ads using:
- **Prompt Generation**: Claude Sonnet 4.5 ($0.15/scene)
- **Image Generation**: Nano Banana Pro via API ($0.15/image)
- **Video Generation**: V3.1 via key.ai ($0.30/8-sec clip)
- **Audio Generation**: Suno ($0.06/music), 11 Labs ($0.10/voiceover)

**Total Cost per Scene**: ~$0.91 | **30-sec video (4 scenes)**: ~$3.64

---

## System Architecture

```
Obsidian Note (Frontmatter + Webhooks)
    ↓ POST https://api.robonuggets.example.com/v1/projects/{id}/start
AWS API Gateway (IAM Auth + Rate Limiting)
    ↓
AWS Step Functions (Orchestration + Human-in-Loop)
    ├─→ Lambda: Prompt Generator (Claude)
    ├─→ Lambda: Image Generator (Nano Banana Pro)
    ├─→ Lambda: Video Generator (V3.1)
    ├─→ Lambda: Audio Generator (Suno + 11 Labs)
    └─→ Lambda: Approval Handler (Wait States)
    ↓
AWS S3 (Versioned Media Storage) + Supabase (Metadata + State)
    ↓
Obsidian Note Updates (Signed URLs, Cost Tracking, Approvals)
```

---

## Implementation Phases

### Phase 1: Database & Security Foundation

#### 1.1 Supabase Database Schema

Create 6 tables in Supabase PostgreSQL:

**File**: `.claude/skills/robonuggets-workflow/database/schema.sql`

```sql
-- 1. video_projects (master project records)
CREATE TABLE video_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    obsidian_note_path TEXT NOT NULL,
    project_name TEXT NOT NULL,
    creative_direction TEXT NOT NULL,
    elements_board_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    workflow_state TEXT,  -- Step Function execution ARN
    total_estimated_cost_usd DECIMAL(10,4) DEFAULT 0,
    total_actual_cost_usd DECIMAL(10,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 2. video_scenes (one project has multiple scenes)
CREATE TABLE video_scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES video_projects(id) ON DELETE CASCADE,
    scene_number INT NOT NULL,
    scene_title TEXT,
    prompt_artifact_id UUID,
    start_image_artifact_id UUID,
    end_image_artifact_id UUID,
    video_artifact_id UUID,
    audio_artifact_id UUID,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(project_id, scene_number)
);

-- 3. video_artifacts (versioned storage references)
CREATE TABLE video_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scene_id UUID REFERENCES video_scenes(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,  -- prompt, image_start, image_end, video, audio_music, audio_voice
    version INT NOT NULL DEFAULT 1,
    s3_bucket TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    s3_version_id TEXT,
    file_size_bytes BIGINT,
    content_type TEXT,
    ai_provider TEXT,  -- claude, nano-banana-pro, v3.1, suno, elevenlabs
    ai_model TEXT,
    prompt_used TEXT,
    generation_params JSONB,
    cost_usd DECIMAL(10,4),
    tokens_input INT,
    tokens_output INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(scene_id, artifact_type, version)
);

-- 4. workflow_approvals (human-in-loop gates)
CREATE TABLE workflow_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES video_projects(id) ON DELETE CASCADE,
    scene_id UUID REFERENCES video_scenes(id) ON DELETE SET NULL,
    approval_stage TEXT NOT NULL,  -- prompts, images, video, audio
    status TEXT NOT NULL DEFAULT 'pending',
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    request_payload JSONB,
    approved_at TIMESTAMPTZ,
    approved_by TEXT,
    approval_notes TEXT,
    response_payload JSONB,
    webhook_callback_url TEXT,
    obsidian_note_updated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. workflow_cost_tracking (per-operation cost logging)
CREATE TABLE workflow_cost_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES video_projects(id) ON DELETE CASCADE,
    scene_id UUID REFERENCES video_scenes(id) ON DELETE SET NULL,
    operation_type TEXT NOT NULL,  -- prompt_gen, image_gen, video_gen, audio_gen
    ai_provider TEXT NOT NULL,
    ai_model TEXT,
    cost_usd DECIMAL(10,4) NOT NULL,
    tokens_input INT,
    tokens_output INT,
    units_consumed DECIMAL(10,2),
    execution_duration_ms INT,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 6. video_workflow_secrets (KMS-encrypted API keys)
CREATE TABLE video_workflow_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_key TEXT UNIQUE NOT NULL,  -- NANO_BANANA_API_KEY, V31_API_KEY, etc
    secret_value_encrypted TEXT NOT NULL,
    kms_key_arn TEXT NOT NULL,
    provider TEXT,  -- nano-banana, v3.1, suno, elevenlabs, claude
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_rotated_at TIMESTAMPTZ
);

CREATE INDEX idx_video_projects_status ON video_projects(status);
CREATE INDEX idx_video_scenes_project ON video_scenes(project_id, scene_number);
CREATE INDEX idx_video_artifacts_scene ON video_artifacts(scene_id, artifact_type);
CREATE INDEX idx_workflow_approvals_status ON workflow_approvals(status, requested_at);
CREATE INDEX idx_workflow_cost_project ON workflow_cost_tracking(project_id, created_at DESC);
```

#### 1.2 KMS Encryption Setup

**Reference**: `.claude/context/setup/kms_encryption_utils.py`

Store encrypted API keys in Supabase:

```python
from kms_encryption_utils import KMSEncryption

kms = KMSEncryption()

# Encrypt and store each API key
api_keys = {
    'NANO_BANANA_API_KEY': os.getenv('NANO_BANANA_API_KEY'),
    'V31_API_KEY': os.getenv('V31_API_KEY'),
    'SUNO_API_KEY': os.getenv('SUNO_API_KEY'),
    'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
    'CLAUDE_API_KEY': os.getenv('ANTHROPIC_API_KEY')
}

for key_name, key_value in api_keys.items():
    encrypted = kms.encrypt_api_key(key_value)
    supabase.table('video_workflow_secrets').insert({
        'secret_key': key_name,
        'secret_value_encrypted': encrypted,
        'kms_key_arn': kms.api_keys_arn,
        'provider': key_name.split('_')[0].lower()
    }).execute()
```

---

### Phase 2: AWS Infrastructure Setup

#### 2.1 S3 Buckets (with Versioning)

**File**: `.claude/skills/robonuggets-workflow/infrastructure/s3-buckets.yaml`

```yaml
Buckets:
  - Name: robonuggets-inputs-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256

  - Name: robonuggets-prompts-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256
    LifecyclePolicy:
      - TransitionToIA: 30 days
      - Expire: 180 days (keep 3 versions)

  - Name: robonuggets-images-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256

  - Name: robonuggets-videos-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256

  - Name: robonuggets-audio-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256

  - Name: robonuggets-outputs-{account-id}-us-east-1
    Versioning: Enabled
    Encryption: AES256
```

**Versioning Strategy**:
```
projects/{project_id}/scenes/{scene_number}/
  ├── prompts/v1.json, v2.json
  ├── images/start_v1.png, start_v2.png, end_v1.png
  ├── videos/clip_v1.mp4
  └── audio/music_v1.mp3, voice_v1.mp3
```

#### 2.2 Lambda Functions

**Structure**:
```
.claude/skills/robonuggets-workflow/lambda/
├── prompt-generator/
│   ├── handler.py
│   ├── requirements.txt
│   └── Dockerfile
├── image-generator/
│   ├── handler.py
│   ├── requirements.txt
│   └── Dockerfile
├── video-generator/
│   ├── handler.py
│   ├── requirements.txt
│   └── Dockerfile
├── audio-generator/
│   ├── handler.py
│   ├── requirements.txt
│   └── Dockerfile
└── approval-handler/
    ├── handler.py
    ├── requirements.txt
    └── Dockerfile
```

**Lambda 1: Prompt Generator** (`prompt-generator/handler.py`)

```python
import json
import boto3
import os
from anthropic import Anthropic
from supabase import create_client
from kms_encryption_utils import KMSEncryption

def lambda_handler(event, context):
    """
    Generate prompts using Claude Sonnet 4.5

    Input: {project_id, scene_id, creative_direction}
    Output: {scene_id, prompts: {image_start, image_end, video_transition, audio_music, audio_voice_script}, artifact_id, cost_usd}
    """

    # Decrypt API keys
    kms = KMSEncryption()
    anthropic_key = get_secret('CLAUDE_API_KEY', kms)
    supabase_key = get_secret('SUPABASE_SERVICE_KEY', kms)

    # Initialize clients
    anthropic = Anthropic(api_key=anthropic_key)
    supabase = create_client(os.environ['SUPABASE_URL'], supabase_key)
    s3 = boto3.client('s3')

    # Extract input
    project_id = event['project_id']
    scene_id = event['scene_id']
    creative_direction = event['creative_direction']

    # Call Claude
    response = anthropic.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        system=PROMPT_GENERATION_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Creative Direction: {creative_direction}\n\nGenerate structured prompts for scene."
        }]
    )

    prompts = json.loads(response.content[0].text)

    # Store in S3
    s3_key = f"projects/{project_id}/scenes/{scene_id}/prompts/v1.json"
    s3.put_object(
        Bucket=os.environ['S3_BUCKET_PROMPTS'],
        Key=s3_key,
        Body=json.dumps(prompts),
        ContentType='application/json',
        ServerSideEncryption='AES256'
    )

    # Create artifact record
    artifact = supabase.table('video_artifacts').insert({
        'scene_id': scene_id,
        'artifact_type': 'prompt',
        'version': 1,
        's3_bucket': os.environ['S3_BUCKET_PROMPTS'],
        's3_key': s3_key,
        'ai_provider': 'claude',
        'ai_model': 'claude-sonnet-4-5',
        'cost_usd': calculate_cost(response),
        'tokens_input': response.usage.input_tokens,
        'tokens_output': response.usage.output_tokens
    }).execute()

    # Track cost
    supabase.table('workflow_cost_tracking').insert({
        'project_id': project_id,
        'scene_id': scene_id,
        'operation_type': 'prompt_gen',
        'ai_provider': 'claude',
        'cost_usd': calculate_cost(response),
        'status': 'success'
    }).execute()

    return {
        'statusCode': 200,
        'body': {
            'scene_id': scene_id,
            'prompts': prompts,
            'artifact_id': artifact.data[0]['id'],
            'cost_usd': calculate_cost(response)
        }
    }

PROMPT_GENERATION_SYSTEM_PROMPT = """
You are a video production AI assistant generating detailed prompts for image/video/audio generation.

Given a creative direction, generate JSON with these fields:
{
  "image_start": "Detailed image prompt for starting frame (describe composition, lighting, camera angle, subject, environment)",
  "image_end": "Detailed image prompt for ending frame",
  "video_transition": "Describe motion/transition from start to end (camera movement, subject action)",
  "audio_music": "Music style and mood description (genre, tempo, instruments, emotion)",
  "audio_voice_script": "Voiceover script (30-50 words, engaging narrative)"
}

Use cinematic language. Be specific about visual details.
"""

def get_secret(key_name, kms):
    """Retrieve and decrypt secret from Supabase"""
    result = supabase.table('video_workflow_secrets').select('secret_value_encrypted').eq('secret_key', key_name).single().execute()
    return kms.decrypt(result.data['secret_value_encrypted'])

def calculate_cost(response):
    """Calculate Claude API cost"""
    input_cost = (response.usage.input_tokens / 1_000_000) * 3.00
    output_cost = (response.usage.output_tokens / 1_000_000) * 15.00
    return round(input_cost + output_cost, 4)
```

**Lambda 2: Image Generator** (`image-generator/handler.py`)

```python
import json
import boto3
import requests
from kms_encryption_utils import KMSEncryption

def lambda_handler(event, context):
    """
    Generate images using Nano Banana Pro API

    Input: {scene_id, prompt, image_type: 'start' | 'end'}
    Output: {scene_id, image_type, artifact_id, s3_url, cost_usd}
    """

    kms = KMSEncryption()
    nano_key = get_secret('NANO_BANANA_API_KEY', kms)

    scene_id = event['scene_id']
    prompt = event['prompt']
    image_type = event['image_type']  # 'start' or 'end'

    # Call Nano Banana Pro API
    response = requests.post(
        'https://api.nanobananapro.com/v1/generate',
        headers={'Authorization': f'Bearer {nano_key}'},
        json={
            'prompt': prompt,
            'width': 1920,
            'height': 1080,
            'quality': 'high'
        }
    )

    result = response.json()
    image_url = result['image_url']

    # Download image
    image_data = requests.get(image_url).content

    # Upload to S3
    s3_key = f"projects/{project_id}/scenes/{scene_id}/images/{image_type}_v1.png"
    s3.put_object(
        Bucket=os.environ['S3_BUCKET_IMAGES'],
        Key=s3_key,
        Body=image_data,
        ContentType='image/png',
        ServerSideEncryption='AES256'
    )

    # Create artifact record
    artifact = supabase.table('video_artifacts').insert({
        'scene_id': scene_id,
        'artifact_type': f'image_{image_type}',
        'version': 1,
        's3_bucket': os.environ['S3_BUCKET_IMAGES'],
        's3_key': s3_key,
        'ai_provider': 'nano-banana-pro',
        'cost_usd': 0.15
    }).execute()

    return {
        'statusCode': 200,
        'body': {
            'scene_id': scene_id,
            'image_type': image_type,
            'artifact_id': artifact.data[0]['id'],
            'cost_usd': 0.15
        }
    }
```

**Lambda 3: Video Generator** (`video-generator/handler.py`)

```python
import time
import requests
from kms_encryption_utils import KMSEncryption

def lambda_handler(event, context):
    """
    Generate video using V3.1 API (via key.ai)

    Input: {scene_id, start_image_s3_key, end_image_s3_key, transition_prompt}
    Output: {scene_id, artifact_id, video_s3_url, cost_usd}
    """

    kms = KMSEncryption()
    v31_key = get_secret('V31_API_KEY', kms)

    # Generate signed URLs for images
    start_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': start_key}, ExpiresIn=3600)
    end_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': end_key}, ExpiresIn=3600)

    # Call V3.1 API (via key.ai)
    response = requests.post(
        'https://api.key.ai/v3.1/generate',
        headers={'Authorization': f'Bearer {v31_key}'},
        json={
            'start_image_url': start_url,
            'end_image_url': end_url,
            'prompt': event['transition_prompt'],
            'duration': 8,  # seconds
            'quality': 'fast'  # v3.1-fast ($0.30)
        }
    )

    job_id = response.json()['job_id']

    # Poll for completion (exponential backoff)
    for attempt in range(30):  # Max 15 minutes
        time.sleep(2 ** min(attempt // 3, 6))  # 1s, 1s, 1s, 2s, 2s, 2s, 4s...

        status_response = requests.get(
            f'https://api.key.ai/v3.1/status/{job_id}',
            headers={'Authorization': f'Bearer {v31_key}'}
        )

        status = status_response.json()
        if status['status'] == 'completed':
            video_url = status['video_url']
            break
    else:
        raise Exception('Video generation timeout')

    # Download and upload to S3
    video_data = requests.get(video_url).content
    s3_key = f"projects/{project_id}/scenes/{scene_id}/videos/clip_v1.mp4"
    s3.put_object(Bucket=os.environ['S3_BUCKET_VIDEOS'], Key=s3_key, Body=video_data)

    # Create artifact
    artifact = supabase.table('video_artifacts').insert({
        'scene_id': scene_id,
        'artifact_type': 'video',
        's3_key': s3_key,
        'ai_provider': 'v3.1',
        'cost_usd': 0.30
    }).execute()

    return {'statusCode': 200, 'body': {'artifact_id': artifact.data[0]['id'], 'cost_usd': 0.30}}
```

**Lambda 4: Audio Generator** (`audio-generator/handler.py`)

Similar pattern for Suno (music) and 11 Labs (voiceover).

**Lambda 5: Approval Handler** (`approval-handler/handler.py`)

```python
def lambda_handler(event, context):
    """
    Create approval request and return task token for Step Functions

    Input: {approval_stage, project_id, artifact_ids, task_token}
    Output: Creates approval record, returns when approved/rejected
    """

    # Create approval record
    approval = supabase.table('workflow_approvals').insert({
        'project_id': event['project_id'],
        'scene_id': event.get('scene_id'),
        'approval_stage': event['approval_stage'],
        'status': 'pending',
        'request_payload': {'artifact_ids': event['artifact_ids']},
        'expires_at': datetime.now() + timedelta(days=1)
    }).execute()

    # Store task token for callback
    approval_id = approval.data[0]['id']

    # Update Obsidian note with approval request (webhook callback)
    # This is handled by separate process that polls for pending approvals

    # Step Function will wait here until callback with task token
    return {'approval_id': approval_id}
```

#### 2.3 Step Functions State Machine

**File**: `.claude/skills/robonuggets-workflow/infrastructure/step-functions.json`

```json
{
  "Comment": "RoboNuggets Video Generation Workflow",
  "StartAt": "Generate Prompts",
  "States": {
    "Generate Prompts": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:ACCOUNT:function:robonuggets-prompt-generator",
      "ResultPath": "$.promptResult",
      "Next": "Request Prompt Approval",
      "Retry": [{
        "ErrorEquals": ["States.TaskFailed"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }]
    },

    "Request Prompt Approval": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "robonuggets-approval-handler",
        "Payload": {
          "approval_stage": "prompts",
          "project_id.$": "$.project_id",
          "artifact_id.$": "$.promptResult.artifact_id",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "Check Prompt Approval",
      "TimeoutSeconds": 86400
    },

    "Check Prompt Approval": {
      "Type": "Choice",
      "Choices": [{
        "Variable": "$.approvalStatus",
        "StringEquals": "approved",
        "Next": "Generate Images Parallel"
      }, {
        "Variable": "$.approvalStatus",
        "StringEquals": "rejected",
        "Next": "Generate Prompts"
      }],
      "Default": "Workflow Failed"
    },

    "Generate Images Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "Generate Start Image",
          "States": {
            "Generate Start Image": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:ACCOUNT:function:robonuggets-image-generator",
              "Parameters": {
                "scene_id.$": "$.scene_id",
                "prompt.$": "$.promptResult.prompts.image_start",
                "image_type": "start"
              },
              "End": true
            }
          }
        },
        {
          "StartAt": "Generate End Image",
          "States": {
            "Generate End Image": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:ACCOUNT:function:robonuggets-image-generator",
              "Parameters": {
                "scene_id.$": "$.scene_id",
                "prompt.$": "$.promptResult.prompts.image_end",
                "image_type": "end"
              },
              "End": true
            }
          }
        }
      ],
      "ResultPath": "$.imageResults",
      "Next": "Request Image Approval"
    },

    "Request Image Approval": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
      "Parameters": {
        "FunctionName": "robonuggets-approval-handler",
        "Payload": {
          "approval_stage": "images",
          "artifact_ids.$": "$.imageResults",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "Generate Video"
    },

    "Generate Video": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:ACCOUNT:function:robonuggets-video-generator",
      "Next": "Generate Audio Parallel"
    },

    "Generate Audio Parallel": {
      "Type": "Parallel",
      "Branches": [
        {"StartAt": "Generate Music", "States": {"Generate Music": {"Type": "Task", "Resource": "arn:aws:lambda::function:robonuggets-audio-generator", "End": true}}},
        {"StartAt": "Generate Voice", "States": {"Generate Voice": {"Type": "Task", "Resource": "arn:aws:lambda::function:robonuggets-audio-generator", "End": true}}}
      ],
      "End": true
    },

    "Workflow Failed": {
      "Type": "Fail",
      "Error": "WorkflowFailed"
    }
  }
}
```

#### 2.4 API Gateway

**File**: `.claude/skills/robonuggets-workflow/infrastructure/api-gateway.yaml`

```yaml
Resources:
  RoboNuggetsAPI:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: robonuggets-workflow-api
      Description: API for RoboNuggets video generation workflow

  ProjectsResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RoboNuggetsAPI
      ParentId: !GetAtt RoboNuggetsAPI.RootResourceId
      PathPart: projects

  CreateProjectMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RoboNuggetsAPI
      ResourceId: !Ref ProjectsResource
      HttpMethod: POST
      AuthorizationType: AWS_IAM
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${CreateProjectFunction.Arn}/invocations

  UsagePlan:
    Type: AWS::ApiGateway::UsagePlan
    Properties:
      UsagePlanName: robonuggets-standard
      Throttle:
        RateLimit: 100
        BurstLimit: 200
      Quota:
        Limit: 10000
        Period: MONTH
```

**Endpoints**:
- `POST /v1/projects` - Create project
- `POST /v1/projects/{id}/start` - Start workflow
- `GET /v1/projects/{id}/status` - Get status
- `POST /v1/approvals/{id}` - Submit approval
- `GET /v1/artifacts/{id}/presigned` - Get signed S3 URL

---

### Phase 3: Obsidian Integration

#### 3.1 Obsidian Note Template

**File**: `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\templates\robonuggets-project.md`

```markdown
---
type: robonuggets-project
project_id: {{UUID}}
status: draft
created: {{date}}
webhook_base_url: https://api.robonuggets.example.com/v1
api_key: {{OBSIDIAN_API_KEY}}
total_cost_usd: 0
scenes_count: 4
---

# {{project_name}}

## Creative Direction

{{creative_direction}}

## Workflow Controls

```dataview
button start-workflow "🚀 Start Workflow"
  POST {{webhook_base_url}}/projects/{{project_id}}/start
  headers: {"X-API-Key": "{{api_key}}"}
```

```dataview
button check-status "📊 Check Status"
  GET {{webhook_base_url}}/projects/{{project_id}}/status
  headers: {"X-API-Key": "{{api_key}}"}
```

## Current Status

**Stage**: {{current_stage}}
**Cost**: ${{total_cost_usd}}
**Pending Approvals**: {{pending_approvals_count}}

## Scene 1

### Prompts (v1)

**Image Start**: {{scene_1_prompt_start}}
**Image End**: {{scene_1_prompt_end}}
**Transition**: {{scene_1_prompt_transition}}

```dataview
button approve-prompts "✅ Approve"
  POST {{webhook_base_url}}/approvals/{{scene_1_approval_id}}
  body: {"status": "approved"}
```

```dataview
button reject-prompts "🔄 Regenerate"
  POST {{webhook_base_url}}/approvals/{{scene_1_approval_id}}
  body: {"status": "rejected", "regenerate": true}
```

### Generated Images

![Start]({{scene_1_image_start_url}})
![End]({{scene_1_image_end_url}})

### Generated Video

<video controls src="{{scene_1_video_url}}"></video>

### Cost Breakdown

| Stage | Cost |
|-------|------|
| Prompts | ${{cost_prompts}} |
| Images | ${{cost_images}} |
| Video | ${{cost_video}} |
| Audio | ${{cost_audio}} |
| **Total** | **${{total_cost}}** |
```

#### 3.2 Webhook Plugin Configuration

**File**: `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\.obsidian\plugins\obsidian-webhooks\config.json`

```json
{
  "webhooks": [
    {
      "name": "Start Workflow",
      "method": "POST",
      "url": "{{webhook_base_url}}/projects/{{project_id}}/start",
      "headers": {
        "X-API-Key": "{{api_key}}",
        "Content-Type": "application/json"
      },
      "onSuccess": {
        "action": "update_frontmatter",
        "fields": {"status": "in_progress"}
      }
    }
  ],
  "auto_refresh": {
    "enabled": true,
    "interval": 30000,
    "endpoints": ["/projects/{{project_id}}/status"]
  }
}
```

---

### Phase 4: Deployment & Testing

#### 4.1 Deployment Script

**File**: `.claude/skills/robonuggets-workflow/deploy.sh`

```bash
#!/bin/bash

# 1. Deploy Supabase schema
psql $DATABASE_URL < database/schema.sql

# 2. Encrypt and store API keys
python scripts/setup_secrets.py

# 3. Deploy S3 buckets
aws cloudformation deploy --template-file infrastructure/s3-buckets.yaml --stack-name robonuggets-s3

# 4. Deploy Lambda functions
for lambda in prompt-generator image-generator video-generator audio-generator approval-handler; do
  cd lambda/$lambda
  docker build -t robonuggets-$lambda .
  aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
  docker tag robonuggets-$lambda $ECR_REGISTRY/robonuggets-$lambda:latest
  docker push $ECR_REGISTRY/robonuggets-$lambda:latest
  aws lambda update-function-code --function-name robonuggets-$lambda --image-uri $ECR_REGISTRY/robonuggets-$lambda:latest
  cd ../..
done

# 5. Deploy Step Functions
aws stepfunctions create-state-machine --definition file://infrastructure/step-functions.json --name RoboNuggetsWorkflow --role-arn $STEP_FUNCTIONS_ROLE

# 6. Deploy API Gateway
aws cloudformation deploy --template-file infrastructure/api-gateway.yaml --stack-name robonuggets-api
```

#### 4.2 Testing Checklist

- [ ] **Unit Tests**: Lambda functions (pytest)
- [ ] **Integration Tests**: Step Functions execution
- [ ] **E2E Test**: Obsidian → API Gateway → Lambda → S3 → Obsidian
- [ ] **Cost Tracking**: Verify costs logged in Supabase
- [ ] **Approval Flow**: Test human-in-loop gates
- [ ] **Error Handling**: Test retry logic, DLQ
- [ ] **Versioning**: Create v2 of artifact, verify S3 versioning

---

## Critical Files to Reference

1. **KMS Encryption**: `.claude/context/setup/kms_encryption_utils.py`
2. **AWS Templates**: `.claude/skills/revstar-quickstart-workflow/assets/aws-services-template.yaml`
3. **Supabase Client**: `.claude/skills/youtube-video-archiver/scripts/supabase_client.py`
4. **Human-in-Loop Pattern**: `quickstarts/quickstart-nexus-claude/hooks/utils/hitl.py`
5. **FastAPI Backend** (reference): `.claude/orchestrator/orchestrator_3_stream/backend/main.py`

---

## Implementation Order

1. **Database** → Create Supabase tables
2. **Secrets** → Encrypt API keys with KMS, store in Supabase
3. **S3** → Create buckets with versioning
4. **Lambda** → Deploy all 5 functions
5. **Step Functions** → Create state machine
6. **API Gateway** → Deploy REST API
7. **Obsidian** → Create template and webhook config
8. **Test** → End-to-end workflow test
9. **Monitor** → CloudWatch dashboards, Langfuse traces

---

## Cost Estimates

**Per 30-second video (4 scenes)**:
- Prompts: $0.60 (4 scenes × $0.15)
- Images: $1.20 (8 images × $0.15)
- Videos: $1.20 (4 clips × $0.30)
- Audio: $0.64 (4 music + 4 voice)
- **Total**: ~$3.64

**AWS Monthly** (100 videos/month): ~$4
**AI Providers Monthly**: ~$364

**Total**: ~$368/month for 100 videos

---

## Next Steps After Approval

1. Create directory structure: `.claude/skills/robonuggets-workflow/`
2. Write database schema SQL
3. Implement Lambda functions (5 files)
4. Create Step Functions state machine JSON
5. Write API Gateway CloudFormation template
6. Create Obsidian template
7. Write deployment scripts
8. Create test suite
9. Deploy to AWS
10. Test end-to-end workflow
