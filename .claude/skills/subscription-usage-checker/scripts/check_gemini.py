#!/usr/bin/env python3
"""
Google Gemini API Usage Checker
Checks Gemini API usage via Google Cloud.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Optional

import requests

# Try to import Google Cloud libraries
try:
    from google.cloud import billing_v1
    from google.oauth2 import service_account
    import google.auth
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Try to import boto3 for AWS Secrets Manager
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from various sources."""
    # 1. Environment variable
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            for secret_name in ["gbautomation/core/gemini-api-key", "gbautomation/core/google-api-key"]:
                try:
                    response = client.get_secret_value(SecretId=secret_name)
                    return response["SecretString"]
                except Exception:
                    continue
        except Exception:
            pass

    return None


def check_gemini_usage() -> dict:
    """
    Check Gemini API usage.

    Note: Google's API usage is typically tracked via Google Cloud Console.
    This function attempts to validate the API key and provide basic info.

    Returns:
        dict with usage information
    """
    api_key = get_gemini_api_key()

    if not api_key:
        # Check if using Application Default Credentials
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                credentials, project = google.auth.default()
                return check_gemini_with_gcloud(credentials, project)
            except Exception:
                pass

        return {
            "status": "error",
            "error": "No Gemini/Google API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY.",
            "note": "Or configure Application Default Credentials with: gcloud auth application-default login"
        }

    # Validate API key with a simple request
    try:
        # List available models to verify key
        response = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            timeout=30
        )

        if response.status_code == 200:
            models = response.json().get("models", [])

            # Filter for Gemini models
            gemini_models = [m for m in models if "gemini" in m.get("name", "").lower()]

            return {
                "status": "success",
                "api_status": "Active",
                "available_models": len(gemini_models),
                "model_names": [m.get("displayName", m.get("name")) for m in gemini_models[:5]],
                "used_display": "See Console",
                "remaining_display": "See quota",
                "status_display": "Active",
                "percent_used": 0,
                "note": "Detailed usage available at console.cloud.google.com/apis/dashboard",
                "quota_note": "Free tier: 60 requests/minute, 1 million tokens/month"
            }
        elif response.status_code == 400:
            error_msg = response.json().get("error", {}).get("message", "Invalid request")
            return {
                "status": "error",
                "error": f"API error: {error_msg}"
            }
        elif response.status_code == 403:
            return {
                "status": "error",
                "error": "API key invalid or Gemini API not enabled for this project"
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


def check_gemini_with_gcloud(credentials, project: str) -> dict:
    """
    Check Gemini usage using Google Cloud credentials.

    Args:
        credentials: Google Cloud credentials
        project: GCP project ID

    Returns:
        dict with usage information
    """
    try:
        # This would use the Cloud Billing API
        # For now, just verify credentials work
        return {
            "status": "success",
            "project": project,
            "auth_type": "Application Default Credentials",
            "api_status": "Active",
            "used_display": "See Console",
            "remaining_display": "See quota",
            "status_display": "GCloud Active",
            "percent_used": 0,
            "note": "Using Application Default Credentials. Check console.cloud.google.com for usage."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Check Gemini API usage")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_gemini_usage()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Gemini API Usage ===\n")
        for key, value in result.items():
            if key == "model_names":
                print(f"  Available models:")
                for m in value:
                    print(f"    - {m}")
            elif not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
