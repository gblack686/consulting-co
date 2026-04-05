#!/bin/bash

# Sync QuickStart Documentation
# This script syncs documentation from all QuickStart repos to the current directory
# Excludes cloud folders and only copies documentation files

set -e

SOURCE_DIR="claude-repos"
TARGET_BASE="."

echo "Starting QuickStart documentation sync..."
echo "=========================================="

# Array of QuickStart directories
QUICKSTARTS=(
    "quickstart-acme-test-claude"
    "quickstart-agentcore-claude"
    "quickstart-board-director-claude"
    "quickstart-compcorrect-claude"
    "quickstart-nexus-claude"
    "quickstart-parenting-autism-claude"
    "quickstart-perl-street-claude"
    "quickstart-word-collections-claude"
)

# Function to sync docs from a QuickStart
sync_quickstart_docs() {
    local qs_name=$1
    local source_path="${SOURCE_DIR}/${qs_name}"
    local target_path="${TARGET_BASE}/${qs_name}"

    if [ ! -d "$source_path" ]; then
        echo "⚠️  Skipping $qs_name - directory not found"
        return
    fi

    echo ""
    echo "📦 Syncing: $qs_name"
    echo "   Source: $source_path"
    echo "   Target: $target_path"

    # Create target directory if it doesn't exist
    mkdir -p "$target_path"

    # Find and copy all markdown files, excluding cloud folders and git directories
    local file_count=0
    while IFS= read -r -d '' file; do
        # Get relative path from source
        local rel_path="${file#${source_path}/}"
        local target_file="${target_path}/${rel_path}"

        # Create parent directory if needed
        mkdir -p "$(dirname "$target_file")"

        # Copy file
        cp "$file" "$target_file"
        ((file_count++))
    done < <(find "$source_path" -type f \( -name "*.md" -o -name "*.txt" \) \
        ! -path "*/cloud/*" \
        ! -path "*/.git/*" \
        ! -path "*/node_modules/*" \
        -print0)

    echo "   ✓ Copied $file_count documentation files"
}

# Sync all QuickStarts
for qs in "${QUICKSTARTS[@]}"; do
    sync_quickstart_docs "$qs"
done

echo ""
echo "=========================================="
echo "✅ QuickStart documentation sync complete!"
echo ""
echo "Documentation has been synced to:"
for qs in "${QUICKSTARTS[@]}"; do
    if [ -d "${TARGET_BASE}/${qs}" ]; then
        echo "  - ${qs}/"
    fi
done
