---
type: expert-file
parent: "[[discord-scraping/_index]]"
file-type: command
command-name: plan
tags: [expert-file, command, planning]
---

# Discord & Scraping Expert - Plan Mode

> Create TAC-informed implementation plans for Discord scraping and signal pipeline changes.

## Purpose

Analyze a requested change or addition to Discord scraping workflows and produce an implementation plan.

## Allowed Tools
`Read, Write, Glob, Grep, Bash`

## Workflow

### Step 1: Load Context
1. Read `expertise.md` for current Discord scraping state
2. Read `_index.md` for available commands and tools
3. Read relevant `MEMORY.md` entries for past signal pipeline decisions

### Step 2: Analyze Request
1. What is being asked? (new channel? new alert? new data source?)
2. Which existing workflows are affected?
3. What new API access is needed?
4. Are there dependencies on other domains?

### Step 3: Classify by TAC Pattern

| If the request involves... | Use TAC Pattern |
|---------------------------|-----------------|
| Scheduled signal report (daily digest) | TAC-3: Template Engineering |
| Scraping a new single source | TAC-6: One Agent One Purpose |
| Syncing signal data to another tool | TAC-5: Feedback Loops |
| Morning brief content changes | TAC-3 + TAC-9: Context Engineering |
| Complex alert routing logic | TAC-5 + TAC-12: Orchestration |
| Improving signal quality over time | TAC-10: Self-Improving Prompts |

### Step 4: Research (if needed)
If the plan requires information about new APIs or tools:

- **API research**: Dispatch browser agent
  ```
  Task(subagent_type: "playwright-bowser-agent",
       prompt: "Research the {tool} API for OpenClaw integration. Find: docs URL, auth method, rate limits, key endpoints for message reading.")
  ```
- **Tutorial research**: Dispatch YouTube agent
  ```
  Task(subagent_type: "youtube-transcript-agent",
       prompt: "Search for 'OpenClaw {tool} integration' or '{tool} trading bot'. Extract config steps and working patterns.")
  ```

### Step 5: Output Plan
Write to `specs/discord-scraping-{feature}.md`:

```markdown
# Plan: {feature_name}

## TAC Pattern: {pattern_name}
## Affected Files: {file_list}
## New Files Needed: {new_file_list}

## Implementation Steps
1. {step}
2. {step}
3. {step}

## Validation Criteria
- Signals parsed correctly from test channel
- Alert threshold triggers as expected
- No duplicate alerts (state management works)

## Estimated Complexity: {low|medium|high}
```
