---
title: "TAC Lesson 11 Quiz - Building Specialized Agents"
lesson: 11
questions: 20
difficulty: Advanced
tactic: "Custom Agents"
diagram: "../diagrams/agent-evolution.excalidraw"
---

# Lesson 11 Quiz: Building Domain-Specific Agents

> **Focus:** Custom Agent Development with Claude SDK
> **Diagram Reference:** [[../diagrams/agent-evolution.excalidraw]]
> **Loot Reference:** [[loot.md]]

---

## Section A: Multiple Choice (10 questions)

### Q1. What is the Agent Evolution Path?
- A) Slow → Fast → Faster
- B) Better agents → More agents → Custom agents
- C) Simple → Complex → Simple
- D) Manual → Semi → Auto

→ [[#A1]]

---

### Q2. What is "The Mismatch Problem"?
- A) Wrong programming language
- B) Out-of-the-box agents built for everyone, not your codebase
- C) Incorrect model selection
- D) Bad documentation

→ [[#A2]]

---

### Q3. What is the most important element of a custom agent?
- A) The tools
- B) The model
- C) The system prompt
- D) The context window

→ [[#A3]]

---

### Q4. What is the Pong Agent Pattern?
- A) A game-playing agent
- B) Simplest custom agent with total system prompt control
- C) A testing agent
- D) A documentation agent

→ [[#A4]]

---

### Q5. What happens when you override the system prompt?
- A) Nothing changes
- B) It's NOT Claude Code anymore - you've created a new product
- C) It becomes faster
- D) It uses less context

→ [[#A5]]

---

### Q6. What does the @tool decorator do?
- A) Speeds up execution
- B) Builds custom tools for agents
- C) Reduces memory usage
- D) Improves security

→ [[#A6]]

---

### Q7. How many default tools does Claude Code include?
- A) 5+
- B) 10+
- C) 15+
- D) 20+

→ [[#A7]]

---

### Q8. What is the Echo Agent Pattern for?
- A) Repeating messages
- B) Adding custom tools to your agent
- C) Testing echoes
- D) Sound processing

→ [[#A8]]

---

### Q9. When should you use Claude Haiku?
- A) For complex reasoning
- B) For simple, fast tasks
- C) For all tasks
- D) Never

→ [[#A9]]

---

### Q10. What are the two system prompt strategies?
- A) Load and Save
- B) Append and Override
- C) Create and Delete
- D) Read and Write

→ [[#A10]]

---

## Section B: True or False (6 questions)

### Q11. Custom agents give full control over the Core Four.
→ [[#A11]]

---

### Q12. Default Claude Code tools don't consume context.
→ [[#A12]]

---

### Q13. Test custom agents in isolation before production.
→ [[#A13]]

---

### Q14. Version control is critical for agent configurations.
→ [[#A14]]

---

### Q15. When you override the system prompt, you're still using Claude Code.
→ [[#A15]]

---

### Q16. All the alpha is in generic problems that everyone can solve.
→ [[#A16]]

---

## Section C: Fill in the Blank (2 questions)

### Q17. "The system prompt is your most important element with __________ exceptions."
→ [[#A17]]

---

### Q18. "All the __________ in engineering is in hard, specific problems that most engineers and agents can't solve out of the box."
→ [[#A18]]

---

## Section D: Short Answer (2 questions)

### Q19. Explain the three agent patterns introduced in this lesson. (Reference: [[loot.md#Agent Patterns]])
→ [[#A19]]

---

### Q20. What is "The Mismatch Problem" and how do custom agents solve it? (Reference: [[loot.md#The Mismatch Problem]])
→ [[#A20]]

---

## Answers

### A1
**B) Better agents → More agents → Custom agents**
The natural progression of agentic engineering.

### A2
**B) Out-of-the-box agents built for everyone, not your codebase**
Generic agents don't know your specific codebase and domain.

### A3
**C) The system prompt**
The system prompt affects EVERY user prompt - zero exceptions.

### A4
**B) Simplest custom agent with total system prompt control**
The basic pattern demonstrating system prompt override.

### A5
**B) It's NOT Claude Code anymore - you've created a new product**
System prompt override creates an entirely new product.

### A6
**B) Builds custom tools for agents**
The @tool decorator creates SDK MCP servers in-memory.

### A7
**C) 15+**
15+ tools that consume context even if unused.

### A8
**B) Adding custom tools to your agent**
Echo pattern demonstrates the @tool decorator.

### A9
**B) For simple, fast tasks**
Match model to task complexity - Haiku for simple/fast.

### A10
**B) Append and Override**
Append extends Claude Code; Override creates new products.

### A11
**True** - Full control over Context, Model, Prompt, and Tools.

### A12
**False** - 15+ tools consume precious context even if unused.

### A13
**True** - Always test in isolation before production.

### A14
**True** - Version control all agent configurations.

### A15
**False** - When you override, it's NOT Claude Code anymore.

### A16
**False** - The alpha is in HARD, SPECIFIC problems others can't solve.

### A17
**zero** - "The system prompt is your most important element with zero exceptions."

### A18
**alpha** - "All the alpha in engineering is in hard, specific problems..."

### A19
The three agent patterns are:

1. **Pong Agent Pattern** - The simplest custom agent demonstrating total system prompt control. Override the system prompt completely to create a new product.

2. **Echo Agent Pattern** - Adds custom tools using the @tool decorator. Build SDK MCP servers in-memory for specialized capabilities.

3. **Calculator Agent Pattern** - More capable custom agent with focused functionality. Uses consistent codebase architecture for better agent navigation.

### A20
**The Mismatch Problem:** Out-of-the-box agents are built for everyone's codebase, not yours. This generic approach creates a mismatch that costs hundreds of hours and millions of tokens as your codebase grows.

**How custom agents solve it:**
- Pass domain-specific knowledge directly to agents
- Full control over the Core Four (Context, Model, Prompt, Tools)
- Template your engineering into the agent itself
- Strip unnecessary tools to save context
- Build for YOUR specific problems, not generic ones

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
