# Master Consulting Questions - Simplified & Categorized

**Purpose:** Comprehensive discovery questions for AI/cloud consulting projects. No redundancies.

---

## 1. 🎯 Problem & Goals

1. What problem are you solving?
2. Who has this problem?
3. How are they solving it today?
4. What does success look like?
5. How will you measure success?
6. Why now? What's the urgency?
7. What happens if this doesn't get built?

---

## 2. 👥 Users & Usage

8. Who are the primary users?
9. How many users? (current and 6-month projection)
10. What's their technical skill level?
11. What devices/platforms will they use?
12. How will they access the system? (web, mobile, API, CLI)

---

## 3. 💼 Business Context

13. What's the business impact? (revenue, cost savings, risk reduction)
14. Can you quantify the value?
15. Which stakeholders care most?
16. Is this standalone or part of a larger initiative?
17. Are follow-on phases planned?

---

## 4. ⚙️ Core Features

18. What are the 2-3 must-have features?
19. What's explicitly NOT in scope for v1?
20. Walk me through a typical user workflow
21. What inputs does the system receive?
22. What outputs does it produce?
23. What's the data format? (JSON, CSV, PDF, etc.)

---

## 5. 🧮 Business Logic

24. Are there specific algorithms or processing rules?
25. Any regulatory or compliance requirements?
26. Any third-party services that must be used?

---

## 6. 🔗 Integrations

27. What existing systems does this integrate with?
28. For each integration: What data flows in/out? How often?
29. What authentication systems? (Okta, AD, Cognito)
30. Do you have an existing AWS environment?
31. Any existing infrastructure to leverage?

---

## 7. 🎨 UI/UX

32. Is there an existing UI we integrate with?
33. If new UI: Are there design guidelines or branding?

---

## 8. ⚡ Performance & Scale

34. What's an acceptable response time?
35. How many requests per day? (current and peak)
36. How much data will be stored?
37. Expected growth rate over 12 months?
38. Any seasonal spikes?

---

## 9. 🔒 Security & Compliance

39. What type of data? (PII, PHI, financial, confidential)
40. Any compliance requirements? (HIPAA, SOC 2, GDPR)
41. Data residency requirements?
42. Encryption requirements?
43. What user roles/permissions are needed?
44. SSO required?
45. API authentication approach?

---

## 10. 💾 Data Management

46. How long must data be kept?
47. Any archival or deletion policies?
48. Audit trail requirements?
49. Recovery time objective (RTO)?
50. Recovery point objective (RPO)?

---

## 11. 🛠️ Technical Stack

51. What programming languages does your team know?
52. What frameworks are you standardized on?
53. What's your team's AWS experience level?
54. Experience with Infrastructure as Code? (CDK, Terraform)
55. What CI/CD tools do you use?
56. What monitoring and logging tools?

---

## 12. 🚧 Constraints

57. Must use or avoid specific AWS services?
58. Any networking constraints? (VPC, private subnets)
59. Budget constraints or cost targets?
60. Timeline constraints?

---

## 13. 📚 History & Context

61. Have you tried solving this before? What happened?
62. What should we avoid repeating?
63. Any existing code or systems to reference?

---

## 14. ✅ Validation & Testing

64. How will you validate this works?
65. Do you have test data?
66. Who signs off before launch?
67. What does "production ready" mean to you?

---

## 15. 📊 Monitoring & Metrics

68. What metrics matter most? (latency, error rate, usage)
69. Who gets alerted when something goes wrong?
70. What dashboards or reports do you need?

---

## 16. 📅 Timeline & Scope

71. When do you need this in production?
72. Are there immovable deadlines?
73. What's the minimum viable product?
74. What features can wait for phase 2?

---

## 17. 🤝 Team & Communication

75. Who makes final decisions?
76. Who provides technical input?
77. Who's the day-to-day point of contact?
78. What's your preferred communication cadence?
79. What collaboration tools? (Slack, Teams, email)

---

## 18. ⚠️ Risks & Assumptions

80. What assumptions are you making?
81. What could go wrong?
82. What unknowns worry you?

---

## 19. 📄 Documentation & Access

83. Can you share existing specs or architecture diagrams?
84. Can we access your AWS environment for discovery?
85. Who else should we talk to?

---

## Quick Reference by Priority

### 🔴 Critical (Must Ask Every Call)
1, 4, 5, 8, 18, 20, 27, 30, 39, 40, 57, 71, 75

### 🟡 High Priority (Ask Unless Clear)
2, 6, 13, 21, 22, 34, 35, 41, 51, 64, 73, 78

### 🟢 Contextual (Ask When Relevant)
All others - adjust based on project type

---

## Question Mapping to Deliverables

| Deliverable | Questions |
|-------------|-----------|
| **Executive Summary** | 1-7, 13-17 |
| **Technical Requirements** | 18-26, 51-55 |
| **Architecture Design** | 27-31, 34-38, 57-59 |
| **Security & Compliance** | 39-45 |
| **Data Design** | 21-23, 46-50 |
| **Testing Strategy** | 64-67 |
| **Monitoring Plan** | 68-70 |
| **Project Plan** | 71-79 |
| **Risk Register** | 80-82 |

---

## Tips for Using This List

### Before the Call
- Review client's industry and typical use cases
- Mark questions already answered in prior materials
- Prepare follow-ups based on initial info

### During the Call
- Start with Category 1 (Problem & Goals)
- Skip questions if already answered
- Drill deeper when you hear vague answers
- Listen for enthusiasm (reveals priorities)
- Note areas of stakeholder disagreement

### Red Flags to Watch
- "We need everything" → Scope creep
- Vague success criteria → Misaligned expectations
- "We'll figure it out later" → Missing requirements
- Unrealistic timeline → Need to negotiate

### After the Call
- Flag gaps needing clarification
- Summarize decisions in writing
- Schedule technical deep-dive if needed

---

**Total Questions:** 85 (streamlined from 100+ original)
**Average Discovery Call:** 45-60 minutes covering ~30 questions
**Follow-up Call:** Deep dive on technical questions (27-59)

**Created:** 2025-11-14
**Last Updated:** 2025-11-14
