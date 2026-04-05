#!/usr/bin/env python3
"""Generate images with specific character reference images for better grounding"""

import os
import sys
import base64
import json
import requests
import argparse
from pathlib import Path

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY') or 'AIzaSyBDq13Qn1nk1cmk_KjcGEbNVCInqoUiNpw'
MODEL = 'gemini-3-pro-image-preview'

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generate_with_character_reference(
    prompt,
    character_ref_images,
    style_guide_prompt=None,
    aspect_ratio='16:9',
    image_size='2K',
    output_path=None
):
    """
    Generate image using specific character reference images

    Args:
        prompt: Generation prompt
        character_ref_images: List of paths to reference images (prioritized in order)
        style_guide_prompt: Additional style guide text (optional)
        aspect_ratio: Image aspect ratio
        image_size: Output size (1K, 2K, 4K)
        output_path: Output file path
    """

    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY not set")
        sys.exit(1)

    # Build full prompt
    if style_guide_prompt:
        full_prompt = f"{prompt}\n\n{style_guide_prompt}"
    else:
        full_prompt = prompt

    # Prepare reference images
    print(f"\n🎯 Character Reference Images ({len(character_ref_images)}):")
    for i, img_path in enumerate(character_ref_images, 1):
        if not os.path.exists(img_path):
            print(f"❌ Error: Reference image not found: {img_path}")
            sys.exit(1)
        size_kb = os.path.getsize(img_path) / 1024
        print(f"   {i}. {os.path.basename(img_path)} ({size_kb:.1f} KB)")

    # Build API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # Build content parts - TEXT FIRST, then IMAGES
    # This is important: prompt should come before reference images
    content_parts = [{"text": full_prompt}]

    # Add reference images in priority order
    for img_path in character_ref_images:
        img_data = encode_image(img_path)
        ext = Path(img_path).suffix.lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')

        content_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": img_data
            }
        })

    data = {
        "contents": [{
            "parts": content_parts
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size
            }
        }
    }

    # Make API call
    print(f"\n🎨 Generating with {MODEL}...")
    print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"🖼️  Reference count: {len(character_ref_images)}")
    print(f"📐 Aspect ratio: {aspect_ratio}")
    print(f"📏 Size: {image_size}")
    print(f"⏳ Please wait...\n")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=180)
        response.raise_for_status()

        result = response.json()

        # Extract image data
        parts = result['candidates'][0]['content']['parts']

        image_data = None
        for part in parts:
            if 'inlineData' in part:
                image_data = part['inlineData']['data']
                break

        if not image_data:
            raise ValueError("No image data found in response")

        # Determine output path
        if not output_path:
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in prompt[:50])
            safe_name = safe_name.strip().replace(' ', '_').lower()
            output_path = f'{safe_name}_grounded.png'

        # Save image
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        print(f"✅ Image generated successfully!")
        print(f"📁 Saved to: {output_path}")
        print(f"🎯 Character grounding: {len(character_ref_images)} reference images")
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

def main():
    parser = argparse.ArgumentParser(
        description='Generate images with specific character reference images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use character design sheet as primary reference
  python scripts/generate_with_character_ref.py \
    "NEURAL-01 robot working in a coffee shop" \
    --refs style-board/neural-01-reference-sheet.png

  # Use multiple references in priority order
  python scripts/generate_with_character_ref.py \
    "NEURAL-01 in futuristic lab" \
    --refs neural-01-sheet.png neural-01-scene.png \
    --aspect-ratio 16:9

  # Include style guide prompt
  python scripts/generate_with_character_ref.py \
    "Robot team meeting" \
    --refs char1.png char2.png \
    --style-guide "Warm cream backgrounds, terracotta accents, soft lighting" \
    --output team_meeting.png
        """
    )

    parser.add_argument('prompt', help='Image generation prompt')
    parser.add_argument('--refs', nargs='+', required=True,
                       help='Reference image paths (in priority order)')
    parser.add_argument('--style-guide',
                       help='Additional style guide prompt text')
    parser.add_argument('--aspect-ratio', default='16:9',
                       choices=['1:1', '16:9', '9:16', '4:3', '3:2', '21:9'],
                       help='Image aspect ratio (default: 16:9)')
    parser.add_argument('--size', default='2K',
                       choices=['1K', '2K', '4K'],
                       help='Image size (default: 2K)')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    generate_with_character_reference(
        prompt=args.prompt,
        character_ref_images=args.refs,
        style_guide_prompt=args.style_guide,
        aspect_ratio=args.aspect_ratio,
        image_size=args.size,
        output_path=args.output
    )

if __name__ == '__main__':
    main()
