#!/usr/bin/env python3
"""
ElevenLabs Usage Checker
Checks voice AI character credits and subscription status.
"""

import argparse
import json
import os
from typing import Optional

import requests

# Try to import boto3 for AWS Secrets Manager
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_api_key() -> str:
    """Get ElevenLabs API key from various sources."""
    # 1. Environment variable
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            # Try RevStar shared first, then gbautomation
            for secret_name in ["revstar/shared/elevenlabs", "gbautomation/core/elevenlabs-api-key"]:
                try:
                    response = client.get_secret_value(SecretId=secret_name)
                    secret = response["SecretString"]
                    # Handle JSON format
                    try:
                        data = json.loads(secret)
                        return data.get("api_key", data.get("ELEVENLABS_API_KEY", secret))
                    except json.JSONDecodeError:
                        return secret
                except Exception:
                    continue
        except Exception:
            pass

    raise ValueError("No ElevenLabs API key found. Set ELEVENLABS_API_KEY or store in AWS Secrets Manager.")


def check_elevenlabs_usage(show_voices: bool = False) -> dict:
    """
    Check ElevenLabs subscription and character usage.

    Returns:
        dict with usage information
    """
    api_key = get_api_key()

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Get subscription info
        response = requests.get(
            "https://api.elevenlabs.io/v1/user/subscription",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            character_count = data.get("character_count", 0)
            character_limit = data.get("character_limit", 0)
            tier = data.get("tier", "unknown")
            next_reset = data.get("next_character_count_reset_unix")

            # Calculate remaining
            remaining = max(0, character_limit - character_count)
            percent_used = (character_count / character_limit * 100) if character_limit > 0 else 0

            result = {
                "status": "success",
                "tier": tier,
                "character_count": character_count,
                "character_limit": character_limit,
                "remaining_characters": remaining,
                "percent_used": percent_used,
                "used_display": f"{character_count:,} chars",
                "remaining_display": f"{remaining:,} chars",
                "status_display": f"{percent_used:.0f}% used",
                "voice_limit": data.get("voice_limit", 0),
                "can_use_instant_voice_cloning": data.get("can_use_instant_voice_cloning", False),
                "can_use_professional_voice_cloning": data.get("can_use_professional_voice_cloning", False),
            }

            if next_reset:
                from datetime import datetime
                reset_date = datetime.fromtimestamp(next_reset)
                result["next_reset"] = reset_date.strftime("%Y-%m-%d")
                result["days_until_reset"] = (reset_date - datetime.now()).days

            # Get voice list if requested
            if show_voices:
                voices_response = requests.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers=headers,
                    timeout=30
                )
                if voices_response.status_code == 200:
                    voices_data = voices_response.json()
                    result["voices"] = [
                        {
                            "name": v.get("name"),
                            "voice_id": v.get("voice_id"),
                            "category": v.get("category")
                        }
                        for v in voices_data.get("voices", [])
                    ]
                    result["voice_count"] = len(result["voices"])

            return result

        elif response.status_code == 401:
            return {
                "status": "error",
                "error": "Invalid API key"
            }
        else:
            return {
                "status": "error",
                "error": f"API returned status {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "Request timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Check ElevenLabs subscription usage")
    parser.add_argument("--show-voices", action="store_true", help="Include voice list")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_elevenlabs_usage(show_voices=args.show_voices)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== ElevenLabs Usage ===\n")
        for key, value in result.items():
            if key == "voices":
                print(f"  voices: {len(value)} voices")
                for v in value[:5]:  # Show first 5
                    print(f"    - {v['name']} ({v['category']})")
                if len(value) > 5:
                    print(f"    ... and {len(value) - 5} more")
            elif not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
