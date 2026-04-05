"""
Lightweight ADW Script Parser

Extracts only what matters for agentic orchestration:
- Which prompt files are referenced
- Which agent API calls are made
- Purpose from docstring

Does NOT analyze internal logic deeply - that's application code!
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ADWScriptEntity:
    """Represents an ADW (AI Developer Workflow) script"""
    name: str
    file_path: str
    purpose: Optional[str] = None
    prompts_invoked: List[str] = field(default_factory=list)
    agent_calls: List[str] = field(default_factory=list)
    mcp_tools_used: List[str] = field(default_factory=list)


class ADWScriptParser:
    """
    Light parser for ADW orchestration scripts

    Only extracts:
    1. Prompt file references
    2. Agent API calls
    3. Purpose/docstring
    """

    # Patterns for finding prompt file references
    PROMPT_FILE_PATTERNS = [
        r'["\']([^"\']*\.md)["\']',                    # Any .md file in quotes
        r'Path\(["\']([^"\']*\.claude[^"\']*)["\']',  # Path to .claude directory
        r'read_prompt\(["\']([^"\']*)["\']',          # read_prompt() calls
        r'open\(["\']([^"\']*\.md)["\']',             # open() with .md files
    ]

    # Patterns for agent/LLM API calls
    AGENT_CALL_PATTERNS = [
        r'anthropic\.(?:Client|messages)',
        r'openai\.(?:Client|ChatCompletion)',
        r'claude\.(?:run|execute)',
        r'agent\.(?:run|execute|invoke)',
    ]

    def parse_script(self, py_path: Path) -> ADWScriptEntity:
        """
        Parse an ADW Python script

        Args:
            py_path: Path to .py file

        Returns:
            ADWScriptEntity with extracted orchestration info
        """
        py_path = Path(py_path)

        with open(py_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse AST for docstring
        try:
            tree = ast.parse(content)
            purpose = ast.get_docstring(tree)
        except:
            purpose = None

        # Find prompt file references (use regex on content)
        prompt_refs = self._find_prompt_references(content)

        # Find agent API calls
        agent_calls = self._find_agent_calls(content)

        # Find MCP tool usage
        mcp_tools = self._find_mcp_tools(content)

        return ADWScriptEntity(
            name=py_path.stem,
            file_path=str(py_path),
            purpose=purpose,
            prompts_invoked=list(set(prompt_refs)),
            agent_calls=list(set(agent_calls)),
            mcp_tools_used=list(set(mcp_tools))
        )

    def _find_prompt_references(self, content: str) -> List[str]:
        """Find references to .md prompt files"""
        refs = []

        for pattern in self.PROMPT_FILE_PATTERNS:
            matches = re.findall(pattern, content)
            refs.extend(matches)

        return refs

    def _find_agent_calls(self, content: str) -> List[str]:
        """Find agent/LLM API calls"""
        calls = []

        for pattern in self.AGENT_CALL_PATTERNS:
            if re.search(pattern, content):
                calls.append(pattern.split('.')[0])  # Get the module name

        return calls

    def _find_mcp_tools(self, content: str) -> List[str]:
        """
        Find MCP tool usage
        Looks for tool invocations like: use_mcp_tool("tool_name")
        """
        tools = []

        # Pattern for MCP tool calls
        patterns = [
            r'use_mcp_tool\(["\'](\w+)["\']',
            r'mcp\.(?:call|invoke)\(["\'](\w+)["\']',
            r'tools\[["\'](\w+)["\']\]',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            tools.extend(matches)

        return tools


def parse_adw_scripts(directory: Path) -> List[ADWScriptEntity]:
    """
    Parse all ADW scripts in a directory

    Looks in:
    - scripts/
    - adws/
    - workflows/

    Args:
        directory: Root directory

    Returns:
        List of ADWScriptEntity objects
    """
    parser = ADWScriptParser()
    scripts = []

    directory = Path(directory)

    search_patterns = [
        'scripts/*.py',
        'adws/*.py',
        'workflows/*.py',
    ]

    for pattern in search_patterns:
        for py_file in directory.glob(pattern):
            # Skip __init__.py and test files
            if py_file.name.startswith('__') or py_file.name.startswith('test_'):
                continue

            try:
                script = parser.parse_script(py_file)
                scripts.append(script)
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")

    return scripts


if __name__ == "__main__":
    # Test on tac-2
    import sys

    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")

    print(f"Parsing ADW scripts from: {directory}")
    scripts = parse_adw_scripts(directory)

    print(f"\nFound {len(scripts)} ADW scripts:")
    for script in scripts:
        print(f"\n{'='*60}")
        print(f"Name: {script.name}")
        print(f"File: {script.file_path}")
        if script.purpose:
            print(f"Purpose: {script.purpose[:100]}...")
        print(f"Prompts invoked: {script.prompts_invoked}")
        print(f"Agent calls: {script.agent_calls}")
        print(f"MCP tools: {script.mcp_tools_used}")
