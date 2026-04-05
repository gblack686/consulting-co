# Combined Query Examples

Complete workflow examples showing how to combine Graphiti (knowledge graph) and pgvector (RAG) queries for comprehensive TAC learning.

## TAC Content Reference

### 11 Repositories
1. agent-experts
2. agentic-finance-review
3. agent-sandboxes
4. building-domain-specific-agents
5. claude-code-damage-control
6. claude-code-hooks-mastery
7. multi-agent-orchestration-the-o-agent
8. orchestrator-agent-with-adws
9. rd-framework-context-window-mastery
10. seven-levels-agentic-prompt-formats
11. building-specialized-agents

### 15 Lessons
- **Lessons 1-8**: Core Tactics
- **Lesson 9**: Elite Context Engineering
- **Lesson 10**: Agentic Prompt Engineering (7 Prompt Levels)
- **Lesson 11**: Building Specialized Agents
- **Lesson 12**: Multi-Agent Orchestration
- **Lesson 13**: Agent-Experts (ACT-LEARN-REUSE)
- **Lesson 14**: Orchestrator Agent with ADWs
- **Lesson 15**: Software Delivery ADW

### Key Frameworks
- Core Four (Context, Model, Prompt, Tools)
- PITER (Prompt, Input, Trigger, Environment, Review)
- R&D (Reduce & Delegate)
- ACT-LEARN-REUSE
- 12 Leverage Points
- 7 Prompt Levels / HOP

---

## Workflow 1: Learning a New TAC Concept

**Goal**: Understand "Tactic #3: Template Your Engineering"

### Step 1: Get Conceptual Overview (Graphiti)

```python
# Search for the tactic's relationships and context
mcp__graphiti__search_memory_facts(
    query="Tactic #3 Template Your Engineering problem class",
    group_ids=["ai-agent-kb"],
    max_facts=10
)
```

Expected insights:
- What problem classes this tactic addresses
- How it relates to other tactics
- Key principles and patterns

### Step 2: Find Concrete Examples (pgvector)

```bash
# Find commands that implement this tactic
python .claude/scripts/kb_search.py --folder commands "template reusable pattern"

# Find skills that demonstrate templates
python .claude/scripts/kb_search.py --folder skills "template generation"
```

### Step 3: Read Source Files

Based on search results, read the actual files:

```python
# Read a specific command file
Read("AI-Agent-KB/commands/plan.md")

# Read a skill implementation
Read("AI-Agent-KB/skills/meta-skill/SKILL.md")
```

### Step 4: Synthesize Learning

Combine conceptual understanding with concrete examples to:
- Understand WHEN to apply the tactic
- Know HOW to implement it
- See EXAMPLES of it in practice

---

## Workflow 2: Building a New ADW

**Goal**: Create an ADW for "automated API documentation generation"

### Step 1: Find Similar ADWs (Graphiti)

```python
# Search for existing ADW patterns
mcp__graphiti__search_nodes(
    query="ADW documentation generation workflow",
    group_ids=["ai-agent-kb"],
    entity_types=["ADW", "Workflow"],
    max_nodes=5
)

# Get ADW structure patterns
mcp__graphiti__search_memory_facts(
    query="ADW workflow steps components",
    max_facts=10
)
```

### Step 2: Find Building Block Components (pgvector)

```bash
# Find commands that could be ADW steps
python .claude/scripts/kb_search.py --folder commands "documentation generate API"

# Find agents that could be delegated to
python .claude/scripts/kb_search.py --folder agents "documentation code analysis"

# Find related skills
python .claude/scripts/kb_search.py --folder skills "documentation markdown"
```

### Step 3: Understand ADW Structure

```python
# Get specific ADW examples
mcp__graphiti__search_memory_facts(
    query="plan_build_review ADW structure steps",
    max_facts=15
)
```

### Step 4: Create ADW Following Patterns

Based on findings, create ADW with:
- Identified steps from similar workflows
- Components discovered via vector search
- Structure patterns from knowledge graph

---

## Workflow 3: Choosing the Right Agent Pattern

**Goal**: Decide between Pong, Echo, and Calculator patterns

### Step 1: Get Pattern Definitions (Graphiti)

```python
# Search for pattern definitions
mcp__graphiti__search_memory_facts(
    query="Pong Echo Calculator agent pattern when to use",
    group_ids=["ai-agent-kb"],
    max_facts=15
)
```

### Step 2: Find Pattern Implementations (pgvector)

```bash
# Find agents using each pattern
python .claude/scripts/kb_search.py --folder agents --verbose "simple request response"
python .claude/scripts/kb_search.py --folder agents --verbose "custom tools"
python .claude/scripts/kb_search.py --folder agents --verbose "tool heavy focused"
```

### Step 3: Compare Patterns

Create a decision matrix based on:
- Complexity of task
- Need for custom tools
- Level of autonomy required
- Type of output expected

---

## Workflow 4: Finding All Components for a Feature

**Goal**: Implement "intelligent code review" capability

### Step 1: Broad Concept Search (Graphiti)

```python
# Find related concepts
mcp__graphiti__search_nodes(
    query="code review feedback quality",
    max_nodes=10
)

# Find methodology
mcp__graphiti__search_memory_facts(
    query="code review best practices patterns",
    max_facts=10
)
```

### Step 2: Component Discovery (pgvector)

```bash
# Find review commands
python .claude/scripts/kb_search.py --folder commands "review code feedback"

# Find analysis agents
python .claude/scripts/kb_search.py --folder agents "analyze code quality"

# Find related skills
python .claude/scripts/kb_search.py --folder skills "review validation"

# Find output formats
python .claude/scripts/kb_search.py --folder output-styles "review report"
```

### Step 3: Assemble Component List

Compile discovered components:

| Category | Component | Purpose |
|----------|-----------|---------|
| Command | `review` | Trigger review workflow |
| Agent | `scout-report-suggest` | Analyze code issues |
| Skill | `fix` | Apply recommendations |
| Output | `review-report` | Format findings |

---

## Workflow 5: Understanding PITER Framework

**Goal**: Apply PITER framework to evaluate automation potential

### Step 1: Get Framework Definition (Graphiti)

```python
# Get PITER components
mcp__graphiti__search_memory_facts(
    query="PITER framework Prompt Input Trigger Environment Review",
    group_ids=["ai-agent-kb"],
    max_facts=15
)
```

### Step 2: Find PITER Examples (pgvector)

```bash
# Find commands with good PITER characteristics
python .claude/scripts/kb_search.py "automated trigger validation"

# Find hooks (natural PITER implementations)
python .claude/scripts/kb_search.py --folder commands --type hook "event automation"
```

### Step 3: Evaluate Your Use Case

For each PITER dimension:

| Dimension | Question | Score (1-5) |
|-----------|----------|-------------|
| **P**rompt | Is input well-defined? | |
| **I**nput | Can data be structured? | |
| **T**rigger | Can this be automated? | |
| **E**nvironment | Is execution isolated? | |
| **R**eview | Is validation possible? | |

---

## Workflow 6: ACT-LEARN-REUSE Cycle (Lesson 13)

**Goal**: Complete a full learning cycle for a new capability

### ACT Phase: Execute with Current Knowledge

```python
# Find relevant patterns
mcp__graphiti__search_memory_facts(
    query="similar implementation patterns",
    max_facts=5
)
```

```bash
# Find applicable commands
python .claude/scripts/kb_search.py --folder commands "implementation build"
```

### LEARN Phase: Extract Insights

After execution, identify:
- What worked well
- What could be improved
- New patterns discovered

```python
# Store learnings in knowledge graph
mcp__graphiti__add_memory(
    name="Learning: [Capability Name]",
    episode_body="Discovered that...",
    source="text",
    group_id="claude-code-learnings"
)
```

### REUSE Phase: Create Reusable Asset

Based on learnings:

```bash
# Find template patterns
python .claude/scripts/kb_search.py --folder commands "template"

# Find skill creation patterns
python .claude/scripts/kb_search.py --folder skills "meta-skill"
```

Create:
- New command template
- Updated skill module
- ADW for future use

---

## Workflow 7: Learning Elite Context Engineering (Lesson 9)

**Goal**: Understand R&D framework for context optimization

### Step 1: Get Framework Concepts (Graphiti)

```python
# Search for R&D framework
mcp__graphiti__search_memory_facts(
    query="R&D framework Reduce Delegate context window optimization",
    group_ids=["ai-agent-kb"],
    max_facts=10
)

# Search for context engineering patterns
mcp__graphiti__search_memory_facts(
    query="elite context engineering static dynamic retrieval",
    max_facts=10
)
```

### Step 2: Find Implementation Examples (pgvector)

```bash
# Find agents that demonstrate good context management
python .claude/scripts/kb_search.py --folder agents "context minimal focused"

# Find commands with good context engineering
python .claude/scripts/kb_search.py --folder commands "context priming"
```

### Step 3: Apply to Your Use Case

Use the R&D questions:
- **Reduce**: What context can I exclude?
- **Delegate**: What can agents retrieve on-demand?

---

## Workflow 8: Understanding 7 Prompt Levels (Lesson 10)

**Goal**: Master Higher Order Prompts (HOP)

### Step 1: Get Level Definitions (Graphiti)

```python
# Search for prompt level hierarchy
mcp__graphiti__search_memory_facts(
    query="7 prompt levels HOP Higher Order Prompt progression",
    group_ids=["ai-agent-kb"],
    max_facts=15
)
```

### Step 2: Find Examples at Each Level (pgvector)

```bash
# Level 1-2: Simple commands
python .claude/scripts/kb_search.py --folder commands "simple direct instruction"

# Level 3-4: Structured prompts
python .claude/scripts/kb_search.py --folder commands "structured template"

# Level 5-7: Higher Order Prompts
python .claude/scripts/kb_search.py --folder skills "HOP wrapper meta"
```

### Step 3: Map Your Prompts

Identify which level your current prompts operate at and how to elevate them.

---

## Workflow 9: Multi-Agent Orchestration (Lesson 12)

**Goal**: Design a fleet of specialized agents

### Step 1: Get Orchestration Patterns (Graphiti)

```python
# Search for O-Agent patterns
mcp__graphiti__search_memory_facts(
    query="multi-agent orchestration O-Agent fleet management coordinator",
    group_ids=["ai-agent-kb"],
    max_facts=10
)

# Search for delegation patterns
mcp__graphiti__search_memory_facts(
    query="agent delegation task routing specialist agents",
    max_facts=10
)
```

### Step 2: Find Agent Building Blocks (pgvector)

```bash
# Find existing specialized agents
python .claude/scripts/kb_search.py --folder agents --verbose "specialist"

# Find orchestration-related commands
python .claude/scripts/kb_search.py --folder commands "orchestrate parallel delegate"

# Find orchestration skills
python .claude/scripts/kb_search.py --folder skills "orchestrator fleet"
```

### Step 3: Design Your Fleet

Map out:
- Coordinator agent (O-Agent)
- Specialist agents (by domain)
- Communication patterns

---

## Workflow 10: Exploring a TAC Repository

**Goal**: Deep-dive into a specific TAC repo (e.g., claude-code-hooks-mastery)

### Step 1: Get Repository Overview (Graphiti)

```python
# Search for repository content
mcp__graphiti__search_memory_facts(
    query="claude-code-hooks-mastery PreToolUse PostToolUse Notification Stop",
    group_ids=["ai-agent-kb"],
    max_facts=15
)

# Get related concepts
mcp__graphiti__search_nodes(
    query="hooks lifecycle events automation",
    entity_types=["Concept", "Pattern"]
)
```

### Step 2: Find Related Components (pgvector)

```bash
# Find hook implementations
python .claude/scripts/kb_search.py --type hook "validation automation"

# Find commands that use hooks
python .claude/scripts/kb_search.py --folder commands "hook trigger event"
```

### Step 3: Read Source Documentation

Based on results, read the actual repo files in `C:\Users\gblac\OneDrive\Desktop\tac\claude-code-hooks-mastery\`

---

## Workflow 11: Safety and Damage Control

**Goal**: Implement defense-in-depth patterns from claude-code-damage-control

### Step 1: Get Safety Concepts (Graphiti)

```python
# Search for damage control patterns
mcp__graphiti__search_memory_facts(
    query="damage control defense-in-depth safety validation rollback",
    group_ids=["ai-agent-kb"],
    max_facts=10
)

# Search for protection layers
mcp__graphiti__search_memory_facts(
    query="pre-execution validation dangerous operation blocking",
    max_facts=10
)
```

### Step 2: Find Safety Implementations (pgvector)

```bash
# Find validation commands
python .claude/scripts/kb_search.py --folder commands "validate safe dangerous"

# Find safety-related hooks
python .claude/scripts/kb_search.py --type hook "block validate permission"

# Find review agents
python .claude/scripts/kb_search.py --folder agents "review validate safety"
```

---

## Workflow 12: Domain-Specific Agent Design

**Goal**: Build a specialized domain agent (from building-domain-specific-agents)

### Step 1: Get Domain Agent Patterns (Graphiti)

```python
# Search for domain specialization patterns
mcp__graphiti__search_memory_facts(
    query="domain-specific agent knowledge injection specialized tools",
    group_ids=["ai-agent-kb"],
    max_facts=10
)
```

### Step 2: Find Domain Expert Examples (pgvector)

```bash
# Find existing expert agents
python .claude/scripts/kb_search.py --folder agents "expert domain specialist"

# Find expertise skills
python .claude/scripts/kb_search.py --folder skills "expertise mental model"
```

### Step 3: Design Domain Injection

Plan:
- Domain knowledge files
- Domain-specific tools
- Domain-appropriate validation

---

## Query Cheat Sheet

### Quick Concept Lookup

```python
mcp__graphiti__search_memory_facts(query="[concept]", max_facts=5)
```

### Quick Component Search

```bash
python .claude/scripts/kb_search.py --vector-only "[keywords]"
```

### Broad Discovery

```python
# Graphiti: relationships
mcp__graphiti__search_memory_facts(query="[topic]", max_facts=20)
```

```bash
# Vector: all component types
python .claude/scripts/kb_search.py --verbose "[topic]"
```

### Focused Component Type

```bash
python .claude/scripts/kb_search.py --folder [folder] --type [type] "[query]"
```

---

## Pro Tips

### 1. Start Broad, Then Narrow

```bash
# First: broad search
python .claude/scripts/kb_search.py "authentication"

# Then: narrow by type
python .claude/scripts/kb_search.py --folder commands "authentication"
```

### 2. Use Both Systems

- Graphiti for **WHY** and **WHEN**
- pgvector for **WHAT** and **HOW**

### 3. Follow the Trail

When Graphiti returns a concept, use pgvector to find implementations:

```python
# Graphiti returns: "Template Your Engineering enables ADW creation"
```

```bash
# Follow up with pgvector
python .claude/scripts/kb_search.py --folder commands "ADW creation"
```

### 4. JSON for Automation

```bash
# Get structured results for scripting
python .claude/scripts/kb_search.py --json "[query]" > results.json
```

### 5. Lower Threshold for Exploration

```bash
# When exploring, accept more results
python .claude/scripts/kb_search.py --threshold 0.4 --top-k 20 "[broad query]"
```
