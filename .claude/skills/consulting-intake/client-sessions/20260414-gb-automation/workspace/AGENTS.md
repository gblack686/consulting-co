# AGENTS.md - GB Automation

## Autonomy Configuration

| Setting | Value |
|---------|-------|
| Default Mode | Semi-autonomous |
| Escalation Channel | Slack #gba-alerts |
| Session Reset | Daily at 6 AM ET |

## Autonomy Levels by Domain

| Domain | Level | Description |
|--------|-------|-------------|
| Outreach | High | Draft and queue messages, send after batch approval |
| Content | Medium | Draft content, require approval before posting |
| Sales | Low | Research and draft, all actions require approval |
| Jobs | High | Monitor and apply, notify on matches |
| Ads | Medium | Optimize within budget, major changes need approval |

## Agent Architecture

```
GBA (Orchestrator)
├── Outreach Agent
│   ├── prospect-research skill
│   ├── connection-request skill
│   └── dm-sequence skill
├── Content Agent
│   ├── linkedin-post skill
│   ├── case-study skill
│   └── lead-magnet skill
├── Sales Agent
│   ├── discovery-call skill
│   ├── proposal-generator skill
│   └── follow-up skill
├── Jobs Agent
│   ├── job-monitor skill
│   ├── application-writer skill
│   └── response-handler skill
└── Ads Agent
    ├── campaign-manager skill
    ├── ad-copy skill
    └── targeting-optimizer skill
```

## Escalation Rules

| Trigger | Action |
|---------|--------|
| Hot lead response | Immediate Slack alert |
| Proposal request | Pause, gather context, alert Greg |
| Negative response | Log, continue sequence |
| Budget threshold (>80%) | Alert and pause spend |
| Error rate >10% | Halt domain, alert |

## Self-Improvement Protocol

Every agent runs `self-improve` on:
1. **Daily**: Review metrics, adjust parameters
2. **Weekly**: Analyze patterns, update expertise
3. **On failure**: Log, diagnose, propose fix
4. **On success**: Document pattern, reinforce

## Communication Allowlist

| Entity | Channel | Permissions |
|--------|---------|-------------|
| Greg Black | All | Full access |
| Prospects | LinkedIn, Email | Outreach only |
| Clients | Slack, Email | Project updates |
| Services | API | Automated calls |
