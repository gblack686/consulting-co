# 3D Avatar Implementation Guide

Based on research of Ready Player Me and Telegram Web App examples.

## 🎯 Key Insights from Research

### Ready Player Me Integration Options

1. **iframe Approach (Simplest for POC)**
   - Embed Ready Player Me avatar creator directly in your web app
   - Use `https://readyplayer.me/` iframe
   - Receive avatar URL via message-passing protocol
   - No backend needed for avatar generation

2. **Visage Library (For Custom Display)**
   ```javascript
   import { Avatar } from '@readyplayerme/visage';

   function App() {
     const modelUrl = 'https://readyplayerme.github.io/visage/male.glb';
     return <Avatar modelSrc={modelUrl} />;
   }
   ```
   - Built on three.js and react-three-fiber
   - Supports `.glb` and `.fbx` formats
   - Can load from URLs, base64, or binary data

3. **Other RPM Resources**
   - `rpm-react-avatar-creator` - React wrapper for avatar creator
   - Animation Library (537 stars) - Pre-built avatar animations
   - Official docs: https://readyplayer.me/developers

### Telegram Web App Integration Patterns

1. **Basic Setup (from vanilla-js-boilerplate)**
   ```html
   <script src="https://telegram.org/js/telegram-web-app.js"></script>
   ```
   - Access via `window.Telegram.WebApp`
   - No build tools needed for basic implementation
   - Deploy to GitHub Pages for easy hosting

2. **Bot Configuration**
   - Create bot with BotFather
   - Add web app URL via BotFather menu settings
   - Two access methods:
     - Menu button in bot bio
     - Inline keyboard button with `web_app` field

3. **Data Flow**
   - User clicks button in Telegram → Opens Web App
   - Web App uses Telegram.WebApp API for bidirectional communication
   - Authentication inherited from Telegram session (no custom auth needed)

## 🔧 Recommended Implementation Strategy

### Phase 1: Minimal Viable Product (Current POC Plan)

**Use iframe approach for speed:**

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
  <!-- Ready Player Me iframe -->
  <iframe
    id="rpm-frame"
    src="https://readyplayer.me/avatar"
    allow="camera *; microphone *"
    style="width: 100%; height: 100vh; border: none;">
  </iframe>

  <script>
    // Listen for avatar URL from RPM
    window.addEventListener('message', (event) => {
      if (event.data?.source === 'readyplayerme') {
        const avatarUrl = event.data.url;

        // Send back to Telegram bot
        window.Telegram.WebApp.sendData(JSON.stringify({
          avatarUrl: avatarUrl
        }));
      }
    });
  </script>
</body>
</html>
```

**Benefits:**
- No backend needed for avatar generation
- Ready Player Me handles all customization UI
- Telegram handles authentication
- Can be deployed to GitHub Pages immediately

### Phase 2: Custom UI (Future Enhancement)

Once iframe POC works, upgrade to custom UI:

1. Build custom HTML/CSS/JS interface with specific options
2. Use Ready Player Me API directly (requires backend)
3. Display preview with Google `<model-viewer>` or Visage
4. Store avatar metadata in your own database

## 📁 Simplified File Structure for POC

```
3d-avatars/
├── bot/
│   ├── index.js           # Telegram bot with Web App button
│   ├── package.json
│   └── .env              # Bot token
├── webapp/
│   └── index.html        # Single-file web app with RPM iframe
└── POC_PLAN.md
```

**No backend needed** for initial POC since RPM iframe handles everything!

## 🚀 Quick Start Steps

1. **Create Telegram Bot**
   ```bash
   # Talk to @BotFather on Telegram
   /newbot
   # Save the token to .env
   ```

2. **Create Simple Bot Script**
   ```javascript
   const TelegramBot = require('node-telegram-bot-api');
   const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });

   bot.onText(/\/start/, (msg) => {
     bot.sendMessage(msg.chat.id, 'Design your avatar!', {
       reply_markup: {
         inline_keyboard: [[
           {
             text: '🎨 Create Avatar',
             web_app: { url: 'https://yourusername.github.io/3d-avatars/' }
           }
         ]]
       }
     });
   });
   ```

3. **Deploy Web App to GitHub Pages**
   - Push `webapp/index.html` to GitHub
   - Enable GitHub Pages in repo settings
   - Update bot with your GitHub Pages URL

4. **Test End-to-End**
   - Open bot in Telegram
   - Click "Create Avatar" button
   - Customize avatar in RPM iframe
   - Avatar URL sent back to bot
   - Bot can store URL or send preview

## 🎨 Inspiration Resources

### Example Bots (from ChatGPT convo)
- `telegram-web-app-bot-example` - Clean base for embedding custom UI
- `StableDiffusionTelegram` - Media generation + Telegram UX
- `segmind_telebot` - External API + Telegram pipeline

### High-Quality Avatar Examples
- AAA Game Art Studio portfolios
- Ready Player Me gallery
- CGTrader game-ready characters

## 📋 Next Actions

1. ✅ Set up Telegram bot with BotFather
2. ✅ Create minimal HTML with RPM iframe
3. ✅ Add Telegram WebApp SDK script
4. ✅ Deploy to GitHub Pages
5. ✅ Connect bot to web app URL
6. ✅ Test complete flow
7. 🔄 Iterate on UI/UX based on testing

## 🔗 Key Links

- Ready Player Me Docs: https://readyplayer.me/developers
- Telegram Web Apps API: https://core.telegram.org/bots/webapps
- Vanilla JS Boilerplate: https://github.com/telegram-mini-apps-dev/vanilla-js-boilerplate
- RPM iframe Example: https://github.com/readyplayerme/Example-iframe
- Visage (Display Library): https://github.com/readyplayerme/visage

---

**Note:** This approach is **much simpler** than the original POC plan because we're leveraging Ready Player Me's hosted iframe instead of building a custom backend. This gets us to a working prototype faster!
