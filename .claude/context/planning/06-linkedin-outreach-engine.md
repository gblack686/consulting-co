# Plan 6: LinkedIn Outreach Engine

## Overview
An automated lead generation and outreach system leveraging HeyReach for LinkedIn campaigns, Google search-based lead extraction, and a systematic funnel from initial contact to product specification calls.

---

## Phase 1: Lead Generation Infrastructure

### 1.1 HeyReach Campaign Setup
- [ ] Reactivate HeyReach account
- [ ] Configure LinkedIn account connections
- [ ] Set up campaign organization structure:
  ```
  /Campaigns
    /AI Development
    /Web Scraping Services
    /AWS Consulting
    /Trading Bot Development
  ```
- [ ] Import existing templates
- [ ] Review and update safety limits

### 1.2 LinkedIn Account Hygiene
- [ ] Audit connected accounts
- [ ] Warm up accounts if needed
- [ ] Set daily action limits:
  - Connection requests: 20-30/day
  - Messages: 50-80/day
  - Profile views: 80-100/day
- [ ] Enable proxy/residential IP rotation
- [ ] Monitor account health scores

### 1.3 Campaign Templates
- [ ] Create template library:
  - Initial connection request
  - First follow-up message
  - Value proposition message
  - Call booking message
  - Re-engagement message
- [ ] A/B test variants
- [ ] Personalization variables setup

---

## Phase 2: Google Search Lead Extraction

### 2.1 Search Query Strategy
- [ ] **Target Keywords**
  - "Founder" + industry
  - "CEO" + startup
  - "CTO" + tech company
  - "Consulting" + specialty
  - "Web scraping" + need
  - "AI development" + company
  - "AWS" + migration/consulting
- [ ] **Geographic Targeting**
  - Major tech hubs
  - Target markets
  - Remote-friendly regions

### 2.2 Search Automation
- [ ] **Google Search Scraping**
  - SERP API integration (SerpApi, ScraperAPI)
  - Or custom Playwright scraper
  - Handle CAPTCHA/rate limits
- [ ] **Result Processing**
  - Extract LinkedIn URLs from results
  - Parse company info
  - Deduplicate against existing leads
- [ ] **Batch Processing**
  - Schedule daily searches
  - Rotate query variations
  - Track search effectiveness

### 2.3 LinkedIn Profile Enrichment
- [ ] **Profile Data Extraction**
  - Name, title, company
  - Industry, location
  - Connection count
  - Recent activity
  - Mutual connections
- [ ] **Company Research**
  - Company size
  - Industry
  - Recent news/funding
  - Tech stack (if available)
- [ ] **Scoring Algorithm**
  - ICP (Ideal Customer Profile) match
  - Engagement likelihood
  - Budget indicators

---

## Phase 3: Lead Database & CRM

### 3.1 Database Schema
- [ ] Design lead data model:
  ```yaml
  lead:
    id: uuid
    linkedin_url: url
    name: string
    title: string
    company: string
    industry: string
    location: string
    email: string (if found)
    phone: string (if found)
    source: google|manual|referral
    icp_score: float
    status: new|contacted|responded|qualified|booked|lost
    campaign_id: uuid
    notes: text
    created_at: timestamp
    updated_at: timestamp
  ```

### 3.2 CRM Integration
- [ ] Evaluate options:
  - HeyReach native CRM
  - HubSpot integration
  - Pipedrive integration
  - Custom Supabase CRM
- [ ] Set up bidirectional sync
- [ ] Configure deal stages
- [ ] Build reporting dashboards

### 3.3 Lead Scoring
- [ ] Define ICP criteria
- [ ] Weighted scoring model
- [ ] Auto-prioritize high-score leads
- [ ] Score decay over time

---

## Phase 4: Outreach Sequences

### 4.1 Connection Request Sequence
- [ ] **Message 1: Connection Request**
  ```
  Hi {first_name}, I came across your profile and was impressed
  by your work at {company}. I'm helping {industry} companies
  with {value_prop}. Would love to connect!
  ```
- [ ] Personalization rules
- [ ] Time-of-day optimization
- [ ] Accept rate tracking

### 4.2 Follow-Up Sequence
- [ ] **Message 2: Value Hook** (Day 2-3 after accept)
  ```
  Thanks for connecting, {first_name}! I noticed {company} is
  {observation}. We recently helped {similar_company} achieve
  {result}. Thought it might be relevant to you.
  ```
- [ ] **Message 3: Case Study** (Day 5-7)
  ```
  Quick follow-up - here's a case study on how we helped
  {use_case}. Would love to hear if this resonates with
  what you're working on.
  ```
- [ ] **Message 4: CTA** (Day 10-14)
  ```
  Hi {first_name}, would you be open to a quick 15-min call
  to see if I can help with {pain_point}? Here's my calendar:
  {calendly_link}
  ```
- [ ] **Message 5: Break-Up** (Day 21)
  ```
  {first_name}, I don't want to keep messaging if this isn't
  a fit. If {value_prop} ever becomes a priority, I'm here
  to help. Best of luck with {company}!
  ```

### 4.3 Sequence Automation
- [ ] Configure HeyReach sequences
- [ ] Set delay intervals
- [ ] Stop conditions (reply, accept meeting)
- [ ] Branch logic based on responses

---

## Phase 5: Call Booking Funnel

### 5.1 Calendly/Cal.com Setup
- [ ] Create booking page for "1-Hour Product Spec Call"
- [ ] Configure availability
- [ ] Add intake questions:
  - Current challenge
  - Timeline
  - Budget range
  - Decision makers
- [ ] Set up reminders
- [ ] Add to HeyReach templates

### 5.2 Pre-Call Workflow
- [ ] Send confirmation email with prep questions
- [ ] Research lead before call
- [ ] Pull relevant case studies
- [ ] Prepare custom demo if applicable

### 5.3 Post-Call Follow-Up
- [ ] Automated thank you email
- [ ] Send meeting notes/recording
- [ ] Proposal generation workflow
- [ ] Move to deal stage in CRM

---

## Phase 6: Analytics & Optimization

### 6.1 Campaign Metrics
- [ ] Track key metrics:
  - Connection request accept rate
  - Reply rate by sequence step
  - Positive reply rate
  - Meeting book rate
  - Show-up rate
  - Conversion to client
- [ ] Build analytics dashboard
- [ ] Weekly performance reports

### 6.2 A/B Testing
- [ ] Test message variants
- [ ] Test send times
- [ ] Test personalization levels
- [ ] Statistical significance tracking

### 6.3 Continuous Improvement
- [ ] Weekly template review
- [ ] Monthly ICP refinement
- [ ] Quarterly strategy review
- [ ] Competitor message analysis

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Lead Sources                               │
│      Google Search │ LinkedIn Search │ Referrals │ Manual   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                Lead Extraction Pipeline                      │
│    SERP Scraping │ Profile Enrichment │ Deduplication       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Lead Database                              │
│         Supabase/HubSpot │ Scoring │ Segmentation           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 HeyReach Campaigns                           │
│    Connection Requests │ Message Sequences │ Tracking       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Response Handling                          │
│       Reply Detection │ Sentiment Analysis │ Routing        │
└─────────────────────────┬───────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Calendly/Cal.com  │   │   Manual Follow-Up  │
│   1-Hour Spec Call  │   │   Nurture Sequence  │
└─────────────────────┘   └─────────────────────┘
```

---

## Compliance & Safety

### LinkedIn Terms of Service
- [ ] Stay within daily action limits
- [ ] Use personalized, non-spammy messages
- [ ] Respect opt-outs immediately
- [ ] No scraping directly from LinkedIn (use APIs)
- [ ] Monitor for warnings/restrictions

### GDPR/Privacy
- [ ] Document legal basis for processing
- [ ] Honor data deletion requests
- [ ] Secure lead data storage
- [ ] Clear unsubscribe mechanism

---

## Dependencies
- HeyReach subscription
- LinkedIn Sales Navigator (recommended)
- SERP API (SerpApi, ScraperAPI)
- Calendly/Cal.com account
- CRM (HubSpot/custom)
- Supabase for custom storage

---

## Deliverables
- [ ] Reactivated HeyReach campaigns
- [ ] Google search lead extraction pipeline
- [ ] Lead scoring system
- [ ] Multi-step outreach sequences
- [ ] Call booking funnel
- [ ] Analytics dashboard
- [ ] Weekly performance reports

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Connection Accept Rate | > 30% |
| Reply Rate | > 15% |
| Positive Reply Rate | > 5% |
| Meeting Book Rate | > 2% |
| Show-Up Rate | > 80% |
| Client Conversion | > 20% of calls |

---

## Weekly Rhythm
- **Monday**: Review last week's metrics, adjust campaigns
- **Tuesday-Thursday**: Campaign execution, response handling
- **Friday**: New lead research, template optimization
- **Ongoing**: Calls as booked, follow-ups
