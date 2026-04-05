# Vexa Meeting Transcription API - Deep Research

**Date**: 2026-03-11
**Repo**: https://github.com/Vexa-ai/vexa
**License**: Apache 2.0
**Stars**: ~1,795 | **Forks**: ~208 | **Open Issues**: 64
**Language**: Python (services) + TypeScript/Node (bot)
**Last Push**: 2026-03-10 (actively maintained, commits every 1-2 days)

---

## 1. What Is Vexa?

Vexa is an **open-source, self-hostable API for real-time meeting transcription**. It deploys bots that automatically join Google Meet, Microsoft Teams, and Zoom meetings, capture audio, and provide real-time transcriptions via REST API and WebSocket.

### Core Capabilities
- **Platforms**: Google Meet, Microsoft Teams, Zoom (Zoom requires Meeting SDK marketplace approval)
- **Transcription**: 100+ languages via Whisper (transcription + translation)
- **Real-time**: Sub-second transcript delivery via WebSocket
- **Interactive bot controls**: Make bots speak (TTS via OpenAI), send/read chat, share screen, set avatar
- **Recording**: Audio capture with configurable storage backends (local, MinIO, S3)
- **MCP Server**: Expose meeting tools to AI agents (Claude, Cursor, etc.)

---

## 2. Architecture

Vexa is a microservices architecture with these core components:

| Service | Role |
|---------|------|
| **api-gateway** (port 8056) | Routes all API requests, handles auth |
| **admin-api** (port 8057) | User/team/token management |
| **bot-manager** | Lifecycle management of meeting bots, spawns containers |
| **vexa-bot** | The actual bot - Playwright/Chromium joins meetings, captures audio |
| **WhisperLive** (port 9090) | Real-time audio transcription via WebSocket |
| **transcription-collector** | Consumes Redis streams, stores transcript segments in Postgres |
| **transcription-service** | Standalone transcription backend (GPU or remote) |
| **mcp** (port 18888) | MCP server exposing Vexa tools to AI agents |
| **tts-service** | Text-to-speech via OpenAI API |
| **redis** | Pub/sub for bot commands, stream for transcription segments |
| **postgres** | Persistent storage for meetings, transcripts, users |
| **minio** | S3-compatible recording storage |

### Data Flow
1. API request hits `api-gateway` -> `bot-manager` spawns a `vexa-bot` container
2. Bot uses Playwright + Chromium to join the meeting as a participant
3. Bot captures audio from DOM `<audio>`/`<video>` elements via Web Audio API
4. Audio resampled to 16kHz, streamed via WebSocket to `WhisperLive`
5. WhisperLive runs Whisper inference, pushes segments to Redis stream
6. `transcription-collector` reads Redis stream, stores in Postgres
7. Client fetches via REST `GET /transcripts/{platform}/{id}` or subscribes via WebSocket

---

## 3. MCP Server

### Configuration for Claude Desktop

```json
{
  "mcpServers": {
    "fastapi-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://api.cloud.vexa.ai/mcp",
        "--header",
        "Authorization: Bearer ${VEXA_API_KEY}"
      ],
      "env": {
        "VEXA_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

API key from: https://vexa.ai/dashboard/api-keys

### Available MCP Tools

**Pre-meeting:**
- `parse_meeting_link` - Extract platform, meeting ID, passcode from URL
- `update_meeting_data` - Set meeting name, participants, languages, notes

**During meeting:**
- `get_bot_status` - Check active bots
- `get_meeting_transcript` - Fetch current transcript snapshot

**Post-meeting:**
- `create_transcript_share_link` - Generate temporary public transcript URL
- `get_meeting_bundle` - Single call for status + notes + recordings + share link
- `list_recordings`, `get_recording`, `get_recording_media_download`, `delete_recording`

### Implementation
- Built with FastAPI + `fastapi_mcp` library
- Source: `services/mcp/main.py`
- Proxies requests to `api-gateway` with `X-API-Key` auth
- Self-hosted MCP runs on port 18888 internally

---

## 4. How the Bot Joins Google Meet

### Technology
- **Playwright** with Chromium browser automation
- **puppeteer-extra-plugin-stealth** to evade bot detection
- TypeScript/Node.js (`services/vexa-bot/src/googleMeet.ts`)

### Join Flow
1. Launch headless Chromium via Playwright with stealth plugin
2. Navigate to Google Meet URL
3. Fill in bot name from `botName` config field
4. Mute audio and video
5. Click "Ask to join" button
6. Wait for admission by meeting host

### User Experience
- **YES, a visible bot participant appears in the meeting**
- The bot shows up as a named participant (configurable name like "Vexa Notetaker")
- Meeting host must admit the bot (or auto-admit if configured)
- Bot can optionally have an avatar image
- Recent optimization (2026-03-08): virtual camera init skipped for transcription-only bots

### Audio Capture
- Finds `<audio>` and `<video>` DOM elements with active MediaStream sources
- Combines streams through Web Audio API
- Resamples to 16kHz mono
- Streams to WhisperLive via WebSocket

### Platform-Specific Notes
- **Teams**: Uses Playwright, requires `teams.live.com/meet/<ID>?p=<PASSCODE>` format
- **Zoom**: Uses native C++ addon wrapping official Zoom Meeting SDK via N-API (no browser)
- **Strategy Pattern**: Shared `meetingFlow.ts` orchestrates lifecycle across all platforms

---

## 5. WebSocket Streaming

### Format
- Client connects to WebSocket endpoint
- Receives transcript segments in real-time as JSON
- Sub-second latency claimed

### Internal Architecture
- Bot audio -> WebSocket (ws://whisperlive:9090/ws) -> WhisperLive
- WhisperLive -> Redis Stream (`transcription_segments`)
- transcription-collector -> Postgres
- Client WebSocket -> api-gateway -> real-time segment delivery

### Tunable Parameters (via env vars)
- `MIN_AUDIO_S`: Minimum audio seconds before processing (default 2.0)
- `MIN_TIME_BETWEEN_REQUESTS_S`: Throttle between requests (default 0.5s)
- `SAME_OUTPUT_THRESHOLD`: Dedup threshold (default 3)
- `VAD_FILTER_THRESHOLD`: Voice Activity Detection sensitivity
- `LANGUAGE_DETECTION_SEGMENTS`: Auto language detection window

Full WebSocket docs: docs.vexa.ai/websocket

---

## 6. Self-Hosted vs Cloud

### Option 1: Hosted SaaS (vexa.ai)
- **Starting at $12/month**
- Free tier for development ("free when you build")
- API key in 3 clicks at vexa.ai/dashboard
- No infrastructure to manage
- MCP endpoint: `https://api.cloud.vexa.ai/mcp`

### Option 2: Vexa Lite (Production Self-Hosted)
- Single Docker container, no GPU required
- Uses external transcription service (their hosted or your own)
- Multi-user, multi-token, team management
- Stateless, scalable, serverless-friendly

```bash
docker run -d --name vexa -p 8056:8056 \
  -e DATABASE_URL="postgresql://user:pass@host/vexa" \
  -e ADMIN_API_TOKEN="your-admin-token" \
  -e TRANSCRIBER_URL="https://transcription.service" \
  -e TRANSCRIBER_API_KEY="transcriber-token" \
  vexaai/vexa-lite:latest
```

### Option 3: Full Docker Compose (Development/Full Self-Host)
- `make all` for full stack with GPU transcription
- Includes: api-gateway, admin-api, bot-manager, vexa-bot, WhisperLive, transcription-collector, redis, postgres, minio, tts-service, mcp, dashboard
- GPU mode: requires NVIDIA GPU for local Whisper inference
- Remote mode: uses external transcription API (no GPU)

### Option 4: Enterprise
- Kubernetes, Nomad, OpenShift support
- Contact for pricing

---

## 7. Installation Requirements

### Vexa Lite (minimal)
- Docker
- PostgreSQL (external or containerized)
- External transcription service URL

### Full Stack
- Docker + Docker Compose
- PostgreSQL
- Redis
- MinIO (or S3-compatible storage)
- **For GPU transcription**: NVIDIA GPU + nvidia-docker
- **For remote transcription**: External API (no GPU needed)
- Node.js (for bot builds)
- Python 3.x (for API services)

### Key Environment Variables
- `DATABASE_URL` / `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `ADMIN_API_TOKEN` - Admin authentication
- `REMOTE_TRANSCRIBER_URL` + `REMOTE_TRANSCRIBER_API_KEY` - External Whisper service
- `OPENAI_API_KEY` - For TTS (bot speaking)
- `ZOOM_CLIENT_ID` + `ZOOM_CLIENT_SECRET` - For Zoom support
- `STORAGE_BACKEND` - `minio`, `s3`, or `local`

---

## 8. Claude/Anthropic Integration

### Direct MCP Integration
Vexa's MCP server works natively with:
- **Claude Desktop** (via `npx mcp-remote`)
- **Cursor** (same MCP config)
- **Any MCP-compatible client**

### Workflow Example
1. Claude receives a meeting link from user
2. Uses `parse_meeting_link` to extract platform + ID
3. Sends bot via `request_meeting_bot`
4. Monitors with `get_bot_status`
5. Fetches transcript with `get_meeting_transcript`
6. Generates summary, action items, etc.

### No Direct Anthropic SDK Integration
- Vexa doesn't use Claude API internally
- It's a meeting data provider, not an LLM consumer
- The MCP bridge is the integration point

---

## 9. Current Status (as of 2026-03-11)

### Activity
- **Very active**: Commits every 1-2 days
- Primary maintainer: DmitriyG228 (Dmitriy, likely founder)
- Last commit: 2026-03-10 (Teams meeting URL fix)

### Recent Development Focus (last 2 weeks)
- Bot optimization v0.9.3: disable incoming video for transcription-only bots
- GPU benchmarking: raised transcription concurrency from 2->20 on RTX 4090
- WhisperLive tuning: configurable env vars for all thresholds
- Teams meeting URL improvements
- Removed proprietary webapp/billing from open-source docker-compose

### Known Issues (from GitHub Issues)
- **Teams bot admission failures** (#171): "always exits with admission_false_positive"
- **Waiting room handling** (#166): bots exit when stuck in waiting rooms
- **Resource waste**: avatar streaming runs even when disabled (#168), virtual camera init unconditional (#167)
- **Reconciliation scheduler kills active bots** (#173): production outage risk
- **VAD state drift** in long sessions (#157)
- **Researching alternatives to Whisper**: Parakeet-TDT being evaluated (#156, #148)

---

## 10. Alternatives Comparison

### Vexa vs Recall.ai vs Google Meet Media API

| Feature | **Vexa** | **Recall.ai** | **Google Meet Media API** |
|---------|----------|---------------|--------------------------|
| **Type** | Open-source API | Closed-source SaaS | Google-native API |
| **License** | Apache 2.0 | Proprietary | Google ToS |
| **Self-hosted** | Yes (full or lite) | No | N/A (Google infra) |
| **Pricing** | $12/mo hosted; free self-host | $0.50/hr (first 5hr free) | Developer Preview (free?) |
| **Google Meet** | Yes (Playwright bot) | Yes (bot) | Yes (WebRTC, still needs "bot" participant) |
| **Teams** | Yes (Playwright bot) | Yes (bot) | No |
| **Zoom** | Yes (native SDK) | Yes (bot) | No |
| **Other platforms** | No | Slack Huddles, Webex, GoTo | No |
| **Bot visible?** | Yes, named participant | Yes, named participant | Yes, app participant (consent required) |
| **Real-time transcripts** | Yes, WebSocket | Yes, streaming | Raw audio only (BYO transcription) |
| **Built-in transcription** | Yes (Whisper, 100+ langs) | Yes ($0.15/hr extra) | No (raw audio streams) |
| **Recording** | Yes (audio, configurable) | Yes (audio + video, MP4) | Raw streams only |
| **MCP Server** | Yes, built-in | No | No |
| **Interactive bot** | Speak, chat, screen share | Limited | No |
| **Maturity** | ~1 year, active OSS | 5+ years, $38M Series B | Developer Preview |
| **Data sovereignty** | Full (self-host) | No (their infra) | Google infra |
| **GPU required** | Optional (can use remote) | N/A (SaaS) | N/A |

### When to Choose What

**Choose Vexa if:**
- You need data sovereignty / self-hosting
- You want an open-source solution you can modify
- You need MCP integration with Claude
- You want built-in Whisper transcription
- Budget-conscious (free self-host or $12/mo)

**Choose Recall.ai if:**
- You need battle-tested production reliability
- You need 6+ platform support (Webex, Slack Huddles, GoTo)
- You want a desktop recording SDK (no visible bot)
- You need enterprise SLA/HIPAA compliance
- You don't need self-hosting

**Choose Google Meet Media API if:**
- You ONLY need Google Meet (no Teams/Zoom)
- You want the most "native" Google integration
- You want WebRTC-quality audio (not browser capture)
- You can wait for it to exit Developer Preview
- You have your own transcription pipeline

### Key Tradeoff
Vexa is the only option that combines: open-source + self-hostable + MCP server + built-in transcription + multi-platform. But it's younger and less battle-tested than Recall.ai, and the bot-visible-in-meeting UX is unavoidable with the Playwright approach.
