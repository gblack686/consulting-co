# Ads Expertise

## Part 1: Domain Fundamentals

### What is B2B Paid Advertising?
Using paid channels (LinkedIn, Meta, Google) to reach target audiences with compelling offers that generate qualified leads. For consulting services, the goal is quality over quantity - better to get 5 perfect-fit leads than 50 tire-kickers.

### Core Principles
1. **Target tight** - Specific audiences beat broad ones
2. **Offer value first** - Lead with content, not sales pitch
3. **Test everything** - Copy, creative, targeting, offers
4. **Measure what matters** - CPL, lead quality, conversion to call
5. **Budget discipline** - Start small, scale what works

## Part 2: Platform Strategy

### LinkedIn Ads (Primary)
**Why**: Direct access to B2B decision-makers
**Best for**: Lead gen, content promotion
**Budget**: $20-50/day minimum
**Expected CPL**: $30-75

### Meta Ads (Secondary)
**Why**: Lower CPL, broader reach
**Best for**: Retargeting, lead magnets
**Budget**: $10-20/day
**Expected CPL**: $10-30

### Platform Comparison
| Factor | LinkedIn | Meta |
|--------|----------|------|
| CPL | Higher ($30-75) | Lower ($10-30) |
| Lead Quality | Higher | Variable |
| Targeting | Job title, company | Interest, behavior |
| Best Use | Direct lead gen | Retargeting, awareness |

## Part 3: Campaign Types

### Lead Gen Campaign (LinkedIn)
**Objective**: Collect leads via LinkedIn Lead Gen Forms
**Offer**: Free consultation, audit, lead magnet
**Targeting**: Decision-makers at target companies
**Budget**: $30-50/day

### Content Promotion (LinkedIn)
**Objective**: Drive traffic to valuable content
**Offer**: Case study, guide, framework
**Targeting**: Broader but relevant audience
**Budget**: $15-25/day

### Retargeting (Meta)
**Objective**: Re-engage website visitors
**Offer**: Case study, testimonial, direct CTA
**Targeting**: Website visitors, video viewers
**Budget**: $10-15/day

## Part 4: Targeting Strategy

### LinkedIn Targeting Layers

**Layer 1: Job Function**
- Operations
- Marketing
- Business Development
- C-Suite

**Layer 2: Seniority**
- Owner
- Director
- VP
- Manager

**Layer 3: Company Size**
- 1-10 employees (primary)
- 11-50 employees (secondary)

**Layer 4: Industry**
- Marketing & Advertising
- Professional Services
- Technology
- Consulting

### Audience Combinations
```yaml
audience_1_hot:
  name: "Founders - Small Agencies"
  function: ["Marketing", "Operations"]
  seniority: ["Owner", "CXO"]
  company_size: "1-10"
  industry: ["Marketing & Advertising", "Professional Services"]
  estimated_size: "5,000-15,000"
  
audience_2_warm:
  name: "Ops Leaders - SMB"
  function: ["Operations", "Business Development"]
  seniority: ["Director", "VP", "Manager"]
  company_size: "11-50"
  industry: ["Technology", "Professional Services"]
  estimated_size: "15,000-30,000"
```

## Part 5: Ad Creative Strategy

### LinkedIn Ad Formats
| Format | Best For | Specs |
|--------|----------|-------|
| Single Image | Lead gen | 1200x627px |
| Carousel | Multi-benefit | 1080x1080px per card |
| Video | Brand awareness | 15-30 seconds |
| Document | Thought leadership | PDF upload |

### Creative Principles
1. **Pattern interrupt** - Stop the scroll
2. **Clear value prop** - What's in it for them?
3. **Social proof** - Results, logos, testimonials
4. **Single CTA** - One clear action

### Ad Copy Framework
```
[HOOK - Pattern interrupt or pain point]

[BODY - What you offer + why it matters]

[PROOF - Result or social proof]

[CTA - Clear next step]
```

### Example Ads

**Lead Gen Ad**:
```
Still doing repetitive tasks manually?

We help agency founders save 15+ hours/week with AI automation.

One client went from 50 hours/week to 35 in 2 weeks.

Free 30-minute audit to see what's automatable.

[Get Your Free Audit]
```

**Content Ad**:
```
How a 3-person agency automated 80% of their admin.

Case study: From overwhelmed to operations machine.

See exactly what we did (and how long it took).

[Read the Case Study]
```

## Part 6: Budget Strategy

### Monthly Budget Allocation
| Channel | Budget | Goal |
|---------|--------|------|
| LinkedIn Lead Gen | $300 | 5-10 leads |
| LinkedIn Content | $100 | Traffic + engagement |
| Meta Retargeting | $100 | Re-engage visitors |
| **Total** | **$500** | **10+ leads** |

### Scaling Rules
- Don't scale until CPL stabilized (7+ days data)
- Scale by 20-30% at a time
- Pause underperformers quickly (3 days no results)
- Add budget to winners, not new experiments

### Budget Alerts
| Threshold | Action |
|-----------|--------|
| 50% spent | Check performance |
| 80% spent | Decide: pause or continue |
| CPL > $75 | Pause and diagnose |
| Zero leads for 3 days | Refresh creative |

## Part 7: Patterns & Learnings

### What Works
- Lead magnets (free audits, guides)
- Specific results in ad copy
- Questions that resonate with pain
- Retargeting warm audiences
- Testing multiple creatives

### What Doesn't Work
- Generic brand awareness
- Complicated offers
- Low daily budgets (<$15)
- Too broad targeting
- Not testing enough

### LinkedIn-Specific Tips
- Lead Gen Forms > Website traffic
- Keep forms short (3-4 fields)
- Pre-fill fields when possible
- Use Thank You page wisely
- Follow up within 1 hour

### Testing Priority
1. Audience (biggest impact)
2. Offer (what you're promoting)
3. Creative (image/video)
4. Copy (headline, body)
