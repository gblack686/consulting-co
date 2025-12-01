require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');

// Validate environment variables
if (!process.env.BOT_TOKEN) {
  console.error('❌ Error: BOT_TOKEN is not set in .env file');
  process.exit(1);
}

if (!process.env.WEB_APP_URL) {
  console.error('❌ Error: WEB_APP_URL is not set in .env file');
  console.log('💡 Tip: Set this to your GitHub Pages URL or ngrok URL');
  process.exit(1);
}

const token = process.env.BOT_TOKEN;
const webAppUrl = process.env.WEB_APP_URL;

// Create bot instance
const bot = new TelegramBot(token, { polling: true });

console.log('🤖 Bot is running...');
console.log(`🌐 Web App URL: ${webAppUrl}`);

// Handle /start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const firstName = msg.from.first_name || 'there';

  bot.sendMessage(
    chatId,
    `👋 Hello ${firstName}!\n\n` +
    `Welcome to the 3D Avatar Creator Bot!\n\n` +
    `Click the button below to design your personalized 3D avatar using Ready Player Me. ` +
    `You'll be able to customize your character's appearance, style, and more!\n\n` +
    `Once you're done, your avatar will be saved and you can use it across different platforms.`,
    {
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: '🎨 Create My Avatar',
              web_app: { url: webAppUrl }
            }
          ]
        ]
      }
    }
  );
});

// Handle /help command
bot.onText(/\/help/, (msg) => {
  const chatId = msg.chat.id;

  bot.sendMessage(
    chatId,
    `📖 *How to Use This Bot*\n\n` +
    `1️⃣ Click the "🎨 Create My Avatar" button\n` +
    `2️⃣ Customize your 3D avatar in the web interface\n` +
    `3️⃣ Your avatar will be saved automatically\n\n` +
    `*Commands:*\n` +
    `/start - Start the bot and create avatar\n` +
    `/help - Show this help message\n` +
    `/about - Learn about this bot`,
    { parse_mode: 'Markdown' }
  );
});

// Handle /about command
bot.onText(/\/about/, (msg) => {
  const chatId = msg.chat.id;

  bot.sendMessage(
    chatId,
    `ℹ️ *About This Bot*\n\n` +
    `This bot allows you to create personalized 3D avatars using Ready Player Me technology.\n\n` +
    `Your avatars are cross-platform compatible and can be used in various games and virtual worlds.\n\n` +
    `Powered by:\n` +
    `• Ready Player Me - Avatar creation\n` +
    `• Telegram Web Apps - Seamless integration\n` +
    `• Node.js - Bot backend`,
    { parse_mode: 'Markdown' }
  );
});

// Handle data sent from Web App
bot.on('message', (msg) => {
  // Check if message contains web_app_data
  if (msg.web_app_data) {
    const chatId = msg.chat.id;

    try {
      const data = JSON.parse(msg.web_app_data.data);

      if (data.avatarUrl) {
        console.log(`✅ Received avatar URL from user ${msg.from.id}: ${data.avatarUrl}`);

        // Send confirmation with avatar URL
        bot.sendMessage(
          chatId,
          `✨ *Avatar Created Successfully!*\n\n` +
          `Your 3D avatar is ready! Here's your avatar URL:\n\n` +
          `\`${data.avatarUrl}\`\n\n` +
          `You can use this URL to display your avatar in compatible applications.\n\n` +
          `Want to create another avatar? Just use /start again!`,
          { parse_mode: 'Markdown' }
        );

        // Optionally send the GLB model as a document
        // Note: Telegram might not preview 3D models directly
        bot.sendDocument(chatId, data.avatarUrl, {
          caption: '📦 Your 3D Avatar Model (GLB format)'
        }).catch(err => {
          console.log('Note: Could not send GLB as document:', err.message);
        });
      }
    } catch (error) {
      console.error('❌ Error parsing web app data:', error);
      bot.sendMessage(
        chatId,
        '⚠️ There was an error processing your avatar. Please try again.'
      );
    }
  }
});

// Handle errors
bot.on('polling_error', (error) => {
  console.error('❌ Polling error:', error.code, error.message);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down bot...');
  bot.stopPolling();
  process.exit(0);
});
