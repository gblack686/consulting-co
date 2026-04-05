# META-1: Obsidian Sync Skill — Build Plan
**Date:** 2026-03-18
**Build location:** `.claude/skills/consulting-intake/templates/skills/obsidian-sync/`

---

## What to Build

A universal OpenClaw skill that logs meaningful agent events to the Obsidian vault. Ships with every client workspace via the consulting-intake pipeline.

---

## Files to Create

```
templates/skills/obsidian-sync/
└── SKILL.md
references/obsidian-integration.md
```

---

## SKILL.md Spec

**Trigger:** Sub-agent pattern — main agent fires `sync-obsidian` after key events. NOT called on every message.

**Trigger events:**
- File created or modified in workspace
- Cron job completes
- Weekly/daily summary generated
- Error or failure logged
- New skill deployed
- Domain updated

**What it writes:**
- Vault path: `GBAutomation Clients / {client_name} / Agent Log / YYYY-MM-DD.md`
- Append-mode: multiple events per day append to the daily file
- Frontmatter: `date`, `agent`, `event_type`, `summary`, `linked_files`

**Note format:**
```markdown
---
date: YYYY-MM-DD
agent: {agent_name}
event_type: file_created | cron_complete | summary | error | skill_deployed
---

## HH:MM — {event_type}
{summary}

**Files:** {linked_file_paths}
```

**Implementation options (in priority order):**
1. Obsidian Local REST Plugin (`http://localhost:27123`) — POST to `/vault/{path}`
2. Direct file write if vault is on local disk (Windows path: `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/`)
3. If neither available: log to `workspace/obsidian-queue.md` for manual sync

**Workspace placeholder:** `{obsidian_vault_path}` — filled at deploy time per client.

---

## references/obsidian-integration.md Spec

Document:
- Obsidian Local REST Plugin setup (install → enable → get API key)
- Vault folder structure for GBAutomation clients
- Frontmatter schema for agent log notes
- Example cron entry that fires this skill
- How to verify sync is working
- Link to existing `obsidian-agent-archiver` skill as reference

---

## Acceptance Criteria

- [ ] SKILL.md passes `skill-format-spec.md` validation
- [ ] Works with Obsidian Local REST Plugin (port 27123)
- [ ] Falls back gracefully if Obsidian is unreachable
- [ ] Appends (not overwrites) daily log file
- [ ] `references/obsidian-integration.md` documents setup steps
- [ ] Referenced in `SKILL.md` pipeline table (Step 2b)
- [ ] Tested: run the skill, verify note appears in vault

---

## Prompt for OpenClaw

> "Build the Obsidian Sync skill from the spec at `specs/meta1-obsidian-sync-plan.md`. Create `templates/skills/obsidian-sync/SKILL.md` and `references/obsidian-integration.md`. Use the existing `obsidian-agent-archiver` skill in `.claude/skills/obsidian-agent-archiver/` as a reference. Follow the pattern in `templates/skills/setup-openclaw/SKILL.md` for SKILL.md structure."
