# Command: Follow-Up

## Purpose
Execute timely, effective follow-up sequences to move deals forward.

## Usage
```
/sales follow-up {prospect} [--type {proposal|discovery|nurture|re-engage}]
```

## Follow-Up Types

### Proposal Follow-Up
After sending a proposal, no response.

### Discovery Follow-Up
Scheduled call, need to confirm or prep.

### Nurture Follow-Up
Not ready now, keep warm.

### Re-Engage Follow-Up
Went cold, try to revive.

## Proposal Follow-Up Sequence

### Day 1 (same day as send)
```
Subject: Just sent over the proposal

{Name},

Proposal just landed in your inbox. Take a look when you have a moment.

Quick question while it's fresh - what's your gut reaction to the scope? Want to make sure we're aligned on what matters most.

Talk soon,
Greg
```

### Day 3 (if no response)
```
Subject: Any questions on the proposal?

{Name},

Wanted to check in on the proposal. 

If anything's unclear or you'd like to adjust the scope, happy to jump on a quick call.

What's your timeline looking like?

Greg
```

### Day 5 (if still no response)
```
Subject: Should I close this out?

{Name},

Haven't heard back, so wanted to check - is this still a priority for you?

No pressure either way. If timing isn't right, just let me know and I'll follow up in a few months.

If you're still interested but have concerns, I'd rather address them than leave you hanging.

What's your thinking?

Greg
```

### Day 7 (final)
```
Subject: One last check

{Name},

Going to assume the timing isn't right and close out this opportunity for now.

If things change, you know where to find me. Happy to pick this back up whenever it makes sense for you.

Best,
Greg
```

## Discovery Follow-Up

### Pre-Call Confirmation (Day before)
```
Subject: Confirming our call tomorrow

{Name},

Looking forward to our call tomorrow at {time}.

Quick prep questions to make our time count:
1. What's the #1 thing you'd want to solve?
2. What have you already tried?

Here's the call link: {link}

See you tomorrow,
Greg
```

### No-Show Follow-Up
```
Subject: Missed you on our call

{Name},

I was on the line but didn't see you join. No worries - I know things come up.

Would you like to reschedule? Here's my calendar: {link}

Or if priorities have changed, just let me know.

Greg
```

## Nurture Follow-Up

### Monthly Check-In Template
```
Subject: {Relevant topic} - thought of you

{Name},

{Timely hook - article, insight, or update relevant to their pain}

No pitch here - just thought it was relevant given what you mentioned about {their pain point}.

Hope things are going well. Let me know if you ever want to revisit the automation conversation.

Greg
```

### Value-Add Template
```
Subject: Quick resource for {their challenge}

{Name},

We just published {resource} that addresses {pain point} you mentioned.

Figured it might be useful even if the timing isn't right for working together: {link}

Let me know if any questions come up.

Greg
```

## Re-Engage Follow-Up

### Breaking the Ice
```
Subject: It's been a while

{Name},

It's been {X months} since we last talked about {topic}.

I'm curious - did you end up solving {pain point}? If so, I'd love to hear what worked. If not, we've since helped {similar company} with exactly that.

Either way, would be great to reconnect.

Greg
```

### New Angle
```
Subject: New approach to {their pain}

{Name},

We've learned a lot since we last connected. One insight: {new approach or case study}.

If {pain point} is still a challenge, might be worth a fresh look.

Open to a quick catch-up?

Greg
```

## Follow-Up Rules

### Timing
| Scenario | Wait Time |
|----------|-----------|
| After proposal sent | Same day check, then day 3, 5, 7 |
| After discovery call | Proposal within 4 hours |
| After no-show | Within 1 hour |
| Nurture leads | Monthly |
| Re-engage cold | 3-6 months |

### Tone Guidelines
- Confident, not desperate
- Helpful, not pushy
- Direct, not passive-aggressive
- Human, not robotic

### What Not to Do
- Don't apologize for following up
- Don't send more than 4 follow-ups on a proposal
- Don't be pushy or guilt-trip
- Don't send at weird hours
- Don't copy/paste without personalizing

## Output

```markdown
## Follow-Up Sent: {Prospect}

**Type**: {type}
**Sequence Step**: {n of total}
**Sent**: {datetime}

**Subject**: {subject}

**Next Follow-Up**: {date} (unless response)

**Notes**: {any context}
```

## Automation Rules

Auto-queue follow-ups:
- Proposal sent → Day 3 follow-up queued
- No response to Day 3 → Day 5 queued
- No response to Day 5 → Day 7 queued
- Day 7 sent → Mark as cold, add to nurture

Manual triggers:
- Positive response → Move to negotiation
- Negative response → Close or nurture
- Question → Answer immediately
