# TAC Skill Index

21 skill files across TAC repositories.

## What is a Skill?

A Claude Code skill is a packaged capability with a SKILL.md manifest, templates, scripts, and references. Skills live in `.claude/skills/`.

## Skills by Repository

### adw-designer (Root TAC Skill)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\.claude\skills\adw-designer\`

**Purpose**: Design ADW pipelines from templates

```
adw-designer/
├── SKILL.md                        # Skill manifest
├── assets/
│   └── templates/
│       ├── tasks_template.md
│       ├── deployment/
│       │   └── run_pipeline.sh
│       ├── test-configs/
│       │   ├── jest.config.js
│       │   └── pytest.ini
│       └── workflows/
│           ├── auto-merge.yml
│           ├── cleanup.yml
│           └── test.yml
├── references/
│   └── tac8_adw_guide.md          # TAC-8 ADW reference
└── scripts/
    └── consultative_setup.py       # Interactive setup
```

Key Files:
- [SKILL.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/.claude/skills/adw-designer/SKILL.md)
- [tac8_adw_guide.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/.claude/skills/adw-designer/references/tac8_adw_guide.md)

### multi-agent-orchestration: meta-agent (3 files)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\.claude\skills\meta-agent\`

**Purpose**: Orchestrate multiple agents dynamically

```
meta-agent/
├── SKILL.md
├── examples.md
└── templates/
    └── subagent-template.md
```

Key Files:
- [SKILL.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/skills/meta-agent/SKILL.md)

### orchestrator_3_stream: meta-prompt (8 files)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\apps\orchestrator_3_stream\.claude\skills\meta-prompt\`

**Purpose**: Generate optimized prompts from templates

```
meta-prompt/
├── SKILL.md
├── PROMPT_TEMPLATE.md
└── examples/
    ├── README.md
    ├── orch_one_shot_agent.md
    ├── orch_scout_and_build.md
    ├── plan.md
    └── question.md
```

Key Files:
- [SKILL.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/apps/orchestrator_3_stream/.claude/skills/meta-prompt/SKILL.md)
- [PROMPT_TEMPLATE.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/apps/orchestrator_3_stream/.claude/skills/meta-prompt/PROMPT_TEMPLATE.md)

## Skill Patterns

### 1. Template-Based Skill
Provides templates that get customized per use.
Example: `adw-designer` - templates for ADW pipelines

### 2. Orchestration Skill
Coordinates multiple components.
Example: `meta-agent` - spawns and manages agents

### 3. Generation Skill
Creates new content from patterns.
Example: `meta-prompt` - generates optimized prompts

## Skill Structure

A well-structured skill includes:

```
skill-name/
├── SKILL.md           # Required: Manifest with description, triggers
├── assets/            # Optional: Static files, templates
├── examples/          # Optional: Usage examples
├── references/        # Optional: Documentation
├── scripts/           # Optional: Python scripts
└── templates/         # Optional: Reusable templates
```

### SKILL.md Format

```markdown
# Skill Name

## Description
What this skill does...

## Triggers
When to use this skill:
- "design adw"
- "create workflow"

## Usage
How to invoke...

## Examples
Sample invocations...
```

## Local Consulting-co Skills

Path: `C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\`

- [youtube-video-archiver](file:///C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/youtube-video-archiver/)
- [revstar-quickstart-workflow](file:///C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/skills/) (managed)

## Related Resources

- [Claude Code Skills Documentation](https://docs.anthropic.com/claude-code/skills)
