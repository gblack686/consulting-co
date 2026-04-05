# Session Follow-Up Email Template

Used by `transcript_agent.py` to generate post-session follow-up emails to clients.

## Template

```
Subject: Follow-Up: {Client Name} Session — {Topic 1}, {Topic 2} & {Topic 3}

Hi {client_first_name},

Great session today — we covered a lot of ground and I feel like we have a clear path forward. Here's a recap of what we discussed and what needs to happen before our next meeting.

What We Covered

{2-3 paragraphs summarizing key discussion points. Be specific — reference actual tools, integrations, and decisions made. Don't be generic.}

Action Items

Greg (me):
- {action item with context — not just "do X" but why}
- ...

{client_first_name}:
- {action item with context}
- ...

{other_stakeholder} (please loop them in):
- {action item with context}
- ...

Next Steps

{1-2 paragraphs identifying the critical-path unlocks before next session. What's blocking progress? What needs to happen first?}

{Optional: mention any async deliverables you'll send separately — videos, docs, etc.}

Let me know if anything looks off or if you want to adjust priorities. Looking forward to {forward-looking statement}.

Greg Black
GBAutomation
greg@gbautomation.xyz
```

## Rules

1. **Write as Greg Black.** First person. Professional but warm.
2. **Reference specific topics** discussed in the call — never be generic.
3. **Action items have owners** — Greg vs. client vs. other stakeholders.
4. **Include deadlines** if they were discussed.
5. **Identify the critical-path blockers** in the Next Steps section — what must happen before the next session for progress to continue.
6. **Do NOT mention AI, agents, automation of this email**, or anything that reveals it was machine-generated.
7. **Do NOT include** "Subject:" in the body — that's handled separately.
8. **Sign off as:**
   ```
   Greg Black
   GBAutomation
   greg@gbautomation.xyz
   ```

## Variables

| Variable | Source |
|----------|--------|
| `{client_first_name}` | Extracted from transcript (first attendee who isn't Greg) |
| `{client_email}` | Looked up from prior Gmail threads or transcript email headers |
| `{other_stakeholder}` | Any 3rd party referenced in discussion (e.g., Mike, CTO, etc.) |
| `{Topic 1-3}` | Top 3 discussion themes for the subject line |

## Integration

This template is used by `transcript_agent.py` in the `CLAUDE_SYSTEM_PROMPT` constant.
The agent:
1. Fetches transcript from Google Meet API or Google Docs
2. Sends transcript + this template structure to Claude CLI
3. Claude returns the filled email
4. Agent creates a Gmail draft (not auto-sent)
5. Greg reviews and hits send

## Example Output

See: `logs/transcript_fisch_20260402_analysis.md`
