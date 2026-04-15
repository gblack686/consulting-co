#!/usr/bin/env bash
# deploy-spec.sh — Push a spec bundle to Mac Mini and kick off Claude Code pipeline
#
# Usage: ./deploy-spec.sh <spec-dir> [--dry-run] [--trees home,chat] [--mode generate]
#
# Example:
#   ./deploy-spec.sh specs/eagle-site
#   ./deploy-spec.sh specs/eagle-site --trees shared,home --mode generate
#   ./deploy-spec.sh specs/eagle-site --dry-run

set -euo pipefail

# ── Config ──
MAC_MINI_HOST="100.88.4.114"
MAC_MINI_USER="greg"
PATH_EXPORT="export PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/greg/.local/bin:\$PATH'"
CLAUDE_BIN="/opt/homebrew/bin/claude"
NOTIFY_CMD="openclaw message send --channel telegram --target 6777263736"

# ── Parse Args ──
SPEC_DIR="${1:?Usage: deploy-spec.sh <spec-dir> [--dry-run] [--trees x,y] [--mode generate]}"
DRY_RUN=false
TREES=""
MODE="generate"

shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --trees) TREES="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ── Read spec.yaml ──
if [[ ! -f "$SPEC_DIR/spec.yaml" ]]; then
  echo "Error: $SPEC_DIR/spec.yaml not found"
  exit 1
fi

# Extract target info from spec.yaml (using python for portable YAML parsing)
PYTHON=$(command -v python3 || command -v python)
REPO=$($PYTHON -c "
import yaml, sys
with open('$SPEC_DIR/spec.yaml') as f:
    spec = yaml.safe_load(f)
print(spec['target']['repo'])
")
REPO_PATH=$($PYTHON -c "
import yaml, sys
with open('$SPEC_DIR/spec.yaml') as f:
    spec = yaml.safe_load(f)
print(spec['target']['repo_path'])
")
BRAND=$($PYTHON -c "
import yaml, sys
with open('$SPEC_DIR/spec.yaml') as f:
    spec = yaml.safe_load(f)
print(spec['brand']['name'])
")
SPEC_NAME=$($PYTHON -c "
import yaml, sys
with open('$SPEC_DIR/spec.yaml') as f:
    spec = yaml.safe_load(f)
print(spec['name'])
")

echo "=== Deploy Spec: $SPEC_NAME ==="
echo "  Config repo: $CONFIG_REPO"
echo "  App repo: $APP_REPO"
echo "  Brand: $BRAND"
echo "  Trees: ${TREES:-all from spec}"
echo "  Mode: $MODE"
echo "  Dry run: $DRY_RUN"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[DRY RUN] Would SCP spec bundle to $MAC_MINI_USER@$MAC_MINI_HOST:$REPO_PATH/.codegen-spec/"
  echo "[DRY RUN] Would start Claude Code pipeline on Mac Mini"
  exit 0
fi

# ── Step 1: SCP spec bundle to Mac Mini ──
echo ">>> Step 1: Uploading spec bundle..."
REMOTE_SPEC_DIR="$REPO_PATH/.codegen-spec"

ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; mkdir -p $REMOTE_SPEC_DIR"
scp -r "$SPEC_DIR/"* "$MAC_MINI_USER@$MAC_MINI_HOST:$REMOTE_SPEC_DIR/"

echo "  Uploaded to $REMOTE_SPEC_DIR"

# ── Step 2: Update brand.yaml in the ui-agents tree ──
echo ">>> Step 2: Syncing brand files..."
BRAND_DIR="$REPO_PATH/apps/infinite-ui/src/brands/$BRAND"

ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; mkdir -p $BRAND_DIR/products/site"
scp "$SPEC_DIR/brand.yaml" "$MAC_MINI_USER@$MAC_MINI_HOST:$BRAND_DIR/brand.yaml"
scp "$SPEC_DIR/product.yaml" "$MAC_MINI_USER@$MAC_MINI_HOST:$BRAND_DIR/products/site/brand.yaml"
scp "$SPEC_DIR/trees.yaml" "$MAC_MINI_USER@$MAC_MINI_HOST:$BRAND_DIR/products/site/trees.yaml"

echo "  Brand files synced"

# ── Step 3: Build the Claude Code prompt ──
echo ">>> Step 3: Assembling pipeline prompt..."

# Determine which trees to generate
if [[ -n "$TREES" ]]; then
  TREE_LIST="$TREES"
else
  TREE_LIST=$($PYTHON -c "
import yaml
with open('$SPEC_DIR/spec.yaml') as f:
    spec = yaml.safe_load(f)
trees = spec.get('trees', {}).get('generate', ['all'])
print(','.join(trees))
")
fi

PROMPT="You are the Pipeline Orchestrator for the $SPEC_NAME code generation pipeline.

Your spec bundle is at: .codegen-spec/

Read these files in order:
1. .codegen-spec/spec.yaml — master manifest
2. .codegen-spec/brand.yaml — design tokens
3. .codegen-spec/product.yaml — product domain model
4. .codegen-spec/trees.yaml — component trees and branches to generate
5. .codegen-spec/agents/team.yaml — your team config
6. .codegen-spec/agents/prompts/orchestrator.md — your detailed instructions
7. .codegen-spec/agents/rules/acceptance.yaml — per-tree acceptance criteria
8. .codegen-spec/agents/rules/style-guide.yaml — coding conventions
9. .codegen-spec/reference/*.html — design reference files

Mode: $MODE
Trees to process: $TREE_LIST

Execute the pipeline as described in your orchestrator prompt. Generate Vue 3 SFC components for each branch of each specified tree, following the phased approach: generate → validate → fix → review.

Write components to: apps/infinite-ui/src/brands/$BRAND/products/site/trees/{tree}/{branch}.vue"

# ── Step 4: Launch Claude Code on Mac Mini ──
echo ">>> Step 4: Launching Claude Code on Mac Mini..."
echo "  Trees: $TREE_LIST"
echo "  Mode: $MODE"

# Notify start
ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; $NOTIFY_CMD --message '🦅 Eagle pipeline starting: trees=$TREE_LIST mode=$MODE'" 2>/dev/null || true

# Run Claude Code in print mode (non-interactive)
ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; cd $REPO_PATH && $CLAUDE_BIN -p \"$PROMPT\" --max-turns 50" 2>&1 | tee /tmp/eagle-pipeline-$(date +%Y%m%d-%H%M%S).log

RESULT=$?

# ── Step 5: Notify completion ──
if [[ $RESULT -eq 0 ]]; then
  echo ">>> Pipeline completed successfully"
  ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; $NOTIFY_CMD --message '✅ Eagle pipeline complete: trees=$TREE_LIST'" 2>/dev/null || true
else
  echo ">>> Pipeline failed (exit code $RESULT)"
  ssh "$MAC_MINI_USER@$MAC_MINI_HOST" "$PATH_EXPORT; $NOTIFY_CMD --message '❌ Eagle pipeline failed: trees=$TREE_LIST exit=$RESULT'" 2>/dev/null || true
fi

echo ""
echo "=== Done ==="
echo "Log: /tmp/eagle-pipeline-$(date +%Y%m%d-%H%M%S).log"
echo "Check results: ssh $MAC_MINI_USER@$MAC_MINI_HOST 'ls $REPO_PATH/apps/infinite-ui/src/brands/$BRAND/products/site/trees/'"
