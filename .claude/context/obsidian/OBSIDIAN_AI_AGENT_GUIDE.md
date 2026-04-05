# Obsidian AI Agent Plugin Integration Guide

*Interactive Claude Code directly in your knowledge base*

---

## What It Is

The Obsidian AI Agent plugin enables **Claude Code chat directly within Obsidian**, allowing you to interact with your vault knowledge base without leaving the app.

**Repository**: https://github.com/m-rgba/obsidian-ai-agent
**Status**: Active development
**Location in consulting-co**: `./obsidian-ai-agent/`

---

## How to Use on Desktop

### Opening the Chat
- Enable plugin in Obsidian Community Plugins settings
- Chat panel appears in right sidebar
- Click anytime to start chatting with Claude Code

### Typical Workflow
```
1. Open a session note in main view
2. Click chat panel on right
3. Ask: "Summarize this session"
   ↓
4. AI reads the note in real-time
5. AI can: create new notes, edit current note, link entities
6. Changes appear instantly in vault
```

### Example Interactions
```
You: "Create a summary table for all sessions this week"
AI: Creates new note with formatted table

You: "Add performance metrics to this section"
AI: Modifies the open note in real-time

You: "Link related entities"
AI: Creates backlinks to related sessions/files
```

---

## Mobile Support

**❌ NOT AVAILABLE**

### Current Limitations
- **Desktop only** - Requires Claude Code CLI (command-line)
- **No iOS/Android support** - Plugin incompatible with mobile Obsidian
- **WSL required on Windows** - Native Windows support being tested
- **Elevated permissions** - Security model requires full access

### Mobile Workarounds

**Option 1: Read-Only Obsidian Mobile**
- AI generates docs on desktop
- Read/annotate on mobile
- Sync back via iCloud/OneDrive

**Option 2: Observability Dashboard**
- Access web dashboard at http://localhost:5173 on mobile (via VPN)
- Browse sessions and metrics
- Read-only interface

**Option 3: Static Exports**
- Generate PDF/HTML of daily summaries on desktop
- Share with team
- Access anywhere

---

## Setup Checklist

### Desktop
- [ ] Clone repo: Done (`./obsidian-ai-agent/`)
- [ ] Install Node.js and Claude Code CLI
- [ ] Open Obsidian and point to `./observability/notes/` vault
- [ ] Enable `obsidian-ai-agent` in Community Plugins
- [ ] Backup vault before first use

### Mobile
- [ ] Install Obsidian app
- [ ] Point to same vault (via sync service)
- [ ] Use read-only mode
- [ ] Or access observability dashboard via web

---

## Architecture in consulting-co

### Data Flow
```
Claude Code Session (desktop)
    ↓
Stop Hook fires
    ↓
obsidian_exporter.py → Neo4j → ./observability/notes/
    ↓
Open Obsidian
    ↓
Obsidian AI Agent (chat in sidebar)
    ↓
AI modifies vault notes
    ↓
(Optional) Sync back to Neo4j
```

### Integration Points
- **Input**: Generated session notes from `obsidian_exporter.py`
- **Processing**: Claude Code AI (via plugin)
- **Output**: Modified notes in vault
- **Sync**: Back to Neo4j via potential bidirectional sync

---

## Future Integration (Not Yet Implemented)

```python
# .claude/hooks/sync_obsidian_edits.py
"""
When Obsidian AI Agent modifies notes,
capture those edits and update Neo4j
"""
# TODO: Implement when ready
```

---

## Permissions & Security

The plugin currently uses elevated permissions:
```
--permission-mode bypassPermissions
--dangerously-skip-permissions
```

**Recommendation**:
- Use only in trusted vaults
- Backup regularly
- Fine-grained controls planned for future release

---

## Status

**Integrated**: ✅ Cloned to `./obsidian-ai-agent/`
**Activated**: ⏳ Pending manual installation
**Documentation**: ✅ This guide
**Mobile Support**: ❌ Not available
**Bidirectional Sync**: ⏳ Future implementation

---

**Next Steps**:
1. Install Node.js and Claude Code CLI locally
2. Open Obsidian → install plugin from community
3. Start chatting with your session notes
