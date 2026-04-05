"""
TAC Repository Extractor - Simplified Version

Extracts:
- Prompts/Commands (.claude/commands/*.md)
- Agents (.claude/agents/*.md)
- ADW Workflows (adws/*.py)
- Concepts/Documentation (README.md, ai_docs/)

Does NOT extract (removed from original):
- AST/Code analysis
- Static analysis (Radon, Bandit)
- MCP server configs
"""

import os
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

# Try to import frontmatter for better markdown parsing
try:
    import frontmatter
    HAS_FRONTMATTER = True
except ImportError:
    HAS_FRONTMATTER = False
    print("Note: python-frontmatter not installed. Using basic parsing.")


@dataclass
class Command:
    """A slash command from .claude/commands/"""
    name: str
    file_path: str
    tac_source: str
    title: Optional[str] = None
    description: Optional[str] = None
    sections: list = None
    delegations: list = None  # Other commands/agents referenced


@dataclass
class Agent:
    """An agent template from .claude/agents/"""
    name: str
    file_path: str
    tac_source: str
    title: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None  # haiku, sonnet, opus
    tools: list = None  # Tools available to agent
    purpose: Optional[str] = None


@dataclass
class ADW:
    """An Agentic Development Workflow from adws/"""
    name: str
    file_path: str
    tac_source: str
    description: Optional[str] = None
    workflow_type: Optional[str] = None  # build, plan, test, etc.
    has_modules: bool = False
    has_triggers: bool = False
    has_tests: bool = False


@dataclass
class Concept:
    """A concept from documentation"""
    name: str
    source_file: str
    tac_source: str
    description: Optional[str] = None
    category: Optional[str] = None


class TACExtractor:
    """Simplified extractor for TAC repositories"""

    def __init__(self, tac_base_path: str):
        self.tac_base = Path(tac_base_path)
        self.results = {
            'commands': [],
            'agents': [],
            'adws': [],
            'concepts': [],
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'tac_base': str(self.tac_base)
            }
        }

    def extract_all(self) -> dict:
        """Extract from all TAC repositories"""
        tac_repos = self._find_tac_repos()

        for repo in tac_repos:
            repo_name = repo.name
            print(f"Processing {repo_name}...")

            # Extract commands
            commands = self._extract_commands(repo, repo_name)
            self.results['commands'].extend(commands)

            # Extract agents
            agents = self._extract_agents(repo, repo_name)
            self.results['agents'].extend(agents)

            # Extract ADWs
            adws = self._extract_adws(repo, repo_name)
            self.results['adws'].extend(adws)

            # Extract concepts from docs
            concepts = self._extract_concepts(repo, repo_name)
            self.results['concepts'].extend(concepts)

        # Add summary
        self.results['metadata']['summary'] = {
            'total_commands': len(self.results['commands']),
            'total_agents': len(self.results['agents']),
            'total_adws': len(self.results['adws']),
            'total_concepts': len(self.results['concepts']),
            'repos_processed': len(tac_repos)
        }

        return self.results

    def _find_tac_repos(self) -> list:
        """Find all TAC repository folders"""
        repos = []
        for item in self.tac_base.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                repos.append(item)
        return sorted(repos, key=lambda x: x.name)

    def _extract_commands(self, repo: Path, repo_name: str) -> list:
        """Extract slash commands from .claude/commands/"""
        commands = []
        commands_dir = repo / '.claude' / 'commands'

        if not commands_dir.exists():
            return commands

        for md_file in commands_dir.rglob('*.md'):
            cmd = self._parse_command(md_file, repo_name)
            if cmd:
                commands.append(asdict(cmd))

        return commands

    def _parse_command(self, file_path: Path, repo_name: str) -> Optional[Command]:
        """Parse a single command file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse frontmatter if available
            title = None
            description = None

            if HAS_FRONTMATTER:
                try:
                    post = frontmatter.loads(content)
                    title = post.get('title')
                    description = post.get('description')
                    content = post.content
                except:
                    pass

            # Extract title from first heading
            if not title:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()

            # Extract sections
            sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)

            # Find delegations (references to other commands/agents)
            delegations = []
            # /command references
            delegations.extend(re.findall(r'/(\w+)', content))
            # @agent references
            delegations.extend(re.findall(r'@(\w+)', content))
            # Remove common false positives
            delegations = [d for d in set(delegations)
                         if d not in ['param', 'return', 'example', 'note']]

            return Command(
                name=file_path.stem,
                file_path=str(file_path),
                tac_source=repo_name,
                title=title,
                description=description,
                sections=sections[:10] if sections else [],
                delegations=delegations[:10] if delegations else []
            )
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")
            return None

    def _extract_agents(self, repo: Path, repo_name: str) -> list:
        """Extract agent templates from .claude/agents/ and agents/"""
        agents = []

        # Check .claude/agents/
        agents_dir = repo / '.claude' / 'agents'
        if agents_dir.exists():
            for md_file in agents_dir.rglob('*.md'):
                agent = self._parse_agent(md_file, repo_name)
                if agent:
                    agents.append(asdict(agent))

        # Check root-level agents/ folder
        root_agents_dir = repo / 'agents'
        if root_agents_dir.exists():
            for md_file in root_agents_dir.rglob('*.md'):
                # Skip README files
                if md_file.stem.lower() == 'readme':
                    continue
                agent = self._parse_agent(md_file, repo_name)
                if agent:
                    agents.append(asdict(agent))
            # Also check for Python agent files
            for py_file in root_agents_dir.glob('*.py'):
                if py_file.stem.startswith('agent_'):
                    agent = self._parse_python_agent(py_file, repo_name)
                    if agent:
                        agents.append(asdict(agent))

        return agents

    def _parse_python_agent(self, file_path: Path, repo_name: str) -> Optional[Agent]:
        """Parse a Python agent file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract docstring
            description = None
            docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
            if docstring_match:
                description = docstring_match.group(1).strip()[:200]

            # Look for model selection
            model = None
            model_match = re.search(r'model\s*=\s*["\']?(claude-\d+-)?(\w+)', content)
            if model_match:
                model = model_match.group(2).lower()

            return Agent(
                name=file_path.stem,
                file_path=str(file_path),
                tac_source=repo_name,
                title=file_path.stem.replace('_', ' ').title(),
                description=description,
                model=model,
                tools=[],
                purpose=description[:100] if description else None
            )
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")
            return None

    def _parse_agent(self, file_path: Path, repo_name: str) -> Optional[Agent]:
        """Parse a single agent file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse frontmatter if available
            title = None
            description = None
            model = None
            purpose = None

            if HAS_FRONTMATTER:
                try:
                    post = frontmatter.loads(content)
                    title = post.get('title')
                    description = post.get('description')
                    model = post.get('model')
                    purpose = post.get('purpose')
                    content = post.content
                except:
                    pass

            # Extract title from first heading
            if not title:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()

            # Extract model from content
            if not model:
                model_match = re.search(r'model[:\s]+(haiku|sonnet|opus)', content, re.IGNORECASE)
                if model_match:
                    model = model_match.group(1).lower()

            # Extract tools
            tools = []
            tools_section = re.search(r'##\s*Tools?\s*\n([\s\S]*?)(?=\n##|\Z)', content)
            if tools_section:
                tool_matches = re.findall(r'[-*]\s*`?(\w+)`?', tools_section.group(1))
                tools = tool_matches[:10]

            # Extract purpose from description or content
            if not purpose:
                purpose_match = re.search(r'purpose[:\s]+(.+?)(?:\n|$)', content, re.IGNORECASE)
                if purpose_match:
                    purpose = purpose_match.group(1).strip()

            return Agent(
                name=file_path.stem,
                file_path=str(file_path),
                tac_source=repo_name,
                title=title,
                description=description,
                model=model,
                tools=tools if tools else [],
                purpose=purpose
            )
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")
            return None

    def _extract_adws(self, repo: Path, repo_name: str) -> list:
        """Extract ADW workflows from adws/"""
        adws = []
        adws_dir = repo / 'adws'

        if not adws_dir.exists():
            return adws

        # Check for modules, triggers, tests
        has_modules = (adws_dir / 'adw_modules').exists()
        has_triggers = (adws_dir / 'adw_triggers').exists()
        has_tests = (adws_dir / 'adw_tests').exists()

        for py_file in adws_dir.glob('adw_*.py'):
            adw = self._parse_adw(py_file, repo_name, has_modules, has_triggers, has_tests)
            if adw:
                adws.append(asdict(adw))

        return adws

    def _parse_adw(self, file_path: Path, repo_name: str,
                   has_modules: bool, has_triggers: bool, has_tests: bool) -> Optional[ADW]:
        """Parse a single ADW file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract docstring
            description = None
            docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
            if docstring_match:
                description = docstring_match.group(1).strip()[:200]

            # Determine workflow type from filename
            name = file_path.stem
            workflow_type = 'unknown'
            if 'build' in name:
                workflow_type = 'build'
            elif 'plan' in name:
                workflow_type = 'plan'
            elif 'test' in name:
                workflow_type = 'test'
            elif 'review' in name:
                workflow_type = 'review'
            elif 'document' in name:
                workflow_type = 'document'
            elif 'sdlc' in name:
                workflow_type = 'sdlc'
            elif 'ship' in name:
                workflow_type = 'ship'
            elif 'patch' in name:
                workflow_type = 'patch'

            return ADW(
                name=name,
                file_path=str(file_path),
                tac_source=repo_name,
                description=description,
                workflow_type=workflow_type,
                has_modules=has_modules,
                has_triggers=has_triggers,
                has_tests=has_tests
            )
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")
            return None

    def _extract_concepts(self, repo: Path, repo_name: str) -> list:
        """Extract concepts from README and ai_docs"""
        concepts = []

        # Parse README.md
        readme = repo / 'README.md'
        if readme.exists():
            readme_concepts = self._parse_readme(readme, repo_name)
            concepts.extend(readme_concepts)

        # Parse ai_docs folder
        ai_docs = repo / 'ai_docs'
        if ai_docs.exists():
            for md_file in ai_docs.glob('*.md'):
                doc_concepts = self._parse_doc(md_file, repo_name)
                concepts.extend(doc_concepts)

        return concepts

    def _parse_readme(self, file_path: Path, repo_name: str) -> list:
        """Extract concepts from README"""
        concepts = []
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                concepts.append(asdict(Concept(
                    name=title_match.group(1).strip(),
                    source_file=str(file_path),
                    tac_source=repo_name,
                    category='repository'
                )))

            # Extract major sections as concepts
            sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
            for section in sections[:5]:  # Limit to top 5 sections
                concepts.append(asdict(Concept(
                    name=section.strip(),
                    source_file=str(file_path),
                    tac_source=repo_name,
                    category='section'
                )))
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")

        return concepts

    def _parse_doc(self, file_path: Path, repo_name: str) -> list:
        """Extract concepts from ai_docs file"""
        concepts = []
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                concepts.append(asdict(Concept(
                    name=title_match.group(1).strip(),
                    source_file=str(file_path),
                    tac_source=repo_name,
                    category='ai_doc'
                )))
        except Exception as e:
            print(f"  Warning: Could not parse {file_path}: {e}")

        return concepts

    def save_results(self, output_path: str):
        """Save extraction results to JSON"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to: {output}")
        print(f"  Commands: {len(self.results['commands'])}")
        print(f"  Agents: {len(self.results['agents'])}")
        print(f"  ADWs: {len(self.results['adws'])}")
        print(f"  Concepts: {len(self.results['concepts'])}")


    def extract_single_repo(self, repo_name: str) -> dict:
        """Extract from a single TAC repository"""
        repo = self.tac_base / repo_name
        if not repo.exists():
            print(f"Error: Repository {repo_name} not found at {repo}")
            return {}

        print(f"Processing {repo_name}...")

        # Reset results for single repo
        self.results = {
            'commands': [],
            'agents': [],
            'adws': [],
            'concepts': [],
            'metadata': {
                'extracted_at': datetime.now().isoformat(),
                'repo_name': repo_name,
                'repo_path': str(repo)
            }
        }

        # Extract commands
        commands = self._extract_commands(repo, repo_name)
        self.results['commands'].extend(commands)

        # Extract agents
        agents = self._extract_agents(repo, repo_name)
        self.results['agents'].extend(agents)

        # Extract ADWs
        adws = self._extract_adws(repo, repo_name)
        self.results['adws'].extend(adws)

        # Extract concepts from docs
        concepts = self._extract_concepts(repo, repo_name)
        self.results['concepts'].extend(concepts)

        # Add summary
        self.results['metadata']['summary'] = {
            'total_commands': len(self.results['commands']),
            'total_agents': len(self.results['agents']),
            'total_adws': len(self.results['adws']),
            'total_concepts': len(self.results['concepts'])
        }

        return self.results

    def generate_readme(self, repo_name: str) -> str:
        """Generate a README.md summary for extracted data"""
        summary = self.results.get('metadata', {}).get('summary', {})
        commands = self.results.get('commands', [])
        agents = self.results.get('agents', [])
        adws = self.results.get('adws', [])
        concepts = self.results.get('concepts', [])

        lines = [
            f"# {repo_name}",
            "",
            f"Source: `C:\\Users\\gblac\\OneDrive\\Desktop\\tac\\{repo_name}\\`",
            "",
            "## Summary",
            "",
            f"| Type | Count |",
            f"|------|-------|",
            f"| Commands | {summary.get('total_commands', 0)} |",
            f"| Agents | {summary.get('total_agents', 0)} |",
            f"| ADWs | {summary.get('total_adws', 0)} |",
            f"| Concepts | {summary.get('total_concepts', 0)} |",
            "",
        ]

        if commands:
            lines.extend([
                "## Commands",
                "",
                "| Name | Title |",
                "|------|-------|",
            ])
            for cmd in commands:
                title = cmd.get('title', '') or ''
                lines.append(f"| `/{cmd['name']}` | {title[:50]} |")
            lines.append("")

        if agents:
            lines.extend([
                "## Agents",
                "",
                "| Name | Model | Purpose |",
                "|------|-------|---------|",
            ])
            for agent in agents:
                model = agent.get('model', '') or ''
                purpose = agent.get('purpose', '') or agent.get('title', '') or ''
                lines.append(f"| `{agent['name']}` | {model} | {purpose[:40]} |")
            lines.append("")

        if adws:
            lines.extend([
                "## ADWs",
                "",
                "| Name | Type |",
                "|------|------|",
            ])
            for adw in adws:
                lines.append(f"| `{adw['name']}` | {adw.get('workflow_type', '')} |")
            lines.append("")

        if concepts:
            lines.extend([
                "## Concepts",
                "",
            ])
            for concept in concepts:
                lines.append(f"- {concept['name']} ({concept.get('category', '')})")
            lines.append("")

        return "\n".join(lines)


def main():
    import sys

    tac_path = r"C:\Users\gblac\OneDrive\Desktop\tac"
    output_base = r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system"

    # Get repo names from command line args, or use defaults
    if len(sys.argv) > 1:
        repo_names = sys.argv[1:]
    else:
        # Default: extract all
        repo_names = None

    extractor = TACExtractor(tac_path)

    if repo_names:
        # Extract specific repos
        for repo_name in repo_names:
            extractor.extract_single_repo(repo_name)

            # Save to repo-specific folder
            output_dir = Path(output_base) / repo_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save JSON
            json_path = output_dir / "extraction.json"
            extractor.save_results(str(json_path))

            # Save README
            readme_path = output_dir / "README.md"
            readme_content = extractor.generate_readme(repo_name)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"  README saved to: {readme_path}")
    else:
        # Extract all and save combined
        extractor.extract_all()
        extractor.save_results(str(Path(output_base) / "data" / "tac_extraction.json"))


if __name__ == '__main__':
    main()
