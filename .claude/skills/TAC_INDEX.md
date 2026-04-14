# TAC Skills Index — consulting-co/.claude/skills/

Auto-generated pattern catalog. Forge scans this before creating any skill.

## Skills

| Skill | Directory | Purpose |
|-------|-----------|---------|
| adw-dispatch | adw-dispatch/ | Autonomous delivery workflow dispatch |
| adw-status | adw-status/ | Delivery workflow status checking |
| anthropic-memory | anthropic-memory/ | Anthropic conversation memory management |
| aws-config-manager | aws-config-manager/ | AWS configuration management |
| browser-automation | browser-automation/ | Chrome DevTools browser automation |
| claude-code-plugin-builder | claude-code-plugin-builder/ | Build Claude Code plugins |
| client-linkedin | client-linkedin/ | LinkedIn client research |
| client-personal-intel | client-personal-intel/ | Personal intelligence gathering |
| client-research | client-research/ | Client research workflows |
| consulting-admin | consulting-admin/ | Consulting administration |
| daily-lesson | daily-lesson/ | Daily TA lesson curriculum |
| dispatch | dispatch/ | Agent dispatch system |
| domain-discovery | domain-discovery/ | GitHub repo domain scanning |
| expert-scheduler | expert-scheduler/ | Expert system job scheduling |
| gmail-inbox-monitor | gmail-inbox-monitor/ | Gmail monitoring and alerting |
| google-workspace | google-workspace/ | Google Workspace integration |
| graphiti | graphiti/ | Knowledge graph management |
| healthcheck | healthcheck/ | System health checking |
| issue-hunter | issue-hunter/ | GitHub issue discovery |
| linkedin-job-applier | linkedin-job-applier/ | LinkedIn job application automation |
| linkedin-outbound-pitch | linkedin-outbound-pitch/ | LinkedIn outbound DM pitching |
| mac-mini-login | mac-mini-login/ | Mac Mini access reference |
| meridian | meridian/ | Meridian proxy management |
| node-connect | node-connect/ | OpenClaw node connection |
| ob-wiki | ob-wiki/ | Obsidian wiki management |
| obsidian-sync | obsidian-sync/ | Obsidian vault synchronization |
| onboarding | onboarding/ | OpenClaw onboarding |
| openai-image-gen | openai-image-gen/ | OpenAI image generation |
| openai-whisper-api | openai-whisper-api/ | Audio transcription |
| position-monitor | position-monitor/ | Hyperliquid position monitoring |
| postmark | postmark/ | Email sending via Postmark |
| sylvan-hills | sylvan-hills/ | Sylvan Hills client workflow |
| trading-morning-brief | trading-morning-brief/ | Morning market brief generation |
| trading-signals | trading-signals/ | Discord signal processing |
| weather | weather/ | Weather forecasts |

## Skill Structure Pattern

Every skill directory contains:
```
skill-name/
├── SKILL.md          # Required — skill definition with frontmatter
├── references/       # Optional — reference docs
├── scripts/          # Optional — executable scripts
└── templates/        # Optional — file templates
```

## SKILL.md Frontmatter Pattern

```yaml
---
name: skill-name
description: "One-line description of what this skill does"
metadata:
  openclaw:
    emoji: "🔧"
    requires:
      anyBins: ["required-cli-tool"]
---
```
