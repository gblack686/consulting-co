#!/usr/bin/env python3
"""Create a style board from website colors and agent images"""

import os
import shutil
from pathlib import Path
from create_color_palette import create_palette_image

def create_style_board(
    agent_images_dir='agent-images/',
    output_dir='style-board/',
    include_characters=None,
    max_characters=2
):
    """
    Create a curated style board with 3-5 reference images

    Args:
        agent_images_dir: Directory containing agent character images
        output_dir: Output directory for style board
        include_characters: List of specific character names to include (None = auto-select)
        max_characters: Maximum number of character images to include
    """

    print("🎨 Creating GB Automation Style Board...")
    print(f"📁 Output directory: {output_dir}\n")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Generate color palette
    print("Step 1: Generating color palette reference...")
    palette_path = os.path.join(output_dir, 'color-palette.png')
    create_palette_image(palette_path)
    print()

    # Step 2: Copy character references
    print("Step 2: Adding character references...")

    # Default character priority (most representative of brand)
    default_characters = ['neural-01-generalist', 'logic-x9-architect']

    if include_characters is None:
        include_characters = default_characters[:max_characters]

    if not os.path.exists(agent_images_dir):
        print(f"⚠️  Warning: Agent images directory not found: {agent_images_dir}")
        print("   Skipping character references")
    else:
        copied_count = 0
        for character_base in include_characters:
            # Find matching file (could be .jpg, .jpeg, .png)
            found = False
            for ext in ['.jpg', '.jpeg', '.png']:
                source_path = os.path.join(agent_images_dir, f'{character_base}{ext}')
                if os.path.exists(source_path):
                    dest_path = os.path.join(output_dir, os.path.basename(source_path))
                    shutil.copy2(source_path, dest_path)
                    print(f"   ✅ Copied: {os.path.basename(source_path)}")
                    copied_count += 1
                    found = True
                    break

            if not found:
                print(f"   ⚠️  Not found: {character_base}")

        print(f"\n   Total character references: {copied_count}")

    # Step 3: Summary
    print("\n" + "="*60)
    print("Style Board Created Successfully!")
    print("="*60)

    # List all files in style board
    style_files = sorted([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))])

    print(f"\n📋 Reference Images ({len(style_files)}):")
    for i, file in enumerate(style_files, 1):
        file_path = os.path.join(output_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        print(f"   {i}. {file} ({size_kb:.1f} KB)")

    print(f"\n💡 Usage:")
    print(f"   python scripts/generate_with_style_guide.py \"Your prompt here\"")
    print(f"\n📂 Style board location: {os.path.abspath(output_dir)}")

    return output_dir

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create GB Automation style board')
    parser.add_argument('--agent-images', default='agent-images/',
                        help='Directory containing agent images (default: agent-images/)')
    parser.add_argument('--output', default='style-board/',
                        help='Output directory (default: style-board/)')
    parser.add_argument('--characters', nargs='+',
                        help='Specific character names to include (without extension)')
    parser.add_argument('--max-characters', type=int, default=2,
                        help='Maximum number of character images (default: 2)')

    args = parser.parse_args()

    create_style_board(
        agent_images_dir=args.agent_images,
        output_dir=args.output,
        include_characters=args.characters,
        max_characters=args.max_characters
    )

if __name__ == '__main__':
    main()
