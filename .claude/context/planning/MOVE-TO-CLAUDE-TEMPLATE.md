# Migration Plan: Move to claude-template Repo

**Date:** 2025-12-01
**Decision:** Use existing `claude-template` repo instead of `consulting-co`

---

## ✅ Why This Makes Perfect Sense

### 1. **You Already Have It**
- `github.com/gblack686/claude-template` exists
- Last updated: 2025-11-29 (3 days ago - very recent!)
- Already contains the working pattern (hooks/, observability/, etc.)
- **This IS the `.claude` directory** - not a wrapper repo

### 2. **Clean Separation**
- `claude-template/` = Your workbench/template
- `consulting-co/` = Actual consulting deliverables
- No mixing of template code with client work

### 3. **Better Story**
"Here's my claude-template repo - my production-ready observability pattern. I clone this for new projects."

### 4. **Already on GitHub**
- Public repo ready to showcase
- Can link from LinkedIn, portfolio, etc.
- Easy to share with clients

---

## 📋 Migration Steps

### Step 1: Copy Essential Planning Docs (5 min)

**From:** `consulting-co/.claude/context/planning/`
**To:** `claude-template/context/planning/`

```bash
cd ~/OneDrive/Desktop

# Copy planning docs
cp consulting-co/.claude/context/planning/TONIGHT-PLAN.md claude-template/context/planning/
cp consulting-co/.claude/context/planning/TONIGHT-SUMMARY.md claude-template/context/planning/
cp consulting-co/.claude/context/planning/UPDATED-ARCHITECTURE-PLAN.md claude-template/context/planning/
cp consulting-co/.claude/context/planning/OBSIDIAN-FOLDER-TREE-V3.md claude-template/context/planning/
cp consulting-co/.claude/context/planning/SUMMARY.md claude-template/context/planning/
```

### Step 2: Copy Review Script (1 min)

```bash
cp consulting-co/.claude/scripts/review_neo4j_schema.py claude-template/scripts/
```

### Step 3: Update Obsidian to Point to claude-template (2 min)

```bash
cd ~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects

# Rename the directory
mv consulting-co claude-template

# Update overview.md
# Change: Repository: C:/.../consulting-co/
# To:     Repository: C:/.../claude-template/
```

### Step 4: Git Commit & Push (2 min)

```bash
cd ~/OneDrive/Desktop/claude-template

git add context/planning/*.md
git add scripts/review_neo4j_schema.py
git commit -m "Add planning docs and Neo4j review script

- TONIGHT-PLAN.md - 2-hour Obsidian setup plan
- TONIGHT-SUMMARY.md - Summary of work completed
- UPDATED-ARCHITECTURE-PLAN.md - No-Langfuse architecture
- OBSIDIAN-FOLDER-TREE-V3.md - Complete Obsidian structure
- SUMMARY.md - Quick reference
- review_neo4j_schema.py - Neo4j schema review script
"

git push origin main
```

### Step 5: Update README.md (5 min)

```bash
cd ~/OneDrive/Desktop/claude-template
```

Update `README.md` to reflect it's now **doc-claude-workbench**:

```markdown
# Claude Code Workbench (claude-template)

Production-ready agentic development workbench with observability, knowledge graphs, and auto-documentation.

## Overview

This is my personal Claude Code template that I use daily. It provides:

✅ **SQLite Observability** - Lightweight event storage (vs 4GB Langfuse)
✅ **Haiku Enrichment** - Real-time analysis (~$0.0003/event, 66% cache hit)
✅ **Neo4j Knowledge Graph** - Entity extraction via Graphiti
✅ **Obsidian Export** - Auto-generated markdown notes
✅ **Multi-Agent Support** - Admin Agent, Code-Fix Agent
✅ **Cost Efficient** - ~$10-20/month total

**The Pattern:**
```
Hooks → SQLite → Haiku Enrichment → Graphiti/Neo4j → Obsidian
```

## Quick Start

[Keep existing Quick Start section]

## Documentation

See `context/planning/` for:
- Architecture plan
- Obsidian structure
- Setup guides
- Implementation roadmap

## Use Cases

- Personal workbench for daily development
- Template for client projects
- Portfolio showcase
- Consulting demo

## Monthly Cost

~$10-20 (OpenAI for Graphiti + Haiku for enrichment)

vs. Langfuse alternative: $50+ with 4GB Docker overhead

## License

MIT
```

### Step 6: Create Project-Specific Settings (Optional)

If you want `consulting-co` to still work:

```bash
cd ~/OneDrive/Desktop/consulting-co

# Option A: Symlink to claude-template
ln -s ../claude-template/.claude .claude

# Option B: Just delete old .claude
rm -rf .claude

# consulting-co becomes just deliverables:
# - proposals/
# - client work/
# - etc.
```

---

## 📁 New Directory Structure

### On Disk
```
~/OneDrive/Desktop/
├── claude-template/              # ⭐ Your workbench repo
│   ├── hooks/
│   ├── agents/
│   ├── skills/
│   ├── commands/
│   ├── observability/
│   ├── obsidian/
│   ├── context/
│   │   └── planning/             # Planning docs
│   ├── scripts/                  # Review scripts
│   └── README.md                 # Updated description
│
├── consulting-co/                # Actual consulting work
│   ├── proposals/
│   ├── client-projects/
│   └── specs/
│
└── obsidian/
    └── Gbautomation/
        └── claude/
            ├── global/           # Shared patterns
            └── projects/
                └── claude-template/  # Renamed from consulting-co
```

### On GitHub
```
github.com/gblack686/
├── claude-template/              # ⭐ Public showcase
├── quickstart-nexus/             # RevStar work (private?)
└── consulting-co/                # Private? Or don't push
```

---

## ✅ Advantages of This Approach

1. **Use Existing Repo**
   - Already on GitHub
   - Already has the pattern
   - Just needs planning docs added

2. **Clean Separation**
   - claude-template = workbench/template
   - consulting-co = deliverables only

3. **Better Branding**
   - "claude-template" is clear, professional
   - Easy to explain: "This is my template, I clone it for projects"

4. **Reusable**
   ```bash
   # Start new project
   git clone claude-template client-project-1
   cd client-project-1
   # Customize for client
   ```

5. **Portfolio Ready**
   - Link from LinkedIn
   - Show in interviews
   - Include in proposals

---

## 🎯 After Migration

### Update Plans
In `claude-template/context/planning/`, update all references:
- Change `consulting-co` → `claude-template`
- Update repository paths
- Update Obsidian paths

### Update Obsidian
In `~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/claude-template/`:
- Update `overview.md` with new repo path
- Update all `.claude-mirror/` references
- Update `docs/neo4j-status.md` with correct paths

### Continue Week 1
Pick up where we left off:
- [ ] Copy hooks (already there!)
- [ ] Enable Graphiti
- [ ] Test end-to-end
- [ ] Record first Loom

---

## 📊 Timeline

**Tonight (15 minutes):**
1. Copy planning docs → claude-template
2. Update Obsidian directory name
3. Update README.md
4. Git commit & push

**Tomorrow:**
Continue Week 1 implementation in claude-template

---

## 🔄 Rollback Plan (if needed)

If you want to go back:
```bash
cd ~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects
mv claude-template consulting-co
# Restore original paths
```

---

## ✅ Decision

**Recommended:** ✅ Migrate to `claude-template`

**Why:**
- Already exists
- Better name
- Clean separation
- Portfolio ready
- Reusable template

**Action:** Execute Step 1-6 above (~15 minutes total)

---

**Ready to execute?** Let's move the planning docs and continue in `claude-template`! 🚀
