"""
DNS Resolution Helper for Windows Compatibility

Resolves hostnames to IP addresses using synchronous socket operations
to avoid Windows asyncio DNS issues.
"""

import socket
from typing import Dict, Tuple
from urllib.parse import urlparse

# Cache resolved IPs
_dns_cache: Dict[Tuple[str, int], str] = {}


def resolve_hostname(hostname: str, port: int) -> str:
    """
    Synchronously resolve hostname to IP address.

    Args:
        hostname: Hostname to resolve
        port: Port number (used for cache key)

    Returns:
        IP address as string

    Raises:
        socket.gaierror: If DNS resolution fails
    """
    cache_key = (hostname, port)

    # Return cached result if available
    if cache_key in _dns_cache:
        return _dns_cache[cache_key]

    # Resolve using synchronous socket (avoids asyncio issues)
    result = socket.getaddrinfo(hostname, port, socket.AF_INET, socket.SOCK_STREAM)
    ip = result[0][4][0]

    # Cache for future use
    _dns_cache[cache_key] = ip

    return ip


def parse_and_resolve_database_url(url: str) -> Dict[str, any]:
    """
    Parse PostgreSQL connection URL and resolve hostname to IP.

    Args:
        url: PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/db)

    Returns:
        Dictionary with connection parameters including resolved IP

    Example:
        >>> params = parse_and_resolve_database_url(
        ...     "postgresql://user:pass@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
        ... )
        >>> params['host']  # Returns IP like "52.8.172.168"
    """
    parsed = urlparse(url)

    # Extract components
    hostname = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path.lstrip('/') or 'postgres'
    username = parsed.username
    password = parsed.password

    # Resolve hostname to IP (synchronous - no asyncio issues)
    ip = resolve_hostname(hostname, port)

    return {
        'host': ip,
        'port': port,
        'database': database,
        'user': username,
        'password': password,
        'original_hostname': hostname
    }


def clear_dns_cache():
    """Clear the DNS resolution cache."""
    _dns_cache.clear()
