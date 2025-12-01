#!/usr/bin/env node

/**
 * Setup Verification Script
 * Run this to check if your bot configuration is correct
 */

require('dotenv').config();
const https = require('https');
const http = require('http');

console.log('\n🔍 Verifying 3D Avatar Bot Setup...\n');

let hasErrors = false;

// Check 1: Environment Variables
console.log('1️⃣ Checking environment variables...');

if (!process.env.BOT_TOKEN) {
  console.error('   ❌ BOT_TOKEN is not set in .env file');
  hasErrors = true;
} else if (process.env.BOT_TOKEN === 'your_bot_token_here') {
  console.error('   ❌ BOT_TOKEN is still the placeholder value');
  console.log('   💡 Get your token from @BotFather on Telegram');
  hasErrors = true;
} else if (!process.env.BOT_TOKEN.match(/^\d+:[A-Za-z0-9_-]+$/)) {
  console.error('   ❌ BOT_TOKEN format looks incorrect');
  console.log('   💡 Should be like: 123456789:ABCdefGhIjKlmNoPQRsTUVwxyZ');
  hasErrors = true;
} else {
  console.log('   ✅ BOT_TOKEN is set and looks valid');
}

if (!process.env.WEB_APP_URL) {
  console.error('   ❌ WEB_APP_URL is not set in .env file');
  hasErrors = true;
} else if (process.env.WEB_APP_URL === 'your_web_app_url_here') {
  console.error('   ❌ WEB_APP_URL is still the placeholder value');
  console.log('   💡 Deploy webapp to GitHub Pages and use that URL');
  hasErrors = true;
} else if (!process.env.WEB_APP_URL.startsWith('https://')) {
  console.error('   ❌ WEB_APP_URL must be HTTPS (required by Telegram)');
  console.log('   💡 Use GitHub Pages or ngrok for HTTPS');
  hasErrors = true;
} else {
  console.log('   ✅ WEB_APP_URL is set and uses HTTPS');
}

console.log('');

// Check 2: Dependencies
console.log('2️⃣ Checking dependencies...');

try {
  require('node-telegram-bot-api');
  console.log('   ✅ node-telegram-bot-api is installed');
} catch (error) {
  console.error('   ❌ node-telegram-bot-api is not installed');
  console.log('   💡 Run: npm install');
  hasErrors = true;
}

try {
  require('dotenv');
  console.log('   ✅ dotenv is installed');
} catch (error) {
  console.error('   ❌ dotenv is not installed');
  console.log('   💡 Run: npm install');
  hasErrors = true;
}

console.log('');

// Check 3: Web App Accessibility
if (process.env.WEB_APP_URL && process.env.WEB_APP_URL.startsWith('https://')) {
  console.log('3️⃣ Checking web app accessibility...');

  const url = new URL(process.env.WEB_APP_URL);
  const protocol = url.protocol === 'https:' ? https : http;

  protocol.get(process.env.WEB_APP_URL, (res) => {
    if (res.statusCode === 200) {
      console.log('   ✅ Web app is accessible (HTTP 200)');

      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (data.includes('telegram-web-app.js')) {
          console.log('   ✅ Telegram WebApp SDK detected');
        } else {
          console.log('   ⚠️  Warning: Telegram WebApp SDK script not found');
        }

        if (data.includes('readyplayer.me')) {
          console.log('   ✅ Ready Player Me integration detected');
        } else {
          console.log('   ⚠️  Warning: Ready Player Me iframe not found');
        }

        printSummary();
      });
    } else {
      console.error(`   ❌ Web app returned HTTP ${res.statusCode}`);
      console.log('   💡 Make sure your GitHub Pages is deployed or ngrok is running');
      hasErrors = true;
      printSummary();
    }
  }).on('error', (error) => {
    console.error(`   ❌ Cannot access web app: ${error.message}`);
    console.log('   💡 Check that the URL is correct and accessible');
    hasErrors = true;
    printSummary();
  });
} else {
  console.log('3️⃣ Skipping web app check (invalid URL)\n');
  printSummary();
}

// Print summary
function printSummary() {
  console.log('\n' + '='.repeat(50));

  if (hasErrors) {
    console.log('\n❌ Setup has issues - please fix the errors above\n');
    console.log('📖 Check QUICKSTART.md for setup instructions\n');
    process.exit(1);
  } else {
    console.log('\n✅ All checks passed! Your bot is ready to run!\n');
    console.log('🚀 Start your bot with: npm start\n');
    console.log('📱 Then open Telegram and send /start to your bot\n');
    process.exit(0);
  }
}
