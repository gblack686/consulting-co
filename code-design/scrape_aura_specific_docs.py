#!/usr/bin/env python3
"""
Scrape specific Aura.build prompting documentation pages
"""

import boto3
import requests
import os
import re
from pathlib import Path
from datetime import datetime
from botocore.exceptions import ClientError

# Obsidian vault path
OBSIDIAN_VAULT = "C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/code-design"

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

    return get_secret_value_response['SecretString']


def scrape_with_jina(url, api_key):
    """Scrape a URL using Jina AI Reader API"""
    jina_url = f"https://r.jina.ai/{url}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Return-Format": "markdown"
    }

    print(f"  Scraping: {url}")

    try:
        response = requests.get(jina_url, headers=headers, timeout=60)

        if response.status_code == 200:
            print(f"  ✓ Successfully scraped ({len(response.text)} characters)")
            return response.text
        else:
            print(f"  ✗ Error: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request failed: {e}")
        return None


def sanitize_filename(title):
    """Convert title to valid filename"""
    filename = re.sub(r'[^\w\s-]', '', title)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-').lower()


def create_obsidian_note(title, content, url, category="aura-prompting"):
    """Create a note in Obsidian vault with frontmatter"""

    filename = sanitize_filename(title)
    filepath = os.path.join(OBSIDIAN_VAULT, f"{filename}.md")

    # Create frontmatter
    frontmatter = f"""---
title: {title}
category: {category}
source: {url}
created: {datetime.now().strftime('%Y-%m-%d')}
tags:
  - aura
  - prompting
  - ai-code-design
  - ui-generation
---

# {title}

"""

    # Combine frontmatter with content
    full_content = frontmatter + content

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  ✓ Saved: {os.path.basename(filepath)}")
    return filepath


def main():
    print("=" * 70)
    print("AURA.BUILD PROMPTING DOCUMENTATION SCRAPER")
    print("=" * 70)
    print()

    # Get Jina AI API key
    print("1. Retrieving Jina AI API key...")
    try:
        jina_api_key = get_secret("gbautomation/core/jina-ai-api-key")
        print("   ✓ API key retrieved")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return

    print()

    # Specific prompting guide pages
    pages_to_scrape = [
        ("Tips for Prompting", "https://www.aura.build/learn/tips-for-prompting"),
        ("Typography Prompting", "https://www.aura.build/learn/typography-prompting"),
        ("Styling Prompting", "https://www.aura.build/learn/styling-prompting"),
        ("Animation Prompting", "https://www.aura.build/learn/animation-prompting"),
        ("Layout Prompting", "https://www.aura.build/learn/layout-prompting"),
        ("How to Edit Designs", "https://www.aura.build/learn/how-to-edit-designs"),
        ("Selling Templates", "https://www.aura.build/learn/selling-templates"),
    ]

    print(f"2. Scraping {len(pages_to_scrape)} prompting guide pages...")
    print()

    scraped_content = []

    for title, url in pages_to_scrape:
        print(f"Processing: {title}")
        content = scrape_with_jina(url, jina_api_key)

        if content:
            filepath = create_obsidian_note(title, content, url)
            scraped_content.append((title, url, filepath))
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nSuccessfully scraped {len(scraped_content)} prompting guides:")

    for title, url, filepath in scraped_content:
        print(f"\n✓ {title}")
        print(f"  {os.path.basename(filepath)}")

    print()
    print(f"All guides saved to: {OBSIDIAN_VAULT}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
