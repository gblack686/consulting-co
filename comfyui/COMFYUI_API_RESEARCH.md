# ComfyUI API Workflows - Research Summary

**Date**: 2025-12-01

## Overview

ComfyUI is "the most powerful and modular diffusion model GUI, api and backend with a graph/nodes interface" for AI image generation. It provides both a visual workflow editor and a comprehensive API for programmatic control.

## Key GitHub Repositories (2024-2025)

### Official Repositories

1. **[comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)** - Main repository
   - Built-in REST API and WebSocket support
   - Weekly release cycle (new stable version ~every Monday)
   - Graph/nodes interface for workflows

2. **[comfyanonymous/ComfyUI_examples](https://github.com/comfyanonymous/ComfyUI_examples)** - Official examples
   - Example workflows with embedded metadata
   - Images contain metadata that can be loaded into ComfyUI to get full workflow
   - Good learning resource for understanding workflow structure

### API-Focused Repositories

3. **[SaladTechnologies/comfyui-api](https://github.com/SaladTechnologies/comfyui-api)** ⭐ RECOMMENDED
   - Simple API server for horizontal scaling
   - Dynamic workflow endpoints
   - Automatic endpoint mounting by adding .js or .ts files to /workflows directory
   - Direct response outputs (synchronous) or async via storage providers
   - Makes ComfyUI easy to scale

4. **[realazthat/comfy-catapult](https://github.com/realazthat/comfy-catapult)** - Programmatic scheduling
   - Python library for scheduling ComfyUI workflows via API
   - Good for automation and batch processing

5. **[SamratBarai/ComfyAPI](https://github.com/SamratBarai/ComfyAPI)** - Python client
   - WebSocket-based interaction
   - Submit workflows and download outputs
   - Real-time progress monitoring

### Workflow Collections

6. **[ComfyUI-Workflow/awesome-comfyui](https://github.com/ComfyUI-Workflow/awesome-comfyui)**
   - Collection of custom nodes
   - Includes REST API nodes for HTTP/REST integration

7. **[cubiq/ComfyUI_Workflows](https://github.com/cubiq/ComfyUI_Workflows)**
   - Well-documented, easy-to-follow workflows
   - Learning-focused examples

8. **[comfy-deploy/comfyui-workflows](https://github.com/comfy-deploy/comfyui-workflows)**
   - Cloud and local-ready workflows
   - Complete API formats and dependencies
   - Immediately reproducible examples

9. **[aimpowerment/comfyui-workflows](https://github.com/aimpowerment/comfyui-workflows)**
   - Collection in .json format

10. **[AIDC-AI/ComfyUI-Copilot](https://github.com/AIDC-AI/ComfyUI-Copilot)**
    - AI-powered custom node
    - Workflow automation and intelligent assistance

## How ComfyUI API Works

### 1. Workflow Format

ComfyUI workflows are represented as JSON with two formats:

**Standard Workflow Format** (UI):
- Human-readable
- Contains UI metadata (positions, sizes)
- Good for saving/loading in ComfyUI interface

**API Format** (`workflow_api.json`):
- Optimized for programmatic execution
- Contains nodes, inputs, and connections
- No UI metadata
- **Export from ComfyUI**: Enable dev mode, save as "API Format"

### 2. Workflow Modification Methods

**Method 1: Template Variables (Handlebars)**
```json
{
  "prompt": "{{positive_prompt}}",
  "seed": "{{seed}}",
  "input_image": "{{input_image}}"
}
```

**Method 2: Python Modification**
```python
def modify_workflow(workflow, parameters):
    # Modify nodes programmatically
    workflow["nodes"]["KSampler"]["inputs"]["seed"] = parameters["seed"]
    workflow["nodes"]["CLIPTextEncode"]["inputs"]["text"] = parameters["prompt"]
    return workflow
```

**Method 3: Direct JSON Manipulation**
- Load workflow JSON
- Find node by ID or class type
- Update inputs/values
- Submit modified workflow to API

### 3. API Communication

**WebSocket API** (Real-time):
```python
import websocket
import json

ws = websocket.create_connection("ws://localhost:8188/ws")

# Queue workflow
response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow_json}
)

# Monitor progress
while True:
    message = json.loads(ws.recv())
    if message["type"] == "executing":
        print(f"Progress: {message['data']}")
    elif message["type"] == "executed":
        print("Workflow complete!")
        break
```

**REST API** (Simpler):
```python
import requests

response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow_json}
)
prompt_id = response.json()["prompt_id"]

# Get output
output = requests.get(f"http://localhost:8188/history/{prompt_id}")
```

## Requirements to Call ComfyUI Workflows

### Prerequisites

1. **Running ComfyUI Instance**
   - Local: `python main.py --listen 0.0.0.0 --port 8188`
   - Default: `http://localhost:8188`
   - API enabled by default

2. **Workflow JSON** (API format)
   - Export from ComfyUI UI in dev mode
   - Use "Save (API Format)" option
   - Results in `workflow_api.json`

3. **Dependencies**
   - Python client: `websocket-client`, `requests`
   - Or use libraries: `comfy-catapult`, `ComfyAPI`

4. **Models & Checkpoints**
   - Ensure referenced models exist in ComfyUI's models directory
   - Workflow will fail if models are missing

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/prompt` | POST | Queue workflow for execution |
| `/queue` | GET | View current queue |
| `/history` | GET | Get execution history |
| `/history/{prompt_id}` | GET | Get specific execution result |
| `/interrupt` | POST | Stop current execution |
| `/ws` | WebSocket | Real-time progress updates |

## Modifying Workflows with API

### Step-by-Step Process

**1. Export Workflow**
```
ComfyUI UI → Enable Dev Mode → Menu → Save (API Format) → workflow_api.json
```

**2. Identify Modification Points**
```python
# Load workflow
with open('workflow_api.json') as f:
    workflow = json.load(f)

# Find nodes (example structure)
# workflow = {
#   "3": {"class_type": "KSampler", "inputs": {"seed": 12345}},
#   "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "a cat"}}
# }
```

**3. Modify Parameters**
```python
# Update seed
workflow["3"]["inputs"]["seed"] = 67890

# Update prompt
workflow["6"]["inputs"]["text"] = "a beautiful landscape"

# Update image dimensions
workflow["5"]["inputs"]["width"] = 1024
workflow["5"]["inputs"]["height"] = 768
```

**4. Submit to API**
```python
import requests

response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow}
)

prompt_id = response.json()["prompt_id"]
print(f"Queued workflow: {prompt_id}")
```

**5. Get Results**
```python
# Wait for completion (polling)
import time

while True:
    history = requests.get(f"http://localhost:8188/history/{prompt_id}").json()

    if prompt_id in history:
        outputs = history[prompt_id]["outputs"]
        # Extract image paths from outputs
        break

    time.sleep(1)
```

### Common Modification Patterns

**Dynamic Prompts:**
```python
def update_prompt(workflow, positive_prompt, negative_prompt=""):
    # Find CLIP text encode nodes
    for node_id, node in workflow.items():
        if node["class_type"] == "CLIPTextEncode":
            if "positive" in node.get("_meta", {}).get("title", "").lower():
                node["inputs"]["text"] = positive_prompt
            elif "negative" in node.get("_meta", {}).get("title", "").lower():
                node["inputs"]["text"] = negative_prompt
    return workflow
```

**Random Seeds:**
```python
import random

def randomize_seed(workflow):
    for node_id, node in workflow.items():
        if node["class_type"] == "KSampler":
            node["inputs"]["seed"] = random.randint(0, 2**32 - 1)
    return workflow
```

**Batch Processing:**
```python
prompts = ["a cat", "a dog", "a bird"]

for prompt in prompts:
    workflow_copy = workflow.copy()
    workflow_copy = update_prompt(workflow_copy, prompt)

    response = requests.post(
        "http://localhost:8188/prompt",
        json={"prompt": workflow_copy}
    )
    print(f"Queued: {prompt}")
```

## Best Practices

1. **Version Control Workflows**
   - Store workflow JSON in Git
   - Use meaningful names: `text_to_image_basic.json`

2. **Template Approach**
   - Create base workflows with placeholders
   - Build library of reusable templates

3. **Error Handling**
   - Check model availability before queuing
   - Validate workflow JSON structure
   - Handle API timeouts gracefully

4. **Performance**
   - Use WebSocket for real-time feedback
   - Batch similar workflows together
   - Consider queue management for high loads

5. **Testing**
   - Test workflows in UI first
   - Validate API format exports
   - Start with simple modifications

## Useful Tutorials & Resources

### Step-by-Step Guides

- **[ComfyUI Workflow into API with Python Example](https://www.comfyuiasapi.com/blog/step-by-step-comfyui-to-api-example-in-python)** - Complete Python tutorial with modify_workflow() function
- **[Deploying Custom ComfyUI Workflows as APIs](https://www.baseten.co/blog/deploying-custom-comfyui-workflows-as-apis/)** - Baseten deployment guide
- **[Hosting a ComfyUI Workflow via API](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/)** - 9elements tutorial on WebSocket API structure
- **[Integrate ComfyUI Workflows via API - ViewComfy Guide](https://www.viewcomfy.com/blog/integrate-comfyui-workflows-into-your-apps-via-api)** - Integration patterns
- **[Productionize Your Comfy UI Workflow](https://www.cerebrium.ai/blog/productionize-your-comfy-ui-workflow)** - Cerebrium production deployment
- **[Executing ComfyUI Workflows as Standalone Scripts](https://www.timlrx.com/blog/executing-comfyui-workflows-as-standalone-scripts)** - Standalone execution patterns

### Tools & Platforms

- **[Replicate: any-comfyui-workflow](https://replicate.com/comfyui/any-comfyui-workflow)** - Run any workflow with API on Replicate
- **[ComfyUI Workflow Basics Tutorial](https://comfyui-wiki.com/en/interface/workflow)** - Official wiki

## Example: Simple Text-to-Image API

```python
import requests
import json
import time

class ComfyUIAPI:
    def __init__(self, host="http://localhost:8188"):
        self.host = host

    def load_workflow(self, path):
        with open(path) as f:
            return json.load(f)

    def modify_text_to_image(self, workflow, prompt, seed=None):
        # Find and update prompt
        for node_id, node in workflow.items():
            if node["class_type"] == "CLIPTextEncode":
                node["inputs"]["text"] = prompt

            if seed and node["class_type"] == "KSampler":
                node["inputs"]["seed"] = seed

        return workflow

    def queue_workflow(self, workflow):
        response = requests.post(
            f"{self.host}/prompt",
            json={"prompt": workflow}
        )
        return response.json()["prompt_id"]

    def get_result(self, prompt_id):
        while True:
            history = requests.get(f"{self.host}/history/{prompt_id}").json()

            if prompt_id in history:
                return history[prompt_id]

            time.sleep(1)

# Usage
api = ComfyUIAPI()
workflow = api.load_workflow("workflow_api.json")
workflow = api.modify_text_to_image(workflow, "a beautiful sunset over mountains")
prompt_id = api.queue_workflow(workflow)
result = api.get_result(prompt_id)
print(f"Generated image: {result}")
```

## Next Steps

1. **Install ComfyUI locally** or use cloud instance
2. **Create simple workflow** in UI (text-to-image)
3. **Export as API format** and examine JSON structure
4. **Write Python client** to modify and queue workflows
5. **Build workflow library** for common use cases
6. **Deploy to production** using SaladTechnologies/comfyui-api or similar

## Sources

- [GitHub - comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [GitHub - ComfyUI-Workflow/awesome-comfyui](https://github.com/ComfyUI-Workflow/awesome-comfyui)
- [GitHub - comfyanonymous/ComfyUI_examples](https://github.com/comfyanonymous/ComfyUI_examples)
- [GitHub - SaladTechnologies/comfyui-api](https://github.com/SaladTechnologies/comfyui-api)
- [GitHub - realazthat/comfy-catapult](https://github.com/realazthat/comfy-catapult)
- [GitHub - SamratBarai/ComfyAPI](https://github.com/SamratBarai/ComfyAPI)
- [ComfyUI Workflow into API with Python Example](https://www.comfyuiasapi.com/blog/step-by-step-comfyui-to-api-example-in-python)
- [Deploying Custom ComfyUI Workflows as APIs](https://www.baseten.co/blog/deploying-custom-comfyui-workflows-as-apis/)
- [Hosting a ComfyUI Workflow via API](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/)
- [Integrate ComfyUI Workflows via API - ViewComfy Guide](https://www.viewcomfy.com/blog/integrate-comfyui-workflows-into-your-apps-via-api)
