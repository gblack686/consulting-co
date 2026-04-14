# Command: DM Sequence

## Purpose
Manage multi-touch DM conversations with connected prospects to book discovery calls.

## Usage
```
/outreach dm-sequence {action} {prospect}
```

Actions: `start`, `continue`, `respond`, `close`

## Sequence Framework

### Message 1: Welcome + Question (Day 0 - after acceptance)
```
Thanks for connecting, {first_name}! Quick q - what's eating up most of your time these days that you wish someone (or something) else could handle?
```

### Message 2: Empathy + Tease (Day 1 - if response)
```
Yeah, {pain_point} is brutal. Funny enough, that's exactly what we've been automating for {similar_role}s. {company_example} cut that down by 70% with our AI assistant. Want me to share how they did it?
```

### Message 3: Value Drop (Day 3 - if no response to M1)
```
{first_name} - just published a quick breakdown on how {industry} folks are using AI to handle {common_task}. Thought you might find it useful: {content_link}

No pressure to respond - just wanted to share something relevant.
```

### Message 4: Case Study (Day 4 - if engaged)
```
Here's the {company_example} breakdown: {case_study_link}

tl;dr - they went from {before_state} to {after_state} in about 2 weeks. Happy to walk you through how it'd look for {prospect_company}.
```

### Message 5: Soft CTA (Day 5 - if still engaged)
```
Based on what you've shared, I think there's a real opportunity to {specific_benefit}. 

Worth a 15-min call to see if our approach fits? Here's my calendar: {cal_link}

If not, totally understand - just let me know and I won't bug you further.
```

### Message 6: Final Follow-up (Day 10 - if no response)
```
{first_name} - circling back one last time. If automating {pain_point} isn't a priority right now, no worries at all. 

But if it is and timing just hasn't been right, reply "later" and I'll check back in a month. Either way, appreciate you connecting.
```

## Response Handling

### Positive Signals
| Signal | Action |
|--------|--------|
| Asks question about service | Answer + advance sequence |
| Expresses pain point | Empathize + share relevant case |
| Shows interest in call | Send calendar link immediately |
| Asks for pricing | Tease value, push to call |

### Neutral Signals
| Signal | Action |
|--------|--------|
| "Interesting" / "Cool" | Ask follow-up question |
| "Not right now" | Ask when to follow up |
| "Send more info" | Share case study, ask for call |

### Negative Signals
| Signal | Action |
|--------|--------|
| "Not interested" | Thank them, offer referral ask |
| "Unsubscribe" / "Stop" | Immediately stop, mark as DNC |
| No response after M6 | Mark as cold, archive |

## Conversation State Machine

```
NEW
 │
 ├─> WELCOMED (M1 sent)
 │      │
 │      ├─> ENGAGED (responded)
 │      │      │
 │      │      ├─> QUALIFIED (pain confirmed)
 │      │      │      │
 │      │      │      ├─> CALL_BOOKED
 │      │      │      │
 │      │      │      └─> NURTURING (not ready)
 │      │      │
 │      │      └─> DISQUALIFIED (not a fit)
 │      │
 │      └─> COLD (no response after sequence)
 │
 └─> DO_NOT_CONTACT (requested stop)
```

## Personalization Variables

| Variable | Source |
|----------|--------|
| `{first_name}` | Prospect card |
| `{pain_point}` | From their response or research |
| `{similar_role}` | Match to their title |
| `{company_example}` | From case study library |
| `{industry}` | From prospect card |
| `{common_task}` | ICP pain points |
| `{content_link}` | From Content domain |
| `{case_study_link}` | From Sales domain |
| `{cal_link}` | Greg's calendar link |

## Timing Rules

| Scenario | Wait Time |
|----------|-----------|
| After connection accepted | 2-4 hours |
| After they respond | 1-4 hours (same day) |
| After no response | Follow sequence timing |
| After call booked | Immediate confirmation |

## Output

Log each interaction:
```yaml
prospect: {name}
conversation_state: {state}
messages:
  - seq: 1
    sent_at: {timestamp}
    content: "{message}"
    response: "{their_response}"
    response_at: {timestamp}
next_action: {message_type}
next_action_at: {timestamp}
```

## Handoff to Sales

When state = CALL_BOOKED:
1. Create discovery call brief
2. Include all conversation context
3. Note specific pain points mentioned
4. Alert Sales domain
5. Update Memory relationship map
