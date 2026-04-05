#!/usr/bin/env python3
"""Generate a color palette reference image from GB Automation brand colors"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors from consulting-page-01.html
COLORS = {
    "Cream Background": "#F3F1E7",
    "Cream Panel": "#E6E4D9",
    "Terracotta": "#D97757",
    "Text Main": "#191919",
    "Text Muted": "#5C5C5C"
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_palette_image(output_path='style-board/color-palette.png'):
    """Create a visual color palette reference image"""

    # Image dimensions
    width = 1200
    swatch_height = 240
    height = len(COLORS) * swatch_height

    # Create image with cream background
    img = Image.new('RGB', (width, height), hex_to_rgb("#F3F1E7"))
    draw = ImageDraw.Draw(img)

    # Draw color swatches
    y_position = 0
    for name, hex_color in COLORS.items():
        # Draw color swatch
        rgb_color = hex_to_rgb(hex_color)
        draw.rectangle(
            [(0, y_position), (width, y_position + swatch_height)],
            fill=rgb_color
        )

        # Determine text color for readability
        # Use dark text on light backgrounds, light text on dark backgrounds
        brightness = (rgb_color[0] * 299 + rgb_color[1] * 587 + rgb_color[2] * 114) / 1000
        text_color = "#191919" if brightness > 128 else "#F3F1E7"
        text_rgb = hex_to_rgb(text_color)

        # Try to load a nice font, fall back to default if not available
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_small = ImageFont.truetype("arial.ttf", 32)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw color name
        draw.text(
            (40, y_position + 60),
            name,
            fill=text_rgb,
            font=font_large
        )

        # Draw hex code
        draw.text(
            (40, y_position + 130),
            hex_color.upper(),
            fill=text_rgb,
            font=font_small
        )

        # Draw RGB values
        rgb_text = f"RGB({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})"
        draw.text(
            (40, y_position + 175),
            rgb_text,
            fill=text_rgb,
            font=font_small
        )

        y_position += swatch_height

    # Save image
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    img.save(output_path)
    print(f"✅ Color palette created: {output_path}")
    print(f"📐 Dimensions: {width}x{height}px")
    print(f"🎨 Colors: {len(COLORS)}")
    return output_path

if __name__ == '__main__':
    create_palette_image()
