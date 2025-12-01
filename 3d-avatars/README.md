# 3D Avatar Telegram Bot

A Telegram bot that allows users to create personalized 3D avatars using Ready Player Me.

## 🎯 Features

- **Easy Avatar Creation**: Click a button in Telegram to open the avatar creator
- **Ready Player Me Integration**: Full-featured 3D avatar customization
- **Seamless Experience**: Web app opens directly in Telegram
- **Cross-Platform Avatars**: GLB models compatible with various platforms
- **No Backend Required**: Uses Ready Player Me's hosted iframe

## 📁 Project Structure

```
3d-avatars/
├── bot/                        # Telegram bot
│   ├── index.js               # Bot logic
│   ├── package.json           # Dependencies
│   ├── .env.example           # Environment variables template
│   └── .gitignore            # Git ignore file
├── webapp/                    # Web app (deploy to GitHub Pages)
│   └── index.html            # Single-page app with RPM iframe
├── POC_PLAN.md               # Original proof of concept plan
├── IMPLEMENTATION_GUIDE.md   # Detailed implementation guide
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Save the **bot token** you receive

### 2. Set Up the Bot

```bash
# Navigate to bot directory
cd 3d-avatars/bot

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

Edit `.env` and add your bot token:
```env
BOT_TOKEN=your_actual_bot_token_here
WEB_APP_URL=https://yourusername.github.io/consulting-co/3d-avatars/webapp/
```

### 3. Deploy the Web App

**Option A: GitHub Pages (Recommended for POC)**

1. Push this repo to GitHub
2. Go to repository Settings → Pages
3. Set source to `main` branch, `/3d-avatars/webapp` folder
4. Your web app will be at: `https://yourusername.github.io/consulting-co/3d-avatars/webapp/`

**Option B: Local Development with ngrok**

```bash
# Install ngrok if you haven't: https://ngrok.com/download

# Serve the webapp folder locally
cd 3d-avatars/webapp
python -m http.server 3067

# In another terminal, expose it with ngrok
ngrok http 3067

# Use the ngrok HTTPS URL in your .env file
```

### 4. Update Bot with Web App URL

Edit `bot/.env` and set:
```env
WEB_APP_URL=https://your-actual-url-here
```

### 5. Run the Bot

```bash
cd 3d-avatars/bot
npm start
```

You should see:
```
🤖 Bot is running...
🌐 Web App URL: https://...
```

### 6. Test It Out!

1. Open Telegram and search for your bot
2. Send `/start`
3. Click "🎨 Create My Avatar"
4. Customize your avatar in the web interface
5. Complete the creation process
6. Your avatar URL will be sent back to the Telegram chat!

## 🎨 How It Works

```
User clicks button in Telegram
         ↓
Telegram opens Web App (index.html)
         ↓
Web App loads Ready Player Me iframe
         ↓
User customizes avatar
         ↓
RPM generates avatar and returns URL
         ↓
Web App sends URL back to Telegram bot
         ↓
Bot receives and displays avatar URL
```

## 📝 Commands

- `/start` - Start the bot and get the avatar creation button
- `/help` - Show help message
- `/about` - Learn about the bot

## 🔧 Configuration

### Bot Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from BotFather | `123456:ABC-DEF...` |
| `WEB_APP_URL` | URL where webapp is hosted | `https://yourusername.github.io/...` |

### Ready Player Me Configuration

The web app uses the `demo` subdomain by default. To use your own:

1. Sign up at [Ready Player Me](https://readyplayer.me/)
2. Get your subdomain from the developer portal
3. Edit `webapp/index.html` and change:
   ```javascript
   const RPM_SUBDOMAIN = 'demo'; // Change to your subdomain
   ```

## 🛠️ Development

### Run bot in development mode with auto-reload:

```bash
cd 3d-avatars/bot
npm run dev
```

### Test the web app locally:

```bash
cd 3d-avatars/webapp
python -m http.server 3067
# Open http://localhost:3067 in browser
```

**Note**: Telegram WebApp features won't work outside of Telegram, but you can test the RPM iframe.

## 📚 Tech Stack

- **Bot**: Node.js + `node-telegram-bot-api`
- **Web App**: Vanilla HTML/CSS/JavaScript
- **Avatar Creation**: Ready Player Me iframe integration
- **Telegram Integration**: Telegram Web Apps SDK
- **Hosting**: GitHub Pages (or any static host)

## 🐛 Troubleshooting

### Bot doesn't respond
- Check that `BOT_TOKEN` is correct in `.env`
- Ensure bot is running (`npm start`)
- Check console for errors

### Web App button doesn't work
- Verify `WEB_APP_URL` is correct and accessible
- Must be HTTPS (GitHub Pages provides this automatically)
- Check browser console in Telegram for errors

### Avatar not sending back to bot
- Check that `web_app_data` handler in bot is working
- Verify Telegram WebApp SDK is loaded in HTML
- Check browser console for errors

### Ready Player Me iframe not loading
- Check internet connection
- Verify iframe `src` URL is correct
- Check browser console for CORS errors

## 🔗 Useful Links

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)
- [Ready Player Me Docs](https://readyplayer.me/developers)
- [Ready Player Me iframe Example](https://github.com/readyplayerme/Example-iframe)

## 📄 License

MIT

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## ✨ Future Enhancements

See `POC_PLAN.md` for planned features:
- Custom backend API
- Avatar gallery/history
- User profiles
- NFT minting integration
- IPFS storage
- Premium features
