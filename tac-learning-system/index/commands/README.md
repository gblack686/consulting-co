# TAC Command Index

388+ slash commands across TAC repositories. Commands are markdown files in `.claude/commands/`.

## Command Categories

### Core Workflow Commands
| Command | TAC Source | Purpose |
|---------|------------|---------|
| `/prime` | All TACs | Initialize context for session |
| `/start` | tac-3+ | Start new task with context |
| `/build` | All TACs | Execute build workflow |
| `/plan` | tac-4+ | Plan before implementing |
| `/implement` | tac-3+ | Implement a feature |

### SDLC Commands (tac-5+)
| Command | Purpose |
|---------|---------|
| `/feature` | Start new feature |
| `/bug` | Fix a bug |
| `/chore` | Non-feature work |
| `/test` | Run tests |
| `/test_e2e` | Run E2E tests |
| `/review` | Code review |
| `/document` | Generate docs |
| `/commit` | Git commit |
| `/pull_request` | Create PR |

### ADW Classification (tac-5+)
| Command | Purpose |
|---------|---------|
| `/classify_adw` | Route to appropriate ADW |
| `/classify_issue` | Categorize issue type |

### Advanced Commands (tac-7+)
| Command | Purpose |
|---------|---------|
| `/install_worktree` | Setup isolated worktree |
| `/cleanup_worktrees` | Clean old worktrees |
| `/health_check` | System health check |
| `/track_agentic_kpis` | Track performance metrics |
| `/in_loop_review` | Review during workflow |

## By Repository

### tac-2 (3 commands)
- [install.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude/commands/install.md)
- [prime.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude/commands/prime.md)
- [tools.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude/commands/tools.md)

### tac-3 (8 commands)
- [bug.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/bug.md)
- [chore.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/chore.md)
- [feature.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/feature.md)
- [implement.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/implement.md)
- [install.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/install.md)
- [prime.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/prime.md)
- [start.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/start.md)
- [tools.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude/commands/tools.md)

### tac-4 (13 commands)
- [bug.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/bug.md)
- [chore.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/chore.md)
- [classify_issue.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/classify_issue.md)
- [commit.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/commit.md)
- [feature.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/feature.md)
- [find_plan_file.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/find_plan_file.md)
- [generate_branch_name.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/generate_branch_name.md)
- [implement.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/implement.md)
- [install.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/install.md)
- [prime.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/prime.md)
- [pull_request.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/pull_request.md)
- [start.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/start.md)
- [tools.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude/commands/tools.md)

### tac-5 (21 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-5\.claude\commands\`
- bug, chore, classify_adw, classify_issue, commit, feature
- find_plan_file, generate_branch_name, implement, install, prime
- pull_request, resolve_failed_e2e_test, resolve_failed_test, start
- test, test_e2e, tools
- e2e/ subfolder: test_basic_query, test_complex_query, test_sql_injection

### tac-6 (27 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-6\.claude\commands\`
- Core: bug, chore, classify_adw, classify_issue, commit, document, feature
- Git: generate_branch_name, pull_request
- Workflow: implement, install, patch, prepare_app, prime, review, start
- Testing: resolve_failed_e2e_test, resolve_failed_test, test, test_e2e, tools
- E2E: conditional_docs + 5 e2e test commands

### tac-7 (33 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-7\.claude\commands\`
- All tac-6 commands plus:
- cleanup_worktrees, health_check, in_loop_review
- install_worktree, track_agentic_kpis
- E2E: test_export_functionality (new)

### tac-8 (Multiple Apps)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-8\`

**app1_agent_layer_primitives** (5 commands): chore, feature, implement, prime, start

**app2_multi_agent_todone** (12 commands): aws-sign-in, build, chore, clean_worktree, feature, implement, init_worktree, mark_in_progress, plan, prime, process_tasks, update_task

**app3_out_loop_multi_agent_task_board** (9 commands): build, chore, clean_worktree, convert_paths_absolute, implement, init_worktree, plan, prime, start

**app4_agentic_prototyping** (14 commands): build, clean_worktree, get_notion_tasks, hi, init_worktree, make_worktree_name, plan, plan_bun_scripts, plan_uv_mcp, plan_uv_script, plan_vite_vue, prime, update_notion_task, update_notion_task_with_file

**app5_nlq_to_sql_aea** (36 commands): Full tac-7 command set + 9 AEA-specific e2e tests

### agentic-prompt-engineering (22 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\agentic-prompt-engineering\.claude\commands\`
- Core: all_tools, background, build, build_w_report, load_ai_docs, load_bundle
- Planning: parallel_subagents, plan_vite_vue, prime, prime_cc, prime_tier_list
- Specialized: create_image, edit_image, crypto_coin_analyzer_agent_prompt, crypto_research
- Meta: question, quick-plan, start, t_metaprompt_workflow
- Experts: cc_hook_expert_build, cc_hook_expert_improve, cc_hook_expert_plan

### building-specialized-agents (17 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\building-specialized-agents\.claude\commands\`
- all_tools, background, build, build_w_report, load_ai_docs, load_bundle
- parallel_subagents, plan_vite_vue, plan_w_docs, prime, prime_cc
- question, quick-plan, scout, scout_plan_build, t_metaprompt_workflow
- Custom app: qa_agent.md

### multi-agent-orchestration (18 commands)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\.claude\commands\`
- all_tools, background, build, build_in_parallel, find_and_summarize
- load_ai_docs, load_bundle, parallel_subagents
- plan, plan_w_docs, plan_w_scouters, prime, prime_3, prime_cc
- question, quick-plan, scout, scout_plan_build

### software-delivery-adw (linked via docs)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\software-delivery-adw\claude_commands\commands\`
- Commands delegating to ADW workflows
