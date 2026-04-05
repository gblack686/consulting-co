# Plan 4: YouTube Automation + Knowledge Capture

## Overview
A comprehensive system for monitoring YouTube channels, capturing video transcripts, generating AI summaries, and storing everything in Obsidian for knowledge retrieval. Includes alerts for new videos and integration with liked videos feed.

---

## Phase 1: YouTube Monitoring System

### 1.1 Channel Subscription Management
- [ ] Create channel watchlist database schema:
  ```yaml
  channel:
    id: string
    name: string
    url: url
    category: string  # tech, trading, ai, etc.
    priority: high|medium|low
    check_frequency: hourly|daily|weekly
    last_checked: timestamp
    notification_enabled: boolean
  ```
- [ ] Build channel CRUD interface
- [ ] Import existing subscriptions via YouTube API
- [ ] Add manual channel entry

### 1.2 New Video Detection
- [ ] **YouTube Data API Integration**
  - Set up API credentials
  - Implement channel video listing
  - Track video IDs to detect new uploads
- [ ] **RSS Feed Alternative**
  - Parse YouTube RSS feeds (no API quota)
  - Faster polling for priority channels
- [ ] **Polling Scheduler**
  - Cron-based checking
  - Priority-based frequency
  - Backoff on rate limits

### 1.3 Alert System
- [ ] **Phone Notifications**
  - Pushover integration
  - Telegram bot notifications
  - SMS via Twilio (optional)
- [ ] **Desktop Notifications**
  - Native OS notifications
  - Browser push notifications
- [ ] **Alert Configuration**
  - Per-channel settings
  - Keyword filters
  - Quiet hours

---

## Phase 2: Transcript Extraction Pipeline

### 2.1 Transcript Sources
- [ ] **YouTube Native Captions**
  - youtube-transcript-api integration
  - Handle auto-generated vs manual captions
  - Multi-language support
- [ ] **Whisper Fallback**
  - Download audio when no captions
  - OpenAI Whisper transcription
  - GPU acceleration (optional)
- [ ] **Third-Party Services**
  - AssemblyAI integration
  - Deepgram alternative
  - Cost comparison per minute

### 2.2 Transcript Processing
- [ ] Clean raw transcript text
- [ ] Add timestamps (optional toggle)
- [ ] Segment into logical sections
- [ ] Extract speaker labels (if available)
- [ ] Identify code blocks/technical content

### 2.3 Transcript Storage
- [ ] Save raw transcripts (TXT/JSON)
- [ ] Store in database with metadata
- [ ] Index for full-text search
- [ ] Link to source video

---

## Phase 3: AI Summarization Engine

### 3.1 Summary Generation
- [ ] **Multi-Level Summaries**
  - TL;DR (1-2 sentences)
  - Executive summary (1 paragraph)
  - Detailed summary (key points)
  - Full chapter breakdown
- [ ] **Claude/GPT Integration**
  - Prompt templates per video type
  - Context-aware summarization
  - Cost optimization (batch processing)

### 3.2 Knowledge Extraction
- [ ] Extract key concepts
- [ ] Identify mentioned tools/libraries
- [ ] Pull out code snippets
- [ ] Extract quotes and insights
- [ ] Generate tags automatically

### 3.3 Embedding Generation
- [ ] Create vector embeddings
- [ ] Store in vector database (Pinecone/Qdrant/local)
- [ ] Enable semantic search
- [ ] Build RAG retrieval system

---

## Phase 4: Liked Videos Integration

### 4.1 Liked Videos Feed Access
- [ ] YouTube API OAuth setup
- [ ] Fetch liked videos list
- [ ] Track new likes (delta sync)
- [ ] Handle private/deleted videos

### 4.2 Daily Import Workflow
- [ ] Schedule daily liked videos check
- [ ] Auto-queue for transcript processing
- [ ] Skip already processed videos
- [ ] Generate daily digest

### 4.3 Like-Based Prioritization
- [ ] Liked videos get higher priority
- [ ] Fast-track processing
- [ ] Immediate notifications (optional)

---

## Phase 5: Obsidian Integration

### 5.1 Note Structure
- [ ] Design video note template:
  ```markdown
  ---
  title: {{video_title}}
  channel: {{channel_name}}
  url: {{video_url}}
  date: {{publish_date}}
  duration: {{duration}}
  tags: {{auto_tags}}
  status: processed
  ---

  ## Summary
  {{executive_summary}}

  ## Key Points
  {{key_points}}

  ## Concepts
  {{extracted_concepts}}

  ## Transcript
  {{full_transcript}}

  ## Related
  {{related_videos}}
  ```

### 5.2 Folder Organization
- [ ] Structure:
  ```
  /YouTube/
    /Channels/
      /{channel_name}/
        - video_1.md
        - video_2.md
    /Daily Digests/
    /By Topic/
    /Liked Videos/
  ```
- [ ] Auto-create folders
- [ ] Maintain index notes

### 5.3 Linking & Discovery
- [ ] Auto-link related videos
- [ ] Cross-reference with existing notes
- [ ] Build knowledge graph connections
- [ ] Create topic clusters

### 5.4 Sync Mechanism
- [ ] File-based sync to Obsidian vault
- [ ] Handle conflicts
- [ ] Real-time or batch updates
- [ ] Mobile sync consideration

---

## Phase 6: Advanced Features

### 6.1 Crawl4AI Integration
- [ ] Set up Crawl4AI for supplementary scraping
- [ ] Fetch video descriptions
- [ ] Scrape linked resources
- [ ] Extract mentioned URLs
- [ ] Process blog posts/docs mentioned in videos

### 6.2 Search & Retrieval
- [ ] Full-text search across transcripts
- [ ] Semantic search via embeddings
- [ ] Filter by channel/date/topic
- [ ] "Find videos about X" natural language queries

### 6.3 Analytics Dashboard
- [ ] Videos processed per day
- [ ] Top channels by volume
- [ ] Topic distribution
- [ ] Processing queue status
- [ ] Cost tracking

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YouTube Sources                          │
│    Subscriptions │ Liked Videos │ Manual URLs │ RSS Feeds   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Detection Layer                            │
│    YouTube API │ RSS Parser │ Polling Scheduler │ Webhooks  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Processing Queue                           │
│              Redis/SQS │ Priority Sorting                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transcript Extraction                        │
│    YouTube Captions │ Whisper │ AssemblyAI │ Cleaning       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Processing                              │
│    Summarization │ Extraction │ Tagging │ Embeddings        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│   SQLite/Supabase │ Vector DB │ Obsidian Files │ S3        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Interfaces                          │
│   Obsidian │ Search API │ Notifications │ Dashboard         │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependencies
- YouTube Data API credentials
- OAuth consent screen (for liked videos)
- youtube-transcript-api
- Whisper (OpenAI or local)
- Claude/GPT API for summarization
- Vector database (Pinecone/Qdrant/ChromaDB)
- Obsidian vault access
- Notification service (Pushover/Telegram)
- Crawl4AI (optional)

---

## Deliverables
- [ ] YouTube channel monitoring system
- [ ] Phone/desktop notification alerts
- [ ] Transcript extraction pipeline
- [ ] AI summarization engine
- [ ] Liked videos daily import
- [ ] Obsidian note generation
- [ ] Search and retrieval interface
- [ ] Analytics dashboard

---

## Success Metrics
- Time from video upload to notification
- Transcript extraction success rate
- Summary quality scores
- Videos processed per day
- Storage efficiency (cost per video)
- Search relevance accuracy
