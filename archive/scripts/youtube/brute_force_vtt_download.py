"""
Try to download all VTT chunks by brute force
Uses a known working signature to attempt all chunk numbers
"""

import urllib.request
import re
import time

# Base URL pattern
BASE_URL = "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/{chunk}.vtt?skid=edgemv-default-1&signature={signature}"

# Use a recent working signature (from chunk 144)
SIGNATURE = "NjkyNTYyMDBfYWZjMGM3MmJhZTY2MWNiNjU2OGM3Mjg2ZDY2YmRiZTlkZTBiZDVlNThkYzRmZTAzYjZiMmMyNGJkOTg5MzIyYQ=="

def clean_vtt_line(line):
    """Clean a single VTT caption line"""
    line = re.sub(r'<[^>]+>', '', line)
    line = re.sub(r'</?[a-z].*?>', '', line)
    return line.strip()

def download_vtt_chunk(chunk_num):
    """Try to download a specific VTT chunk"""
    url = BASE_URL.format(chunk=chunk_num, signature=SIGNATURE)

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
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

        return text_lines, True
    except Exception:
        return [], False

def main():
    print("=" * 70)
    print("BRUTE FORCE VTT CHUNK DOWNLOADER")
    print("=" * 70)
    print("\n⚠ Attempting to download chunks 0-150 using a known signature")
    print("This may not work if signatures are chunk-specific or expired.\n")

    print("Trying to download chunks...\n")
    print("-" * 70)

    all_text = []
    successful_chunks = []
    failed_chunks = []

    for chunk_num in range(0, 151):
        print(f"  Chunk {chunk_num:3d}...", end=" ", flush=True)

        text_lines, success = download_vtt_chunk(chunk_num)

        if success and text_lines:
            all_text.extend(text_lines)
            successful_chunks.append(chunk_num)
            print("✓")
        else:
            failed_chunks.append(chunk_num)
            print("✗")

        time.sleep(0.05)  # Be nice to the server

    if not all_text:
        print("\n" + "=" * 70)
        print("✗ FAILED - No chunks downloaded successfully")
        print("=" * 70)
        print("\nThe signature is likely:")
        print("  - Chunk-specific (each chunk needs its own signature)")
        print("  - Expired (signatures have a time limit)")
        print("\nYou MUST scrub through the entire video and capture all VTT URLs.")
        return

    # Combine into single transcript
    full_transcript = '\n'.join(all_text)

    # Save to file
    output_file = 'rd_framework_brute_force_transcript.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print()
    print("=" * 70)
    print("✓ EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\n📄 File saved: {output_file}")
    print(f"📊 Chunks successful: {len(successful_chunks)}")
    print(f"📊 Chunks failed: {len(failed_chunks)}")
    print(f"📊 Total characters: {len(full_transcript):,}")
    print(f"📊 Total words: {len(full_transcript.split()):,}")
    print(f"📊 Total lines: {len(all_text):,}")
    print(f"\nSuccessful chunks: {successful_chunks[:20]}{'...' if len(successful_chunks) > 20 else ''}")
    print()
    print("=" * 70)
    print("Preview (first 1000 characters):")
    print("=" * 70)
    print(full_transcript[:1000])
    if len(full_transcript) > 1000:
        print("\n... (transcript continues)")
    print("=" * 70)

if __name__ == "__main__":
    main()
