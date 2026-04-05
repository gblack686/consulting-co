#!/usr/bin/env python3
"""
MTG Art Finder - Search Magic: The Gathering cards via Scryfall API

Searches for cards by name, oracle text (function), and color filters.
Returns card details and high-resolution art URLs.
"""

import requests
import time
import random
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import quote


@dataclass
class MTGCard:
    """Represents a Magic: The Gathering card."""
    name: str
    set_name: str
    set_code: str
    collector_number: str
    mana_cost: str
    type_line: str
    oracle_text: str
    colors: List[str]
    color_identity: List[str]
    rarity: str
    artist: str
    # Image URLs
    image_small: str
    image_normal: str
    image_large: str
    image_art_crop: str  # Just the art, no border
    image_png: str  # High-res PNG
    # Links
    scryfall_uri: str
    gatherer_uri: Optional[str] = None

    def __str__(self):
        colors_str = ''.join(self.colors) if self.colors else 'Colorless'
        return f"{self.name} ({colors_str}) - {self.set_name} [{self.rarity}]"


class MTGArtFinder:
    """Search for MTG cards and retrieve art using Scryfall API."""

    BASE_URL = "https://api.scryfall.com"

    # Color mappings
    COLOR_MAP = {
        'white': 'W', 'w': 'W',
        'blue': 'U', 'u': 'U',
        'black': 'B', 'b': 'B',
        'red': 'R', 'r': 'R',
        'green': 'G', 'g': 'G',
        'colorless': 'C', 'c': 'C',
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGArtFinder/1.0',
            'Accept': 'application/json'
        })
        self.last_request_time = 0

    def _rate_limit(self):
        """Scryfall asks for 50-100ms between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.1:
            time.sleep(0.1 - elapsed)
        self.last_request_time = time.time()

    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a rate-limited request to Scryfall API."""
        self._rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _parse_card(self, data: Dict) -> MTGCard:
        """Parse Scryfall card data into MTGCard object."""
        # Handle double-faced cards
        images = data.get('image_uris', {})
        if not images and 'card_faces' in data:
            # Use front face images
            images = data['card_faces'][0].get('image_uris', {})

        return MTGCard(
            name=data.get('name', ''),
            set_name=data.get('set_name', ''),
            set_code=data.get('set', ''),
            collector_number=data.get('collector_number', ''),
            mana_cost=data.get('mana_cost', ''),
            type_line=data.get('type_line', ''),
            oracle_text=data.get('oracle_text', ''),
            colors=data.get('colors', []),
            color_identity=data.get('color_identity', []),
            rarity=data.get('rarity', ''),
            artist=data.get('artist', ''),
            image_small=images.get('small', ''),
            image_normal=images.get('normal', ''),
            image_large=images.get('large', ''),
            image_art_crop=images.get('art_crop', ''),
            image_png=images.get('png', ''),
            scryfall_uri=data.get('scryfall_uri', ''),
            gatherer_uri=data.get('related_uris', {}).get('gatherer'),
        )

    def _normalize_colors(self, colors: List[str]) -> List[str]:
        """Convert color names to Scryfall color codes."""
        normalized = []
        for color in colors:
            c = color.lower().strip()
            if c in self.COLOR_MAP:
                normalized.append(self.COLOR_MAP[c])
            elif c.upper() in ['W', 'U', 'B', 'R', 'G', 'C']:
                normalized.append(c.upper())
        return normalized

    def search_by_name(self, name: str, exact: bool = False) -> List[MTGCard]:
        """
        Search for cards by name.

        Args:
            name: Card name to search for
            exact: If True, search for exact name match

        Returns:
            List of matching MTGCard objects
        """
        if exact:
            # Exact name search
            try:
                data = self._request('/cards/named', {'exact': name})
                return [self._parse_card(data)]
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    return []
                raise
        else:
            # Fuzzy/partial name search
            query = f'name:"{name}"'
            return self.search(query)

    def search_by_text(self, text: str, colors: List[str] = None) -> List[MTGCard]:
        """
        Search for cards by oracle text (card function/ability).

        Args:
            text: Text to search for in card rules
            colors: Optional list of colors to filter by

        Returns:
            List of matching MTGCard objects
        """
        query = f'oracle:"{text}"'

        if colors:
            color_codes = self._normalize_colors(colors)
            if color_codes:
                query += f' color:{",".join(color_codes)}'

        return self.search(query)

    def search_by_color(self, colors: List[str], exact: bool = False) -> List[MTGCard]:
        """
        Search for cards by color.

        Args:
            colors: List of colors (e.g., ['red', 'blue'] or ['R', 'U'])
            exact: If True, match exact color combination only

        Returns:
            List of matching MTGCard objects
        """
        color_codes = self._normalize_colors(colors)
        if not color_codes:
            return []

        color_str = ','.join(color_codes)
        if exact:
            query = f'color={color_str}'  # Exact match
        else:
            query = f'color<={color_str}'  # Include subset

        return self.search(query)

    def search(self, query: str, unique: str = 'cards', order: str = 'name',
               include_extras: bool = False, limit: int = 50) -> List[MTGCard]:
        """
        Perform a full Scryfall search query.

        Args:
            query: Scryfall search syntax query
            unique: 'cards', 'art', or 'prints'
            order: Sort order ('name', 'released', 'rarity', 'color', 'usd', 'edhrec')
            include_extras: Include tokens, promos, etc.
            limit: Maximum number of results

        Returns:
            List of matching MTGCard objects
        """
        cards = []
        params = {
            'q': query,
            'unique': unique,
            'order': order,
            'include_extras': str(include_extras).lower(),
        }

        try:
            data = self._request('/cards/search', params)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return []
            raise

        # Parse results
        for card_data in data.get('data', [])[:limit]:
            try:
                cards.append(self._parse_card(card_data))
            except Exception as e:
                print(f"Warning: Failed to parse card: {e}")
                continue

        return cards

    def get_random_card(self, query: str = None) -> Optional[MTGCard]:
        """
        Get a random card, optionally matching a query.

        Args:
            query: Optional Scryfall search query to filter random selection

        Returns:
            A random MTGCard or None
        """
        params = {}
        if query:
            params['q'] = query

        try:
            data = self._request('/cards/random', params)
            return self._parse_card(data)
        except requests.HTTPError:
            return None

    def get_card_art_url(self, card: MTGCard, size: str = 'art_crop') -> str:
        """
        Get the art URL for a card.

        Args:
            card: MTGCard object
            size: 'small', 'normal', 'large', 'art_crop', or 'png'

        Returns:
            URL to the card art
        """
        size_map = {
            'small': card.image_small,
            'normal': card.image_normal,
            'large': card.image_large,
            'art_crop': card.image_art_crop,
            'png': card.image_png,
        }
        return size_map.get(size, card.image_art_crop)

    def download_art(self, card: MTGCard, output_path: str, size: str = 'art_crop') -> bool:
        """
        Download card art to a file.

        Args:
            card: MTGCard object
            output_path: Path to save the image
            size: Image size to download

        Returns:
            True if successful
        """
        url = self.get_card_art_url(card, size)
        if not url:
            return False

        self._rate_limit()
        response = self.session.get(url)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return True

    def search_for_agent(self, purpose: str, top_n: int = 20,
                         pick_random: int = 1) -> List[MTGCard]:
        """
        Search for MTG cards that match a Claude Code agent's purpose.

        Extracts key concepts from the purpose text and translates them
        to Scryfall search queries. Returns randomized results from
        the top matches to add variety.

        Args:
            purpose: The agent's purpose/description text
            top_n: Number of top results to consider (default 20)
            pick_random: Number of random cards to return from top_n (default 5)

        Returns:
            List of MTGCard objects (randomized from top results)
        """
        # Extract key concepts and build search query
        query_parts = []
        purpose_lower = purpose.lower()

        # Keyword to MTG concept mapping
        concept_map = {
            # Creation/Building
            ('create', 'write', 'build', 'generate', 'implement', 'construct'):
                'oracle:create type:creature',
            ('engineer', 'artificer', 'builder'):
                '(type:artificer OR type:engineer)',

            # Planning/Strategy
            ('plan', 'strategic', 'analyze', 'design', 'architect'):
                '(oracle:scry OR oracle:"look at")',
            ('research', 'investigate', 'explore', 'scout'):
                '(oracle:scry OR oracle:"search your library")',

            # Validation/Testing
            ('validate', 'test', 'verify', 'check', 'protect'):
                '(oracle:prevent OR oracle:indestructible OR oracle:hexproof)',

            # Speed/Execution
            ('fast', 'quick', 'rapid', 'immediate'):
                'oracle:haste',

            # Memory/Persistence
            ('memory', 'store', 'persist', 'remember', 'retrieve'):
                '(oracle:graveyard OR oracle:"return from")',

            # Copying/Spawning
            ('copy', 'spawn', 'clone', 'duplicate', 'meta'):
                'oracle:"create a copy"',

            # Information Gathering
            ('scrape', 'fetch', 'gather', 'collect', 'draw'):
                'oracle:"draw a card"',

            # Transformation
            ('transform', 'convert', 'modify', 'edit'):
                '(oracle:transform OR oracle:"becomes a")',
        }

        # Check which concepts match
        matched_queries = []
        for keywords, query in concept_map.items():
            if any(kw in purpose_lower for kw in keywords):
                matched_queries.append(query)

        # Build final query
        if matched_queries:
            # Combine up to 2 matched concepts
            query = ' '.join(matched_queries[:2])
        else:
            # Fallback: search for creature with "create"
            query = 'type:creature oracle:create'

        # Add creature type for better art
        if 'type:creature' not in query:
            query = f'type:creature {query}'

        # Search with popularity ordering
        cards = self.search(query, order='edhrec', limit=top_n)

        # Randomize from top results
        if cards and len(cards) > pick_random:
            random.shuffle(cards)
            cards = cards[:pick_random]

        return cards

    def extract_agent_color(self, purpose: str) -> str:
        """
        Determine the MTG color identity based on agent purpose.

        Args:
            purpose: The agent's purpose/description

        Returns:
            Color name (White, Blue, Black, Red, Green, or Colorless)
        """
        purpose_lower = purpose.lower()

        # Color mapping based on Claude Code concept mapping
        color_signals = {
            'White': ['validate', 'protect', 'rule', 'permission', 'safe', 'govern', 'order'],
            'Blue': ['plan', 'analyze', 'research', 'strategy', 'optimize', 'intelligence', 'think'],
            'Black': ['memory', 'persist', 'store', 'retrieve', 'data', 'state', 'history'],
            'Red': ['fast', 'quick', 'build', 'execute', 'deploy', 'speed', 'immediate'],
            'Green': ['grow', 'adapt', 'learn', 'scale', 'improve', 'evolve', 'feedback'],
        }

        scores = {color: 0 for color in color_signals}

        for color, keywords in color_signals.items():
            for keyword in keywords:
                if keyword in purpose_lower:
                    scores[color] += 1

        # Return highest scoring color, or Colorless if no matches
        max_color = max(scores, key=scores.get)
        return max_color if scores[max_color] > 0 else 'Colorless'


def format_card_display(card: MTGCard) -> str:
    """Format a card for display."""
    lines = [
        f"{'='*60}",
        f"  {card.name}",
        f"  {card.mana_cost}",
        f"{'='*60}",
        f"  Type: {card.type_line}",
        f"  Colors: {', '.join(card.colors) if card.colors else 'Colorless'}",
        f"  Set: {card.set_name} ({card.set_code.upper()}) #{card.collector_number}",
        f"  Rarity: {card.rarity.capitalize()}",
        f"  Artist: {card.artist}",
        f"",
        f"  Oracle Text:",
    ]

    # Wrap oracle text
    if card.oracle_text:
        for line in card.oracle_text.split('\n'):
            lines.append(f"    {line}")

    lines.extend([
        f"",
        f"  Art URL: {card.image_art_crop}",
        f"  Scryfall: {card.scryfall_uri}",
        f"{'='*60}",
    ])

    return '\n'.join(lines)


if __name__ == '__main__':
    import sys

    finder = MTGArtFinder()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mtg_search.py name <card_name>")
        print("  python mtg_search.py text <oracle_text> [color1,color2,...]")
        print("  python mtg_search.py color <color1,color2,...>")
        print("  python mtg_search.py random [query]")
        print("  python mtg_search.py agent <purpose_text> [top_n] [pick_random]")
        print("  python mtg_search.py agent-file <agent_md_file> [top_n] [pick_random]")
        print("")
        print("Examples:")
        print("  python mtg_search.py name 'Lightning Bolt'")
        print("  python mtg_search.py text 'draw a card' blue")
        print("  python mtg_search.py color red,blue")
        print("  python mtg_search.py random 'type:creature color:green'")
        print("  python mtg_search.py agent 'specialized file implementation engineer'")
        print("  python mtg_search.py agent-file /path/to/build-agent.md 20 5")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'name':
        name = sys.argv[2] if len(sys.argv) > 2 else ''
        print(f"Searching for cards named '{name}'...\n")
        cards = finder.search_by_name(name)

    elif command == 'text':
        text = sys.argv[2] if len(sys.argv) > 2 else ''
        colors = sys.argv[3].split(',') if len(sys.argv) > 3 else None
        print(f"Searching for cards with text '{text}'" +
              (f" in colors {colors}" if colors else "") + "...\n")
        cards = finder.search_by_text(text, colors)

    elif command == 'color':
        colors = sys.argv[2].split(',') if len(sys.argv) > 2 else []
        print(f"Searching for {colors} cards...\n")
        cards = finder.search_by_color(colors)

    elif command == 'random':
        query = sys.argv[2] if len(sys.argv) > 2 else None
        print(f"Getting random card" + (f" matching '{query}'" if query else "") + "...\n")
        card = finder.get_random_card(query)
        cards = [card] if card else []

    elif command == 'agent':
        purpose = sys.argv[2] if len(sys.argv) > 2 else ''
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        pick_random = int(sys.argv[4]) if len(sys.argv) > 4 else 1

        # Detect color from purpose
        color = finder.extract_agent_color(purpose)
        print(f"Agent Purpose: {purpose[:100]}...")
        print(f"Detected Color: {color}")
        print(f"Searching top {top_n}, returning {pick_random} randomized...\n")

        cards = finder.search_for_agent(purpose, top_n, pick_random)

    elif command == 'agent-file':
        filepath = sys.argv[2] if len(sys.argv) > 2 else ''
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        pick_random = int(sys.argv[4]) if len(sys.argv) > 4 else 1

        # Read agent file and extract purpose
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract purpose section
            purpose_match = re.search(r'## Purpose\s*\n(.*?)(?=\n##|\n```|$)',
                                      content, re.DOTALL)
            if purpose_match:
                purpose = purpose_match.group(1).strip()
            else:
                # Try to get from frontmatter or first paragraph
                purpose = content[:500]

            # Extract agent name
            name_match = re.search(r'name:\s*["\']?([^"\'}\n]+)', content)
            agent_name = name_match.group(1).strip() if name_match else 'Unknown'

            color = finder.extract_agent_color(purpose)
            print(f"Agent: {agent_name}")
            print(f"Purpose: {purpose[:150]}...")
            print(f"Detected Color: {color}")
            print(f"Searching top {top_n}, returning {pick_random} randomized...\n")

            cards = finder.search_for_agent(purpose, top_n, pick_random)

        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    if cards:
        print(f"Found {len(cards)} card(s):\n")
        for card in cards[:10]:  # Show max 10
            print(format_card_display(card))
            print()
    else:
        print("No cards found.")
