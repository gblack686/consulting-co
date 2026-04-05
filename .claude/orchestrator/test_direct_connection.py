#!/usr/bin/env python3
"""Test direct connection to Supabase with new password"""
import socket

def test_direct_connection():
    """Test psycopg2 direct connection (port 5432)"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # Try port 5432 (direct connection)
        # Note: Direct hostname fails DNS, so we'll try the pooler IP on port 5432
        hostname = "aws-0-us-west-1.pooler.supabase.com"
        port = 5432  # Changed from 6543 to 5432
        print(f"Resolving {hostname}:{port}...")
        result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        ip = result[0][4][0]
        print(f"✅ Resolved to: {ip}")

        # Connection params with password from dashboard
        conn_params = {
            'host': ip,
            'port': port,
            'database': 'postgres',
            'user': 'postgres.unickqnwfheaczccvgbw',  # Format: postgres.project_ref
            'password': 'C15sSJw9KksMDvfJ'
        }

        print(f"Trying user: {conn_params['user']}")

        print("Connecting with psycopg2 to direct connection...")
        conn = psycopg2.connect(**conn_params, cursor_factory=RealDictCursor)

        print("✅ Connected!")

        cur = conn.cursor()
        cur.execute('SELECT version()')
        result = cur.fetchone()
        print(f"✅ Query successful!")
        print(f"PostgreSQL: {result['version'][:80]}...")

        # Test a simple table query
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5")
        tables = cur.fetchall()
        print(f"\n✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")

        cur.close()
        conn.close()

        print("\n🎉 SUCCESS! Direct connection works!")
        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_direct_connection()
    sys.exit(0 if success else 1)
