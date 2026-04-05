# Stop Hook Flow - Anthropic Memory Tool

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER ENDS CLAUDE SESSION                         │
│                         (Ctrl+C or exit)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  Claude Code Stop Hook Triggered                    │
│                                                                     │
│  Reads: .claude/settings.local.json                                │
│  Finds:                                                             │
│    "hooks": {                                                       │
│      "Stop": [                                                      │
│        {                                                            │
│          "command": "uv run .claude/hooks/memory_ingest_hook.py",  │
│          "timeout": 10                                              │
│        }                                                            │
│      ]                                                              │
│    }                                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 1: Find Latest Transcript                         │
│                                                                     │
│  Location: ~/.claude/projects/                                      │
│  Pattern:  {project-id}/{project-id}.jsonl                         │
│                                                                     │
│  Example:                                                           │
│    ~/.claude/projects/f7d072bc-9196-49fc-807f-c10b617f567b/        │
│                       f7d072bc-9196-49fc-807f-c10b617f567b.jsonl   │
│                                                                     │
│  Action: Find most recently modified .jsonl file                   │
│  Result: transcript_path, session_id (first 8 chars: "f7d072bc")   │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 2: Parse JSONL Transcript                         │
│                                                                     │
│  Read file line by line:                                            │
│    {"role": "user", "content": "Help me implement auth"}           │
│    {"role": "assistant", "content": [{"type": "text", ...}]}       │
│    {"role": "assistant", "content": [{"type": "tool_use", ...}]}   │
│    ...                                                              │
│                                                                     │
│  Convert to readable format:                                        │
│    USER: Help me implement auth                                     │
│    ASSISTANT: I'll help you implement authentication...             │
│    [TOOL: Read]                                                     │
│    [TOOL RESULT]                                                    │
│    ASSISTANT: I've read the file...                                 │
│                                                                     │
│  Result: formatted_transcript (string)                              │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 3: Extract Entities Using Claude                       │
│                                                                     │
│  Call Anthropic API:                                                │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Model: claude-haiku-4 (fast & cost-effective)                │ │
│  │ Prompt: "Extract structured entities from this transcript..." │ │
│  │                                                               │ │
│  │ Extract:                                                      │ │
│  │   1. Files (paths, types, descriptions)                      │ │
│  │   2. Technologies (names, categories, versions)              │ │
│  │   3. Concepts (patterns, techniques)                         │ │
│  │   4. Decisions (choices, rationale, alternatives)            │ │
│  │   5. Tools Used (Read, Write, Edit, Bash counts)             │ │
│  │   6. Key Learnings (insights, takeaways)                     │ │
│  │   7. Tags (keywords)                                          │ │
│  │   8. Summary (1-2 sentences)                                  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Result: entities (JSON object)                                     │
│                                                                     │
│  Example Output:                                                    │
│  {                                                                  │
│    "files": [                                                       │
│      {"path": "auth-middleware.ts", "type": "TypeScript"}          │
│    ],                                                               │
│    "technologies": [                                                │
│      {"name": "JWT", "category": "library"}                        │
│    ],                                                               │
│    "concepts": [                                                    │
│      {"name": "Token refresh rotation"}                            │
│    ],                                                               │
│    "tags": ["authentication", "security"],                         │
│    "summary": "Implemented JWT auth with refresh tokens"           │
│  }                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│           STEP 4: Generate Session Summary (Markdown)               │
│                                                                     │
│  Template:                                                          │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ ---                                                           │ │
│  │ date: 2026-01-11                                              │ │
│  │ session_id: f7d072bc                                          │ │
│  │ tags: [authentication, security]                              │ │
│  │ entities:                                                     │ │
│  │   files: [auth-middleware.ts]                                │ │
│  │   technologies: [JWT, OAuth2]                                │ │
│  │ ---                                                           │ │
│  │                                                               │ │
│  │ # Session Summary                                             │ │
│  │                                                               │ │
│  │ Implemented JWT auth with refresh tokens                      │ │
│  │                                                               │ │
│  │ ## Files Involved                                             │ │
│  │ - **auth-middleware.ts** (TypeScript)                         │ │
│  │                                                               │ │
│  │ ## Technologies Used                                          │ │
│  │ - **JWT** (library)                                           │ │
│  │ - **OAuth2** (framework)                                      │ │
│  │                                                               │ │
│  │ ## Tools Used                                                 │ │
│  │ - **Read** (3x) - Read existing code                          │ │
│  │ - **Edit** (2x) - Updated middleware                          │ │
│  │ ...                                                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Result: summary_content (markdown string)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│             STEP 5: Store Session Memory                            │
│                                                                     │
│  Path: .claude/memories/sessions/2026-01-11_f7d072bc.md           │
│                                                                     │
│  Actions:                                                           │
│    1. Create sessions directory if needed                          │
│    2. Write frontmatter + content to file                          │
│    3. Set file permissions                                         │
│                                                                     │
│  File Structure:                                                    │
│  .claude/memories/                                                  │
│  └── sessions/                                                      │
│      ├── 2026-01-10_abc12345.md                                    │
│      ├── 2026-01-11_def67890.md                                    │
│      └── 2026-01-11_f7d072bc.md  ← NEW FILE                        │
│                                                                     │
│  Result: ✅ Session stored                                          │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│          STEP 6: Update Entity Indices (Parallel)                   │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Update           │  │ Update           │  │ Update           │ │
│  │ files.md         │  │ technologies.md  │  │ concepts.md      │ │
│  │                  │  │                  │  │                  │ │
│  │ Read existing    │  │ Read existing    │  │ Read existing    │ │
│  │ Parse entries    │  │ Parse entries    │  │ Parse entries    │ │
│  │ Add new files    │  │ Add new techs    │  │ Add new concepts │ │
│  │ Write updated    │  │ Write updated    │  │ Write updated    │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                     │
│  Location: .claude/memories/entities/                               │
│                                                                     │
│  Example files.md:                                                  │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ # Files Registry                                              │ │
│  │                                                               │ │
│  │ - **app/auth/middleware.ts** (TypeScript) - Auth middleware  │ │
│  │ - **app/auth/routes.py** (Python) - Auth routes              │ │
│  │ - **auth-middleware.ts** (TypeScript) ← NEWLY ADDED           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Result: ✅ Entity indices updated                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 7: Rebuild Master Index                           │
│                                                                     │
│  Scan all directories:                                              │
│    - Count sessions: 15 files                                      │
│    - Count patterns: 3 files                                       │
│    - Count entities: 3 types                                       │
│                                                                     │
│  Generate index.md:                                                 │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ # Memory System Index                                         │ │
│  │                                                               │ │
│  │ Generated: 2026-01-11 15:30:45                                │ │
│  │                                                               │ │
│  │ ## Statistics                                                 │ │
│  │ - Total Sessions: 15                                          │ │
│  │ - Total Patterns: 3                                           │ │
│  │ - Total Entity Types: 3                                       │ │
│  │                                                               │ │
│  │ ## Recent Sessions                                            │ │
│  │ - [[sessions/2026-01-11_f7d072bc.md]] (2026-01-11)          │ │
│  │ - [[sessions/2026-01-11_def67890.md]] (2026-01-11)          │ │
│  │ ...                                                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Path: .claude/memories/index.md                                    │
│  Result: ✅ Master index updated                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    HOOK EXECUTION COMPLETE                          │
│                                                                     │
│  Total Time: ~5-15 seconds                                          │
│  Exit Code: 0 (success)                                             │
│                                                                     │
│  Outputs Created:                                                   │
│    ✅ .claude/memories/sessions/2026-01-11_f7d072bc.md             │
│    ✅ .claude/memories/entities/files.md (updated)                 │
│    ✅ .claude/memories/entities/technologies.md (updated)          │
│    ✅ .claude/memories/entities/concepts.md (updated)              │
│    ✅ .claude/memories/index.md (regenerated)                      │
│                                                                     │
│  Logs Written:                                                      │
│    📋 .claude/logs/memory.log                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Step Breakdown

### Step 1: Find Latest Transcript
```python
def find_latest_transcript() -> Path:
    # Search: ~/.claude/projects/*/
    # Find:   {uuid}/{uuid}.jsonl
    # Return: Most recently modified file
```

**Why?** Claude stores conversation history as JSONL files in project directories.

---

### Step 2: Parse JSONL Transcript
```python
def _parse_jsonl_transcript(transcript_path: Path) -> str:
    # Input:  JSONL (one JSON object per line)
    # Output: Human-readable conversation format

    # Handles:
    # - User messages
    # - Assistant messages
    # - Tool use blocks
    # - Tool result blocks
```

**Why?** Claude needs readable text, not raw JSON, for entity extraction.

---

### Step 3: Extract Entities Using Claude
```python
def extract_from_transcript(transcript: str) -> Dict:
    # Send transcript to Claude Haiku 4
    # Prompt: "Extract files, technologies, concepts..."
    # Return: Structured JSON
```

**Claude Haiku's Analysis:**
- Reads entire conversation
- Identifies mentioned files with paths
- Spots technologies and their purposes
- Extracts conceptual patterns
- Notes architectural decisions
- Counts tool usage
- Generates summary

---

### Step 4: Generate Session Summary
```python
def generate_session_summary(entities, session_id, date) -> str:
    # Build markdown with YAML frontmatter
    # Include all extracted entities
    # Format for human readability
```

**Output Format:**
```markdown
---
frontmatter: metadata
---

# Human-readable summary
## Sections for each entity type
```

---

### Step 5: Store Session Memory
```python
def create_memory(path, content, metadata):
    # Validate path (prevent traversal)
    # Create parent directories
    # Write frontmatter + content
    # Return success status
```

**Security:** All paths validated to prevent `../../../etc/passwd` attacks.

---

### Step 6: Update Entity Indices
```python
def _update_entity_indices(executor, entities):
    # For each entity type:
    #   1. Read existing index
    #   2. Parse current entries
    #   3. Add new unique entries
    #   4. Write updated index
```

**Deduplication:** Only adds entities that don't already exist.

---

### Step 7: Rebuild Master Index
```python
def create_index():
    # Scan all directories
    # Count files by type
    # List recent sessions
    # Generate navigation doc
```

**Purpose:** Single entry point to browse all memories.

---

## Error Handling

```
┌─────────────────────────────────────────┐
│ Any Step Fails?                         │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 1. Log error with full traceback        │
│ 2. Return exit code 1                   │
│ 3. Claude shows hook failed              │
│ 4. Session data preserved in transcript │
└─────────────────────────────────────────┘
```

**Safe Failure:** If hook fails, original transcript remains intact for retry.

---

## Performance

| Step | Avg Time | Why |
|------|----------|-----|
| Find transcript | <0.1s | File system scan |
| Parse JSONL | 0.1-0.5s | Depends on session length |
| **Extract entities** | **1-3s** | **Claude Haiku API call** |
| Generate summary | <0.1s | Template rendering |
| Store memory | <0.1s | File write |
| Update indices | 0.5-1s | Read/write 3 files |
| Rebuild index | <0.1s | Directory scan + write |
| **TOTAL** | **2-5s** | Most time in Claude Haiku API |

---

## File System Changes

```
BEFORE Hook:
.claude/memories/
├── sessions/
│   └── (14 existing files)
├── patterns/
├── entities/
│   ├── files.md
│   ├── technologies.md
│   └── concepts.md
└── index.md

AFTER Hook:
.claude/memories/
├── sessions/
│   ├── (14 existing files)
│   └── 2026-01-11_f7d072bc.md  ← NEW
├── patterns/
├── entities/
│   ├── files.md                 ← UPDATED
│   ├── technologies.md          ← UPDATED
│   └── concepts.md              ← UPDATED
└── index.md                     ← REGENERATED
```

---

## Logging

All operations logged to `.claude/logs/memory.log`:

```
2026-01-11 15:30:40 - memory_ingest_hook - INFO - Memory ingestion hook started
2026-01-11 15:30:40 - memory_ingest_hook - INFO - Found latest transcript: /home/user/.claude/projects/f7d072bc.../f7d072bc....jsonl
2026-01-11 15:30:40 - memory_ingest_hook - INFO - Processing session: f7d072bc
2026-01-11 15:30:41 - memory_ingest_hook - INFO - Extracting entities from transcript...
2026-01-11 15:30:48 - memory_ingest_hook - INFO - Extracted 3 files, 5 technologies, 2 concepts
2026-01-11 15:30:48 - memory_ingest_hook - INFO - Storing session memory at: sessions/2026-01-11_f7d072bc.md
2026-01-11 15:30:48 - memory_ingest_hook - INFO - Session memory created successfully: sessions/2026-01-11_f7d072bc.md
2026-01-11 15:30:48 - memory_ingest_hook - INFO - Updating entity indices...
2026-01-11 15:30:49 - memory_ingest_hook - INFO - Updating master index...
2026-01-11 15:30:49 - memory_ingest_hook - INFO - Memory ingestion complete!
```
