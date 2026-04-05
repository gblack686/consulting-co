"""
Simple Neo4j Cypher query runner for exploring TAC knowledge graph.
"""

import os
from neo4j import GraphDatabase


class Neo4jQueryRunner:
    """Run Cypher queries against Neo4j"""

    def __init__(self, uri: str = "bolt://localhost:7687",
                 user: str = "neo4j",
                 password: str = "password"):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            print(f"✅ Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()

    def run_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)

    def show_database_stats(self):
        """Show database statistics"""
        print("\n" + "="*60)
        print("NEO4J DATABASE STATISTICS")
        print("="*60)

        # Count all nodes
        query = "MATCH (n) RETURN count(n) as total_nodes"
        result = self.run_query(query)
        print(f"\nTotal Nodes: {result[0]['total_nodes']}")

        # Count nodes by label
        query = """
        MATCH (n)
        RETURN labels(n) as label, count(n) as count
        ORDER BY count DESC
        """
        result = self.run_query(query)
        print("\nNodes by Label:")
        for record in result:
            labels = record['label']
            count = record['count']
            print(f"  {labels}: {count}")

        # Count relationships
        query = "MATCH ()-[r]->() RETURN count(r) as total_rels"
        result = self.run_query(query)
        print(f"\nTotal Relationships: {result[0]['total_rels']}")

        # Count relationships by type
        query = """
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        """
        result = self.run_query(query)
        print("\nRelationships by Type:")
        for record in result:
            rel_type = record['rel_type']
            count = record['count']
            print(f"  {rel_type}: {count}")

    def find_core_concepts(self):
        """Find core TAC concepts (Core Four, SDLC, etc.)"""
        print("\n" + "="*60)
        print("CORE TAC CONCEPTS")
        print("="*60)

        # Find Episode nodes that mention core concepts
        query = """
        MATCH (e:Episode)
        WHERE e.name CONTAINS 'concept' OR e.content CONTAINS 'Core Four'
        RETURN e.name as episode_name,
               substring(e.content, 0, 200) as preview
        LIMIT 10
        """
        result = self.run_query(query)

        if result:
            print("\nConcept Episodes Found:")
            for record in result:
                print(f"\n📘 {record['episode_name']}")
                print(f"   Preview: {record['preview']}...")
        else:
            print("\n⚠️  No concept episodes found")

    def find_prompts(self):
        """Find TAC prompts"""
        print("\n" + "="*60)
        print("TAC PROMPTS")
        print("="*60)

        query = """
        MATCH (e:Episode)
        WHERE e.name CONTAINS 'prompt'
        RETURN e.name as episode_name,
               substring(e.content, 0, 200) as preview
        LIMIT 10
        """
        result = self.run_query(query)

        if result:
            print("\nPrompt Episodes Found:")
            for record in result:
                print(f"\n📄 {record['episode_name']}")
                print(f"   Preview: {record['preview']}...")
        else:
            print("\n⚠️  No prompt episodes found")

    def find_semantic_matches(self):
        """Find semantic matches (code-to-concept links)"""
        print("\n" + "="*60)
        print("SEMANTIC MATCHES")
        print("="*60)

        query = """
        MATCH (e:Episode)
        WHERE e.name CONTAINS 'semantic'
        RETURN e.name as episode_name,
               substring(e.content, 0, 300) as content
        LIMIT 10
        """
        result = self.run_query(query)

        if result:
            print("\nSemantic Match Episodes Found:")
            for record in result:
                print(f"\n🔗 {record['episode_name']}")
                print(f"   {record['content']}...")
        else:
            print("\n⚠️  No semantic match episodes found")

    def find_entities(self):
        """Find Entity nodes (extracted by Graphiti)"""
        print("\n" + "="*60)
        print("EXTRACTED ENTITIES")
        print("="*60)

        query = """
        MATCH (n:Entity)
        RETURN n.name as entity_name,
               labels(n) as labels,
               substring(n.summary, 0, 150) as summary
        LIMIT 20
        """
        result = self.run_query(query)

        if result:
            print("\nEntities Extracted by Graphiti:")
            for record in result:
                name = record.get('entity_name', 'Unknown')
                summary = record.get('summary', 'No summary')
                print(f"\n  • {name}")
                print(f"    {summary}...")
        else:
            print("\n⚠️  No Entity nodes found")
            print("    (Graphiti may not have processed episodes yet)")

    def search_by_keyword(self, keyword: str):
        """Search for keyword in episodes"""
        print(f"\n" + "="*60)
        print(f"SEARCHING FOR: '{keyword}'")
        print("="*60)

        query = """
        MATCH (e:Episode)
        WHERE toLower(e.content) CONTAINS toLower($keyword)
        RETURN e.name as episode_name,
               substring(e.content, 0, 300) as preview
        LIMIT 10
        """
        result = self.run_query(query, {'keyword': keyword})

        if result:
            print(f"\nFound {len(result)} episodes mentioning '{keyword}':")
            for record in result:
                print(f"\n📍 {record['episode_name']}")
                print(f"   {record['preview']}...")
        else:
            print(f"\n⚠️  No episodes found containing '{keyword}'")

    def show_sample_graph(self):
        """Show a sample of the graph structure"""
        print("\n" + "="*60)
        print("SAMPLE GRAPH STRUCTURE")
        print("="*60)

        query = """
        MATCH (a)-[r]->(b)
        RETURN a.name as from_entity,
               type(r) as relationship,
               b.name as to_entity
        LIMIT 10
        """
        result = self.run_query(query)

        if result:
            print("\nSample Relationships:")
            for record in result:
                from_e = record.get('from_entity', 'Unknown')
                rel = record.get('relationship', 'UNKNOWN')
                to_e = record.get('to_entity', 'Unknown')
                print(f"  {from_e} --[{rel}]--> {to_e}")
        else:
            print("\n⚠️  No relationships found")


def main():
    """Run sample queries"""
    # Get Neo4j connection details
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

    print("="*60)
    print("TAC KNOWLEDGE GRAPH - NEO4J QUERY TOOL")
    print("="*60)
    print(f"Connecting to: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")

    try:
        runner = Neo4jQueryRunner(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

        # Run various queries
        runner.show_database_stats()
        runner.find_core_concepts()
        runner.find_prompts()
        runner.find_semantic_matches()
        runner.find_entities()
        runner.show_sample_graph()

        # Search for specific concepts
        print("\n" + "="*60)
        print("KEYWORD SEARCHES")
        print("="*60)

        keywords = ["Core Four", "upload", "complexity", "delegate"]
        for keyword in keywords:
            runner.search_by_keyword(keyword)

        runner.close()
        print("\n✅ Queries complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is Neo4j running? Check: docker ps | grep neo4j")
        print("2. Has data been ingested? Run: python storage/graphiti_storage.py")
        print("3. Are credentials correct? Check NEO4J_PASSWORD")


if __name__ == "__main__":
    main()
