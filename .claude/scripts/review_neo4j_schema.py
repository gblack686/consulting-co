#!/usr/bin/env python3
"""Review Neo4j schema and data for consulting-co project."""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Connection details
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

if not password:
    print("ERROR: NEO4J_PASSWORD not found in .env file")
    exit(1)

print(f"Connecting to Neo4j at {uri}...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✓ Connected successfully!\n")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

def run_query(query, description):
    """Run a Cypher query and print results."""
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}\n")

    with driver.session() as session:
        try:
            result = session.run(query)
            records = list(result)

            if not records:
                print("  (No results)")
            else:
                for i, record in enumerate(records, 1):
                    print(f"  {i}. {dict(record)}")

            print(f"\n  Total: {len(records)} results")

        except Exception as e:
            print(f"  ✗ Query failed: {e}")

    print()

# ============================================================================
# SCHEMA QUERIES
# ============================================================================

print("\n" + "="*70)
print("🔍 NEO4J KNOWLEDGE GRAPH REVIEW")
print("="*70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. Node Labels
run_query(
    "CALL db.labels()",
    "All Node Labels in Database"
)

# 2. Relationship Types
run_query(
    "CALL db.relationshipTypes()",
    "All Relationship Types"
)

# 3. Database Stats
run_query(
    """
    MATCH (n)
    WITH labels(n) as labels, count(n) as count
    RETURN labels, count
    ORDER BY count DESC
    """,
    "Node Counts by Label"
)

# 4. Relationship Stats
run_query(
    """
    MATCH ()-[r]->()
    WITH type(r) as rel_type, count(r) as count
    RETURN rel_type, count
    ORDER BY count DESC
    """,
    "Relationship Counts by Type"
)

# ============================================================================
# EPISODE QUERIES
# ============================================================================

# 5. Total Episodes
run_query(
    "MATCH (e:Episode) RETURN count(e) as episode_count",
    "Total Episodes Stored"
)

# 6. Recent Episodes
run_query(
    """
    MATCH (e:Episode)
    RETURN e.name as name, e.created_at as created, e.source as source
    ORDER BY e.created_at DESC
    LIMIT 10
    """,
    "Last 10 Episodes (Most Recent)"
)

# 7. Episodes by Source
run_query(
    """
    MATCH (e:Episode)
    WITH e.source as source, count(e) as count
    RETURN source, count
    ORDER BY count DESC
    """,
    "Episodes Grouped by Source"
)

# ============================================================================
# ENTITY QUERIES
# ============================================================================

# 8. Total Entities
run_query(
    "MATCH (e:Entity) RETURN count(e) as entity_count",
    "Total Entities Extracted"
)

# 9. Entity Types Breakdown
run_query(
    """
    MATCH (e:Entity)
    WITH e.entity_type as entity_type, count(e) as count
    RETURN entity_type, count
    ORDER BY count DESC
    """,
    "Entity Types Breakdown"
)

# 10. Top Entities by Connections
run_query(
    """
    MATCH (e:Entity)-[r]-()
    WITH e, count(r) as connections
    RETURN e.name as name, e.entity_type as type, connections
    ORDER BY connections DESC
    LIMIT 20
    """,
    "Top 20 Most Connected Entities"
)

# 11. Sample Relationships
run_query(
    """
    MATCH (a:Entity)-[r]->(b:Entity)
    RETURN type(r) as relationship, a.name as from_entity, b.name as to_entity
    LIMIT 15
    """,
    "Sample Entity Relationships"
)

# ============================================================================
# TEMPORAL QUERIES
# ============================================================================

# 12. Activity Over Time (if timestamps exist)
run_query(
    """
    MATCH (e:Episode)
    WHERE e.created_at IS NOT NULL
    WITH date(e.created_at) as day, count(e) as episodes
    RETURN day, episodes
    ORDER BY day DESC
    LIMIT 14
    """,
    "Episode Activity (Last 14 Days)"
)

# ============================================================================
# SPECIFIC ENTITY QUERIES
# ============================================================================

# 13. Find Authentication-Related Entities
run_query(
    """
    MATCH (e:Entity)
    WHERE toLower(e.name) CONTAINS 'auth'
       OR toLower(e.name) CONTAINS 'login'
       OR toLower(e.name) CONTAINS 'token'
    RETURN e.name as name, e.entity_type as type
    LIMIT 10
    """,
    "Authentication-Related Entities"
)

# 14. Find Technology Entities
run_query(
    """
    MATCH (e:Entity)
    WHERE e.entity_type = 'Technology' OR e.entity_type = 'Tool'
    RETURN e.name as name, e.entity_type as type
    ORDER BY e.name
    LIMIT 20
    """,
    "Technology & Tool Entities"
)

# 15. Find Decision Entities
run_query(
    """
    MATCH (e:Entity)
    WHERE e.entity_type = 'Decision' OR toLower(e.name) CONTAINS 'adr'
    RETURN e.name as name, e.created_at as created
    ORDER BY e.created_at DESC
    LIMIT 10
    """,
    "Decision Entities (ADRs)"
)

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("\n" + "="*70)
print("💡 RECOMMENDATIONS")
print("="*70 + "\n")

# Get counts for recommendations
with driver.session() as session:
    episode_count = session.run("MATCH (e:Episode) RETURN count(e) as count").single()["count"]
    entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]

    print(f"Current State:")
    print(f"  - Episodes: {episode_count}")
    print(f"  - Entities: {entity_count}")
    print()

    if episode_count == 0:
        print("⚠️  No episodes found!")
        print("   Action: Run some Claude Code sessions to populate the graph.")
    elif episode_count < 10:
        print("✓ Graph is starting to populate")
        print("   Suggestion: Run 10-20 more sessions for better insights.")
    else:
        print("✓ Good episode coverage!")

    print()

    if entity_count == 0:
        print("⚠️  No entities found!")
        print("   Action: Check if Graphiti entity extraction is working.")
    elif entity_count < 50:
        print("✓ Entity extraction is working")
        print("   Suggestion: More sessions will discover more entities.")
    else:
        print("✓ Rich entity graph!")

    print()

print("\n" + "="*70)
print("📸 NEXT STEPS")
print("="*70 + "\n")

print("1. Open Neo4j Browser at http://localhost:7474")
print("2. Run these queries for screenshots:\n")

print("   Graph Visualization (Top Entities):")
print("   ```")
print("   MATCH (e:Entity)-[r]-()")
print("   WITH e, count(r) as connections")
print("   ORDER BY connections DESC")
print("   LIMIT 10")
print("   MATCH path = (e)-[r]-(connected)")
print("   RETURN path")
print("   LIMIT 50")
print("   ```\n")

print("   Timeline View (Recent Episodes):")
print("   ```")
print("   MATCH (e:Episode)")
print("   RETURN e.name, e.created_at, e.source")
print("   ORDER BY e.created_at DESC")
print("   LIMIT 20")
print("   ```\n")

print("   Entity Clustering:")
print("   ```")
print("   MATCH (e1:Entity)-[r1]-(shared:Entity)-[r2]-(e2:Entity)")
print("   WHERE e1 <> e2")
print("   RETURN e1, r1, shared, r2, e2")
print("   LIMIT 50")
print("   ```\n")

print("3. Take screenshots and save to:")
print("   ~/OneDrive/Desktop/obsidian/Gbautomation/claude/projects/consulting-co/attachments/screenshots/")
print()

driver.close()

print("="*70)
print("✓ Review Complete!")
print("="*70)
