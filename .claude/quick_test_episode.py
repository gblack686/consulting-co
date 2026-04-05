#!/usr/bin/env python3
"""Quick test to create an episode in Graphiti."""

import os
import asyncio
from dotenv import load_dotenv
from graphiti_core import Graphiti
from datetime import datetime

load_dotenv()

async def main():
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    print(f"Connecting to Neo4j at {neo4j_uri}...")

    graphiti = Graphiti(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password,
    )

    episode_name = f"test-current-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    episode_text = f"""[CONVERSATION TURN]
Timestamp: {datetime.now().isoformat()}

[USER REQUEST]
those arent our recent logs tho are they? lets get our logs working

[ASSISTANT RESPONSE]
You're absolutely right - those are old test episodes. Let me check if our hook is actually running and capture our current conversation.

[TOOLS USED]
- Bash
- Glob
- Write

[KEY CONCEPTS]
Claude Code hooks, Graphiti logging, Neo4j knowledge graph, entity extraction

[OUTCOME]
Configured hooks.json to register the log_to_graphiti hook with Claude Code
"""

    print(f"Creating episode: {episode_name}")

    await graphiti.add_episode(
        name=episode_name,
        episode_body=episode_text,
        reference_time=datetime.now(),
        source_description=f"Claude Code Session (Manual test - {datetime.now().strftime('%Y-%m-%d %H:%M')})",
    )

    print("✓ Episode created successfully!")

    await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
