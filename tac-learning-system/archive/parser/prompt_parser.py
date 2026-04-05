"""
Document-Centric Prompt Parser for TAC Agentic Codebases

Extracts structure from markdown prompts:
- Title and purpose
- Workflow sections
- Delegation references
- Tool mentions
- Success criteria
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import frontmatter


@dataclass
class PromptEntity:
    """Represents a TAC prompt file"""
    name: str
    file_path: str
    content: str
    sections: Dict[str, str] = field(default_factory=dict)
    workflow_steps: List[str] = field(default_factory=list)
    delegations: List[str] = field(default_factory=list)
    tools_mentioned: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    prompt_type: str = "unknown"


class PromptParser:
    """Parse TAC markdown prompt files"""

    # Common section headers in TAC prompts
    SECTION_PATTERNS = [
        r'^##\s+(Context|Background|Overview|Purpose)',
        r'^##\s+(Workflow|Steps|Process|Plan)',
        r'^##\s+(Success Criteria|Done When|Completion)',
        r'^##\s+(Tools|Requirements|Dependencies)',
        r'^##\s+(Usage|Example|How to Use)',
        r'^##\s+(Notes|Important|Warnings)',
    ]

    # Patterns for finding delegations to other prompts
    DELEGATION_PATTERNS = [
        r'/(\w+[-\w]*)',                    # /slash-command
        r'@(\w+[-\w]*)',                    # @mention
        r'use (?:the )?`?([/\w-]+)`?',      # "use the xyz" or "use /xyz"
        r'delegate to `?([/\w-]+)`?',       # "delegate to xyz"
        r'run `?/([/\w-]+)`?',              # "run /command"
        r'\.claude/commands/(\w+[-\w]*)\.md', # direct file reference
    ]

    # Patterns for tool mentions
    TOOL_PATTERNS = [
        r'MCP Server:?\s*(\w+)',
        r'uses? (?:the )?(\w+) MCP',
        r'`(\w+)` tool',
        r'@mcp[:\s]+(\w+)',
    ]

    def parse_prompt_file(self, md_path: Path) -> PromptEntity:
        """
        Parse a TAC prompt markdown file and extract structured data

        Args:
            md_path: Path to .md file

        Returns:
            PromptEntity with extracted structure
        """
        md_path = Path(md_path)

        # Parse frontmatter and content
        with open(md_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        metadata = post.metadata if hasattr(post, 'metadata') else {}
        content = post.content if hasattr(post, 'content') else str(post)

        # Extract title (first # heading)
        title = self._extract_title(content)
        if not title:
            title = md_path.stem

        # Extract sections
        sections = self._extract_sections(content)

        # Extract workflow steps
        workflow_steps = self._extract_workflow_steps(
            sections.get('Workflow', sections.get('Steps', ''))
        )

        # Find delegations to other prompts
        delegations = self._find_delegations(content)

        # Extract tool mentions
        tools = self._extract_tool_mentions(content)

        # Extract success criteria
        success_criteria = self._extract_success_criteria(
            sections.get('Success Criteria', sections.get('Done When', ''))
        )

        # Classify prompt type
        prompt_type = self._classify_prompt(content, workflow_steps, delegations)

        return PromptEntity(
            name=title,
            file_path=str(md_path),
            content=content,
            sections=sections,
            workflow_steps=workflow_steps,
            delegations=list(set(delegations)),  # Remove duplicates
            tools_mentioned=list(set(tools)),
            success_criteria=success_criteria,
            metadata=metadata,
            prompt_type=prompt_type
        )

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from first # heading"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract content by section headers
        Returns dict of section_name -> section_content
        """
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # Check if this is a section header (## Header)
            section_match = re.match(r'^##\s+(.+)$', line)

            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = section_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _extract_workflow_steps(self, workflow_text: str) -> List[str]:
        """
        Extract ordered workflow steps from text
        Looks for numbered or bulleted lists
        """
        if not workflow_text:
            return []

        steps = []

        # Pattern for numbered steps (1. , 2. , etc.)
        numbered_pattern = r'^\s*\d+\.\s+(.+)$'

        # Pattern for bulleted steps (-, *, +)
        bullet_pattern = r'^\s*[-*+]\s+(.+)$'

        for line in workflow_text.split('\n'):
            # Try numbered first
            match = re.match(numbered_pattern, line)
            if match:
                steps.append(match.group(1).strip())
                continue

            # Try bulleted
            match = re.match(bullet_pattern, line)
            if match:
                steps.append(match.group(1).strip())

        return steps

    def _find_delegations(self, content: str) -> List[str]:
        """
        Find references to other prompts
        Returns list of prompt names that this delegates to
        """
        delegations = []

        for pattern in self.DELEGATION_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                delegation = match.group(1).strip()
                # Clean up leading slashes
                delegation = delegation.lstrip('/')
                if delegation:
                    delegations.append(delegation)

        return delegations

    def _extract_tool_mentions(self, content: str) -> List[str]:
        """Find mentions of MCP tools or other dependencies"""
        tools = []

        for pattern in self.TOOL_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            tools.extend(match.group(1).strip() for match in matches)

        return tools

    def _extract_success_criteria(self, criteria_text: str) -> List[str]:
        """
        Extract success criteria from section text
        Looks for checkbox lists or bullet points
        """
        if not criteria_text:
            return []

        criteria = []

        # Pattern for checkbox items (- [ ] or - [x])
        checkbox_pattern = r'^\s*-\s*\[[x ]\]\s+(.+)$'

        # Pattern for regular bullets
        bullet_pattern = r'^\s*[-*+]\s+(.+)$'

        for line in criteria_text.split('\n'):
            # Try checkbox first
            match = re.match(checkbox_pattern, line, re.IGNORECASE)
            if match:
                criteria.append(match.group(1).strip())
                continue

            # Try bullet
            match = re.match(bullet_pattern, line)
            if match:
                criteria.append(match.group(1).strip())

        return criteria

    def _classify_prompt(self, content: str, workflow_steps: List[str],
                        delegations: List[str]) -> str:
        """
        Classify prompt type based on structure:
        - simple-task: Single purpose, no workflow
        - simple-workflow: 1-3 steps
        - complex-workflow: 4+ steps
        - orchestration: 3+ delegations
        - meta-prompt: Generates other prompts
        """
        content_lower = content.lower()

        # Check for meta-prompt
        if 'generate a prompt' in content_lower or 'create a prompt' in content_lower:
            return 'meta-prompt'

        # Check for orchestration (many delegations)
        if len(delegations) >= 3:
            return 'orchestration'

        # Check workflow complexity
        if workflow_steps:
            if len(workflow_steps) <= 3:
                return 'simple-workflow'
            else:
                return 'complex-workflow'

        return 'simple-task'


def parse_tac_directory(directory: Path) -> List[PromptEntity]:
    """
    Parse all prompt files in a TAC directory

    Looks in:
    - .claude/commands/*.md
    - specs/*.md
    - prompts/*.md
    - workflows/*.md

    Args:
        directory: Root directory of TAC repo

    Returns:
        List of PromptEntity objects
    """
    parser = PromptParser()
    prompts = []

    directory = Path(directory)

    # Common locations for prompts in TAC repos
    search_patterns = [
        '.claude/commands/*.md',
        'specs/*.md',
        'prompts/*.md',
        'workflows/*.md',
        'adws/*.md',
    ]

    for pattern in search_patterns:
        for md_file in directory.glob(pattern):
            try:
                prompt = parser.parse_prompt_file(md_file)
                prompts.append(prompt)
            except Exception as e:
                print(f"Error parsing {md_file}: {e}")

    return prompts


if __name__ == "__main__":
    # Test on tac-2
    import sys

    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")

    print(f"Parsing prompts from: {directory}")
    prompts = parse_tac_directory(directory)

    print(f"\nFound {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"\n{'='*60}")
        print(f"Name: {prompt.name}")
        print(f"Type: {prompt.prompt_type}")
        print(f"File: {prompt.file_path}")
        print(f"Workflow steps: {len(prompt.workflow_steps)}")
        print(f"Delegations: {prompt.delegations}")
        print(f"Tools: {prompt.tools_mentioned}")
        if prompt.workflow_steps:
            print("\nWorkflow:")
            for i, step in enumerate(prompt.workflow_steps, 1):
                print(f"  {i}. {step[:80]}...")
