#!/bin/bash
# ============================================================
# Sync All TAC .claude Ecosystems to Obsidian
# ============================================================
#
# This script processes all .claude directories from TAC projects
# and syncs them to the Obsidian AI-Agent-KB using Claude CLI.
#
# Usage:
#   ./sync-all-tac-ecosystems.sh           # Dry run (show commands)
#   ./sync-all-tac-ecosystems.sh --execute # Actually run syncs
#
# ============================================================

set -e

LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/tac-ecosystem-sync-$(date +%Y%m%d_%H%M%S).log"
EXECUTE_MODE=false

# Parse arguments
if [[ "$1" == "--execute" ]]; then
    EXECUTE_MODE=true
    echo "🚀 EXECUTE MODE: Will run actual syncs"
else
    echo "📋 DRY RUN MODE: Showing commands only (use --execute to run)"
fi

mkdir -p "$LOG_DIR"

# TAC directories to process
DIRECTORIES=(
    # TAC Course Projects (12)
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-experts/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandbox-skill/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/agent-sandboxes/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/agentic-finance-review/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/building-domain-specific-agents/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-damage-control/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/claude-code-hooks-mastery/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/fork-repository-skill/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/multi-agent-orchestration-the-o-agent/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/orchestrator-agent-with-adws/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/rd-framework-context-window-mastery/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/seven-levels-agentic-prompt-formats/.claude"

    # TAC Numbered Projects (7)
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-1/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-2/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-3/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-4/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-5/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-6/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-7/.claude"

    # TAC-8 Sub-Projects (5)
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app1__agent_layer_primitives/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app2__multi_agent_todone/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app3__out_loop_multi_agent_task_board/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app4__agentic_prototyping/.claude"
    "C:/Users/gblac/OneDrive/Desktop/tac/tac-8/tac8_app5__nlq_to_sql_aea/.claude"
)

TOTAL=${#DIRECTORIES[@]}
COUNT=0
SUCCESS=0
FAILED=0

echo ""
echo "============================================================"
echo "TAC Ecosystem Sync - Processing $TOTAL directories"
echo "============================================================"
echo ""

# Log header
{
    echo "============================================================"
    echo "TAC Ecosystem Sync Started: $(date)"
    echo "Mode: $([ "$EXECUTE_MODE" = true ] && echo "EXECUTE" || echo "DRY RUN")"
    echo "============================================================"
    echo ""
} >> "$LOG_FILE"

for DIR in "${DIRECTORIES[@]}"; do
    ((COUNT++))

    # Extract project name
    PROJECT=$(basename "$(dirname "$DIR")")

    echo "[$COUNT/$TOTAL] $PROJECT"
    echo "  Path: $DIR"

    if [ -d "$DIR" ]; then
        if [ "$EXECUTE_MODE" = true ]; then
            echo "  Status: Syncing..."

            # Run the sync command
            # Using claude CLI with the sync-claude-ecosystem skill
            if claude -p "/sync-claude-ecosystem $DIR" --dangerously-skip-permissions >> "$LOG_FILE" 2>&1; then
                echo "  Result: ✅ Success"
                ((SUCCESS++))
            else
                echo "  Result: ❌ Failed (check log)"
                ((FAILED++))
            fi
        else
            echo "  Command: claude -p \"/sync-claude-ecosystem $DIR\""
            echo "  Status: Ready (dry run)"
        fi
    else
        echo "  Status: ⚠️ Directory not found"
        ((FAILED++))
    fi

    echo ""

    # Log entry
    {
        echo "[$COUNT/$TOTAL] $PROJECT"
        echo "  Path: $DIR"
        echo "  Exists: $([ -d "$DIR" ] && echo "Yes" || echo "No")"
        echo ""
    } >> "$LOG_FILE"
done

echo "============================================================"
echo "Sync Complete"
echo "  Total: $TOTAL"
if [ "$EXECUTE_MODE" = true ]; then
    echo "  Success: $SUCCESS"
    echo "  Failed: $FAILED"
fi
echo "  Log: $LOG_FILE"
echo "============================================================"

# Log footer
{
    echo ""
    echo "============================================================"
    echo "Sync Complete: $(date)"
    echo "  Total: $TOTAL"
    [ "$EXECUTE_MODE" = true ] && echo "  Success: $SUCCESS"
    [ "$EXECUTE_MODE" = true ] && echo "  Failed: $FAILED"
    echo "============================================================"
} >> "$LOG_FILE"
