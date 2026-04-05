# Open Questions from Session — Erica Cruz (2026-03-05)

---

## Q: How can Erica transfer all her iPhone photos to Google Drive?
**Asked by**: Greg (asked Claude directly during session)
**Answer**:
The easiest automatic method is **Google Photos with Backup & Sync**:
1. Install **Google Photos** app on Erica's iPhone
2. Go to Settings → Backup & Sync → turn ON
3. Set upload quality to "Storage Saver" (free) or "Original Quality" (counts toward Google storage)
4. Set backup to Wi-Fi only (saves cellular data)
5. All camera roll photos auto-upload — no manual action needed

For direct Google Drive folder organization, use the **Google Drive iOS app** → tap the `+` button → upload folders. Less automatic but gives folder control.

**Best workflow for Erica's use case**: Google Photos for automatic backup of all content, then manually move organized folders to Google Drive when ready to work with them for social media repurposing.

**Action**: Include in Erica's next steps email. Also — the agent can use the Google Drive API to help organize photos once they're uploaded.

**Sources**: [Google Drive iOS Help](https://support.google.com/drive/answer/2424368?hl=en&co=GENIE.Platform%3DiOS) | [Auto Sync Guide](https://www.multcloud.com/tutorials/auto-sync-iphone-photos-to-google-drive-0121.html)

---

## Q: Does ClassBento have an API?
**Asked by**: Greg ("I doubt that they have an API")
**Answer**:
**No documented public API found.** ClassBento's website mentions connecting to other websites to sync class data, but this appears to be an internal partner integration, not a developer API.

**Workaround**: Browser automation via OpenClaw's browser plugin. The agent can:
- Navigate to classbento.com
- Log in with Erica's credentials (stored as OpenClaw secrets)
- Check ticket sales, new registrations
- Even post new workshops if the UI is consistent

**Action**: Set up browser automation skill for ClassBento. Store credentials via `openclaw secrets set CLASSBENTO_EMAIL` and `CLASSBENTO_PASSWORD`. Treat as a browser-controlled tool, not an API tool.

**Sources**: [ClassBento Booking System page](https://classbento.com.au/class-booking-system)

---

## Q: How does Erica export her ChatGPT memory/history and import it to Claude?
**Asked by**: Greg ("if Claude is listening, can you please tell Erica how to import or export your memory from ChatGPT into Claude?")
**Answer**:
Anthropic released a native **memory import tool** in early March 2026 (just released!):

**Step-by-step:**
1. In ChatGPT, go to Settings → Data Controls → Export Data → request your data export
2. Alternatively, paste this prompt into ChatGPT: *"Please summarize all of my stored memories, preferences, recurring patterns, and personal context from our conversations in a structured format I can import to another AI."*
3. Copy the output
4. In Claude (claude.ai), go to Settings → Memory → Import Memory → paste the output
5. Memory updates appear within 24 hours

**Note**: This is experimental. Claude may not incorporate 100% of imported memories perfectly.

**Action**: Include step-by-step in Erica's next steps email. Also tell her to start a **Claude Project** for Cruz Creations to store her business context.

**Sources**: [Claude Import Help](https://support.claude.ai/en/articles/12123587-import-and-export-your-memory-from-claude) | [Tom's Guide walkthrough](https://www.tomsguide.com/ai/you-can-move-your-chatgpt-memory-to-claude-in-60-seconds-heres-how) | [Fast Company article](https://www.fastcompany.com/91501002/anthropic-claude-app-import-chats-from-open-ai-chatgpt-gemini-copilot-memory-tool)

---

## Q: What is Remotion? Is it good for Erica's video repurposing?
**Asked by**: Greg ("Remotion is a hot new one")
**Answer**:
**Remotion** is a framework for creating videos programmatically using React. Key facts:
- Open source, free to use (paid license for SaaS products)
- You write React components → Remotion renders them as MP4/WebM/GIF
- Great for: automated social media clips, TikTok-style captioned videos, batch-rendering variations
- Use case for Erica: Build a template React component for workshop recap videos → feed it attendee names, workshop date, photos → auto-render personalized clips

**Reality check**: Remotion requires coding knowledge (React). Not a no-code tool. Greg would need to build the template; Erica would just provide inputs.

**Better no-code alternative for Erica**: **Descript** or **CapCut** + AI trim features. Or Claude with the computer-use tool to control video editing software.

**Action**: Not a day-1 priority. Flag for Phase 2 (content library automation). Greg to build a simple Remotion template for workshop recap reels once the core workflows are running.

**Sources**: [Remotion.dev](https://www.remotion.dev/) | [GitHub](https://github.com/remotion-dev/remotion) | [Creator's Guide](https://medium.com/@PowerUpSkills/the-creators-complete-guide-to-remotion-build-videos-with-code-for-free-114f0774ed27)

---

## Q: How does Erica set up a custom Gmail domain (erica@cruisecreations.com)?
**Asked by**: Erica ("I'm trying to connect cruisecreations.com because right now I'm just using artbycruzcreations@gmail.com")
**Answer**:
Two options:

**Option A: Google Workspace (Recommended — Greg uses this)**
1. Go to workspace.google.com → Start free trial → $6/user/month after
2. Add domain: cruisecreations.com
3. Verify ownership (add DNS TXT record via Squarespace/GoDaddy/wherever domain is registered)
4. Create user: erica@cruisecreations.com
5. All Gmail features work as normal — same interface, just custom domain
6. **Benefit**: Can give the AI agent its own workspace user (e.g., `assistant@cruisecreations.com`) with API access

**Option B: Gmail Send-As with custom domain (Free if domain has SMTP)**
- Cheaper but requires an email hosting provider for the domain
- Less clean for agent integration

**Action**: Recommend Option A (Google Workspace Business Starter at $6/month). Include in next steps email. Once set up, the workshop-assistant and newsletter agents connect to this email.
