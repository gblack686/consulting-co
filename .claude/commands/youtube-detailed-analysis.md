---
description: Generate comprehensive detailed analysis for YouTube video transcripts using Claude Code
---

Analyze a YouTube video transcript and generate a comprehensive DETAILED ANALYSIS markdown file for Obsidian vault.

## Instructions

### Step 1: Get Video Information

If the user didn't provide video info, ask:
"Which video would you like to analyze? Provide either:
- Video ID (e.g., C5USs51zYu8)
- Video title
- Path to transcript file"

### Step 2: Load Transcript and Metadata

1. **Find transcript file:**
   - Check `indydevdan/vtts/` directory
   - Look for files containing the video ID or matching title
   - Read the transcript content

2. **Load video metadata:**
   - Read `indydevdan_videos_to_scrape.json`
   - Find matching video by ID or title
   - Extract: title, channel_name, channel_url, video_url, video_id

### Step 3: Generate Comprehensive Analysis

Using the transcript, create a DETAILED ANALYSIS with:

#### Required Sections:

**1. Frontmatter (YAML)**
```yaml
---
title: {Video Title}
creator: "[[{Channel Name}]]"
channel: {Channel Name}
channel_url: {Channel URL}
video_url: {Video URL}
video_id: {Video ID}
date_accessed: {Today's date YYYY-MM-DD}
analysis_depth: comprehensive
type: deep-dive-analysis
tags: [{5-8 relevant technical tags extracted from content}]
---
```

**2. Title & Executive Summary**
```markdown
# {Video Title}

## 📊 Executive Summary

{2-3 paragraph comprehensive summary of main topic, core argument, and key takeaways}

**Core Argument:** {Main thesis in one sentence}
```

**3. The Problem Section** (if applicable)
```markdown
## 🔍 The Problem

{What problem or challenge does the video address?}

### Current State / Pain Points

{Use ASCII diagrams to visualize the problem:}
```
┌─────────────────────────────────────────┐
│ PROBLEM 1                               │
│    • Detail                             │
│    • Detail                             │
└─────────────────────────────────────────┘
         ↓
{More diagrams as needed}
```
```

**4. Solution Overview**
```markdown
## 💡 Solution/Approach

{High-level explanation of the solution}

### Approach

{Create comparison diagrams:}
```
TRADITIONAL APPROACH          →  NEW APPROACH
┌──────────────┐                 ┌──────────────┐
│ Old Way      │                 │ New Way      │
└──────────────┘                 └──────────────┘
```
```

**5. Technical Implementation**
```markdown
## 🛠️ Technical Details/Implementation

{Detailed breakdown with:}
- Step-by-step processes
- Code examples mentioned
- Technical diagrams
- Gotchas and best practices
```

**6. Key Insights & Takeaways**
```markdown
## 📈 Key Insights

### Technical
- {Technical insight 1}
- {Technical insight 2}

### Strategic
- {Strategic insight 1}
- {Strategic insight 2}

### Practical Application
- {How to apply this}
- {Common pitfalls to avoid}
```

**7. Related Concepts**
```markdown
## 🔗 Related Concepts

- [[Concept 1]]
- [[Tool/Technology Name]]
- [[Pattern Name]]
```

**8. Footer**
```markdown
---
**Last Updated:** {Today's date}
**Status:** Archived
```

### Step 4: Export to Obsidian

1. **Determine output path:**
   ```
   C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\youtube\
   ```

2. **Create filename:**
   ```
   {Safe Video Title} - DETAILED ANALYSIS.md
   ```
   - Remove special characters
   - Replace spaces with hyphens
   - Limit to 80 characters

3. **Write file:**
   - Use Write tool to save the analysis
   - Display success message with file path

### Step 5: Confirm Completion

Display:
```
✅ Detailed analysis created!

📁 Location: youtube/{filename}
📝 Title: {Video Title}
🏷️ Tags: {tags}
📊 Analysis depth: Comprehensive

To view in Obsidian:
Open: C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\youtube\{filename}
```

---

## Style Guidelines

When generating analysis:

✅ **DO:**
- Use emoji section markers (📊, 🔍, 💡, 🛠️, 📈, 🔗)
- Create ASCII flowcharts and diagrams to visualize processes
- Use tables for comparisons
- Extract technical concepts and link with [[WikiLinks]]
- Focus on practical, actionable insights
- Make it comprehensive but scannable

❌ **DON'T:**
- Skip the ASCII diagrams (they're essential!)
- Write generic summaries (be specific to this video)
- Ignore workflows/processes mentioned (diagram them!)
- Miss technical concepts (these become knowledge graph nodes)

---

## Example Tag Extraction

From content, identify and tag:
- **Tools mentioned:** `mcp-servers`, `langchain`, `claude-code`
- **Concepts:** `agent-architecture`, `prompt-engineering`, `rag`
- **Patterns:** `orchestration`, `specialization`, `tool-use`
- **Domains:** `ai-coding`, `devops`, `web-development`

---

## Example Usage

```
/youtube-detailed-analysis C5USs51zYu8
/youtube-detailed-analysis "RD Framework Context Window Mastery"
/youtube-detailed-analysis ../indydevdan/vtts/video.txt
```

---

## Batch Processing

To analyze multiple videos, ask:
"Would you like to analyze all available transcripts?"

Then:
1. List all `.txt` files in `indydevdan/vtts/`
2. Load metadata from `indydevdan_videos_to_scrape.json`
3. For each transcript:
   - Check if analysis already exists (skip if yes)
   - Generate detailed analysis
   - Export to Obsidian
   - Show progress: "[X/Y] Processed: {title}"

---

## Quality Checklist

Before saving, verify:
- [ ] Executive summary is 2-3 paragraphs
- [ ] At least 2-3 ASCII diagrams/flowcharts included
- [ ] Detailed section breakdowns present
- [ ] Extracted 5+ relevant technical tags
- [ ] Creator link uses [[WikiLink]] format
- [ ] Related concepts are linked with [[WikiLinks]]
- [ ] Frontmatter is complete and valid YAML
- [ ] Filename ends with ` - DETAILED ANALYSIS.md`

---

## Notes

- **No API key required** - Uses Claude Code's current session
- **Fast processing** - Direct analysis without external API calls
- **Consistent format** - Matches existing detailed analysis files
- **Knowledge graph integration** - WikiLinks connect to Obsidian graph
