#!/usr/bin/env python3
"""Debug date comparison issue."""

import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(Path(__file__).parent.parent.parent / '.env')

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

# Test with November 13, 2025
target_date = datetime(2025, 11, 13).date()
start_time = datetime.combine(target_date, datetime.min.time())
end_time = start_time + timedelta(days=1)

start_ts = start_time.isoformat()
end_ts = end_time.isoformat()

print(f"Target date: {target_date}")
print(f"Start timestamp: {start_ts}")
print(f"End timestamp: {end_ts}")
print()

with driver.session() as session:
    # Get episodes with debug info
    result = session.run("""
        MATCH (e:Episodic)
        RETURN e.name as name,
               e.created_at as created_at,
               toString(e.created_at) as created_str
        ORDER BY e.created_at DESC
        LIMIT 5
    """)

    print("Recent episodes:")
    for record in result:
        print(f"  {record['created_str']} - {record['name']}")
        created_at = record['created_at']
        print(f"    Type: {type(created_at)}")
        print(f"    Value: {created_at}")
        print()

    # Try the actual query
    print(f"\nQuerying with range: {start_ts} to {end_ts}")
    result = session.run("""
        MATCH (e:Episodic)
        WHERE e.created_at >= $start_ts AND e.created_at < $end_ts
        RETURN count(e) as count
    """, start_ts=start_ts, end_ts=end_ts)

    count = result.single()['count']
    print(f"Episodes found in range: {count}")

driver.close()
