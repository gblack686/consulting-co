#!/usr/bin/env python3
"""Nano Banana image-to-image generation using base robot image"""

import os
import sys
import base64
import json
import requests

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY') or 'AIzaSyBDq13Qn1nk1cmk_KjcGEbNVCInqoUiNpw'
MODEL = 'gemini-3-pro-image-preview'
BASE_IMAGE = 'agent-images/neural-01-generalist.jpg'
PROMPT = "Transform this robot so it's using a hammer to build components of another robot. Keep the robot's design style but show it actively working in an industrial workshop with tools and sparks flying. Detailed mechanical design with visible gears and circuits. Cinematic lighting with dramatic shadows."

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generate_image():
    """Generate image using Gemini REST API with base image"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # Encode the base image
    print(f"📁 Loading base image: {BASE_IMAGE}")
    base_image_data = encode_image(BASE_IMAGE)

    data = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base_image_data
                    }
                }
            ]
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
    print(f"🖼️  Base image: NEURAL-01 Generalist")
    print(f"⏳ This may take a moment...\n")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()

        # Find the image part
        parts = result['candidates'][0]['content']['parts']

        image_data = None
        for part in parts:
            if 'inlineData' in part:
                image_data = part['inlineData']['data']
                break

        if not image_data:
            raise ValueError("No image data found in response")

        # Save image
        output_path = 'robot_builder_from_neural01.png'
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        print(f"\n✅ Image successfully generated!")
        print(f"📁 Saved to: {output_path}")
        print(f"📊 Original base: {BASE_IMAGE}")
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
