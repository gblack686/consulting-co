"""
Anthropic Memory Tool - Core Memory Executor

Handles all memory operations: create, view, list, search.
Uses file-based storage with markdown format.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml
import json
import re
import frontmatter


class SecurityError(Exception):
    """Raised when security validation fails"""
    pass


class MemoryExecutor:
    """Core memory operations handler"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize memory executor

        Args:
            config_path: Path to memory-config.yaml (optional)
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "memory-config.yaml"

        self.config = self._load_config(config_path)

        # Set up paths
        self.memory_base = Path(self.config["memory_base_path"])
        self.sessions_dir = self.memory_base / "sessions"
        self.patterns_dir = self.memory_base / "patterns"
        self.entities_dir = self.memory_base / "entities"

        # Create directories if they don't exist
        self._ensure_directories()

    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _ensure_directories(self):
        """Create memory directories if they don't exist"""
        self.memory_base.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
        self.patterns_dir.mkdir(exist_ok=True)
        self.entities_dir.mkdir(exist_ok=True)

    def _validate_path(self, requested_path: str) -> Path:
        """
        Validate and resolve memory path to prevent traversal attacks

        Args:
            requested_path: User-requested path

        Returns:
            Validated absolute path

        Raises:
            SecurityError: If path traversal attempt detected
        """
        if not self.config.get("validate_paths", True):
            return self.memory_base / requested_path

        # Clean path
        clean_path = requested_path.lstrip("/").lstrip("\\")

        # Resolve to absolute path
        full_path = (self.memory_base / clean_path).resolve()

        # Check if path is within memory_base
        if not str(full_path).startswith(str(self.memory_base.resolve())):
            raise SecurityError(f"Path traversal attempt detected: {requested_path}")

        return full_path

    def create_memory(
        self,
        path: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create or update a memory file

        Args:
            path: Relative path within memory directory (e.g., "sessions/2026-01-11_session1.md")
            content: Markdown content
            metadata: Optional frontmatter metadata

        Returns:
            Success status and file path
        """
        # Validate path
        file_path = self._validate_path(path)

        # Ensure .md extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(".md")

        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare frontmatter
        if metadata is None:
            metadata = {}

        # Add default metadata
        if "date" not in metadata:
            metadata["date"] = datetime.now().strftime("%Y-%m-%d")

        # Create post with frontmatter
        post = frontmatter.Post(content, **metadata)

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        return {
            "success": True,
            "path": str(file_path.relative_to(self.memory_base)),
            "full_path": str(file_path),
            "created_at": datetime.now().isoformat()
        }

    def view_memory(self, path: str) -> Dict:
        """
        View a memory file

        Args:
            path: Relative path within memory directory

        Returns:
            Memory content and metadata
        """
        # Validate path
        file_path = self._validate_path(path)

        # Ensure .md extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(".md")

        # Check if file exists
        if not file_path.exists():
            return {
                "success": False,
                "error": f"Memory not found: {path}"
            }

        # Load file with frontmatter
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        return {
            "success": True,
            "path": str(file_path.relative_to(self.memory_base)),
            "metadata": post.metadata,
            "content": post.content,
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }

    def list_memories(
        self,
        directory: str = "",
        pattern: str = "*.md",
        limit: Optional[int] = None
    ) -> Dict:
        """
        List memory files in a directory

        Args:
            directory: Subdirectory to list (e.g., "sessions", "patterns")
            pattern: Glob pattern for filtering
            limit: Maximum number of results

        Returns:
            List of memory file paths with metadata
        """
        # Determine search directory
        if directory:
            search_dir = self._validate_path(directory)
        else:
            search_dir = self.memory_base

        # Find files
        files = list(search_dir.rglob(pattern))

        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Apply limit
        if limit:
            files = files[:limit]

        # Build result list
        memories = []
        for file_path in files:
            try:
                # Read frontmatter only
                with open(file_path, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)

                memories.append({
                    "path": str(file_path.relative_to(self.memory_base)),
                    "metadata": post.metadata,
                    "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "size_bytes": file_path.stat().st_size
                })
            except Exception as e:
                # Skip files that can't be read
                continue

        return {
            "success": True,
            "count": len(memories),
            "memories": memories
        }

    def search_memories(
        self,
        query: str,
        directories: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict:
        """
        Search memories using simple text matching

        Note: This is a basic implementation. For semantic search,
        use Claude to analyze and rank results.

        Args:
            query: Search query
            directories: Specific directories to search (None = all)
            limit: Maximum results

        Returns:
            Search results with relevance scores
        """
        # Determine search directories
        if directories is None:
            search_dirs = [self.sessions_dir, self.patterns_dir, self.entities_dir]
        else:
            search_dirs = [self._validate_path(d) for d in directories]

        # Collect all memory files
        all_files = []
        for search_dir in search_dirs:
            if search_dir.exists():
                all_files.extend(search_dir.rglob("*.md"))

        # Search results
        results = []
        query_lower = query.lower()

        for file_path in all_files:
            try:
                # Read file
                with open(file_path, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)

                # Calculate simple relevance score
                content_lower = post.content.lower()
                metadata_str = json.dumps(post.metadata).lower()

                # Count occurrences in content and metadata
                content_score = content_lower.count(query_lower) * 2
                metadata_score = metadata_str.count(query_lower) * 3  # Weight metadata higher

                # Check tags
                tags = post.metadata.get("tags", [])
                tag_score = sum(5 for tag in tags if query_lower in tag.lower())

                total_score = content_score + metadata_score + tag_score

                if total_score > 0:
                    # Find snippet with query
                    snippet = self._extract_snippet(post.content, query, length=200)

                    results.append({
                        "path": str(file_path.relative_to(self.memory_base)),
                        "score": total_score,
                        "metadata": post.metadata,
                        "snippet": snippet,
                        "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            except Exception:
                continue

        # Sort by score
        results.sort(key=lambda r: r["score"], reverse=True)

        # Apply limit
        results = results[:limit]

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }

    def _extract_snippet(self, content: str, query: str, length: int = 200) -> str:
        """
        Extract a snippet around the query match

        Args:
            content: Full content
            query: Search query
            length: Snippet length

        Returns:
            Snippet with ... markers
        """
        query_lower = query.lower()
        content_lower = content.lower()

        # Find first occurrence
        idx = content_lower.find(query_lower)

        if idx == -1:
            # No match, return beginning
            return content[:length] + ("..." if len(content) > length else "")

        # Extract snippet around match
        start = max(0, idx - length // 2)
        end = min(len(content), idx + len(query) + length // 2)

        snippet = content[start:end]

        # Add ellipsis
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def delete_memory(self, path: str) -> Dict:
        """
        Delete a memory file

        Args:
            path: Relative path within memory directory

        Returns:
            Success status
        """
        # Validate path
        file_path = self._validate_path(path)

        # Ensure .md extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(".md")

        # Check if exists
        if not file_path.exists():
            return {
                "success": False,
                "error": f"Memory not found: {path}"
            }

        # Delete file
        file_path.unlink()

        return {
            "success": True,
            "path": path,
            "deleted_at": datetime.now().isoformat()
        }

    def create_index(self) -> Dict:
        """
        Create master index file

        Returns:
            Success status and index path
        """
        # Count memories by type
        session_count = len(list(self.sessions_dir.glob("*.md")))
        pattern_count = len(list(self.patterns_dir.glob("*.md")))
        entity_count = len(list(self.entities_dir.glob("*.md")))

        # Get recent sessions
        recent_sessions = self.list_memories(directory="sessions", limit=5)

        # Build index content
        content = f"""# Memory System Index

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Statistics

- **Total Sessions**: {session_count}
- **Total Patterns**: {pattern_count}
- **Total Entity Types**: {entity_count}
- **Total Memories**: {session_count + pattern_count + entity_count}

## Recent Sessions

"""
        # Add recent sessions
        for memory in recent_sessions.get("memories", []):
            metadata = memory.get("metadata", {})
            path = memory["path"]
            date = metadata.get("date", "Unknown")
            tags = metadata.get("tags", [])
            tags_str = ", ".join(f"#{tag}" for tag in tags) if tags else "No tags"

            content += f"- [[{path}]] ({date}) - {tags_str}\n"

        content += """
## Directory Structure

- `sessions/` - Individual session summaries
- `patterns/` - Recurring patterns and learnings
- `entities/` - Entity registry (files, technologies, concepts)

## Commands

- `/memory-search [query]` - Search all memories
- `/memory-view [path]` - View specific memory
- `/memory-entities` - List all entities
- `/memory-patterns` - View patterns

---

*This index is auto-generated. Do not edit manually.*
"""

        # Save index
        result = self.create_memory(
            path="index.md",
            content=content,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "session_count": session_count,
                "pattern_count": pattern_count,
                "entity_count": entity_count
            }
        )

        return result


# CLI interface for testing
if __name__ == "__main__":
    import sys

    executor = MemoryExecutor()

    if len(sys.argv) < 2:
        print("Usage: memory_executor.py <command> [args...]")
        print("\nCommands:")
        print("  create <path> <content> - Create memory")
        print("  view <path> - View memory")
        print("  list [directory] - List memories")
        print("  search <query> - Search memories")
        print("  index - Create index")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create" and len(sys.argv) >= 4:
        path = sys.argv[2]
        content = sys.argv[3]
        result = executor.create_memory(path, content)
        print(json.dumps(result, indent=2))

    elif command == "view" and len(sys.argv) >= 3:
        path = sys.argv[2]
        result = executor.view_memory(path)
        print(json.dumps(result, indent=2))

    elif command == "list":
        directory = sys.argv[2] if len(sys.argv) >= 3 else ""
        result = executor.list_memories(directory)
        print(json.dumps(result, indent=2))

    elif command == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        result = executor.search_memories(query)
        print(json.dumps(result, indent=2))

    elif command == "index":
        result = executor.create_index()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
