# Scope of Work: Influence Attribution & Impact Scoring System
**Package**: Essential | **Timeline**: 5 weeks

## Project Overview

Build a data-driven scoring engine that measures true B2B influencer impact by connecting LinkedIn content, engagement patterns, and audience quality to brand outcome likelihood. The system will provide transparent, quantifiable metrics for selecting high-value influencers.

## Deliverables

### Core Scoring Engine
- **Influence Impact Score (IIS)** algorithm with 4 weighted components:
  - Reach Score (followers × seniority × industry fit)
  - Engagement Quality Score (comment depth, seniority of engagers)
  - Topical Authority Score (embedding similarity to brand ICP)
  - Conversion Proxy Score (clicks, shares, product mentions)

### Attribution Model
- Weighted engagement system (likes < comments < reposts)
- Seniority weighting of engaged users
- Audience ICP match analysis
- Historical post performance normalization

### Dashboard & Visualization
- Interactive influencer ranking table
- Transparent scoring breakdown (show WHY influencers rank highly)
- Filter/sort by: industry, audience type, seniority, topic alignment
- Head-to-head influencer comparison

### API Integration
- RESTful API endpoints exposing IIS scores
- Filter capabilities for marketplace front-end
- Real-time score calculation endpoints

### Documentation & Support
- Scoring methodology documentation
- API integration guide
- 2-week post-launch support

## Technical Specifications

**Stack**: Python (scikit-learn, pandas), FastAPI, React dashboard, PostgreSQL
**Architecture**: Batch scoring pipeline + API layer + React frontend
**Integration**: RESTful API with JSON responses
**Scalability**: Designed for 10K-100K influencer profiles

## Assumptions & Constraints

- Client provides LinkedIn engagement data in structured format (CSV/JSON)
- Data includes: profile info, post content, engagement metrics, follower data
- Optional: UTM-tagged traffic or website analytics (if available for conversion signals)
- Client provides timely feedback (within 48 hours)

## Out of Scope

- Real-time LinkedIn data scraping (client provides data)
- Time-series analysis or trend forecasting (available as add-on)
- Mobile app interface
- Weekly "Influencer Movement" reports (available as add-on)
- Multi-tenant authentication system

## Success Metrics

1. IIS scores generated for 95%+ of provided influencer profiles
2. Dashboard loads and filters <2 seconds for 95th percentile queries
3. API response time <500ms for score retrieval
4. Scoring methodology is explainable and validated by stakeholders

## Support & Maintenance

- 2-week post-launch support included
- Optional add-ons available: weekly trend reports, time-series analysis, alerts for trending influencers
