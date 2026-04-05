# Understanding Agent Skills in Claude/Cursor: A Complete Guide

## Introduction

For the past week, I've been working through agent skill issues. Now you have agent skills, sub agents, custom slash commands, output styles, plugins, hooks, memory files, and MCP servers.

What is this all for? I've been using Cloud Code since it was first available in February. Since its release, I've generated more code than in my previous 15 years as an engineer. This tool has changed engineering, but this once simple tool has gotten complex over the year, so let's simplify it.

Skills are simple, but they're so similar to MCP, sub agents, and custom slash commands, it's hard to know when to use a skill. There's a right way to think about skills, and there's a wrong way. I want to show you both to make it absolutely clear what this feature can do for your engineering.

**Skills are powerful, but you should not always build a skill.**

---

## The Wrong Way to Use Skills

Let's first look at the wrong way to use skills to solve an engineering problem. Here we have:
- A **skill** on the left
- A **sub agent** in the middle  
- A **custom slash command** on the right

If you're parallel agent coding, generating multiple solutions at the same time, you've likely created git work trees.

**Question:** Which one of these three ways is the right way to create or manage your git work trees?

---

## Feature Comparison Matrix

To answer this, we need to understand how these features really differ.

### Key Capabilities Comparison

| Capability | Skills | Sub Agents | Custom Slash Commands | MCP Servers |
|------------|--------|------------|---------------------|-------------|
| **Agent-Triggered** | ✅ Yes | ✅ Yes | ❌ Manual | ⚠️ Varies |
| **Context Efficiency** | ✅ High (Progressive Disclosure) | ✅ High | ✅ High | ❌ Low (Explodes context) |
| **Context Persistence** | ✅ Yes | ❌ No (Isolated) | ✅ Yes | ✅ Yes |
| **Modularity** | ✅ High (Dedicated directory) | ⚠️ Medium | ⚠️ Medium | ⚠️ Medium |
| **Composability** | ✅ Very High | ❌ Limited | ✅ Very High | ✅ High |
| **Shareability** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

### Progressive Disclosure (Skills)

Skills use three levels of progressive disclosure:
1. **Metadata level** - Basic information
2. **Instructions** - The skill.md file content
3. **Resources** - All resources pulled in when needed

---

## When to Use Each Feature

### Core Use Cases

| Feature | Primary Purpose | Best For |
|---------|----------------|----------|
| **Skills** | Automatic behavior | Reusable, agent-invoked workflows |
| **MCP Servers** | External integrations | Third-party services and APIs |
| **Sub Agents** | Isolated workflows | Parallel tasks, disposable context |
| **Custom Slash Commands** | Manual triggers | One-off tasks, explicit control |

### Real-World Examples

#### ✅ **Use a SKILL when:**
- Automatically extract text and data from PDFs
- Detect style guide violations
- Managing git work trees (multiple operations)
- Any repeatable workflow the agent should automatically handle

#### ✅ **Use an MCP SERVER when:**
- Connect to Jira
- Query your database
- Fetch real-time weather data from APIs
- Any external service integration

#### ✅ **Use a SUB AGENT when:**
- Run a comprehensive security audit
- Fix and debug failing tests at scale
- **Parallelize multiple workflows**
- Test multiple approaches simultaneously
- Any task where you're okay losing the context afterward

#### ✅ **Use a CUSTOM SLASH COMMAND when:**
- Generate git commit messages
- Create a UI component
- One-off, simple tasks
- When you need explicit control and visibility

**Rule of Thumb:** Whenever you see the word **"parallel"**, think sub agents immediately. Nothing else supports parallel calling.

---

## The Fundamental Truth: Prompts Are the Primitive

### The Core 4 of Agentic Coding

Every agent is built on these four pieces:

1. **Context**
2. **Model**
3. **Prompt**
4. **Tools**

**If you understand these, if you can build and manage these, you will win.**

### The Composition Hierarchy

```
┌─────────────────────────────────────┐
│         SKILLS (Top Level)          │
│  Can compose everything below       │
└─────────────────────────────────────┘
              ▲
              │
┌─────────────┴───────────────────────┐
│   CUSTOM SLASH COMMANDS             │
│   (The Primitive - Super Important) │
└─────────────────────────────────────┘
              ▲
              │
    ┌─────────┴──────────┐
    │                    │
┌───┴──────┐    ┌────────┴─────┐
│   MCP    │    │  SUB AGENTS  │
│ SERVERS  │    │              │
└──────────┘    └──────────────┘
```

### Why Prompts Matter Most

> **"The prompt is the fundamental unit of knowledge work and of programming. If you don't know how to build and manage prompts, you will lose."**

Everything is a prompt in the end. It's **tokens in, tokens out**.

**Always start with a custom slash command.** Don't jump to skills, sub agents, or MCP servers right away. Keep it simple. Build a prompt.

---

## The Right Way to Think About Skills

### From Prompt to Skill: When to Upgrade

**Use a prompt when:**
- You need to create a single git work tree
- One prompt solves the problem
- It's a one-off task

**Upgrade to a skill when:**
- You need to **manage** multiple git work trees
- One prompt is not enough
- You need a reusable solution
- Multiple related operations (create, list, remove, merge, etc.)

### What Skills Are Really For

Skills are for:
- ✅ Packaging reusable solutions
- ✅ Managing multiple related operations
- ✅ Agent-first automation
- ✅ Domain-specific expertise
- ✅ Repeat workflows with best practices

Skills are NOT for:
- ❌ One-off tasks (use slash commands)
- ❌ External integrations (use MCP)
- ❌ Parallel workflows (use sub agents)
- ❌ Replacing prompts

### Skills Should Compose Prompts

**Best Practice:** Your skills should use custom slash commands internally!

Example from the work tree manager skill:
```markdown
Instructions: Use the slash command tool to execute work tree operations.
```

The compositional chain:
1. **Base Level:** Custom Slash Command (the prompt)
2. **Middle Level:** Sub Agents (if parallelization needed)
3. **Top Level:** Skills (compose multiple prompts/operations)

---

## Feature Definitions

### Agent Skills
Package custom expertise that your agent autonomously applies to your reoccurring workflows.

**Key Features:**
- Agent-invoked
- Context protection (progressive disclosure)
- Dedicated file system structure
- Composable with other features
- Agentic approach

### MCP Servers
Connect your agents to external tools and data sources.

**Use for:**
- Third-party integrations
- Bundling multiple services
- Exposing capabilities to agents

### Sub Agents
Delegate isolatable specialized tasks with separate contexts that can work in parallel.

**Key Benefits:**
- Parallel execution
- Isolated context
- Scalable workflows
- Context disposal (not preserved)

### Custom Slash Commands
Reusable prompt shortcuts that you invoke manually.

**Why they're critical:**
- Closest to bare metal agent + LLM
- The fundamental primitive
- Must be mastered first
- Everything else builds on this

### Hooks
Deterministic automation that executes commands at specific lifecycle events.

**Purpose:**
- Add determinism vs. agent decisions
- Balance agentic and deterministic approaches
- Lifecycle event triggers

### Plugins
Package and distribute sets of work.

**Purpose:**
- Share and reuse Cloud Code extensions
- Distribution mechanism

### Output Styles
Control how agents present results.

**Examples:**
- Text-to-speech summaries
- Diff views
- Observable tools
- Custom formatting

---

## Pros and Cons of Agent Skills

### ✅ Pros

1. **Agent Invoked** - Lean into autonomy, delegate more work
2. **Context Protection** - Progressive disclosure, unlike MCP servers
3. **Dedicated File System Pattern** - Logical grouping, easy to manage
4. **Composable** - Can include MCP, sub agents, slash commands
5. **Agentic Approach** - Agent does the right thing automatically

### ❌ Cons

1. **Doesn't Go All the Way** 
   - Can't nest sub agents in skills directory
   - Can't nest prompts in a dedicated `/commands` directory
   - Missing `/agents` directory
   - Why not fully embrace the bundle approach?

2. **Reliability Questions**
   - Will agents use the right skills when chained?
   - Can you guarantee 5 skills will be called in order?
   - Compare to slash commands: guaranteed execution order

3. **Not Actually New**
   - Could do this with prompt engineering + custom slash commands + slash command tool
   - Skills = Opinionated prompt engineering + modularity
   - Thin wrapper over existing capabilities

**Overall Rating: 8/10**

---

## Practical Recommendations

### The Decision Tree

```
START: Do I need to solve a problem?
  │
  ├─ Is it a one-off task?
  │    └─ YES → Use CUSTOM SLASH COMMAND
  │
  ├─ Is it an external service?
  │    └─ YES → Use MCP SERVER
  │
  ├─ Do I need parallelization?
  │    └─ YES → Use SUB AGENT
  │
  └─ Is it a repeatable workflow with multiple operations?
       └─ YES → Use SKILL (that composes slash commands)
```

### Best Practices

1. **Always start with a custom slash command**
2. **Master prompts first** - They're the foundation
3. **Use skills to compose multiple related prompts**
4. **Don't convert all slash commands to skills** - That's a mistake
5. **Keep slash commands as your primitive**
6. **Use sub agents when you need parallelization**
7. **Reserve MCP for external integrations**

### The Composition Strategy

```
Skill: Work Tree Manager
  ├─ /create-tree (slash command)
  ├─ /remove-tree (slash command)  
  ├─ /list-trees (slash command)
  ├─ /merge-tree (slash command)
  └─ Agent orchestrates based on user request
```

---

## Key Takeaways

1. **The prompt is the fundamental unit** - Master it first
2. **Skills are not replacements** - They're compositional units
3. **Each feature has distinct purposes** - Use them appropriately
4. **Slash commands are the primitive** - Don't abandon them
5. **Compose, don't replace** - Skills should use slash commands internally
6. **Parallel = Sub Agents** - Clear distinction
7. **External = MCP** - Clear distinction
8. **Automatic + Repeatable = Skills** - Clear distinction

---

## Example: Git Work Tree Manager Skill

### Operations Included
- Create work tree
- Remove work tree
- List work trees
- Merge work tree
- Stop work tree
- Start work tree

### Usage
```
manage git work trees
remove red tree
create purple tree with offset 4
list our trees
```

The agent automatically:
1. Identifies the skill to use
2. Calls appropriate slash commands
3. Executes in proper order
4. Summarizes results

---

## Final Thoughts

Use whatever works for you. Don't let these features stop you from shipping work.

**Strong bias towards slash commands** - They're the primitive. When you're thinking about composing many slash commands, sub agents, or MCPs, think about putting them in a skill.

**Your skills should have a collection of slash commands** - This is the right approach.

Skills are powerful and a dedicated way across the platform to enable engineers to create repeatable agent-first solutions. It's domain-specific expertise in an agent-first way.

**Rating: 8/10** - Solid feature, but doesn't replace existing capabilities. It's a higher compositional level for grouping features to solve specific problems in a repeatable way.

---

## Resources

- Meta Skill: Use a skill to build other skills
- Video Processor Skill: Process and manage video files, create transcriptions
- Work Tree Manager Skill: Complete git work tree management

**Remember:** Build the thing that builds the thing. This is the power of agentic abstractions.

---

*Stay focused and keep building.*

