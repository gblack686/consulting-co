---
title: "TAC Lesson 5 Quiz - Close The Loops"
lesson: 5
questions: 22
difficulty: Intermediate
tactic: "Always Add Feedback Loops"
diagram: "../diagrams/adw-architecture.excalidraw"
---

# Lesson 5 Quiz: Close The Loops

> **Tactic #5:** Always Add Feedback Loops
> **Diagram Reference:** [[../diagrams/adw-architecture.excalidraw]]
> **Loot Reference:** [[loot.md]]

---

## Section A: Multiple Choice (10 questions)

### Q1. What is Tactic #5?
- A) Stay Out The Loop
- B) Always Add Feedback Loops
- C) One Agent, One Purpose
- D) Target Zero-Touch Engineering

→ [[#A1]]

---

### Q2. What is the difference between testing and review?
- A) Testing is automated, review is manual
- B) Testing asks "does it work?", Review asks "is it what we planned?"
- C) Testing is faster than review
- D) There is no difference

→ [[#A2]]

---

### Q3. What happens when you "close the loop"?
- A) You end the agent session
- B) Agent operates, gets feedback, continues until positive
- C) You delete old code
- D) You merge the PR

→ [[#A3]]

---

### Q4. According to the lesson, your work is useless unless it's:
- A) Documented
- B) Reviewed
- C) Tested
- D) Deployed

→ [[#A4]]

---

### Q5. What validates your agent's work in a closed loop system?
- A) Human review only
- B) Linters, unit tests, UI tests, E2E tests
- C) Customer feedback
- D) Code comments

→ [[#A5]]

---

### Q6. What is the "ultimate test" of your work?
- A) Unit tests
- B) Your users
- C) Code review
- D) CI/CD pipeline

→ [[#A6]]

---

### Q7. What was the "next best test" before agents?
- A) Integration tests
- B) You (manual testing)
- C) QA team
- D) Automated scripts

→ [[#A7]]

---

### Q8. What is the "next best test" now with agents?
- A) More manual testing
- B) An army of agents validating your codebase
- C) External QA services
- D) Customer beta testing

→ [[#A8]]

---

### Q9. What does "in-loop" agent coding mean?
- A) Running agents in containers
- B) You prompting back and forth with your agent
- C) Circular dependencies
- D) Infinite loops in code

→ [[#A9]]

---

### Q10. What does "out-loop" mean?
- A) Breaking out of loops
- B) High-level prompts running through PITER on isolated devices
- C) External APIs
- D) Cloud computing

→ [[#A10]]

---

## Section B: True or False (7 questions)

### Q11. Manual testing (clicking through the browser) is efficient use of time.
→ [[#A11]]

---

### Q12. Engineers that test with their agents win, with zero exceptions.
→ [[#A12]]

---

### Q13. The value of tests is multiplied by the number of agent executions.
→ [[#A13]]

---

### Q14. In-loop prompting is preferred over out-loop systems as you progress.
→ [[#A14]]

---

### Q15. Closing the loop lets the code write itself.
→ [[#A15]]

---

### Q16. Architecture leverage is irrelevant to validation and testing.
→ [[#A16]]

---

### Q17. End-to-end agents are preferable to in-loop agents.
→ [[#A17]]

---

## Section C: Fill in the Blank (3 questions)

### Q18. "We want attempts _____, size up, streak up, and presence _____."
→ [[#A18]]

---

### Q19. "Your work is useless unless it's __________."
→ [[#A19]]

---

### Q20. "This is us building the __________ that builds the system."
→ [[#A20]]

---

## Section D: Short Answer (2 questions)

### Q21. List at least five examples of validation steps that can be handed off to agents. (Reference: [[loot.md#Common Validation Steps]])
→ [[#A21]]

---

### Q22. Explain the Agentic KPIs and why they matter. (Reference: [[loot.md#Agentic KPIs]])
→ [[#A22]]

---

## Answers

### A1
**B) Always Add Feedback Loops**

### A2
**B) Testing asks "does it work?", Review asks "is it what we planned?"**
These are fundamentally different questions requiring different approaches.

### A3
**B) Agent operates, gets feedback, continues until positive**
Closed loops let agents self-correct until the job is done right.

### A4
**C) Tested**
Your work is useless unless it's tested - the ultimate test is your users.

### A5
**B) Linters, unit tests, UI tests, E2E tests**
Multiple validation mechanisms create comprehensive feedback loops.

### A6
**B) Your users**
The ultimate test will always be your users.

### A7
**B) You (manual testing)**
Before agents, you were the next best test after users.

### A8
**B) An army of agents validating your codebase**
Now agents can validate at scales you never could.

### A9
**B) You prompting back and forth with your agent**
In-loop means interactive, conversational prompting.

### A10
**B) High-level prompts running through PITER on isolated devices**
Out-loop means autonomous execution without your direct involvement.

### A11
**False** - Manual testing is a waste of time - hand it off to agents.

### A12
**True** - Engineers that test with agents win, full stop, zero exceptions.

### A13
**True** - Tests multiply in value with each agent execution.

### A14
**False** - You want LESS in-loop prompting as you progress.

### A15
**True** - Closing the loop lets the code write itself.

### A16
**False** - Architecture is a massive leverage point for validation.

### A17
**True** - End-to-end agents, not in-loop agents, are the goal.

### A18
**down, down** - "We want attempts down, size up, streak up, and presence down."

### A19
**tested** - "Your work is useless unless it's tested."

### A20
**system** - "This is us building the system that builds the system."

### A21
Examples of validation steps:
1. Run your linter
2. Execute unit tests
3. Run UI tests
4. CI/CD integration tests
5. Build/compile your application
6. Check Datadog logs
7. Monitor Sentry for errors
8. Run custom evaluations
9. LLM as judge workflows

### A22
The Agentic KPIs are:
- **Attempts down** - Fewer iterations needed
- **Size up** - Handle larger tasks
- **Streak up** - Longer successful runs
- **Presence down** - Less human intervention required

These matter because they measure your progress toward autonomous agent systems. Better KPIs mean more leverage and less manual work.

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
