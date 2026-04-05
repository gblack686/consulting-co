"""
Graphiti storage layer for TAC Learning System.

Stores extracted entities and relationships in Neo4j via Graphiti
for semantic search and temporal queries.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType


class GraphitiStorage:
    """Store and query TAC knowledge graph using Graphiti"""

    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password"):
        """
        Initialize Graphiti client.

        Args:
            neo4j_uri: Neo4j database URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        # Check for OpenAI API key (Graphiti requires it for embeddings)
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable required for Graphiti")

        print(f"Connecting to Neo4j at {neo4j_uri}...")

        try:
            self.client = Graphiti(
                neo4j_uri=neo4j_uri,
                neo4j_user=neo4j_user,
                neo4j_password=neo4j_password
            )
            print("✅ Connected to Graphiti/Neo4j")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise

    async def ingest_prompts(self, prompts: List[Dict[str, Any]], episode_name: str = "prompt_extraction") -> None:
        """
        Ingest prompt entities into Graphiti.

        Args:
            prompts: List of prompt entities
            episode_name: Name for the episode
        """
        print(f"\n📄 Ingesting {len(prompts)} prompts...")

        for prompt in prompts:
            # Build fact text for Graphiti
            fact_text = f"""
Prompt: {prompt['name']}
Type: {prompt['prompt_type']}
File: {prompt['file_path']}

Content:
{prompt['content'][:500]}

Sections: {', '.join(prompt.get('sections', {}).keys())}
Delegations: {', '.join(prompt.get('delegations', []))}
Tools: {', '.join(prompt.get('tools_mentioned', []))}
"""

            try:
                await self.client.add_episode(
                    name=episode_name,
                    episode_body=fact_text,
                    source=EpisodeType.text,
                    source_description=f"TAC prompt: {prompt['name']}",
                    reference_time=datetime.now()
                )
                print(f"  ✅ Ingested prompt: {prompt['name']}")
            except Exception as e:
                print(f"  ❌ Failed to ingest {prompt['name']}: {e}")

    async def ingest_code_entities(self, code_data: Dict[str, Any], episode_name: str = "code_extraction") -> None:
        """
        Ingest code entities (modules, functions, classes) into Graphiti.

        Args:
            code_data: Code entities data from code_parser
            episode_name: Name for the episode
        """
        modules = code_data.get('modules', [])
        print(f"\n🐍 Ingesting {len(modules)} modules...")

        for module in modules:
            # Build fact text for module
            module_facts = f"""
Python Module: {module['name']}
File: {module['file_path']}
Lines of Code: {module['lines_of_code']}

Functions: {len(module.get('functions', []))}
Classes: {len(module.get('classes', []))}
Imports: {len(module.get('imports', []))}
"""

            # Add function details
            for func in module.get('functions', []):
                module_facts += f"""

Function: {func['name']}
Parameters: {', '.join(p['name'] for p in func.get('parameters', []))}
Returns: {func.get('return_type', 'None')}
Decorators: {', '.join(func.get('decorators', []))}
Complexity: {func.get('complexity_hint', 0)}
Async: {func.get('is_async', False)}
Calls: {', '.join(func.get('calls', [])[:5])}
"""
                if func.get('docstring'):
                    module_facts += f"Docstring: {func['docstring'][:200]}\n"

            # Add class details
            for cls in module.get('classes', []):
                module_facts += f"""

Class: {cls['name']}
Base Classes: {', '.join(cls.get('base_classes', []))}
Methods: {', '.join(cls.get('methods', []))}
Attributes: {', '.join(cls.get('attributes', []))}
"""

            try:
                await self.client.add_episode(
                    name=episode_name,
                    episode_body=module_facts,
                    source=EpisodeType.text,
                    source_description=f"Python module: {module['name']}",
                    reference_time=datetime.now()
                )
                print(f"  ✅ Ingested module: {module['name']}")
            except Exception as e:
                print(f"  ❌ Failed to ingest {module['name']}: {e}")

    async def ingest_concepts(self, concepts_data: Dict[str, Any], episode_name: str = "concept_extraction") -> None:
        """
        Ingest learning concepts into Graphiti.

        Args:
            concepts_data: Concepts from transcript parsing
            episode_name: Name for the episode
        """
        concepts = concepts_data.get('concepts', [])
        print(f"\n💡 Ingesting {len(concepts)} concepts...")

        for concept in concepts:
            concept_text = f"""
Concept: {concept['name']}
Category: {concept['category']}
Definition: {concept.get('definition', '')}

Keywords: {', '.join(concept.get('keywords', []))}
Related: {', '.join(concept.get('related_concepts', []))}
"""

            try:
                await self.client.add_episode(
                    name=episode_name,
                    episode_body=concept_text,
                    source=EpisodeType.text,
                    source_description=f"TAC concept: {concept['name']}",
                    reference_time=datetime.now()
                )
                print(f"  ✅ Ingested concept: {concept['name']}")
            except Exception as e:
                print(f"  ❌ Failed to ingest {concept['name']}: {e}")

    async def ingest_semantic_matches(self, matches_data: Dict[str, Any], episode_name: str = "semantic_matching") -> None:
        """
        Ingest semantic matches (code-to-concept links) into Graphiti.

        Args:
            matches_data: Semantic matches from semantic_matcher
            episode_name: Name for the episode
        """
        matches = matches_data.get('matches', [])
        print(f("\n🔗 Ingesting {len(matches)} semantic matches...")

        for match in matches:
            match_text = f"""
Semantic Match: {match['source_type']} demonstrates concept

Source: {match['source_name']} ({match['source_type']})
Concept: {match['concept_name']}
Similarity Score: {match['similarity_score']}
Confidence: {match['confidence']}
"""
            if match.get('llm_validated'):
                match_text += f"\nLLM Validated: {match['llm_explanation']}\n"

            try:
                await self.client.add_episode(
                    name=episode_name,
                    episode_body=match_text,
                    source=EpisodeType.text,
                    source_description=f"Semantic match: {match['source_name']} → {match['concept_name']}",
                    reference_time=datetime.now()
                )
                print(f"  ✅ Ingested match: {match['source_name']} → {match['concept_name']}")
            except Exception as e:
                print(f"  ❌ Failed to ingest match: {e}")

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph using semantic search.

        Args:
            query: Natural language query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        print(f"\n🔍 Searching: '{query}'")

        try:
            results = await self.client.search(query, num_results=num_results)
            print(f"✅ Found {len(results)} results")
            return results
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    async def close(self):
        """Close Graphiti client"""
        if hasattr(self.client, 'close'):
            await self.client.close()


async def ingest_all_data(data_dir: Path, neo4j_uri: str = "bolt://localhost:7687",
                          neo4j_user: str = "neo4j", neo4j_password: str = "password") -> None:
    """
    Ingest all extracted TAC data into Graphiti.

    Args:
        data_dir: Directory containing extracted data
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
    """
    print("="*60)
    print("GRAPHITI INGESTION PIPELINE")
    print("="*60)

    # Initialize Graphiti client
    storage = GraphitiStorage(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # Load and ingest prompts
        prompts_file = data_dir / "tac-2" / "prompts.json"
        if prompts_file.exists():
            prompts = json.loads(prompts_file.read_text())
            await storage.ingest_prompts(prompts, "tac2_prompts")

        # Load and ingest code entities
        code_file = data_dir / "tac-2" / "code_entities.json"
        if code_file.exists():
            code_data = json.loads(code_file.read_text())
            await storage.ingest_code_entities(code_data, "tac2_code")

        # Load and ingest concepts
        concepts_file = data_dir / "lesson-2" / "concepts.json"
        if concepts_file.exists():
            concepts_data = json.loads(concepts_file.read_text())
            await storage.ingest_concepts(concepts_data, "lesson2_concepts")

        # Load and ingest semantic matches
        matches_file = data_dir / "semantic" / "semantic_matches.json"
        if matches_file.exists():
            matches_data = json.loads(matches_file.read_text())
            await storage.ingest_semantic_matches(matches_data, "tac2_semantic_links")

        print("\n✅ Graphiti ingestion complete!")

        # Example searches
        print("\n" + "="*60)
        print("EXAMPLE SEARCHES")
        print("="*60)

        example_queries = [
            "What is the Core Four?",
            "Show me prompts that handle file uploads",
            "What functions demonstrate the SDLC?",
        ]

        for query in example_queries:
            results = await storage.search(query, num_results=3)
            print(f"\nQuery: {query}")
            print(f"Results: {len(results)}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('name', 'Unknown')}")

    finally:
        await storage.close()


if __name__ == "__main__":
    import asyncio

    # Configuration
    data_dir = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data")

    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable required")
        print("Graphiti uses OpenAI for embeddings")
        exit(1)

    # Neo4j connection details (adjust as needed)
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"Neo4j User: {NEO4J_USER}")

    # Run ingestion
    asyncio.run(ingest_all_data(
        data_dir,
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD
    ))
