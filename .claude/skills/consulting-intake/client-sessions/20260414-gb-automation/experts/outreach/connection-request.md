# Command: Connection Request

## Purpose
Send personalized LinkedIn connection requests to qualified prospects.

## Usage
```
/outreach connection-request {prospect_file_or_batch}
```

## Input
- Prospect file(s) from prospect-research
- Or: batch file with multiple prospects
- Template override (optional)

## Process

### Step 1: Load Prospect Data
Read prospect card(s) and validate:
- [ ] Has personalization hooks
- [ ] Has suggested template
- [ ] Has custom first line
- [ ] Not already connected

### Step 2: Select Template
Choose based on prospect data:

**Template A: Mutual Interest** (default for content creators)
```
Hey {first_name} - saw your post about {topic}. Building AI ops tools for {industry} folks. Would love to connect and swap notes.
```

**Template B: Specific Observation** (for growth signals)
```
{first_name} - noticed you're scaling {company}. Been helping {role}s automate the ops side with AI. Thought there might be overlap. Connect?
```

**Template C: Content Hook** (for thought leaders)
```
{first_name} - your take on {topic} resonated. Working on AI tools for exactly this. Would value your perspective.
```

**Template D: Mutual Connection** (when applicable)
```
{first_name} - {mutual_name} and I were just talking about {topic}. Seems like you're deep in this space too. Would love to connect.
```

### Step 3: Personalize
Replace variables:
- `{first_name}` - From prospect card
- `{topic}` - From recent activity
- `{company}` - From prospect card
- `{industry}` - Inferred from company
- `{role}` - Generic for their title
- `{mutual_name}` - If using Template D

### Step 4: Validate Message
- [ ] Under 300 characters (LinkedIn limit)
- [ ] No typos or placeholder text
- [ ] Personalization is accurate
- [ ] Tone is casual and human

### Step 5: Queue or Send
Based on configuration:
- **Auto-send**: Send immediately (if autonomy = high)
- **Queue**: Add to batch for approval (default)

### Step 6: Log
Record in tracking:
```yaml
prospect: {name}
company: {company}
template: {A/B/C/D}
message: "{full_message}"
sent_at: {timestamp}
status: pending_acceptance
```

## Batch Mode

For batch processing:
1. Load all prospect files from directory
2. Filter by priority (P1 first)
3. Respect daily limits (30 max)
4. Generate batch summary for approval
5. Send approved batch with human-like delays (30-90s between)

## Safety Limits

| Limit | Value | Action if exceeded |
|-------|-------|-------------------|
| Daily connections | 30 | Queue for tomorrow |
| Hourly connections | 10 | Slow down |
| Consecutive sends | 5 | 5-minute break |

## Output

Batch summary:
```markdown
## Connection Request Batch - {date}

**Total**: {n} requests
**Templates**: A: {n}, B: {n}, C: {n}, D: {n}

### Requests
| Name | Company | Template | First Line Preview |
|------|---------|----------|-------------------|
| ... | ... | ... | ... |

**Status**: Ready for approval / Sent
```

## Follow-up
After connection accepted:
- Trigger `dm-sequence` command
- Update prospect status
- Log in Memory relationship map
