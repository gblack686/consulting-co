"""
Secrets Manager local file cache.
Reduces AWS API calls by caching secret values on disk with a TTL.

Cache location: state/.secret_cache.json
Default TTL: 3600s (1 hour)
"""
import json
import time
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / "state" / ".secret_cache.json"
DEFAULT_TTL = 3600  # 1 hour


def _load() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save(cache: dict):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))


def get_secret(secret_id: str, region: str = "us-east-1", ttl: int = DEFAULT_TTL) -> dict:
    """
    Return parsed secret dict. Fetches from AWS only if cache is stale.
    """
    cache = _load()
    entry = cache.get(secret_id)

    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["value"]

    import boto3
    sm = boto3.client("secretsmanager", region_name=region)
    value = json.loads(sm.get_secret_value(SecretId=secret_id)["SecretString"])

    cache[secret_id] = {"ts": time.time(), "value": value}
    _save(cache)
    return value
