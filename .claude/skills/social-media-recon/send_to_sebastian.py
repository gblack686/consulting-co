"""
Send social-media-recon SKILL.md to greg@gbautomation.xyz with deployment
instructions for Sebastian (Mac Mini).
"""
import sys, os, base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Add consulting-admin scripts to path for google_client auth
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "consulting-admin"))
from scripts import google_client

SENDER = "Greg Black | GBAutomation <greg@gbautomation.xyz>"
TO = "greg@gbautomation.xyz"
SUBJECT = "Sebastian: Social Media Recon Skill — Deploy to Mac Mini"

SKILL_PATH = os.path.join(os.path.dirname(__file__), "SKILL.md")

BODY_HTML = """\
<html>
<body style="font-family: Arial, sans-serif; color: #2D2D2D; line-height: 1.6;">

<h2 style="color: #D97757;">Social Media Recon Skill for Sebastian</h2>

<p>Attached: <strong>SKILL.md</strong> &mdash; a browser-native social media research skill
that uses <strong>Steer</strong> (macOS GUI automation) instead of Chrome DevTools MCP.</p>

<h3 style="color: #D97757; border-bottom: 2px solid #D97757; padding-bottom: 6px;">
What It Does</h3>
<ul>
  <li>Researches people <strong>for Patrick Bauer</strong> (pbauer) &mdash; his clients/prospects</li>
  <li>Instagram deep dive &mdash; profile metadata, post grid screenshots, <strong>verbatim caption reading</strong> via OCR, engagement analysis</li>
  <li>Facebook research &mdash; profile, about section, recent public posts, life events</li>
  <li>Produces <code>personal-intel.md</code> + screenshots + Telegram summary</li>
  <li>All output saved to <code>~/.openclaw/workspace/gbauto/pbauer/{slug}/instagram/</code> etc.</li>
  <li>Triggerable remotely via Listen job server or Telegram message</li>
</ul>

<h3 style="color: #D97757; border-bottom: 2px solid #D97757; padding-bottom: 6px;">
Deployment Steps</h3>
<ol>
  <li><strong>Clone gbauto repos</strong> &mdash; all GBAutomation client repos:
    <pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
cd ~/.openclaw/workspace
gh repo list gbauto --limit 100 --json name -q '.[].name' | \\
  xargs -I{} gh repo clone gbauto/{} gbauto/{}
    </pre>
  </li>
  <li><strong>One-time Safari auth</strong> &mdash; On the Mac Mini, open Safari and manually log into:
    <ul>
      <li><code>https://www.instagram.com</code> &mdash; approve 2FA, check "Remember me"</li>
      <li><code>https://www.facebook.com</code> &mdash; approve 2FA, check "Remember me"</li>
    </ul>
  </li>
  <li><strong>Copy the skill</strong> &mdash; place SKILL.md into Sebastian's workspace:
    <pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
mkdir -p ~/.openclaw/workspace/skills/social-media-recon
cp SKILL.md ~/.openclaw/workspace/skills/social-media-recon/SKILL.md
    </pre>
  </li>
  <li><strong>Verify Steer works</strong>:
    <pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
steer see --app Safari --json | head -5
steer ocr --app Safari --store | head -10
    </pre>
  </li>
  <li><strong>Restart gateway</strong>:
    <pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
sleep 4
openclaw skills list  # should show social-media-recon
    </pre>
  </li>
  <li><strong>Test it</strong> &mdash; send via Telegram or Listen:
    <pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
just send "social recon: Aidan Pinter @aidanpinter - IG + FB"
    </pre>
  </li>
</ol>

<h3 style="color: #D97757; border-bottom: 2px solid #D97757; padding-bottom: 6px;">
Output Structure</h3>
<pre style="background: #F3F1E7; padding: 12px; border-radius: 6px; font-size: 13px;">
~/.openclaw/workspace/gbauto/pbauer/{slug}/
  instagram/   &larr; screenshots, profile data, captions
  linkedin/    &larr; profile research
  facebook/    &larr; profile, timeline, about section
  personal-intel.md
</pre>

<h3 style="color: #D97757; border-bottom: 2px solid #D97757; padding-bottom: 6px;">
Why Sebastian Instead of Windows MCP</h3>
<ul>
  <li>No Chrome profile conflicts ("browser already running" errors)</li>
  <li>Safari stays permanently logged in &mdash; no 2FA interruptions</li>
  <li>Steer OCR reads captions natively (no fragile DOM selectors)</li>
  <li>Listen server (port 7600) = trigger research jobs remotely from Windows</li>
  <li>Screenshots via <code>steer see</code> are higher fidelity than MCP snapshots</li>
</ul>

<p style="color: #888; font-size: 13px; margin-top: 24px; border-top: 1px solid #E8E5DA; padding-top: 12px;">
Sent from Claude Code &mdash; GBAutomation consulting-co workspace
</p>

</body>
</html>
"""

BODY_TEXT = """\
Social Media Recon Skill for Sebastian (Mac Mini)

Attached: SKILL.md

This skill researches people FOR Patrick Bauer (pbauer) — his clients/prospects.
Output goes to: ~/.openclaw/workspace/gbauto/pbauer/{slug}/instagram/ etc.

Deployment:
1. Clone gbauto repos: gh repo list gbauto ... | xargs gh repo clone
2. Log into Instagram + Facebook on Safari (one-time, manual)
3. Copy SKILL.md to ~/.openclaw/workspace/skills/social-media-recon/
4. Verify: steer see --app Safari --json
5. Restart gateway: launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
6. Test: just send "social recon: Aidan Pinter @aidanpinter - IG + FB"

The skill uses Steer (GUI automation) instead of Chrome DevTools MCP.
No profile conflicts, permanent Safari auth, OCR-based caption reading.
"""


def main():
    gmail = google_client.gmail_service()

    # Build multipart/mixed message (text + attachment)
    msg = MIMEMultipart("mixed")
    msg["to"] = TO
    msg["from"] = SENDER
    msg["subject"] = SUBJECT

    # Body (alternative: text + html)
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(BODY_TEXT, "plain"))
    alt.attach(MIMEText(BODY_HTML, "html"))
    msg.attach(alt)

    # Attach SKILL.md
    with open(SKILL_PATH, "rb") as f:
        attachment = MIMEBase("text", "markdown")
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", "attachment",
            filename="social-media-recon-SKILL.md"
        )
        msg.attach(attachment)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent! Message ID: {result['id']}")
    return result["id"]


if __name__ == "__main__":
    main()
