"""
ULTRA-FAST VTT PROCESSOR
Handles multiple input formats:
- cURL commands with VTT URLs
- Plain VTT URLs
- Raw VTT content
"""

import urllib.request
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def clean_vtt_line(line):
    """Clean a single VTT caption line"""
    line = re.sub(r'<[^>]+>', '', line)
    line = re.sub(r'</?[a-z].*?>', '', line)
    return line.strip()

def extract_urls_from_text(text):
    """Extract all VTT URLs from any text format (cURL, plain URLs, etc.)"""
    # Find all URLs containing .vtt
    url_pattern = r'https?://[^\s"\'<>]+\.vtt[^\s"\'<>]*'
    urls = re.findall(url_pattern, text)

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls

def extract_chunk_number(url):
    """Extract chunk number from URL"""
    match = re.search(r'/(\d+)\.vtt', url)
    return int(match.group(1)) if match else 999999

def download_vtt(url, chunk_num):
    """Download and parse a single VTT file"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')

        lines = content.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()

            if (not line or
                line.startswith('WEBVTT') or
                '-->' in line or
                line.isdigit() or
                line.startswith(('STYLE', 'NOTE', 'Kind:', 'Language:'))):
                continue

            cleaned = clean_vtt_line(line)
            if cleaned:
                text_lines.append(cleaned)

        return chunk_num, text_lines, True
    except Exception as e:
        return chunk_num, [], False

def parse_raw_vtt(content):
    """Parse raw VTT content"""
    lines = content.split('\n')
    text_lines = []

    for line in lines:
        line = line.strip()

        if (not line or
            line.startswith('WEBVTT') or
            '-->' in line or
            line.isdigit() or
            line.startswith(('STYLE', 'NOTE', 'Kind:', 'Language:'))):
            continue

        cleaned = clean_vtt_line(line)
        if cleaned:
            text_lines.append(cleaned)

    return text_lines

def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_vtt_processor.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    print("=" * 70)
    print("ULTRA-FAST VTT PROCESSOR")
    print("=" * 70)
    print(f"\nReading: {input_file}")

    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        print("✗ Input file is empty!")
        sys.exit(1)

    # Try to extract URLs
    urls = extract_urls_from_text(content)

    if urls:
        print(f"✓ Found {len(urls)} VTT URLs")

        # Sort by chunk number
        sorted_urls = sorted(urls, key=extract_chunk_number)

        print("\nDownloading in parallel (max 10 concurrent)...")
        print("-" * 70)

        all_chunks = []
        success_count = 0
        fail_count = 0

        # Download in parallel with thread pool
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(download_vtt, url, extract_chunk_number(url)): url
                for url in sorted_urls
            }

            for future in as_completed(futures):
                chunk_num, text_lines, success = future.result()
                all_chunks.append((chunk_num, text_lines, success))

                if success:
                    success_count += 1
                    print(f"  ✓ Chunk {chunk_num:3d} ({len(text_lines)} lines)")
                else:
                    fail_count += 1
                    print(f"  ✗ Chunk {chunk_num:3d} FAILED")

        # Sort by chunk number
        all_chunks.sort(key=lambda x: x[0])

        # Combine all text
        all_text = []
        for chunk_num, text_lines, success in all_chunks:
            if success:
                all_text.extend(text_lines)

        full_transcript = '\n'.join(all_text)

    else:
        # No URLs found - treat as raw VTT content
        print("No URLs found - parsing as raw VTT content...")
        text_lines = parse_raw_vtt(content)
        full_transcript = '\n'.join(text_lines)
        success_count = 1 if text_lines else 0
        fail_count = 0

    if not full_transcript.strip():
        print("\n✗ No transcript content extracted!")
        sys.exit(1)

    # Generate output filename from input
    input_path = Path(input_file)
    output_file = input_path.parent / f"{input_path.stem}_transcript.txt"

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print()
    print("=" * 70)
    print("✓ EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\n📄 Output: {output_file}")
    print(f"📊 Successful: {success_count}")
    print(f"📊 Failed: {fail_count}")
    print(f"📊 Characters: {len(full_transcript):,}")
    print(f"📊 Words: {len(full_transcript.split()):,}")
    print(f"📊 Lines: {len(full_transcript.splitlines()):,}")
    print()
    print("=" * 70)
    print("Preview (first 500 characters):")
    print("=" * 70)
    print(full_transcript[:500])
    if len(full_transcript) > 500:
        print("\n... (transcript continues)")
    print("=" * 70)

if __name__ == "__main__":
    main()
