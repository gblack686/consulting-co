#!/usr/bin/env python3
"""
Anthropic Memory Tool - Stop Hook

Automatically ingests session data into memory when Claude session ends.

This hook:
1. Reads the session transcript
2. Extracts entities using Claude
3. Stores session summary
4. Updates entity index
5. Optionally exports to Obsidian
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add skills directory to path
SKILLS_DIR = Path(__file__).parent.parent / "skills" / "anthropic-memory" / "scripts"
sys.path.insert(0, str(SKILLS_DIR))

from memory_executor import MemoryExecutor
from entity_extractor import EntityExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_ingest_hook")


def find_latest_transcript() -> Path:
    """
    Find the most recent transcript file

    Returns:
        Path to latest transcript
    """
    # Check for transcript in ~/.claude/projects/
    projects_dir = Path.home() / ".claude" / "projects"

    # Find all transcript files
    transcript_files = []
    for project_dir in projects_dir.glob("*"):
        if project_dir.is_dir():
            transcript = project_dir / f"{project_dir.name}.jsonl"
            if transcript.exists():
                transcript_files.append(transcript)

    if not transcript_files:
        raise FileNotFoundError("No transcript files found")

    # Return most recently modified
    latest = max(transcript_files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found latest transcript: {latest}")
    return latest


def get_session_id(transcript_path: Path) -> str:
    """
    Extract session ID from transcript path

    Args:
        transcript_path: Path to transcript file

    Returns:
        Session ID (last 8 chars of directory name)
    """
    # Session ID is the directory name (UUID)
    full_id = transcript_path.parent.name
    # Truncate to 8 chars for readability
    return full_id[:8]


def main():
    """Main hook execution"""
    try:
        logger.info("Memory ingestion hook started")

        # Find latest transcript
        transcript_path = find_latest_transcript()
        session_id = get_session_id(transcript_path)

        logger.info(f"Processing session: {session_id}")

        # Initialize executor and extractor
        executor = MemoryExecutor()
        extractor = EntityExtractor()

        # Extract entities from transcript
        logger.info("Extracting entities from transcript...")
        entities = extractor.extract_from_file(transcript_path)

        logger.info(f"Extracted {len(entities.get('files', []))} files, "
                   f"{len(entities.get('technologies', []))} technologies, "
                   f"{len(entities.get('concepts', []))} concepts")

        # Generate session date
        session_date = datetime.now().strftime("%Y-%m-%d")

        # Generate session summary
        summary_content = extractor.generate_session_summary(
            entities=entities,
            session_id=session_id,
            date=session_date
        )

        # Prepare metadata for frontmatter
        metadata = {
            "date": session_date,
            "session_id": session_id,
            "tags": entities.get("tags", []),
            "entities": {
                "files": [f["path"] for f in entities.get("files", [])],
                "technologies": [t["name"] for t in entities.get("technologies", [])],
                "concepts": [c["name"] for c in entities.get("concepts", [])]
            },
            "tools_used": {
                tool: info["count"]
                for tool, info in entities.get("tools_used", {}).items()
                if isinstance(info, dict) and info.get("count", 0) > 0
            }
        }

        # Store session memory
        session_path = f"sessions/{session_date}_{session_id}.md"
        logger.info(f"Storing session memory at: {session_path}")

        result = executor.create_memory(
            path=session_path,
            content=summary_content,
            metadata=metadata
        )

        if result["success"]:
            logger.info(f"Session memory created successfully: {result['path']}")
        else:
            logger.error(f"Failed to create session memory: {result.get('error')}")
            return 1

        # Update entity indices
        logger.info("Updating entity indices...")
        _update_entity_indices(executor, entities)

        # Update master index
        logger.info("Updating master index...")
        executor.create_index()

        logger.info("Memory ingestion complete!")
        return 0

    except Exception as e:
        logger.error(f"Memory ingestion failed: {e}", exc_info=True)
        return 1


def _update_entity_indices(executor: MemoryExecutor, entities: Dict):
    """
    Update entity index files

    Args:
        executor: Memory executor instance
        entities: Extracted entities
    """
    # Update files index
    if entities.get("files"):
        _update_file_index(executor, entities["files"])

    # Update technologies index
    if entities.get("technologies"):
        _update_technology_index(executor, entities["technologies"])

    # Update concepts index
    if entities.get("concepts"):
        _update_concept_index(executor, entities["concepts"])


def _update_file_index(executor: MemoryExecutor, files: List[Dict]):
    """Update files.md entity index"""
    # Read existing index
    existing = executor.view_memory("entities/files.md")

    if existing["success"]:
        content = existing["content"]
        existing_files = set()
        # Parse existing files (simple line parsing)
        for line in content.split("\n"):
            if line.startswith("- "):
                # Extract file path from markdown list
                file_path = line.split("**")[1] if "**" in line else ""
                if file_path:
                    existing_files.add(file_path)
    else:
        content = "# Files Registry\n\nAll files encountered across sessions.\n\n"
        existing_files = set()

    # Add new files
    for file in files:
        path = file["path"]
        if path not in existing_files:
            file_type = file.get("type", "unknown")
            description = file.get("description", "")
            content += f"- **{path}** ({file_type})"
            if description:
                content += f" - {description}"
            content += "\n"

    # Save updated index
    executor.create_memory(
        path="entities/files.md",
        content=content,
        metadata={"entity_type": "files", "updated": datetime.now().isoformat()}
    )


def _update_technology_index(executor: MemoryExecutor, technologies: List[Dict]):
    """Update technologies.md entity index"""
    # Read existing index
    existing = executor.view_memory("entities/technologies.md")

    if existing["success"]:
        content = existing["content"]
        existing_techs = set()
        for line in content.split("\n"):
            if line.startswith("- "):
                tech_name = line.split("**")[1] if "**" in line else ""
                if tech_name:
                    existing_techs.add(tech_name)
    else:
        content = "# Technologies Registry\n\nAll technologies used across sessions.\n\n"
        existing_techs = set()

    # Add new technologies
    for tech in technologies:
        name = tech["name"]
        if name not in existing_techs:
            category = tech.get("category", "unknown")
            purpose = tech.get("purpose", "")
            content += f"- **{name}** ({category})"
            if purpose:
                content += f" - {purpose}"
            content += "\n"

    # Save updated index
    executor.create_memory(
        path="entities/technologies.md",
        content=content,
        metadata={"entity_type": "technologies", "updated": datetime.now().isoformat()}
    )


def _update_concept_index(executor: MemoryExecutor, concepts: List[Dict]):
    """Update concepts.md entity index"""
    # Read existing index
    existing = executor.view_memory("entities/concepts.md")

    if existing["success"]:
        content = existing["content"]
        existing_concepts = set()
        for line in content.split("\n"):
            if line.startswith("- "):
                concept_name = line.split("**")[1] if "**" in line else ""
                if concept_name:
                    existing_concepts.add(concept_name)
    else:
        content = "# Concepts Registry\n\nAll concepts discussed across sessions.\n\n"
        existing_concepts = set()

    # Add new concepts
    for concept in concepts:
        name = concept["name"]
        if name not in existing_concepts:
            description = concept.get("description", "")
            importance = concept.get("importance", "")
            content += f"- **{name}**"
            if description:
                content += f" - {description}"
            if importance:
                content += f"\n  - _Why it matters:_ {importance}"
            content += "\n"

    # Save updated index
    executor.create_memory(
        path="entities/concepts.md",
        content=content,
        metadata={"entity_type": "concepts", "updated": datetime.now().isoformat()}
    )


if __name__ == "__main__":
    sys.exit(main())
