# TAC Agent Index

16 agent templates across TAC repositories. Agents are markdown files in `.claude/agents/`.

## Agent Categories

### Meta Agents
| Agent | TAC Source | Purpose |
|-------|------------|---------|
| meta-agent | agentic-prompt-engineering, multi-agent-orchestration | Orchestrate other agents |

### Research Agents
| Agent | TAC Source | Purpose |
|-------|------------|---------|
| docs-scraper | agentic-prompt-engineering, multi-agent-orchestration | Scrape and analyze documentation |
| crypto-coin-analyzer | agentic-prompt-engineering | Analyze crypto projects |
| scout-report-suggest | multi-agent-orchestration | Scout codebase and suggest |
| scout-report-suggest-fast | multi-agent-orchestration | Fast version of scout |

### Build Agents
| Agent | TAC Source | Purpose |
|-------|------------|---------|
| build-agent | multi-agent-orchestration | Execute build workflows |

### Review Agents
| Agent | TAC Source | Purpose |
|-------|------------|---------|
| review-agent | multi-agent-orchestration/orchestrator_3_stream | Code review |
| playwright-validator | multi-agent-orchestration | E2E test validation |

## By Repository

### agentic-prompt-engineering (3 agents)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\agentic-prompt-engineering\.claude\agents\`

- **[crypto-coin-analyzer.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/agents/crypto-coin-analyzer.md)**
  - Analyzes cryptocurrency projects
  - Uses web research and analysis prompts

- **[docs-scraper.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/agents/docs-scraper.md)**
  - Scrapes documentation sites
  - Extracts key information for context

- **[meta-agent.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/agents/meta-agent.md)**
  - Orchestrates other agents
  - Decomposes complex tasks

### multi-agent-orchestration (6 agents)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\.claude\agents\`

- **[build-agent.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/build-agent.md)**
  - Executes build workflows
  - Handles compilation and deployment

- **[docs-scraper.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/docs-scraper.md)**
  - Documentation scraping
  - Context extraction

- **[meta-agent.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/meta-agent.md)**
  - Multi-agent orchestration
  - Task decomposition and delegation

- **[playwright-validator.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/playwright-validator.md)**
  - E2E test validation
  - Browser automation testing

- **[scout-report-suggest.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/scout-report-suggest.md)**
  - Codebase scouting
  - Generates reports and suggestions

- **[scout-report-suggest-fast.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/.claude/agents/scout-report-suggest-fast.md)**
  - Fast scouting variant
  - Quick analysis

### orchestrator_3_stream (7 agents)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\apps\orchestrator_3_stream\.claude\agents\`

- build-agent.md
- docs-scraper.md
- meta-agent.md
- playwright-validator.md
- **[review-agent.md](file:///C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration/apps/orchestrator_3_stream/.claude/agents/review-agent.md)** (unique)
- scout-report-suggest.md
- scout-report-suggest-fast.md

## Agent Design Patterns

### 1. Single-Purpose Agent
Simple prompt that does one thing well.
Example: `docs-scraper` - only scrapes and extracts documentation

### 2. Workflow Agent
Executes multi-step workflows with state.
Example: `build-agent` - plan → implement → test → report

### 3. Meta Agent
Orchestrates other agents dynamically.
Example: `meta-agent` - analyzes task → spawns appropriate agents

### 4. Validator Agent
Verifies outputs from other processes.
Example: `playwright-validator` - runs E2E tests to validate UI

## Related Resources

- [Consulting-co Agents](file:///C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/agents/) - Local project agents
- [Building Specialized Agents Course](file:///C:/Users/gblac/OneDrive/Desktop/tac/building-specialized-agents/README.md)
