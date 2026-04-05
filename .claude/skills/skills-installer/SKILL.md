---
name: skills-installer
description: "Consulting: Skills Installer - Transform workflow catalog entries into validated SKILL.md files with agent assignment, analyze-before-install scoring, and eval generation"
metadata: {"openclaw": {"requires": {"env": []}}}
---

# Skills Installer

## Purpose

Guided walkthrough that reads a client's workflow catalog, generates production-ready SKILL.md files for each selected workflow, assigns them to the correct domain agents, validates against the quality rubric, creates eval test cases, and registers them in openclaw.json.

## Variables

- `session_dir` (required) — Path to the client session directory (e.g., `.claude/skills/consulting-intake/client-sessions/20260305-michael-fisch`)
- `--batch` (optional) — Skip inter-skill confirmations, generate all selected skills without pausing
- `--guided` (optional, default) — Generate one at a time with confirmation between each
- `--phase N` (optional) — Auto-select all workflows in build phase N
- `--eval-only` (optional) — Generate eval files for existing skills without regenerating SKILL.md files

## Instructions

- IMPORTANT: metadata in every generated SKILL.md MUST be single-line JSON. This is the #1 cause of OpenClaw skill loading failures. NEVER use multiline YAML for metadata.
- IMPORTANT: Never hardcode API keys, tokens, or secrets in generated skills. Always reference via `requires.env` in metadata and `openclaw secrets set` in instructions.
- Description format MUST follow: `"{Category}: {Title} - {one-line purpose}"`
- Steps in generated skills must be actionable — reference actual API endpoints, not placeholders like "call the API"
- Every external action (send email, process payment, modify data) MUST have an `[APPROVAL GATE]` unless the workflow catalog explicitly has an empty `human_in_the_loop` array AND AGENTS.md grants Level 3+ autonomy for that domain
- Preserve all JSONC comments when editing openclaw.json
- Delivery: files written to `{session_dir}/workspace/skills/{agent-id}/{skill-name}/SKILL.md`

## Relevant Files

- `.claude/skills/consulting-intake/templates/skill.md.tmpl` — Canonical skill template (Purpose > Variables > Instructions > Workflow > Report)
- `.claude/skills/consulting-intake/references/skill-format-spec.md` — Format spec with critical single-line metadata rule
- `.claude/skills/consulting-intake/references/quality-rubric.md` — Validation rubric (25 pts per skill)
- `{session_dir}/session_output/workflow-catalog.json` — Source workflows with priority scores, APIs, HITL gates
- `{session_dir}/workspace/openclaw.json` — Agent config, bindings, existing skill entries
- `{session_dir}/workspace/AGENTS.md` — Agent domains, autonomy levels, tool access

## Workflow

### Phase 0: Obsidian Vault Research (ALWAYS RUN FIRST)

Before any other phase, grep the client-scoped Obsidian vault to gather existing knowledge and reference filepaths relevant to this client and their workflows.

Vault path: `{session_dir}/obsidian`

1. Check that `{session_dir}/obsidian` exists. If not, note "No client vault found" and proceed — vault context is enrichment, not a blocker.
2. Read the client name from `{session_dir}/session_output/client_profile.json`
3. Grep the vault for the client name (and key aliases — company name, agent name, primary contact):
   ```
   Grep pattern: "{client_name}|{company_name}|{agent_name}" path: {session_dir}/obsidian
   ```
4. Grep for each workflow domain keyword (e.g., "QuickBooks", "onboarding", "AR aging", "shipment") to find related vault notes, ADRs, session notes, or archived skills
5. Grep for `openclaw` + `skill` + `agent` to find deployment notes, install logs, or troubleshooting records
6. Collect all matched filepaths into a `vault_references[]` list — these become available to:
   - Inform agent matching decisions (Phase 3)
   - Enrich generated SKILL.md context sections (Phase 4)
   - Cross-reference in the summary report (Phase 9)
7. If vault matches exist, display a brief summary:
   ```
   Vault context found:
     3 notes matching "Fish Group" / "Finn"
     2 notes matching "QuickBooks"
     1 note matching "onboarding"
   Filepaths saved for reference in skill generation.
   ```

### Phase 1: Dynamic Injection (Load Context)

Run preprocessing to load all session context upfront — saves tokens by avoiding file reads mid-conversation.

1. Read `{session_dir}/session_output/workflow-catalog.json` — extract total workflows, build phases, workflow list
2. Read `{session_dir}/workspace/openclaw.json` — extract agents (id, name, model, emoji), bindings (keywords per agent), registered skill names from `skills.entries`
3. Read `{session_dir}/workspace/AGENTS.md` — extract autonomy levels per agent
4. Read `{session_dir}/session_output/client_profile.json` — extract client name, timezone, team members
5. Scan `{session_dir}/workspace/skills/` — list existing SKILL.md files to detect already-built skills
6. Hold all extracted data in working memory for subsequent phases

Alternatively, run `preprocess.sh {session_dir}` to inject this context automatically via shell preprocessing.

### Phase 2: Present Menu

Display workflows grouped by build phase, sorted by `priority_score` descending within each phase.

Format:
```
=== {Client Name} Workflow Catalog ({total} workflows) ===

Phase 1: Foundation (Sessions 3-4)
  [1] WF-001  AR Aging Follow-Up Emails        priority:9  complexity:low   [REGISTERED]
  [2] WF-002  Daily Cash Position Summary       priority:9  complexity:low
  [3] WF-004  Data Discrepancy Checker          priority:8  complexity:low

Phase 2: Client Operations (Sessions 5-6)
  [4] WF-003  New Client Workspace Generator    priority:8  complexity:med
  [5] WF-005  Weekly Client Digest              priority:7  complexity:low   [INSTALLED]
  ...
```

Status markers:
- `[INSTALLED]` — SKILL.md file exists at target path
- `[REGISTERED]` — Listed in openclaw.json `skills.entries` but no SKILL.md file
- (blank) — Not yet built or registered

If `build_phases` is not present in the catalog, sort all workflows by `priority_score` desc without phase grouping.

Ask user: "Which workflows to build? Enter numbers (1,2,3), a phase (phase1), or 'all'."

### Phase 3: Agent Matching

For each selected workflow, determine the target agent using this algorithm:

**Step 1 — API keyword matching:**
Score each agent by how many of the workflow's `apis[]` match that agent's binding keywords:

| API in catalog | Matches binding keywords |
|---|---|
| QuickBooks | quickbooks, sync, dashboard |
| Airtable | airtable, sync |
| Plaid | quickbooks (co-occurs), dashboard |
| Cin7 | piermont, sync, dashboard |
| ShipStation | shipment |
| Gmail/Outlook | (generic — +0.5 to all email-capable agents) |
| GitHub | new client, onboard |
| Supabase | sync, dashboard |
| Google Calendar | (generic — main unless specific agent handles scheduling) |
| Claude | (no routing — reasoning tool, not an API) |

**Step 2 — Name/description keyword matching:**
Check workflow name and description against each agent's binding `on[]` keywords. +1 per match.

**Step 3 — Special-case overrides:**
- "gary" or "customer service" in name/description → `garys-cs`
- "access", "provision", "permission", "revoke", "audit" → `permissions`
- "onboard", "offboard", "new client", "welcome" → `client-ops`
- Pure financial/data workflows (QuickBooks, Plaid, Cin7, Airtable only) → `data-airtable`

**Step 4 — Present for confirmation:**
```
WF-001 AR Aging Follow-Up Emails
  → data-airtable (📊 Data Agent)
  Matched: quickbooks (binding), sync (binding)
  Confirm? [Y/n/change agent]
```

If no agent scores > 0, assign to `main` and flag: "No strong domain match — assigned to main. Consider creating a binding."

### Phase 4: Generate SKILL.md

For each selected workflow, generate a SKILL.md file by mapping catalog fields to the template.

**When generating 3+ skills and `--batch` is set**, use the Agent tool with `run_in_background: true` to fork parallel generation agents. Each forked agent receives:
- The single workflow catalog entry (JSON)
- The target agent config (id, name, model, bindings)
- The skill template
- The API → Env Var mapping table
- The client's USER.md and SOUL.md content for context

For `--guided` mode (default), generate sequentially with user review between each.

**Field mapping from workflow catalog:**

| Template Field | Source |
|---|---|
| `name` | kebab-case of workflow `name` (e.g., "AR Aging Follow-Up Emails" → `ar-aging-follow-up-emails`) |
| `description` | `"{Category}: {Title} - {first sentence of description}"` |
| `metadata.requires.env` | Map from workflow `apis[]` using API → Env Var table below |
| Purpose section | Full workflow `description` |
| Variables section | `prerequisites` that are configurable (thresholds, recipients, etc.) |
| Instructions section | Critical guardrails + delivery mode + trigger/schedule info |
| Workflow phases | Derive from: (1) data fetch/API calls, (2) processing/analysis, (3) output/delivery |
| Approval gates | Direct from `human_in_the_loop[]` — mark each with `[APPROVAL GATE]` |
| Validation steps | Direct from `validation_gates[]` — add as verification substeps |
| Error handling | One failure mode per validation gate |
| Report section | Concrete output format based on workflow type |

**API → Env Var Mapping Table:**

| API | Env Var(s) |
|---|---|
| QuickBooks | `"QUICKBOOKS_CLIENT_ID"`, `"QUICKBOOKS_CLIENT_SECRET"` |
| Plaid | `"PLAID_API_KEY"`, `"PLAID_CLIENT_ID"` |
| Cin7 | `"CIN7_API_KEY"` |
| ShipStation | `"SHIPSTATION_API_KEY"` |
| Gmail/Outlook | `"GOOGLE_CLIENT_ID"`, `"GOOGLE_CLIENT_SECRET"`, `"GOOGLE_REFRESH_TOKEN"` |
| Supabase | `"SUPABASE_URL"`, `"SUPABASE_SERVICE_KEY"` |
| GitHub | `"GITHUB_TOKEN"` |
| Airtable | `"AIRTABLE_API_KEY"` |
| Stripe | `"STRIPE_SECRET_KEY"` |
| Google Calendar | `"GOOGLE_CLIENT_ID"`, `"GOOGLE_CLIENT_SECRET"`, `"GOOGLE_REFRESH_TOKEN"` |
| Google Drive | `"GOOGLE_CLIENT_ID"`, `"GOOGLE_CLIENT_SECRET"`, `"GOOGLE_REFRESH_TOKEN"` |
| LinkedIn | `"LINKEDIN_ACCESS_TOKEN"` |
| Claude | (none — uses model configured in openclaw.json) |

**Agent → Category Mapping:**

| Agent ID | Category for description |
|---|---|
| `main` | "Ops" |
| `client-ops` | "Ops" |
| `data-airtable` | "Data" |
| `permissions` | "Admin" |
| `garys-cs` | "Service" |
| (any other) | Derive from agent name or ask user |

**Schedule → Cron Mapping:**

| Schedule value | Default cron expression |
|---|---|
| `daily` | `0 7 * * 1-5` (weekday mornings) |
| `weekly` | `0 9 * * 1` (Monday 9am) |
| `monthly` | `0 9 1 * *` (1st of month) |
| `quarterly` | `0 9 1 1,4,7,10 *` (1st of quarter) |
| `annual` | `0 9 15 1 *` (mid-January) |
| `null` (event/manual) | No cron — on-demand or webhook trigger |

Adjust cron timezone to match client's timezone from `client_profile.json`.

**Context Files section (Ben AI — vault document references):**

Every generated skill MUST include this section:
```markdown
## Context Files

- `workspace/USER.md` — Client preferences, timezone, team members
- `workspace/MEMORY.md` — Accumulated business knowledge and decisions
- `workspace/SOUL.md` — Brand voice, values, and operational boundaries
- `workspace/AGENTS.md` — Autonomy levels for approval gate calibration
```

If Phase 0 found relevant vault notes, add them as Obsidian references:
```markdown
## Vault References

- `{vault_filepath_1}` — {one-line description of what it contains}
- `{vault_filepath_2}` — {one-line description}
```

This gives the running OpenClaw skill persistent business context beyond just API endpoints, plus links back to the knowledge base for deeper research.

**Dependency handling:**
If the workflow's `prerequisites` array references other workflow IDs (e.g., WF-016 requires WF-003 and WF-007), add to the Instructions section:
```
- DEPENDENCY: This skill requires {prerequisite workflow name} to be built and tested first.
  Verify {dependency skill-name} is installed before running.
```

**Output path:** `{session_dir}/workspace/skills/{agent-id}/{skill-name}/SKILL.md`

If the file already exists, ask: "SKILL.md already exists for {name}. Overwrite? [y/N]"

### Phase 5: Analyze Before Install

Before registering any skill in openclaw.json, run a 3-part analysis.

**5a. Relevance Score (0-10):**
- +3 if all skill APIs exist in `workspace/TOOLS.md`
- +2 if all prerequisites from workflow catalog are available
- +2 if schedule fits client's timezone and working hours
- +2 if the agent assignment has strong binding keyword matches
- +1 if the workflow addresses a documented client pain point (check MEMORY.md)

**5b. Security Scan (PASS/FAIL):**
Check the generated SKILL.md content for:
- [ ] No hardcoded API keys, tokens, passwords, or secrets
- [ ] All secrets referenced via `requires.env` in metadata
- [ ] No dangerous bash patterns (`rm -rf`, `DROP TABLE`, `curl | bash`, `eval`)
- [ ] No raw user input passed to shell commands without sanitization
- [ ] Channel-facing skills have `allowFrom` populated in openclaw.json

Any FAIL blocks installation until fixed.

**5c. Quality Grade (per-skill rubric, 25 points):**

| Check | Points | How to verify |
|---|---|---|
| YAML frontmatter parses | 3 | `name` and `description` present in `---` block |
| metadata single-line JSON | 5 | metadata field is on one line, parses as valid JSON |
| Description format | 2 | Matches `"{Category}: {Name} - {purpose}"` |
| Steps are actionable | 5 | Steps reference actual APIs from workflow's `apis[]`, not placeholders |
| Trigger defined | 3 | Cron expression, heartbeat, webhook, or "on-demand" specified |
| Output format specified | 3 | Report section has concrete format block |
| Error handling section | 2 | At least one failure mode per phase |
| Approval gates match AGENTS.md | 2 | High-blast actions have `[APPROVAL GATE]`, autonomy level respected |

Grades:
- **A** (23-25): Deploy immediately
- **B** (20-22): Deploy with minor notes
- **C** (15-19): Fix required — loop back to Phase 4 for this skill
- **F** (<15): Reject and regenerate from scratch

**Present analysis card:**
```
┌─────────────────────────────────────────────┐
│ ar-aging-follow-up-emails                   │
│ Agent: data-airtable (📊 Data Agent)        │
│ Relevance: 9/10  Security: PASS             │
│ Quality: A (24/25)                          │
│ Status: Ready to install                    │
└─────────────────────────────────────────────┘
```

If Quality is C or F, identify failing checks, fix the SKILL.md, and re-validate before proceeding.

### Phase 6: Generate Eval Test Cases

For each generated skill, create an eval file at:
`{session_dir}/workspace/skills/{agent-id}/{skill-name}/evals/test-{skill-name}.md`

**Eval structure:**

```markdown
---
name: test-{skill-name}
description: "Eval: {Skill Title} - Verify skill produces correct workflow with HITL gates and API references"
---

# Eval: {Skill Title}

## Test Prompt
"{A natural-language request that would trigger this skill}"

## Expected Behavior (With Skill)
1. Follows phased workflow (Phase 1 → 2 → 3, not ad-hoc)
2. References correct APIs: {list from workflow apis[]}
3. Includes approval gates: {list from human_in_the_loop[]}
4. Produces output matching the Report format
5. Uses env vars, not hardcoded keys

## Baseline Behavior (Without Skill)
- Agent may attempt the task but will lack:
  - Structured phases
  - Specific validation gates
  - Consistent output format
  - HITL gates at correct points

## Assertions
- [ ] Response follows phased workflow structure
- [ ] Response mentions {api_1} API
- [ ] Response mentions {api_2} API
- [ ] Response includes [APPROVAL GATE] before {hitl_step_1}
- [ ] Response produces structured output ({output_type})
- [ ] Response does NOT contain hardcoded API keys or tokens
- [ ] Response references workspace/USER.md or workspace/MEMORY.md for context
```

**Derive test prompt** from the workflow's binding keywords and description. It should sound like a natural user request, not a test command.

**Derive assertions** directly from:
- `apis[]` → one assertion per API that it's referenced
- `human_in_the_loop[]` → one assertion per HITL step
- `validation_gates[]` → one assertion per gate
- Security: always assert no hardcoded keys

These eval files enable future `claude eval` runs with worktree-based A/B comparison.

### Phase 7: Register in openclaw.json

After all skills pass analysis (Phase 5):

1. Read current `{session_dir}/workspace/openclaw.json`
2. For each new skill, construct the entry:
   - `user_invocable: true` if workflow trigger is `"manual"`
   - `user_invocable: true` if workflow has `user_invocable` field set
   - `enabled: true` for all
3. Group new entries under domain comments matching existing file style:
   ```
   // {Agent Domain} domain (new)
   "{skill-name}": { enabled: true },
   ```
4. Show the proposed additions to the user:
   ```
   Adding 3 new skill entries to openclaw.json:

   // Data & Airtable domain (new)
   "ar-aging-follow-up-emails":    { enabled: true },
   "daily-cash-position-summary":  { enabled: true },
   "data-discrepancy-checker":     { enabled: true },
   ```
5. On user confirmation, write the updated file preserving all existing JSONC comments
6. Skip any skills already present in `skills.entries` — note as "already registered" in the report

### Phase 8: Batch Commit Offer

After all files are written, offer commit options:

- **Single commit** (default for same-phase installs): `feat: add {N} skills for {client} Phase {N}`
- **Per-domain commits**: One commit per agent domain (`feat: add data-airtable skills for {client}`)
- **Per-skill commits**: Separate commit per skill (`feat: add {skill-name} for {client}`)
- **No commit**: Just leave files on disk

Only offer if user is in a git repository with uncommitted changes.

### Phase 9: Summary Report

```
## Skills Installer Report

Session: {session_dir}
Client: {client_name}
Date: {date}
Workflows processed: {N}

### Analysis Cards
{analysis card for each skill}

### Files Created
| File | Agent | Type |
|------|-------|------|
| workspace/skills/data-airtable/ar-aging-follow-up-emails/SKILL.md | data-airtable | skill |
| workspace/skills/data-airtable/ar-aging-follow-up-emails/evals/test-ar-aging-follow-up-emails.md | data-airtable | eval |
| ... | ... | ... |

### openclaw.json Updates
{N} entries added, {M} already registered (skipped)

### Cron Commands (run after deploy)
  openclaw cron add "ar-aging-follow-up-emails" "0 9 * * 1" --tz "{timezone}"
  openclaw cron add "daily-cash-position-summary" "0 7 * * 1-5" --tz "{timezone}"
  ...

### Prerequisites Still Needed
- [ ] quickbooks_api_key — required by WF-001, WF-002
- [ ] plaid_api_key — required by WF-002
- ...

### Next Steps
1. Review generated skills in workspace/skills/
2. Set up missing prerequisites (API keys via `openclaw secrets set`)
3. Deploy to OpenClaw instance
4. Run cron commands above
5. Run evals: `claude eval` to A/B test skills
6. Run `/skills-installer {session_dir} --phase 2` for next build phase
```

## Error Handling

- **workflow-catalog.json not found**: "No workflow catalog found at {path}. Run /workflow-ideator first to generate one."
- **openclaw.json not found**: "No openclaw.json found. Run /consulting-intake first to generate the workspace."
- **Zero workflows selected**: "No workflows selected. Run again and choose at least one."
- **SKILL.md write fails**: Check directory permissions. Create parent dirs if missing.
- **JSONC parse error on openclaw.json**: Fall back to showing the proposed entries for manual paste.
- **Quality grade C or F**: Fix inline and re-validate. Do not proceed to next workflow until >= 20/25.
- **Security scan FAIL**: Show exact line with the violation. Fix before registering.
