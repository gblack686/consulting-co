#!/bin/bash
# Fix for message_start parser bug in claude-agent-sdk
# This script patches the message_parser.py to handle message_start events

PARSER_FILE="$HOME/.local/lib/python3.12/site-packages/claude_agent_sdk/_internal/message_parser.py"

if [ ! -f "$PARSER_FILE" ]; then
    echo "❌ Parser file not found: $PARSER_FILE"
    exit 1
fi

# Backup original file
cp "$PARSER_FILE" "${PARSER_FILE}.backup"
echo "✅ Created backup: ${PARSER_FILE}.backup"

# Check if message_start is already handled
if grep -q '"message_start"' "$PARSER_FILE"; then
    echo "⚠️  message_start already handled in parser"
    exit 0
fi

# Find the line number of the case _: statement (the default case)
DEFAULT_CASE_LINE=$(grep -n 'case _:' "$PARSER_FILE" | cut -d: -f1)

if [ -z "$DEFAULT_CASE_LINE" ]; then
    echo "❌ Could not find default case in parser"
    exit 1
fi

# Create a temporary Python script to do the patching
python3 << 'PYTHON_PATCH'
import re

parser_file = "/home/gblac/.local/lib/python3.12/site-packages/claude_agent_sdk/_internal/message_parser.py"

with open(parser_file, 'r') as f:
    content = f.read()

# Check if already patched
if '"message_start"' in content:
    print("✅ message_start already handled")
    exit(0)

# Find the default case and add message_start handling before it
# message_start events are informational/metadata, so we'll handle them as SystemMessage
pattern = r'(\s+)case "stream_event":.*?(?=\s+case _:)'
replacement = r'\1case "stream_event":\n            try:\n                return StreamEvent(\n                    uuid=data["uuid"],\n                    session_id=data["session_id"],\n                    event=data["event"],\n                    parent_tool_use_id=data.get("parent_tool_use_id"),\n                )\n            except KeyError as e:\n                raise MessageParseError(\n                    f"Missing required field in stream_event message: {e}", data\n                ) from e\n\n        case "message_start":\n            # message_start is a metadata event, treat as SystemMessage\n            try:\n                return SystemMessage(\n                    subtype="message_start",\n                    data=data,\n                )\n            except KeyError as e:\n                raise MessageParseError(\n                    f"Missing required field in message_start: {e}", data\n                ) from e'

# Actually, let's use a simpler approach - find the case _: line and insert before it
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for the default case
    if re.match(r'\s+case _:', line):
        # Insert message_start handler before the default case
        indent = len(line) - len(line.lstrip())
        new_lines.append(f'{" " * indent}case "message_start":')
        new_lines.append(f'{" " * (indent + 4)}# message_start is a metadata event, treat as SystemMessage')
        new_lines.append(f'{" " * (indent + 4)}try:')
        new_lines.append(f'{" " * (indent + 8)}return SystemMessage(')
        new_lines.append(f'{" " * (indent + 12)}subtype="message_start",')
        new_lines.append(f'{" " * (indent + 12)}data=data,')
        new_lines.append(f'{" " * (indent + 8)})')
        new_lines.append(f'{" " * (indent + 4)}except KeyError as e:')
        new_lines.append(f'{" " * (indent + 8)}raise MessageParseError(')
        new_lines.append(f'{" " * (indent + 12)}f"Missing required field in message_start: {{e}}", data')
        new_lines.append(f'{" " * (indent + 8)}) from e')
        new_lines.append('')  # Empty line
    new_lines.append(line)
    i += 1

new_content = '\n'.join(new_lines)

with open(parser_file, 'w') as f:
    f.write(new_content)

print("✅ Successfully patched message_parser.py to handle message_start events")
PYTHON_PATCH

if [ $? -eq 0 ]; then
    echo "✅ Parser patch applied successfully"
else
    echo "❌ Failed to apply patch, restoring backup"
    cp "${PARSER_FILE}.backup" "$PARSER_FILE"
    exit 1
fi







