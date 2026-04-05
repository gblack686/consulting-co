---
title: "Claude Code Skills Changed Everything (And Nobody Noticed)"
creator: Leon van Zyl
channel: Leon van Zyl
channel_url: https://www.youtube.com/channel/UCtevzRsHEKhs-RK8pAqwSyQ
video_url: https://www.youtube.com/watch?v=epZy_NajGnA
video_id: epZy_NajGnA
upload_date: 2026-03-24
date_accessed: 2026-03-26
duration: "20:38"
type: deep-dive-analysis
tags:
  - claude-code
  - agent-skills
  - skill-creator
  - subagents
  - context-forking
  - dynamic-injection
  - evals
  - agentic-coding
  - skills-marketplace
---

# Claude Code Skills Changed Everything (And Nobody Noticed)

## Executive Summary

Leon van Zyl walks through the full current state of Claude Code agent skills system, covering every major feature added since the initial release. The video is structured as a progressive tutorial: starting from installation (via the plugin command or skills.sh marketplace), moving through manual skill creation and the automated Skill Creator, then into the three advanced features that represent genuine architectural upgrades -- subagents with background mode, context forking, and dynamic context injection via pre-processing commands.

The most operationally significant content is in the second half. Context forking allows a skill to spin off into its own dedicated session, keeping the parent conversation context window clean and returning only a summary. Dynamic injection lets a skill run shell commands before the model even sees the prompt, populating placeholders with live project data (directory tree, package.json contents, recent git commits) at zero token cost. Both of these directly address the two biggest practical problems with long-running agentic workflows: context window pollution and wasted tokens on project discovery.

The video closes with the eval system, which creates blind A/B comparisons between a skill-augmented response and the base model response. This is framed as future-proofing: as models improve (Leon references a hypothetical Opus 5), evals let you determine whether a custom skill still provides uplift or if the base model has caught up. The eval runner uses worktrees for parallel isolated test execution.

## Key Topics and Concepts

1. **Skills installation paths** -- plugin command (Anthropic official marketplace) and skills.sh (community/third-party marketplace)
2. **Skill file structure** -- .claude/skills/{name}/SKILL.md with YAML frontmatter (name, description, trigger conditions) and prompt body
3. **Skill Creator meta-skill** -- automates skill scaffolding, generates documentation, examples, and test harnesses
4. **Two skill types** -- capability uplift (adding abilities the model lacks) vs. encoded preferences (enforcing style/workflow conventions)
5. **Subagents with background mode** -- background: true flag lets a skill fork into a background agent, freeing the main session
6. **Context forking** -- skill runs in its own session with a dedicated context window; only a summary is passed back
7. **Dynamic context injection** -- pre-processing shell commands populate placeholders before the prompt reaches the model
8. **Evaluations and blind A/B comparisons** -- benchmark skill-augmented output against base model output using worktrees

## Detailed Breakdown

### 1. Installing Skills (00:27 - 02:55)

Two installation methods:

- **Plugin command**: Search available plugins from within Claude Code. Requires the Anthropic official marketplace (claude-plugins-official GitHub repo) to be registered. If missing, add the repo URL as a marketplace source.
- **skills.sh**: A community marketplace website. Browse categories, select skills (e.g., from the Anthropic collection), use spacebar to select/deselect, then install. Downloads skill folders into the .claude/ directory structure.

### 2. Manual Skill Creation (02:55 - 04:04)

A skill is a markdown file at .claude/skills/{skill-name}/SKILL.md with YAML frontmatter containing name, description, and trigger fields, followed by the prompt instructions for the model. The frontmatter trigger field tells Claude when to automatically invoke the skill. The body contains the actual instructions the model follows.

### 3. Skill Creator and Skill Types (04:04 - 06:46)

The **Skill Creator** is itself a skill that automates building new skills. It generates documentation, examples, and test harnesses. Two categories of skills:

- **Capability uplift**: Gives the model abilities it does not have natively (e.g., image generation via external APIs, specialized code patterns). Example: a nano banana image generation skill for web design mockups.
- **Encoded preferences**: Defines style rules, workflow sequences, or design system conventions the model should follow. Example: a skill that enforces a specific frontend design system to prevent generic/sloppy AI-generated UI.

### 4. Invoking Skills and Commands Merge (07:43 - 08:28)

Custom slash commands and skills have been merged -- there is no longer a separate commands system. Skills are invoked either by slash command or automatically when the trigger condition matches. The model is generally intelligent enough to recognize when a skill applies based on the user request.

### 5. Subagents with Background Mode (08:28 - 10:30)

Configuration in the skill frontmatter:

- background: true -- the skill runs as a subagent in a separate background process
- The main session remains free for other work
- Useful for long-running tasks (large code reviews, multi-file refactors, test suites)

Leon demonstrates a code review skill that processes PRs, evaluates each change for safety, and produces merge-ready output. He notes this kind of review can take 20+ minutes -- background mode prevents it from blocking the developer.

### 6. Context Forking (10:30 - 12:46)

The most architecturally important feature. When a skill uses context forking:

- It spins off into its **own dedicated session** with a fresh context window
- The parent session is not polluted with the skill intermediate work (file reads, reference lookups, etc.)
- Only a **summary of the final result** is passed back to the parent
- Configured via a fork: true property in the skill definition

This directly solves the problem of skills that need to load large reference files, documentation, or codebases. Without forking, all that context would consume the parent session window and degrade subsequent interactions.

### 7. Dynamic Context Injection (13:55 - 17:54)

Pre-processing commands run **before** the model sees the prompt, populating placeholder values:

- Uses shell command syntax in the skill definition
- Examples shown:
  - pwd -- inject current working directory
  - tree -- inject project directory structure
  - cat package.json -- inject dependency manifest
  - git log --oneline -10 -- inject recent commit history
- These run at effectively zero token cost for discovery -- the model does not need to spend tokens figuring out project structure

Leon emphasizes this eliminates the common pattern where Claude burns tokens running ls, cat, find commands to orient itself in a new project. The pre-processing step front-loads that context for free.

### 8. Evaluations and Blind A/B Comparisons (17:54 - 20:29)

The eval system:

- Creates an evals/ subfolder in the skill directory
- Uses git **worktrees** for isolated parallel test execution
- Runs the skill-augmented model and the base model on the same task
- Presents results as a blind comparison with metrics
- Opens a viewer/dashboard showing benchmark results, assertions, and standard behavior metrics

Purpose: continuously validate that custom skills still provide value as base models improve. If a future model (e.g., Opus 5) can natively perform a task a skill was built for, the eval will show no uplift, signaling the skill can be retired.

## Key Insights and Takeaways

1. **Context forking is the highest-value feature for complex workflows.** Any skill that reads reference files, documentation, or large codebases should use forking to avoid polluting the parent session.

2. **Dynamic injection replaces the orientation tax.** Every Claude Code session starts with the model spending tokens to understand the project. Pre-processing commands eliminate this cost entirely for known project structures.

3. **Skills are now the unified extension mechanism.** The merge of custom commands into skills simplifies the mental model -- everything is a skill with a SKILL.md file.

4. **Background subagents enable async workflows.** Long-running tasks (reviews, test suites, multi-file generation) no longer block the developer primary session.

5. **Evals future-proof your skill investment.** As models improve, evals prevent accumulating stale skills that add complexity without uplift.

6. **Capability uplift vs. encoded preferences is a useful taxonomy.** It clarifies whether a skill adds a new ability or enforces existing conventions -- different design approaches for each.

## Tools and Technologies Mentioned

| Tool/Technology | Context |
|---|---|
| **Claude Code** | Primary CLI tool; all skills are built for this |
| **skills.sh** | Community marketplace for browsing/installing skills |
| **claude-plugins-official** | Anthropic official GitHub marketplace repo |
| **Skill Creator** | Meta-skill that automates skill building with tests |
| **Cursor / Open Code** | Mentioned as alternative agentic coding tools that also support skills |
| **Airtop** | Sponsor -- cloud browser platform for web scraping/automation tasks |
| **Nano Banana** | Referenced as an image generation tool for design mockups |
| **Git worktrees** | Used by the eval system for isolated parallel test execution |
| **Skool (Agentic Labs)** | Leon paid community (dollar7/mo, 700+ members) for AI automation learning |

## Application to AI Consulting with Claude Code

### Direct operational improvements

- **Context forking for client project skills**: The consulting-intake skill and other client-facing skills that load reference documents (openclaw templates, expert system patterns, quality rubrics) should use forking to prevent context window contamination during intake sessions.

- **Dynamic injection for project scaffolding**: Pre-processing commands can inject the client current project structure, dependency manifest, and recent git history into consulting skills automatically. This eliminates the orientation phase at the start of every session and reduces token cost.

- **Background subagents for code review delivery**: The plan-build-review workflow can run review steps as background subagents, allowing the main session to continue with other tasks while reviews complete.

### Skill portfolio strategy

- **Audit existing skills against the two-type taxonomy**: Classify each skill in .claude/skills/ as capability uplift or encoded preferences. Capability uplift skills (browser automation, YouTube transcript extraction) need evals to track base model improvement. Encoded preferences skills (consulting-intake templates, style guides) are more durable since they encode business-specific conventions.

- **Add evals to high-value skills**: The consulting-intake skill and tac-scaffolding skill are prime candidates for eval harnesses. As Claude models improve, evals will show whether custom orchestration still outperforms the base model built-in capabilities.

- **Dynamic injection for the consulting-intake workflow**: The intake skill currently relies on the model reading template files during execution. Pre-processing injection could front-load client profile data, template contents, and reference documents, cutting tokens and improving response quality.

### Client deliverable potential

- **Skill creation as a consulting deliverable**: The Skill Creator meta-skill can be used during client sessions to build custom skills for the client specific workflows. This is a tangible, demonstrable deliverable -- the client gets a tested, benchmarked skill they can use independently.

- **Eval reports as proof of value**: Running evals on client-specific skills produces quantifiable benchmarks showing skill uplift over base model behavior. These reports can be included in session deliverables as evidence of ROI.
