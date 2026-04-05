#!/usr/bin/env python3
"""Check what episodes exist in Neo4j."""

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
    # Get all episodes with their timestamps
    result = session.run("""
        MATCH (e:Episodic)
        RETURN e.name as name,
               e.created_at as created_at,
               e.source as source
        ORDER BY e.created_at DESC
        LIMIT 20
    """)

    print("Recent Episodes in Neo4j:\n")
    for record in result:
        print(f"  {record['created_at']} - {record['name']}")
        print(f"    Source: {record['source']}\n")

    # Count total episodes
    count_result = session.run("MATCH (e:Episodic) RETURN count(e) as count")
    total = count_result.single()['count']
    print(f"Total Episodes: {total}")

driver.close()
