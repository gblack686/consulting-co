---
name: claude-code-plugin-builder
description: Build Claude Code marketplace plugins with guided workflow. Asks detailed questions about purpose, components, distribution, and generates complete plugin structure with documentation.
triggers:
  - build claude code plugin
  - create claude code plugin
  - plugin builder
  - marketplace plugin
  - claude plugin
---

# Claude Code Plugin Builder Skill

Build production-ready Claude Code marketplace plugins through a guided, question-driven workflow.

## Overview

This skill guides you through creating Claude Code plugins by:
1. Asking 5+ detailed questions about your plugin requirements
2. Generating the complete plugin file structure
3. Creating all necessary configuration files
4. Producing comprehensive documentation

## Prerequisites

- Understanding of Claude Code basics
- Git repository for plugin hosting (if distributing)
- Knowledge of your target use case

---

## Phase 1: Discovery Questions

Before building the plugin, I need to gather requirements. Please answer each question carefully.

### Question 1: Plugin Purpose & Scope

**What problem does this plugin solve?**

Choose the primary purpose:

| Option | Description | Typical Components |
|--------|-------------|-------------------|
| **A) Workflow Automation** | Automate repetitive development tasks | Commands, Hooks |
| **B) Code Quality** | Enforce standards, reviews, validation | Agents, Skills, Hooks |
| **C) External Integrations** | Connect to APIs, databases, services | MCP Servers, Commands |
| **D) Team Collaboration** | Standardize processes across team | Commands, Agents, Skills |
| **E) AI Enhancement** | Extend Claude's specialized knowledge | Skills, Agents |
| **F) Multi-Purpose** | Combination of above | Multiple components |

**Also describe in 1-2 sentences:** What specific task or workflow will this plugin enable?

---

### Question 2: Component Selection

**Which components should this plugin include?**

Select ALL that apply:

| Component | Purpose | Files Created |
|-----------|---------|---------------|
| **Commands** | User-triggered slash commands (`/deploy`) | `commands/*.md` |
| **Agents** | Specialized AI agents for tasks | `agents/*.md` |
| **Skills** | Auto-invoked capabilities | `skills/*/SKILL.md` |
| **Hooks** | Lifecycle event handlers | `hooks/hooks.json` |
| **MCP Servers** | External service connections | `.mcp.json` |

**Example combinations:**
- Code Review Plugin: Commands + Agents
- Security Scanner: Hooks + Skills
- API Integration: MCP Servers + Commands
- Full DevOps Suite: All components

---

### Question 3: Distribution Strategy

**How will this plugin be distributed?**

| Option | Location | Use Case |
|--------|----------|----------|
| **A) Personal Use** | `~/.claude/` | Only your projects |
| **B) Team/Project** | `.claude/settings.json` | Shared via git with team |
| **C) Public Marketplace** | GitHub public repo | Open source distribution |
| **D) Private Marketplace** | Private repo/server | Company internal use |

**Follow-up if B/C/D:** What is the marketplace name or repository path?

---

### Question 4: Target Environment

**What development context is this plugin designed for?**

Select ALL that apply:

| Environment | Examples | File Patterns |
|-------------|----------|---------------|
| **Frontend** | React, Vue, Angular, Svelte | `*.tsx`, `*.vue`, `*.jsx` |
| **Backend** | Node, Python, Go, Rust, Java | `*.ts`, `*.py`, `*.go` |
| **Full-Stack** | Next.js, Django, Rails | Multiple patterns |
| **DevOps** | Docker, K8s, Terraform, CI/CD | `Dockerfile`, `*.yaml` |
| **Data/ML** | Python, Jupyter, models | `*.py`, `*.ipynb` |
| **Mobile** | React Native, Flutter | `*.tsx`, `*.dart` |
| **Language Agnostic** | Works with any project | No specific patterns |

---

### Question 5: Plugin Identity

**Provide plugin metadata:**

```
Plugin Name: [e.g., "code-review-pro"]
Display Name: [e.g., "Code Review Pro"]
Description: [1-2 sentence description]
Author Name: [Your name or org]
Author Email: [Contact email]
Version: [e.g., "1.0.0"]
Category: [development|productivity|integration|security|other]
Tags: [comma-separated, e.g., "code-review,quality,automation"]
```

---

## Phase 2: Conditional Questions

Based on your answers, I may ask additional questions:

### Question 6: Hook Configuration *(if hooks selected)*

**Which lifecycle events should this plugin respond to?**

| Event | When Triggered | Use Cases |
|-------|----------------|-----------|
| **SessionStart** | New session begins | Context injection, initialization |
| **UserPromptSubmit** | User sends message | Preprocessing, validation |
| **PreToolUse** | Before tool executes | Security checks, logging |
| **PostToolUse** | After tool executes | Verification, cleanup |
| **Notification** | System events | Alerting, monitoring |
| **SubagentStop** | Subagent completes | Result collection |
| **Stop** | Session ends | Cleanup, reporting |

**For each selected event, describe:**
- What action should be taken?
- Should it be `command` (bash) or `prompt` (LLM evaluation)?
- Any file patterns to match?

---

### Question 7: MCP Integration *(if MCP selected)*

**What external services should this plugin connect to?**

| Service Type | Examples | Configuration Needed |
|--------------|----------|---------------------|
| **Git/GitHub** | Repos, PRs, Issues | GitHub token |
| **Database** | PostgreSQL, MongoDB | Connection string |
| **Cloud** | AWS, GCP, Azure | Credentials/region |
| **API Services** | REST, GraphQL | API keys, endpoints |
| **Communication** | Slack, Discord | Webhooks/tokens |
| **Custom** | Your own service | Custom config |

**For each service, provide:**
- Service name and type
- Required environment variables
- Authentication method

---

### Question 8: Agent Architecture *(if agents selected)*

**How should the agents be structured?**

| Pattern | Description | Example |
|---------|-------------|---------|
| **Single Specialist** | One focused agent | Bug detector agent |
| **Parallel Multi-Agent** | Multiple simultaneous | Code review (5 parallel reviewers) |
| **Sequential Pipeline** | Phased handoffs | Feature dev (explore → architect → review) |
| **Orchestrator** | Main + sub-agents | Coordinator delegates to specialists |

**For each agent, describe:**
- Agent name and purpose
- Tools it should have access to
- When it should be invoked

---

## Phase 3: Plugin Generation

Once questions are answered, I will generate:

### Directory Structure

```
{plugin-name}/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/                     # Slash commands
│   ├── {command-1}.md
│   └── {command-2}.md
├── agents/                       # Custom agents
│   ├── {agent-1}.md
│   └── {agent-2}.md
├── skills/                       # Agent skills
│   └── {skill-name}/
│       └── SKILL.md
├── hooks/                        # Event handlers
│   └── hooks.json
├── .mcp.json                     # MCP configuration
└── README.md                     # Documentation
```

### Generated Files

#### 1. plugin.json
```json
{
  "$schema": "https://anthropic.com/claude-code/plugin.schema.json",
  "name": "{plugin-name}",
  "version": "{version}",
  "description": "{description}",
  "author": {
    "name": "{author-name}",
    "email": "{author-email}"
  },
  "category": "{category}",
  "tags": ["{tags}"],
  "components": {
    "commands": ["commands/*.md"],
    "agents": ["agents/*.md"],
    "skills": ["skills/*/SKILL.md"],
    "hooks": ["hooks/hooks.json"]
  }
}
```

#### 2. Command Template (commands/{name}.md)
```markdown
---
description: {command-description}
---

# {Command Name}

{Detailed instructions for Claude when this command is invoked}

## Steps

1. {Step 1}
2. {Step 2}
3. {Step 3}

## Output Format

{Expected output structure}
```

#### 3. Agent Template (agents/{name}.md)
```markdown
---
description: {agent-description}
tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# {Agent Name}

{Agent purpose and behavior description}

## Capabilities

- {Capability 1}
- {Capability 2}

## Guidelines

- {Guideline 1}
- {Guideline 2}
```

#### 4. Skill Template (skills/{name}/SKILL.md)
```markdown
---
name: {skill-name}
description: {skill-description}
triggers:
  - {trigger-phrase-1}
  - {trigger-phrase-2}
globs:
  - "{file-pattern-1}"
  - "{file-pattern-2}"
---

# {Skill Name}

{Skill purpose and when to use}

## Knowledge

{Specialized knowledge this skill provides}

## Best Practices

- {Practice 1}
- {Practice 2}
```

#### 5. Hooks Template (hooks/hooks.json)
```json
{
  "hooks": [
    {
      "event": "{event-type}",
      "type": "command",
      "pattern": "{file-pattern}",
      "action": "{bash-command}"
    },
    {
      "event": "{event-type}",
      "type": "prompt",
      "pattern": "{tool-pattern}",
      "prompt": "{llm-prompt}"
    }
  ]
}
```

#### 6. MCP Template (.mcp.json)
```json
{
  "mcpServers": {
    "{server-name}": {
      "command": "{executable}",
      "args": ["{args}"],
      "env": {
        "{ENV_VAR}": "{value}"
      }
    }
  }
}
```

---

## Phase 4: Documentation Generation

After generating the plugin, I will create comprehensive documentation:

### README.md Structure

```markdown
# {Plugin Display Name}

{Description}

## Installation

### From Marketplace
\`\`\`bash
/plugin marketplace add {marketplace-path}
/plugin install {plugin-name}@{marketplace-name}
\`\`\`

### Manual Installation
\`\`\`bash
git clone {repo-url}
/plugin marketplace add ./path/to/plugin
/plugin install {plugin-name}
\`\`\`

## Components

### Commands
| Command | Description |
|---------|-------------|
| `/{command-1}` | {description} |
| `/{command-2}` | {description} |

### Agents
| Agent | Purpose |
|-------|---------|
| {agent-1} | {description} |
| {agent-2} | {description} |

### Skills
| Skill | Auto-Triggers |
|-------|---------------|
| {skill-1} | {trigger-conditions} |

### Hooks
| Event | Action |
|-------|--------|
| {event-1} | {action} |

## Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `{VAR_1}` | Yes/No | {description} |

### Settings
Add to `.claude/settings.json`:
\`\`\`json
{
  "plugins": [{
    "name": "{plugin-name}",
    "marketplace": "{marketplace}",
    "config": {
      "{option}": "{value}"
    }
  }]
}
\`\`\`

## Usage Examples

### Example 1: {Use Case}
\`\`\`bash
/{command} {args}
\`\`\`

### Example 2: {Use Case}
{Description of workflow}

## Development

### Local Testing
\`\`\`bash
/plugin marketplace add ./dev/{plugin-name}
/plugin install {plugin-name}@dev
\`\`\`

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test locally
5. Submit PR

## Changelog

### v{version} - {date}
- Initial release
- {Feature 1}
- {Feature 2}

## License

{License type}

## Author

{Author name} - {email}
```

---

## Phase 5: Marketplace Configuration

If distributing via marketplace, I will also generate:

### marketplace.json
```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "{marketplace-name}",
  "version": "1.0.0",
  "description": "{marketplace-description}",
  "owner": {
    "name": "{owner-name}",
    "email": "{owner-email}"
  },
  "plugins": [
    {
      "name": "{plugin-name}",
      "source": "./{plugin-directory}",
      "description": "{plugin-description}",
      "category": "{category}",
      "tags": ["{tags}"]
    }
  ]
}
```

### Distribution Checklist
- [ ] plugin.json complete with all metadata
- [ ] README.md with installation instructions
- [ ] All components tested locally
- [ ] marketplace.json created (if marketplace distribution)
- [ ] Repository created and pushed
- [ ] Test installation from marketplace

---

## Reference Documentation

This skill is based on:
- [[Claude-Code-Release-Report-2025]] - Complete feature documentation
- [[Claude-Code-Directory-Structure-Guide]] - File structure reference
- [Official Plugin Docs](https://code.claude.com/docs/en/plugins)
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [MCP Integration](https://code.claude.com/docs/en/mcp)
- [Agent Skills](https://code.claude.com/docs/en/skills)

---

## How to Use This Skill

When you want to build a Claude Code plugin:

1. **Invoke the skill** by saying "build claude code plugin" or "create marketplace plugin"
2. **Answer the 5 core questions** about purpose, components, distribution, environment, and identity
3. **Answer conditional questions** based on your component selections
4. **Review generated structure** and provide feedback
5. **Receive complete plugin files** ready to use or distribute
6. **Get documentation** including README and marketplace config

The skill will output all files and documentation needed for a production-ready plugin.

---

## Example Workflow

**User:** "I want to build a code review plugin for my team"

**Skill Response:**
1. Asks about purpose → Code Quality selected
2. Asks about components → Commands + Agents selected
3. Asks about distribution → Team/Project selected
4. Asks about environment → Full-Stack selected
5. Asks about identity → User provides metadata
6. Asks about agent architecture → Parallel Multi-Agent selected
7. Generates complete plugin structure
8. Creates README.md documentation
9. Provides installation instructions

**Output:** Complete plugin ready for team distribution via git.