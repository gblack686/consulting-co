# YouTube Video Analysis Agent 🎥

*Transform raw transcripts into comprehensive insights*

---

## Purpose

Generate deep-dive analysis markdown files for YouTube videos with:
- Executive summaries
- Process flowcharts (in markdown/ASCII)
- Detailed breakdowns
- Key insights extraction
- Obsidian-formatted notes with proper linking

---

## When to Use

- After downloading a YouTube video transcript
- When you want comprehensive analysis (not just basic transcript export)
- For videos from whitelisted creators (Cole Medin, IndyDevDan, Sean Kochel, etc.)

---

## Workflow

### Input Required
- Video ID
- Video title
- Channel name
- Full transcript text
- Channel URL
- Video URL

### Analysis Process

1. **Read Full Transcript**
   - Extract main themes
   - Identify workflows/processes
   - Note key technical concepts
   - Find quotes and examples

2. **Generate Comprehensive Analysis**
   - Executive summary (2-3 paragraphs)
   - Visual diagrams (ASCII/markdown flowcharts)
   - Detailed section-by-section breakdown
   - Process workflows (if applicable)
   - Key insights and takeaways
   - Technical concepts explained
   - Related links and references

3. **Format for Obsidian**
   - Proper frontmatter with metadata
   - Tags extraction (tools, domains, concepts)
   - Creator links (using [[Creator Name]] format)
   - Related video links
   - Type: `deep-dive-analysis`
   - Analysis depth: `comprehensive`

4. **Export to Vault**
   - Save to `{OBSIDIAN_VAULT}/youtube/`
   - Filename: `{Video Title} - DETAILED ANALYSIS.md`
   - Create/update creator index file
   - Link to related videos

---

## Template Structure

```markdown
---
title: {Video Title}
creator: "[[{Creator Name}]]"
channel: {Channel Name}
channel_url: {Channel URL}
video_url: {Video URL}
video_id: {Video ID}
date_accessed: {YYYY-MM-DD}
analysis_depth: comprehensive
type: deep-dive-analysis
tags: [{extracted-tags}]
---

# {Video Title}

## 📊 Executive Summary

{2-3 paragraph summary of main points and core argument}

**Core Argument:** {Main thesis}

---

## 🔍 The Problem

{What problem does the video address?}

### Current State / Pain Points

```
{ASCII diagrams showing current state}

┌─────────────────────────────────────────┐
│ PROBLEM 1                               │
│    • Detail                             │
│    • Detail                             │
└─────────────────────────────────────────┘
         ↓
{More diagrams}
```

---

## 💡 Solution Overview

{High-level solution explanation}

### Approach

```
{Flowcharts showing the solution}

TRADITIONAL APPROACH          →  NEW APPROACH
┌──────────────┐                 ┌──────────────┐
│ Old Way      │                 │ New Way      │
└──────────────┘                 └──────────────┘
```

---

## 🛠️ Technical Implementation

{Detailed breakdown of how to implement}

### Step-by-Step Process

1. **{Step Name}**
   - Details
   - Code examples (if mentioned)
   - Gotchas

2. **{Next Step}**
   ...

---

## 📈 Key Insights & Takeaways

### Technical
- Insight 1
- Insight 2

### Strategic
- Insight 1
- Insight 2

### Practical Application
- How to apply this
- Common pitfalls to avoid

---

## 🔗 Related Concepts

- [[Concept 1]]
- [[Concept 2]]
- [[Tool/Technology 1]]

---

## Related Creators/Videos

- [[Creator Name]] - Related topic
- [[Another Video Title|Video about X]]

---

**Last Updated:** {date}
**Status:** Archived
```

---

## Prompt for Analysis

When you have a transcript, use this approach:

```
I have a YouTube video transcript that I need analyzed comprehensively.

Video Details:
- Title: {title}
- Creator: {creator}
- Channel: {channel}
- Video ID: {video_id}
- URL: {url}

Please analyze this transcript and generate a comprehensive markdown report with:

1. Executive summary (2-3 paragraphs)
2. ASCII/markdown flowcharts and diagrams showing processes and workflows
3. Detailed breakdown of main sections
4. Key insights and technical concepts
5. Related concepts and links
6. Proper Obsidian frontmatter with extracted tags

Format it as a "deep-dive-analysis" for my Obsidian vault, similar to a research paper.
Focus on extracting:
- Workflows and processes (visualize with diagrams)
- Technical patterns and architectures
- Key quotes and examples
- Actionable insights
- Related concepts to link in knowledge graph

Here's the transcript:

{paste full transcript}
```

---

## Examples of Good Tags

From existing analyses:
- `mcp-servers`, `ai-coding`, `tools`, `infrastructure`
- `rapid-development`, `design-to-code`, `workflow`
- `agent-architecture`, `orchestration`, `specialization`
- `prompt-engineering`, `context-engineering`

---

## Creator Index Files

For each creator, maintain an index file:

**`{OBSIDIAN_VAULT}/youtube/{Creator Name}.md`**

```markdown
---
title: {Creator Name}
type: creator
channel_url: {URL}
handle: @{handle}
focus_areas: [area1, area2]
whitelist_status: active
---

# {Creator Name}

{Brief description}

## Channel Info
- **YouTube:** {url}
- **Handle:** @{handle}
- **Whitelisted:** Yes ✓

## Videos

### Archived Videos
1. [[Video 1 DETAILED ANALYSIS|Video 1]]
2. [[Video 2 DETAILED ANALYSIS|Video 2]]

## Key Topics by Video
{Summary of topics covered}

## Related Creators
- [[Other Creator]]

---
**Last Updated:** {date}
**Status:** Active archive
```

---

## Integration Points

### From YouTube Video Archiver Skill
- Transcript files in `indydevdan/vtts/`
- Video metadata from scraper
- Channel whitelist

### To Obsidian Vault
- Path: `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\youtube\`
- Format: Obsidian markdown with proper linking
- Graph view: Connected by creator and concepts

---

## Quality Checklist

Before saving analysis:
- [ ] Executive summary is 2-3 paragraphs
- [ ] At least 2-3 ASCII diagrams/flowcharts
- [ ] Detailed section breakdowns
- [ ] Extracted 5+ relevant tags
- [ ] Creator link uses [[WikiLink]] format
- [ ] Related concepts are linked
- [ ] Frontmatter is complete
- [ ] File named correctly (ends with ` - DETAILED ANALYSIS.md`)

---

## Usage Example

```bash
# 1. Get transcript from youtube-video-archiver
transcript=$(cat indydevdan/vtts/video-name_videoID.txt)

# 2. Ask Claude to analyze with detailed prompt
# (Use the prompt template above)

# 3. Save output to Obsidian vault
# Claude will generate and save the file

# 4. Verify in Obsidian
# Open vault and check graph view for connections
```

---

**Status**: ✅ Documented workflow (not automated)
**Output**: Comprehensive markdown analysis files
**Format**: Obsidian-compatible with diagrams
**Location**: `{vault}/youtube/`
