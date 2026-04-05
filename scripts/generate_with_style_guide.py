#!/usr/bin/env python3
"""Generate images using GB Automation style guide with multi-image references"""

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
STYLE_GUIDE_DIR = 'style-board/'
STYLE_TEMPLATE_PATH = '.claude/context/style-guide-template.md'

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_style_template(template_path):
    """Load the style guide template"""
    if not os.path.exists(template_path):
        print(f"⚠️  Style guide template not found at: {template_path}")
        return None

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract just the key style guide section for the prompt
    # (Full template is quite long, so we'll extract the core elements)
    style_summary = """
STYLE GUIDE - GB Automation Brand:
- Color Palette: Cream backgrounds (#F3F1E7), terracotta accents (#D97757), dark charcoal text (#191919)
- Aesthetic: Minimalist, warm, professional, glass morphism effects with soft backdrop blur
- Materials: Brushed metal, polished chrome, copper/bronze accents for robots
- Lighting: Soft, diffused, warm tones with occasional dramatic highlights, golden hour quality
- Composition: Spacious, balanced, clean backgrounds, subtle depth of field, professional product photography style
- Mood: Professional yet approachable, calm, trustworthy, modern
- Character Style: Sleek metallic robots with visible mechanical details (gears, circuits), industrial but refined, humanoid proportions
- Typography: Newsreader (serif) for headlines, Inter (sans-serif) for body
"""
    return style_summary

def load_reference_images(style_dir, max_images=5):
    """Load reference images from style guide directory"""
    if not os.path.exists(style_dir):
        print(f"⚠️  Style guide directory not found: {style_dir}")
        return []

    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    # Get all image files
    image_files = []
    for file in os.listdir(style_dir):
        file_path = os.path.join(style_dir, file)
        if os.path.isfile(file_path) and Path(file).suffix.lower() in image_extensions:
            image_files.append(file_path)

    # Limit to max_images
    image_files = image_files[:max_images]

    if not image_files:
        print(f"⚠️  No reference images found in {style_dir}")

    return image_files

def generate_with_style_guide(
    prompt,
    style_guide_dir=STYLE_GUIDE_DIR,
    style_template=STYLE_TEMPLATE_PATH,
    aspect_ratio='1:1',
    image_size='2K',
    output_path=None,
    max_reference_images=5
):
    """Generate image using style guide and reference images"""

    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
        sys.exit(1)

    # Load style DNA
    print("📋 Loading style guide template...")
    style_dna = load_style_template(style_template)

    # Load reference images
    print(f"📁 Loading reference images from {style_guide_dir}...")
    reference_images = load_reference_images(style_guide_dir, max_reference_images)

    if not reference_images:
        print("⚠️  Warning: No reference images found. Generation will proceed without style references.")
        use_references = False
    else:
        print(f"🖼️  Found {len(reference_images)} reference images:")
        for img in reference_images:
            print(f"   - {os.path.basename(img)}")
        use_references = True

    # Combine prompt with style DNA
    if style_dna:
        full_prompt = f"{prompt}\n\n{style_dna}"
    else:
        full_prompt = prompt
        print("⚠️  Warning: Proceeding without style guide template")

    # Build API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    # Build content parts
    content_parts = [{"text": full_prompt}]

    # Add reference images if available
    if use_references:
        for img_path in reference_images:
            img_data = encode_image(img_path)
            # Determine MIME type
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
    print(f"\n🎨 Generating image with {MODEL}...")
    print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"🖼️  Reference images: {len(reference_images)}")
    print(f"📐 Aspect ratio: {aspect_ratio}")
    print(f"📏 Image size: {image_size}")
    print(f"⏳ This may take a moment...\n")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
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
            # Generate filename from prompt
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in prompt[:50])
            safe_name = safe_name.strip().replace(' ', '_').lower()
            output_path = f'{safe_name}_styled.png'

        # Save image
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(image_data))

        print(f"\n✅ Image successfully generated!")
        print(f"📁 Saved to: {output_path}")
        print(f"🎨 Style guide applied: {len(reference_images)} reference images")
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
        description='Generate images using GB Automation style guide',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a character variation
  python scripts/generate_with_style_guide.py "NEURAL-01 robot working in a modern office"

  # Generate marketing asset
  python scripts/generate_with_style_guide.py "Hero image for AI automation company" --aspect-ratio 16:9

  # Generate with custom output path
  python scripts/generate_with_style_guide.py "Robot team collaborating" --output team_collab.png

  # Use fewer reference images for faster generation
  python scripts/generate_with_style_guide.py "New robot design" --max-references 3
        """
    )

    parser.add_argument('prompt', help='Image generation prompt')
    parser.add_argument('--aspect-ratio', default='1:1',
                        choices=['1:1', '16:9', '9:16', '4:3', '3:2', '21:9'],
                        help='Image aspect ratio (default: 1:1)')
    parser.add_argument('--size', default='2K',
                        choices=['1K', '2K', '4K'],
                        help='Image size (default: 2K)')
    parser.add_argument('--output', help='Output file path (default: auto-generated)')
    parser.add_argument('--style-dir', default=STYLE_GUIDE_DIR,
                        help=f'Style guide directory (default: {STYLE_GUIDE_DIR})')
    parser.add_argument('--style-template', default=STYLE_TEMPLATE_PATH,
                        help=f'Style guide template path (default: {STYLE_TEMPLATE_PATH})')
    parser.add_argument('--max-references', type=int, default=5,
                        help='Maximum reference images to use (default: 5)')

    args = parser.parse_args()

    generate_with_style_guide(
        prompt=args.prompt,
        style_guide_dir=args.style_dir,
        style_template=args.style_template,
        aspect_ratio=args.aspect_ratio,
        image_size=args.size,
        output_path=args.output,
        max_reference_images=args.max_references
    )

if __name__ == '__main__':
    main()
