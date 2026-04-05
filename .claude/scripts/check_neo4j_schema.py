#!/usr/bin/env python3
"""Check Neo4j schema to see what properties exist."""

import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(Path(__file__).parent.parent.parent / '.env')

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    # Get sample Entity properties
    result = session.run("""
        MATCH (e:Entity)
        RETURN e
        LIMIT 1
    """)

    record = result.single()
    if record:
        entity = record['e']
        print("Entity properties:")
        for key in entity.keys():
            print(f"  - {key}: {type(entity[key]).__name__}")
    else:
        print("No Entity nodes found")

    # Get sample Episodic properties
    result = session.run("""
        MATCH (e:Episodic)
        RETURN e
        LIMIT 1
    """)

    record = result.single()
    if record:
        episode = record['e']
        print("\nEpisodic properties:")
        for key in episode.keys():
            print(f"  - {key}: {type(episode[key]).__name__}")
    else:
        print("No Episodic nodes found")

driver.close()
