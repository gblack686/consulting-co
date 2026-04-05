---
title: "How to Build Claude Skills Better than 99% of People"
creator: Ben van Sprundel
channel: Ben AI
video_url: https://www.youtube.com/watch?v=X3uum6W2xEI
video_id: X3uum6W2xEI
date_accessed: 2026-03-26
upload_date: 2026-02-24
duration: "18:36"
views: 171312
likes: 4194
type: deep-dive-analysis
tags:
  - claude-skills
  - skill-engineering
  - claude-cowork
  - claude-code
  - plugins
  - progressive-disclosure
  - context-engineering
  - ai-automation
  - monetization
  - saas-replacement
---

# How to Build Claude Skills Better than 99% of People

## Executive Summary

Ben van Sprundel (Ben AI) presents a comprehensive framework for building high-quality Claude Skills, positioning skill engineering as the defining competency of 2026. He argues that skills occupy a critical middle ground between isolated AI tools (custom GPTs, project-scoped prompts) that lack persistence and self-improvement, and rigid deterministic automation platforms (n8n, Make) that cannot handle nuanced, judgment-dependent workflows. Skills combine the flexibility of natural language instructions with the structure of SOPs, reference files, scripts, and MCP connectors -- all accessible through a single agent interface.

The video covers the full lifecycle: why skills matter, what they are structurally, how they differ from plugins, the three types of skills (first-party Anthropic, third-party marketplace, custom-built), and a step-by-step prompt framework for building production-quality skills. Ben emphasizes that skill engineering is analogous to UX design -- the craft lies in balancing completeness with clarity, handling edge cases, and iterating based on output quality. He demonstrates a live build of an infographic-generation skill, showing how it evolves through multiple iterations with added rules, QA steps, and example outputs.

Most notably for consulting practitioners, Ben frames skills as a new monetizable software layer. Because skills are sharable, versionable, and deployable (via zip, GitHub, or marketplace), they function like micro-SaaS products that can be sold or bundled into plugins for entire departments. He predicts skill marketplaces will become significant, with businesses and individuals selling domain-specific skill packages. This aligns directly with the consulting model of packaging expertise into repeatable, scalable deliverables.

## Key Topics

### Why Skills Matter (00:22)

- AI agents (Claude Code, Cowork, Codex) are increasingly powerful but still need **guardrails, context, and SOPs** specific to each business
- Previous approaches (custom GPTs, project prompts) are **isolated, do not self-improve, and cannot handle deep context**
- Deterministic automation platforms (n8n, Make) are great for clear-cut workflows but fail on judgment-dependent tasks
- Skills sit in the middle: natural-language instructions that an agent can execute, self-improve, and share across a team

### What Skills Actually Are (01:53)

- **Folders** containing instructions, scripts, and resources that help an agent perform a specific task accurately
- Core component: **SKILL.md** file -- the instruction set (like a system prompt + SOP combined)
- Beyond the core SKILL.md, skills can include:
  - **Reference/knowledge files** (text): example outputs, style guides, ICP definitions, background context, personality/voice docs
  - **MCP configuration files**: defines which tools the agent can use and how to navigate them efficiently
  - **Asset files** (non-text): images, presentations, videos, binary examples (e.g., layout templates)
  - **Script files** (Python/JS): functions for API calls, code execution, data processing

### How Skills Work -- Progressive Disclosure (05:20)

- Skills use **progressive disclosure** to avoid overloading the agent context window
- On registration: only the skill metadata, name, and description are stored in memory
- The description tells the agent **when to trigger** the skill
- On trigger: the full SKILL.md and referenced files are **loaded into the context window**
- This means you can have **hundreds of skills** registered without context pollution

### Skills vs. Plugins (06:20)

- **Plugins** are packaged, bundled sets of commands, agents, and connectors
- Three differentiators:
  1. Plugins add an **orchestration layer** on top of skills -- commands serve as triggers that sequence multiple tasks
  2. Plugins are **easily shared and divided by department** (Sales plugin, Marketing plugin, each with its own connectors)
  3. Plugins are **versionable** -- they behave like SaaS, with characteristics you can update over time
- Implication: plugins are the deployment and distribution unit; skills are the atomic unit of capability

### The Three Types of Skills (08:00)

1. **First-party (Anthropic built-in)**: Pre-built skills from Anthropic, customizable by editing
2. **Third-party (Marketplace)**: Skills from marketplaces (Anthropic own, MP Smithy, etc.) -- potentially monetizable
3. **Custom-built**: Your own skills, built from your domain expertise -- the highest-value category
### Building Quality Skills -- The Framework (09:44)

#### Planning and Context Engineering (10:26)

- **Start with the ideal outcome** and work backward -- what does the perfect output look like?
- **Biggest-impact-first**: identify which steps in the process have the most impact on output quality
- Gather all **reference information** the skill needs: style guides, examples, ICP docs, voice/personality definitions
- Consider **reuse**: skills for related tasks (e.g., LinkedIn strategy, YouTube writing, newsletter ideation) can share reference docs
- Prepare tool/MCP definitions for any external services the skill needs

#### Skill Building Prompt Framework (10:26)

The recommended SKILL.md structure:

1. **Trigger definition**: Clear description of when/how the skill activates (e.g., triggered anytime user mentions generating an infographic)
2. **Goal/objective**: Short statement of the skill purpose (deeper detail comes in steps)
3. **Tool/connector declarations**: Which MCPs, APIs, or scripts the skill uses
4. **Step-by-step execution flow**: A numbered table or list describing each step. Key design decisions at each step:
   - Is this step in-the-loop (human approval) or autonomous?
   - Does the step need dynamic input? (QA checkboxes, open fields, selects)
   - What is the expected output format?
5. **Variations/options**: Instead of one-off outputs, offer the user choices (e.g., 3 layout variations to pick from)
6. **Rules section**: Guardrails for edge cases, things the skill commonly gets wrong
   - Tip: **Do not over-instruct** -- only add rules that are obligatory. Over-specification causes the agent to over-index on rules and lose focus
   - Rules should be **continuously updated** based on observed failures
7. **Self-improvement/learning section**: Instructions for the skill to automatically improve itself
   - After user approves a final output, the skill saves it as training data
   - Builds a library of approved examples that inform future executions
8. **Example outputs**: Concrete examples of what good looks like -- the skill gets trained on these

### Live Demo: Infographic Generator (15:01)

- Built an infographic skill using the framework above
- Initial version produced decent output; iterated **five times** with additional rules and examples
- Added: brand guidelines checkbox, variation generation, QA approval step
- Key observation: **the first version is never the final version** -- plan for iteration

### Improvements and Deployment (16:22)

- **Updating**: When the skill does not perform correctly, modify the SKILL.md. Do not pollute it -- focus on core instructions and only add rules for actual failures
- **Sharing**: Easiest method is zip and share. Also deployable via GitHub
- **Plugins**: Bundle multiple skills into a plugin for department-level deployment
- **Marketplace**: Upload to Anthropic marketplace or community platforms

## Key Insights and Takeaways

### 1. Skills as the New Software Layer

The strongest thesis in this video: skills are becoming a **monetizable software layer** that replaces traditional SaaS for many use cases. They are cheaper to build, instantly customizable, and distribute through marketplaces. This is the SaaS-is-dead argument made concrete.

### 2. Progressive Disclosure is the Scaling Mechanism

The reason you can have hundreds of skills without performance degradation is progressive disclosure -- only metadata is in memory until triggered. This is the same pattern used in the consulting-co repo skill architecture with SKILL.md files.

### 3. Skill Engineering is UX Design

The analogy to UX is powerful: you are designing an experience where the agent produces the right output reliably. This means balancing feature completeness against cognitive load, handling edge cases with rules (not over-specification), and iterating based on observed output quality.

### 4. Self-Improving Skills

The self-learning pattern -- where approved outputs are saved as examples that inform future runs -- creates a flywheel. Each execution potentially improves the skill. This is distinct from simple prompt iteration; it is building a training dataset within the skill itself.

### 5. Do Not Over-Instruct

A counterintuitive but critical insight: adding too many rules causes the agent to over-focus on constraints rather than the core task. Only add rules for observed failures, not preemptive guardrails.

### 6. Plugins as the Distribution Unit

Individual skills are the atomic unit; plugins are the packaging/distribution unit. For a consulting business, this means delivering client value as a plugin (bundle of skills + connectors + commands) rather than individual skill files.
## Tools and Technologies Mentioned

| Tool | Category | Purpose |
|------|----------|---------|
| Claude Code | AI Agent | Primary skill execution environment |
| Claude Cowork | AI Agent | Collaborative skill execution |
| Codex (OpenAI) | AI Agent | Alternative skill platform |
| N8N | Automation | Workflow automation (deterministic) |
| Make.com | Automation | Workflow automation (deterministic) |
| APIFY | Scraping | Web data extraction |
| Skyvern | Browser Automation | Web task automation |
| Relevance AI | AI Platform | Agent building |
| ElevenLabs | Voice AI | Audio generation |
| Sendspark | Video | Personalized video |
| Agentive | AI Platform | Agent deployment |
| Dumpling AI | AI Tools | AI utilities |
| Nano Banana | Image Gen | Infographic/visual generation |
| MP Smithy | Marketplace | Skill marketplace |
| Prompt Cowboy | Prompting | Free prompting tool |
| GitHub | Distribution | Skill/plugin deployment |

## Application to an Advanced Practitioner (20+ Skills, AI Consulting Business)

### What You Already Do That Aligns

- Your .claude/skills/ directory with 20+ skills already follows the folder-based architecture Ben describes
- Progressive disclosure is already how Claude Code loads skills -- SKILL.md metadata triggers full context load
- You already bundle skills with templates, scripts, and reference files (e.g., consulting-intake has templates/, references/, client-sessions/)

### Where to Level Up

1. **Self-Improvement Loops**: The pattern of having skills save approved outputs as future training data is worth systematizing. Your skills could append successful outputs to a references/approved-examples/ directory that gets loaded on subsequent runs. This creates compounding quality over time without manual SKILL.md edits.

2. **Plugin Packaging for Clients**: Instead of delivering individual skills to consulting clients, package related skills into versioned plugins. The consulting-intake skill already generates full workspaces -- extend this to produce a plugin manifest that bundles the workspace skills into a single deployable unit. This becomes a deliverable the client can install, version, and share across their team.

3. **Marketplace Monetization**: With 20+ battle-tested skills, you have inventory ready for marketplace distribution. The consulting-intake pipeline could be adapted to produce marketplace-ready skill packages -- complete with metadata, descriptions, and example outputs -- as a secondary output alongside client deliverables.

4. **Rule Hygiene**: The warning about over-instruction is relevant. Audit existing skills for rule bloat. Rules added preemptively (before observing a failure) are candidates for removal. Keep SKILL.md files focused on the execution flow and only add rules for documented failure modes.

5. **Variation Patterns**: The approach of generating multiple output variations (e.g., 3 infographic layouts) before final selection is a quality pattern that could be applied to consulting deliverables. Skills that produce client-facing artifacts (reports, architectures, proposals) could offer 2-3 variations for client selection.

6. **Department-Level Plugins for Clients**: For clients like Fish Group or trading clients, build department-specific plugins that bundle skills + MCP connectors + commands. This positions the consulting deliverable as a product, not a one-off service, and justifies recurring revenue for plugin updates and new skill additions.

### Strategic Takeaway

Ben validates the direction you are already heading: skills are the atomic unit of AI consulting value, plugins are the distribution unit, and marketplaces are the monetization channel. The gap to close is formalizing the self-improvement loop, adopting plugin-level packaging for client delivery, and preparing skill inventory for marketplace listing. The consulting-intake pipeline is already 80% of the way to producing marketplace-ready output -- the remaining 20% is metadata, versioning, and approved-example libraries.
