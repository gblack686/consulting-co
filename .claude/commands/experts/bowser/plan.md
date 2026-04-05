---
type: expert-file
parent: "[[bowser/_index]]"
file-type: command
command-name: "plan"
human_reviewed: false
tags: [expert-file, command, planning, bowser]
---

# Bowser Expert - Plan Mode

> Create browser automation plans informed by backend capabilities and known quirks.

## Purpose
Plan browser automation tasks using proven patterns from the bowser expertise. Produces a spec with backend selection, workflow steps, fallback strategy, and expected output files.

## Usage
```
/experts:bowser:plan [user_request]
```

## Allowed Tools
`Read`, `Glob`, `Grep`, `Task`, `Write`

---

## Planning Framework

### Step 1: Backend Selection

Which backend does this task need?

| Need | Backend | Reason |
|------|---------|--------|
| Authenticated site | claude-bowser | Uses real Chrome profile |
| Public page scraping | playwright-bowser | Headless, parallel capable |
| YouTube transcript | Apify | Browser transcript panel needs Google sign-in |
| YouTube description/metadata | claude-bowser | Works without auth |
| Parallel QA testing | bowser-agent (QA mode) | Multiple instances |
| Resource link following | WebFetch | Don't navigate browser away |

### Step 2: Auth Assessment

Does the target require authentication?

| Auth Level | Strategy |
|------------|----------|
| No auth needed | Use playwright-bowser (headless) |
| Google account needed | Cannot use MCP Chrome DevTools — find API fallback |
| Site-specific login | claude-bowser may work if user signs in manually first |
| API key/token | Use API directly, skip browser |

### Step 3: Fallback Strategy

What happens when the primary approach fails?

| Primary | Fallback | When to Switch |
|---------|----------|----------------|
| Browser transcript | Apify | Transcript panel spinner hangs |
| Browser description | WebFetch on video page | Navigation repeatedly fails |
| MCP Chrome DevTools | playwright-bowser | MCP server wedged |
| Browser scraping | WebFetch | Simple content extraction |

### Step 4: Output Convention

What files will be produced?

| Task Type | Output Files |
|-----------|-------------|
| YouTube extraction | `{ID}_transcript.txt`, `{ID}_description.txt`, `{ID}_metadata.json` |
| QA testing | Screenshots in `screenshots/bowser-qa/{run}/`, aggregated report |
| Blog summarization | Summary in response (no file) |
| Shopping | Confirmation in response (no file) |
| Custom workflow | Depends on workflow definition |

### Step 5: Validation

How to verify the automation worked:

- [ ] Target page loaded (check via `take_snapshot`)
- [ ] Expected content extracted (verify char count > 0)
- [ ] Output files saved to correct location
- [ ] All resource links followed and captured
- [ ] Screenshots taken at key steps (for QA)

---

## Plan Output Format

```markdown
# Browser Automation Plan: {Title}

## Task Analysis
| Property | Value |
|----------|-------|
| Target | {URL or site} |
| Auth required | {Yes/No — which service} |
| Backend | {claude-bowser / playwright-bowser / Apify} |
| Fallback | {fallback strategy} |

## Workflow Steps
1. {Step 1}
2. {Step 2}
3. {Step 3}

## Known Quirks
- {Any relevant quirks from Part 4 of expertise}

## Output Files
| File | Purpose |
|------|---------|
| `{path}` | {description} |

## Validation
- [ ] {check 1}
- [ ] {check 2}
```

---

## Examples

### Example 1: "Extract YouTube video transcript"
**Backend**: Apify (primary), MCP Chrome DevTools (for description only)
**Plan**: Fetch transcript via Apify, extract description via browser, combine outputs

### Example 2: "Run QA tests on our landing page"
**Backend**: bowser-agent (QA mode) (parallel)
**Plan**: Discover YAML stories, spawn agents, collect pass/fail results

### Example 3: "Summarize a blog post"
**Backend**: playwright-bowser (headless)
**Plan**: Navigate to blog, find latest post, extract content, summarize

### Example 4: "Add an item to Amazon cart"
**Backend**: claude-bowser (headed, needs Amazon auth)
**Plan**: Navigate Amazon, search, add to cart, stop at checkout
