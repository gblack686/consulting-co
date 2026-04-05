#!/usr/bin/env python3
"""
Fix for message_start parser bug in claude-agent-sdk.

The SDK's message_parser.py doesn't handle "message_start" events,
causing MessageParseError. This script adds support for message_start
by treating it as a SystemMessage (metadata event).
"""

import sys
import os
from pathlib import Path

def patch_message_parser():
    # Find the parser file in the user's site-packages
    home = Path.home()
    parser_file = home / ".local" / "lib" / "python3.12" / "site-packages" / "claude_agent_sdk" / "_internal" / "message_parser.py"
    
    if not parser_file.exists():
        # Try to find it via import
        try:
            import claude_agent_sdk
            sdk_path = Path(claude_agent_sdk.__file__).parent
            parser_file = sdk_path / "_internal" / "message_parser.py"
            if not parser_file.exists():
                print(f"❌ Parser file not found at {parser_file}")
                return False
        except Exception as e:
            print(f"❌ Could not locate parser file: {e}")
            return False
    
    print(f"📝 Found parser file: {parser_file}")
    
    # Backup original
    backup_file = parser_file.with_suffix('.py.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy2(parser_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    else:
        print(f"ℹ️  Backup already exists: {backup_file}")
    
    # Read the file
    with open(parser_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if '"message_start"' in content and 'case "message_start":' in content:
        print("✅ message_start already handled in parser")
        return True
    
    # Find the location to insert (before the default case)
    lines = content.split('\n')
    new_lines = []
    i = 0
    inserted = False
    
    while i < len(lines):
        line = lines[i]
        
        # Look for the default case "case _:"
        if not inserted and line.strip() == 'case _:':
            # Insert message_start handler before default case
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            new_lines.append(f'{indent_str}case "message_start":')
            new_lines.append(f'{indent_str}    # message_start is a metadata event, treat as SystemMessage')
            new_lines.append(f'{indent_str}    try:')
            new_lines.append(f'{indent_str}        return SystemMessage(')
            new_lines.append(f'{indent_str}            subtype="message_start",')
            new_lines.append(f'{indent_str}            data=data,')
            new_lines.append(f'{indent_str}        )')
            new_lines.append(f'{indent_str}    except KeyError as e:')
            new_lines.append(f'{indent_str}        raise MessageParseError(')
            new_lines.append(f'{indent_str}            f"Missing required field in message_start: {{e}}", data')
            new_lines.append(f'{indent_str}        ) from e')
            new_lines.append('')
            inserted = True
        
        new_lines.append(line)
        i += 1
    
    if not inserted:
        print("❌ Could not find default case (case _:) in parser file")
        return False
    
    # Write the patched content
    new_content = '\n'.join(new_lines)
    with open(parser_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Successfully patched message_parser.py to handle message_start events")
    return True

if __name__ == '__main__':
    success = patch_message_parser()
    sys.exit(0 if success else 1)







