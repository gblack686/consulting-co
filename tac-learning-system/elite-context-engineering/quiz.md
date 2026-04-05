---
title: "TAC Lesson 9 Quiz - Elite Context Engineering"
lesson: 9
questions: 20
difficulty: Intermediate
tactic: "Context Engineering"
diagram: "../diagrams/core-four.excalidraw"
---

# Lesson 9 Quiz: Elite Context Engineering

> **Focus:** R&D Framework for Context Management
> **Diagram Reference:** [[../diagrams/core-four.excalidraw]]
> **Loot Reference:** [[loot.md]]

---

## Section A: Multiple Choice (10 questions)

### Q1. What is the R&D Framework for context management?
- A) Research and Development
- B) Reduce and Delegate
- C) Read and Delete
- D) Review and Document

→ [[#A1]]

---

### Q2. How many levels of context engineering are there?
- A) Two
- B) Three (plus a hidden fourth)
- C) Five
- D) Seven

→ [[#A2]]

---

### Q3. What is "context priming"?
- A) Loading maximum context upfront
- B) Using dedicated reusable prompts to set up initial context
- C) Deleting old context
- D) Compressing context

→ [[#A3]]

---

### Q4. What problem do always-on memory files (claude.md) have?
- A) They're too small
- B) They grow bloated with irrelevant or contradictory info
- C) They're too fast
- D) They cost money

→ [[#A4]]

---

### Q5. Why should you delete default .mcp.json files?
- A) They're insecure
- B) They consume 10-12% of context window wastefully
- C) They slow down agents
- D) They're deprecated

→ [[#A5]]

---

### Q6. What is the "context sweet spot"?
- A) The cheapest token range
- B) The range where your agent performs at maximum capability
- C) The minimum context
- D) The maximum context

→ [[#A6]]

---

### Q7. What happens when you're "vibe coding"?
- A) You write better code
- B) You're not paying attention to context state
- C) You're in flow state
- D) You're pair programming

→ [[#A7]]

---

### Q8. What should you install in your IDE for context management?
- A) A debugger
- B) A token counter/tokenizer
- C) A linter
- D) A formatter

→ [[#A8]]

---

### Q9. What are the only two ways to manage your context window?
- A) Add and Remove
- B) Reduce and Delegate
- C) Compress and Expand
- D) Load and Unload

→ [[#A9]]

---

### Q10. What replaces claude.md files in context priming?
- A) Larger memory files
- B) Dedicated reusable prompts (custom slash commands)
- C) Database storage
- D) Cloud sync

→ [[#A10]]

---

## Section B: True or False (6 questions)

### Q11. A focused agent is a performant agent.
→ [[#A11]]

---

### Q12. The context window is NOT a precious resource.
→ [[#A12]]

---

### Q13. MCP servers should be loaded by default in every project.
→ [[#A13]]

---

### Q14. There's a "sweet spot" range where agents perform optimally.
→ [[#A14]]

---

### Q15. Always-on context like claude.md is dynamic and controllable.
→ [[#A15]]

---

### Q16. If you can't measure context, you can't improve it.
→ [[#A16]]

---

## Section C: Fill in the Blank (2 questions)

### Q17. "Context engineering is the name of the game for high value engineering in the age of __________."
→ [[#A17]]

---

### Q18. "Your agent's context window is a precious, renewable, but limited __________ resource."
→ [[#A18]]

---

## Section D: Short Answer (2 questions)

### Q19. Explain the R&D Framework and how it applies to context management. (Reference: [[loot.md#The R&D Framework]])
→ [[#A19]]

---

### Q20. What are the problems with always-on memory files like claude.md? (Reference: [[loot.md#Problems with Always-On Context]])
→ [[#A20]]

---

## Answers

### A1
**B) Reduce and Delegate**
The R&D Framework: Reduce unnecessary context, Delegate work to appropriate places.

### A2
**B) Three (plus a hidden fourth)**
Three main levels plus a fourth for bleeding-edge agentic engineering.

### A3
**B) Using dedicated reusable prompts to set up initial context**
Context priming uses custom slash commands to set up task-specific context.

### A4
**B) They grow bloated with irrelevant or contradictory info**
Memory files only grow and can contain contradictory information.

### A5
**B) They consume 10-12% of context window wastefully**
Default MCP configs waste context unless you're using every server.

### A6
**B) The range where your agent performs at maximum capability**
The sweet spot maximizes agent performance for the task at hand.

### A7
**B) You're not paying attention to context state**
Vibe coding means ignoring context management - only tackling low-hanging fruit.

### A8
**B) A token counter/tokenizer**
Token counters help you understand context consumption before loading.

### A9
**B) Reduce and Delegate**
These are the only two approaches in the R&D Framework.

### A10
**B) Dedicated reusable prompts (custom slash commands)**
Context priming uses task-specific commands instead of bloated memory files.

### A11
**True** - Focus is essential for agent performance.

### A12
**False** - The context window is precious, renewable, but limited.

### A13
**False** - Only load MCP servers when needed to save context.

### A14
**True** - There's an optimal context range for each task.

### A15
**False** - Always-on context is NOT dynamic or controllable.

### A16
**True** - What gets measured gets managed.

### A17
**agents** - "Context engineering is the name of the game for high value engineering in the age of agents."

### A18
**temporal** - "Your agent's context window is a precious, renewable, but limited temporal resource."

### A19
The R&D Framework has two components:
1. **Reduce** - Remove unnecessary context, avoid bloat, minimize what's loaded
2. **Delegate** - Move context to appropriate places (specialized agents, external systems)

Every context management technique fits into one or both of these categories. The goal is to hit the "context sweet spot" where your agent performs optimally.

### A20
Problems with always-on memory files:
- **Not dynamic** - Can't change based on task type
- **Not controllable** - Always loaded whether needed or not
- **Only grow** - Engineering work changes but files just accumulate
- **Become bloated** - Eventually full of irrelevant context
- **Contradictory info** - Worst case contains conflicting instructions

Solution: Use context priming with dedicated slash commands instead.

---

## Score Guide

| Score | Level |
|-------|-------|
| 18-20 | Mastery |
| 15-17 | Proficient |
| 12-14 | Developing |
| <12 | Review [[loot.md]] and [[transcript.txt]] |

---

[[loot.md]] | [[transcript.txt]] | [[../diagrams/core-four.excalidraw]]
