# GitHub Actions CI + Eval System for Greg Trading Workspace

**Target repo**: `gblack686/greg-trading-workspace`
**Date**: 2026-03-18
**Status**: Implementation spec -- hand directly to Claude Code agent

---

## 1. Objectives

1. Run OpenClaw trading skills as GitHub Actions workflows using `anthropics/claude-code-action@v1`
2. Score every skill execution with a structured eval system (0.0--1.0)
3. Gate first-run skills behind Discord approval before they run autonomously
4. Route outputs to dedicated Discord channels via webhooks
5. Self-improve skills that score below 0.85 or get rejected by Greg

---

## 2. Repo Structure

```
greg-trading-workspace/
|-- .github/
|   |-- workflows/
|   |   |-- claude.yml              # Interactive: @claude in issues/PRs + build trigger
|   |   |-- skill-runner.yml        # Cron + manual: runs trading skills
|   |   +-- eval-reporter.yml       # Posts eval results to Discord
|   |-- CODEOWNERS                  # Greg approves all PRs to main
|   +-- pull_request_template.md
|-- config/
|   |-- discord-channels.json       # Skill -> Discord channel webhook mapping
|   |-- eval-criteria.json          # Per-skill-type eval weights
|   +-- schedules.json              # Cron schedule registry
|-- evals/
|   |-- .gitkeep                    # Eval JSONs land here: evals/{skill-name}/{run-id}.json
|   +-- _aggregate/                 # Weekly rollup reports
|-- scripts/
|   |-- eval-scorer.py              # Compute eval_score from criteria
|   |-- discord-notify.py           # Post to Discord via webhook
|   |-- approval-gate.py            # Check if skill is approved, post to Discord if not
|   +-- self-improve.py             # Open GitHub issue for failing skills
|-- skills/                         # OpenClaw SKILL.md files (mirrors workspace/skills/)
|   |-- execution/
|   |   +-- apex-trade-executor/SKILL.md
|   |-- risk/
|   |   |-- risk-guard-sl-audit/SKILL.md
|   |   +-- manage-risk/SKILL.md
|   |-- intelligence/
|   |   |-- signal-scout/SKILL.md
|   |   |-- news-scout/SKILL.md
|   |   +-- youtube-scout/SKILL.md
|   |-- analytics/
|   |   |-- quant-backtest/SKILL.md
|   |   +-- chart-maker/SKILL.md
|   |-- operations/
|   |   |-- morning-brief/SKILL.md
|   |   |-- paper-trader/SKILL.md
|   |   +-- health-check/SKILL.md
|   +-- build/
|       +-- self-improve/SKILL.md
|-- CLAUDE.md                       # Repo-level Claude Code instructions
+-- README.md
```

---

## 3. OAuth Token Setup

### How the token flows

Greg has a Claude Code OAuth token (`sk-ant-oat01-...`) stored in AWS Secrets Manager at `gbautomation/core/anthropic-api-key`. The existing `claude-test.yml` in consulting-co already proves this works:

```yaml
claude_code_oauth_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
```

### Setup steps for the new repo

1. Retrieve the token from AWS Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id gbautomation/core/anthropic-api-key \
     --query SecretString --output text
   ```

2. Store it as a GitHub Actions secret named `CLAUDE_ACCESS_TOKEN` on `gblack686/greg-trading-workspace`:
   ```bash
   gh secret set CLAUDE_ACCESS_TOKEN --repo gblack686/greg-trading-workspace
   ```

3. Store Discord webhook URLs as secrets:
   ```bash
   gh secret set DISCORD_WEBHOOK_EXECUTION --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_RISK --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_MORNING_BRIEF --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_SIGNAL_FEED --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_ANALYTICS --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_NEWS_FEED --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_BUILD_LOG --repo gblack686/greg-trading-workspace
   gh secret set DISCORD_WEBHOOK_APPROVAL_QUEUE --repo gblack686/greg-trading-workspace
   ```

4. The action input is `claude_code_oauth_token` (not `anthropic_api_key`). This is confirmed by the existing `claude-test.yml` and `adw-plan-build-review.yml` in consulting-co. Do NOT set `ANTHROPIC_API_KEY` as an env var -- it conflicts with the CLI's own auth.

---

## 4. Workflow YAML Files

### 4.1 claude.yml -- Interactive Build Trigger

Handles `@claude` mentions in issues/PRs and manual skill build requests.

```yaml
name: Claude Build Agent

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  workflow_dispatch:
    inputs:
      skill_name:
        description: 'Skill to build (e.g. risk-guard-sl-audit)'
        required: true
      task_description:
        description: 'What to build or improve'
        required: true

permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write

jobs:
  # ---- Interactive mode: @claude in issues/PRs ----
  claude-interactive:
    if: >
      (github.event_name == 'issue_comment' || github.event_name == 'pull_request_review_comment')
      && contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
          github_token: ${{ secrets.GITHUB_TOKEN }}

  # ---- Manual skill build ----
  build-skill:
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create worktree branch
        run: |
          BRANCH="build/${{ github.event.inputs.skill_name }}-$(date +%s)"
          git checkout -b "$BRANCH"
          echo "BRANCH=$BRANCH" >> $GITHUB_ENV

      - name: Install Claude CLI
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Build skill with Claude
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
        run: |
          ~/.local/bin/claude -p "You are building a skill for the Greg Trading workspace.

          Skill: ${{ github.event.inputs.skill_name }}
          Task: ${{ github.event.inputs.task_description }}

          Read CLAUDE.md for repo conventions.
          Read config/eval-criteria.json for the eval criteria this skill must satisfy.
          Read existing skills in skills/ for format examples.

          Build the skill following OpenClaw SKILL.md format.
          Ensure no hardcoded secrets -- use env var references.
          Include an approval gate for any trade execution steps.

          After building, create a draft eval in evals/${{ github.event.inputs.skill_name }}/draft.json
          with all criteria fields set to null (to be filled on first run)." \
          --allowedTools "Read,Write,Edit,Glob,Grep,Bash" \
          --dangerously-skip-permissions

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --staged --quiet || git commit -m "build: ${{ github.event.inputs.skill_name }}"
          git push -u origin "$BRANCH"

      - name: Open PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create \
            --title "Build: ${{ github.event.inputs.skill_name }}" \
            --body "Auto-built by Claude.

          **Skill**: ${{ github.event.inputs.skill_name }}
          **Task**: ${{ github.event.inputs.task_description }}

          Review the SKILL.md and eval criteria before merging." \
            --base main \
            --head "$BRANCH"

      - name: Notify Discord build-log
        if: always()
        run: |
          python scripts/discord-notify.py \
            --channel build-log \
            --title "Skill Build: ${{ github.event.inputs.skill_name }}" \
            --status "${{ job.status }}" \
            --url "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        env:
          DISCORD_WEBHOOKS: ${{ toJSON(secrets) }}
```

### 4.2 skill-runner.yml -- Cron + Manual Skill Execution

Runs trading skills on schedule or manual dispatch. Each run produces an eval JSON.

```yaml
name: Skill Runner

on:
  schedule:
    # Risk Guard SL audit -- every 15 minutes
    - cron: '*/15 * * * *'
    # Morning brief -- 6:00 AM PT = 13:00 UTC (14:00 UTC during DST)
    - cron: '0 13 * * *'
    # Nightly backtest -- 2:00 AM PT = 09:00 UTC (10:00 UTC during DST)
    - cron: '0 10 * * *'
    # Weekly performance review -- Sunday 10:00 PM PT = Monday 05:00 UTC
    - cron: '0 5 * * 1'
    # Dataset scout -- Sunday 10:00 PM PT = Monday 06:00 UTC
    - cron: '0 6 * * 1'

  workflow_dispatch:
    inputs:
      skill_name:
        description: 'Skill to run (e.g. morning-brief, risk-guard-sl-audit)'
        required: true
        type: choice
        options:
          - morning-brief
          - risk-guard-sl-audit
          - manage-risk
          - signal-scout
          - news-scout
          - youtube-scout
          - quant-backtest
          - chart-maker
          - paper-trader
          - health-check
          - apex-trade-executor
      extra_context:
        description: 'Additional context for the skill run'
        required: false
        default: ''

permissions:
  contents: write
  issues: write
  id-token: write

jobs:
  resolve-skill:
    runs-on: ubuntu-latest
    outputs:
      skill_name: ${{ steps.resolve.outputs.skill_name }}
      discord_channel: ${{ steps.resolve.outputs.discord_channel }}
    steps:
      - uses: actions/checkout@v4
        with:
          sparse-checkout: |
            config/schedules.json
            config/discord-channels.json

      - name: Resolve which skill to run
        id: resolve
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            SKILL="${{ github.event.inputs.skill_name }}"
          else
            # Map cron schedule to skill name
            CRON="${{ github.event.schedule }}"
            case "$CRON" in
              "*/15 * * * *") SKILL="risk-guard-sl-audit" ;;
              "0 13 * * *")  SKILL="morning-brief" ;;
              "0 10 * * *")  SKILL="quant-backtest" ;;
              "0 5 * * 1")   SKILL="weekly-performance-review" ;;
              "0 6 * * 1")   SKILL="dataset-scout" ;;
              *)             SKILL="unknown"; echo "::warning::Unknown cron: $CRON" ;;
            esac
          fi
          echo "skill_name=$SKILL" >> $GITHUB_OUTPUT

          # Look up Discord channel from config
          CHANNEL=$(python3 -c "
          import json
          with open('config/discord-channels.json') as f:
              channels = json.load(f)
          print(channels.get('$SKILL', {}).get('channel', 'build-log'))
          ")
          echo "discord_channel=$CHANNEL" >> $GITHUB_OUTPUT

  run-skill:
    needs: resolve-skill
    if: needs.resolve-skill.outputs.skill_name != 'unknown'
    runs-on: ubuntu-latest
    env:
      SKILL_NAME: ${{ needs.resolve-skill.outputs.skill_name }}
      RUN_ID: ${{ github.run_id }}-${{ github.run_attempt }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests

      - name: Check approval gate
        id: approval
        run: |
          python scripts/approval-gate.py \
            --skill "$SKILL_NAME" \
            --evals-dir evals/ \
            --output approval-status.json

          APPROVED=$(python3 -c "import json; print(json.load(open('approval-status.json'))['approved'])")
          echo "approved=$APPROVED" >> $GITHUB_OUTPUT

      - name: Install Claude CLI
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Execute skill
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_ACCESS_TOKEN }}
        run: |
          SKILL_PATH=$(find skills/ -name "SKILL.md" -path "*${SKILL_NAME}*" | head -1)
          if [ -z "$SKILL_PATH" ]; then
            echo "::error::No SKILL.md found for $SKILL_NAME"
            exit 1
          fi

          EXTRA="${{ github.event.inputs.extra_context }}"

          ~/.local/bin/claude -p "You are executing a trading skill in the Greg Trading workspace.

          SKILL FILE: $SKILL_PATH
          Read it now and follow its workflow exactly.

          Additional context: ${EXTRA:-none}

          CRITICAL RULES:
          - NEVER execute live trades. All trade actions are proposals only.
          - Log all outputs to evals/${SKILL_NAME}/${RUN_ID}-output.json
          - Include timestamps on all data points.
          - If any API call fails, log the failure and continue with remaining steps.

          After execution, produce an eval self-assessment JSON at:
            evals/${SKILL_NAME}/${RUN_ID}.json

          The eval JSON must follow this schema:
          {
            \"skill_name\": \"${SKILL_NAME}\",
            \"run_id\": \"${RUN_ID}\",
            \"timestamp\": \"<ISO 8601>\",
            \"trigger\": \"${{ github.event_name }}\",
            \"criteria\": {
              // Fill in the criteria from config/eval-criteria.json for this skill type
              // Each criterion: { \"passed\": true/false, \"detail\": \"...\" }
            },
            \"eval_score\": <0.0-1.0 weighted average>,
            \"summary\": \"<one paragraph>\",
            \"approved\": <look up from evals/ whether this skill has been approved>
          }" \
          --allowedTools "Read,Write,Edit,Glob,Grep,Bash,WebSearch" \
          --dangerously-skip-permissions

      - name: Commit eval results
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add evals/
          git diff --staged --quiet || git commit -m "eval: ${SKILL_NAME} run ${RUN_ID}"
          git push || echo "Push failed -- will retry"
          git pull --rebase && git push || true

      - name: Upload eval artifact
        uses: actions/upload-artifact@v4
        with:
          name: eval-${{ env.SKILL_NAME }}-${{ env.RUN_ID }}
          path: evals/${{ env.SKILL_NAME }}/
          retention-days: 30

      - name: Trigger eval reporter
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'eval-reporter.yml',
              ref: 'main',
              inputs: {
                skill_name: '${{ env.SKILL_NAME }}',
                run_id: '${{ env.RUN_ID }}',
                discord_channel: '${{ needs.resolve-skill.outputs.discord_channel }}',
                job_status: '${{ job.status }}'
              }
            });
```

### 4.3 eval-reporter.yml -- Discord Posting + Self-Improvement Trigger

```yaml
name: Eval Reporter

on:
  workflow_dispatch:
    inputs:
      skill_name:
        required: true
        type: string
      run_id:
        required: true
        type: string
      discord_channel:
        required: true
        type: string
      job_status:
        required: true
        type: string

permissions:
  contents: read
  issues: write

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests

      - name: Load eval and compute score
        id: eval
        run: |
          EVAL_FILE="evals/${{ inputs.skill_name }}/${{ inputs.run_id }}.json"
          if [ ! -f "$EVAL_FILE" ]; then
            echo "::warning::No eval file found at $EVAL_FILE"
            echo "eval_score=0.0" >> $GITHUB_OUTPUT
            echo "needs_improvement=true" >> $GITHUB_OUTPUT
            echo "first_run=false" >> $GITHUB_OUTPUT
            exit 0
          fi

          python scripts/eval-scorer.py \
            --eval-file "$EVAL_FILE" \
            --criteria-file config/eval-criteria.json \
            --output eval-result.json

          SCORE=$(python3 -c "import json; print(json.load(open('eval-result.json'))['eval_score'])")
          FIRST_RUN=$(python3 -c "import json; print(json.load(open('eval-result.json')).get('first_run', False))")
          echo "eval_score=$SCORE" >> $GITHUB_OUTPUT
          echo "first_run=$FIRST_RUN" >> $GITHUB_OUTPUT

          if python3 -c "exit(0 if $SCORE < 0.85 else 1)"; then
            echo "needs_improvement=true" >> $GITHUB_OUTPUT
          else
            echo "needs_improvement=false" >> $GITHUB_OUTPUT
          fi

      - name: Post to skill-specific Discord channel
        run: |
          python scripts/discord-notify.py \
            --channel "${{ inputs.discord_channel }}" \
            --skill "${{ inputs.skill_name }}" \
            --run-id "${{ inputs.run_id }}" \
            --score "${{ steps.eval.outputs.eval_score }}" \
            --status "${{ inputs.job_status }}" \
            --eval-file "evals/${{ inputs.skill_name }}/${{ inputs.run_id }}.json" \
            --url "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        env:
          DISCORD_WEBHOOK_EXECUTION: ${{ secrets.DISCORD_WEBHOOK_EXECUTION }}
          DISCORD_WEBHOOK_RISK: ${{ secrets.DISCORD_WEBHOOK_RISK }}
          DISCORD_WEBHOOK_MORNING_BRIEF: ${{ secrets.DISCORD_WEBHOOK_MORNING_BRIEF }}
          DISCORD_WEBHOOK_SIGNAL_FEED: ${{ secrets.DISCORD_WEBHOOK_SIGNAL_FEED }}
          DISCORD_WEBHOOK_ANALYTICS: ${{ secrets.DISCORD_WEBHOOK_ANALYTICS }}
          DISCORD_WEBHOOK_NEWS_FEED: ${{ secrets.DISCORD_WEBHOOK_NEWS_FEED }}
          DISCORD_WEBHOOK_BUILD_LOG: ${{ secrets.DISCORD_WEBHOOK_BUILD_LOG }}
          DISCORD_WEBHOOK_APPROVAL_QUEUE: ${{ secrets.DISCORD_WEBHOOK_APPROVAL_QUEUE }}

      - name: Post to approval queue (first run only)
        if: steps.eval.outputs.first_run == 'True'
        run: |
          python scripts/discord-notify.py \
            --channel "approval-queue" \
            --skill "${{ inputs.skill_name }}" \
            --run-id "${{ inputs.run_id }}" \
            --score "${{ steps.eval.outputs.eval_score }}" \
            --status "${{ inputs.job_status }}" \
            --first-run \
            --eval-file "evals/${{ inputs.skill_name }}/${{ inputs.run_id }}.json" \
            --url "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        env:
          DISCORD_WEBHOOK_APPROVAL_QUEUE: ${{ secrets.DISCORD_WEBHOOK_APPROVAL_QUEUE }}

      - name: Open improvement issue (low score)
        if: steps.eval.outputs.needs_improvement == 'true'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          SCORE="${{ steps.eval.outputs.eval_score }}"
          gh issue create \
            --title "needs-improvement: ${{ inputs.skill_name }} scored $SCORE" \
            --body "## Eval Report

          **Skill**: ${{ inputs.skill_name }}
          **Run ID**: ${{ inputs.run_id }}
          **Score**: $SCORE (threshold: 0.85)
          **Status**: ${{ inputs.job_status }}

          ### Eval Details
          \`\`\`json
          $(cat evals/${{ inputs.skill_name }}/${{ inputs.run_id }}.json 2>/dev/null || echo '{}')
          \`\`\`

          ### Action Required
          @claude Please analyze this eval failure and improve the skill.
          Read the SKILL.md, the eval criteria, and the eval output.
          Fix the issues and open a PR.

          cc @gblack686" \
            --label "needs-improvement,auto-eval"
```

---

## 5. Eval JSON Schema

```typescript
interface EvalResult {
  // Identity
  skill_name: string;           // e.g. "risk-guard-sl-audit"
  run_id: string;               // e.g. "12345678-1"
  timestamp: string;            // ISO 8601
  trigger: "schedule" | "workflow_dispatch" | "issue_comment";
  duration_seconds: number;

  // Criteria -- keys vary by skill_type
  criteria: Record<string, {
    passed: boolean;
    weight: number;             // 0.0-1.0, from eval-criteria.json
    detail: string;             // human-readable explanation
  }>;

  // Aggregate
  eval_score: number;           // 0.0-1.0, weighted average of criteria
  summary: string;              // one paragraph natural language summary

  // Approval tracking
  approved: boolean;            // false until Greg approves first run
  approved_by: string | null;   // "greg" or null
  approved_at: string | null;   // ISO 8601 or null

  // Lineage
  previous_run_id: string | null;
  improvement_issue: number | null;  // GitHub issue number if this was a re-run
}
```

### Criteria by Skill Type

These live in `config/eval-criteria.json`:

```json
{
  "execution": {
    "fill_detected": { "weight": 0.25, "description": "Trade fill event was detected from exchange API" },
    "sl_placed_within_5s": { "weight": 0.25, "description": "Stop-loss order placed within 5 seconds of fill" },
    "slippage_within_threshold": { "weight": 0.20, "description": "Slippage was within configured threshold (e.g. 0.1%)" },
    "plan_saved_to_supabase": { "weight": 0.15, "description": "Trade plan record saved to Supabase" },
    "telegram_notification_sent": { "weight": 0.15, "description": "Trade notification delivered to Greg via Telegram" }
  },
  "risk": {
    "all_positions_have_sl": { "weight": 0.30, "description": "Every open position has a stop-loss set" },
    "drawdown_within_limits": { "weight": 0.25, "description": "Portfolio drawdown is within configured threshold" },
    "alerts_fired_correctly": { "weight": 0.20, "description": "Alerts were sent for all flagged conditions" },
    "data_freshness": { "weight": 0.15, "description": "Position data fetched within last 5 minutes" },
    "no_duplicate_alerts": { "weight": 0.10, "description": "No duplicate alerts within 30-minute window" }
  },
  "intelligence": {
    "signals_parsed": { "weight": 0.25, "description": "Signals parsed with all required fields" },
    "score_above_threshold": { "weight": 0.25, "description": "Signal quality score above 0.7" },
    "telegram_delivered": { "weight": 0.20, "description": "High-quality signals delivered to Greg" },
    "no_duplicates": { "weight": 0.15, "description": "No duplicate signals from same source within 1 hour" },
    "source_attribution": { "weight": 0.15, "description": "Every signal has a source channel/URL" }
  },
  "analytics": {
    "data_completeness": { "weight": 0.25, "description": "No gaps in OHLCV data for requested range" },
    "metrics_calculated": { "weight": 0.25, "description": "All 5 core metrics present (return, Sharpe, drawdown, win rate, avg P&L)" },
    "chart_rendered": { "weight": 0.20, "description": "Chart PNG generated without errors" },
    "report_delivered": { "weight": 0.15, "description": "Report delivered via Telegram or saved to memory" },
    "statistical_significance": { "weight": 0.15, "description": "Minimum trade count for valid results (>30)" }
  },
  "operations": {
    "brief_delivered": { "weight": 0.25, "description": "Morning brief or report delivered successfully" },
    "all_sections_present": { "weight": 0.25, "description": "All required sections included in output" },
    "data_sources_healthy": { "weight": 0.20, "description": "All data sources returned valid data" },
    "within_time_window": { "weight": 0.15, "description": "Skill completed within expected time window" },
    "no_stale_data": { "weight": 0.15, "description": "No data older than staleness threshold used" }
  },
  "build": {
    "skill_has_required_sections": { "weight": 0.20, "description": "SKILL.md has name, description, workflow, output format, error handling" },
    "no_hardcoded_secrets": { "weight": 0.25, "description": "No API keys, tokens, or credentials in code" },
    "approval_gate_present": { "weight": 0.20, "description": "Trade execution steps have [APPROVAL GATE] markers" },
    "testnet_validated": { "weight": 0.20, "description": "Skill tested against testnet or paper trading mode" },
    "eval_criteria_defined": { "weight": 0.15, "description": "Eval criteria JSON exists for this skill" }
  }
}
```

### Skill-to-Type Mapping

Lives in `config/discord-channels.json` (see next section) alongside channel mapping.

---

## 6. Discord Channel Config

`config/discord-channels.json`:

```json
{
  "_comment": "Maps skill names to Discord channels and skill types. Webhook URLs are in GitHub Secrets, not here.",

  "apex-trade-executor": {
    "channel": "execution-approvals",
    "webhook_secret": "DISCORD_WEBHOOK_EXECUTION",
    "skill_type": "execution"
  },
  "risk-guard-sl-audit": {
    "channel": "risk-alerts",
    "webhook_secret": "DISCORD_WEBHOOK_RISK",
    "skill_type": "risk"
  },
  "manage-risk": {
    "channel": "risk-alerts",
    "webhook_secret": "DISCORD_WEBHOOK_RISK",
    "skill_type": "risk"
  },
  "morning-brief": {
    "channel": "morning-brief",
    "webhook_secret": "DISCORD_WEBHOOK_MORNING_BRIEF",
    "skill_type": "operations"
  },
  "signal-scout": {
    "channel": "signal-feed",
    "webhook_secret": "DISCORD_WEBHOOK_SIGNAL_FEED",
    "skill_type": "intelligence"
  },
  "news-scout": {
    "channel": "news-feed",
    "webhook_secret": "DISCORD_WEBHOOK_NEWS_FEED",
    "skill_type": "intelligence"
  },
  "youtube-scout": {
    "channel": "news-feed",
    "webhook_secret": "DISCORD_WEBHOOK_NEWS_FEED",
    "skill_type": "intelligence"
  },
  "quant-backtest": {
    "channel": "analytics",
    "webhook_secret": "DISCORD_WEBHOOK_ANALYTICS",
    "skill_type": "analytics"
  },
  "chart-maker": {
    "channel": "analytics",
    "webhook_secret": "DISCORD_WEBHOOK_ANALYTICS",
    "skill_type": "analytics"
  },
  "paper-trader": {
    "channel": "execution-approvals",
    "webhook_secret": "DISCORD_WEBHOOK_EXECUTION",
    "skill_type": "execution"
  },
  "health-check": {
    "channel": "build-log",
    "webhook_secret": "DISCORD_WEBHOOK_BUILD_LOG",
    "skill_type": "operations"
  },
  "weekly-performance-review": {
    "channel": "analytics",
    "webhook_secret": "DISCORD_WEBHOOK_ANALYTICS",
    "skill_type": "analytics"
  },
  "dataset-scout": {
    "channel": "analytics",
    "webhook_secret": "DISCORD_WEBHOOK_ANALYTICS",
    "skill_type": "analytics"
  },

  "_default": {
    "channel": "build-log",
    "webhook_secret": "DISCORD_WEBHOOK_BUILD_LOG",
    "skill_type": "build"
  }
}
```

---

## 7. Scripts

### 7.1 scripts/eval-scorer.py

```python
"""
Reads an eval JSON, loads criteria weights from eval-criteria.json,
computes the weighted eval_score, and determines if this is a first run.
"""
import json
import argparse
import os
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-file", required=True)
    parser.add_argument("--criteria-file", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.eval_file) as f:
        eval_data = json.load(f)

    with open(args.criteria_file) as f:
        all_criteria = json.load(f)

    skill_name = eval_data["skill_name"]

    # Determine skill type from discord-channels.json
    channels_file = os.path.join(os.path.dirname(args.criteria_file), "discord-channels.json")
    with open(channels_file) as f:
        channels = json.load(f)
    skill_type = channels.get(skill_name, channels["_default"])["skill_type"]

    # Get weights for this skill type
    type_criteria = all_criteria.get(skill_type, {})

    # Compute weighted score
    total_weight = 0.0
    weighted_sum = 0.0
    for criterion_name, criterion_config in type_criteria.items():
        weight = criterion_config["weight"]
        eval_criterion = eval_data.get("criteria", {}).get(criterion_name, {})
        passed = eval_criterion.get("passed", False)
        total_weight += weight
        if passed:
            weighted_sum += weight

    eval_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Check if first run (no prior evals for this skill)
    evals_dir = os.path.dirname(args.eval_file)
    existing_evals = glob.glob(os.path.join(evals_dir, "*.json"))
    # Exclude the current eval and any drafts
    prior_evals = [
        e for e in existing_evals
        if os.path.basename(e) != os.path.basename(args.eval_file)
        and "draft" not in os.path.basename(e)
    ]
    first_run = len(prior_evals) == 0

    result = {
        "eval_score": round(eval_score, 4),
        "first_run": first_run,
        "skill_type": skill_type,
        "criteria_evaluated": len(type_criteria),
        "criteria_passed": sum(
            1 for c in type_criteria
            if eval_data.get("criteria", {}).get(c, {}).get("passed", False)
        ),
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

### 7.2 scripts/discord-notify.py

```python
"""
Posts formatted eval results to a Discord channel via webhook.
Webhook URLs are read from environment variables.
"""
import json
import argparse
import os
import requests

CHANNEL_TO_ENV = {
    "execution-approvals": "DISCORD_WEBHOOK_EXECUTION",
    "risk-alerts": "DISCORD_WEBHOOK_RISK",
    "morning-brief": "DISCORD_WEBHOOK_MORNING_BRIEF",
    "signal-feed": "DISCORD_WEBHOOK_SIGNAL_FEED",
    "analytics": "DISCORD_WEBHOOK_ANALYTICS",
    "news-feed": "DISCORD_WEBHOOK_NEWS_FEED",
    "build-log": "DISCORD_WEBHOOK_BUILD_LOG",
    "approval-queue": "DISCORD_WEBHOOK_APPROVAL_QUEUE",
}

def post_to_discord(webhook_url: str, embed: dict):
    payload = {"embeds": [embed]}
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--score", type=float, default=0.0)
    parser.add_argument("--status", default="unknown")
    parser.add_argument("--title", default=None)
    parser.add_argument("--eval-file", default=None)
    parser.add_argument("--url", default="")
    parser.add_argument("--first-run", action="store_true")
    args = parser.parse_args()

    env_key = CHANNEL_TO_ENV.get(args.channel, "DISCORD_WEBHOOK_BUILD_LOG")
    webhook_url = os.environ.get(env_key)
    if not webhook_url:
        print(f"WARNING: No webhook URL found for {env_key}, skipping Discord post")
        return

    # Color: green if score >= 0.85, yellow if >= 0.5, red otherwise
    if args.score >= 0.85:
        color = 0x2ECC71  # green
    elif args.score >= 0.5:
        color = 0xF39C12  # yellow
    else:
        color = 0xE74C3C  # red

    title = args.title or f"Eval: {args.skill}"
    if args.first_run:
        title = f"FIRST RUN -- APPROVAL NEEDED: {args.skill}"
        color = 0x3498DB  # blue

    # Load eval details if available
    detail_text = ""
    if args.eval_file and os.path.exists(args.eval_file):
        with open(args.eval_file) as f:
            eval_data = json.load(f)
        criteria = eval_data.get("criteria", {})
        lines = []
        for name, info in criteria.items():
            icon = "PASS" if info.get("passed") else "FAIL"
            lines.append(f"{icon} {name}: {info.get('detail', 'N/A')}")
        detail_text = "\n".join(lines[:10])  # cap at 10 lines

    embed = {
        "title": title,
        "color": color,
        "fields": [
            {"name": "Skill", "value": args.skill, "inline": True},
            {"name": "Score", "value": f"{args.score:.2f}", "inline": True},
            {"name": "Status", "value": args.status, "inline": True},
            {"name": "Run ID", "value": args.run_id, "inline": False},
        ],
        "url": args.url,
    }

    if detail_text:
        embed["description"] = f"```\n{detail_text}\n```"

    if args.first_run:
        embed["footer"] = {
            "text": "React to approve: Checkmark=Approve | X=Reject | Warning=Modify"
        }

    post_to_discord(webhook_url, embed)
    print(f"Posted to #{args.channel}")

if __name__ == "__main__":
    main()
```

### 7.3 scripts/approval-gate.py

```python
"""
Checks whether a skill has been approved by looking at existing evals.
If no prior eval exists with approved=true, this is a first run.

Outputs a JSON file with { "approved": true/false, "first_run": true/false }
"""
import json
import argparse
import os
import glob

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--evals-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    skill_dir = os.path.join(args.evals_dir, args.skill)
    if not os.path.isdir(skill_dir):
        # No evals exist at all -- first run
        result = {"approved": False, "first_run": True}
    else:
        eval_files = sorted(glob.glob(os.path.join(skill_dir, "*.json")))
        eval_files = [f for f in eval_files if "draft" not in os.path.basename(f)]

        if not eval_files:
            result = {"approved": False, "first_run": True}
        else:
            # Check if any eval has approved=true
            approved = False
            for ef in eval_files:
                with open(ef) as f:
                    data = json.load(f)
                if data.get("approved", False):
                    approved = True
                    break
            result = {"approved": approved, "first_run": not approved}

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

### 7.4 scripts/self-improve.py

```python
"""
Called when a skill scores below 0.85 or is rejected.
Opens a GitHub issue tagged needs-improvement.
The claude.yml workflow will pick up the @claude mention in the issue body.
"""
import json
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--eval-file", required=True)
    parser.add_argument("--score", type=float, required=True)
    args = parser.parse_args()

    with open(args.eval_file) as f:
        eval_data = json.load(f)

    # Find failing criteria
    failures = []
    for name, info in eval_data.get("criteria", {}).items():
        if not info.get("passed", False):
            failures.append(f"- {name}: {info.get('detail', 'No detail')}")

    failures_text = "\n".join(failures) if failures else "No specific failures logged"

    body = f"""## Auto-Improvement Request

**Skill**: {args.skill}
**Score**: {args.score} (threshold: 0.85)
**Run ID**: {eval_data.get('run_id', 'unknown')}

### Failing Criteria
{failures_text}

### Summary
{eval_data.get('summary', 'No summary available')}

### Instructions
@claude Please:
1. Read the SKILL.md for `{args.skill}`
2. Read the eval output at `{args.eval_file}`
3. Read `config/eval-criteria.json` for the criteria definitions
4. Fix the issues causing the failures above
5. Open a PR with the improvements

Focus on the failing criteria. Do not change passing criteria behavior.
"""

    result = subprocess.run(
        [
            "gh", "issue", "create",
            "--title", f"needs-improvement: {args.skill} scored {args.score}",
            "--body", body,
            "--label", "needs-improvement,auto-eval",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error creating issue: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

---

## 8. CLAUDE.md for the Greg Trading Repo

This file goes in the repo root to give Claude Code context on every run.

```markdown
# Greg Trading Workspace -- Claude Code Instructions

## What This Is
Multi-agent Hyperliquid trading system built on OpenClaw.
Agents: Sebastian (supervisor), Apex (trade executor), Risk Guard, Quant,
Signal Scout, Volume Monitor, News Scout, Chart Maker, YouTube Scout, Paper Trader.

## CRITICAL SAFETY RULES
1. NEVER execute live trades on Hyperliquid. All trade actions are PROPOSALS ONLY.
2. NEVER expose API keys, tokens, or secrets in code or logs.
3. Every skill run MUST produce an eval JSON in evals/{skill-name}/{run-id}.json.
4. Skills that modify positions or place orders MUST have [APPROVAL GATE] markers.

## Repo Structure
- `skills/` -- OpenClaw SKILL.md files organized by type (execution, risk, intelligence, analytics, operations, build)
- `evals/` -- Eval result JSONs. One subdirectory per skill.
- `config/` -- discord-channels.json, eval-criteria.json, schedules.json
- `scripts/` -- Python utilities for eval scoring, Discord posting, approval gates
- `.github/workflows/` -- Three workflows: claude.yml, skill-runner.yml, eval-reporter.yml

## Eval System
- Every run produces `evals/{skill}/{run-id}.json`
- Score = weighted average of criteria (see config/eval-criteria.json)
- Threshold: 0.85 to auto-approve
- Below 0.85: GitHub issue opened with `needs-improvement` label
- First run of any skill: posted to #approval-queue Discord for Greg's sign-off

## Skill Format
Follow OpenClaw SKILL.md format. See existing skills in skills/ for examples.
Required sections: name, description, Allowed Tools, Workflow (phased), Output Format, Error Handling.

## Discord Channels
See config/discord-channels.json for skill-to-channel mapping.
Webhook URLs are stored as GitHub Secrets, never in code.
```

---

## 9. Build Order

### Phase 1: Foundation (do first)

| Step | What | Files |
|------|------|-------|
| 1.1 | Create the GitHub repo `gblack686/greg-trading-workspace` | `gh repo create` |
| 1.2 | Store `CLAUDE_ACCESS_TOKEN` as GitHub secret | `gh secret set` |
| 1.3 | Write `CLAUDE.md` | `CLAUDE.md` |
| 1.4 | Write config files | `config/discord-channels.json`, `config/eval-criteria.json` |
| 1.5 | Write the 4 Python scripts | `scripts/eval-scorer.py`, `discord-notify.py`, `approval-gate.py`, `self-improve.py` |
| 1.6 | Create `evals/.gitkeep` | `evals/.gitkeep` |
| 1.7 | Create `claude.yml` workflow | `.github/workflows/claude.yml` |

**Acceptance criteria for Phase 1:**
- Repo exists on GitHub with CLAUDE.md, config/, scripts/, evals/
- `CLAUDE_ACCESS_TOKEN` secret is set
- `claude.yml` can be triggered via `workflow_dispatch` and responds to `@claude` in issues

### Phase 2: Skill Runner

| Step | What | Files |
|------|------|-------|
| 2.1 | Port 3 skills from consulting-co workspace | `skills/operations/morning-brief/SKILL.md`, `skills/risk/risk-guard-sl-audit/SKILL.md`, `skills/operations/health-check/SKILL.md` |
| 2.2 | Write `skill-runner.yml` | `.github/workflows/skill-runner.yml` |
| 2.3 | Test with `workflow_dispatch` for `health-check` | Manual trigger |

**Acceptance criteria for Phase 2:**
- `skill-runner.yml` runs `health-check` via manual dispatch
- Eval JSON is committed to `evals/health-check/{run-id}.json`
- Cron schedules are defined (even if initially disabled for testing)

### Phase 3: Eval Reporter + Discord

| Step | What | Files |
|------|------|-------|
| 3.1 | Create Discord server with 8 channels | Discord setup |
| 3.2 | Create webhooks for each channel | Discord webhook setup |
| 3.3 | Store all webhook URLs as GitHub secrets | `gh secret set` (8 webhooks) |
| 3.4 | Write `eval-reporter.yml` | `.github/workflows/eval-reporter.yml` |
| 3.5 | Test end-to-end: dispatch health-check, verify Discord post | Manual test |

**Acceptance criteria for Phase 3:**
- Running `health-check` via dispatch produces a Discord embed in `#build-log`
- First run posts to `#approval-queue` with approval request
- Eval score is displayed correctly in the embed

### Phase 4: Self-Improvement Loop

| Step | What | Files |
|------|------|-------|
| 4.1 | Verify `@claude` trigger works on issues | Test with a manual issue |
| 4.2 | Run a skill that intentionally scores low | Test self-improve flow |
| 4.3 | Verify issue is created with `needs-improvement` label | Check GitHub issues |
| 4.4 | Verify Claude picks up the issue and opens a PR | Check PRs |

**Acceptance criteria for Phase 4:**
- Low-scoring eval creates a GitHub issue
- Claude responds to the `@claude` mention in the issue
- PR is opened with improvements
- Re-run scores higher

### Phase 5: Enable Cron + Remaining Skills

| Step | What | Files |
|------|------|-------|
| 5.1 | Port remaining skills from consulting-co workspace | All `skills/` subdirectories |
| 5.2 | Enable cron schedules (uncomment or set) | `.github/workflows/skill-runner.yml` |
| 5.3 | Monitor first 24h of cron runs | Check Actions tab + Discord |

**Acceptance criteria for Phase 5:**
- Risk Guard runs every 15 minutes and posts to `#risk-alerts`
- Morning brief runs at 6:00 AM PT and posts to `#morning-brief`
- All skills have eval JSONs accumulating in `evals/`
- No duplicate alerts within 30-minute windows

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OAuth token expiry | All workflows stop | Set up token rotation reminder. Store backup key in AWS SM. Monitor for auth failures in Actions. |
| 15-min cron = high Actions usage | Cost / rate limit | GitHub gives 2,000 free minutes/month for private repos. Risk Guard every 15m = ~2,880 runs/month. Consider running on self-hosted runner if cost is an issue. |
| Claude hallucinates eval scores | False positives | `eval-scorer.py` re-computes the score from criteria. Claude fills criteria pass/fail, but the aggregate score is computed deterministically. |
| Race condition on eval commits | Git push conflicts | The workflow does `git pull --rebase && git push` with retry. Unlikely to conflict since different skills write to different subdirectories. |
| Discord webhook rate limits | Missed notifications | Discord allows 30 requests/minute per webhook. Risk Guard at 4/hour is well within limits. |
| First-run approval relies on Discord reactions | No automated callback | Phase 1: Greg manually marks approved by editing the eval JSON (`approved: true`). Phase 2: Build a Discord bot that listens for reactions and commits the approval via GitHub API. |
| Self-improvement loop creates infinite issues | Issue spam | Add a check: if an open `needs-improvement` issue already exists for this skill, do not create another. Add a max-retries counter (3 attempts before requiring manual review). |
| GitHub Actions scheduled cron can be delayed 5-20 min | Risk Guard SL check timing | For truly time-critical checks (SL audit), consider a self-hosted runner or a separate always-on process. GitHub Actions cron is best-effort, not real-time. |

---

## 11. Discord Approval Flow (Detailed)

### Phase 1 (MVP -- Manual Approval)

1. Skill runs for the first time
2. Eval is posted to `#approval-queue` with embed showing score + criteria
3. Greg reviews on mobile
4. Greg edits `evals/{skill}/approved.json` with `{ "approved": true, "approved_by": "greg", "approved_at": "..." }`
5. Next run of skill-runner checks `approval-gate.py` and finds approval

### Phase 2 (Automated -- Discord Bot)

1. Same as above, but a Discord bot listens for reactions on the embed
2. Checkmark reaction triggers a GitHub API call: commits `approved.json` to the repo
3. X reaction triggers a `needs-improvement` issue
4. Warning reaction triggers an issue tagged `needs-modification` with a prompt for Greg to specify changes

The Discord bot is a separate piece of infrastructure (could be a Cloudflare Worker or a small Node.js service). Not in scope for Phase 1.

---

## 12. Cron Schedule Reference

| Skill | Cron (UTC) | Cron (PT) | Frequency |
|-------|-----------|-----------|-----------|
| risk-guard-sl-audit | `*/15 * * * *` | every 15 min | 96/day |
| morning-brief | `0 13 * * *` | 6:00 AM PT | daily |
| quant-backtest (nightly) | `0 10 * * *` | 2:00 AM PT | daily |
| weekly-performance-review | `0 5 * * 1` | Sun 9:00 PM PT | weekly |
| dataset-scout | `0 6 * * 1` | Sun 10:00 PM PT | weekly |

Note: PT offsets assume PST (UTC-8). During PDT (UTC-7), these shift by 1 hour. If exact timing matters, use two cron entries or adjust seasonally.

---

## 13. GitHub Secrets Checklist

| Secret Name | Source | Description |
|-------------|--------|-------------|
| `CLAUDE_ACCESS_TOKEN` | AWS SM `gbautomation/core/anthropic-api-key` | Claude Code OAuth token |
| `DISCORD_WEBHOOK_EXECUTION` | Discord channel settings | `#execution-approvals` webhook URL |
| `DISCORD_WEBHOOK_RISK` | Discord channel settings | `#risk-alerts` webhook URL |
| `DISCORD_WEBHOOK_MORNING_BRIEF` | Discord channel settings | `#morning-brief` webhook URL |
| `DISCORD_WEBHOOK_SIGNAL_FEED` | Discord channel settings | `#signal-feed` webhook URL |
| `DISCORD_WEBHOOK_ANALYTICS` | Discord channel settings | `#analytics` webhook URL |
| `DISCORD_WEBHOOK_NEWS_FEED` | Discord channel settings | `#news-feed` webhook URL |
| `DISCORD_WEBHOOK_BUILD_LOG` | Discord channel settings | `#build-log` webhook URL |
| `DISCORD_WEBHOOK_APPROVAL_QUEUE` | Discord channel settings | `#approval-queue` webhook URL |
