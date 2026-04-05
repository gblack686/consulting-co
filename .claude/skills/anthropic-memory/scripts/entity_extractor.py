"""
Anthropic Memory Tool - Entity Extractor

Uses Claude to extract structured entities from conversation transcripts.
Extracts: Files, Technologies, Concepts, Decisions
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from anthropic import Anthropic


class EntityExtractor:
    """Extract entities from conversation transcripts using Claude"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-haiku-4"):
        """
        Initialize entity extractor

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use (default: claude-haiku-4 for speed and cost)
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    def extract_from_transcript(self, transcript: str) -> Dict:
        """
        Extract entities from conversation transcript

        Args:
            transcript: Full conversation transcript (JSONL format or plain text)

        Returns:
            Dictionary with extracted entities
        """
        # Build extraction prompt
        prompt = self._build_extraction_prompt(transcript)

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        try:
            # Extract JSON from response
            content = response.content[0].text
            entities = json.loads(content)
            return entities
        except json.JSONDecodeError:
            # If not valid JSON, return empty structure
            return self._empty_entity_structure()

    def _build_extraction_prompt(self, transcript: str) -> str:
        """Build prompt for entity extraction"""
        return f"""Extract structured entities from this conversation transcript.

Analyze the conversation and extract:

1. **Files** - Code files, configuration files, documentation files mentioned
   - Include file paths when available
   - Note file type (e.g., Python, TypeScript, YAML)

2. **Technologies** - Frameworks, libraries, tools, languages used
   - Include version numbers if mentioned
   - Note what they're used for

3. **Concepts** - Patterns, techniques, architectural approaches discussed
   - Include brief descriptions
   - Note why they're important

4. **Decisions** - Architectural choices, design decisions made
   - Include rationale
   - Note alternatives considered

5. **Tools Used** - Which Claude tools were used (Read, Edit, Write, Bash, etc.)
   - Include usage count for each
   - Note what they were used for

6. **Key Learnings** - Important insights, best practices discovered
   - Actionable takeaways
   - Things to remember for future sessions

Return your analysis as valid JSON with this exact structure:

{{
  "files": [
    {{
      "path": "string",
      "type": "string",
      "description": "string"
    }}
  ],
  "technologies": [
    {{
      "name": "string",
      "category": "string (framework|library|tool|language)",
      "purpose": "string",
      "version": "string (optional)"
    }}
  ],
  "concepts": [
    {{
      "name": "string",
      "description": "string",
      "importance": "string"
    }}
  ],
  "decisions": [
    {{
      "decision": "string",
      "rationale": "string",
      "alternatives": ["string"],
      "impact": "string"
    }}
  ],
  "tools_used": {{
    "Read": {{"count": 0, "purpose": "string"}},
    "Write": {{"count": 0, "purpose": "string"}},
    "Edit": {{"count": 0, "purpose": "string"}},
    "Bash": {{"count": 0, "purpose": "string"}},
    "Grep": {{"count": 0, "purpose": "string"}},
    "Glob": {{"count": 0, "purpose": "string"}}
  }},
  "key_learnings": [
    {{
      "learning": "string",
      "actionable": "string"
    }}
  ],
  "tags": ["string"],
  "summary": "string (1-2 sentences)"
}}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just the JSON object.

---

Conversation Transcript:

{transcript}

---

Extract entities now:"""

    def _empty_entity_structure(self) -> Dict:
        """Return empty entity structure"""
        return {
            "files": [],
            "technologies": [],
            "concepts": [],
            "decisions": [],
            "tools_used": {},
            "key_learnings": [],
            "tags": [],
            "summary": ""
        }

    def extract_from_file(self, transcript_path: Path) -> Dict:
        """
        Extract entities from transcript file

        Args:
            transcript_path: Path to transcript file (JSONL)

        Returns:
            Dictionary with extracted entities
        """
        # Read transcript
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        # Handle JSONL format
        if transcript_path.suffix == ".jsonl":
            transcript = self._parse_jsonl_transcript(transcript_path)
        else:
            # Plain text
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()

        return self.extract_from_transcript(transcript)

    def _parse_jsonl_transcript(self, transcript_path: Path) -> str:
        """
        Parse JSONL transcript into readable format

        Args:
            transcript_path: Path to JSONL file

        Returns:
            Formatted transcript string
        """
        lines = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)

                    # Extract role and content
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")

                    # Handle different content formats
                    if isinstance(content, list):
                        # Multiple content blocks
                        for block in content:
                            if isinstance(block, dict):
                                block_type = block.get("type", "text")
                                if block_type == "text":
                                    lines.append(f"{role.upper()}: {block.get('text', '')}")
                                elif block_type == "tool_use":
                                    tool_name = block.get("name", "unknown")
                                    lines.append(f"[TOOL: {tool_name}]")
                                elif block_type == "tool_result":
                                    lines.append(f"[TOOL RESULT]")
                            else:
                                lines.append(f"{role.upper()}: {block}")
                    else:
                        # Simple string content
                        lines.append(f"{role.upper()}: {content}")

                except json.JSONDecodeError:
                    continue

        return "\n".join(lines)

    def generate_session_summary(
        self,
        entities: Dict,
        session_id: str,
        date: str
    ) -> str:
        """
        Generate markdown session summary from entities

        Args:
            entities: Extracted entities
            session_id: Session identifier
            date: Session date

        Returns:
            Markdown content for session file
        """
        # Build markdown content
        content = f"""# Session Summary

{entities.get('summary', 'No summary available')}

## Context

Session ID: {session_id}
Date: {date}

"""

        # Files
        if entities.get("files"):
            content += "## Files Involved\n\n"
            for file in entities["files"]:
                content += f"- **{file['path']}** ({file.get('type', 'unknown')})\n"
                if file.get("description"):
                    content += f"  - {file['description']}\n"
            content += "\n"

        # Technologies
        if entities.get("technologies"):
            content += "## Technologies Used\n\n"
            for tech in entities["technologies"]:
                version = f" v{tech['version']}" if tech.get("version") else ""
                content += f"- **{tech['name']}{version}** ({tech.get('category', 'unknown')})\n"
                if tech.get("purpose"):
                    content += f"  - {tech['purpose']}\n"
            content += "\n"

        # Concepts
        if entities.get("concepts"):
            content += "## Concepts Discussed\n\n"
            for concept in entities["concepts"]:
                content += f"- **{concept['name']}**\n"
                content += f"  - {concept.get('description', 'No description')}\n"
                if concept.get("importance"):
                    content += f"  - _Why it matters:_ {concept['importance']}\n"
            content += "\n"

        # Decisions
        if entities.get("decisions"):
            content += "## Decisions Made\n\n"
            for decision in entities["decisions"]:
                content += f"### {decision['decision']}\n\n"
                content += f"**Rationale:** {decision.get('rationale', 'Not specified')}\n\n"
                if decision.get("alternatives"):
                    content += f"**Alternatives Considered:** {', '.join(decision['alternatives'])}\n\n"
                if decision.get("impact"):
                    content += f"**Impact:** {decision['impact']}\n\n"

        # Tools Used
        if entities.get("tools_used"):
            content += "## Tools Used\n\n"
            for tool, info in entities["tools_used"].items():
                if isinstance(info, dict) and info.get("count", 0) > 0:
                    content += f"- **{tool}** ({info['count']}x) - {info.get('purpose', 'various operations')}\n"
            content += "\n"

        # Key Learnings
        if entities.get("key_learnings"):
            content += "## Key Learnings\n\n"
            for learning in entities["key_learnings"]:
                content += f"- {learning.get('learning', 'Unknown')}\n"
                if learning.get("actionable"):
                    content += f"  - _Action:_ {learning['actionable']}\n"
            content += "\n"

        return content


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: entity_extractor.py <transcript_path>")
        sys.exit(1)

    transcript_path = Path(sys.argv[1])

    # Extract entities
    extractor = EntityExtractor()
    entities = extractor.extract_from_file(transcript_path)

    # Print results
    print(json.dumps(entities, indent=2))

    # Generate summary
    summary = extractor.generate_session_summary(
        entities=entities,
        session_id="test",
        date="2026-01-11"
    )

    print("\n--- SESSION SUMMARY ---\n")
    print(summary)
