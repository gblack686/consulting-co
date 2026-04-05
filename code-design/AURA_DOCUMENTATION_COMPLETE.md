# Aura.build Documentation - Complete Extraction

**Date**: 2025-12-07
**Location**: `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/code-design/`
**Source**: https://www.aura.build/learn/introduction

---

## ✅ Completion Summary

### API Keys Stored

1. **Jina AI API Key**
   - **Secret Name**: `gbautomation/core/jina-ai-api-key`
   - **ARN**: `arn:aws:secretsmanager:us-east-1:274487662938:secret:gbautomation/core/jina-ai-api-key-PdW4f3`
   - **Purpose**: Web scraping and content extraction
   - **Service**: Jina AI Reader API

2. **Google AI API Key** (Previously stored)
   - **Secret Name**: `gbautomation/core/google-ai-api-key`
   - **ARN**: `arn:aws:secretsmanager:us-east-1:274487662938:secret:gbautomation/core/google-ai-api-key-4Smd59`
   - **Purpose**: Google Gemini AI API access

---

## 📚 Documentation Files Created

### Total Files: 14 documents
### Total Size: ~156KB

| # | Filename | Size | Category | Description |
|---|----------|------|----------|-------------|
| 1 | `00-INDEX-Aura-Prompting-Strategies.md` | 15KB | Index | Master reference guide with all key strategies |
| 2 | `tips-for-prompting.md` | 24KB | Core Guide | Comprehensive prompting techniques |
| 3 | `typography-prompting.md` | 6.9KB | Specialty | Font and typography strategies |
| 4 | `styling-prompting.md` | 6.8KB | Specialty | Styling and design system prompts |
| 5 | `animation-prompting.md` | 6.8KB | Specialty | Animation techniques |
| 6 | `layout-prompting.md` | 6.8KB | Specialty | Layout patterns |
| 7 | `how-to-edit-designs.md` | 6.8KB | Workflow | Post-generation editing |
| 8 | `selling-templates.md` | 11KB | Business | Monetization strategies |
| 9 | `introduction.md` | 22KB | Foundation | Platform overview |
| 10 | `getting-started.md` | 6.7KB | Foundation | Quick start guide |
| 11 | `examples.md` | 6.6KB | Foundation | Use cases and examples |
| 12 | `api-reference.md` | 6.7KB | Technical | API documentation |
| 13 | `prompting-strategies.md` | 6.8KB | Reference | Video tutorials index |
| 14 | `temp-best-practices.md` | 6.3KB | Reference | Best practices guide |

---

## 🎯 Key Insights Extracted

### 1. HTML Generation Principles

**6 Core Components:**
1. Specify the framework (Tailwind, Bootstrap, Material UI)
2. Define component structure clearly
3. Include responsive behavior requirements
4. Reference style guides and brand colors
5. Mention interactive elements and animations
6. Provide references or inspiration

### 2. Component Templates

Pre-built prompts for:
- Hero Sections
- Pricing Tables
- Navigation Bars
- Testimonial Cards
- Forms and Inputs
- Modal Dialogs
- Alert Components
- Sidebar Navigation

### 3. Responsive Design Strategies

**4 Key Techniques:**
1. Specify exact breakpoints (desktop/tablet/mobile)
2. Describe mobile-specific behaviors
3. Prioritize content for mobile
4. Ensure touch-friendly elements (44px minimum)

### 4. Device Framing

Techniques for:
- Desktop Browser Frames (macOS traffic lights)
- iPhone Frames (with notch/Dynamic Island)
- iPad Frames (bezels and rounded corners)

### 5. Typography System

**Recommended Fonts:**
- **Sans-Serif**: Inter, Geist, Manrope, Plus Jakarta Sans, IBM Plex Sans
- **Monospace**: Geist Mono, IBM Plex Mono, JetBrains Mono
- **Serif**: Merriweather, IBM Plex Serif, Libre Baskerville

**Standard Scale:**
- H1: 40-48px (weight 600-700)
- H2: 28-32px (weight 600-700)
- H3: 20-24px (weight 500-600)
- Body: 16px (weight 400)
- Small: 14px (weight 400)
- Micro: 12px (weight 400)

### 6. Animation Techniques

**Common Patterns:**
- Fade-in effects (800ms, ease-in-out)
- Slide-in animations (translateX transitions)
- Blur effects (blur(10px) → blur(0))
- Sequenced/staggered animations (150ms delays)

**JavaScript Libraries:**
- Three.js (3D scenes)
- COBE.js (Interactive globes)
- Vanta.js (Animated backgrounds)
- GSAP (Professional animations)

### 7. Tailwind CSS System

**Design Tokens:**
- **Colors**: 50 (lightest) → 900 (darkest)
- **Spacing**: 1 unit = 0.25rem (4px)
- **Typography**: text-xs → text-9xl
- **Breakpoints**: sm, md, lg, xl, 2xl

### 8. Layout Patterns

**Common UI Patterns:**
- Bento Grid (mixed-sized cells)
- Modal Dialogs (overlay + backdrop)
- List Layouts (avatar + metadata)
- Alert Components (status variants)
- Sidebar Navigation (fixed-width)
- Action Bars (toolbars)
- Top Navigation (responsive nav)

### 9. Advanced Prompting

**Power User Techniques:**
1. **Chain Requests**: Iterative refinement
2. **Example Snippets**: Provide code samples
3. **Persona-Based**: "As if you were a UI designer..."
4. **Accessibility**: WCAG 2.1 AA compliance

### 10. Styling Frameworks

**Best Practices:**
- Be explicit about CSS frameworks
- Include specific class patterns
- Specify component libraries
- Mention CSS architecture (BEM, etc.)
- Reference known styles (iOS, Spotify, etc.)

---

## 🔧 Tools & Scripts Created

### 1. `scrape_aura_docs.py`
Initial documentation scraper for main pages.

### 2. `scrape_aura_specific_docs.py`
Targeted scraper for prompting-specific guides.

**Features:**
- AWS Secrets Manager integration
- Jina AI Reader API usage
- Automatic Obsidian note creation with frontmatter
- Error handling and retry logic

---

## 📊 Usage Statistics

### Scraping Session
- **Total Pages Attempted**: 13
- **Successfully Scraped**: 12
- **Failed**: 1 (timeout on best-practices, later recovered)
- **Total Content**: ~156KB markdown
- **Time**: ~5 minutes

### API Usage
- **Service**: Jina AI Reader API
- **Requests**: 13
- **Success Rate**: 92%
- **Data Format**: Markdown

---

## 🎨 Key Takeaways for AI Code Design

### Best Practices Distilled

1. **Be Specific**: Always specify framework, colors, fonts, and behaviors
2. **Think Responsive**: Mobile-first, then scale up
3. **Typography Matters**: Use modern web fonts with proper scale
4. **Animate Subtly**: 300-500ms for interactions, use timing functions
5. **Reference Reality**: Mention known apps/sites for style inspiration
6. **Accessibility First**: WCAG compliance, keyboard nav, ARIA labels
7. **Device Context**: Frame designs in realistic devices
8. **Chain Refinement**: Start simple, iterate with follow-up prompts

### Prompting Formula

```
[Component Type] + [Framework] + [Structure Details] +
[Responsive Behavior] + [Colors/Branding] + [Interactions] +
[Reference/Inspiration]
```

**Example:**
```
Create a pricing table with Tailwind CSS featuring 3 tiers
(Starter, Pro, Enterprise) in a responsive grid. Use blue-600
as primary color, include hover effects that lift cards with
shadow, and make it similar to Stripe's pricing page. On mobile,
stack cards vertically with 44px touch targets.
```

---

## 🔗 Quick Access

### Obsidian Vault Location
```
C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/code-design/
```

### Master Index File
```
00-INDEX-Aura-Prompting-Strategies.md
```

### AWS Secrets Manager
```bash
# Retrieve Jina AI API Key
aws secretsmanager get-secret-value --secret-id gbautomation/core/jina-ai-api-key --region us-east-1

# List all gbautomation API keys
aws secretsmanager list-secrets --query "SecretList[?starts_with(Name, 'gbautomation/core/')].Name" --region us-east-1
```

---

## 📈 Next Steps

### Potential Enhancements

1. **Automated Updates**
   - Schedule periodic re-scraping of Aura docs
   - Track changes and version differences

2. **Integration with Projects**
   - Create templates for common project types
   - Build prompt library for RevStar QuickStarts

3. **Knowledge Graph**
   - Add to Obsidian knowledge graph
   - Link with other design resources

4. **AI Agent Integration**
   - Create specialized agent for UI generation
   - Build prompt templates into agent workflows

5. **Community Sharing**
   - Contribute successful prompts back
   - Build internal template marketplace

---

## 📝 Notes

### What Worked Well
- Jina AI Reader API provided clean markdown extraction
- Automatic frontmatter generation made notes Obsidian-ready
- Retry logic handled timeout gracefully
- AWS Secrets Manager integration smooth

### Lessons Learned
- Some pages (video tutorials) are less content-rich
- Jina AI timeout can occur on heavy pages (increase to 60s)
- Obsidian linking requires careful filename sanitization
- Master index file provides huge value for navigation

### Future Considerations
- Add screenshot capture for visual examples
- Extract embedded videos or code snippets separately
- Build interactive prompt builder tool
- Create Obsidian templates for new design docs

---

**Documentation Extraction Complete** ✅

*All Aura.build prompting strategies and insights successfully captured and organized in Obsidian vault.*

---

**Maintained By**: GB Automation
**Project**: Code Design Knowledge Base
**Version**: 1.0
**Last Updated**: 2025-12-07
