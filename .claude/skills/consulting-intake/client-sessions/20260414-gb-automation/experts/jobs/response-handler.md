# Command: Response Handler

## Purpose
Handle responses from job applications and move conversations toward contracts.

## Usage
```
/jobs response-handler {response_type} {opportunity_id}
```

## Response Types

### Positive Interest
"We'd like to chat" / "Can you tell me more?" / "Let's schedule a call"

### Info Request
"Send more information" / "What's your rate?" / "Do you have examples?"

### Soft Rejection
"Not a fit right now" / "We went another direction" / "Position filled"

### No Response
More than 2 weeks since application

## Response Handling

### Positive Interest Handler

**Goal**: Schedule call ASAP

**Response Template**:
```
{Name},

Great to hear from you. I'm available:
- {Day/Time 1}
- {Day/Time 2}
- {Day/Time 3}

Or grab a time that works: {calendar_link}

Looking forward to the conversation.

Greg
```

**Actions**:
1. Reply within 1 hour
2. Offer 3 specific times
3. Include calendar link
4. Update pipeline to "Responding"
5. Set reminder if no reply in 24 hours

### Info Request Handler

**Goal**: Provide value, redirect to call

**For "What's your rate?"**:
```
Good question. For consulting engagements like this, I typically work on monthly retainers ranging from $3,500-5,000 depending on scope.

But rates really depend on what we're trying to accomplish. Would be easier to nail down after a quick conversation about your specific needs.

Free for a 15-minute call? {calendar_link}

Greg
```

**For "Send more info"**:
```
Happy to share more.

Here's a case study from a similar project: {link}

Rather than overload you with docs, want to do a quick 15-minute call? I can walk you through our approach and answer questions live.

{calendar_link}

Greg
```

**Actions**:
1. Reply within 4 hours
2. Provide requested info concisely
3. Always redirect to call
4. Include relevant proof
5. Update pipeline to "Responding"

### Soft Rejection Handler

**Goal**: Learn, stay in touch, ask for referral

**For "Not a fit right now"**:
```
Thanks for letting me know. Timing is everything.

If anything changes, I'm always happy to revisit. Would it be helpful if I checked back in a few months?

Also - know anyone else who might be dealing with similar automation challenges? Happy to be a resource.

Best,
Greg
```

**For "Went another direction"**:
```
Appreciate you closing the loop.

If you don't mind me asking - what tipped the decision? Always looking to improve.

And if things don't work out with who you chose, I'm here.

Best,
Greg
```

**Actions**:
1. Reply within 24 hours
2. Thank them for responding
3. Ask for feedback (optional)
4. Offer to stay in touch
5. Ask for referral
6. Update pipeline to "Closed Lost"
7. Add to nurture list

### No Response Handler

**Goal**: Final attempt or close out

**After 2 weeks - Follow-up 1**:
```
{Name},

Wanted to check in on my application for {role}.

Still interested if the position is open. If you've moved on or it's not a fit, no worries - just let me know.

Greg
```

**After 3 weeks - Final**:
```
{Name},

Going to assume timing isn't right and close this out on my end.

If things change, you know where to find me.

Best,
Greg
```

**Actions**:
1. Send follow-up at 2 weeks
2. Final follow-up at 3 weeks
3. Mark as "Closed Lost" after 4 weeks
4. Do not add to nurture (never responded)

## Call Booking Flow

When call is scheduled:
1. Send calendar invite immediately
2. Include video link
3. Send prep email 24 hours before
4. Update pipeline to "Interviewing"
5. Trigger discovery-call prep (from Sales domain)

**Prep Email**:
```
{Name},

Looking forward to our call tomorrow at {time}.

A few things that might help us make the most of our time:
1. What's the main thing you're hoping to solve?
2. Any must-have requirements I should know about?

See you soon.

Greg
```

## Output

```markdown
## Response Handled: {Company}

**Response Type**: {type}
**Received**: {datetime}
**Replied**: {datetime}
**Reply Time**: {hours}

**Action Taken**: {description}
**Pipeline Updated**: {new stage}
**Follow-up Set**: {if applicable}

**Next Step**: {what happens next}
```

## Automation Rules

Auto-queue:
- Reminder if positive response not replied in 1 hour
- Follow-up 1 at 2 weeks if no response
- Follow-up 2 (final) at 3 weeks
- Close out at 4 weeks

Alerts:
- Immediate notification on any response
- Priority alert on "Let's chat" responses
