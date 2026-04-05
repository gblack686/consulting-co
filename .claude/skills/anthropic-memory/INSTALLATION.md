# Anthropic Memory Tool - Global Installation Guide

## 📍 Current Status

Right now, this skill is **local** to the `consulting-co` project only. To make it work **globally** across all Claude Code sessions, follow these steps.

---

## 🌍 Make It Global (Option 1: Copy to Global Directory)

### Step 1: Copy Skill to Global Location

```bash
# Create global skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Copy the entire skill directory
cp -r .claude/skills/anthropic-memory ~/.claude/skills/anthropic-memory

# Verify it copied
ls ~/.claude/skills/anthropic-memory
```

**Windows (PowerShell):**
```powershell
# Create global skills directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"

# Copy the skill
Copy-Item -Recurse -Force .claude\skills\anthropic-memory "$env:USERPROFILE\.claude\skills\anthropic-memory"

# Verify
dir "$env:USERPROFILE\.claude\skills\anthropic-memory"
```

### Step 2: Copy Stop Hook to Global Location

```bash
# Create global hooks directory
mkdir -p ~/.claude/hooks

# Copy the hook
cp .claude/hooks/memory_ingest_hook.py ~/.claude/hooks/memory_ingest_hook.py

# Make it executable (Linux/Mac)
chmod +x ~/.claude/hooks/memory_ingest_hook.py

# Verify
ls -l ~/.claude/hooks/memory_ingest_hook.py
```

**Windows (PowerShell):**
```powershell
# Create global hooks directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\hooks"

# Copy the hook
Copy-Item -Force .claude\hooks\memory_ingest_hook.py "$env:USERPROFILE\.claude\hooks\memory_ingest_hook.py"

# Verify
dir "$env:USERPROFILE\.claude\hooks\memory_ingest_hook.py"
```

### Step 3: Create Global Memories Directory

```bash
# Create global memories directory structure
mkdir -p ~/.claude/memories/sessions
mkdir -p ~/.claude/memories/patterns
mkdir -p ~/.claude/memories/entities

# Verify
ls -la ~/.claude/memories/
```

**Windows (PowerShell):**
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\memories\sessions"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\memories\patterns"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\memories\entities"

# Verify
dir "$env:USERPROFILE\.claude\memories"
```

### Step 4: Update Global Config

Edit `~/.claude/skills/anthropic-memory/config/memory-config.yaml`:

```yaml
# Update paths to use global directory
memory_base_path: ~/.claude/memories  # Changed from .claude/memories
obsidian_vault_path: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation
```

**Windows:** Use full path:
```yaml
memory_base_path: C:/Users/gblac/.claude/memories
```

### Step 5: Enable Global Stop Hook

Edit or create `~/.claude/settings.json` (global settings):

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run ~/.claude/hooks/memory_ingest_hook.py",
        "timeout": 15
      }
    ]
  }
}
```

**Windows:**
```json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run C:/Users/gblac/.claude/hooks/memory_ingest_hook.py",
        "timeout": 15
      }
    ]
  }
}
```

---

## 🔗 Alternative: Symlink (Option 2)

Instead of copying, create symlinks to keep everything in sync:

```bash
# Link skill directory
ln -s $(pwd)/.claude/skills/anthropic-memory ~/.claude/skills/anthropic-memory

# Link hook
ln -s $(pwd)/.claude/hooks/memory_ingest_hook.py ~/.claude/hooks/memory_ingest_hook.py

# Link memories directory
ln -s $(pwd)/.claude/memories ~/.claude/memories
```

**Windows (requires admin PowerShell):**
```powershell
# Enable Developer Mode or run as Administrator
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\anthropic-memory" -Target "$(Get-Location)\.claude\skills\anthropic-memory"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\hooks\memory_ingest_hook.py" -Target "$(Get-Location)\.claude\hooks\memory_ingest_hook.py"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\memories" -Target "$(Get-Location)\.claude\memories"
```

---

## ✅ Verify Installation

### Test 1: Check Files Exist

```bash
# Check skill exists globally
ls ~/.claude/skills/anthropic-memory/skill.md

# Check hook exists globally
ls ~/.claude/hooks/memory_ingest_hook.py

# Check memories directory exists
ls ~/.claude/memories/
```

### Test 2: Test Hook Manually

```bash
# Set required environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Run hook manually (should fail gracefully if no recent session)
uv run ~/.claude/hooks/memory_ingest_hook.py
```

Expected output:
```
Memory ingestion hook started
Found latest transcript: /home/user/.claude/projects/.../....jsonl
Processing session: abc12345
Extracting entities from transcript...
```

### Test 3: Test Memory Executor

```bash
# Test creating a memory
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py create "test/sample.md" "This is a test memory"

# Test listing memories
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py list

# Test searching memories
uv run ~/.claude/skills/anthropic-memory/scripts/memory_executor.py search "test"
```

### Test 4: Run a Real Claude Session

```bash
# Open a new terminal
# Start Claude Code in any directory
cd ~/Desktop/test-project
claude

# Have a conversation, use some tools
> Help me create a simple Python script

# Exit the session (Ctrl+C or type "exit")
# The Stop hook should run automatically

# Check if memory was created
ls ~/.claude/memories/sessions/
cat ~/.claude/memories/sessions/$(ls -t ~/.claude/memories/sessions/ | head -1)
```

---

## 🧪 Automated Test Suite

Run the automated tests:

```bash
# Run test suite
uv run ~/.claude/skills/anthropic-memory/tests/test_memory_system.py
```

Expected output:
```
✅ Test 1: Memory Executor - create_memory: PASSED
✅ Test 2: Memory Executor - view_memory: PASSED
✅ Test 3: Memory Executor - list_memories: PASSED
✅ Test 4: Memory Executor - search_memories: PASSED
✅ Test 5: Entity Extractor - extract_entities: PASSED
✅ Test 6: Stop Hook - find_transcript: PASSED
✅ Test 7: Stop Hook - full_integration: PASSED

All tests passed! Memory system is working correctly.
```

---

## 📊 Verify It's Working

After installation, every Claude Code session should:

1. **On Session End** → Stop hook runs automatically
2. **Hook Extracts** → Entities from conversation
3. **Hook Creates** → Session summary file
4. **Hook Updates** → Entity indices
5. **Hook Rebuilds** → Master index

Check the results:

```bash
# View latest session memory
ls -lt ~/.claude/memories/sessions/ | head -1

# View entity indices
cat ~/.claude/memories/entities/files.md
cat ~/.claude/memories/entities/technologies.md

# View master index
cat ~/.claude/memories/index.md
```

---

## 🔍 Troubleshooting

### Hook Not Running?

**Check global settings:**
```bash
cat ~/.claude/settings.json
```

Should contain:
```json
{
  "hooks": {
    "Stop": [...]
  }
}
```

**Check hook is executable (Linux/Mac):**
```bash
chmod +x ~/.claude/hooks/memory_ingest_hook.py
```

### No Memories Created?

**Check API key:**
```bash
echo $ANTHROPIC_API_KEY
```

**Check logs:**
```bash
cat ~/.claude/logs/memory.log
```

**Run hook manually:**
```bash
uv run ~/.claude/hooks/memory_ingest_hook.py
```

### Permission Errors?

**Linux/Mac:**
```bash
chmod -R 755 ~/.claude/skills/anthropic-memory
chmod -R 755 ~/.claude/hooks
chmod -R 755 ~/.claude/memories
```

**Windows:** Run PowerShell as Administrator

### Import Errors?

**Install dependencies:**
```bash
pip install anthropic python-frontmatter pyyaml
```

---

## 🗑️ Uninstall

To remove the global skill:

```bash
# Remove skill
rm -rf ~/.claude/skills/anthropic-memory

# Remove hook
rm ~/.claude/hooks/memory_ingest_hook.py

# Remove memories (optional - this deletes your data!)
rm -rf ~/.claude/memories

# Remove from settings
# Edit ~/.claude/settings.json and remove the Stop hook
```

---

## 📝 Summary

**Location of Files After Global Install:**

```
~/.claude/
├── skills/
│   └── anthropic-memory/
│       ├── skill.md
│       ├── README.md
│       ├── config/memory-config.yaml
│       └── scripts/
│           ├── memory_executor.py
│           └── entity_extractor.py
├── hooks/
│   └── memory_ingest_hook.py
├── memories/
│   ├── sessions/
│   ├── patterns/
│   ├── entities/
│   └── index.md
└── settings.json  # Contains Stop hook config
```

**How to Verify It's Global:**

Open Claude Code in **any directory**, run a session, and check:
```bash
ls ~/.claude/memories/sessions/
```

You should see a new session file created!

---

## 🎯 Quick Install Script

Copy and paste this entire block:

```bash
#!/bin/bash
# Quick install script for Anthropic Memory Tool

echo "Installing Anthropic Memory Tool globally..."

# Create directories
mkdir -p ~/.claude/skills ~/.claude/hooks ~/.claude/memories/{sessions,patterns,entities}

# Copy files
cp -r .claude/skills/anthropic-memory ~/.claude/skills/
cp .claude/hooks/memory_ingest_hook.py ~/.claude/hooks/

# Make hook executable
chmod +x ~/.claude/hooks/memory_ingest_hook.py

# Update config for global paths
sed -i 's|memory_base_path: .claude/memories|memory_base_path: ~/.claude/memories|' ~/.claude/skills/anthropic-memory/config/memory-config.yaml

# Add Stop hook to global settings
cat << 'EOF' > ~/.claude/settings.json
{
  "hooks": {
    "Stop": [
      {
        "command": "uv run ~/.claude/hooks/memory_ingest_hook.py",
        "timeout": 15
      }
    ]
  }
}
EOF

echo "✅ Installation complete!"
echo "Test it: Run a Claude Code session in any directory, then check ~/.claude/memories/sessions/"
```

Save as `install_global.sh` and run:
```bash
chmod +x install_global.sh
./install_global.sh
```

---

**Status:** Ready for global installation! 🚀
