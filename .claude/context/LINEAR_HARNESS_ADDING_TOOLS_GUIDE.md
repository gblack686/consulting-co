# Adding Tools to Linear Harness - Complete Guide

**Date**: 2025-12-16
**Context**: Tool Management and MCP Configuration Strategies

## Current State: Two Different Approaches

### Approach 1: Claude Code CLI (`.mcp.json`)

**Used by:** Claude Code CLI, standalone Claude sessions
**File:** `.mcp.json` in project root
**Example:**
```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=unickqnwfheaczccvgbw"
    },
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer lin_api_xxxxx"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["puppeteer-mcp-server"]
    }
  }
}
```

**How it works:**
- Claude Code CLI reads `.mcp.json` at startup
- Auto-discovers tools from connected MCP servers
- Tools become available to agent automatically

**Pros:**
- ✅ Declarative configuration (easy to read/modify)
- ✅ No code changes needed to add servers
- ✅ Standardized across projects
- ✅ Can be version controlled
- ✅ Works with all Claude Code CLI sessions

**Cons:**
- ❌ Only works with Claude Code CLI, not Python SDK
- ❌ No programmatic validation
- ❌ Can't dynamically configure based on project state

### Approach 2: Python SDK (Hardcoded in `client.py`)

**Used by:** Linear-Coding-Agent-Harness, custom autonomous agents
**File:** `client.py` (Python code)
**Example:**
```python
# client.py
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    # ... manually listed
]

LINEAR_TOOLS = [
    "mcp__linear__list_teams",
    "mcp__linear__get_team",
    # ... manually listed
]

ClaudeSDKClient(
    options=ClaudeCodeOptions(
        allowed_tools=[
            *BUILTIN_TOOLS,
            *PUPPETEER_TOOLS,
            *LINEAR_TOOLS,
        ],
        mcp_servers={
            "puppeteer": {"command": "npx", "args": ["puppeteer-mcp-server"]},
            "linear": {
                "type": "http",
                "url": "https://mcp.linear.app/mcp",
                "headers": {"Authorization": f"Bearer {LINEAR_API_KEY}"}
            }
        }
    )
)
```

**How it works:**
- MCP servers configured programmatically in Python
- Tools must be explicitly listed in `allowed_tools`
- Changes require editing Python code

**Pros:**
- ✅ Full programmatic control
- ✅ Dynamic configuration based on environment
- ✅ Type checking and validation
- ✅ Can inject secrets from environment variables
- ✅ Works with Python SDK

**Cons:**
- ❌ Tools must be manually listed (error-prone)
- ❌ Requires code changes to add servers
- ❌ Not standardized across projects
- ❌ Harder for non-Python users to modify

---

## The Problem with Current Linear Harness

### Manual Tool Management is Brittle

**Current issue in `client.py`:**
```python
# All 24 Linear tools hardcoded by hand
LINEAR_TOOLS = [
    "mcp__linear__list_teams",
    "mcp__linear__get_team",
    "mcp__linear__list_projects",
    "mcp__linear__get_project",
    "mcp__linear__create_project",
    "mcp__linear__update_project",
    "mcp__linear__list_issues",
    "mcp__linear__get_issue",
    "mcp__linear__create_issue",
    "mcp__linear__update_issue",
    # ... 14 more tools
]
```

**Problems:**
1. **Maintenance burden** - What if Linear adds new tools?
2. **Error-prone** - Easy to typo tool names
3. **No discovery** - Can't auto-detect available tools
4. **Duplication** - Listed in `allowed_tools` AND `mcp_servers`

---

## Recommended Approach: Hybrid Strategy

### Use `.mcp.json` + Dynamic Tool Discovery

**Best of both worlds:**
1. ✅ Declarative MCP server config (`.mcp.json`)
2. ✅ Auto-discover tools from MCP servers
3. ✅ Programmatic filtering/validation if needed
4. ✅ Easy to add new servers without code changes

### Implementation Strategy

#### Step 1: Create `.mcp.json` in Project Root

**File:** `C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/.mcp.json`

```json
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer ${LINEAR_API_KEY}"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["puppeteer-mcp-server"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    }
  }
}
```

**Note:** `${ENV_VAR}` syntax is pseudo-code - actual implementation needs to read from environment.

#### Step 2: Update `client.py` to Load from `.mcp.json`

**New approach:**

```python
import json
import os
from pathlib import Path
from typing import Dict, List, Any

def load_mcp_config(project_dir: Path) -> Dict[str, Any]:
    """
    Load MCP server configuration from .mcp.json with environment variable substitution.

    Args:
        project_dir: Project directory to search for .mcp.json

    Returns:
        Dictionary of MCP server configurations
    """
    # Look for .mcp.json in project dir, then parent dirs, then home dir
    search_paths = [
        project_dir / ".mcp.json",
        Path.cwd() / ".mcp.json",
        Path.home() / ".mcp.json"
    ]

    mcp_file = None
    for path in search_paths:
        if path.exists():
            mcp_file = path
            break

    if not mcp_file:
        print("No .mcp.json found, using default configuration")
        return {}

    print(f"Loading MCP configuration from: {mcp_file}")

    with open(mcp_file) as f:
        config = json.load(f)

    # Substitute environment variables in config
    config = substitute_env_vars(config)

    return config.get("mcpServers", {})


def substitute_env_vars(obj: Any) -> Any:
    """
    Recursively substitute ${ENV_VAR} placeholders with environment variable values.

    Args:
        obj: Configuration object (dict, list, or string)

    Returns:
        Configuration with substituted values
    """
    if isinstance(obj, dict):
        return {k: substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Replace ${VAR} with environment variable
        import re
        def replace_env(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                raise ValueError(f"Environment variable {var_name} not set")
            return value

        return re.sub(r'\$\{([^}]+)\}', replace_env, obj)
    else:
        return obj


def discover_mcp_tools(mcp_servers: Dict[str, Any]) -> List[str]:
    """
    Discover available tools from MCP servers.

    For now, this is a placeholder that returns wildcard permissions.
    In a full implementation, you would:
    1. Connect to each MCP server
    2. Call the `list_tools` method
    3. Collect all tool names

    Args:
        mcp_servers: MCP server configurations

    Returns:
        List of tool names (or wildcards for all tools)
    """
    # Simple approach: allow all tools from configured servers
    tool_patterns = []

    for server_name in mcp_servers.keys():
        # Allow all tools from this server
        tool_patterns.append(f"mcp__{server_name}__*")

    return tool_patterns


def create_client(project_dir: Path, model: str) -> ClaudeSDKClient:
    """
    Create a Claude Agent SDK client with MCP configuration from .mcp.json.

    Args:
        project_dir: Directory for the project
        model: Claude model to use

    Returns:
        Configured ClaudeSDKClient
    """
    # Load MCP servers from .mcp.json
    mcp_servers = load_mcp_config(project_dir)

    if not mcp_servers:
        print("Warning: No MCP servers configured")
        print("Create .mcp.json to configure MCP servers")

    # Discover available tools
    mcp_tool_patterns = discover_mcp_tools(mcp_servers)

    # Built-in tools
    builtin_tools = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]

    # Combine all tools
    allowed_tools = builtin_tools + mcp_tool_patterns

    print(f"Configured MCP servers: {list(mcp_servers.keys())}")
    print(f"Allowed tool patterns: {mcp_tool_patterns}")
    print()

    # Security settings
    security_settings = {
        "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                "Bash(*)",
                *allowed_tools,  # Include all MCP tool patterns
            ],
        },
    }

    settings_file = project_dir / ".claude_settings.json"
    project_dir.mkdir(parents=True, exist_ok=True)

    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            system_prompt="You are an expert full-stack developer building a production-quality web application. You use Linear for project management and tracking all your work.",
            allowed_tools=allowed_tools,
            mcp_servers=mcp_servers,  # Pass the loaded config directly
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
```

#### Step 3: Usage - Adding New Tools

**To add a new MCP server:**

1. **Edit `.mcp.json`:**
```json
{
  "mcpServers": {
    "linear": { /* existing */ },
    "puppeteer": { /* existing */ },

    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

2. **Set environment variable:**
```bash
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxx'
```

3. **Run the agent:**
```bash
python autonomous_agent_demo.py --project-dir ./my_project
```

**That's it!** No code changes needed. The agent now has access to all GitHub MCP tools.

---

## Should a Skill Manage This?

### YES - A Skill Would Be Extremely Valuable

**Proposed Skill:** `linear-harness-mcp-manager`

**What it should do:**

1. **Initialize `.mcp.json`** with recommended defaults
2. **Add MCP servers** interactively
3. **Validate MCP configuration** (test connections)
4. **List available tools** from connected servers
5. **Generate documentation** of available tools
6. **Update `client.py`** to use dynamic loading

### Skill Implementation Outline

**File:** `.claude/skills/linear-harness-mcp-manager/skill.md`

```markdown
---
name: linear-harness-mcp-manager
description: Manage MCP server configuration for Linear-Coding-Agent-Harness projects
version: 1.0.0
---

# Linear Harness MCP Manager

Manage MCP server configuration for autonomous coding agent projects.

## Capabilities

1. **Initialize MCP Configuration**
   - Creates `.mcp.json` with recommended servers
   - Sets up environment variable templates
   - Generates documentation

2. **Add MCP Server**
   - Interactive prompts for server details
   - Validates server connection
   - Updates `.mcp.json`

3. **List Available Tools**
   - Connects to MCP servers
   - Lists all available tools
   - Generates tool documentation

4. **Validate Configuration**
   - Tests all MCP server connections
   - Checks environment variables
   - Verifies tool accessibility

## Commands

### Initialize New Project

```bash
/linear-harness-init
```

Creates `.mcp.json` with:
- Linear MCP (if LINEAR_API_KEY set)
- Puppeteer MCP (for browser automation)
- Environment variable placeholders

### Add MCP Server

```bash
/linear-harness-add-mcp <server-name>
```

Interactive prompts:
1. Server type (http, stdio, sse)
2. Connection details (URL, command, args)
3. Authentication (headers, env vars)
4. Test connection

### List Tools

```bash
/linear-harness-list-tools
```

Output:
```
MCP Servers Configured:
├─ linear (24 tools)
│  ├─ mcp__linear__list_teams
│  ├─ mcp__linear__create_project
│  └─ ... (22 more)
├─ puppeteer (7 tools)
│  ├─ mcp__puppeteer__puppeteer_navigate
│  └─ ... (6 more)
└─ github (15 tools)
   ├─ mcp__github__create_issue
   └─ ... (14 more)

Total: 46 tools available
```

### Validate Configuration

```bash
/linear-harness-validate
```

Checks:
- ✅ .mcp.json exists and is valid JSON
- ✅ All environment variables set
- ✅ All MCP servers accessible
- ✅ Tools discoverable from each server
```

**File:** `.claude/skills/linear-harness-mcp-manager/README.md`

```markdown
# Linear Harness MCP Manager Skill

## Installation

1. Copy this skill to your Linear harness project:
   ```bash
   cp -r .claude/skills/linear-harness-mcp-manager /path/to/linear-harness/.claude/skills/
   ```

2. Create slash commands:
   ```bash
   cd /path/to/linear-harness
   mkdir -p .claude/commands
   ```

3. Use the skill:
   ```bash
   /linear-harness-init
   /linear-harness-add-mcp github
   /linear-harness-validate
   ```

## What This Skill Does

### Problem It Solves

The Linear harness currently hardcodes MCP server configuration in `client.py`:
- 🔴 Adding servers requires editing Python code
- 🔴 Tools must be manually listed (error-prone)
- 🔴 No validation of MCP connections
- 🔴 No discovery of available tools

### Solution

This skill provides:
- ✅ Declarative `.mcp.json` configuration
- ✅ Interactive MCP server setup
- ✅ Automatic tool discovery
- ✅ Connection validation
- ✅ Documentation generation

### Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Initialize Project                                  │
│     /linear-harness-init                                │
│                                                         │
│     Creates:                                            │
│     ├─ .mcp.json (empty or with defaults)              │
│     ├─ .env.template (environment variable template)    │
│     └─ MCP_TOOLS.md (documentation placeholder)         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. Add MCP Servers                                     │
│     /linear-harness-add-mcp linear                      │
│     /linear-harness-add-mcp puppeteer                   │
│     /linear-harness-add-mcp github                      │
│                                                         │
│     For each server:                                    │
│     ├─ Prompts for connection details                   │
│     ├─ Tests connection                                 │
│     ├─ Updates .mcp.json                                │
│     └─ Updates MCP_TOOLS.md                             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. Validate Configuration                              │
│     /linear-harness-validate                            │
│                                                         │
│     Checks:                                             │
│     ├─ .mcp.json syntax valid                           │
│     ├─ Environment variables set                        │
│     ├─ MCP servers accessible                           │
│     ├─ Tools discoverable                               │
│     └─ Generates validation report                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. Run Autonomous Agent                                │
│     python autonomous_agent_demo.py --project-dir ...   │
│                                                         │
│     Agent automatically:                                │
│     ├─ Loads .mcp.json                                  │
│     ├─ Connects to configured servers                   │
│     ├─ Discovers available tools                        │
│     └─ Uses tools during development                    │
└─────────────────────────────────────────────────────────┘
```

## Example Usage

### Scenario: Add GitHub MCP Server

```bash
# 1. Initialize if not already done
/linear-harness-init

# 2. Add GitHub server
/linear-harness-add-mcp github
```

**Skill prompts:**
```
Adding MCP server: github

Server type?
  1. http (HTTP/HTTPS endpoint)
  2. stdio (Local command)
  3. sse (Server-Sent Events)
> 2

Command to run?
> npx

Arguments (comma-separated)?
> -y, @modelcontextprotocol/server-github

Environment variables needed (key=value, comma-separated)?
> GITHUB_PERSONAL_ACCESS_TOKEN

Testing connection to github MCP server...
✅ Connected successfully
✅ Discovered 15 tools

Updated .mcp.json
Updated MCP_TOOLS.md

To use this server:
1. Set environment variable:
   export GITHUB_PERSONAL_ACCESS_TOKEN='your-token'

2. Run the agent:
   python autonomous_agent_demo.py --project-dir ./my_project
```

**Resulting `.mcp.json`:**
```json
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer ${LINEAR_API_KEY}"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["puppeteer-mcp-server"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

**Resulting `MCP_TOOLS.md`:**
```markdown
# Available MCP Tools

## Linear (24 tools)
- mcp__linear__list_teams
- mcp__linear__create_project
- mcp__linear__list_issues
- ... (21 more)

## Puppeteer (7 tools)
- mcp__puppeteer__puppeteer_navigate
- mcp__puppeteer__puppeteer_screenshot
- ... (5 more)

## GitHub (15 tools)
- mcp__github__create_issue
- mcp__github__create_pull_request
- mcp__github__search_repositories
- ... (12 more)

**Total: 46 tools available**

Generated: 2025-12-16
```
```

---

## Implementation Roadmap

### Phase 1: Standardize on `.mcp.json` (2 hours)

1. Create `.mcp.json` in Linear harness root
2. Update `client.py` to load from `.mcp.json`
3. Test with existing servers (Linear, Puppeteer)
4. Document in README

### Phase 2: Build MCP Manager Skill (4 hours)

1. Create skill structure
2. Implement `/linear-harness-init` command
3. Implement `/linear-harness-add-mcp` command
4. Implement `/linear-harness-validate` command
5. Implement `/linear-harness-list-tools` command

### Phase 3: Tool Discovery (2 hours)

1. Implement MCP tool discovery (connect to server, list tools)
2. Generate tool documentation automatically
3. Cache discovered tools for performance

### Phase 4: Testing & Documentation (2 hours)

1. Test with multiple MCP servers
2. Create comprehensive usage examples
3. Add to Linear harness documentation
4. Create video walkthrough

**Total Estimated Time: 10 hours**

---

## Benefits of Skill-Managed MCP Configuration

### For Users

1. **No Code Changes** - Add servers via slash commands, not Python edits
2. **Validation** - Catch configuration errors before running agents
3. **Discovery** - See all available tools without reading docs
4. **Consistency** - Same configuration approach across projects

### For Developers

1. **Maintainability** - Declarative config easier to update
2. **Testing** - Can validate MCP connections independently
3. **Debugging** - Clear error messages when servers misconfigured
4. **Extensibility** - Easy to add new servers without code changes

### For Azure DevOps Adaptation

When adapting for Azure DevOps:

**Without Skill:**
```python
# Must edit client.py
AZURE_DEVOPS_TOOLS = [
    "mcp__azuredevops__list_projects",
    "mcp__azuredevops__create_workitem",
    # ... manually list 30+ tools
]
```

**With Skill:**
```bash
/linear-harness-add-mcp azuredevops
# Interactive prompts guide you through setup
# Tools auto-discovered
# Configuration validated
# Ready to go
```

---

## Recommended Architecture

```
linear-harness/
├── .mcp.json                    # ← MCP server configuration (NEW)
├── .env.template                # ← Environment variable template (NEW)
├── client.py                    # ← Updated to load .mcp.json
├── autonomous_agent_demo.py     # ← No changes needed
├── prompts/
│   ├── initializer_prompt.md
│   └── coding_prompt.md
├── .claude/
│   ├── skills/
│   │   └── linear-harness-mcp-manager/  # ← NEW SKILL
│   │       ├── skill.md
│   │       ├── README.md
│   │       └── commands/
│   │           ├── init.md
│   │           ├── add-mcp.md
│   │           ├── validate.md
│   │           └── list-tools.md
│   └── commands/
│       ├── linear-harness-init.md
│       ├── linear-harness-add-mcp.md
│       ├── linear-harness-validate.md
│       └── linear-harness-list-tools.md
└── MCP_TOOLS.md                 # ← Auto-generated tool documentation (NEW)
```

---

## Summary

### How to Add Tools NOW (Manual)

1. Edit `client.py`:
   ```python
   GITHUB_TOOLS = [
       "mcp__github__create_issue",
       "mcp__github__create_pr",
       # ... list all tools
   ]

   ClaudeSDKClient(
       allowed_tools=[*BUILTIN_TOOLS, *LINEAR_TOOLS, *PUPPETEER_TOOLS, *GITHUB_TOOLS],
       mcp_servers={
           "linear": {...},
           "puppeteer": {...},
           "github": {
               "command": "npx",
               "args": ["-y", "@modelcontextprotocol/server-github"],
               "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ["GITHUB_TOKEN"]}
           }
       }
   )
   ```

2. Set environment variable:
   ```bash
   export GITHUB_TOKEN='ghp_xxxxx'
   ```

3. Run agent

### How to Add Tools BETTER (Recommended)

1. **Create `.mcp.json`** (one time setup)
2. **Update `client.py`** to load from `.mcp.json` (one time)
3. **Add new servers** by editing `.mcp.json` (no code changes)

### How to Add Tools BEST (With Skill)

1. **Build the skill** (10 hours, one time)
2. **Use slash commands** to manage MCP servers:
   ```bash
   /linear-harness-add-mcp github
   /linear-harness-add-mcp azuredevops
   /linear-harness-add-mcp supabase
   ```

**Recommendation:** Start with "Better" approach (`.mcp.json`), then build skill if you plan to:
- Add/remove MCP servers frequently
- Share harness with non-technical users
- Adapt harness for multiple PM tools (Azure DevOps, Jira, etc.)
- Need validation and documentation generation

The skill would make the harness **much more accessible** and **easier to adapt** for different use cases.
