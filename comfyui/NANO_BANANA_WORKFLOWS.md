# Nano Banana ComfyUI Workflows - Complete Guide

**Date**: 2025-12-01

## What is Nano Banana?

**Nano Banana** (aka **Gemini 2.5 Flash Image**) is Google's state-of-the-art image generation and editing AI model that went viral for its incredible quality and capabilities. It's accessible via Google's Gemini API and has been integrated into ComfyUI through several custom nodes.

## GitHub Repositories

### 1. ShmuelRonen/ComfyUI-NanoBanano ⭐ MOST POPULAR

**Repository**: [GitHub - ShmuelRonen/ComfyUI-NanoBanano](https://github.com/ShmuelRonen/ComfyUI-NanoBanano)

**Features:**
- Multi-modal operations (generate, edit, style transfer, object insertion)
- Support for up to 5 reference images
- Character consistency across generations
- Batch processing (up to 4 images per request)
- Temperature control for creativity
- Customizable aspect ratios

**Installation:**
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/ShmuelRonen/ComfyUI-NanoBanano.git
cd ComfyUI-NanoBanano
pip install -r requirements.txt
```

**API Setup:**
```bash
# Method 1: Environment variable (recommended)
export GEMINI_API_KEY="your_api_key_here"

# Method 2: Enter directly in node's api_key field
```

**Get API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in and enable billing (paid tier required)
3. Generate API key (starts with `AIza...`)

**Available Operations:**
- **Generate**: Create new images from text prompts
- **Edit**: Modify existing images with text instructions
- **Style Transfer**: Apply styles from reference images
- **Object Insertion**: Add elements to existing scenes

**Key Parameters:**
- `prompt`: Text description of what you want
- `reference_image_1` to `reference_image_5`: Upload reference images
- `temperature`: Creativity level (0.0-1.0)
  - 0.0 = More deterministic/consistent
  - 1.0 = More creative/varied
- `batch_count`: Number of images per run (1-4)
- `aspect_ratio`: Image dimensions (only affects generation, not editing)

**Note**: This is an unofficial implementation.

---

### 2. ru4ls/ComfyUI_Nano_Banana

**Repository**: [GitHub - ru4ls/ComfyUI_Nano_Banana](https://github.com/ru4ls/ComfyUI_Nano_Banana)

**Features:**
- Text-to-Image generation
- Image-to-Image editing
- Image Fusion
- **Unified "Nano Banana All-in-One" node**
  - Combines all features in single interface
  - Dynamically adapts based on `image_count` parameter
- Generate up to **10 alternative images**
- Grounding and search capabilities

**Installation:**
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/ru4ls/ComfyUI_Nano_Banana.git
cd ComfyUI_Nano_Banana
pip install -r requirements.txt
```

**Configuration:**
- Same API key setup as above (Google AI Studio)
- Uses Gemini 2.5 Flash Image API

**Advantages:**
- More alternatives per generation (up to 10)
- All-in-one node simplifies workflow
- Additional grounding features

---

### 3. darkamenosa/comfy_nanobanana

**Repository**: [GitHub - darkamenosa/comfy_nanobanana](https://github.com/darkamenosa/comfy_nanobanana)

**Features:**
- Intelligent API key handling
- Simpler implementation
- Good for basic use cases

**Installation:**
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/darkamenosa/comfy_nanobanana.git
cd comfy_nanobanana
pip install -r requirements.txt
```

---

## Official ComfyUI Support

### ComfyUI Partner Nodes (Native Support)

**Blog Post**: [Nano-banana via ComfyUI Partner Nodes!](https://blog.comfy.org/p/nano-banana-via-comfyui-api-nodes)

ComfyUI now has **official native support** for Nano Banana via Partner Nodes:

**Features:**
- ✅ Text-to-image generation
- ✅ Image-to-image editing
- ✅ Character consistency and fidelity
- ✅ Text output capability
- ✅ Customizable resolutions & aspect ratios

**Getting Started:**
1. Update ComfyUI to latest version
2. Partner Nodes are built-in (no custom node installation needed)
3. Get Google Gemini API key
4. Search for "Nano Banana" nodes in ComfyUI

**Official Documentation**: [Nano Banana Pro and ComfyUI Official Example](https://docs.comfy.org/tutorials/partner-nodes/google/nano-banana-pro)

**Blog Post**: [Meet Nano Banana Pro in ComfyUI!](https://blog.comfy.org/p/meet-nano-banana-pro-in-comfyui)

---

## Example Workflows

### 1. Basic Workflow with Reference Images

**Source**: [Civitai - Basic Nano Banana ComfyUI workflow with up to 5 reference images](https://civitai.com/models/1906863/basic-nano-banana-comfyui-workflow-with-up-to-5-reference-images)

**Use Case**: Generate images with style/character consistency using reference images

**Key Features:**
- Load up to 5 reference images
- Combine with text prompts
- Maintain character/style consistency across generations

### 2. Advanced Nano Banana Workflow

**Source**: [Civitai - Nano Bannana [Comfyui] - Super Advanced](https://civitai.com/models/1902418/nano-bannana-comfyui)

**Use Case**: Complex multi-step image generation and editing

---

## Nano Banana × Wan2.2: Cinematic AI Video

**Source**: [MimicPC - Nano-banana × Wan2.2: Cinematic AI Video Made Easy](https://www.mimicpc.com/workflows/nano-banana-wan-22-quickly-create-cinematic-videos)

**Integration**: Combine Nano Banana with Wan2.2 for video generation

**Use Case**: Create cinematic AI videos quickly
- Generate keyframes with Nano Banana
- Animate with Wan2.2
- Produce cinematic video output

---

## API Usage Requirements

### Prerequisites

1. **Google Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Enable billing (paid tier required)
   - Generate API key

2. **ComfyUI Installation**
   - ComfyUI installed and running
   - Python environment with pip

3. **Custom Node or Partner Node**
   - Install one of the custom nodes above
   - OR use native Partner Nodes (latest ComfyUI)

### API Costs

**Gemini 2.5 Flash Image Pricing**:
- Paid tier required (no free tier for image generation)
- Check [Google AI Pricing](https://ai.google.dev/pricing) for current rates
- Typically billed per image generation

### Rate Limits

- Check Google Cloud Console for your project's rate limits
- Batch processing (1-4 or up to 10 images) counts as multiple requests
- Consider implementing retry logic for API failures

---

## Workflow Creation Guide

### Basic Text-to-Image Workflow

**Nodes Required:**
1. **Nano Banana Node** (any implementation)
2. **Save Image Node** (ComfyUI built-in)

**Steps:**
1. Add Nano Banana node to canvas
2. Set operation mode to "Generate"
3. Enter prompt: `"a serene mountain landscape at sunset"`
4. Set aspect ratio: `1:1` or `16:9`
5. Set temperature: `0.7` (balanced creativity)
6. Set batch count: `4` (generate 4 variations)
7. Connect to Save Image node
8. Run workflow

**Example JSON Structure** (simplified):
```json
{
  "1": {
    "class_type": "NanoBananaNode",
    "inputs": {
      "operation": "generate",
      "prompt": "a serene mountain landscape at sunset",
      "aspect_ratio": "16:9",
      "temperature": 0.7,
      "batch_count": 4,
      "api_key": "${GEMINI_API_KEY}"
    }
  },
  "2": {
    "class_type": "SaveImage",
    "inputs": {
      "images": ["1", 0]
    }
  }
}
```

### Image Editing Workflow

**Nodes Required:**
1. **Load Image Node**
2. **Nano Banana Node**
3. **Save Image Node**

**Steps:**
1. Load source image
2. Connect to Nano Banana node
3. Set operation to "Edit"
4. Prompt: `"add a rainbow in the sky"`
5. Temperature: `0.5` (more faithful to original)
6. Run workflow

### Style Transfer Workflow

**Nodes Required:**
1. **Load Image Node** (content)
2. **Load Image Node** (style reference)
3. **Nano Banana Node**
4. **Save Image Node**

**Steps:**
1. Load content image
2. Load style reference image
3. Connect both to Nano Banana node
4. Set operation to "Style Transfer"
5. Prompt: `"apply artistic style from reference"`
6. Connect multiple reference images for complex styles
7. Run workflow

### Character Consistency Workflow

**Use Case**: Generate multiple images of the same character

**Nodes Required:**
1. **Nano Banana Node**
2. **Load Image Node** (character reference)
3. **Save Image Node**

**Steps:**
1. Load character reference image
2. Connect to Nano Banana as `reference_image_1`
3. Generate with different prompts:
   - `"the character walking in a forest"`
   - `"the character reading a book"`
   - `"the character playing guitar"`
4. Temperature: `0.3-0.5` (maintain consistency)
5. Batch process multiple variations

---

## API Programmatic Usage

### Python Example (Using Requests)

```python
import requests
import json
import os
import base64

class NanoBananaAPI:
    def __init__(self, comfyui_host="http://localhost:8188"):
        self.host = comfyui_host
        self.api_key = os.getenv("GEMINI_API_KEY")

    def load_workflow(self, path):
        with open(path) as f:
            return json.load(f)

    def modify_nano_banana_workflow(self, workflow, prompt, operation="generate", temperature=0.7, batch_count=4, reference_images=None):
        """
        Modify Nano Banana workflow with custom parameters

        Args:
            workflow: Base workflow JSON
            prompt: Text prompt
            operation: "generate", "edit", "style_transfer", "object_insertion"
            temperature: 0.0-1.0 (creativity)
            batch_count: 1-4 (or up to 10 for ru4ls implementation)
            reference_images: List of base64 encoded images
        """
        # Find Nano Banana node
        for node_id, node in workflow.items():
            if "NanoBanana" in node.get("class_type", ""):
                node["inputs"]["prompt"] = prompt
                node["inputs"]["operation"] = operation
                node["inputs"]["temperature"] = temperature
                node["inputs"]["batch_count"] = batch_count
                node["inputs"]["api_key"] = self.api_key

                # Add reference images
                if reference_images:
                    for i, img in enumerate(reference_images[:5], 1):
                        node["inputs"][f"reference_image_{i}"] = img

        return workflow

    def queue_workflow(self, workflow):
        response = requests.post(
            f"{self.host}/prompt",
            json={"prompt": workflow}
        )
        return response.json()["prompt_id"]

    def get_result(self, prompt_id):
        import time
        while True:
            history = requests.get(f"{self.host}/history/{prompt_id}").json()

            if prompt_id in history:
                return history[prompt_id]

            time.sleep(2)

    def encode_image(self, image_path):
        """Encode image to base64 for API"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

# Usage Example
api = NanoBananaAPI()

# Load base workflow
workflow = api.load_workflow("nano_banana_workflow.json")

# Text-to-Image
workflow = api.modify_nano_banana_workflow(
    workflow,
    prompt="a cyberpunk city at night with neon lights",
    operation="generate",
    temperature=0.8,
    batch_count=4
)
prompt_id = api.queue_workflow(workflow)
result = api.get_result(prompt_id)
print(f"Generated images: {result}")

# Style Transfer with Reference
reference_img = api.encode_image("style_reference.jpg")
workflow = api.modify_nano_banana_workflow(
    workflow,
    prompt="apply this artistic style",
    operation="style_transfer",
    temperature=0.5,
    reference_images=[reference_img]
)
prompt_id = api.queue_workflow(workflow)
result = api.get_result(prompt_id)
```

### Batch Processing Example

```python
prompts = [
    "a serene beach at sunrise",
    "a mystical forest with glowing mushrooms",
    "a futuristic space station",
    "an ancient temple in the mountains"
]

results = []

for prompt in prompts:
    workflow = api.load_workflow("nano_banana_workflow.json")
    workflow = api.modify_nano_banana_workflow(
        workflow,
        prompt=prompt,
        operation="generate",
        temperature=0.7,
        batch_count=2  # 2 variations per prompt
    )

    prompt_id = api.queue_workflow(workflow)
    result = api.get_result(prompt_id)
    results.append({
        "prompt": prompt,
        "result": result
    })

    print(f"Completed: {prompt}")

print(f"Generated {len(results) * 2} total images")
```

---

## Comparison: Which Implementation to Use?

| Feature | ShmuelRonen | ru4ls | darkamenosa | Official Partner |
|---------|-------------|-------|-------------|------------------|
| **Batch Size** | 1-4 images | 1-10 images | 1-4 images | Varies |
| **Reference Images** | Up to 5 | Multiple | Limited | Up to 5 |
| **All-in-One Node** | ❌ | ✅ | ❌ | ✅ |
| **Grounding** | ❌ | ✅ | ❌ | ✅ |
| **Official Support** | ❌ | ❌ | ❌ | ✅ |
| **Complexity** | Medium | Medium | Low | Low |
| **Best For** | General use | High volume | Simple tasks | Production |

**Recommendation**:
- **Production**: Use Official Partner Nodes (latest ComfyUI)
- **High Volume**: Use ru4ls (up to 10 images)
- **Most Popular**: Use ShmuelRonen (most stars/forks)
- **Simplest**: Use darkamenosa or Official Partner

---

## Best Practices

### 1. Temperature Settings

- **0.0-0.3**: High consistency, less creativity (character consistency, editing)
- **0.4-0.6**: Balanced (general use)
- **0.7-0.9**: More creativity, less consistency (artistic exploration)
- **0.9-1.0**: Maximum creativity (experimental results)

### 2. Prompt Engineering

**Good Prompts:**
- "a serene mountain landscape at sunset, photorealistic, 8k quality"
- "cyberpunk city street with neon signs, rainy, night time, cinematic lighting"
- "portrait of a wizard, fantasy art style, detailed face, magical atmosphere"

**Bad Prompts:**
- "nice picture" (too vague)
- "something cool" (not descriptive)
- Single words without context

### 3. Reference Image Usage

- **Style Transfer**: Use 1-2 strong style references
- **Character Consistency**: Use 1 clear character reference
- **Complex Scenes**: Combine multiple references (3-5)

### 4. Batch Processing

- Start with batch_count=2 to test
- Increase to 4 (or 10) for variety
- Balance API costs vs variety needed

### 5. Error Handling

```python
import time

def queue_with_retry(api, workflow, max_retries=3):
    for attempt in range(max_retries):
        try:
            prompt_id = api.queue_workflow(workflow)
            return prompt_id
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

## Troubleshooting

### API Key Issues

**Problem**: `Invalid API key` error

**Solutions**:
1. Verify API key starts with `AIza...`
2. Check billing is enabled in Google Cloud Console
3. Ensure environment variable is set: `echo $GEMINI_API_KEY`
4. Try entering key directly in node

### Rate Limit Errors

**Problem**: `429 Too Many Requests`

**Solutions**:
1. Reduce batch_count
2. Add delays between requests (2-5 seconds)
3. Check Google Cloud Console quotas
4. Implement exponential backoff retry logic

### Image Quality Issues

**Problem**: Generated images don't match expectations

**Solutions**:
1. Improve prompt specificity
2. Adjust temperature (lower for more control)
3. Use reference images for guidance
4. Try multiple batch generations

### Node Not Found

**Problem**: Can't find Nano Banana node in ComfyUI

**Solutions**:
1. Restart ComfyUI after installation
2. Check custom_nodes directory
3. Verify requirements.txt installed correctly
4. Update ComfyUI to latest version (for Partner Nodes)

---

## Sources

- [GitHub - ShmuelRonen/ComfyUI-NanoBanano](https://github.com/ShmuelRonen/ComfyUI-NanoBanano)
- [GitHub - ru4ls/ComfyUI_Nano_Banana](https://github.com/ru4ls/ComfyUI_Nano_Banana)
- [GitHub - darkamenosa/comfy_nanobanana](https://github.com/darkamenosa/comfy_nanobanana)
- [Nano-banana via ComfyUI Partner Nodes!](https://blog.comfy.org/p/nano-banana-via-comfyui-api-nodes)
- [Meet Nano Banana Pro in ComfyUI!](https://blog.comfy.org/p/meet-nano-banana-pro-in-comfyui)
- [Nano Banana Pro and ComfyUI Official Example](https://docs.comfy.org/tutorials/partner-nodes/google/nano-banana-pro)
- [Basic Nano Banana ComfyUI workflow with up to 5 reference images](https://civitai.com/models/1906863/basic-nano-banana-comfyui-workflow-with-up-to-5-reference-images)
- [Nano Bannana [Comfyui] - Super Advanced](https://civitai.com/models/1902418/nano-bannana-comfyui)
- [MimicPC - Nano-banana × Wan2.2: Cinematic AI Video Made Easy](https://www.mimicpc.com/workflows/nano-banana-wan-22-quickly-create-cinematic-videos)

---

## Next Steps

1. **Install ComfyUI** (if not already)
2. **Choose implementation**:
   - Official Partner Nodes (recommended)
   - OR ShmuelRonen custom node
3. **Get Google Gemini API key** from AI Studio
4. **Test basic text-to-image workflow**
5. **Experiment with reference images** for style transfer
6. **Build API integration** for programmatic usage
7. **Create workflow library** for common use cases
