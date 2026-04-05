# Tools — Cruz Creations Agent

## Connected (API Available)

| Tool | Use | Status |
|------|-----|--------|
| Gmail API | Draft + send workshop emails, FAQ responses, newsletters | Needs OAuth setup with erica@cruisecreations.com |
| Google Calendar API | Read events, send calendar summaries in morning brief | Needs OAuth |
| Google Drive API | Save workshop photos, organize content library | Needs OAuth |
| Google Forms / Sheets API | Read QR code form submissions (attendee data) | Needs OAuth |
| Shopify Admin API | Update products, pricing, collections on cruisecreations.com | Needs API key from Shopify admin |
| WhatsApp Business API | Receive Erica's messages, send morning brief and notifications | Needs Meta Business account or Twilio sandbox |
| OpenRouter API | Power all LLM calls for Luna and sub-agents | Set via: `openclaw secrets set OPENROUTER_API_KEY <key>` |

## Browser-Automated (No API)

| Tool | Use | Method |
|------|-----|--------|
| ClassBento | Check ticket sales, view registrations, post new workshops | Browser automation — agent logs in, navigates UI |
| Canva (optional) | Generate event flyers from templates | Canva Connect API (limited) OR browser automation |

## Planned (Phase 2+)

| Tool | Use | Notes |
|------|-----|-------|
| Instagram Graph API | Post reels/images, read analytics | Requires Meta Business account + app review |
| TikTok for Developers | Post videos, read analytics | Limited posting API; easier for analytics |
| iCloud / Google Photos | Auto-backup iPhone camera roll | Google Photos app on iPhone with Backup & Sync |
| Remotion | Batch-render workshop recap videos | Phase 3 — requires React template build |

## Secrets Setup

```bash
# Required for Phase 1 launch:
openclaw secrets set OPENROUTER_API_KEY <key>
openclaw secrets set GMAIL_CLIENT_ID <id>
openclaw secrets set GMAIL_CLIENT_SECRET <secret>
openclaw secrets set SHOPIFY_API_KEY <key>
openclaw secrets set SHOPIFY_API_SECRET <secret>
openclaw secrets set WHATSAPP_API_TOKEN <token>

# Phase 2:
openclaw secrets set CLASSBENTO_EMAIL artbycruzcreations@gmail.com
openclaw secrets set CLASSBENTO_PASSWORD <password>
openclaw secrets set INSTAGRAM_ACCESS_TOKEN <token>
```

## Replacing Mailchimp

Luna handles all newsletter functions natively:
- Consumer newsletter → drafted by `newsletter-email` agent, sent via Gmail
- Artist community → separate Gmail draft, manually reviewed before send
- No external platform needed → saves $50/month immediately
