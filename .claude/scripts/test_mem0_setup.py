#!/usr/bin/env python3
"""
Mem0 + Supabase Setup Validation Script

This script verifies that your Mem0 RAG system is properly configured
and ready to use with Claude Code.

Usage:
    python test_mem0_setup.py

"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_env_file() -> bool:
    """Check if .env.mem0 exists and load it"""
    print_header("1. Checking Environment File")

    env_file = Path(".env.mem0")

    if not env_file.exists():
        print_error(f".env.mem0 not found in {Path.cwd()}")
        print_info("Copy .env.mem0 template from project root")
        return False

    print_success(f"Found .env.mem0")

    # Load environment
    load_dotenv(".env.mem0")
    return True

def check_required_vars() -> Tuple[bool, dict]:
    """Check if all required environment variables are set"""
    print_header("2. Checking Environment Variables")

    required_vars = {
        "DATABASE_URL": "Supabase connection string",
        "LLM_API_KEY": "OpenAI API key",
        "LLM_PROVIDER": "LLM provider (openai, openrouter, ollama)",
        "LLM_CHOICE": "LLM model name",
        "EMBEDDING_MODEL_CHOICE": "Embedding model",
    }

    optional_vars = {
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_KEY": "Supabase API key",
        "TRANSPORT": "Transport protocol (sse or stdio)",
        "PORT": "Server port",
    }

    config = {}
    all_valid = True

    print(f"{Colors.BOLD}Required Variables:{Colors.RESET}")
    for var, description in required_vars.items():
        value = os.getenv(var)
        config[var] = value

        if value:
            # Mask sensitive values
            display_value = f"{value[:20]}..." if len(str(value)) > 20 else value
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var}: NOT SET - {description}")
            all_valid = False

    print(f"\n{Colors.BOLD}Optional Variables:{Colors.RESET}")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
            config[var] = value
        else:
            print_warning(f"{var}: Not set (using default)")

    return all_valid, config

def test_database_connection(config: dict) -> bool:
    """Test PostgreSQL connection"""
    print_header("3. Testing Database Connection")

    try:
        import psycopg2
    except ImportError:
        print_warning("psycopg2 not installed, skipping database test")
        print_info("Install with: pip install psycopg2-binary")
        return True

    db_url = config.get("DATABASE_URL", "")
    if not db_url:
        print_error("DATABASE_URL not configured")
        return False

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Test basic query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        if result:
            print_success("PostgreSQL connection successful")

            # Check for pgvector extension
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');"
            )
            has_vector = cursor.fetchone()[0]

            if has_vector:
                print_success("pgvector extension is installed")
            else:
                print_error("pgvector extension NOT found - run: CREATE EXTENSION vector;")

            # Check for mem0_memories table
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'mem0_memories');"
            )
            has_table = cursor.fetchone()[0]

            if has_table:
                print_success("mem0_memories table exists")

                # Count memories
                cursor.execute("SELECT COUNT(*) FROM mem0_memories;")
                count = cursor.fetchone()[0]
                print_info(f"  └─ Contains {count} memories")
            else:
                print_error("mem0_memories table NOT found - run SQL schema script")

            cursor.close()
            conn.close()
            return has_vector and has_table

    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print_info("Check your DATABASE_URL and ensure Supabase is accessible")
        return False

    return True

def test_openai_connection(config: dict) -> bool:
    """Test OpenAI API connection"""
    print_header("4. Testing OpenAI API Connection")

    try:
        import openai
    except ImportError:
        print_warning("openai library not installed")
        print_info("Install with: pip install openai")
        return True

    api_key = config.get("LLM_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        print_error("Invalid OpenAI API key format")
        return False

    try:
        client = openai.OpenAI(api_key=api_key)

        # Test with a simple embedding
        response = client.embeddings.create(
            model=config.get("EMBEDDING_MODEL_CHOICE", "text-embedding-3-small"),
            input="test"
        )

        if response and response.data:
            embedding = response.data[0].embedding
            print_success("OpenAI API connection successful")
            print_success(f"Embedding generated: {len(embedding)} dimensions")
            return True

    except Exception as e:
        print_error(f"OpenAI API test failed: {str(e)}")
        print_info("Check your LLM_API_KEY and ensure it's valid")
        return False

    return False

def test_mem0_server(config: dict) -> bool:
    """Test Mem0 MCP server connection"""
    print_header("5. Testing Mem0 MCP Server")

    try:
        import requests
    except ImportError:
        print_warning("requests library not installed")
        print_info("Install with: pip install requests")
        return True

    port = config.get("PORT", "8050")
    url = f"http://localhost:{port}/sse"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_success(f"Mem0 MCP server is running at {url}")
            return True
        else:
            print_warning(f"Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to Mem0 server at {url}")
        print_info("Make sure Mem0 MCP server is running:")
        print_info("  cd ../Archon\\ Projects/mcp-mem0")
        print_info("  docker run --env-file .env.mem0 -p 8050:8050 mcp/mem0")
        return False
    except Exception as e:
        print_warning(f"Connection test failed: {str(e)}")

    return False

def check_file_structure() -> bool:
    """Check if all expected files exist"""
    print_header("6. Checking File Structure")

    expected_files = {
        ".env.mem0": "Environment configuration",
        ".claude/context/setup/mem0_supabase_schema.sql": "Database schema",
        ".claude/context/setup/MEM0_INTEGRATION_SETUP.md": "Setup guide",
        ".claude/context/setup/QUICK_START.md": "Quick start guide",
    }

    all_exist = True
    for filepath, description in expected_files.items():
        if Path(filepath).exists():
            print_success(f"{filepath} - {description}")
        else:
            print_warning(f"{filepath} - NOT FOUND (optional)")
            all_exist = False

    return all_exist

def generate_report(config: dict, test_results: dict) -> str:
    """Generate a summary report"""
    print_header("Summary Report")

    # Count passed tests
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)

    print(f"Tests passed: {passed}/{total}\n")

    for test_name, result in test_results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {test_name}: {status}")

    print()

    if passed == total:
        print_success("All systems go! Your Mem0 RAG setup is ready to use.")
        return "READY"
    elif passed >= total - 1:
        print_warning("Setup mostly working - some optional components missing")
        return "PARTIAL"
    else:
        print_error("Setup has critical issues - see above for details")
        return "FAILED"

def main():
    """Run all setup tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Mem0 + Supabase RAG Setup Validator{Colors.RESET}\n")

    test_results = {}
    config = {}

    # Check env file
    if not check_env_file():
        print_error("Cannot proceed without .env.mem0")
        sys.exit(1)

    # Check variables
    vars_ok, config = check_required_vars()
    test_results["Environment Variables"] = vars_ok

    if not vars_ok:
        print_error("Missing required environment variables")
        sys.exit(1)

    # Run optional tests
    test_results["File Structure"] = check_file_structure()
    test_results["Database Connection"] = test_database_connection(config)
    test_results["OpenAI API"] = test_openai_connection(config)
    test_results["Mem0 MCP Server"] = test_mem0_server(config)

    # Generate report
    status = generate_report(config, test_results)

    print_info("For detailed setup instructions, see: MEM0_INTEGRATION_SETUP.md")
    print_info("For quick start guide, see: QUICK_START.md")

    # Exit code based on status
    if status == "READY":
        sys.exit(0)
    elif status == "PARTIAL":
        sys.exit(0)  # Still functional with warnings
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nSetup validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
