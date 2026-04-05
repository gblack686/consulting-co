---
description: Generate a professional consulting proposal with email, scope of work, and timeline
args: <tier> <project_name> [client_name]
---

# Quick Proposal Generator

Generate a professional consulting proposal with email, scope of work, and timeline.

## Usage

```
/consulting:quick-proposal <tier> <project_name> [client_name]
```

**Tiers**: `essential`, `professional`, `comprehensive`

**Arguments**:
- `<tier>` - Proposal tier (essential/professional/comprehensive)
- `<project_name>` - Name or brief description of the project
- `[client_name]` - Optional client/company name (default: "Client")

## Examples

```bash
/consulting:quick-proposal essential "E-commerce Website" "Acme Corp"
/consulting:quick-proposal professional "AI Chatbot Integration"
/consulting:quick-proposal comprehensive "Full Platform Migration" "TechStartup Inc"
```

## What It Generates

Files will be saved in: `proposals/{project-slug}-{YYYYMMDD}/`

**Four Files**:
1. `proposal.md` - Ultra-concise overview (copy/paste ready)
2. `proposal-email.md` - Professional email to client
3. `scope-of-work.md` - Detailed scope document
4. `timeline.md` - Week-by-week timeline

**Length Guidelines** (keep concise and scannable):
- **Essential**: All files combined ~100-150 lines total
- **Professional**: All files combined ~200-300 lines total
- **Comprehensive**: All files combined ~400-500 lines total

---

## Instructions

You are a consulting proposal expert. Generate a complete proposal package based on the provided arguments.

**IMPORTANT**: Parse the arguments as follows:
- First argument: tier (essential/professional/comprehensive)
- Second argument: project_name
- Third argument (optional): client_name (default: "Client")

### File Organization

**CRITICAL**: All proposal files MUST be saved in the following directory structure:

```
proposals/{project-slug}-{YYYYMMDD}/proposal.md
```

Where:
- `{project-slug}` = lowercase, hyphenated version of project_name (e.g., "E-commerce Website" → "e-commerce-website")
- `{YYYYMMDD}` = today's date in YYYYMMDD format (e.g., "20250117")

**Example**: For project "AI Chatbot Integration" on Jan 17, 2025:
- Directory: `proposals/ai-chatbot-integration-20250117/`
- File: `proposal.md`

### Tier Definitions

**Essential** (4-8 weeks):
- Core deliverables only
- Standard implementation
- Basic documentation
- 2-week support window

**Professional** (8-16 weeks):
- Full feature set
- Custom implementation
- Comprehensive documentation
- 4-week support + training
- Performance optimization

**Comprehensive** (16-24 weeks):
- Enterprise-grade solution
- Advanced features
- Complete documentation suite
- 8-week support + training
- Security audit + optimization
- Ongoing maintenance option

### Output Format

Generate a SINGLE concise `proposal.md` file formatted as a ready-to-send email.

**CRITICAL LINE LIMITS**:
- **Essential**: Maximum 15 lines (ultra-concise)
- **Professional**: Maximum 50 lines (concise)
- **Comprehensive**: Maximum 100 lines (detailed but scannable)

#### Essential Tier Template (~15 lines)

```markdown
**Subject**: {project_name} - Essential Package

Hi {client_name},

I'll build {1-sentence description of core deliverable}.

**Deliverables**:
- {Core feature 1}
- {Core feature 2}
- {Core feature 3}
- Basic documentation + 2-week support

**Timeline**: {X} weeks | **Stack**: {brief tech mention}

**Next Steps**: Review → Kickoff call → Begin Week 1

Best,
[Your Name]
```

#### Professional Tier Template (~50 lines)

```markdown
**Subject**: {project_name} - Professional Package

Hi {client_name},

I'll deliver {1-2 sentence description including key value prop}.

**Scope**:

**Discovery (Weeks 1-2)**:
- {Discovery item 1}
- {Discovery item 2}

**Build (Weeks 3-X)**:
- {Feature 1}
- {Feature 2}
- {Feature 3}
- {Feature 4}

**Launch (Final weeks)**:
- Production deployment
- Team training
- 4-week support

**Stack**: {Brief tech stack - 1 line}

**Included**:
- ✅ {Benefit 1}
- ✅ {Benefit 2}
- ✅ {Benefit 3}

**Not Included**:
- ❌ {Out of scope 1}
- ❌ {Out of scope 2}

**Timeline**: {X} weeks | **Milestones**: Week 2 (Design approval), Week X (UAT), Week Y (Launch)

**Next Steps**:
1. Review scope
2. 30min alignment call
3. Sign & begin

Best,
[Your Name]
```

#### Comprehensive Tier Template (~100 lines)

```markdown
**Subject**: {project_name} - Comprehensive Package

Hi {client_name},

{2-3 sentence overview including problem, solution, and key value proposition}

---

**Deliverables**:

**Phase 1: Discovery (Weeks 1-2)**
- {Activity 1}
- {Activity 2}
- {Activity 3}
- Deliverable: {Output}

**Phase 2: Development (Weeks 3-X)**
- {Component 1}
- {Component 2}
- {Component 3}
- {Component 4}
- {Component 5}
- Deliverable: {Output}

**Phase 3: Optimization (Weeks X-Y)**
- Performance tuning
- Security audit
- Complete documentation
- Deliverable: {Output}

**Phase 4: Launch (Final weeks)**
- Production deployment
- Team training (2 sessions)
- 8-week support period
- Deliverable: {Output}

---

**Technical Approach**:
- Stack: {Tech stack - 1 line}
- Architecture: {1-2 sentences}
- Integration: {Key integrations}

**What's Included**:
- ✅ {Feature 1}
- ✅ {Feature 2}
- ✅ {Feature 3}
- ✅ {Feature 4}
- ✅ Enterprise security & testing
- ✅ Complete documentation
- ✅ Knowledge transfer

**Out of Scope**:
- ❌ {Item 1}
- ❌ {Item 2}
- ❌ {Item 3}

**Success Metrics**:
1. {Metric 1}
2. {Metric 2}
3. {Metric 3}

**Timeline**: {X} weeks
- Week 2: Architecture approval
- Week X: Feature freeze
- Week Y: Go-live

**Communication**:
- Weekly updates (email)
- Bi-weekly sync (30min)
- Slack for ad-hoc

---

**Next Steps**:
1. Review proposal
2. Schedule 30min call
3. Sign agreement

Looking forward to partnering!

Best,
[Your Name]
```

### Generation Guidelines

1. **Be Specific**: Tailor content to the project_name provided
2. **Be Realistic**: Set achievable timelines and deliverables
3. **Be Professional**: Use consulting industry best practices
4. **Be Clear**: Avoid jargon, explain technical terms
5. **Be Comprehensive**: Cover all aspects (scope, timeline, risks)

### Content Customization

Based on project_name keywords, intelligently adapt:
- **"Website/Web App"** → Focus on frontend, UX, responsive design
- **"API/Integration"** → Focus on backend, data flows, authentication
- **"AI/ML"** → Focus on model development, training, deployment
- **"Migration"** → Focus on data transfer, downtime, rollback plans
- **"Mobile"** → Focus on iOS/Android, app stores, testing
- **"Dashboard/Analytics"** → Focus on data visualization, reporting
- **"Knowledge Graph"** → Focus on graph databases, relationships, visualization
- **"Influence/Social"** → Focus on network analysis, scoring algorithms, engagement metrics

### After Generation

After generating the proposal file, provide this summary:

```
✅ Proposal Generated:

📁 proposals/{project-slug}-{YYYYMMDD}/proposal.md
   ({tier} tier - ~{line_count} lines)

Next steps:
1. Review and customize
2. Update [Your Name]
3. Copy/paste into email to {client_name}
```

---

**Remember**:
- Generate professional, tailored proposals that position you as the expert
- Be clear and realistic about deliverables and timelines
- Always save files in the correct directory structure
