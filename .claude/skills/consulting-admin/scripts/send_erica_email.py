"""Send next-steps email to Erica Cruz."""
import sys
import base64
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.google_client import gmail_service

BODY = """Hey Erica!

It was so great building with you today. Luna is taking shape — here's everything you need to do on your end to get us ready for launch.

1. Download the Claude app
Go to claude.ai and download the app (iOS or desktop). Start using it for your daily tasks — the more you use it now, the more familiar it'll feel when Luna is live.

2. Set up Google Photos backup on your iPhone
This lets your pottery photos automatically sync to Google Drive so Luna can access them for content drafts:
- Download the Google Photos app if you don't have it
- Open it → tap your profile photo (top right) → Photos settings → Backup → turn ON
- Set quality to "Storage saver" to avoid filling up Drive

3. Migrate your ChatGPT memory to Claude
Anthropic just released a memory import tool this month. In ChatGPT, go to Settings → Data Controls → Export data, download your memory, then import it into Claude. This carries over everything ChatGPT knows about you and your business.

4. Get your Shopify API key
So Luna can pull order and customer data:
- Shopify Admin → Apps → Develop apps → Create an app
- Name it "Luna Agent"
- Under Configuration, enable: Orders (read), Customers (read), Products (read)
- Hit Install, then copy the Admin API access token
- Send it to me and I'll add it securely

5. Set up Google Workspace for cruisecreations.com
This gets you a professional erica@cruisecreations.com email that Gmail will route through:
- Go to workspace.google.com → Get started
- Use your domain: cruisecreations.com
- Choose Business Starter ($6/month)
- Follow the DNS verification steps (takes ~15 min)

6. Keep Mailchimp for now — cancel once we go live
Once Luna's email workflows are running (drafting newsletters, FAQ replies, pickup notifications), you'll be able to cancel Mailchimp and save ~$50/month. I'll tell you exactly when it's safe to pull the plug.

---

I'm targeting ~2 weeks for deployment. Once I have your Shopify key and Google Workspace is set up, we're in great shape.

Any questions, just reply here or shoot me a message.

Talk soon,
Greg"""

def send():
    service = gmail_service()

    msg = MIMEText(BODY)
    msg["To"] = "artbycruzcreations@gmail.com"
    msg["Subject"] = "Your Luna Agent — Next Steps from Today's Session"

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print(f"Sent! Message ID: {result['id']}")

if __name__ == "__main__":
    send()
