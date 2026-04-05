# GB Automation Landing Page - Product Requirements Document (PRD)

## 1. Overview & Project Details

| Field | Detail |
|-------|--------|
| **Project Title** | GB Automation - Agentic Systems Program Landing Page |
| **Product Manager** | Greg Black |
| **Version** | 1.0 |
| **Status** | In Progress |
| **Target Release Date** | November 2025 |
| **Team/Stakeholders** | Greg Black (Developer/Owner) |
| **Document Date** | November 2, 2025 |

---

## 2. Purpose & Objectives

- **Problem Statement:** Technical founders and businesses need a clear way to understand and engage with GB Automation's Agentic Systems Program without lengthy discovery calls. Current lack of web presence makes it difficult to communicate value proposition and capture qualified leads.

- **Vision:** A high-converting landing page that clearly articulates the "Vibe Coding" methodology, showcases the 90-day Agentic Systems Program, and captures qualified leads through a contact form.

- **Business Objectives (SMART goals):**
  - Launch production landing page within 1 week
  - Capture 10+ qualified leads per month through contact form
  - Achieve sub-2 second page load time
  - Mobile-responsive design for 50%+ mobile traffic

- **Success Metrics/KPIs:**
  - Contact form conversion rate > 3%
  - Average time on page > 90 seconds
  - Bounce rate < 60%
  - Form submissions tracked in DynamoDB

---

## 3. Target Audience & User Stories

- **User Personas:**
  - **Technical Founder Tom:** 30-45 years old, has raised seed funding, needs to build AI infrastructure fast, understands APIs and cloud services, wants hands-on collaboration
  - **VP Engineering Emily:** Works at mid-size company, tasked with AI innovation, looking for external expertise to accelerate POC development, needs to justify investment to leadership

- **User Stories/Use Cases:**
  - "As a technical founder, I want to quickly understand what the Agentic Systems Program delivers so I can decide if it fits my needs"
  - "As a VP of Engineering, I want to see the technical stack and methodology so I can evaluate feasibility"
  - "As a potential client, I want to easily submit my information and schedule a discovery call"
  - "As a mobile user, I want to browse the landing page smoothly on my phone"

---

## 4. Features & Functional Requirements

### Core Features (P0 - Must Have)

#### Hero Section:
- **Description/Purpose:** Immediately communicate value proposition
- **Functionality:**
  - Headline: "Build Smarter and Faster with an AI Developer That Codes in Your Vibe"
  - Subheadline: 90-day program overview
  - Primary CTA: "Schedule Discovery Call" button
  - Secondary CTA: "Learn More" (scroll to features)
- **Acceptance Criteria:**
  - Hero visible above fold on all screen sizes
  - CTA buttons clearly clickable with hover states
  - Compelling visual or animation present

#### What You Get Section:
- **Description/Purpose:** Showcase the 3 Claude agents and deliverables
- **Functionality:**
  - Display 3 agent types with icons/descriptions
  - List key deliverables (RAG backend, CloudFormation kit, interface options)
  - Visual representation of system architecture
- **Acceptance Criteria:**
  - Icons/graphics load properly
  - Text is scannable and concise
  - Clear visual hierarchy

#### Process Overview Section:
- **Description/Purpose:** Explain the 90-day engagement structure
- **Functionality:**
  - Display 4 phases: Vibe Discovery, Development Sprint, Agent Orchestration, Handoff
  - Timeline visualization
  - Clear explanation of collaboration model
- **Acceptance Criteria:**
  - Easy to understand at a glance
  - Visual timeline or diagram included

#### Pricing Section:
- **Description/Purpose:** Transparent pricing for $50K / 90 days
- **Functionality:**
  - Display price prominently
  - List what's included
  - Show support level (20+ hrs/week)
  - Optional add-ons mentioned
- **Acceptance Criteria:**
  - Price clearly visible
  - Value proposition evident
  - CTA to contact/schedule

#### Contact Form (P0):
- **Description/Purpose:** Capture qualified leads with context
- **Functionality:**
  - Fields: Name (required), Email (required), Company, Phone, Message (required)
  - Field: "What are you looking to build?" (textarea)
  - Validation for email format
  - Submit to AWS Amplify Data (DynamoDB)
  - Success message after submission
  - Error handling for failed submissions
- **Acceptance Criteria:**
  - Form validates input before submission
  - Data saved to DynamoDB successfully
  - User receives clear feedback (success/error)
  - Email notification sent to greg@gbautomation.xyz (optional P1)

#### Footer:
- **Description/Purpose:** Contact info and branding
- **Functionality:**
  - Email: greg@gbautomation.xyz
  - Copyright and company name
  - Optional: Social links (LinkedIn)
- **Acceptance Criteria:**
  - Email link works (mailto:)
  - Copyright year dynamic or current

### P1 Features (High Value)
- Email notification on form submission
- LinkedIn profile link
- Testimonial section (once available)
- Case study snippets

### P2 Features (Nice to Have)
- Dark mode toggle
- Animated process diagram
- Blog section
- FAQ accordion

### Data Model Requirements

**ContactSubmission Model:**
```typescript
{
  id: string (auto-generated)
  name: string (required)
  email: string (required)
  company: string (optional)
  phone: string (optional)
  message: string (required)
  projectDescription: string (required)
  createdAt: datetime (auto)
  status: enum ["new", "contacted", "qualified", "closed"] (default: "new")
}
```

---

## 5. Non-Functional Requirements

- **Performance:**
  - Initial page load < 2 seconds on 4G connection
  - Largest Contentful Paint (LCP) < 2.5s
  - Contact form submission response < 500ms
  - Images optimized and lazy-loaded

- **Security:**
  - HTTPS only
  - Input sanitization on all form fields
  - Rate limiting on form submissions (prevent spam)
  - No authentication required (public landing page)
  - API endpoints protected with CORS

- **Reliability & Supportability:**
  - 99.9% uptime (via AWS Amplify hosting)
  - Form submission errors logged
  - Graceful error handling with user-friendly messages
  - Analytics tracking (Google Analytics or similar)

- **Usability & Accessibility:**
  - Mobile-first responsive design
  - WCAG 2.1 AA compliance
  - Keyboard navigation support
  - Screen reader compatible
  - Minimum font size 16px
  - High contrast text (4.5:1 ratio)
  - Clear focus indicators

- **Environment:**
  - Target browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
  - Mobile: iOS Safari, Chrome Android
  - Tablet support

---

## 6. Technical Specifications (Amplify Specific)

- **AWS Services:**
  - **Amplify Hosting:** CI/CD, static hosting, custom domain
  - **Amplify Data:** GraphQL API with DynamoDB backend for contact form submissions
  - **Optional:** Amazon SES for email notifications

- **Frontend Framework:**
  - React 18+
  - Vite for build tooling (fast dev experience)
  - Tailwind CSS for styling
  - React Hook Form for form management
  - Framer Motion for animations (optional)

- **CI/CD Workflow:**
  - Main branch deploys to production
  - Feature branches auto-deploy to preview URLs
  - Git-based workflow via AWS Amplify console

- **Development Environment Prerequisites:**
  - Node.js 18+ (preferably 20+)
  - npm or pnpm
  - Git
  - AWS Account with Amplify access
  - AWS CLI configured

---

## 7. Assumptions, Constraints, & Dependencies

- **Assumptions:**
  - Users have modern browsers with JavaScript enabled
  - Most traffic will come from LinkedIn and direct referrals
  - Contact form submissions represent qualified leads (not spam)

- **Constraints:**
  - Budget: Minimal AWS costs (< $10/month for hosting + DynamoDB)
  - Timeline: 1 week to production
  - No backend team - serverless only

- **Dependencies:**
  - AWS account access
  - Domain name for production (gbautomation.xyz or similar)
  - Email address for contact notifications

---

## 8. Timeline & Milestones

- **Major Milestones:**
  - Day 1: PRD complete, local dev environment setup
  - Day 2: React app scaffolded, basic layout and styling
  - Day 3: Contact form with Amplify Data integration
  - Day 4: Content population, responsive design refinement
  - Day 5: AWS Amplify setup and dev deployment
  - Day 6: Testing, accessibility audit, performance optimization
  - Day 7: Production deployment

- **Release Plan:**
  - v1.0: Core landing page with contact form
  - v1.1: Email notifications, analytics integration
  - v1.2: Testimonials section (when available)
  - v2.0: Blog/content section

- **Open Questions:**
  - Domain name preference? (gbautomation.xyz or other?)
  - Specific design preferences or brand colors?
  - Existing logo/brand assets?
  - Calendly or similar for scheduling integration?
