# Nano Banana + Veo Agent Skills - Complete Guide

**Location:** `C:/Users/gblac/.claude/global/skills/`

**Last Updated:** 2025-12-18

---

## Overview

Two complementary skills for AI image generation and video animation:

| Skill | Purpose | Models Used |
|-------|---------|-------------|
| `nano-banana-agent/` | Image generation, editing, blending | Gemini 2.5 Flash Image, Gemini 3 Pro Image |
| `veo-agent/` | Video generation, frame interpolation | Veo 3.1 (Vertex AI) |

**Complete Pipeline:** Generate keyframe images → Animate between them

---

## 1. Nano Banana Agent (Image Generation)

### Location
```
C:/Users/gblac/.claude/global/skills/nano-banana-agent/
```

### Scripts Available

| Script | Purpose |
|--------|---------|
| `scripts/generate_image.py` | Basic text-to-image, editing, blending |
| `scripts/generate_with_style_guide.py` | Brand-consistent generation with references |
| `scripts/interactive_generate.py` | Multi-turn iterative refinement |
| `scripts/create_style_board.py` | Create style reference directory |
| `scripts/create_color_palette.py` | Extract color palettes |

### API Keys Required

```bash
export GEMINI_API_KEY=your_gemini_api_key
# Get from: https://aistudio.google.com/apikey
```

---

## Basic Image Generation

### Simple Text-to-Image

```bash
cd "C:/Users/gblac/.claude/global/skills/nano-banana-agent"

python scripts/generate_image.py \
  "A sleek metallic robot working at a modern desk with soft golden hour lighting" \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9 \
  --size 2K \
  --output robot_desk.png
```

**Parameters:**
- `--model`:
  - `gemini-2.5-flash-image` (Fast, cheaper)
  - `gemini-3-pro-image-preview` (High quality, up to 4K, 14 reference images)
- `--aspect-ratio`: `1:1`, `16:9`, `9:16`, `4:3`, `3:2`, `21:9`
- `--size`: `1K`, `2K`, `4K` (Pro model only)
- `--output`: Output filename

---

## Image Editing (with Input Image)

```bash
python scripts/generate_image.py \
  "Add dramatic storm clouds to the sky and make the lighting more cinematic" \
  --input-images original_photo.jpg \
  --aspect-ratio 16:9 \
  --size 2K \
  --output edited_dramatic.png
```

---

## Multi-Image Blending (up to 14 images)

```bash
python scripts/generate_image.py \
  "Combine these robot characters in a futuristic laboratory setting with glass walls and holographic displays" \
  --input-images neural01.png logicx9.png architect.png \
  --aspect-ratio 16:9 \
  --size 2K \
  --output robot_team_lab.png
```

---

## Brand-Consistent Generation (Style Guide Mode)

### Setup (One-Time)

```bash
# Create style board directory with reference images
python scripts/create_style_board.py
```

This creates `style-board/` with:
- Color palette reference image
- Character reference images (NEURAL-01, LOGIC-X9, etc.)
- Style guide template

### Generate with Style Consistency

```bash
python scripts/generate_with_style_guide.py \
  "NEURAL-01 robot presenting at a tech conference" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output conference_presentation.png
```

**Style DNA Applied:**
- **Colors:** Cream (#F3F1E7), terracotta (#D97757), charcoal (#191919)
- **Aesthetic:** Minimalist, warm, glass morphism
- **Materials:** Brushed metal, polished chrome, copper accents
- **Lighting:** Soft, diffused, golden hour quality
- **Composition:** Spacious, balanced, clean backgrounds

**Parameters:**
- `--style-dir`: Style board directory (default: `style-board/`)
- `--max-references`: Max reference images to use (default: 5)

---

## Example Prompts for Robot Images

### Hero Shot
```bash
python scripts/generate_image.py \
  "NEURAL-01 Generalist robot standing heroically, dramatic side lighting, brushed metal surface with copper accents, minimalist cream background, professional product photography style, 8K detail" \
  --aspect-ratio 1:1 --size 2K --output neural01_hero.png
```

### Action Shot
```bash
python scripts/generate_image.py \
  "Sleek metallic robot using a hammer at a modern workbench, sparks flying, dramatic lighting, industrial workshop setting with warm tones, shallow depth of field" \
  --aspect-ratio 16:9 --size 2K --output robot_workshop.png
```

### Team Collaboration
```bash
python scripts/generate_image.py \
  "Three humanoid robots collaborating around a holographic display, modern glass office, soft diffused lighting, cream and terracotta color palette, professional corporate photography" \
  --aspect-ratio 16:9 --size 2K --output team_collab.png
```

### Marketing Hero Image
```bash
python scripts/generate_with_style_guide.py \
  "AI automation for modern businesses - hero image showing robots and humans working together in a bright, professional office" \
  --aspect-ratio 21:9 --size 2K --output marketing_hero.png
```

### Character Variations
```bash
# Same character, different scenes
python scripts/generate_with_style_guide.py \
  "NEURAL-01 robot working in a coffee shop, serving drinks" \
  --aspect-ratio 1:1 --output neural_coffee.png

python scripts/generate_with_style_guide.py \
  "NEURAL-01 robot in a modern gym, lifting weights" \
  --aspect-ratio 1:1 --output neural_gym.png
```

---

## 2. Veo Agent (Video Animation)

### Location
```
C:/Users/gblac/.claude/global/skills/veo-agent/
```

### Scripts Available

| Script | Purpose |
|--------|---------|
| `scripts/generate_video.py` | Text-to-video (Gemini API - simple) |
| `scripts/interpolate_frames_vertex.py` | **Frame interpolation (Vertex AI + GCS)** |
| `scripts/upload_to_gcs.py` | Upload images to GCS |
| `scripts/download_from_gcs.py` | Download videos from GCS |

### Environment Variables Required

```bash
# For Vertex AI (frame interpolation - REQUIRED)
export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/veo-agent-key.json
export GCP_PROJECT_ID=gblackautomation
export VEO_GCS_BUCKET=gblackautomation-veo-videos

# For Gemini API (text-to-video only)
export GEMINI_API_KEY=your_gemini_api_key
```

### GCS Bucket Structure

**Bucket:** `gs://gblackautomation-veo-videos`

```
gs://gblackautomation-veo-videos/
├── veo-images/              # Input frames
└── generated-videos/        # Output videos
```

---

## Simple Text-to-Video (Gemini API)

```bash
cd "C:/Users/gblac/.claude/global/skills/veo-agent"

python scripts/generate_video.py \
  "A sleek metallic robot slowly turning its head, soft studio lighting, smooth motion" \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --output robot_turn.mp4
```

**Limitations:** No frame interpolation, no reference images

---

## Frame Interpolation (Vertex AI - REQUIRED for Animation)

### Basic Usage

```bash
python scripts/interpolate_frames_vertex.py \
  start_frame.png end_frame.png \
  "Smooth parallax camera motion, subtle robot movement, cinematic lighting transition" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --aspect-ratio 16:9 \
  --output animated_robot.mp4
```

**Parameters:**
- First two args: Start and end frame image paths (or GCS URIs)
- Third arg: Motion description prompt
- `--project`: GCP project ID (gblackautomation)
- `--bucket`: GCS bucket name (gblackautomation-veo-videos)
- `--aspect-ratio`: `16:9`, `9:16`, `1:1`
- `--output`: Local output filename (optional)

**What It Does:**
1. Uploads frames to `gs://gblackautomation-veo-videos/veo-images/`
2. Calls Vertex AI Veo 3.1 endpoint
3. Polls for completion (1-5 minutes)
4. Downloads video from `gs://gblackautomation-veo-videos/generated-videos/`

---

## Example Animation Prompts

### Parallax Camera Movement

```bash
python scripts/interpolate_frames_vertex.py \
  robot_front.png robot_side.png \
  "Smooth parallax camera pan from front to side view, subtle depth movement, professional lighting maintained throughout" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output parallax_pan.mp4
```

### Hammer Swing Animation

```bash
python scripts/interpolate_frames_vertex.py \
  hammer_up.png hammer_down.png \
  "NEURAL-01 robot, fluid hammer swing motion from raised position to impact, subtle camera shake on impact, industrial workshop lighting" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output hammer_swing.mp4
```

### Head Turn

```bash
python scripts/interpolate_frames_vertex.py \
  looking_left.png looking_right.png \
  "Smooth robotic head turn, mechanical precision, subtle servo motor movement, soft studio lighting" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output head_turn.mp4
```

### Agent Photo Animation (Your Use Case)

```bash
python scripts/interpolate_frames_vertex.py \
  agent_start.png agent_end.png \
  "Subtle parallax camera movement, professional agent photo animation, smooth depth transition" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output agent_animated.mp4
```

---

## Complete Image-to-Video Pipeline

### Full Workflow Example

```bash
# ===========================================
# Step 1: Generate START frame
# ===========================================
cd "C:/Users/gblac/.claude/global/skills/nano-banana-agent"

python scripts/generate_image.py \
  "NEURAL-01 robot with hammer raised, mid-swing pose, industrial workbench, dramatic side lighting, sparks visible, brushed metal surfaces" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output start_frame.png

# ===========================================
# Step 2: Generate END frame
# ===========================================
python scripts/generate_image.py \
  "NEURAL-01 robot with hammer lowered after strike, same workbench and angle, impact sparks settling, dramatic lighting maintained" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output end_frame.png

# ===========================================
# Step 3: Animate between frames
# ===========================================
cd "C:/Users/gblac/.claude/global/skills/veo-agent"

python scripts/interpolate_frames_vertex.py \
  ../nano-banana-agent/start_frame.png \
  ../nano-banana-agent/end_frame.png \
  "Powerful hammer swing motion with subtle parallax camera movement, sparks flying on impact, industrial workshop setting" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output hammer_animation.mp4

# Video will be saved to hammer_animation.mp4
```

---

## Brand-Consistent Video Pipeline

```bash
# ===========================================
# Step 1: Generate START frame with style guide
# ===========================================
cd "C:/Users/gblac/.claude/global/skills/nano-banana-agent"

python scripts/generate_with_style_guide.py \
  "NEURAL-01 robot standing at modern desk, arms at sides, professional lighting" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output brand_start.png

# ===========================================
# Step 2: Generate END frame with style guide
# ===========================================
python scripts/generate_with_style_guide.py \
  "NEURAL-01 robot at same desk, arms raised in welcoming gesture, same lighting and angle" \
  --aspect-ratio 16:9 \
  --size 2K \
  --output brand_end.png

# ===========================================
# Step 3: Animate with Veo
# ===========================================
cd "C:/Users/gblac/.claude/global/skills/veo-agent"

python scripts/interpolate_frames_vertex.py \
  ../nano-banana-agent/brand_start.png \
  ../nano-banana-agent/brand_end.png \
  "Smooth robotic motion, arms raising to welcoming position, professional presentation style" \
  --project gblackautomation \
  --bucket gblackautomation-veo-videos \
  --output brand_welcome.mp4
```

---

## Prompt Engineering Tips

### For Nano Banana (Images)

**Good Prompts Include:**
1. **Subject**: Main focus (robot, character, scene)
2. **Action/Pose**: What they're doing
3. **Setting**: Environment, location
4. **Lighting**: Golden hour, dramatic, soft, studio
5. **Camera**: Angle, distance, depth of field
6. **Style**: Photorealistic, cinematic, product photography
7. **Colors**: Specific palette or mood
8. **Details**: Materials, textures, atmosphere

**Example Good Prompt:**
```
Wide-angle shot of NEURAL-01 Generalist robot standing in a modern minimalist office.
Brushed metal surface with copper accents, visible mechanical gears.
Soft diffused lighting from large windows, golden hour warmth.
Cream and terracotta color palette background.
Shallow depth of field with robot in sharp focus.
Professional product photography style, 8K detail.
```

**Example Bad Prompt:**
```
robot in office
```

### For Veo (Videos)

**Good Prompts Include:**
1. **Motion Type**: Pan, zoom, dolly, parallax
2. **Subject Movement**: How subjects move
3. **Speed**: Slow, smooth, fluid, dramatic
4. **Camera Movement**: Subtle, tracking, static
5. **Continuity**: "Maintaining lighting", "same angle"

**Example Good Prompt:**
```
Smooth parallax camera pan from left to right.
NEURAL-01 robot remains centered in frame.
Subtle depth-of-field shift as camera moves.
Professional lighting maintained throughout.
Fluid cinematic motion, no sudden movements.
```

**Example Bad Prompt:**
```
camera moves
```

---

## Model Capabilities Comparison

### Nano Banana Models

| Feature | Flash (2.5) | Pro (3.0) |
|---------|-------------|-----------|
| Speed | ⚡ Ultra-fast | Moderate |
| Cost | 💰 Cheaper | Higher |
| Max Resolution | 2K | 4K |
| Reference Images | 1 | Up to 14 |
| Character Consistency | Basic | Advanced (5 subjects) |
| Quality | Good | Exceptional |
| Best For | Quick iterations | Final assets |

### Veo Endpoints

| Feature | Gemini API | Vertex AI |
|---------|-----------|-----------|
| Text-to-video | ✅ | ✅ |
| Frame interpolation | ❌ | ✅ |
| Reference images | ❌ | ✅ |
| Auth | API Key | Service Account |
| Setup | Easy | Moderate |
| Best For | Quick tests | Production |

---

## Common Issues & Solutions

### Nano Banana Issues

**"GEMINI_API_KEY not found"**
- Solution: `export GEMINI_API_KEY=your_key_here`
- Get key from: https://aistudio.google.com/apikey

**"google-genai package not installed"**
- Solution: `pip install google-genai`

**"Invalid aspect ratio"**
- Solution: Use valid ratios: `1:1`, `16:9`, `9:16`, `4:3`, `3:2`, `21:9`

**"Image size requires Pro model"**
- Solution: Use `--model gemini-3-pro-image-preview` for 2K/4K

---

### Veo Issues

**"gcsUri isn't supported by this model"**
- Cause: Using Gemini API for frame interpolation
- Solution: Use Vertex AI with `interpolate_frames_vertex.py`

**"bytesBase64 isn't supported"**
- Cause: Using Gemini API for frame interpolation
- Solution: Switch to Vertex AI endpoint

**"Permission denied on GCS bucket"**
- Solution: Grant "Storage Object Admin" role to service account

**"GOOGLE_APPLICATION_CREDENTIALS not set"**
- Solution: `export GOOGLE_APPLICATION_CREDENTIALS=~/.gcp/veo-agent-key.json`

---

## Cost Estimates

### Nano Banana (Google Gemini)
- Check current pricing: https://ai.google.dev/pricing
- Typically billed per image generation
- Pro model costs more than Flash

### Veo 3.1 (Vertex AI)
- Billed per video generation
- 8-second videos (~$0.50-$2.00 depending on resolution)
- Frame interpolation included in video cost

---

## Quick Reference Commands

### Generate Image (Basic)
```bash
cd "C:/Users/gblac/.claude/global/skills/nano-banana-agent"
python scripts/generate_image.py "YOUR PROMPT" --aspect-ratio 16:9 --size 2K --output result.png
```

### Generate Image (Brand Style)
```bash
cd "C:/Users/gblac/.claude/global/skills/nano-banana-agent"
python scripts/generate_with_style_guide.py "YOUR PROMPT" --aspect-ratio 16:9 --output result.png
```

### Animate Between Images
```bash
cd "C:/Users/gblac/.claude/global/skills/veo-agent"
python scripts/interpolate_frames_vertex.py start.png end.png "MOTION DESCRIPTION" \
  --project gblackautomation --bucket gblackautomation-veo-videos --output result.mp4
```

---

## Additional Resources

### Documentation Files
- `nano-banana-agent/SKILL.md` - Nano Banana skill definition
- `veo-agent/SKILL.md` - Veo skill definition
- `nano-banana-agent/references/api_reference.md` - API quick reference
- `.claude/context/VEO_VERTEX_AI_SUCCESS.md` - Working Veo implementation guide
- `.claude/context/VEO_GCS_SETUP_GUIDE.md` - GCS setup instructions

### Related Files in Repo
- `code-design/nano-banana-pro-api.md` - Nano Banana Pro API docs
- `comfyui/NANO_BANANA_WORKFLOWS.md` - ComfyUI integration guide
- `tools/remote-coding-agent/.agents/google-nano-banana-agent.md` - Agent definition

### External Links
- Google AI Studio (API keys): https://aistudio.google.com/
- Gemini API Pricing: https://ai.google.dev/pricing
- Vertex AI Docs: https://cloud.google.com/vertex-ai/docs

---

## Example Use Cases

### Marketing Assets
1. Generate hero images with brand style guide
2. Create character variations for different scenarios
3. Animate hero images for website headers

### Product Demonstrations
1. Generate product shots (start and end states)
2. Animate product interactions
3. Create video tutorials

### Social Media Content
1. Generate 1:1 images for Instagram
2. Generate 9:16 stories
3. Animate static posts for engagement

### Website Content
1. 16:9 hero images
2. 21:9 ultra-wide banners
3. Parallax animations for scrolling effects

---

**Last Updated:** 2025-12-18
**Maintained By:** GB Automation
**GCS Bucket:** `gs://gblackautomation-veo-videos`
