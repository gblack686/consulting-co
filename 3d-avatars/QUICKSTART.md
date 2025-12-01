# 🚀 Quick Start Guide - 3D Avatar Bot

Get your 3D Avatar Telegram bot running in **less than 10 minutes**!

## ✅ Prerequisites

- Node.js installed (v14 or higher)
- A Telegram account
- A GitHub account (for hosting the web app)

## 📋 Step-by-Step Setup

### Step 1: Create Your Telegram Bot (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Send this message: `/newbot`
3. Choose a name for your bot (e.g., "My Avatar Creator")
4. Choose a username (must end in 'bot', e.g., "my_avatar_creator_bot")
5. **Save the token** you receive - it looks like: `123456789:ABCdefGhIjKlmNoPQRsTUVwxyZ`

### Step 2: Install Bot Dependencies (1 minute)

```bash
cd 3d-avatars/bot
npm install
```

### Step 3: Configure Environment Variables (1 minute)

```bash
# Copy the example file
cp .env.example .env

# Edit .env file
```

Add your bot token:
```env
BOT_TOKEN=123456789:ABCdefGhIjKlmNoPQRsTUVwxyZ
WEB_APP_URL=https://yourusername.github.io/consulting-co/3d-avatars/webapp/
```

**Note**: We'll update `WEB_APP_URL` after deploying in the next step.

### Step 4: Deploy Web App to GitHub Pages (3 minutes)

**Option A: GitHub Pages (Recommended)**

1. Make sure your repo is on GitHub
2. Go to your repo settings: `https://github.com/yourusername/consulting-co/settings`
3. Click **Pages** in the left sidebar
4. Under "Source", select **main** branch
5. Click **Save**
6. Wait 1-2 minutes for deployment
7. Your web app will be at: `https://yourusername.github.io/consulting-co/3d-avatars/webapp/`

**Update your .env file** with this URL:
```env
WEB_APP_URL=https://yourusername.github.io/consulting-co/3d-avatars/webapp/
```

**Option B: Quick Local Testing with ngrok**

```bash
# In one terminal - serve the webapp
cd 3d-avatars/webapp
python -m http.server 3067

# In another terminal - expose with ngrok
ngrok http 3067

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io) to your .env
```

### Step 5: Start Your Bot (30 seconds)

```bash
cd 3d-avatars/bot
npm start
```

You should see:
```
🤖 Bot is running...
🌐 Web App URL: https://...
```

### Step 6: Test It! (2 minutes)

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Click the **"🎨 Create My Avatar"** button
5. Customize your avatar
6. Complete the creation
7. See your avatar URL in the chat! 🎉

## 🎯 Verification Checklist

- [ ] Bot responds to `/start` command
- [ ] Button appears in the chat
- [ ] Clicking button opens web app
- [ ] Ready Player Me loads successfully
- [ ] Can customize avatar
- [ ] Avatar URL is sent back to chat

## 🐛 Common Issues

### "Bot doesn't respond"
- **Check**: Is the bot running? (`npm start`)
- **Check**: Is your `BOT_TOKEN` correct in `.env`?
- **Fix**: Restart the bot

### "Web app button does nothing"
- **Check**: Is `WEB_APP_URL` an HTTPS URL?
- **Check**: Can you access the URL in a browser?
- **Fix**: Make sure GitHub Pages is deployed or ngrok is running

### "Ready Player Me doesn't load"
- **Check**: Internet connection
- **Check**: Browser console for errors (right-click → Inspect → Console)
- **Fix**: Try refreshing the web app

### "Avatar doesn't send to bot"
- **Check**: Bot console for errors
- **Check**: Telegram web app console for errors
- **Fix**: Make sure you complete the entire avatar creation process

## 🎨 Customization Tips

### Change the bot messages

Edit `bot/index.js` and modify the text in the `sendMessage` calls.

### Use your own Ready Player Me subdomain

1. Sign up at [readyplayer.me](https://readyplayer.me/)
2. Get your subdomain from the developer portal
3. Edit `webapp/index.html`:
   ```javascript
   const RPM_SUBDOMAIN = 'your-subdomain'; // Change this
   ```

### Customize the web app appearance

Edit `webapp/index.html` - all styles are in the `<style>` section!

## 📚 What to Do Next

Once your bot is working:

1. **Read the full README** for more details
2. **Check out IMPLEMENTATION_GUIDE.md** for advanced features
3. **Review POC_PLAN.md** for future enhancement ideas
4. **Customize the UI** to match your brand
5. **Add your own features** (avatar gallery, storage, etc.)

## 🆘 Need Help?

- Check the main **README.md** for detailed troubleshooting
- Review **IMPLEMENTATION_GUIDE.md** for implementation details
- Check Telegram Web Apps docs: https://core.telegram.org/bots/webapps
- Check Ready Player Me docs: https://readyplayer.me/developers

---

**Congratulations! 🎉 Your 3D Avatar bot is now live!**
