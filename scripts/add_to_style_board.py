#!/usr/bin/env python3
"""Add images to the style board for better character grounding"""

import os
import shutil
import argparse
from pathlib import Path

def add_to_style_board(image_path, style_board_dir='style-board/', new_name=None):
    """Add an image to the style board"""

    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return False

    # Create style board if it doesn't exist
    os.makedirs(style_board_dir, exist_ok=True)

    # Determine output filename
    if new_name:
        dest_filename = new_name
    else:
        dest_filename = os.path.basename(image_path)

    dest_path = os.path.join(style_board_dir, dest_filename)

    # Copy file
    shutil.copy2(image_path, dest_path)

    # Get file size
    size_kb = os.path.getsize(dest_path) / 1024

    print(f"✅ Added to style board:")
    print(f"   File: {dest_filename}")
    print(f"   Size: {size_kb:.1f} KB")
    print(f"   Path: {dest_path}")

    return dest_path

def list_style_board(style_board_dir='style-board/'):
    """List all images in the style board"""

    if not os.path.exists(style_board_dir):
        print(f"📂 Style board doesn't exist yet: {style_board_dir}")
        return

    files = [f for f in os.listdir(style_board_dir)
             if os.path.isfile(os.path.join(style_board_dir, f))]

    if not files:
        print(f"📂 Style board is empty: {style_board_dir}")
        return

    print(f"\n📋 Style Board Contents ({len(files)} images):")
    print("=" * 60)

    total_size = 0
    for i, file in enumerate(sorted(files), 1):
        file_path = os.path.join(style_board_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        total_size += size_kb
        print(f"{i}. {file:<40} {size_kb:>8.1f} KB")

    print("=" * 60)
    print(f"Total size: {total_size:.1f} KB")
    print(f"\n💡 Use with: python scripts/generate_with_style_guide.py \"Your prompt\"")

def main():
    parser = argparse.ArgumentParser(description='Manage style board reference images')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add image to style board')
    add_parser.add_argument('image', help='Path to image file')
    add_parser.add_argument('--name', help='New filename (optional)')
    add_parser.add_argument('--style-dir', default='style-board/',
                           help='Style board directory (default: style-board/)')

    # List command
    list_parser = subparsers.add_parser('list', help='List style board contents')
    list_parser.add_argument('--style-dir', default='style-board/',
                            help='Style board directory (default: style-board/)')

    args = parser.parse_args()

    if args.command == 'add':
        add_to_style_board(args.image, args.style_dir, args.name)
    elif args.command == 'list':
        list_style_board(args.style_dir)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
