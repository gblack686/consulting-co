---
title: "TAC Lesson 12 Quiz - Multi-Agent Orchestration"
lesson: 12
questions: 20
difficulty: Advanced
tactic: "Orchestrator Pattern"
diagram: "../diagrams/agent-evolution.excalidraw"
---

# Lesson 12 Quiz: Multi-Agent Orchestration

> **Focus:** The Orchestrator Agent and Fleet Management
> **Diagram Reference:** [[../diagrams/agent-evolution.excalidraw]]
> **Loot Reference:** [[loot.md]]

---

## Section A: Multiple Choice (10 questions)

### Q1. What is the full Agent Evolution Path?
- A) Base → Better → Custom
- B) Base → Better → More → Custom → Orchestrated
- C) Simple → Complex
- D) One → Many

→ [[#A1]]

---

### Q2. What is the Single Interface Pattern?
- A) One UI for users
- B) One orchestrator agent that creates, commands, and deletes agents
- C) One API endpoint
- D) One codebase

→ [[#A2]]

---

### Q3. What are the Three Pillars of Multi-Agent Orchestration?
- A) Speed, Cost, Quality
- B) Orchestrator, CRUD for Agents, Observability
- C) Plan, Build, Ship
- D) Input, Process, Output

→ [[#A3]]

---

### Q4. What does PETER stand for in multi-agent systems?
- A) Plan, Execute, Test, Evaluate, Review
- B) Prompt input, Trigger (HTTP), Environment, Review (observability)
- C) Process, Engineer, Test, Execute, Release
- D) Plan, Engineer, Test, Evaluate, Report

→ [[#A4]]

---

### Q5. Why is observability key in multi-agent systems?
- A) It looks cool
- B) If you can't measure it, you can't improve or scale it
- C) It's required by law
- D) It's free

→ [[#A5]]

---

### Q6. What is CRUD for Agents?
- A) A new programming language
- B) Create, Read, Update, Delete operations for agents
- C) A testing framework
- D) A documentation standard

→ [[#A6]]

---

### Q7. What becomes your engineering output constraint in multi-agent systems?
- A) Computing power
- B) The rate at which you create and command agents
- C) Memory
- D) Network speed

→ [[#A7]]

---

### Q8. How does the R&D Framework apply to multi-agent context?
- A) It doesn't apply
- B) Reduce context in orchestrator, Delegate to specialized sub-agents
- C) Add more context everywhere
- D) Ignore context management

→ [[#A8]]

---

### Q9. What must you track for every agent you spin up?
- A) Only cost
- B) Context windows, models, prompts, and tools (Core Four)
- C) Only time
- D) Only errors

→ [[#A9]]

---

### Q10. What is "Adopt your agent's perspective multiplied"?
- A) Using multiple monitors
- B) Tracking the Core Four across your entire fleet
- C) Hiring more engineers
- D) Using larger models

→ [[#A10]]

---

## Section B: True or False (6 questions)

### Q11. Multi-agent orchestration is an out-loop system.
→ [[#A11]]

---

### Q12. You don't need to track context windows for every agent.
→ [[#A12]]

---

### Q13. The R&D Framework doesn't apply to multi-agent systems.
→ [[#A13]]

---

### Q14. One orchestrator agent can command a fleet of specialized agents.
→ [[#A14]]

---

### Q15. Observability is optional for multi-agent success.
→ [[#A15]]

---

### Q16. The Single Interface Pattern uses multiple orchestrators.
→ [[#A16]]

---

## Section C: Fill in the Blank (2 questions)

### Q17. "If you can't __________ it, you can't improve it. If you can't measure it, you can't scale it."
→ [[#A17]]

---

### Q18. "The rate at which you create and command agents becomes your engineering __________ constraint."
→ [[#A18]]

---

## Section D: Short Answer (2 questions)

### Q19. Explain the Three Pillars of Multi-Agent Orchestration. (Reference: [[loot.md#The Three Pillars of Multi-Agent Orchestration]])
→ [[#A19]]

---

### Q20. How does multi-agent orchestration compound engineering leverage? (Reference: [[loot.md#Out-Loop Multi-Agent Systems]])
→ [[#A20]]

---

## Answers

### A1
**B) Base → Better → More → Custom → Orchestrated**
The complete evolution path for agentic engineering.

### A2
**B) One orchestrator agent that creates, commands, and deletes agents**
One interface to rule them all.

### A3
**B) Orchestrator, CRUD for Agents, Observability**
The three essential pillars for multi-agent success.

### A4
**B) Prompt input, Trigger (HTTP), Environment, Review (observability)**
PETER for multi-agent out-loop systems.

### A5
**B) If you can't measure it, you can't improve or scale it**
Observability is essential for improvement and scaling.

### A6
**B) Create, Read, Update, Delete operations for agents**
Standard operations for managing agents at scale.

### A7
**B) The rate at which you create and command agents**
Agent creation/command rate becomes the constraint.

### A8
**B) Reduce context in orchestrator, Delegate to specialized sub-agents**
R&D applies by reducing orchestrator context and delegating.

### A9
**B) Context windows, models, prompts, and tools (Core Four)**
Track the Core Four for every agent in your fleet.

### A10
**B) Tracking the Core Four across your entire fleet**
Adopt perspective at scale across all agents.

### A11
**True** - Multi-agent orchestration is an out-loop PETER system.

### A12
**False** - Track context windows for EVERY agent you spin up.

### A13
**False** - R&D applies: Reduce in orchestrator, Delegate to sub-agents.

### A14
**True** - One orchestrator commands the entire fleet.

### A15
**False** - Observability is ESSENTIAL, not optional.

### A16
**False** - Single Interface Pattern uses ONE orchestrator.

### A17
**measure** - "If you can't measure it, you can't improve it."

### A18
**output** - "...becomes your engineering output constraint."

### A19
The Three Pillars are:

1. **Orchestrator Agent** - The unified interface to command all agents. One orchestrator talks to all specialized agents.

2. **CRUD for Agents** - Create, Read, Update, Delete operations for managing agents at scale. Enables dynamic fleet management.

3. **Observability** - Real-time monitoring of performance, costs, and results. Essential because "if you can't measure it, you can't improve or scale it."

### A20
Multi-agent orchestration compounds leverage by:

- **Out-loop execution** - PETER system (Prompt, Trigger HTTP, Environment, Review via observability)
- **Fleet management** - Command multiple specialized agents through one interface
- **R&D at scale** - Reduce context in orchestrator, delegate to focused sub-agents
- **Parallel execution** - Multiple agents working simultaneously
- **Automated CRUD** - Create, manage, and delete agents programmatically
- **Observability** - Track and improve the entire system continuously

The constraint shifts from your abilities to the rate at which you can create and command agents.

---

## Score Guide

| Score | Level |
|-------|-------|
| 18-20 | Mastery |
| 15-17 | Proficient |
| 12-14 | Developing |
| <12 | Review [[loot.md]] and [[transcript.txt]] |

---

[[loot.md]] | [[transcript.txt]] | [[../diagrams/agent-evolution.excalidraw]]
