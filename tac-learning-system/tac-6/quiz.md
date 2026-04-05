---
title: "TAC Lesson 6 Quiz - Let Your Agents Focus"
lesson: 6
questions: 22
difficulty: Advanced
tactic: "One Agent, One Prompt, One Purpose"
diagram: "../diagrams/adw-architecture.excalidraw"
---

# Lesson 6 Quiz: Let Your Agents Focus

> **Tactic #6:** One Agent, One Prompt, One Purpose
> **Diagram Reference:** [[../diagrams/adw-architecture.excalidraw]]
> **Loot Reference:** [[loot.md]]

---

## Section A: Multiple Choice (10 questions)

### Q1. What is Tactic #6?
- A) Always Add Feedback Loops
- B) One Agent, One Prompt, One Purpose
- C) Target Zero-Touch Engineering
- D) Prioritize Agentics

→ [[#A1]]

---

### Q2. What is "context pollution"?
- A) Dirty data in your database
- B) Overloading context window causing distracted agents
- C) Bad documentation
- D) Too many files in a repo

→ [[#A2]]

---

### Q3. What are the three constraints of agentic engineers?
- A) Time, money, resources
- B) Context window, codebase complexity, our abilities
- C) Speed, accuracy, cost
- D) Model, prompt, tools

→ [[#A3]]

---

### Q4. What does the Minimum Context Principle state?
- A) Use the minimum context required to solve the problem
- B) Always provide maximum context
- C) Context doesn't matter
- D) Only use structured context

→ [[#A4]]

---

### Q5. What question does PLAN answer?
- A) Did we make it real?
- B) Does it work?
- C) What are we building?
- D) How does it work?

→ [[#A5]]

---

### Q6. What question does REVIEW answer?
- A) Does it work?
- B) Is what we built what we planned?
- C) What are we building?
- D) How fast is it?

→ [[#A6]]

---

### Q7. What question does DOCUMENT answer?
- A) What are we building?
- B) Did we make it real?
- C) How does it work?
- D) Is it deployed?

→ [[#A7]]

---

### Q8. What MCP tool is introduced for browser automation?
- A) Selenium MCP
- B) Puppeteer MCP
- C) Playwright MCP
- D) Cypress MCP

→ [[#A8]]

---

### Q9. How many constraints do specialized agents bypass?
- A) One out of three
- B) Two out of three
- C) All three
- D) None

→ [[#A9]]

---

### Q10. Why should agents run single prompts?
- A) To save tokens
- B) To let agents focus on one purpose well
- C) To reduce costs
- D) To simplify debugging

→ [[#A10]]

---

## Section B: True or False (7 questions)

### Q11. A focused engineer is a productive engineer; agents are the same.
→ [[#A11]]

---

### Q12. Big context windows always improve agent performance.
→ [[#A12]]

---

### Q13. Every piece of context increases variables agents must reason about.
→ [[#A13]]

---

### Q14. Specialized agents bypass 2 of 3 engineering constraints.
→ [[#A14]]

---

### Q15. Documentation creates feedback loops for future agents.
→ [[#A15]]

---

### Q16. You should add as much context as possible to help agents.
→ [[#A16]]

---

### Q17. By using individualized agents, you effectively create evals for your codebase.
→ [[#A17]]

---

## Section C: Matching (1 question)

### Q18. Match each SDLC step to its question:

| Step | Question |
|------|----------|
| Plan | _____ |
| Build | _____ |
| Test | _____ |
| Review | _____ |
| Document | _____ |

Options:
- A) Does it work?
- B) Is what we built what we planned?
- C) What are we building?
- D) Did we make it real?
- E) How does it work?

→ [[#A18]]

---

## Section D: Fill in the Blank (2 questions)

### Q19. "A focused engineer working on a single task is a __________ engineer."
→ [[#A19]]

---

### Q20. "You want to context engineer as __________ as possible."
→ [[#A20]]

---

## Section E: Short Answer (2 questions)

### Q21. Explain why every step of engineering requires different context. (Reference: [[loot.md#Engineering Steps Require Different Context]])
→ [[#A21]]

---

### Q22. How do individualized agents with specific prompts create evals for your codebase? (Reference: [[loot.md#Create Evals for Your Agentic Layer]])
→ [[#A22]]

---

## Answers

### A1
**B) One Agent, One Prompt, One Purpose**

### A2
**B) Overloading context window causing distracted agents**
Context pollution makes agents lose focus on the original task.

### A3
**B) Context window, codebase complexity, our abilities**
These are the three fundamental constraints we work within.

### A4
**A) Use the minimum context required to solve the problem**
Less context means agents can focus better.

### A5
**C) What are we building?**
Planning answers the foundational "what" question.

### A6
**B) Is what we built what we planned?**
Review validates against the original plan.

### A7
**C) How does it work?**
Documentation explains the implementation.

### A8
**C) Playwright MCP**
Playwright MCP enables browser automation for agents.

### A9
**B) Two out of three**
Specialized agents bypass context window and codebase complexity constraints.

### A10
**B) To let agents focus on one purpose well**
Single prompts allow maximum focus and effectiveness.

### A11
**True** - Focus is equally important for agents and engineers.

### A12
**False** - Big context windows often cause confusion and distraction.

### A13
**True** - More context = more variables = harder reasoning.

### A14
**True** - They bypass context window and codebase complexity.

### A15
**True** - Documentation provides feedback for future agent reference.

### A16
**False** - You want MINIMUM context required to solve the problem.

### A17
**True** - Specialized agents enable eval creation for your agentic layer.

### A18
| Step | Question |
|------|----------|
| Plan | **C) What are we building?** |
| Build | **D) Did we make it real?** |
| Test | **A) Does it work?** |
| Review | **B) Is what we built what we planned?** |
| Document | **E) How does it work?** |

### A19
**productive** - "A focused engineer working on a single task is a productive engineer."

### A20
**little** - "You want to context engineer as little as possible."

### A21
Every step of engineering requires a different set of:
- Information
- Approach and perspective
- Tools
- Context

Planning needs different context than building. Testing needs different context than reviewing. By honoring these differences with dedicated agents, each step can be optimized independently.

### A22
By using individualized agents with specific prompts for one purpose:
- You can change the model and rerun
- You can add thinking mode and rerun
- You can change your agentic coding tool and rerun
- Each specialized prompt becomes a repeatable eval
- You can measure and compare performance across configurations

This creates a testing framework for your agentic layer itself.

---

## Score Guide

| Score | Level |
|-------|-------|
| 20-22 | Mastery |
| 17-19 | Proficient |
| 13-16 | Developing |
| <13 | Review [[loot.md]] and [[transcript.txt]] |

---

[[loot.md]] | [[transcript.txt]] | [[../diagrams/adw-architecture.excalidraw]]
