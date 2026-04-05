# Linear Anthropic Harness - Architecture & Azure DevOps Adaptation

**Date**: 2025-12-16
**Source**: Linear-Coding-Agent-Harness Analysis
**Status**: Adaptation Strategy

## Executive Summary

The Linear-Coding-Agent-Harness implements Anthropic's **two-agent pattern** for long-running autonomous development tasks. It solves the multi-session problem by using Linear as the source of truth for project state, replacing local file-based tracking with a cloud-based project management system. Adapting this for Azure DevOps would be **moderately straightforward** - the core pattern remains the same, only the API integration layer needs to change.

---

## How the Two-Agent Pattern Works

### The Core Problem It Solves

AI agents face a fundamental limitation: **context windows are finite, but complex projects require hours or days of work.** When an agent's context fills up:
- It loses all memory of previous work
- It cannot resume where it left off
- Progress is lost between sessions

### Anthropic's Solution: Two Specialized Agents

Instead of one general-purpose agent that tries to do everything, the harness uses **two distinct agent roles**:

#### Agent 1: Initializer (Session 1 Only)

**Single Responsibility**: Set up the foundation for all future work.

**What it does:**
1. Reads the application specification (`app_spec.txt`)
2. Creates a Linear project for the application
3. Generates **50 comprehensive Linear issues** with:
   - Detailed descriptions
   - Specific test steps
   - Priority levels (1-4)
   - Acceptance criteria
4. Creates a special **META issue** for session handoff tracking
5. Sets up project structure (directories, `init.sh`, git repo)
6. Saves state in `.linear_project.json` marker file
7. Optionally begins implementing highest-priority features

**Key Output:** A Linear workspace with 50 organized issues representing the entire project scope.

**Duration:** One session (until context fills up or initialization complete)

#### Agent 2: Coding Agent (Sessions 2+)

**Single Responsibility**: Implement one feature at a time, verify thoroughly, hand off cleanly.

**What it does each session:**

1. **Orient** - Read project files, check git history, understand spec
2. **Query Linear** - Get current project status from Linear API:
   - How many issues are Done?
   - What's In Progress?
   - What's the highest-priority Todo issue?
3. **Verify** - Test 1-2 previously completed features via Puppeteer:
   - Navigate through UI with browser automation
   - Take screenshots
   - Check for regressions or bugs
   - If broken → reopen the issue and fix it FIRST
4. **Claim** - Update Linear issue status: `Todo` → `In Progress`
5. **Implement** - Write the code for the selected feature
6. **Test** - Verify with Puppeteer browser automation:
   - Click through the UI like a real user
   - Capture screenshots
   - Verify all test steps from issue description
   - Check for console errors
7. **Document** - Add detailed comment to Linear issue:
   - What was implemented
   - What was tested
   - Git commit hash
8. **Complete** - Update Linear issue status: `In Progress` → `Done`
9. **Commit** - Git commit with descriptive message
10. **Handoff** - Add session summary to META issue:
    - What was accomplished
    - Current progress stats
    - Notes for next session
11. **End Cleanly** - Leave app in working state, all code committed

**Duration:** Multiple sessions, each completing 1-2 issues (varies by complexity)

---

## How the Agents Communicate

### Traditional Approach (File-Based)
The original Anthropic autonomous coding harness uses:
- `feature_list.json` - Tracks completion status
- `claude-progress.txt` - Session notes
- Git commits - Full history

**Problem:** Files are local, no visibility for humans or other systems.

### Linear-Integrated Approach (Cloud-Based)

The harness replaces files with **Linear as the source of truth**:

| Traditional File | Linear Equivalent | Benefits |
|-----------------|-------------------|----------|
| `feature_list.json` | Linear Issues with status | Real-time visibility, searchable, shareable |
| `claude-progress.txt` | Comments on META issue | Threaded discussions, @mentions, notifications |
| Test case descriptions | Issue descriptions with test steps | Structured, version-controlled |
| Session handoff notes | Issue comments | Permanent, timestamped, auditable |

**Communication Flow:**

```
Session 1 (Initializer):
  ├─ Creates Linear Project: "My App"
  ├─ Creates 50 Issues: "Auth - Login", "UI - Homepage", etc.
  ├─ Creates META Issue: "[META] Project Progress Tracker"
  └─ Saves .linear_project.json: {project_id, team_id, meta_issue_id}

Session 2 (Coding Agent):
  ├─ Reads .linear_project.json → knows Linear project ID
  ├─ Queries Linear API → "What's in Todo?"
  ├─ Reads META Issue comments → "What did previous session do?"
  ├─ Selects highest-priority Todo issue
  ├─ Updates issue status → In Progress
  ├─ Implements feature
  ├─ Adds comment with implementation details
  ├─ Updates issue status → Done
  ├─ Adds comment to META issue with session summary
  └─ Ends cleanly

Session 3 (Coding Agent):
  ├─ Reads .linear_project.json
  ├─ Queries Linear API → "What's in Todo?"
  ├─ Reads META Issue comments → "Session 2 completed Auth - Login"
  ├─ Verifies Session 2's work with Puppeteer
  ├─ (If broken) → Reopens issue, fixes it first
  ├─ (If working) → Proceeds to next Todo issue
  └─ Repeats coding agent workflow
```

**Key Insight:** Each agent starts with **zero memory** but gains full context by:
1. Reading `.linear_project.json` (which Linear project to use)
2. Querying Linear API (current state of all issues)
3. Reading META issue comments (session summaries from predecessors)

---

## Key Architecture Components

### 1. Linear MCP Integration

**File:** `client.py`

The harness uses Linear's **MCP (Model Context Protocol) server** over HTTP:

```python
{
    "type": "http",
    "url": "https://mcp.linear.app/mcp",
    "headers": {
        "Authorization": f"Bearer {LINEAR_API_KEY}"
    }
}
```

**Available Linear MCP Tools:**
- `mcp__linear__list_teams` - Get available teams
- `mcp__linear__create_project` - Create Linear project
- `mcp__linear__list_issues` - Query issues by status, priority, project
- `mcp__linear__get_issue` - Get detailed issue info
- `mcp__linear__create_issue` - Create new issue
- `mcp__linear__update_issue` - Change status, priority, etc.
- `mcp__linear__create_comment` - Add comment to issue
- `mcp__linear__list_comments` - Read issue comments

### 2. State Persistence

**File:** `.linear_project.json` (created by Initializer)

```json
{
  "initialized": true,
  "created_at": "2025-12-16T10:00:00Z",
  "team_id": "TEAM-abc123",
  "project_id": "PROJECT-xyz789",
  "project_name": "Claude.ai Clone",
  "meta_issue_id": "ISSUE-meta456",
  "total_issues": 50,
  "notes": "Project initialized by initializer agent"
}
```

**Purpose:**
- Marker file that Linear has been set up
- Stores IDs needed for all Linear API calls
- Prevents re-initialization

### 3. Security Model

**File:** `security.py`

Three layers of security:
1. **Bash Allowlist** - Only permitted commands can execute
2. **Filesystem Restrictions** - Limited to project directory
3. **MCP Permissions** - Tools must be explicitly allowed

**Allowed Bash Commands:**
```python
ALLOWED_COMMANDS = {
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep",
    # Node.js
    "npm", "node", "npx",
    # Version control
    "git",
    # Process management
    "ps", "lsof", "sleep", "pkill",
    # Python (if needed)
    "python", "python3", "pip",
}
```

**Security Hook:** Validates every bash command before execution. Blocks anything not in allowlist.

### 4. Browser Automation

**Puppeteer MCP Integration** (stdio transport):

Used for **mandatory UI verification**:
- `mcp__puppeteer__puppeteer_navigate` - Go to URL
- `mcp__puppeteer__puppeteer_screenshot` - Capture screenshot
- `mcp__puppeteer__puppeteer_click` - Click elements
- `mcp__puppeteer__puppeteer_fill` - Fill inputs
- `mcp__puppeteer__puppeteer_select` - Dropdowns
- `mcp__puppeteer__puppeteer_hover` - Hover states

**Why Required:** Agents must test like humans, through the actual UI. No shortcuts.

### 5. Progress Tracking

**File:** `progress.py`

Utilities for:
- Session headers (which iteration, which mode)
- Linear initialization detection
- Progress summaries

**Visual Feedback:**
```
═══════════════════════════════════════════════════════════
  AUTONOMOUS CODING SESSION #5 (CODING MODE)
  Project: My App
  Model: claude-opus-4-5-20251101
═══════════════════════════════════════════════════════════
```

---

## Adapting for Azure DevOps

### Difficulty Assessment: **Moderate** (3-5 days of work)

The core two-agent pattern is **platform-agnostic**. Only the API integration layer needs to change.

### What Changes?

#### 1. Replace Linear MCP with Azure DevOps REST API

**Current (Linear):**
```python
# Uses MCP server at https://mcp.linear.app/mcp
# Tools auto-discovered via MCP protocol
await client.tool("mcp__linear__list_issues", {
    "projectId": project_id,
    "status": "Todo"
})
```

**New (Azure DevOps):**
```python
# Direct REST API calls to Azure DevOps
import requests

headers = {
    "Authorization": f"Basic {base64_encoded_pat}",
    "Content-Type": "application/json"
}

# List work items
response = requests.get(
    f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=7.0",
    headers=headers,
    json={
        "query": "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'To Do'"
    }
)
```

**Implementation Options:**

**Option A: Build Custom MCP Server for Azure DevOps** (Recommended)
- Create an MCP server wrapping Azure DevOps REST API
- Maintains tool-based architecture
- Easier for agent to use (structured tools vs raw API)
- Reusable across other projects

**Option B: Direct API Integration**
- Replace Linear MCP calls with Azure DevOps REST calls
- Simpler to implement initially
- Less flexible, harder to maintain

#### 2. Map Linear Concepts to Azure DevOps Concepts

| Linear | Azure DevOps | Mapping Notes |
|--------|--------------|---------------|
| **Team** | **Project** | Top-level container |
| **Project** | **Epic** or **Feature** | Group related work |
| **Issue** | **User Story** or **Task** | Individual work item |
| **Status** (Todo/In Progress/Done) | **State** (New/Active/Closed) | Workflow states |
| **Priority** (1-4) | **Priority** (1-4) | Same scale |
| **Comments** | **Comments** or **Discussion** | Threaded conversations |
| **Description** | **Description** | Markdown content |
| **Labels/Tags** | **Tags** | Categorization |

#### 3. Update State File Structure

**Current (`.linear_project.json`):**
```json
{
  "initialized": true,
  "team_id": "TEAM-abc123",
  "project_id": "PROJECT-xyz789",
  "meta_issue_id": "ISSUE-meta456"
}
```

**New (`.azure_devops_project.json`):**
```json
{
  "initialized": true,
  "organization": "myorg",
  "project": "MyProject",
  "area_path": "MyProject\\MyApp",
  "epic_id": 12345,
  "meta_work_item_id": 12346,
  "work_item_type": "User Story",
  "total_work_items": 50
}
```

#### 4. Update Prompts

**Initializer Prompt Changes:**

```diff
- Use `mcp__linear__list_teams` to see available teams.
+ Use Azure DevOps API to list available projects and area paths.

- Use `mcp__linear__create_project` to create a new project.
+ Create a new Epic in Azure DevOps to group all work items.

- Use `mcp__linear__create_issue` to create 50 issues.
+ Use Azure DevOps API to create 50 User Stories under the Epic.

- Save the project ID to `.linear_project.json`
+ Save the Epic ID and project info to `.azure_devops_project.json`
```

**Coding Prompt Changes:**

```diff
- Query Linear for highest-priority Todo issue
+ Query Azure DevOps for highest-priority New/To Do User Story

- Update Linear issue status to "In Progress"
+ Update Azure DevOps work item State to "Active"

- Add comment to Linear issue
+ Add comment to Azure DevOps work item

- Update Linear issue status to "Done"
+ Update Azure DevOps work item State to "Closed"
```

### What Stays the Same?

✅ **Two-agent pattern** - Initializer + Coding agents
✅ **Session handoff** - Via comments on META work item
✅ **Git integration** - Commits still track progress
✅ **Security model** - Bash allowlist unchanged
✅ **Browser automation** - Puppeteer testing unchanged
✅ **Project structure** - `init.sh`, directories, etc.
✅ **Core workflow** - Orient → Query → Verify → Implement → Test → Document → Commit → Handoff

### Implementation Roadmap

#### Phase 1: Azure DevOps API Wrapper (1-2 days)

**Create:** `azure_devops_client.py`

```python
class AzureDevOpsClient:
    def __init__(self, organization: str, project: str, pat: str):
        self.org = organization
        self.project = project
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis"

    def list_work_items(self, state: str = None, area_path: str = None) -> list:
        """Query work items using WIQL"""
        wiql_query = f"SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '{self.project}'"
        if state:
            wiql_query += f" AND [System.State] = '{state}'"
        if area_path:
            wiql_query += f" AND [System.AreaPath] = '{area_path}'"

        # Execute WIQL query
        response = requests.post(
            f"{self.base_url}/wit/wiql?api-version=7.0",
            headers=self.headers,
            json={"query": wiql_query}
        )

        # Get work item details
        work_item_ids = [wi['id'] for wi in response.json().get('workItems', [])]
        return self.get_work_items(work_item_ids)

    def create_work_item(self, work_item_type: str, title: str, description: str,
                         priority: int = 2, area_path: str = None, epic_id: int = None) -> dict:
        """Create a new work item"""
        document = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority}
        ]

        if area_path:
            document.append({"op": "add", "path": "/fields/System.AreaPath", "value": area_path})

        if epic_id:
            # Link to Epic
            document.append({
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"{self.base_url}/wit/workItems/{epic_id}"
                }
            })

        response = requests.post(
            f"{self.base_url}/wit/workitems/${work_item_type}?api-version=7.0",
            headers={**self.headers, "Content-Type": "application/json-patch+json"},
            json=document
        )
        return response.json()

    def update_work_item(self, work_item_id: int, state: str = None, **fields) -> dict:
        """Update work item fields"""
        document = []

        if state:
            document.append({"op": "add", "path": "/fields/System.State", "value": state})

        for field, value in fields.items():
            document.append({"op": "add", "path": f"/fields/{field}", "value": value})

        response = requests.patch(
            f"{self.base_url}/wit/workitems/{work_item_id}?api-version=7.0",
            headers={**self.headers, "Content-Type": "application/json-patch+json"},
            json=document
        )
        return response.json()

    def add_comment(self, work_item_id: int, comment_text: str) -> dict:
        """Add a comment to a work item"""
        response = requests.post(
            f"{self.base_url}/wit/workItems/{work_item_id}/comments?api-version=7.0-preview.3",
            headers=self.headers,
            json={"text": comment_text}
        )
        return response.json()

    def get_comments(self, work_item_id: int) -> list:
        """Get all comments for a work item"""
        response = requests.get(
            f"{self.base_url}/wit/workItems/{work_item_id}/comments?api-version=7.0-preview.3",
            headers=self.headers
        )
        return response.json().get('comments', [])
```

#### Phase 2: Update Agent Logic (1 day)

**Modify:** `agent.py`

```python
from azure_devops_client import AzureDevOpsClient

async def run_autonomous_agent_azure(
    project_dir: Path,
    organization: str,
    project: str,
    pat: str,
    model: str,
    max_iterations: Optional[int] = None,
):
    """Run autonomous agent with Azure DevOps integration"""

    # Initialize Azure DevOps client
    ado_client = AzureDevOpsClient(organization, project, pat)

    # Check if already initialized
    state_file = project_dir / ".azure_devops_project.json"

    if not state_file.exists():
        # Run initializer
        prompt = get_azure_initializer_prompt()
        # Agent will use Azure DevOps client to create Epic and User Stories
    else:
        # Run coding agent
        state = json.loads(state_file.read_text())
        prompt = get_azure_coding_prompt(state)
        # Agent will query User Stories, implement, update states
```

#### Phase 3: Update Prompts (1 day)

**Create:** `prompts/azure_initializer_prompt.md`
- Replace Linear MCP calls with Azure DevOps API instructions
- Update work item creation syntax
- Adjust state file structure

**Create:** `prompts/azure_coding_prompt.md`
- Replace Linear queries with Azure DevOps WIQL queries
- Update state transitions (Todo → New/Active/Closed)
- Adjust comment syntax

#### Phase 4: Testing & Validation (1 day)

- Test initializer creates Epic + 50 User Stories
- Test coding agent can query and update work items
- Test session handoff via META work item comments
- Verify security model still works
- Validate browser automation unchanged

### API Compatibility Comparison

| Feature | Linear MCP | Azure DevOps REST API | Notes |
|---------|-----------|----------------------|-------|
| **Authentication** | Bearer token | PAT (Basic auth) | Both simple |
| **Work Item Creation** | POST /issues | POST /wit/workitems/\$Type | Similar |
| **Querying** | GraphQL-like filters | WIQL (SQL-like) | Different syntax, same capability |
| **Status Updates** | PATCH /issues/:id | PATCH /wit/workitems/:id | JSON Patch format |
| **Comments** | POST /comments | POST /wit/workitems/:id/comments | Similar |
| **Relationships** | Built into schema | /relations link | More manual in ADO |
| **Real-time Updates** | Webhooks available | Webhooks available | Both support notifications |

**Verdict:** Azure DevOps REST API is **fully capable** of supporting this pattern. No missing features.

### Complexity Factors

#### Easy (No Changes Needed):
✅ Two-agent pattern
✅ Session handoff concept
✅ Git integration
✅ Security model
✅ Browser testing
✅ File structure

#### Moderate (Straightforward Adaptation):
⚠️ API calls (Linear → Azure DevOps)
⚠️ State file format
⚠️ Prompt instructions
⚠️ Work item mapping

#### Hard (Optional Advanced Features):
❌ Azure DevOps Boards customization (custom fields, workflows)
❌ Azure Repos integration (PR creation, code reviews)
❌ Azure Pipelines integration (CI/CD automation)
❌ Azure Test Plans integration (test case management)

### Why This Pattern Works for Any PM Tool

The **key insight** is that the two-agent pattern is **decoupled from the specific PM tool**:

**Required Capabilities:**
1. Create a project/container
2. Create work items with descriptions and statuses
3. Query work items by status
4. Update work item status
5. Add comments to work items
6. Read comments from work items

**Any PM tool with these capabilities can work:**
- ✅ Linear
- ✅ Azure DevOps
- ✅ Jira
- ✅ GitHub Issues
- ✅ GitLab Issues
- ✅ Monday.com
- ✅ Asana
- ✅ ClickUp
- ✅ Trello (with limitations)

**The agents don't care about:**
- How the API is structured
- What authentication mechanism is used
- Whether it's GraphQL, REST, or RPC
- The specific terminology (issues vs work items vs tasks)

**They only care about:**
- "Where is the list of things to do?"
- "How do I mark something in progress?"
- "How do I leave notes for the next session?"

This is why adaptation is straightforward - **you're just swapping out the communication layer, not the core logic.**

---

## Advantages of Linear Integration (vs File-Based)

| Aspect | File-Based (Original) | Linear-Integrated | Winner |
|--------|----------------------|------------------|--------|
| **Visibility** | Only visible in codebase | Real-time web dashboard | 🏆 Linear |
| **Collaboration** | Single agent only | Multiple agents + humans | 🏆 Linear |
| **Search** | Manual file searching | Full-text search, filters | 🏆 Linear |
| **Notifications** | None | Email, Slack, webhooks | 🏆 Linear |
| **History** | Git commits only | Comments + state changes | 🏆 Linear |
| **Recovery** | Hard (parse JSON files) | Easy (query API) | 🏆 Linear |
| **Reporting** | Manual analysis | Built-in charts, analytics | 🏆 Linear |
| **Setup Complexity** | Zero (just files) | Requires API key, project | 🏆 Files |
| **Offline** | Works offline | Requires internet | 🏆 Files |
| **Cost** | Free | \$\$ (Linear subscription) | 🏆 Files |

**Verdict:** Linear integration is **significantly better** for any serious project, especially when:
- Multiple stakeholders need visibility
- Project spans days/weeks
- Human oversight is required
- Budget allows for tooling

---

## Example Session Transcript

### Session 1: Initializer

```
═══════════════════════════════════════════════════════════
  AUTONOMOUS CODING SESSION #1 (INITIALIZER MODE)
  Project: My App
  Model: claude-opus-4-5-20251101
═══════════════════════════════════════════════════════════

[Tool: mcp__linear__list_teams]
   Input: {}
   [Done]

Found team: "My Team" (TEAM-abc123)

[Tool: mcp__linear__create_project]
   Input: {name: "My App", teamIds: ["TEAM-abc123"], description: "Full-stack web application"}
   [Done]

Created Linear project: PROJECT-xyz789

Now creating 50 Linear issues...

[Tool: mcp__linear__create_issue]
   Input: {title: "Auth - User login flow", teamId: "TEAM-abc123", projectId: "PROJECT-xyz789", priority: 1, description: "## Feature Description\nImplement user authentication with email/password...\n\n## Test Steps\n1. Navigate to /login\n2. Enter valid credentials\n3. Click 'Sign In'\n4. Verify redirect to dashboard"}
   [Done]

Issue created: ISSUE-001 (Auth - User login flow)

[Tool: mcp__linear__create_issue]
   ... (48 more issues)
   [Done]

[Tool: mcp__linear__create_issue]
   Input: {title: "[META] Project Progress Tracker", teamId: "TEAM-abc123", projectId: "PROJECT-xyz789", description: "## Project Overview\nMy App - Full-stack web application\n\n## Session Tracking\n..."}
   [Done]

Created META issue: ISSUE-meta456

Setting up project structure...

[Bash: mkdir -p src/frontend src/backend]
   [Done]

Creating init.sh...

Initializing git repository...

[Bash: git init && git add . && git commit -m "Initial setup"]
   [Done]

Saving state to .linear_project.json...

Updating META issue with session summary...

[Tool: mcp__linear__create_comment]
   Input: {issueId: "ISSUE-meta456", body: "## Session 1 Complete - Initialization\n\n### Accomplished\n- Created 50 Linear issues from app_spec.txt\n- Set up project structure\n- Created init.sh\n- Initialized git repository\n\n### Linear Status\n- Total issues: 50\n- Done: 0\n- In Progress: 0\n- Todo: 50"}
   [Done]

Session 1 complete. Next agent will continue with implementation.
```

### Session 2: Coding Agent

```
═══════════════════════════════════════════════════════════
  AUTONOMOUS CODING SESSION #2 (CODING MODE)
  Project: My App
  Model: claude-opus-4-5-20251101
═══════════════════════════════════════════════════════════

Orienting to project...

[Bash: pwd]
   /path/to/my_project

[Bash: cat app_spec.txt]
   [Reads full specification]

[Bash: cat .linear_project.json]
   {project_id: "PROJECT-xyz789", team_id: "TEAM-abc123", meta_issue_id: "ISSUE-meta456"}

Checking Linear status...

[Tool: mcp__linear__list_issues]
   Input: {projectId: "PROJECT-xyz789", status: "Done"}
   [Done]

0 issues Done. (Fresh project, no verification needed)

[Tool: mcp__linear__list_issues]
   Input: {projectId: "PROJECT-xyz789", status: "Todo", limit: 5, orderBy: "priority"}
   [Done]

Found 5 Todo issues:
1. ISSUE-001: Auth - User login flow (Priority: 1)
2. ISSUE-002: Database - PostgreSQL setup (Priority: 1)
3. ISSUE-003: API - Express server scaffold (Priority: 1)
4. ISSUE-004: Frontend - React app scaffold (Priority: 1)
5. ISSUE-005: Auth - JWT token generation (Priority: 2)

Selecting highest-priority issue: ISSUE-001 (Auth - User login flow)

Claiming issue...

[Tool: mcp__linear__update_issue]
   Input: {id: "ISSUE-001", status: "In Progress"}
   [Done]

Reading issue description for test steps...

[Tool: mcp__linear__get_issue]
   Input: {id: "ISSUE-001"}
   [Done]

Test steps:
1. Navigate to /login
2. Enter valid credentials
3. Click 'Sign In'
4. Verify redirect to dashboard

Implementing authentication...

[Writing code for auth module, Express routes, React login component]

Starting development server...

[Bash: npm run dev]
   Server running on http://localhost:3045

Testing with Puppeteer...

[Tool: mcp__puppeteer__puppeteer_navigate]
   Input: {url: "http://localhost:3045/login"}
   [Done]

[Tool: mcp__puppeteer__puppeteer_screenshot]
   [Done - screenshot shows login page]

[Tool: mcp__puppeteer__puppeteer_fill]
   Input: {selector: "#email", value: "test@example.com"}
   [Done]

[Tool: mcp__puppeteer__puppeteer_fill]
   Input: {selector: "#password", value: "password123"}
   [Done]

[Tool: mcp__puppeteer__puppeteer_click]
   Input: {selector: "button[type='submit']"}
   [Done]

[Tool: mcp__puppeteer__puppeteer_screenshot]
   [Done - screenshot shows dashboard, redirect successful]

Feature verified! Adding implementation comment...

[Tool: mcp__linear__create_comment]
   Input: {issueId: "ISSUE-001", body: "## Implementation Complete\n\n### Changes Made\n- src/backend/auth/login.js\n- src/frontend/components/LoginForm.jsx\n- JWT token generation\n- Cookie-based session management\n\n### Verification\n- Tested via Puppeteer\n- Login flow works end-to-end\n- Redirect to dashboard successful\n- No console errors\n\n### Git Commit\ncommit abc123: Implement user login authentication"}
   [Done]

Marking issue as Done...

[Tool: mcp__linear__update_issue]
   Input: {id: "ISSUE-001", status: "Done"}
   [Done]

Committing to git...

[Bash: git add . && git commit -m "Implement user login authentication\n\n- JWT token generation\n- Login form with validation\n- Session management\n- Linear issue: ISSUE-001"]
   [Done]

Updating META issue with session summary...

[Tool: mcp__linear__create_comment]
   Input: {issueId: "ISSUE-meta456", body: "## Session 2 Complete - First Feature\n\n### Completed This Session\n- ISSUE-001: Auth - User login flow\n\n### Current Progress\n- 1 issues Done\n- 0 issues In Progress\n- 49 issues remaining in Todo\n\n### Notes for Next Session\n- Login working, continue with database setup (ISSUE-002)\n- All verification tests passing"}
   [Done]

Session 2 complete. Ready for next agent to continue.
```

---

## Advantages for Azure DevOps Adaptation

### Why Azure DevOps Works Well

1. **Enterprise Integration**
   - Already used by many organizations
   - Integrated with Azure Repos, Pipelines, Test Plans
   - SSO/Active Directory support
   - Compliance and audit trails

2. **Mature API**
   - Well-documented REST API
   - WIQL (Work Item Query Language) for complex queries
   - Webhooks and service hooks
   - PowerShell and Azure CLI support

3. **Work Item Hierarchy**
   - Epic → Feature → User Story → Task
   - Perfect for organizing 50+ work items
   - Built-in relationships and dependencies

4. **Customizable Workflows**
   - Can define custom states (Todo → In Progress → Done)
   - Custom fields for agent metadata
   - Process templates for standardization

### Potential Enhancements (Beyond Linear)

1. **Azure Repos Integration**
   ```python
   # Link commits to work items automatically
   git commit -m "Implement login #123"
   # Azure DevOps auto-links commit to work item 123
   ```

2. **Azure Pipelines Integration**
   ```yaml
   # Trigger builds when agent commits
   trigger:
     branches:
       include:
         - main

   steps:
     - script: npm test
     - script: npm run build
     # Update work item status on success/failure
   ```

3. **Azure Test Plans Integration**
   - Convert issue test steps into formal test cases
   - Track test execution results
   - Link test results to work items

4. **Advanced Queries**
   ```sql
   -- WIQL allows complex queries
   SELECT [System.Id], [System.Title]
   FROM WorkItems
   WHERE [System.TeamProject] = 'MyApp'
     AND [System.State] = 'To Do'
     AND [System.Tags] CONTAINS 'agent-ready'
     AND [Microsoft.VSTS.Common.Priority] <= 2
   ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.CreatedDate] DESC
   ```

5. **Dashboards and Reporting**
   - Burndown charts (work remaining)
   - Velocity tracking (features per session)
   - Custom widgets showing agent progress
   - Executive summaries from query results

---

## Recommended Approach for Adaptation

### Option 1: Custom MCP Server for Azure DevOps (Best)

**Pros:**
- Maintains tool-based architecture
- Reusable across multiple projects
- Easier for agents to use
- Community can benefit

**Cons:**
- More upfront work (build MCP server)
- Need to learn MCP protocol

**Effort:** 5-7 days total

### Option 2: Direct API Integration (Faster)

**Pros:**
- Simpler implementation
- No MCP server needed
- Can start immediately

**Cons:**
- Less flexible
- Harder to maintain
- Not reusable

**Effort:** 3-4 days total

### Recommended: **Option 1** for production use, **Option 2** for proof-of-concept

---

## Conclusion

The Linear-Coding-Agent-Harness demonstrates that Anthropic's two-agent pattern is:
1. **Highly effective** for long-running autonomous development
2. **Platform-agnostic** - works with any PM tool with basic CRUD operations
3. **Moderately easy to adapt** - core logic unchanged, only API layer changes

**For Azure DevOps specifically:**
- ✅ All required capabilities present (work items, states, comments)
- ✅ Enterprise-grade features (audit, security, integration)
- ✅ Well-documented REST API
- ⚠️ Requires 3-7 days of implementation work
- ✅ No technical blockers

**Bottom line:** Adapting the Linear harness for Azure DevOps is **absolutely feasible** and would provide significant value for organizations already using Azure DevOps. The two-agent pattern itself requires zero changes - only the communication layer needs updating.

---

**Next Steps to Adapt:**
1. Set up Azure DevOps test project
2. Build API wrapper (python `azure_devops_client.py`)
3. Update prompts (initializer and coding)
4. Test with simple 5-issue demo
5. Scale to full 50-issue projects
6. (Optional) Build reusable MCP server for community

**Estimated Timeline:** 1 week for MVP, 2 weeks for production-ready version
