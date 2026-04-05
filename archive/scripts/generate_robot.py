#!/usr/bin/env python3
"""Simple Nano Banana image generation using REST API"""

import os
import sys
import base64
import json
import requests

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY') or 'AIzaSyBDq13Qn1nk1cmk_KjcGEbNVCInqoUiNpw'
MODEL = 'gemini-3-pro-image-preview'
PROMPT = "A robot using a hammer to build a component of another robot. Industrial workshop setting with tools and metal parts. Detailed mechanical design with visible gears and circuits. Cinematic lighting with dramatic shadows."

def generate_image():
    """Generate image using Gemini REST API"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{"text": PROMPT}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "1:1",
                "imageSize": "2K"
            }
        }
    }

    print(f"🎨 Generating image with {MODEL}...")
    print(f"📝 Prompt: {PROMPT[:100]}...")
    print(f"⏳ This may take a moment...\n")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()

        # Debug: Show response structure
        print("DEBUG: Response keys:", list(result.keys()))
        if 'candidates' in result:
            print(f"DEBUG: Candidates count: {len(result['candidates'])}")
            if result['candidates']:
                print(f"DEBUG: First candidate keys: {list(result['candidates'][0].keys())}")
                if 'content' in result['candidates'][0]:
                    parts = result['candidates'][0]['content']['parts']
                    print(f"DEBUG: Parts count: {len(parts)}")
                    for i, part in enumerate(parts):
                        print(f"DEBUG: Part {i} keys: {list(part.keys())}")
        else:
            print("DEBUG: Full response:")
            print(json.dumps(result, indent=2)[:1000])

        # Extract image data
        parts = result['candidates'][0]['content']['parts']

        # Find the image part
        image_data = None
        for part in parts:
            if 'inlineData' in part:
                image_data = part['inlineData']['data']
                break

        if not image_data:
            raise ValueError("No image data found in response")

        # Save image
        output_path = 'robot_builder.png'
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        print(f"\n✅ Image successfully generated!")
        print(f"📁 Saved to: {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text[:500]}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    generate_image()
