#!/usr/bin/env python3
"""
Update all agent files with MTG card art based on their purpose.
"""

import os
import re
import sys
from mtg_search import MTGArtFinder


def extract_purpose(content: str) -> str:
    """Extract purpose section from agent markdown."""
    purpose_match = re.search(r'## Purpose\s*\n(.*?)(?=\n##|\n```|$)', content, re.DOTALL)
    if purpose_match:
        return purpose_match.group(1).strip()
    return content[:500]


def extract_agent_name(content: str) -> str:
    """Extract agent name from frontmatter."""
    name_match = re.search(r'name:\s*["\']?([^"\'\n}]+)', content)
    if name_match:
        return name_match.group(1).strip()
    return "Unknown"


def update_agent_file(filepath: str, card_name: str, color: str, art_url: str) -> bool:
    """Update agent file frontmatter with MTG card info."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # First, clean up any duplicate frontmatter blocks
    # Pattern: ---\nbanner:...\n---\n---\n becomes ---\n
    content = re.sub(r'^---\s*\nbanner:[^\n]+\n---\s*\n---\s*\n', '---\n', content)

    # Also handle other duplicate frontmatter patterns
    content = re.sub(r'^---\s*\n[^-]+\n---\s*\n---\s*\n', '---\n', content)

    # Update or add banner (only update the first occurrence in frontmatter)
    if 'banner:' in content:
        content = re.sub(r'banner:\s*["\']?[^"\'\n]+["\']?', f'banner: "{art_url}"', content, count=1)

    # Update or add mtg_card
    if 'mtg_card:' in content:
        content = re.sub(r'mtg_card:\s*["\']?[^"\'\n]+["\']?', f'mtg_card: "{card_name}"', content, count=1)
    else:
        # Add after banner line
        content = re.sub(r'(banner:\s*["\']?[^"\'\n]+["\']?)', f'\\1\nmtg_card: "{card_name}"', content, count=1)

    # Update or add mtg_color
    if 'mtg_color:' in content:
        content = re.sub(r'mtg_color:\s*["\']?[^"\'\n]+["\']?', f'mtg_color: "{color}"', content, count=1)
    else:
        # Add after mtg_card line
        content = re.sub(r'(mtg_card:\s*["\']?[^"\'\n]+["\']?)', f'\\1\nmtg_color: "{color}"', content, count=1)

    # Update inline image if present (after frontmatter)
    content = re.sub(
        r'!\[([^\]]*)\]\(https://cards\.scryfall\.io/[^)]+\)',
        f'![{card_name}]({art_url})',
        content,
        count=1
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    agents_dir = r'C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation\AI-Agent-KB\02-Agents'

    if len(sys.argv) > 1:
        agents_dir = sys.argv[1]

    finder = MTGArtFinder()
    results = []

    print(f"Scanning agents in: {agents_dir}\n")

    for filename in sorted(os.listdir(agents_dir)):
        if filename.endswith('.md') and not filename.startswith('_'):
            filepath = os.path.join(agents_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            purpose = extract_purpose(content)
            agent_name = extract_agent_name(content)

            # Search for card
            cards = finder.search_for_agent(purpose, top_n=20, pick_random=1)
            color = finder.extract_agent_color(purpose)

            if cards:
                card = cards[0]
                results.append({
                    'agent': agent_name,
                    'file': filename,
                    'card': card.name,
                    'color': color,
                    'art_url': card.image_art_crop,
                    'type': card.type_line
                })

                # Update the file
                update_agent_file(filepath, card.name, color, card.image_art_crop)

                print(f"✓ {agent_name}")
                print(f"  Card: {card.name}")
                print(f"  Color: {color}")
                print(f"  Art: {card.image_art_crop}")
                print()
            else:
                print(f"✗ {agent_name}: No cards found\n")

    print("=" * 60)
    print(f"Updated {len(results)} agents")
    print("=" * 60)

    return results


if __name__ == '__main__':
    main()
