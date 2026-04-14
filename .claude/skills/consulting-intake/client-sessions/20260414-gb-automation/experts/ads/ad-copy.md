# Command: Ad Copy

## Purpose
Create high-converting ad copy for campaigns.

## Usage
```
/ads ad-copy {type} [--offer {offer}] [--audience {audience}] [--platform {linkedin|meta}]
```

Types: `lead_gen`, `content`, `retargeting`, `testimonial`

## Ad Copy Framework

### Structure
```
[HOOK - Stop the scroll]

[BODY - Value + Relevance]

[PROOF - Results or social proof]

[CTA - Clear action]
```

## Lead Gen Ads

### Template 1: Pain Point
```
{Pain point as question or statement}

{What we do about it}

{Proof point with specific result}

{CTA with clear offer}
```

**Example**:
```
Still doing {repetitive task} manually?

We help {audience} save 15+ hours/week with AI automation.

One client went from 50 hours/week to 35 in just 2 weeks.

Free 30-min audit to see what's automatable.

[Get Your Free Audit]
```

### Template 2: Result Lead
```
{Specific result achieved}

{How we did it}

{Who it's for}

{CTA}
```

**Example**:
```
How a 3-person agency automated 80% of their admin.

We built an AI assistant that handles scheduling, reporting, and follow-ups.

Perfect for founders who want to scale without hiring.

See if it works for you.

[Book Free Consultation]
```

### Template 3: Question Hook
```
{Provocative question}

{Agitate the pain}

{Solution hint}

{CTA}
```

**Example**:
```
What would you do with 10 extra hours every week?

Most agency founders spend half their time on tasks a bot could handle.

We install AI assistants that actually understand your business.

[See How It Works]
```

## Content Promotion Ads

### Template: Case Study
```
{Compelling headline result}

{Quick context}

{What they'll learn}

{CTA to read}
```

**Example**:
```
From 60-hour weeks to 40: How [Company] did it.

They were drowning in client work and admin.

Inside: The exact workflows they automated + how long it took.

[Read the Case Study]
```

### Template: Lead Magnet
```
{What they'll get}

{Why it's valuable}

{What they'll be able to do}

{CTA to download}
```

**Example**:
```
Free: AI Automation Audit Checklist

The exact framework we use to find 15+ hours of automatable tasks.

You'll know exactly where to start (and what to skip).

[Download Free Checklist]
```

## Retargeting Ads

### Template: Reminder
```
{Reference to previous visit}

{Reinforce value prop}

{New angle or urgency}

{CTA}
```

**Example**:
```
Still thinking about automating your operations?

Here's what's changed since you visited:
- New case study from a {industry} company
- Updated pricing (more flexible)

Ready to chat?

[Book a Quick Call]
```

### Template: Social Proof
```
{What others are saying}

{Quote or result}

{CTA}
```

**Example**:
```
"I got 15 hours back every week."

That's what [Client] said after we installed their AI assistant.

Your turn?

[Get Started]
```

## Platform-Specific Guidelines

### LinkedIn
- Professional tone
- Specific to role/industry
- Data and results work
- 150-300 characters for text ads
- Clear value proposition

### Meta
- More casual tone
- Emotional hooks work
- Visual-heavy
- 125 characters primary text
- Strong creative matters more

## Headline Options

### Pain-Based
- "Still doing {task} manually?"
- "Tired of {pain}?"
- "{Pain} is killing your growth"

### Result-Based
- "Save 15 hours/week"
- "How {company} cut {metric} by {%}"
- "From {before} to {after}"

### Curiosity-Based
- "The AI tool {audience} are using"
- "What {successful person} knows about {topic}"
- "Why {common practice} doesn't work"

## CTA Options

| Goal | CTA |
|------|-----|
| Book call | "Book Free Consultation" |
| Download | "Download Free Guide" |
| Learn more | "See How It Works" |
| Case study | "Read the Case Study" |
| Audit | "Get Your Free Audit" |

## Output

```markdown
## Ad Copy Generated

**Type**: {type}
**Platform**: {platform}
**Audience**: {audience}
**Offer**: {offer}

---

### Variant A
**Headline**: {headline}
**Body**:
{copy}

**CTA**: {cta}

---

### Variant B
**Headline**: {headline}
**Body**:
{copy}

**CTA**: {cta}

---

### Variant C
**Headline**: {headline}
**Body**:
{copy}

**CTA**: {cta}

---

**Recommended test order**: A vs B first, winner vs C
```

## Quality Checklist

Before running:
- [ ] Hook stops the scroll
- [ ] Value prop is clear
- [ ] Proof is specific
- [ ] CTA is obvious
- [ ] Under character limits
- [ ] No jargon
- [ ] Matches landing page
