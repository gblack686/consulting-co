# Repo Cleanup — Agent Team Specs

**Plan:** `~/.claude/plans/memoized-wandering-sunset.md`
**Review Catalog:** `.claude/context/REPO_CLEANUP_REVIEW.md`
**Target:** `gbauto/gbautomation/second-brain/`

Each agent below is a self-contained task. Can run as team-runner agents or parallel Claude subagents.

---

## Agent 1: Security Cleanup

**Role:** Delete credential files. No processing needed.
**Execution:** Sequential, first.
**Permission:** acceptEdits (needs rm/mv)

### Tasks:
1. `rm -rf .claude/context/lightsail-openclaw-dump/` (51 MB, plaintext API keys)
2. `rm .claude/context/AGGREGATED_KEYS_AND_CREDENTIALS.md`
3. `rm .claude/context/CREDENTIALS_UPLOADED.md`
4. `rm .claude/context/README_CREDENTIALS.md`
5. `rm .claude/context/REVSTAR_CREDENTIALS_BY_PROJECT.md`
6. `rm .claude/context/store-credentials-to-kms*.bat .claude/context/store-credentials-to-kms.sh`
7. `rm .claude/context/retrieve-credentials-from-kms.sh .claude/context/upload-to-kms.sh`
8. `rm .temp-lightsail-key`
9. Verify `.env` and `.env.mem0` are in `.gitignore`
10. `grep -r "sk-ant\|sk-proj\|AKIA" --include="*.json" --include="*.md" --exclude-dir=archive --exclude-dir=node_modules .` — report any remaining exposed keys

---

## Agent 2: YouTube Transcript Processor

**Role:** Process all YouTube transcripts into second brain. Standardize naming.
**Execution:** Can run parallel with others.
**Input:** `.claude/context/tac-scan/`, `.claude/context/*_transcript.txt`, `.claude/context/*.en.json3`
**Output:** `gbauto/gbautomation/second-brain/intelligence/transcripts/youtube/`

### Tasks:
1. Create `intelligence/transcripts/youtube/` in second brain
2. For each video ID found in `.claude/context/tac-scan/` and `.claude/context/`:
   - Copy `{ID}_transcript.txt` → `intelligence/transcripts/youtube/{ID}_transcript.txt`
   - Copy `{ID}_metadata.json` → `intelligence/transcripts/youtube/{ID}_metadata.json`
   - Copy `{ID}_description.txt` → `intelligence/transcripts/youtube/{ID}_description.txt`
   - Skip raw formats: `.json3`, `.vtt`, `.info.json`, `.en-orig.json3`, `.srt`
3. Create `intelligence/transcripts/youtube/_INDEX.md` listing all videos with titles (from metadata)
4. Rename `tac-scan/` → archive as `archive/youtube-transcripts-raw/`
5. Archive all root-level `.claude/context/{ID}*` YouTube files to `archive/youtube-raw/`

### Naming Convention:
```
{VIDEO_ID}_transcript.txt    — cleaned timestamped text
{VIDEO_ID}_metadata.json     — title, channel, views, date, segments
{VIDEO_ID}_description.txt   — video description
```

---

## Agent 3: Architecture & Design Compiler

**Role:** Compile architecture docs into second brain knowledge articles.
**Execution:** Can run parallel.
**Input:** `.claude/context/architecture/`, `.claude/context/ANTHROPIC_MEMORY_SKILL_DESIGN.md`, etc.
**Output:** `gbauto/gbautomation/second-brain/knowledge/concepts/`

### Tasks:
1. Read all architecture files:
   - `CLAUDE_MD_SAMPLE_A_TAC_PURIST.md`
   - `CLAUDE_MD_SAMPLE_B_CONSULTING_OPERATOR.md`
   - `CLAUDE_MD_SAMPLE_C_COMPOSABLE_ARCHITECTURE.md`
   - `OPENTELEMETRY_MULTIPROCESS_CONTEXT_PROPAGATION.md`
   - `ANTHROPIC_MEMORY_SKILL_DESIGN.md`
   - `CLAUDE_AGENT_SDK_WINDOWS_GUIDE.md`
   - `OBSIDIAN_AGENT_KB_PLAN.md`
   - `STYLE_GUIDE_SYSTEM_COMPLETE.md`
   - `FINAL_ORGANIZATION_STRUCTURE.md`
   - `GITHUB_WATCHLIST_INTEGRATION.md`
2. Compile into knowledge articles:
   - `knowledge/concepts/claude-md-patterns.md` — the 3 CLAUDE.md variants + lessons
   - `knowledge/concepts/architecture-decisions.md` — org structure, memory design, observability
   - `knowledge/concepts/integration-patterns.md` — watchlist, agent SDK, style guide
3. Skip: `OPENCLAW_MULTI_AGENT_ARCHITECTURE.md` (not using this approach)
4. Update `knowledge/index.md` with new articles

---

## Agent 4: Integration Guide Compiler

**Role:** Compile integration guides into knowledge articles.
**Execution:** Can run parallel.
**Input:** `.claude/context/ELEVENLABS_*.md`, `VEO_*.md`, `api-*.ts`, `OPTION1_LAUNCH_GUIDE.md`
**Output:** `gbauto/gbautomation/second-brain/knowledge/concepts/`

### Tasks:
1. Compile ElevenLabs docs (7 files) → `knowledge/concepts/elevenlabs-integration.md`
2. Compile VEO docs (4 files) → `knowledge/concepts/veo-video-generation.md`
3. Process `api-generate-document.ts` + `api-schedule-call.ts` → `knowledge/concepts/api-patterns.md`
4. Process `KMS_SETUP_GUIDE.md` → `knowledge/concepts/aws-kms-setup.md`
5. Skip: `LINEAR_HARNESS_*.md` (3 files — not using currently)
6. Update `knowledge/index.md`

---

## Agent 5: Client Data Processor

**Role:** Move client data to respective client second brains.
**Execution:** Can run parallel.
**Input:** `.claude/context/clients/`, `.claude/skills/consulting-intake/client-sessions/`

### Tasks:
1. `context/clients/garrett-shuster/` → `gbauto/garrett-shuster/second-brain/intelligence/` (create if needed, or archive)
2. `context/clients/gregory-black/` → `gbauto/gbautomation/second-brain/intelligence/research/`
3. `context/clients/erica-cruz-transcript-20260305.txt` → Erica client second brain or archive
4. `context/clients/ISV_Accelerate_First_Call_Deck.pptx` → `gbauto/gbautomation/second-brain/intelligence/references/`
5. Client sessions stay in consulting-intake (they're templates/history)

---

## Agent 6: Research & LinkedIn Compiler

**Role:** Compile research content into knowledge articles.
**Execution:** Can run parallel.
**Input:** `.claude/context/linkedin-research/`, `linkedin-posts/`, `linkedin/`, `interview-prep/`, `codebase-optimization/`
**Output:** `gbauto/gbautomation/second-brain/knowledge/concepts/`

### Tasks:
1. Compile LinkedIn research → `knowledge/concepts/linkedin-automation-strategy.md`
2. Compile interview prep → `knowledge/concepts/interview-frameworks.md`
3. Compile codebase optimization → `knowledge/concepts/codebase-optimization-patterns.md`
4. Process parallax prompt variations → `knowledge/concepts/creative-prompt-engineering.md`
5. Update `knowledge/index.md`

---

## Agent 7: Bulk Archiver

**Role:** Move all archive-destined directories. No processing.
**Execution:** Sequential (lots of mv operations).
**Permission:** acceptEdits

### Tasks (mkdir -p archive/ then mv each):
```bash
# Root-level directories
mv observability/ archive/
mv dynamous-posts/ archive/
mv claude-repos/ archive/
mv openclaw-deploy/ archive/
mv code-design/ archive/    # after Agent 3/4 process
mv zeroclaw-deploy/ archive/
mv awesome-nano-banana-pro-prompts/ archive/  # after processing
mv logs/ archive/
mv obsidian-ai-agent/ archive/  # after processing
mv 3d-avatars/ archive/
mv quickstarts/ archive/
mv tac-learning-system/ archive/
mv indydevdan/ archive/
mv tools/ archive/
mv voiceflow/ archive/
mv comfyui/ archive/
mv plugins/ archive/
mv gmail/ archive/
mv screenshots/ archive/

# .claude internal
mv .claude/orchestrator/ archive/.claude-orchestrator/

# Root junk files
rm nul battery-report.html technology-logos.html temp_ids.txt
rm aang_the_last_airbender.jpg mac-login-screen.png test_collaboration.png
rm add_tech_logos.py generate_robot.py generate_robot_from_base.py
rm option5_*.png option7_*.png generalist_*.png robot_builder*.png
mv eleven_history*.json veo_*.json option7_parallax_*.* archive/media/
mv svg-export-glyphs-subsetting.excalidraw terminal-bug-20251218.md archive/
mv my-second-brain-requirements.md archive/

# .claude superseded docs
mkdir -p archive/.claude-docs/
mv .claude/COMPLETE_STACK_QUICK_START.md archive/.claude-docs/
mv .claude/OBSERVABILITY_INTEGRATION_COMPLETE.md archive/.claude-docs/
mv .claude/OBSERVABILITY_INTEGRATION_PLAN.md archive/.claude-docs/
mv .claude/OBSERVABILITY_QUICK_START.md archive/.claude-docs/
mv .claude/SIMPLIFIED_OBSERVABILITY.md archive/.claude-docs/
mv .claude/OBSIDIAN_COMMANDS_CREATED.md archive/.claude-docs/
mv .claude/OBSIDIAN_DAILY_SUMMARY.md archive/.claude-docs/
mv .claude/OBSIDIAN_GRAPHITI_QUICK_START.md archive/.claude-docs/
mv .claude/OBSIDIAN_INTEGRATION_PLAN.md archive/.claude-docs/
mv .claude/OBSIDIAN_QUICK_REFERENCE.md archive/.claude-docs/
mv .claude/OBSIDIAN_QUICK_START.md archive/.claude-docs/
mv .claude/LANGFUSE_*.md archive/.claude-docs/
mv .claude/NEO4J_QUERIES.md archive/.claude-docs/
mv .claude/NEXT_LEVEL_VISION.md archive/.claude-docs/
mv .claude/CLAUDE_SUBAGENT_EXTRACTION.md archive/.claude-docs/
mv .claude/FIXES_APPLIED.md archive/.claude-docs/
mv .claude/INTEGRATION_SUMMARY.md archive/.claude-docs/
mv .claude/INTEGRATION_VERIFICATION.txt archive/.claude-docs/
mv .claude/GET_LANGFUSE_API_KEYS.md archive/.claude-docs/
mv .claude/GRAPHITI_SETUP_COMPLETE.md archive/.claude-docs/
mv .claude/TELEMETRY_SUMMARY.txt archive/.claude-docs/
mv .claude/TEST_RESULTS.md archive/.claude-docs/
mv .claude/TEST_SCENARIO.txt archive/.claude-docs/

# .claude one-off Python scripts
mkdir -p archive/.claude-scripts/
mv .claude/check_*.py .claude/fetch_*.py .claude/test_*.py archive/.claude-scripts/
mv .claude/verify_*.py .claude/extract_usage.py archive/.claude-scripts/
mv .claude/init_graphiti.py .claude/quick_test_episode.py archive/.claude-scripts/
mv .claude/view_knowledge_graph.py archive/.claude-scripts/
mv .claude/.test_extraction.jsonl .claude/test_transcript.jsonl archive/.claude-scripts/
mv .claude/langfuse_hook_debug.log archive/.claude-scripts/
mv .claude/open_dashboards.bat archive/.claude-scripts/

# Hook backups
mv .claude/hooks.json.old archive/.claude-scripts/
mv .claude/hooks/pre_tool_use.py.bak archive/.claude-scripts/
mv .claude/hooks/post_tool_use.py.bak archive/.claude-scripts/
mv .claude/hooks/log_to_graphiti_openai_backup.py archive/.claude-scripts/
mv .claude/hooks/TEST_TOOL_EXTRACTION.md archive/.claude-scripts/
```

---

## Agent 8: Browser Agent Consolidation

**Role:** Merge 5 browser agents into one unified agent definition.
**Execution:** After archiving.
**Output:** `.claude/agents/browser-agent.md` (updated)

### Tasks:
1. Read all 5 browser agents (A3-A7)
2. Create unified `browser-agent.md` with:
   - **Headed mode** (Chrome DevTools MCP) — for visual browsing, screenshots, interaction
   - **Headless mode** (Playwright CLI) — for parallel scraping, QA testing, automation
   - Combined expertise from all 5
3. Archive originals to `archive/.claude-agents/`
4. Update any commands/hooks that reference the old agent names

---

## Agent 9: ADW/Ecosystem Archiver

**Role:** Archive superseded ADW commands and Overstory/Scoping experts.
**Execution:** After archiving.

### Tasks:
```bash
mkdir -p archive/.claude-commands/
mv .claude/commands/adw.md archive/.claude-commands/
mv .claude/commands/ecosystem/identify-adws.md archive/.claude-commands/
mv .claude/commands/ecosystem/link-adw-components.md archive/.claude-commands/
mv .claude/commands/experts/overstory/ archive/.claude-commands/
mv .claude/commands/scoping/ archive/.claude-commands/
mv .claude/commands/codebase-knowledge-extract/ archive/.claude-commands/
```

---

## Agent 10: Verification & Ref Cleanup

**Role:** Verify no broken references, update CLAUDE.md, .gitignore.
**Execution:** Last.

### Tasks:
1. Add `archive/` to `.gitignore`
2. Update root `CLAUDE.md` — remove refs to deleted/archived dirs
3. `grep -r "observability\|orchestrator\|dynamous\|code-design\|claude-repos\|zeroclaw\|adw" .claude/agents/ .claude/commands/ .claude/hooks/ .claude/skills/` — fix broken refs
4. Run `python .claude/skills/skill-discovery/scripts/discover.py` — verify skills resolve
5. `du -sh .` — report new repo size
6. Report summary: what was archived, processed, deleted

---

## Agent 11: gb-automation-landing Repo Extract

**Role:** Move landing page to its own GitHub repo.
**Execution:** Can run parallel with archiving.

### Tasks:
1. `gh repo create gbautomation/gb-automation-landing --private --description "GBAutomation landing page (Amplify)"`
2. Copy `gb-automation-landing/` contents (excluding node_modules/, dist/, .next/)
3. Push to new repo
4. `mv gb-automation-landing/ archive/`

---

## Agent 12: Library Sync

**Role:** Update The Library catalog after cleanup.
**Execution:** After all other agents complete.

### Tasks:
1. `gh repo clone gbauto-tac/the-library /tmp/the-library`
2. Read `library.yaml`
3. Remove entries pointing to archived dirs
4. Update paths for anything that moved
5. Add new entries (skill-discovery, compile_knowledge)
6. Push updated `library.yaml`

---

## Execution Order

```
Phase 1 (sequential):     Agent 1 (security)
Phase 2 (parallel):       Agents 2, 3, 4, 5, 6 (knowledge processing)
Phase 3 (sequential):     Agent 7 (bulk archive), Agent 11 (landing page extract)
Phase 4 (parallel):       Agents 8, 9 (consolidation)
Phase 5 (sequential):     Agent 10 (verification)
Phase 6 (sequential):     Agent 12 (library sync)
```

**Estimated total:** 12 agents, ~6 parallel batches
**Can use team-runner?** Team-runner is designed for Mac Mini dispatch via Meridian. These tasks are local (Windows). Better to use Claude Code subagents (`Agent` tool with `subagent_type`) directly, which run locally with full tool access.
