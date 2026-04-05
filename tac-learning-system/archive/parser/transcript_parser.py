"""
Transcript Parser for TAC Lessons

Extracts concepts, frameworks, and tactics from lesson transcripts.
Uses pattern matching and semantic analysis to identify:
- Key concepts and definitions
- Frameworks (The Core Four, 12 Leverage Points)
- Tactics (Adopt your agent's perspective)
- Patterns and best practices
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class Concept:
    """A concept extracted from transcript"""
    name: str
    definition: str
    category: str  # framework, tactic, pattern, principle, tool
    lesson_number: int
    transcript_lines: Tuple[int, int]  # (start, end)
    related_concepts: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class Framework:
    """A framework like 'The Core Four' or '12 Leverage Points'"""
    name: str
    description: str
    components: List[str]
    lesson_number: int
    transcript_lines: Tuple[int, int]


@dataclass
class Tactic:
    """A TAC tactic"""
    number: int
    name: str
    description: str
    lesson_number: int
    why_important: str = ""
    transcript_lines: Tuple[int, int] = (0, 0)


class TranscriptParser:
    """Parse TAC lesson transcripts to extract concepts"""

    # Patterns for identifying key concepts
    CONCEPT_PATTERNS = [
        # "The X is Y" definitions
        (r'(?:the )?(\w+(?:\s+\w+){0,3})\s+(?:is|are|means?)\s+(.+?)\.', 'definition'),

        # "We call this X" introductions
        (r'(?:we call|this is|known as|called)\s+(?:the )?(\w+(?:\s+\w+){0,3})', 'introduction'),

        # Numbered concepts: "1. X", "First, Y"
        (r'(?:^|\n)(\d+)\.\s+([^.]+)', 'enumeration'),
        (r'(?:first|second|third|fourth|fifth),?\s+(.+?)(?:\.|,|\n)', 'enumeration'),
    ]

    # Known frameworks from TAC
    KNOWN_FRAMEWORKS = {
        'core four': ['Context', 'Model', 'Prompt', 'Tools'],
        'software development lifecycle': ['Plan', 'Code', 'Test', 'Review', 'Document'],
        '12 leverage points': [
            'Context', 'Model', 'Prompt', 'Tools',  # Core 4
            'Documentation', 'Types', 'Architecture', 'Tests',  # Through-agent
            'Planning', 'ADWs', 'KPIs', 'Agentic Layer'  # Meta-level
        ],
    }

    def parse_transcript(self, transcript_path: Path, lesson_number: int) -> Dict:
        """
        Parse a lesson transcript and extract all concepts

        Returns:
            Dict with concepts, frameworks, tactics, and metadata
        """
        transcript_path = Path(transcript_path)

        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # Extract different types of content
        concepts = self._extract_concepts(lines, lesson_number)
        frameworks = self._extract_frameworks(lines, lesson_number)
        tactics = self._extract_tactics(lines, lesson_number)

        return {
            'lesson_number': lesson_number,
            'transcript_file': str(transcript_path),
            'concepts': [self._concept_to_dict(c) for c in concepts],
            'frameworks': [self._framework_to_dict(f) for f in frameworks],
            'tactics': [self._tactic_to_dict(t) for t in tactics],
            'metadata': {
                'total_lines': len(lines),
                'concept_count': len(concepts),
                'framework_count': len(frameworks),
                'tactic_count': len(tactics),
            }
        }

    def _extract_concepts(self, lines: List[str], lesson_number: int) -> List[Concept]:
        """Extract concepts from transcript lines"""
        concepts = []
        text = ' '.join(lines)

        # Known concepts to look for (from context)
        known_concepts = {
            'core four': 'The four fundamental elements agents need: Context, Model, Prompt, and Tools',
            'software development lifecycle': 'The five steps: Plan, Code, Test, Review, Document',
            'agentic coding': 'Building systems that operate autonomously on your behalf',
            'leverage points': 'Areas where small changes create big impact in agentic systems',
            'agent perspective': 'Understanding that agents are brilliant but blind - they need your context',
        }

        # Search for known concepts in text
        for concept_name, definition in known_concepts.items():
            # Find where this concept is mentioned
            pattern = re.compile(r'\b' + re.escape(concept_name) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))

            if matches:
                # Get approximate line numbers
                first_match_pos = matches[0].start()
                chars_before = text[:first_match_pos].count('\n')

                # Extract surrounding context for better definition
                start_pos = max(0, first_match_pos - 200)
                end_pos = min(len(text), first_match_pos + 200)
                context = text[start_pos:end_pos]

                # Try to find definition in context
                found_def = self._extract_definition_from_context(context, concept_name)
                if found_def:
                    definition = found_def

                concept = Concept(
                    name=concept_name.title(),
                    definition=definition,
                    category='framework' if 'framework' in concept_name.lower() or 'cycle' in concept_name.lower() else 'principle',
                    lesson_number=lesson_number,
                    transcript_lines=(chars_before, chars_before + 10),
                    keywords=[word for word in concept_name.split()]
                )
                concepts.append(concept)

        return concepts

    def _extract_definition_from_context(self, context: str, concept_name: str) -> Optional[str]:
        """Try to extract definition from surrounding context"""
        # Pattern: "X is Y"
        pattern = re.compile(
            r'\b' + re.escape(concept_name) + r'\s+(?:is|are|means?)\s+([^.]+)\.',
            re.IGNORECASE
        )
        match = pattern.search(context)
        if match:
            return match.group(1).strip()
        return None

    def _extract_frameworks(self, lines: List[str], lesson_number: int) -> List[Framework]:
        """Extract frameworks like The Core Four"""
        frameworks = []
        text = ' '.join(lines).lower()

        for framework_name, components in self.KNOWN_FRAMEWORKS.items():
            if framework_name in text:
                # Find line number
                line_num = 0
                for i, line in enumerate(lines):
                    if framework_name in line.lower():
                        line_num = i
                        break

                # Create description based on known framework
                descriptions = {
                    'core four': 'The four fundamental elements agents need to operate like you',
                    'software development lifecycle': 'The compressed SDLC for agentic coding: Plan, Code, Test, Review, Document',
                    '12 leverage points': 'The 12 areas where you can maximize agent effectiveness'
                }

                framework = Framework(
                    name=framework_name.title(),
                    description=descriptions.get(framework_name, ''),
                    components=components,
                    lesson_number=lesson_number,
                    transcript_lines=(line_num, line_num + 20)
                )
                frameworks.append(framework)

        return frameworks

    def _extract_tactics(self, lines: List[str], lesson_number: int) -> List[Tactic]:
        """Extract TAC tactics from transcript"""
        tactics = []
        text = ' '.join(lines)

        # Pattern: "tactic [number]: [name]" or "adopt your agent's perspective"
        tactic_patterns = [
            r'tactic\s+(\d+)[:\s]+([^.]+)',
            r'our\s+(?:lesson\s+\d+\s+)?tactic[:\s]+([^.]+)',
        ]

        for pattern in tactic_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2 and match.group(1).isdigit():
                    tactic_num = int(match.group(1))
                    tactic_name = match.group(2).strip()
                else:
                    tactic_num = lesson_number  # Use lesson number if not explicit
                    tactic_name = match.group(1).strip()

                # Find line number
                line_num = text[:match.start()].count('\n')

                # Extract why it's important (look ahead in text)
                why_text = text[match.end():match.end()+300]
                why_match = re.search(r'why[?:\s]+([^.]+)\.', why_text, re.IGNORECASE)
                why_important = why_match.group(1) if why_match else ""

                tactic = Tactic(
                    number=tactic_num,
                    name=tactic_name,
                    description=f"Tactic {tactic_num}: {tactic_name}",
                    lesson_number=lesson_number,
                    why_important=why_important,
                    transcript_lines=(line_num, line_num + 10)
                )
                tactics.append(tactic)

        return tactics

    def _concept_to_dict(self, concept: Concept) -> Dict:
        """Convert Concept to dict for JSON"""
        return {
            'name': concept.name,
            'definition': concept.definition,
            'category': concept.category,
            'lesson_number': concept.lesson_number,
            'transcript_lines': {
                'start': concept.transcript_lines[0],
                'end': concept.transcript_lines[1]
            },
            'related_concepts': concept.related_concepts,
            'keywords': concept.keywords
        }

    def _framework_to_dict(self, framework: Framework) -> Dict:
        """Convert Framework to dict"""
        return {
            'name': framework.name,
            'description': framework.description,
            'components': framework.components,
            'lesson_number': framework.lesson_number,
            'transcript_lines': {
                'start': framework.transcript_lines[0],
                'end': framework.transcript_lines[1]
            }
        }

    def _tactic_to_dict(self, tactic: Tactic) -> Dict:
        """Convert Tactic to dict"""
        return {
            'number': tactic.number,
            'name': tactic.name,
            'description': tactic.description,
            'lesson_number': tactic.lesson_number,
            'why_important': tactic.why_important,
            'transcript_lines': {
                'start': tactic.transcript_lines[0],
                'end': tactic.transcript_lines[1]
            }
        }


def parse_lesson_transcript(transcript_path: Path, lesson_number: int, output_path: Optional[Path] = None):
    """
    Parse a lesson transcript and save concepts to JSON

    Args:
        transcript_path: Path to transcript file
        lesson_number: Lesson number (e.g., 2)
        output_path: Where to save output JSON (optional)
    """
    import json

    parser = TranscriptParser()
    result = parser.parse_transcript(transcript_path, lesson_number)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        print(f"Saved concepts to: {output_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"LESSON {lesson_number} CONCEPT EXTRACTION")
    print(f"{'='*60}")
    print(f"Transcript: {transcript_path.name}")
    print(f"Concepts found: {result['metadata']['concept_count']}")
    print(f"Frameworks found: {result['metadata']['framework_count']}")
    print(f"Tactics found: {result['metadata']['tactic_count']}")

    print(f"\n{'='*60}")
    print("CONCEPTS:")
    print(f"{'='*60}")
    for concept in result['concepts']:
        print(f"\n📘 {concept['name']}")
        print(f"   Category: {concept['category']}")
        print(f"   Definition: {concept['definition'][:100]}...")

    print(f"\n{'='*60}")
    print("FRAMEWORKS:")
    print(f"{'='*60}")
    for framework in result['frameworks']:
        print(f"\n🎯 {framework['name']}")
        print(f"   {framework['description']}")
        print(f"   Components: {', '.join(framework['components'][:5])}...")

    print(f"\n{'='*60}")
    print("TACTICS:")
    print(f"{'='*60}")
    for tactic in result['tactics']:
        print(f"\n⚡ Tactic {tactic['number']}: {tactic['name']}")
        if tactic['why_important']:
            print(f"   Why: {tactic['why_important'][:80]}...")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        transcript_path = Path(sys.argv[1])
        lesson_num = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    else:
        transcript_path = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\indydevdan\vtts\the-12-leverage-points_transcript.txt")
        lesson_num = 2

    output_dir = Path(__file__).parent.parent / "data" / f"lesson-{lesson_num}"
    output_path = output_dir / "concepts.json"

    result = parse_lesson_transcript(transcript_path, lesson_num, output_path)
