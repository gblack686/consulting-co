# Obsidian Integration - Quick Start Guide

> Get your Obsidian vault integrated with Claude Code in 10 minutes

## Prerequisites

- [ ] Obsidian installed with a vault created
- [ ] Node.js 18+ installed
- [ ] Claude Code CLI working

## Step 1: Install Dependencies (2 min)

```bash
cd .claude/skills/obsidian-vault
npm install
```

## Step 2: Configure Vault Path (1 min)

Edit `.claude/skills/obsidian-vault/config/vault-settings.json`:

```json
{
  "vaultPath": "C:/Users/YOUR_USER/Documents/Obsidian/YourVault",
  "projectFolder": "Projects/consulting-co"
}
```

**Common vault locations:**
- **Windows:** `C:/Users/[username]/Documents/Obsidian/[vault-name]`
- **Mac:** `/Users/[username]/Documents/Obsidian/[vault-name]`
- **Linux:** `/home/[username]/Documents/Obsidian/[vault-name]`

**Tip:** Use forward slashes (`/`) even on Windows for JSON compatibility.

## Step 3: Initialize Vault Structure (1 min)

```bash
node .claude/skills/obsidian-vault/scripts/init-vault.js
```

This creates in your Obsidian vault:
```
Projects/
  consulting-co/
    Daily Notes/
    Decisions/
    Learnings/
    Tasks/
    Meetings/
    Templates/
```

## Step 4: Test Commands (3 min)

Start a Claude Code session:

```bash
claude
```

Test each command:

```bash
# 1. Create daily note
/daily-note

# 2. Create a test note
/note-create "Test Note" learning

# 3. Search for the note
/note-search "test"

# 4. Create a decision record
/decision-log "Test ADR"
```

## Step 5: Verify in Obsidian (2 min)

Open Obsidian and navigate to:
- `Projects/consulting-co/Daily Notes/` - See today's note
- `Projects/consulting-co/Learnings/` - See "Test Note"
- `Projects/consulting-co/Decisions/` - See "Test ADR"

All notes should have proper frontmatter and tags!

## Step 6: Enable Hooks (Optional - 1 min)

To automatically create daily notes and sync sessions:

### Windows
Create `.claude/hooks/session-start/obsidian-context-load.bat`:
```batch
@echo off
node .claude/skills/obsidian-vault/scripts/session-start.js
```

### Mac/Linux
Create `.claude/hooks/session-start/obsidian-context-load.sh`:
```bash
#!/bin/bash
node .claude/skills/obsidian-vault/scripts/session-start.js
```

Make executable:
```bash
chmod +x .claude/hooks/session-start/obsidian-context-load.sh
```

## Troubleshooting

### Issue: "Vault path does not exist"
**Fix:** Double-check the `vaultPath` in `vault-settings.json`
- Use absolute path
- Use forward slashes `/` not backslashes `\`
- Verify folder exists in your file system

### Issue: "Cannot find module 'glob'"
**Fix:** Install dependencies
```bash
cd .claude/skills/obsidian-vault
npm install
```

### Issue: "Permission denied"
**Fix:** Check folder permissions
```bash
# Windows (run as Administrator)
icacls "C:/Users/YourUser/Documents/Obsidian" /grant Users:F

# Mac/Linux
chmod -R u+w ~/Documents/Obsidian/YourVault
```

### Issue: Commands not recognized
**Fix:** Restart Claude Code session
```bash
# Exit current session
exit

# Start new session
claude
```

## Next Steps

### Customize Templates
Edit templates in `.claude/skills/obsidian-vault/templates/`:
- `daily-note.md` - Your daily note structure
- `adr.md` - Architecture decision records
- `learning.md` - Learning notes
- `task.md` - Task notes

### Configure Settings
Adjust `.claude/skills/obsidian-vault/config/vault-settings.json`:
- Enable/disable auto-sync
- Change folder names
- Adjust search settings
- Set tag preferences

### Set Up Agents
The integration includes two agents:

**@knowledge-curator** - Extracts learnings from sessions
```bash
# Manually trigger
@knowledge-curator extract learnings from this session
```

**@obsidian-organizer** - Organizes vault structure
```bash
# Manually trigger
@obsidian-organizer organize my vault
```

### Add More Commands
Create custom commands in `.claude/commands/`:
- `/weekly-review.md` - Weekly retrospective
- `/meeting-note.md` - Meeting notes
- `/sprint-planning.md` - Sprint planning notes

## Daily Workflow Example

```bash
# Morning
claude
# Auto-creates daily note
# Shows pending tasks

# During work
/decision-log "Use Redis for caching"
# Logs architectural decision

# Research something
/note-search "how we handled authentication"
# Finds past solutions

# Load context
/context-load "ADR-005-Auth-Strategy"
# Brings decision into conversation

# End of day
stop
# Session logged to daily note
# Learnings extracted automatically
```

## Integration with Existing .claude Setup

This integration works alongside:
- **revstar-quickstart-workflow** skill
- **aws-cdk-diagram** skill
- **git-wizard** skill
- Existing hooks and commands

**No conflicts!** All Obsidian commands are prefixed with `/note-*` or `/vault-*`

## Advanced: MCP Server (Future)

For bidirectional real-time sync, you can implement the MCP server:
1. See `.claude/OBSIDIAN_INTEGRATION_PLAN.md` - Option 2
2. Requires MCP server setup
3. Enables Obsidian → Claude Code sync
4. Advanced graph queries

**For now:** Skill-based integration (Option 1) is fully functional!

## Resources

- **Full Plan:** `.claude/OBSIDIAN_INTEGRATION_PLAN.md`
- **Skill Docs:** `.claude/skills/obsidian-vault/SKILL.md`
- **README:** `.claude/skills/obsidian-vault/README.md`
- **GitHub Repo:** https://github.com/m-rgba/obsidian-ai-agent

## Support

If you encounter issues:
1. Check logs: `.claude/logs/obsidian-operations.log`
2. Review configuration: `vault-settings.json`
3. Verify Node.js version: `node --version` (should be 18+)
4. Test vault path: Navigate to it in file explorer

## Quick Reference Card

```
COMMANDS
--------
/note-create [title] [category]  → Create note
/note-search [query]              → Search vault
/decision-log [title]             → Create ADR
/daily-note                       → Today's note
/vault-sync                       → Manual sync
/context-load [note]              → Load to context

CATEGORIES
----------
daily          → Daily Notes/
architecture   → Decisions/Architecture/
learning       → Learnings/
task           → Tasks/
meeting        → Meetings/

SEARCH SYNTAX
-------------
keyword                           → Basic search
#tag                              → Tag search
date:2025-11-13                   → Date search
folder:Decisions                  → Folder search
#tag date:last-7-days keyword     → Combined

AGENTS
------
@knowledge-curator                → Extract learnings
@obsidian-organizer               → Organize vault
```

## Configuration Files Location

```
.claude/
├── OBSIDIAN_INTEGRATION_PLAN.md       ← Full integration plan
├── OBSIDIAN_QUICK_START.md            ← This file
├── skills/obsidian-vault/
│   ├── SKILL.md                       ← Skill definition
│   ├── README.md                      ← Detailed docs
│   ├── package.json                   ← Dependencies
│   ├── config/
│   │   └── vault-settings.json        ← EDIT THIS FIRST
│   ├── templates/                     ← Customize these
│   └── scripts/                       ← Implementation
└── commands/
    ├── note-create.md                 ← Command definitions
    └── note-search.md
```

---

**You're ready to go! Start with `/daily-note` in your next Claude Code session.**

**Version:** 1.0
**Last Updated:** November 13, 2025
