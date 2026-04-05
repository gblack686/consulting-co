#!/usr/bin/env python3
"""
Scrape Aura.build documentation using Jina AI and save to Obsidian vault
"""

import boto3
import requests
import os
import re
from pathlib import Path
from datetime import datetime
from botocore.exceptions import ClientError
from urllib.parse import urljoin, urlparse

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
        response = requests.get(jina_url, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"  ✓ Successfully scraped")
            return response.text
        else:
            print(f"  ✗ Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Request failed: {e}")
        return None


def sanitize_filename(title):
    """Convert title to valid filename"""
    # Remove special characters and replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', title)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-').lower()


def create_obsidian_note(title, content, category="aura-docs"):
    """Create a note in Obsidian vault with frontmatter"""

    filename = sanitize_filename(title)
    filepath = os.path.join(OBSIDIAN_VAULT, f"{filename}.md")

    # Create frontmatter
    frontmatter = f"""---
title: {title}
category: {category}
source: Aura.build Documentation
created: {datetime.now().strftime('%Y-%m-%d')}
tags:
  - aura
  - prompting
  - ai-code-design
  - documentation
---

"""

    # Combine frontmatter with content
    full_content = frontmatter + content

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  ✓ Saved: {filepath}")
    return filepath


def extract_navigation_links(content):
    """Extract documentation links from content"""
    # This is a simple extraction - you might want to customize based on Aura's structure
    links = []

    # Look for markdown links
    link_pattern = r'\[([^\]]+)\]\((/learn/[^\)]+)\)'
    matches = re.findall(link_pattern, content)

    for title, path in matches:
        full_url = f"https://www.aura.build{path}"
        links.append((title, full_url))

    return links


def main():
    print("=" * 70)
    print("AURA.BUILD DOCUMENTATION SCRAPER")
    print("=" * 70)
    print()

    # Get Jina AI API key from AWS Secrets Manager
    print("1. Retrieving Jina AI API key from AWS Secrets Manager...")
    try:
        jina_api_key = get_secret("gbautomation/core/jina-ai-api-key")
        print("   ✓ API key retrieved")
    except Exception as e:
        print(f"   ✗ Failed to retrieve API key: {e}")
        return

    print()

    # Define pages to scrape
    base_url = "https://www.aura.build"
    pages_to_scrape = [
        ("Introduction", "https://www.aura.build/learn/introduction"),
        ("Getting Started", "https://www.aura.build/learn/getting-started"),
        ("Prompting Strategies", "https://www.aura.build/learn/prompting-strategies"),
        ("Best Practices", "https://www.aura.build/learn/best-practices"),
        ("Examples", "https://www.aura.build/learn/examples"),
        ("API Reference", "https://www.aura.build/learn/api-reference"),
    ]

    print(f"2. Scraping {len(pages_to_scrape)} documentation pages...")
    print()

    scraped_content = []

    for title, url in pages_to_scrape:
        print(f"Processing: {title}")
        content = scrape_with_jina(url, jina_api_key)

        if content:
            # Save to Obsidian
            filepath = create_obsidian_note(title, content)
            scraped_content.append((title, url, filepath))

            # Extract additional links (for future scraping)
            links = extract_navigation_links(content)
            if links:
                print(f"  Found {len(links)} additional links")

        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nSuccessfully scraped {len(scraped_content)} pages:")

    for title, url, filepath in scraped_content:
        print(f"\n✓ {title}")
        print(f"  Source: {url}")
        print(f"  Saved: {filepath}")

    print()
    print(f"All documentation saved to: {OBSIDIAN_VAULT}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
