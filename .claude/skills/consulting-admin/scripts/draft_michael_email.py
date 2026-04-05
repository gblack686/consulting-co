"""
Create a Gmail draft to Michael Fisch with:
- agency_comparison.png attached
- fish_group_deployment_report.html attached
- Architecture diagram PNG inlined in body
"""
import sys
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.google_client import gmail_service

OUTPUT = Path(__file__).parent.parent / "output"
CHART_PNG = OUTPUT / "agency_comparison.png"
REPORT_HTML = OUTPUT / "fish_group_deployment_report.html"

BODY_HTML = """\
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 640px; color: #1a1a1a;">

<p>Hey Mike,</p>

<p>Great session today — really good to catch up. Following up with the materials we discussed, plus a breakdown of the different ways you can deploy and interact with the AI stack we're building.</p>

<h3 style="margin-top:24px; font-size:16px;">📊 Agency Comparison Chart</h3>
<p style="font-size:14px; color:#444;">Where n8n, Claude Code, and OpenClaw sit on the autonomy spectrum — and where Fish Group should land in each phase:</p>
<img src="cid:agency_chart" style="width:100%; border-radius:8px; margin:8px 0 20px;" alt="Agency Comparison Chart"/>

<h3 style="font-size:16px;">📋 Attached: Architecture & Deployment Options Report</h3>
<p style="font-size:14px; color:#444;">The HTML report covers all four deployment options in detail:</p>
<ul style="font-size:14px; color:#444; line-height:1.8;">
  <li><strong>Option 1 — Local Dev</strong>: Claude Code on your laptop (start here this week)</li>
  <li><strong>Option 2 — Claude Pro Seats</strong>: Good for team writing, not automation</li>
  <li><strong>Option 3 — EC2 + OpenClaw</strong>: Always-on autonomous agent in the cloud</li>
  <li><strong>Option 4 — Hybrid</strong>: Local dev + EC2 cloud (recommended for Fish Group)</li>
</ul>

<h3 style="font-size:16px; margin-top:24px;">✅ Your Next Steps Before We Meet Again</h3>
<ol style="font-size:14px; color:#444; line-height:2.0;">
  <li><strong>Get hands dirty with Claude Code</strong> — try one small thing: read a Gmail thread, pull an Airtable record, whatever. Build the muscle memory.</li>
  <li><strong>Generate an Airtable personal access token</strong> — Airtable → Account → Developer Hub → Personal access tokens. Send it to me.</li>
  <li><strong>Set up your first AWS account</strong> — I'll send you the per-client account strategy + my AWS contact separately.</li>
  <li><strong>Map Piermont's 2-3 most painful manual steps</strong> — specifically in the shipment request → ShipStation flow. We'll scope those as the first skills in our follow-up.</li>
  <li><strong>Send me Emil's email</strong> — want to CC him on everything going forward.</li>
</ol>

<h3 style="font-size:16px; margin-top:24px;">🗓 Let's Schedule the Follow-Up</h3>
<p style="font-size:14px; color:#444;">I'm thinking 60-90 min, focused on: EC2 setup + first skill deployment (client onboarding). Once that's live, Finn 🐟 is operational. Let me know your availability.</p>

<p style="font-size:14px; color:#444;">Invoice coming in a separate email.</p>

<p style="margin-top:24px; font-size:14px;">Talk soon,<br/>Greg</p>

<p style="font-size:12px; color:#999; margin-top:32px; border-top:1px solid #eee; padding-top:12px;">
  P.S. — Yes, Claude wrote this email. But the ideas are mine. 🤖
</p>
</div>
"""

def create_draft():
    service = gmail_service()

    msg = MIMEMultipart("related")
    # Michael's email not captured in transcript — draft addressed to self for now
    # Update To field before sending
    msg["To"] = "gbautomationbusiness@gmail.com"
    msg["X-Draft-Note"] = "UPDATE To: field with Michael's email before sending"
    msg["Subject"] = "Fish Group — Architecture Options + Agency Chart"

    # Multipart alternative for HTML body
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(BODY_HTML, "html"))
    msg.attach(alt)

    # Inline chart image (CID reference)
    with open(CHART_PNG, "rb") as f:
        img = MIMEImage(f.read(), _subtype="png")
        img.add_header("Content-ID", "<agency_chart>")
        img.add_header("Content-Disposition", "inline", filename="agency_comparison.png")
        msg.attach(img)

    # Attach HTML report as file
    with open(REPORT_HTML, "rb") as f:
        html_attachment = MIMEBase("application", "octet-stream")
        html_attachment.set_payload(f.read())
        encoders.encode_base64(html_attachment)
        html_attachment.add_header(
            "Content-Disposition", "attachment",
            filename="Fish_Group_Deployment_Options.html"
        )
        msg.attach(html_attachment)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    print(f"Draft created! ID: {draft['id']}")
    print(f"Open in Gmail: https://mail.google.com/mail/#drafts/{draft['id']}")

if __name__ == "__main__":
    create_draft()
