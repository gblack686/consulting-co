# TAC Agent Index — consulting-co/.claude/agents/

Auto-generated pattern catalog. Forge scans this before creating any agent.

## Agent Definitions (33+)

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| AI Codebase Optimizer | ai-codebase-optimizer.md | claude-sonnet | Analyze and optimize codebases |
| AWS Org Expert | aws-org-expert-agent.md | claude-sonnet | AWS organization management |
| Bowser | bowser-agent.md | claude-sonnet | Browser automation via Chrome DevTools |
| Build Agent | build-agent.md | claude-sonnet | Build system management |
| Cinematographer | cinematographer.md | claude-sonnet | Visual content creation |
| GitHub Actions Agent | github-actions-agent.md | claude-sonnet | CI/CD pipeline management |
| GitHub Issue Agent | github-issue-agent.md | claude-sonnet | Issue triage and PR creation |
| Google Workspace Agent | google-workspace-agent.md | claude-sonnet | Gmail, Calendar, Drive integration |
| Graphiti Agent | graphiti-agent.md | claude-sonnet | Knowledge graph management |
| Meta Pi Agent | meta-pi-agent.md | claude-sonnet | Meta-agent for Pi orchestration |

## Agent Structure Pattern

Every agent file follows this frontmatter structure:

```yaml
---
name: agent-name
model: provider/model-name
expertise:
  - path: path/to/expertise.yaml
    use-when: "When to load this expertise"
    updatable: true
    max-lines: 10000
skills:
  - path: path/to/skill.md
    use-when: "When to use this skill"
tools:
  - read
  - write
  - edit
  - bash
  - delegate
domain:
  - path: allowed/path/
    read: true
    upsert: true
    delete: false
---
```

## Key Patterns

- **Single responsibility**: Each agent handles ONE domain
- **Expertise is updatable**: Agents learn over time via expertise YAMLs
- **Domain restrictions**: Agents can only read/write within their domain
- **Delegation**: Agents can delegate to other agents via `delegate` tool
