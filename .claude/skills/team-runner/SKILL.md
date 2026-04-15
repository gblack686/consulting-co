# Team Runner

End-to-end skill for planning, building, and running agent teams on Mac Mini through the Meridian pipeline (Max plan billing).

## Trigger

Invoke with `/team-runner` or when the user says "run a team", "start a deliberation", "plan an agent team", "spin up agents".

## Inputs

- **project**: Path to project knowledge base or repo on Mac Mini (e.g., `~/repos/eagle-app`, `~/repos/ceo-agents`)
- **team-type**: `ceo-board` (deliberation) | `multi-team` (lead-agents coding) | `ui-gen` (ui-agents generation)
- **brief** (ceo-board only): Path to brief directory or inline problem statement
- **playground**: `true` | `false` (default: `false`) — generate interactive HTML report

## Phases

### Phase 1: Spec Planning Session

Gather context and produce a team spec. This is an interactive planning session.

1. **Read project knowledge base** — scan the project's README, CLAUDE.md, existing `.pi/` config, and any prior specs
2. **Determine team composition** — based on team-type:
   - `ceo-board`: CEO + board members (default 8, customizable). Each member has a name, role, personality, model preference
   - `multi-team`: Orchestrator + teams (Planning, Engineering, Validation). Each team has a Lead + members
   - `ui-gen`: Setup + Brand + UI Generation (x3) + Validation (x3). Optimized for Vue SFC output
3. **Set token limits** — per-agent max_tokens, total budget ceiling, model selection per agent
4. **Define execution strategy** — sequential, parallel, or round-robin. Number of rounds (for ceo-board deliberation)
5. **Write spec** — output `team-spec.yaml` to `.claude/context/{project-slug}/team-spec.yaml`

**Checkpoint: User approves spec before proceeding.**

### Phase 2: Build Agents

Create agent infrastructure from approved spec.

1. **Create Claw Empire department** — POST to `/api/departments` on Mac Mini Claw Empire (:8800)
   - Auth: `Authorization: Bearer eagle-empire-2026`
   - Department named after the project
2. **Create Claw Empire agents** — POST to `/api/agents` for each agent in the spec
   - Map spec roles to Claw Empire roles: orchestrator/lead → `team_leader`, senior agents → `senior`, junior → `junior`
   - Set `cli_provider: claude` (routes through bridge)
   - Set personality from spec
3. **Archive to AI-Agent-KB** — invoke `/obsidian-agent-archiver` or write agent .md files directly to:
   - `C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\Agents\{agent-name}.md`
   - Use frontmatter: name, role, team, model, personality, created date
4. **Save agent ID mapping** — write `agent-ids.json` mapping spec agent names to Claw Empire UUIDs

### Phase 3: Run Team

Execute the agent team through the Meridian pipeline.

**Mac Mini connection**: `ssh greg@100.88.4.114`

**Execution chain**: `pi -p` → claude-bridge (:8077) → `claude -p` → Meridian (:3456) → Claude SDK → Max plan

1. **For each agent call**:
   - Update Claw Empire status: `PATCH /api/agents/{id}` → `{"status": "working"}`
   - Run: `pi -p --provider anthropic --model {agent.model} --no-tools --append-system-prompt "{agent.prompt}" "{message}"`
   - Capture response, save to output directory
   - Update Claw Empire status → `{"status": "idle"}`
2. **Orchestration patterns by team-type**:
   - `ceo-board`: CEO frames → board members respond (parallel where possible, sequential if Pi lockfile issue) → CEO synthesizes memo
   - `multi-team`: Orchestrator routes → team leads delegate → members execute → results flow back
   - `ui-gen`: Setup scaffolds → Brand validates tokens → Generators build SFCs → Validators check
3. **Output directory**: `{project}/.pi/{team-type}/output/{timestamp}/`

### Phase 4: Commit & Report

1. **Git commit** — on Mac Mini, commit all generated output:
   ```bash
   cd {project} && git add -A && git commit -m "team-runner: {team-type} output for {brief-name}"
   ```
2. **Generate report** — summarize the run:
   - Agents called, tokens used (estimated), time elapsed
   - Key outputs and decisions
   - If `playground=true`: generate an interactive HTML playground (via `/playground` skill) with:
     - Agent cards showing each agent's input/output
     - Timeline view of execution order
     - Expandable memo/output sections
3. **Log to wiki** — append entry to `~/repos/wiki/team-runs.md`:
   ```markdown
   ## {date} — {project} / {team-type}
   - Brief: {brief-name}
   - Agents: {count}
   - Duration: {elapsed}
   - Output: {output-dir}
   - Memo: {link to memo if ceo-board}
   ```

## Infrastructure Reference

| Service | Port | Purpose |
|---------|------|---------|
| Meridian | 3456 | Claude Code SDK proxy (launchd) |
| Claude Bridge | 8077 | Pi → claude CLI shim (launchd) |
| Claw Empire | 8800 | Visual agent dashboard |
| ttyd TUI | 7681 | Web terminal (Tailscale :8443/tui) |

## Claw Empire API

- Base: `http://127.0.0.1:8800`
- Auth: `Authorization: Bearer eagle-empire-2026`
- Create department: `POST /api/departments`
- Create agent: `POST /api/agents` — `{name, name_ko, department_id, role, cli_provider, avatar_emoji, personality}`
- Update status: `PATCH /api/agents/{id}` — `{status: "working"|"idle"|"break"}`
- List agents: `GET /api/agents`

## Pi Lockfile Workaround

Pi uses a session lockfile. When running multiple `pi -p` calls in parallel, add `--no-session` to avoid lock contention. Alternatively, run board members sequentially (slower but reliable).

## Models Available via Bridge

All route through claude-bridge → Meridian → Max plan:
- `claude-sonnet-4-6` (fast, cheap on Max)
- `claude-opus-4-6` (powerful, for CEO/orchestrator roles)
- `claude-sonnet-4-5-20250929`
- `claude-opus-4-5-20250514`
