# How to Edit Designs

Source: https://www.aura.build/learn/how-to-design
Scraped: 2026-03-05

---

Master the Aura editor to edit and customize designs. Learn how to switch modes, customize styles, manage assets, and fine-tune every detail.

View Modes
Preview Mode

See your site exactly as visitors will. Interact with buttons, links, and animations without editing distractions.

Design Mode

The visual builder. Click elements to edit text, swap images, and adjust styles using the sidebar controls.

Code Mode

For full control. Edit the raw HTML and Tailwind classes directly. Changes update in real-time.

Styling & Assets
Setting Fonts & Typography

The Selection Fonts panel (accessible from the toolbar) provides comprehensive typography management. It automatically detects fonts used in your design and offers powerful bulk editing capabilities.

Imported Fonts

View all Google Fonts currently loaded in your page. Fonts are automatically imported when you use them. You can remove unused fonts to optimize page load.

• See which fonts are actively used vs unused
• Remove individual fonts or bulk remove unused fonts
• Fonts load automatically when selected from the font picker
Font Pairings

Quick presets that apply complementary fonts to headings and body text simultaneously. Includes popular combinations like Inter/Inter, Playfair/Geist, and more.

• One-click application of heading + body font combinations
• Automatically sets appropriate font weights
• Removes unused fonts after applying a pairing
Change Fonts by Style

Bulk edit fonts based on text size:

• Headings: Change all text larger than 20px at once
• Body Text: Change all text 20px or smaller at once
• Adjust font weight and letter spacing (tracking) for each style group
• Hover to highlight matching elements in the preview
Detected Font Styles

Automatically detects all unique font style combinations used in your design based on computed styles:

• Shows font family, size, weight, style, and letter spacing
• Displays usage count for each style
• Edit weight and tracking for each detected style
• Hover to highlight all elements using that style
Detected Fonts

Lists all font family classes found in your HTML (e.g., font-sans, font-playfair):

• Change font family for all elements using a specific font class
• Adjust weight and letter spacing per font
• Supports both predefined fonts and arbitrary values like font-[Space_Mono]
• Hover to highlight elements using each font
Setting Colors

The Selection Colors panel (accessible from the toolbar) automatically detects all colors used in your design and provides powerful color management tools.

Color Mode Toggle

Switch between Light and Dark mode. When switching, color intensities are automatically inverted (e.g., text-gray-200 becomes text-gray-800) to maintain proper contrast.

• Automatically detects current mode based on text colors
• Inverts color intensities when switching modes
• Preserves opacity values (e.g., white/70)
• Flips white/black colors appropriately
Theme Colors

Detects base color names (e.g., "blue", "red", "gray") used throughout your design:

• Shows usage count for each color name
• Replace all instances of a color name with another (e.g., replace all "blue" with "indigo")
• Color presets: Quick theme swaps (Neutral, Gray, Stone, Indigo, Blue, Orange, Green)
• Hover to highlight all elements using a theme color
Detected Colors

Automatically finds all color classes used in your design:

• Types: Text colors, background colors, border colors, gradients, hover states
• Filters: All, Color, Gradient, Text, Background, Border, Hover
• Shows usage count for each color class
• Change individual colors using the Color Picker
• Supports Tailwind classes, hex codes, RGB/RGBA, HSL/HSLA
• Handles gradients (linear, radial, conic) as single units
• Hover to highlight elements using each color
Text Gradients

When changing a text color to a gradient, the system automatically applies bg-clip-text and text-transparent classes to enable gradient text effects.

Changing Assets

The Asset Picker (found in the Edit Popover's "Embed" section) lets you replace elements with pre-built components from Aura's library.

•
Component Library: Browse and insert buttons, cards, forms, and other UI components
•
Search & Filter: Find components by name, category, or tags
•
Replace Elements: Select an element and choose a component to replace it while maintaining positioning
•
Customize After Insert: All inserted components can be edited like any other element
Image Picker

The Image Picker provides multiple ways to add images to your design. Access it from the Edit Popover when selecting an image element or background.

Aura Library

Browse curated, high-quality images from Aura's collection. Search by keywords and filter by category.

Unsplash

Access millions of free photos from Unsplash. Search by keywords and download directly.

My Images

View and reuse images you've previously uploaded. Organized by date for easy access.

Upload Options
•
Drag & Drop: Drop image files directly onto the Image Picker for instant upload
•
Upload Button: Click "Upload" to select one or multiple images from your device
•
Image URL: Paste any image URL to use external images instantly
•
AI Analysis: Uploaded images are automatically analyzed for metadata, colors, and keywords
Remix Images

Generate AI-powered variations of your images using the Remix feature. Available in the Image Picker, this lets you:

•
Create style variations (e.g., "make it more vibrant", "add a vintage look")
•
Adjust composition and framing
•
Generate multiple options to choose from
•
Use various AI models including Gemini 3 Pro, GPT Image, and Ideogram
Selection Assets Panel

The Selection Assets button in the toolbar opens a panel that automatically detects all images in your design (both <img> tags and background images). You can:

• View all images in one place with thumbnails
• Hover to highlight images in the preview
• Click thumbnails or use Image Picker to replace any image
• See image type (Image Tag vs Background) and instance numbers
• Access Background Section for setting page backgrounds
Setting Backgrounds

Backgrounds can be set for any element using the Background section in the Edit Popover or the Selection Assets panel. You can use Embed (3D), Video, or Image backgrounds, plus color overlays for layered effects.

Embed (3D)
• Spline 3D backgrounds
• Unicorn Studio embeds
• Interactive 3D scenes
• Paste Spline/Unicorn URLs
Video
• YouTube/Vimeo URLs
• Direct video file URLs
• Autoplay and loop options
• Muted playback
Image
• Upload or select from Image Picker
• Background size: cover, contain, auto
• Background position controls
• Fixed or absolute positioning
Background Effects

All background types support visual effects:

• Hue rotation, blur, saturation, brightness
• Opacity and blend modes
• Alpha masks for gradient fades
• Height controls (full, 3/4, half, custom)
• Z-index for layering
Color Backgrounds
• Solid colors using hex codes or Tailwind classes
• Gradient backgrounds (linear, radial)
• Breakpoint-aware colors (different colors per device)
• Can be combined with image/video/embed backgrounds
Advanced Editing
The Edit Popover

Clicking any element in Design Mode opens the Edit Popover on the right side. It's organized into collapsible sections that appear based on the element type and current classes.

Editing Tailwind Classes

The Tailwind Classes textarea lets you directly edit utility classes. The textarea auto-resizes as you type.

•
Real-time Preview: Changes apply instantly to the selected element
•
Visual Controls Sync: Editing classes updates the visual controls (sliders, pickers) automatically
•
Breakpoint Filtering: Filter classes by breakpoint to see only mobile, tablet, or desktop classes
•
Common Classes: Examples include p-4, flex, rounded-lg, shadow-lg
Editing CSS Styles

The Inline CSS section lets you write custom CSS that gets applied via the style attribute.

•
Syntax: Write standard CSS properties (e.g., transform: rotate(45deg);)
•
Merge with Existing: New styles merge with existing inline styles
•
Use Cases: Complex transforms, custom animations, properties not in Tailwind
•
Auto-expand: The textarea expands when inline styles are detected
Visual Edits

Visual controls provide intuitive sliders, pickers, and dropdowns for common properties. All changes apply in real-time.

Layout & Spacing
• Width & Height (with max/min)
• Margins (all sides or individual)
• Padding (all sides or individual)
• Position (static, relative, absolute)
• Z-index
Visual Effects
• Border (color, width, radius)
• Shadow (multiple presets)
• Opacity & Blend modes
• Filters (blur, grayscale, brightness)
• Transforms (rotate, scale, translate)
Measurements

The Measurements panel shows computed dimensions and spacing values for the selected element.

•
Dimensions: Actual width and height in pixels
•
Spacing: Computed margins and padding values
•
Position: Top, right, bottom, left offsets for positioned elements
•
Use Cases: Ensure consistent spacing, align elements precisely, debug layout issues
Breakpoint-Aware Editing

Most visual controls support breakpoint-specific values. Use the breakpoint filter dropdown to set different values for desktop, tablet, and mobile. The Edit Popover shows a breakpoint indicator when editing breakpoint-specific properties.

Responsive
Breakpoints

Switch between Desktop, Tablet, and Mobile views using the device mode toggle in the top bar. The editor adapts the preview to match each breakpoint.

Responsive Prefixes

Use Tailwind's responsive prefixes to target specific breakpoints:

• sm: Small screens (640px+)
• md: Medium screens (768px+)
• lg: Large screens (1024px+)
• xl: Extra large (1280px+)
Breakpoint-Aware Controls

When editing in a specific device mode, visual controls automatically apply breakpoint prefixes. For example, changing font size in mobile mode adds text-sm while desktop keeps text-xl.

Preview layouts on all devices
Adjust typography for mobile readability
Change layout direction (flex-col on mobile)
Hide/show elements per breakpoint
Animations
Animations

Add smooth animations to elements using the Animations section in the Edit Popover. Animations enhance user experience and draw attention to important content.

Entry Animations

Elements animate in when they enter the viewport:

Fade In
Slide Up
Slide Left
Scale
Hover Effects

Interactive animations on hover:

• Lift (translate up)
• Scale (grow/shrink)
• Shadow changes
• Color transitions
Custom Animations

Use CSS transforms and transitions in the Inline CSS section for advanced animations like rotations, 3D transforms, and complex keyframe animations.

View Modes
Styling & Assets
Advanced Editing
Responsive Design
Animations
PRODUCT
Create
Templates
Components
Assets
Pricing
Changelog
Affiliates
WHAT WE USE
Mobbin
Screen Studio
Courses
UI Kit
Video Editor
Mockups
CONNECT
Privacy
Terms
Support
Report Issue
LinkedIn
X

© 2026 Aura. All rights reserved. Made with Cursor.
