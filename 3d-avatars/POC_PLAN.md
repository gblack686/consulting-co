# POC Plan: Telegram Button → 3D Avatar Render

## Architecture Overview

**Flow**: Telegram Bot → Web App → Backend API → Ready Player Me → 3D Model Viewer

## Implementation Steps

### 1. Telegram Bot Setup `(3d-avatars/bot/)`
- Create a Telegram bot using BotFather
- Implement a "Design Avatar" button that opens a Web App
- Use `node-telegram-bot-api` or similar library
- Store bot token in `.env`

### 2. Web App Frontend `(3d-avatars/webapp/)`
- Simple HTML/CSS/JS interface (no complex framework for POC)
- Basic customization options:
  - Avatar style (masculine/feminine/neutral)
  - Hair style/color picker
  - Outfit selection
- "Generate Avatar" button
- Embed `<model-viewer>` component for 3D preview
- Use Telegram Web Apps SDK to communicate back to bot

### 3. Backend API `(3d-avatars/api/)`
- Express.js server (random port: 3067)
- Endpoints:
  - `POST /api/avatar/generate` - Receives customization params
  - `GET /api/avatar/:id` - Retrieves generated avatar data
- Integrates with Ready Player Me API
- Stores avatar URLs and metadata temporarily

### 4. Ready Player Me Integration
- Use their REST API (simplest approach)
- Generate avatar from parameters
- Receive GLB model URL back
- No custom 3D generation needed for POC

### 5. 3D Viewer Implementation
- Use Google's `<model-viewer>` web component
- Embed in Web App to display GLB models
- Basic controls: rotate, zoom
- Fullscreen preview option

### 6. Complete Flow
```
User clicks "Design Avatar" in Telegram
  ↓
Web App opens with customization UI
  ↓
User selects options and clicks "Generate"
  ↓
Backend calls Ready Player Me API
  ↓
Ready Player Me returns GLB model URL
  ↓
Web App displays 3D model in viewer
  ↓
User can view/rotate avatar in real-time
  ↓
Optional: Send preview image back to Telegram chat
```

## Technology Stack
- **Bot**: Node.js + `node-telegram-bot-api`
- **Web App**: Vanilla HTML/CSS/JS + Telegram Web Apps SDK
- **Backend**: Express.js
- **Avatar API**: Ready Player Me (free tier)
- **3D Viewer**: Google Model Viewer
- **Hosting**: Local for POC (ngrok for Telegram webhook)

## Key Files Structure
```
3d-avatars/
├── bot/
│   ├── index.js           # Telegram bot logic
│   └── package.json
├── webapp/
│   ├── index.html         # Web App UI
│   ├── style.css
│   └── app.js            # Frontend logic
├── api/
│   ├── server.js         # Express API
│   ├── routes/
│   │   └── avatar.js     # Avatar endpoints
│   └── package.json
└── .env                  # Bot token, API keys
```

## Minimal Viable Features
1. ✅ Single button in Telegram that opens Web App
2. ✅ 3 basic customization options (style, hair, outfit)
3. ✅ Call Ready Player Me API with params
4. ✅ Display 3D model in web viewer
5. ✅ Rotate/zoom controls

## What's Explicitly Skipped for POC
- ❌ NFT minting
- ❌ IPFS storage
- ❌ User authentication/profiles
- ❌ Avatar gallery/history
- ❌ Custom 3D generation (using RPM instead)
- ❌ Payment/premium features

## Next Steps
1. Set up Telegram bot with Web App button
2. Create simple Web App UI for avatar customization
3. Integrate Ready Player Me API for avatar generation
4. Build backend to handle avatar generation requests
5. Implement 3D model viewer in Web App
6. Connect all components and test end-to-end flow

## Reference Resources
- Ready Player Me API: https://readyplayer.me/
- Telegram Web Apps: https://core.telegram.org/bots/webapps
- Google Model Viewer: https://modelviewer.dev/
- Telegram Bot API: https://core.telegram.org/bots/api
