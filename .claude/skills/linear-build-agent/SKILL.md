---
name: linear-build-agent
description: "Build: Linear Build Agent - Accept a plan, create Linear project + issues, run autonomous coding sessions, notify via Telegram"
user-invocable: true
---

# Linear Build Agent

Accept a project plan from the user, create a Linear project with issues, then launch autonomous coding sessions via the Claude Agent SDK. Send a Telegram notification with results when complete.

## Allowed Tools
`Read, Write, Edit, Bash, Glob, Grep, WebSearch, Agent`

## Workflow

### Phase 1: Plan Intake

1. The user provides a project plan (inline text, file path, or URL).
2. If a file path is given, read it. If inline, save it as `app_spec.txt` in the project directory.
3. Extract from the plan:
   - **Project name** (kebab-case slug for directory name)
   - **Tech stack** (frontend, backend, database, etc.)
   - **Features list** (grouped by domain/phase)
   - **Priority mapping** (P1=foundational, P2=primary, P3=secondary, P4=polish)

### Phase 2: Plan Review & Gap Analysis

Review the plan for completeness. Check:

| Category | Questions |
|----------|-----------|
| Edge Cases | Error handling, boundary conditions, empty states |
| Success Criteria | How do we verify each feature works? |
| Integration | External APIs, env vars, secrets needed |
| Scope | What's in/out, MVP vs stretch |
| Technical | Performance targets, testing approach, deployment |

Present a brief summary of gaps found. Ask the user to confirm or provide answers. If the user says "skip" or "looks good", proceed without blocking.

**[APPROVAL GATE]** — Wait for user confirmation before Phase 3.

### Phase 3: Linear Project Setup

1. Retrieve the Linear API key:
```bash
LINEAR_API_KEY=$(python -c "
import json, subprocess
r = subprocess.run(['aws', 'secretsmanager', 'get-secret-value',
    '--secret-id', 'gbautomation/core/linear-api-key',
    '--query', 'SecretString', '--output', 'text'],
    capture_output=True, text=True)
print(r.stdout.strip())
")
```

2. Use the Linear MCP tools (already configured in CLI):
   - `mcp__linear__list_teams` — get team ID
   - `mcp__linear__create_project` — create project with name from plan
   - Create issues from the features list using `mcp__linear__create_issue`:
     - Title format: `[Phase X] Feature name` or `[Domain] Feature name`
     - Include description with test steps and acceptance criteria
     - Set priority 1-4 based on plan
     - Aim for comprehensive coverage (all features from the plan)
   - Create META issue: `[META] Project Progress Tracker` with session tracking template
   - Save `.linear_project.json` state file in project directory

3. Create `init.sh` setup script based on tech stack.
4. Initialize git repo with initial commit.
5. Create project directory structure.

### Phase 4: Generate Coding Prompt

Generate a `coding_prompt.md` tailored to this project:
- Technology-specific guidelines (React patterns, API conventions, etc.)
- Code organization rules from the plan
- Error handling patterns
- Testing requirements
- Security considerations
- Feature-specific implementation notes

Save to the project directory alongside `app_spec.txt`.

### Phase 5: Launch Autonomous Agent Sessions

Set up and run the autonomous coding loop using the Claude Agent SDK:

```bash
cd "<project_dir>"

# Set environment
export LINEAR_API_KEY="<from Phase 3>"

# Run the agent harness
python "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/autonomous_agent_demo.py" \
  --project-dir "<project_dir>" \
  --max-iterations 6
```

**Session flow:**
- Session 1: Initializer (if `.linear_project.json` doesn't exist yet) or first coding session
- Sessions 2-6: Coding agent sessions, each with fresh context
- Each session picks highest-priority Todo issue, implements, tests, marks Done
- Sessions hand off via META issue comments

Monitor the output. If the harness exits early or errors, report the issue.

### Phase 6: Completion Report & Telegram Notification

After all sessions complete (or max iterations reached):

1. Query Linear for final status:
   - Count Done / In Progress / Todo issues
   - Read META issue comments for session summaries
   - Get the Linear project URL

2. Build completion report:
```
Project: {project_name}
Linear: https://linear.app/ai-agent-mastery-gb/project/{project_slug}
Sessions: {completed_count} / {max_iterations}

Done: X issues
In Progress: Y issues
Remaining: Z issues

Session Highlights:
- Session 1: {summary}
- Session 2: {summary}
...
```

3. Send Telegram notification:
```bash
# Get Telegram credentials from AWS
TELEGRAM_CREDS=$(aws secretsmanager get-secret-value \
  --secret-id "gbautomation/telegram/bot" \
  --query "SecretString" --output text)
BOT_TOKEN=$(echo "$TELEGRAM_CREDS" | python -c "import sys,json; print(json.load(sys.stdin)['bot_token'])")
CHAT_ID=$(echo "$TELEGRAM_CREDS" | python -c "import sys,json; print(json.load(sys.stdin)['chat_id'])")

# Send message
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="${CHAT_ID}" \
  -d parse_mode="Markdown" \
  -d text="<report>"
```

4. Present the final report to the user.

## Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| Max iterations | 6 | Override with user input |
| Model | claude-haiku-4-5-20251001 | Cost-efficient for coding sessions |
| Linear team | ai-agent-mastery-gb | GBAutomation Linear workspace |
| Project dir | `generations/{project-slug}` | Under the harness directory |

## Error Handling

- **Linear API fails**: Check API key, retry once, then report to user
- **Agent session crashes**: Log error, continue to next session (harness handles this)
- **All sessions error**: Send Telegram notification with error summary
- **Telegram fails**: Still show report in chat — Telegram is best-effort

## Dependencies

- `claude_code_sdk` Python package (Agent SDK)
- Linear MCP server (configured in Claude CLI)
- AWS CLI (for secrets retrieval)
- `curl` (for Telegram API)
- Harness code at `C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/`
