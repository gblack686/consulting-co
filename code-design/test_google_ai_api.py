#!/usr/bin/env python3
"""
Test script for Google AI (Gemini) API
Retrieves Google AI API key from AWS Secrets Manager and makes a test API call
"""

import boto3
import json
import requests
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return secret


def test_google_gemini_api(api_key):
    """
    Test the Google AI (Gemini) API with a simple text generation request
    """

    # Google AI API endpoint for Gemini
    model = "gemini-2.0-flash-exp"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    # Simple test payload
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello! Please respond with a brief greeting to confirm the API is working."
            }]
        }]
    }

    print("=" * 60)
    print("GOOGLE AI (GEMINI) API TEST")
    print("=" * 60)
    print(f"\nModel: {model}")
    print(f"Endpoint: {url.split('?')[0]}")
    print(f"Test Prompt: {payload['contents'][0]['parts'][0]['text']}")
    print("\nSending request...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✓ SUCCESS! Google AI API is working!")
            result = response.json()

            # Extract the generated text
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    generated_text = candidate['content']['parts'][0]['text']
                    print(f"\nGenerated Response:")
                    print(f"  {generated_text}")

            print(f"\nFull Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✗ ERROR!")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n✗ REQUEST FAILED!")
        print(f"Error: {str(e)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nRetrieving Google AI API key from AWS Secrets Manager...")

    try:
        # Get the API key from AWS Secrets Manager
        api_key = get_secret("gbautomation/core/google-ai-api-key")
        print(f"✓ API key retrieved successfully")

        # Test the Google Gemini API
        test_google_gemini_api(api_key)

    except ClientError as e:
        print(f"\n✗ Failed to retrieve API key from AWS Secrets Manager")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
