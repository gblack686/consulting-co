#!/bin/bash
# Langfuse trace utility wrapper
# Usage:
#   traces list [--limit N] [--project-id ID]
#   traces get --trace-id ID
#   traces projects

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/langfuse_api.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: langfuse_api.py not found at $PYTHON_SCRIPT"
    exit 1
fi

# Use Python to run the API client
python3 "$PYTHON_SCRIPT" "$@"
