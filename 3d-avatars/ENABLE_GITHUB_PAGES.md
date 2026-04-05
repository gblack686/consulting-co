# 📄 Enable GitHub Pages - Step by Step

Your code is now on GitHub! Follow these simple steps to enable GitHub Pages so your web app is accessible.

## 🎯 Steps to Enable GitHub Pages

### 1. Open Your Repository Settings

Go to: **https://github.com/gblack686/consulting-co/settings**

Or:
1. Go to https://github.com/gblack686/consulting-co
2. Click the **"Settings"** tab at the top

### 2. Navigate to Pages

1. In the left sidebar, scroll down and click **"Pages"**
2. You'll see the GitHub Pages settings

### 3. Configure the Source

Under **"Build and deployment"** section:

1. **Source**: Select **"Deploy from a branch"**
2. **Branch**:
   - Select **"main"** from the dropdown
   - Select **"/ (root)"** from the folder dropdown
3. Click **"Save"**

### 4. Wait for Deployment (1-2 minutes)

GitHub will start building your site. You'll see:
- A message: "GitHub Pages source saved"
- After 1-2 minutes, refresh the page
- You'll see: "Your site is live at https://gblack686.github.io/consulting-co/"

### 5. Verify Web App is Accessible

Your web app will be at:

**https://gblack686.github.io/consulting-co/3d-avatars/webapp/**

Click this link to verify it loads. You should see:
- "🎨 Create Your 3D Avatar" header
- "Powered by Ready Player Me" subtitle
- A loading screen

**Note**: The Telegram-specific features won't work outside of Telegram, but you should see the page load.

## ✅ Once GitHub Pages is Enabled

Your `.env` file is already configured with the correct URL:
```
WEB_APP_URL=https://gblack686.github.io/consulting-co/3d-avatars/webapp/
```

You're ready to start the bot!

## 🚀 Start Your Bot

```bash
cd C:\Users\gblac\OneDrive\Desktop\consulting-co\3d-avatars\bot
npm start
```

You should see:
```
🤖 Bot is running...
🌐 Web App URL: https://gblack686.github.io/consulting-co/3d-avatars/webapp/
```

## 🧪 Test Your Bot

1. Open Telegram
2. Search for your bot (use the username you created with @BotFather)
3. Send `/start`
4. Click the **"🎨 Create My Avatar"** button
5. The web app will open inside Telegram
6. Customize your avatar!
7. Complete the creation
8. Your avatar URL will be sent back to the chat! 🎉

## 🐛 Troubleshooting

### GitHub Pages not showing up?
- Make sure you're on the **"Settings"** tab (not "Insights" or other tabs)
- Look for **"Pages"** in the left sidebar (scroll down if needed)
- If you don't see "Pages", make sure the repository is public

### Web app not loading after 5 minutes?
- Check that you selected **"main"** branch and **"/ (root)"** folder
- Go to the **"Actions"** tab to see if there are any build errors
- Make sure the files are pushed to GitHub (check the repo online)

### 404 Error when accessing the web app URL?
- Wait a few more minutes - first deployment can take up to 5 minutes
- Verify the exact URL: https://gblack686.github.io/consulting-co/3d-avatars/webapp/
- Check that `webapp/index.html` exists in your GitHub repo

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Telegram Web Apps Guide](https://core.telegram.org/bots/webapps)

---

**Need help?** Check the main **README.md** or **QUICKSTART.md** for more details!
