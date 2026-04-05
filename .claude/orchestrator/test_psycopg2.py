#!/usr/bin/env python3
"""Test psycopg2 (old synchronous driver) - should work on Windows"""
import socket

def test_psycopg2():
    """Test psycopg2 synchronous connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # Resolve hostname first
        hostname = "aws-0-us-west-1.pooler.supabase.com"
        port = 6543
        print(f"Resolving {hostname}:{port}...")
        result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
        ip = result[0][4][0]
        print(f"✅ Resolved to: {ip}")

        # Use dict parameters to avoid special char issues
        conn_params = {
            'host': ip,
            'port': port,
            'database': 'postgres',
            'user': 'postgres.unickqnwfheaczccvgbw',
            'password': 'G^qjC7F$@P65DqpN*mmv'
        }

        print("Connecting with psycopg2...")
        conn = psycopg2.connect(**conn_params, cursor_factory=RealDictCursor)

        print("✅ Connected!")

        cur = conn.cursor()
        cur.execute('SELECT version()')
        result = cur.fetchone()
        print(f"✅ Query successful: {result['version'][:60]}...")

        cur.close()
        conn.close()

        return True

    except ImportError:
        print("❌ psycopg2 not installed. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'psycopg2-binary', '--quiet'])
        print("✅ Installed! Please run again.")
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_psycopg2()
    sys.exit(0 if success else 1)
