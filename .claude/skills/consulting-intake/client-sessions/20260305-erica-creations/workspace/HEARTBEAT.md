# Heartbeat — Luna 🌙

Luna checks in and runs scheduled tasks on a cycle, like the moon.

## Daily Beats

### Morning Brief — 8:00 AM PST
```
openclaw cron add "morning-brief" "0 8 * * *"
```
**Trigger**: Every day at 8am PST
**Actions**:
1. Check Gmail for priority emails (unread, flagged, mentions of "pickup" or "event")
2. Pull today's Google Calendar events
3. Fetch current moon phase (lunar API or web search)
4. Pull one art/business-of-art headline from web
5. Generate a morning pages journaling prompt (inspired by The Artist's Way)
6. Send summary to Erica via WhatsApp

**Format**:
```
Good morning Erica ☀️

🌙 Moon: Waxing Gibbous (75% full)

📬 Emails needing attention (2):
  - Rachel asks about pickup for Feb workshop
  - ClassBento: new ticket sale for March 22nd

📅 Today:
  - 3pm: Studio time blocked

📰 Art world: [headline]

✍️ Morning pages prompt: What would you create today if no one was watching?
```

### Weekly Workshop Check — Every Monday 9:00 AM PST
```
openclaw cron add "workshop-check" "0 9 * * 1"
```
**Actions**:
1. Check ClassBento (browser automation) for upcoming workshop registrations
2. Check Google Forms for recent QR code submissions
3. Draft weekly recap for Erica: attendee counts, pickup status, upcoming events

### Monthly Newsletter Draft — 1st of each month, 10:00 AM PST
```
openclaw cron add "newsletter-draft" "0 10 1 * *"
```
**Actions**:
1. Pull last month's workshop dates, attendee count, any new Shopify products
2. Check social media highlights (most-viewed post of the month)
3. Draft two newsletter versions: consumer (upcoming events) + artist community
4. Send drafts to Erica via WhatsApp with "Ready for review"

## Heartbeat to Main Agent
Every 15 minutes, Luna sends a heartbeat to herself to stay alive and check for urgent messages.

```json
{
  "every": "15m",
  "target": "main",
  "ackMaxChars": 300
}
```
