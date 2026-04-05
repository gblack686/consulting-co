# Anthropic Memory Tool - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Globally (2 minutes)

**Windows:**
```cmd
cd C:\Users\gblac\OneDrive\Desktop\consulting-co
install_global.bat
```

**Mac/Linux:**
```bash
cd ~/Desktop/consulting-co
chmod +x .claude/skills/anthropic-memory/install_global.sh
./install_global.sh
```

### Step 2: Verify Installation (30 seconds)

```bash
# Run verification script
uv run ~/.claude/skills/anthropic-memory/verify_installation.py

# Or on Windows:
uv run %USERPROFILE%\.claude\skills\anthropic-memory\verify_installation.py
```

Expected output:
```
✅ All checks passed! Installation is complete.
```

### Step 3: Test It! (1 minute)

Open a **NEW** terminal in **any directory**:

```bash
cd ~/Desktop/test-project  # Any directory!
claude

# Have a short conversation
> Help me create a simple hello.py script that prints "Hello World"

# Exit the session
Ctrl+C
```

**Check the results:**
```bash
# List session memories
ls ~/.claude/memories/sessions/

# View the latest session
cat ~/.claude/memories/sessions/$(ls -t ~/.claude/memories/sessions/ | head -1)
```

You should see a markdown file with:
- Session summary
- Files created (hello.py)
- Technologies used (Python)
- Tools used (Write)
- Key learnings

---

## 📊 What Happens Automatically

Every time you end a Claude Code session:

```
1. Stop Hook Runs (2-5 seconds)
   └─> Finds your conversation transcript

2. Claude Haiku Analyzes It
   └─> Extracts entities (files, tech, concepts)

3. Creates Session Memory
   └─> Saves to ~/.claude/memories/sessions/YYYY-MM-DD_xxxxxx.md

4. Updates Entity Indices
   └─> Adds to files.md, technologies.md, concepts.md

5. Rebuilds Master Index
   └─> Updates index.md with stats
```

---

## 🎯 Example Session Flow

### You Run:
```bash
cd ~/my-project
claude
> Help me implement JWT authentication in auth.py
```

### Claude Does:
```
- Reads existing code
- Creates auth.py
- Implements JWT logic
- Runs tests
```

### You Exit:
```
Ctrl+C
```

### Memory System Creates:

**File:** `~/.claude/memories/sessions/2026-01-11_f7d072bc.md`
```markdown
---
date: 2026-01-11
session_id: f7d072bc
tags: [authentication, security]
entities:
  files: [auth.py, test_auth.py]
  technologies: [JWT, PyJWT, Python]
  concepts: [Token-based authentication]
---

# Session Summary

Implemented JWT authentication in Python using PyJWT library.

## Files Involved
- **auth.py** (Python) - Authentication middleware
- **test_auth.py** (Python) - Unit tests

## Technologies Used
- **JWT** (library) - Token generation and validation
- **PyJWT** (library) - Python JWT implementation
- **Python** (language)

## Concepts Discussed
- **Token-based authentication** - Using JWT tokens instead of sessions
  - _Why it matters:_ Stateless auth enables horizontal scaling

## Tools Used
- **Read** (2x) - Read existing code
- **Write** (2x) - Create new files
- **Bash** (1x) - Run tests

## Key Learnings
- JWT tokens should expire after reasonable time
  - _Action:_ Implement refresh token rotation
- Use httpOnly cookies for token storage
  - _Action:_ Never store tokens in localStorage
```

---

## 🔍 Search Your Memory

After a few sessions, search across all your memories:

**Using the memory executor:**
```bash
# Search for authentication-related sessions
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py search "authentication"

# List all sessions
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py list sessions

# View a specific session
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py view sessions/2026-01-11_f7d072bc.md

# View master index
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py view index.md
```

**Using grep (quick and dirty):**
```bash
# Find sessions about React
grep -r "React" ~/.claude/memories/sessions/

# Find all files you've worked on
cat ~/.claude/memories/entities/files.md

# Find all technologies you've used
cat ~/.claude/memories/entities/technologies.md
```

---

## 🧪 Run Tests

Verify everything works:

```bash
# Run full test suite
uv run ~/.claude/skills/anthropic-memory/tests/test_memory_system.py
```

Expected output:
```
🧪 Anthropic Memory Tool - Test Suite
============================================================

📋 Running Memory Executor Tests...
✅ Memory Executor - create_memory: PASSED
✅ Memory Executor - view_memory: PASSED
✅ Memory Executor - list_memories: PASSED
✅ Memory Executor - search_memories: PASSED
✅ Security - path_traversal: PASSED
✅ Memory Executor - create_index: PASSED

📋 Running Entity Extractor Tests...
✅ Entity Extractor - extract_entities: PASSED
✅ Entity Extractor - generate_summary: PASSED

============================================================
Test Results: 8/8 passed
============================================================

🎉 All tests passed! Memory system is working correctly.
```

---

## 📁 Where Are My Memories?

All memories are stored in your global Claude directory:

```
~/.claude/memories/
├── sessions/                    # One file per session
│   ├── 2026-01-10_abc12345.md
│   ├── 2026-01-11_def67890.md
│   └── 2026-01-11_f7d072bc.md
├── patterns/                    # Recurring patterns (future)
├── entities/                    # Entity registries
│   ├── files.md                # All files you've worked on
│   ├── technologies.md         # All tech you've used
│   └── concepts.md             # All concepts discussed
└── index.md                    # Master index with stats
```

**Windows:**
```
C:\Users\gblac\.claude\memories\
```

---

## ⚙️ Configuration

Edit `~/.claude/skills/anthropic-memory/config/memory-config.yaml`:

```yaml
# Where to store memories
memory_base_path: ~/.claude/memories

# Where to export to Obsidian (optional)
obsidian_vault_path: ~/Desktop/obsidian/Gbautomation

# Entity extraction
enable_entity_extraction: true
entity_extraction_model: claude-haiku-4  # Fast & cheap!

# Search
search_result_limit: 10
semantic_search_enabled: true
```

---

## 🐛 Troubleshooting

### "Memory not created after session"

1. **Check hook ran:**
   ```bash
   # Look for errors in logs
   cat ~/.claude/logs/memory.log
   ```

2. **Check settings file:**
   ```bash
   cat ~/.claude/settings.json
   # Should have "Stop" hook configured
   ```

3. **Test hook manually:**
   ```bash
   uv run ~/.claude/hooks/memory_ingest_hook.py
   ```

### "Entity extraction failed"

1. **Check API key:**
   ```bash
   echo $ANTHROPIC_API_KEY
   # Should output: sk-ant-...
   ```

2. **Test entity extractor directly:**
   ```bash
   # Create test transcript
   echo "USER: Help with Python\nASSISTANT: Sure!" > test.txt

   # Test extraction
   uv run ~/.claude/skills/anthropic-memory/scripts/entity_extractor.py test.txt
   ```

### "Permission denied"

**Linux/Mac:**
```bash
chmod +x ~/.claude/hooks/memory_ingest_hook.py
chmod -R 755 ~/.claude/skills/anthropic-memory
```

**Windows:** Run PowerShell as Administrator

---

## 📚 Learn More

- **Full Documentation:** `README.md`
- **Installation Details:** `INSTALLATION.md`
- **Stop Hook Flow:** `STOP_HOOK_FLOW.md`
- **Run Tests:** `tests/test_memory_system.py`
- **Verify Install:** `verify_installation.py`

---

## 🎉 You're Ready!

1. ✅ Skill installed globally
2. ✅ Stop hook configured
3. ✅ Tests passing

**Now just use Claude Code normally** - every session will be automatically saved to your memory system!

No commands to remember. No manual steps. Just chat with Claude, and your knowledge accumulates over time. 🚀

---

## 💡 Pro Tips

**Tip 1: Search Before Starting**
```bash
# Before starting a new feature
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py search "authentication"
# Review what you did last time
```

**Tip 2: Export to Obsidian**
```yaml
# In config/memory-config.yaml
enable_obsidian_export: true
obsidian_vault_path: ~/path/to/vault
```

**Tip 3: Use Tags**
The system auto-generates tags from your conversations. You can manually add them too by editing session files.

**Tip 4: Pattern Detection**
After 3+ similar sessions, patterns will be automatically detected and saved to `patterns/`.

---

**Happy coding! 🎯**
