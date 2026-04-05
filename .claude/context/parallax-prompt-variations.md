# Parallax Animation Prompt Variations
## For Simple, Non-Distracting Project Overview Page Background

### Option 1: Medium Shot with Soft Blur
**START FRAME:**
```
Medium shot of NEURAL-01 Generalist robot from waist up, holding a tablet or blueprint, soft cream background with minimal detail, slight blur effect, clean composition, professional but approachable. Match exact character design from reference.
```

**END FRAME:**
```
Medium shot of NEURAL-01 Generalist robot from waist up, giving thumbs up gesture, soft cream background with minimal detail, slight blur effect, clean composition, satisfied expression. Match exact character design from reference.
```

---

### Option 2: Close Framing with Gradient Background
**START FRAME:**
```
Close framing of NEURAL-01 Generalist robot upper body, looking at blueprint in hands, simple gradient background (cream to light terracotta), no environmental details, shallow depth of field, minimalist composition. Match exact character design from reference.
```

**END FRAME:**
```
Close framing of NEURAL-01 Generalist robot upper body, arms crossed confidently, simple gradient background (cream to warm terracotta), no environmental details, shallow depth of field, minimalist composition. Match exact character design from reference.
```

---

### Option 3: Portrait Style with Vignette
**START FRAME:**
```
Portrait-style shot of NEURAL-01 Generalist robot torso and head, holding small tool or device, cream-colored backdrop with soft vignette edges, studio photography style, clean and simple, no distracting elements. Match exact character design from reference.
```

**END FRAME:**
```
Portrait-style shot of NEURAL-01 Generalist robot torso and head, relaxed pose with arms at sides, cream-colored backdrop with soft vignette edges, studio photography style, clean and simple, no distracting elements. Match exact character design from reference.
```

---

### Option 4: Product Photography Style
**START FRAME:**
```
NEURAL-01 Generalist robot centered in frame from chest up, minimal pose holding blueprint, completely plain cream background (#F3F1E7), professional product photography lighting, no environment, no props beyond blueprint, ultra-clean composition. Match exact character design from reference.
```

**END FRAME:**
```
NEURAL-01 Generalist robot centered in frame from chest up, standing tall with confident posture, completely plain cream background (#F3F1E7), professional product photography lighting, no environment, no additional props, ultra-clean composition. Match exact character design from reference.
```

---

### Option 5: Subtle Motion Blur Background (RECOMMENDED FOR PARALLAX)
**START FRAME:**
```
NEURAL-01 Generalist robot medium shot, slight forward lean suggesting movement, background is heavily blurred cream and terracotta abstract shapes, focus entirely on character, minimal depth, parallax-ready composition. Match exact character design from reference.
```

**END FRAME:**
```
NEURAL-01 Generalist robot medium shot, upright relaxed stance, background is heavily blurred cream and terracotta abstract shapes, focus entirely on character, minimal depth, parallax-ready composition. Match exact character design from reference.
```

---

### Option 6: Extreme Minimal (Flat Design Ready)
**START FRAME:**
```
NEURAL-01 Generalist robot waist-up portrait, simple standing pose, solid flat cream background, no shadows, no environment, clean vector-like style, perfect for layered parallax animation. Match exact character design from reference.
```

**END FRAME:**
```
NEURAL-01 Generalist robot waist-up portrait, arms slightly raised in completion gesture, solid flat cream background, no shadows, no environment, clean vector-like style, perfect for layered parallax animation. Match exact character design from reference.
```

---

## Recommended Settings for All Variations

- **Aspect Ratio**: `16:9` (standard web background)
- **Image Size**: `2K` (good quality without being too heavy)
- **Reference Images**: Design sheet + scene + color palette (prioritize character)

## Key Differences Between Options

| Option | Background Detail | Framing | Best For |
|--------|------------------|---------|----------|
| 1 | Soft blur | Medium | Gentle parallax movement |
| 2 | Gradient | Close | Subtle depth effect |
| 3 | Vignette | Portrait | Professional hero section |
| 4 | Plain solid | Product | Maximum simplicity |
| 5 | Motion blur | Medium | **Multi-layer parallax** ⭐ |
| 6 | Flat solid | Minimal | Vector-style animation |

## Generation Command Template

```bash
cd "C:/Users/gblac/OneDrive/Desktop/consulting-co"

# Start Frame
python scripts/generate_with_character_ref.py \
  "[PROMPT FROM ABOVE]" \
  --refs style-board/neural-01-design-sheet.jpeg \
          style-board/neural-01-scene.png \
          style-board/color-palette.png \
  --aspect-ratio 16:9 \
  --size 2K \
  --output parallax_start_v[N].png

# End Frame
python scripts/generate_with_character_ref.py \
  "[PROMPT FROM ABOVE]" \
  --refs style-board/neural-01-design-sheet.jpeg \
          style-board/neural-01-scene.png \
          style-board/color-palette.png \
  --aspect-ratio 16:9 \
  --size 2K \
  --output parallax_end_v[N].png
```

## Additional Modifications You Can Request

- **Even more zoomed in**: "Close-up from shoulders up"
- **Even simpler background**: "Pure solid color, no gradients"
- **Different poses**: "Typing gesture", "Pointing at screen", "Looking at camera"
- **Transparency-ready**: "Clean edges for PNG alpha channel"
- **Lighting adjustments**: "Flat lighting", "Rim light only", "No shadows"

## Quick Test Generation

Want to see Option 5 (recommended for parallax)? I can generate it immediately.
