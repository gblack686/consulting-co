# consulting-co Repo Cleanup Review Catalog

**Generated:** 2026-04-12 | **Git History:** 34 commits (2025-12-01 → 2026-04-12)

This document catalogs every area of the repo for review before cleanup.
Mark each item: **PROCESS** (extract to second brain) | **ARCHIVE** (move to archive/) | **KEEP** (stays in repo) | **SKIP** (no value, just archive)

**User review completed:** 2026-04-12

---

## A. AGENT PROMPTS & DEFINITIONS (.claude/agents/)

31 agent definition files — these are the consulting practice's core IP.

| # | Agent | Purpose | Decision |
|---|-------|---------|----------|
| A1 | consulting-agent.md | Main consulting orchestrator | **KEEP** |
| A2 | google-workspace-agent.md | Gmail/Drive/Calendar automation | **ARCHIVE** — superseded by A1 |
| A3 | bowser-agent.md | Browser automation (Playwright/Chrome) | **CONSOLIDATE** → single browser agent |
| A4 | bowser-qa-agent.md | UI QA validation | **CONSOLIDATE** → single browser agent |
| A5 | claude-bowser-agent.md | Chrome DevTools browser agent | **CONSOLIDATE** → single browser agent |
| A6 | playwright-bowser-agent.md | Headless Playwright agent | **CONSOLIDATE** → single browser agent |
| A7 | agent-browser-agent.md | Vercel Labs agent-browser (WSL) | **CONSOLIDATE** → single browser agent |
| A8 | hooks-expert-agent.md | Hooks implementation specialist | **KEEP** |
| A9 | tac-expert-agent.md | TAC architecture composer | **KEEP** |
| A10 | obsidian-expert-agent.md | Obsidian vault operations | **KEEP** |
| A11 | obsidian-kb-expert.md | Obsidian KB architecture | **KEEP** |
| A12 | openclaw-expert-agent.md | OpenClaw management | **KEEP** — update expertise |
| A13 | aws-org-expert-agent.md | AWS organization management | **KEEP** |
| A14 | supabase-expert-agent.md | Supabase vault secrets | **KEEP** |
| A15 | youtube-transcript-agent.md | YouTube transcript extraction | **KEEP** |
| A16 | build-agent.md | Code implementation from plans | **KEEP** |
| A17 | review-agent.md | Code review against plan | **KEEP** |
| A18 | plan-agent.md | Implementation planning | **KEEP** |
| A19 | orchestrator-agent.md | Chat routing and task dispatch | **KEEP** |
| A20 | github-issue-agent.md | GitHub issue management | **KEEP** |
| A21 | statusline-setup.md | Status line config | **REVIEW** — wrong category? |
| A22-31 | (remaining agents) | Various specialized agents | **REVIEW** |

**ACTION ITEMS:**
- **Browser consolidation**: Merge A3-A7 into one `browser-agent.md` that handles both Playwright CLI (headless) and Chrome DevTools (headed). Two modes, one agent. Archive the 5 originals.
- **A12 OpenClaw**: Keep but update expertise section with current state
- **Catalog all agents** in second brain `capabilities/`

---

## B. COMMANDS (.claude/commands/) — 130+ files

### B1. Expert Systems (largest group)
| Expert | Files | Decision |
|--------|-------|----------|
| TAC | 9 files | **KEEP** — core methodology |
| OpenClaw | 13 files | **KEEP** — operational knowledge |
| Bowser | 4 files | **KEEP** — good patterns, merge with consolidated browser agent |
| Hooks | 4 files | **KEEP** |
| LinkedIn | 5 files | **KEEP** |
| Obsidian | 4 files | **KEEP** |
| AWS Org | 6 files | **KEEP** |
| Supabase | 5 files | **KEEP** |
| Pi Extensions | 5 files | **KEEP** |
| Overstory | 5 files | **ARCHIVE** — not currently relevant |

### B2. Workflow Commands
| Command Group | Files | Decision |
|---------------|-------|----------|
| Codebase Knowledge Extract | 8 files | **ARCHIVE** |
| Graphiti | 11 files | **KEEP** |
| LinkedIn | 8 files | **KEEP** |
| TAC Organizer | 5 files | **MERGE** with TAC system, update |
| Scoping | 5 files | **ARCHIVE** |
| Ecosystem/ADW | 6 files (identify-adws, link-adw-components, etc.) | **ARCHIVE** — ADW superseded by agent teams/team-runner |
| Bowser | 6 files | **KEEP** — good patterns, merge into browser workflow |
| Consulting | 1 file (quick-proposal) | **KEEP** |

### B3. Standalone Commands
| Command | Purpose | Decision |
|---------|---------|----------|
| adw.md | ADW dispatch | **ARCHIVE** — superseded by agent teams |
| plan-build-review.md | Plan/build/review cycle | **KEEP** |
| note-create.md / note-search.md | Obsidian note management | **KEEP** |
| youtube-detailed-analysis.md | Deep YT video analysis | **KEEP** — merge into YouTube agent team spec |
| validate.md / ultimate_validate_command.md | System validation | **KEEP** |
| test-agent.md | Agent testing | **KEEP** |
| check-subscriptions.md | Subscription tracking | **KEEP** |
| github-scrape.md / github-scrape-week.md | GitHub activity scraping | **KEEP** |
| search-knowledge.md | Knowledge search | **KEEP** |
| sync-claude-ecosystem.md | Ecosystem sync | **KEEP** |

**ACTION ITEMS:**
- **YouTube agent team**: YouTube needs to be an entire agent team with a full spec/PRD. Important system — needs end-to-end validation.
- **TAC organizer**: Merge with TAC system, update commands to reflect current architecture
- **ADW commands**: All superseded by agent teams pattern + team-runner command. Archive entirely.
- **Browser commands**: Keep patterns but consolidate under unified browser agent

---

## C. SKILLS (.claude/skills/) — 45+ skills

> **CRITICAL GAP:** Skills need user approval before they can be considered usable. Many are in unknown/stale status. A **separate project/spec/PRD** is needed to:
> 1. Review each skill individually and generate a report card
> 2. Get user approval before marking as production-ready
> 3. This is a full-blown audit — not part of this cleanup pass
>
> **For this cleanup:** Keep all skills in place. The skill audit is a follow-up initiative.

### C1. Consulting Pipeline Skills
| Skill | Phase | Status | Action |
|-------|-------|--------|--------|
| consulting-intake | PROSPECT→ONBOARD | Active | [ ] KEEP |
| consulting-admin | Operations | Active | [ ] KEEP |
| consulting-co | Meta | Empty shell | [ ] ARCHIVE |
| client-linkedin | PROSPECT | Active | [ ] KEEP |
| client-personal-intel | PROSPECT | Active | [ ] KEEP |
| client-research | PROSPECT | Active | [ ] KEEP |
| intake-session-processor | ONBOARD | Active | [ ] KEEP |
| create-second-brain-prd | ONBOARD | Active | [ ] KEEP |
| skill-discovery | META | Active | [ ] KEEP |

### C2. Knowledge & Integration Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| graphiti | Knowledge graph | [ ] KEEP |
| knowledge-sync | Knowledge sync | [ ] KEEP |
| tac-kb-query | TAC knowledge base | [ ] KEEP |
| obsidian-vault | Obsidian operations | [ ] KEEP |
| obsidian-agent-archiver | Archive agents to vault | [ ] KEEP |
| obsidian-schema-generator | Generate vault schemas | [ ] KEEP |

### C3. Infrastructure Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| github-actions-manager | CI/CD management | [ ] KEEP |
| github-cdk-workflows | CDK deployment | [ ] KEEP |
| github-issue-manager | Issue tracking | [ ] KEEP |
| aws-config-manager | AWS config | [ ] KEEP |
| linear-build-agent | Linear integration | [ ] KEEP |

### C4. Communication Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| gmail-manager | Gmail operations | [ ] KEEP |
| gmail-inbox-monitor | Inbox watching | [ ] KEEP (email_watcher) |
| daily-client-logs | Daily log generation | [ ] KEEP |

### C5. Content & Media Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| youtube-video-archiver | DELETED but dir lingers | [ ] ARCHIVE ghost dir |
| youtube-transcript-apify | Apify transcript extraction | [ ] KEEP |
| mtg-art-finder | Magic card art finder | [ ] KEEP |

### C6. Meta/Workflow Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| plan-build-review-adw | ADW lifecycle | [ ] KEEP |
| adw-dispatch / adw-status | ADW management | [ ] KEEP |
| workflow-ideator | Workflow brainstorming | [ ] KEEP |
| worktree-manager | Git worktree ops | [ ] KEEP |
| cost-tracker | Usage cost tracking | [ ] KEEP |
| subscription-usage-checker | Subscription monitoring | [ ] KEEP |
| skills-installer | Skill installation | [ ] KEEP |
| claude-code-plugin-builder | Plugin scaffolding | [ ] KEEP |
| social-media-recon | Social media research | [ ] KEEP |
| revstar-quickstart-workflow | RevStar consulting | [ ] KEEP |

### C7. GWS Sub-Skills (.claude/skills/gws/)
| Count | Purpose | Action |
|-------|---------|--------|
| 48+ | Google Workspace micro-skills (gmail, drive, calendar, meet, contacts, admin) | [ ] KEEP (modular GWS automation) |

### C8. Specialized Skills
| Skill | Purpose | Action |
|-------|---------|--------|
| browser-automation | Justfile + test framework | [ ] KEEP |
| hooks | Hook scaffolding templates | [ ] KEEP |
| tac-scaffolding | TAC pattern templates | [ ] KEEP |
| mac-mini-codegen | Mac Mini code gen | [ ] REVIEW — recent (2026-04-08) |
| multi-agent-orchestrator-administration | Orchestrator admin | [ ] REVIEW — if orchestrator archived? |
| anthropic-memory | Memory management | [ ] KEEP |

### C9. Client Sessions (consulting-intake/client-sessions/)
| Session | Files | Size | Action |
|---------|-------|------|--------|
| 20260221-greg-trading | 88 files | 974K | [ ] PROCESS → client second brain |
| 20260305-erica-creations | 14 files | 132K | [ ] PROCESS → client second brain |
| 20260305-michael-fisch | 60 files | 703K | [ ] PROCESS → client second brain |

---

## D. HOOKS (.claude/hooks/) — 26+ files

### D1. Active Hooks
| Hook | Event | Purpose | Action |
|------|-------|---------|--------|
| session_start.py | SessionStart | Load context | [ ] KEEP |
| session_end.py | SessionEnd | Save context | [ ] KEEP |
| session-start-context.py | SessionStart | Knowledge context injection | [ ] KEEP |
| session-end-flush.py | SessionEnd | Session summary to daily log | [ ] KEEP |
| pre-compact-flush.py | PreCompact | Extract decisions before compaction | [ ] KEEP |
| pre_tool_use.py | PreToolUse | Permission checks | [ ] KEEP |
| post_tool_use.py | PostToolUse | Post-action processing | [ ] KEEP |
| user_prompt_submit.py | UserPromptSubmit | Input processing | [ ] KEEP |
| log_to_graphiti.py | PostToolUse | Graphiti logging | [ ] KEEP |
| log_to_langfuse.py | PostToolUse | Langfuse tracing | [ ] KEEP |
| observe_to_graphiti.py | PostToolUse | Observability logging | [ ] KEEP |
| obsidian_ecosystem_sync.py | SessionEnd | Obsidian sync | [ ] KEEP |
| memory_ingest_hook.py | SessionEnd | Memory ingestion | [ ] KEEP |
| notification.py | Various | Notifications | [ ] KEEP |
| mini_doc_agent.py | PostToolUse | Doc generation | [ ] KEEP |
| subagent_stop.py | SubagentStop | Subagent cleanup | [ ] KEEP |
| trace_review_agent.py | SessionEnd | Trace analysis | [ ] KEEP |

### D2. Organized Hook Subdirs
| Subdir | Purpose | Action |
|--------|---------|--------|
| hooks/aws/ | AWS-related hooks | [ ] KEEP |
| hooks/cicd/ | CI/CD hooks | [ ] KEEP |
| hooks/creative/ | Creative workflow hooks | [ ] KEEP |
| hooks/dev/ | Development hooks | [ ] KEEP |
| hooks/git/ | Git operation hooks | [ ] KEEP |
| hooks/security/ | Security guard hooks | [ ] KEEP |
| hooks/utils/ | Utility hooks | [ ] KEEP |

### D3. Stale/Backup (Archive)
| File | Action |
|------|--------|
| pre_tool_use.py.bak | [ ] ARCHIVE |
| post_tool_use.py.bak | [ ] ARCHIVE |
| log_to_graphiti_openai_backup.py | [ ] ARCHIVE |
| TEST_TOOL_EXTRACTION.md | [ ] ARCHIVE |
| hooks.json.old | [ ] ARCHIVE |
| orchestrator-session-start.py | [ ] REVIEW (if orchestrator archived) |
| orchestrator-startup.py | [ ] REVIEW (if orchestrator archived) |

---

## E. CONTEXT FILES (.claude/context/) — 176 MB

### E1. YouTube Transcripts (Multiple Video IDs)
| Video ID | Creator/Topic | Files | Action |
|----------|--------------|-------|--------|
| CxErCGVo-oo | (unknown) | .json3, .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| F4zSxfBe5R0 | (unknown) | .json3, .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| LOazLNQnB80 | (unknown) | .json3, .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| M-3w1wEv0M0 | (unknown) | .json3 (2 copies), .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| QP-rSbSNd_o | (unknown) | .json3, manual.json3, _transcript_full | [ ] PROCESS |
| RhLpV6QDBFE | (unknown) | .json3 (2 copies), .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| Y6EyN9OI4RU | (unknown) | .json3 (2 copies), .info.json, _description, _metadata, _transcript | [ ] PROCESS |
| VFYrBEkEVsw | (unknown) | _description, _metadata, _transcript | [ ] PROCESS |
| XpxDwVt3OFw | (unknown) | _description, _metadata, _transcript | [ ] PROCESS |
| ZpZ7lFoWaT8 | (unknown) | _description, _metadata, _transcript | [ ] PROCESS |
| _VBmr6Rh56Y | (unknown) | .en.vtt, .description, _metadata, _transcript | [ ] PROCESS |
| nDHXLnwlIaY | (unknown) | _description, _metadata, _transcript | [ ] PROCESS |
| 34Dzv0IaYuE | (unknown) | .en-US.srt | [ ] PROCESS |

### E2. Architecture & Design Docs
| File | Topic | Action |
|------|-------|--------|
| ANTHROPIC_MEMORY_SKILL_DESIGN.md | Memory skill architecture | [ ] PROCESS |
| CLAUDE_AGENT_SDK_WINDOWS_GUIDE.md | Agent SDK setup | [ ] PROCESS |
| CLAUDE_CODE_CONTEXT_REFERENCE.md | Context window reference | [ ] PROCESS |
| OBSIDIAN_AGENT_KB_PLAN.md | Agent KB architecture | [ ] PROCESS |
| OPENCLAW_PI_PATTERNS_PLAN.md | Pi extension patterns | [ ] PROCESS |
| NANO_BANANA_VEO_SKILLS_GUIDE.md | Nano Banana + VEO skills | [ ] PROCESS |
| STYLE_GUIDE_SYSTEM_COMPLETE.md | Style guide system | [ ] PROCESS |
| GITHUB_WATCHLIST_INTEGRATION.md | GitHub watchlist setup | [ ] PROCESS |
| FINAL_ORGANIZATION_STRUCTURE.md | Org structure decisions | [ ] PROCESS |
| NON_TAC_SYNC_COMPLETE.md | Non-TAC sync report | [ ] SKIP |
| TAC_BATCH_SYNC_REPORT.md | TAC batch sync report | [ ] SKIP |
| PARSER_BUG_FIX.md | One-off bug fix | [ ] SKIP |
| YOUTUBE_ARCHIVER_STATUS.md | Archiver status report | [ ] SKIP |

### E3. Architecture Subdirectory
> **Note:** These need re-scoping through the lens of new architecture (skills on Mac Mini, self-sufficient with credentials, access to all services). Context and intent still valuable.

| File | Topic | Decision |
|------|-------|----------|
| CLAUDE_MD_SAMPLE_A_TAC_PURIST.md | CLAUDE.md template variant A | **PROCESS** |
| CLAUDE_MD_SAMPLE_B_CONSULTING_OPERATOR.md | CLAUDE.md template variant B | **PROCESS** |
| CLAUDE_MD_SAMPLE_C_COMPOSABLE_ARCHITECTURE.md | CLAUDE.md template variant C | **PROCESS** |
| OPENCLAW_MULTI_AGENT_ARCHITECTURE.md | OpenClaw multi-agent design | **SKIP** — may not be using this approach |
| OPENTELEMETRY_MULTIPROCESS_CONTEXT_PROPAGATION.md | OTel patterns | **PROCESS** |

### E4. Client Research (context/clients/)
| Client | Files | Size | Action |
|--------|-------|------|--------|
| garrett-shuster/ | Instagram snapshots, apify data, personal intel, experience screenshots | 68 MB | [ ] PROCESS → client second brain |
| gregory-black/ | Self-research, apify data, build scripts, deep-research | subset | [ ] PROCESS → GBAutomation second brain |
| erica-cruz-transcript | Session transcript | 1 file | [ ] PROCESS → client second brain |
| ISV_Accelerate_First_Call_Deck.pptx | AWS partner deck | 3 MB | [ ] PROCESS → reference |

### E5. Integration Guides
| File | Topic | Decision |
|------|-------|----------|
| LINEAR_HARNESS_*.md (3 files) | Linear harness guides | **SKIP** — not using currently |
| LINEAR_API_KEY_STORED.md | API key notification | **SKIP** |
| OPTION1_LAUNCH_GUIDE.md | ElevenLabs launch | **PROCESS** |
| ELEVENLABS_*.md (7 files) | ElevenLabs integration | **PROCESS** (consolidate) |
| VEO_*.md (4 files) | Google VEO video gen | **PROCESS** |
| api-generate-document.ts | Document gen API | **PROCESS** |
| api-schedule-call.ts | Call scheduling API | **PROCESS** |

### E6. Telemetry/Observability Docs
| File | Topic | Action |
|------|-------|--------|
| FULL_TELEMETRY_IMPLEMENTATION.md | Telemetry setup | [ ] SKIP (hooks are source of truth) |
| TELEMETRY_IMPLEMENTATION_COMPLETE.md | Completion report | [ ] SKIP |
| TELEMETRY_VERIFICATION_REPORT.md | Verification report | [ ] SKIP |
| TRACE_COMPARISON.md | Trace debugging | [ ] SKIP |
| TRACE_FIX_SUMMARY.md | Fix notes | [ ] SKIP |
| TRACE_INPUT_OUTPUT_FIX.md | Fix notes | [ ] SKIP |
| DASHBOARD_LATENCY_COLUMN.md | Dashboard config | [ ] SKIP |
| LANGFUSE_*.md (4 files) | Langfuse setup/debug | [ ] SKIP |
| LATENCY_*.md (2 files) | Latency debugging | [ ] SKIP |
| KMS_SETUP_GUIDE.md | KMS setup | [ ] PROCESS (infrastructure knowledge) |

### E7. Credential Files (SECURITY — DELETE)
| File | Action |
|------|--------|
| AGGREGATED_KEYS_AND_CREDENTIALS.md | [ ] DELETE |
| CREDENTIALS_UPLOADED.md | [ ] DELETE |
| README_CREDENTIALS.md | [ ] DELETE |
| REVSTAR_CREDENTIALS_BY_PROJECT.md | [ ] DELETE |
| store-credentials-to-kms*.bat (3 files) | [ ] DELETE |
| store-credentials-to-kms.sh | [ ] DELETE |
| retrieve-credentials-from-kms.sh | [ ] DELETE |
| upload-to-kms.sh | [ ] DELETE |

### E8. Research Subdirectories
| Directory | Content | Size | Action |
|-----------|---------|------|--------|
| linkedin-research/ | Campaign research, prospects | 5.9 MB | [ ] PROCESS |
| linkedin-posts/ | LinkedIn post content | small | [ ] PROCESS |
| linkedin/ | LinkedIn profile data | small | [ ] PROCESS |
| interview-prep/ | Interview frameworks | small | [ ] PROCESS |
| research/ | General research docs | small | [ ] REVIEW |
| shopping/ | Shopping comparison data | small | [ ] SKIP |
| youtube-likes/ | YouTube scan artifact | 11 MB | [ ] SKIP |
| testing/ | Test artifacts | 9.3 MB | [ ] SKIP |
| qa/ | QA artifacts | 1.7 MB | [ ] SKIP |
| codebase-optimization/ | Code optimization research | small | [ ] PROCESS |

### E9. YouTube Transcripts (formerly "TAC Scan") — DOMAIN WORKFLOW
> **Rename:** tac-scan → youtube-transcripts (this is the core YouTube transcript workflow)
> **Needs:** Full spec/PRD as part of YouTube agent team initiative

| Content | Files | Decision |
|---------|-------|----------|
| 14 video transcripts + metadata | ~58 files | **PROCESS** → intelligence/transcripts/youtube/ |
| SCAN_REPORT.md | 1 file | **PROCESS** → intelligence/ |

**File handling:** Keep rich text (_transcript.txt, _description.txt, _metadata.json). Delete raw formats (.json3, .vtt, .info.json) — they're regenerable via yt-dlp. Standardize naming convention.

### E10. Other Context Subdirs
| Directory | Content | Action |
|-----------|---------|--------|
| lightsail-openclaw-dump/ | 51 MB server dump — PLAINTEXT CREDENTIALS | [ ] DELETE (security) |
| setup/ | Setup guides | [ ] REVIEW |
| implementation/ | Implementation notes | [ ] REVIEW |
| google-workspace/ | GWS setup docs | [ ] PROCESS |
| observability/ | Observability docs | [ ] SKIP (hooks are truth) |
| obsidian/ | Obsidian config docs | [ ] PROCESS |
| planning/ | OLD planning docs (25 files) | [ ] SKIP (superseded by specs/) |
| telemetry/ | Telemetry docs | [ ] SKIP |
| parallax-*.md | Parallax prompt variations | [ ] PROCESS (creative IP) |
| style-guide-template.md | Style guide template | [ ] PROCESS |
| remote-coding-agent-integration-plan.md | Integration plan | [ ] PROCESS |
| openclaw-practical-guide*.* | OpenClaw guide | [ ] PROCESS |
| fix_message_parser.* | Parser fix scripts | [ ] SKIP |
| dashboard-complete.tsx | Dashboard component | [ ] PROCESS (reference implementation) |
| dashboard-full-with-agents.png | Dashboard screenshot | [ ] SKIP |
| elevenlabs-*.* | ElevenLabs configs | [ ] PROCESS |

---

## F. SPECS (specs/) — 752 KB, STAYS IN REPO

### F1. Core Guides (keep)
| File | Topic |
|------|-------|
| CLAUDE-CODE-ESSENTIALS-GUIDE.md | Claude Code essentials |
| CONSULTING-WORKFLOW.md | Consulting workflow |
| VIBE-PLANNING-FRAMEWORK.md | Vibe planning |
| agent-skills-guide.md | Agent skills reference |
| claude-code-ecosystem-handbook-part1.md | Ecosystem handbook |
| claude-official-docs.md | Official docs reference |

### F2. Project Specs (keep)
| File | Topic |
|------|-------|
| greg-trading-official-plan.md | Trading bot (100KB) |
| mission-control-plan.md | Mission control hub |
| tac-agent-composer-redesign.md | TAC agent composer |
| adw-plan.md | ADW architecture |
| pi-extensions-setup-plan.md | Pi extensions |

### F3. Infrastructure (review)
| File | Topic | Action |
|------|-------|--------|
| AWS-PRD-SYSTEM-READY.md | AWS PRD system | [ ] REVIEW |
| CLAUDE-CODE-EC2-ARCHITECTURE.md | EC2 architecture | [ ] REVIEW |
| ORCHESTRATOR-SETUP-COMPLETE.md | Orchestrator setup | [ ] ARCHIVE (orchestrator going away) |
| PRD-DEPLOYMENT-COMPLETE.md | PRD deployment | [ ] REVIEW |

### F4. Meta Plans (keep)
| File | Topic |
|------|-------|
| meta1-obsidian-sync-plan.md | Obsidian sync |
| meta2-github-sdlc-plan.md | GitHub SDLC |
| meta3-youtube-universal-plan.md | YouTube pipeline |
| meta4-web-research-plan.md | Web research |

### F5. Marketing/Workflows (keep)
| File | Topic |
|------|-------|
| marketing/vsl-script-*.md | VSL scripts (3 versions — consolidate?) |
| workflows/CUSTOMER-PLANNING-WORKFLOW.md | Customer planning |
| workflows/MASTER_CONSULTING_QUESTIONS.md | Discovery questions |

---

## G. ROOT-LEVEL DIRECTORIES (Archive Candidates)

| # | Directory | Size | Content Summary | Action |
|---|-----------|------|----------------|--------|
| G1 | observability/ | 2.0 GB | Monitoring project — apps, scripts, specs | [ ] ARCHIVE |
| G2 | dynamous-posts/ | 610 MB | Remotion video experiments | [ ] ARCHIVE |
| G3 | claude-repos/ | 514 MB | Cloned reference repos | [ ] ARCHIVE |
| G4 | openclaw-deploy/ | 312 MB | CDK IaC deployment | [ ] ARCHIVE |
| G5 | code-design/ | 259 MB | AURA docs, API patterns, generated images | [ ] PROCESS → ARCHIVE |
| G6 | zeroclaw-deploy/ | 217 MB | Superseded CDK deployment | [ ] ARCHIVE |
| G7 | awesome-nano-banana-pro-prompts/ | 195 MB | Image generation prompts | **PROCESS** → second brain, then archive |
| G8 | logs/ | 122 MB | Old session logs (2024-2025) | [ ] ARCHIVE |
| G9 | obsidian-ai-agent/ | 107 MB | Obsidian plugin project | **PROCESS** → second brain, then archive |
| G10 | 3d-avatars/ | 31 MB | Avatar POC | [ ] ARCHIVE |
| G11 | quickstarts/ | 11 MB | Template projects | [ ] ARCHIVE |
| G12 | tac-learning-system/ | 3.9 MB | TAC 8-lesson curriculum | [ ] ARCHIVE |
| G13 | indydevdan/ | 3.4 MB | External reference | [ ] ARCHIVE |
| G14 | tools/ | small | remote-coding-agent | [ ] ARCHIVE |
| G15 | voiceflow/ | 132 KB | Stale integration | [ ] ARCHIVE |
| G16 | comfyui/ | 36 KB | Empty research stub | [ ] ARCHIVE |
| G17 | plugins/ | minimal | Empty | [ ] ARCHIVE |
| G18 | gmail/ | empty | Empty dir | [ ] ARCHIVE |
| G19 | screenshots/ | minimal | Bowser screenshots | [ ] ARCHIVE |
| G20 | gb-automation-landing/ | large | Landing page (MOVE TO OWN REPO) | [ ] MOVE → ARCHIVE |

### Root-Level Dirs That STAY:
| Directory | Size | Why Keep |
|-----------|------|----------|
| customer-gateway-proxy/ | small | Active deployed proxy |
| openclaw-skills/ | 20 KB | Active OpenClaw skills |
| specs/ | 752 KB | Project specifications |
| wiki/ | 320 KB | Company wiki |
| portfolio/ | 104 KB | Project portfolio |
| style-board/ | 1.3 MB | Design assets |
| scripts/ | 102 KB | Utility scripts |
| proposals/ | small | Client proposals |
| PRP/ | small | Product requirements |
| .claude/ | (cleaned) | Core harness |

---

## H. ROOT-LEVEL FILES (Cleanup)

| File | Purpose | Action |
|------|---------|--------|
| CLAUDE.md | Project instructions | [ ] KEEP (update after cleanup) |
| README.md | Project overview | [ ] KEEP |
| .gitignore | Git exclusions | [ ] KEEP (update) |
| .mcp.json | MCP server config | [ ] KEEP |
| package.json | npm config | [ ] REVIEW |
| .gitmodules | Submodule refs | [ ] REVIEW (submodules being archived) |
| TODO.md | Task list | [ ] PROCESS → Linear/second brain, then ARCHIVE |
| my-second-brain-requirements.md | Requirements | [ ] PROCESS → second brain, then ARCHIVE |
| .temp-lightsail-key | AWS key | [ ] DELETE (security) |
| .env, .env.mem0 | Environment vars | [ ] VERIFY in .gitignore |
| nul | Windows artifact | [ ] DELETE |
| battery-report.html | System report | [ ] DELETE |
| technology-logos.html | Generated HTML | [ ] DELETE |
| terminal-bug-20251218.md | Bug report | [ ] ARCHIVE |
| temp_ids.txt | Temp file | [ ] DELETE |
| svg-export-glyphs-subsetting.excalidraw | Design file | [ ] ARCHIVE |
| test_collaboration.png | Test screenshot | [ ] DELETE |
| aang_the_last_airbender.jpg | Image | [ ] DELETE |
| mac-login-screen.png | Screenshot | [ ] DELETE |
| add_tech_logos.py | One-off script | [ ] DELETE |
| generate_robot*.py (2 files) | One-off scripts | [ ] DELETE |
| eleven_history*.json (2 files) | ElevenLabs data | [ ] ARCHIVE |
| veo_*.json (2 files) | VEO operation data | [ ] ARCHIVE |
| option*.png (4 files) | Generated images | [ ] DELETE |
| generalist_*.png (4 files) | Generated images | [ ] DELETE |
| robot_builder*.png (2 files) | Generated images | [ ] DELETE |
| option7_parallax_*.mp4 (2 files) | Generated videos | [ ] ARCHIVE |
| option7_parallax_*.json (2 files) | VEO configs | [ ] ARCHIVE |

---

## I. .CLAUDE TOP-LEVEL DOCS (Superseded — Archive)

| File | Topic | Action |
|------|-------|--------|
| ARCHITECTURE.md | Core architecture | [ ] KEEP |
| README.md | Entry point | [ ] KEEP |
| CONSULTING_COMMANDS_COMPLETE.md | Command reference | [ ] KEEP |
| TOKEN_ACCOUNTING_GUIDE.md | Token accounting | [ ] KEEP |
| OBSERVABILITY_INTEGRATION.md | Observability (master) | [ ] KEEP |
| OBSIDIAN_GRAPHITI_INTEGRATION.md | Obsidian+Graphiti (master) | [ ] KEEP |
| All other *.md (20+ files) | Superseded variants | [ ] ARCHIVE |

---

## J. .CLAUDE PYTHON SCRIPTS (One-Off — Archive)

| Category | Files | Action |
|----------|-------|--------|
| Graphiti debug | check_episodes, check_episodic, init_graphiti, quick_test_episode, view_knowledge_graph, check_schema | [ ] ARCHIVE |
| Langfuse debug | check_langfuse_* (4), fetch_langfuse_traces, fetch_trace_details* (2), check_trace_details | [ ] ARCHIVE |
| Test scripts | test_* (15+ files) | [ ] ARCHIVE |
| Verify scripts | verify_telemetry_ready, verify_token_accounting | [ ] ARCHIVE |
| Other | extract_usage | [ ] ARCHIVE |

---

## K. PROCESSING PRIORITY ORDER

1. **SECURITY** (Phase 1): Delete credential files — E7, lightsail dump, .temp-lightsail-key
2. **AGENT PROMPTS** (Phase 2a): Catalog all agent definitions (A) and expert systems (B1) into second brain `capabilities/`
3. **WORKFLOW KNOWLEDGE** (Phase 2b): Extract workflow patterns from commands (B2) into second brain `knowledge/concepts/`
4. **YOUTUBE TRANSCRIPTS** (Phase 2c): Process E1 + E9 (tac-scan) into second brain `intelligence/transcripts/`
5. **ARCHITECTURE DOCS** (Phase 2d): Process E2, E3, E5 into second brain `knowledge/concepts/`
6. **CLIENT DATA** (Phase 2e): Move E4 + C9 client sessions to respective client second brains
7. **RESEARCH** (Phase 2f): Process E8 (LinkedIn, interview, codebase optimization) into second brain
8. **CREATIVE IP** (Phase 2g): Process parallax prompts, style guides, VEO configs into second brain
9. **ARCHIVE** (Phase 3-4): Move G1-G20 directories + I + J to archive/
10. **LIBRARY SYNC** (Phase 6): Update The Library catalog

---

## TOTALS

- **KEEP in repo:** ~15 directories, ~250 files (agents, commands, skills, hooks, configs, specs)
- **PROCESS → second brain:** ~50-80 files producing ~10-15 knowledge articles
- **ARCHIVE:** ~25 directories, ~4 GB
- **DELETE (security):** ~15 credential files + lightsail dump (51 MB)
- **DELETE (junk):** ~20 root-level temp files/images
