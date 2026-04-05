"""
Download all VTT chunks by trying sequential chunk numbers
Based on the URL pattern from the provided samples
"""

import urllib.request
import re
import time

# Base URL pattern extracted from the samples
BASE_URL = "https://chunk-oci-us-ashburn-1-vop1.edgemv.mux.com/v1/subtitle/VNJ00IGlgtbd2RkIFGJz61Py00STwBFMKe01WfKrktkVBv744jr3U4ui02MKIpaLKVlywAX55Py8tyiCvzZE3LqI02w/{chunk}.vtt?skid=edgemv-default-1&signature={signature}"

# Known working signatures (from your samples)
SIGNATURES = {
    4: "NjkyNTYyMDBfNmY2OTlhMTc0NTUwODMyODEyNDI4NTJiMTQxYTBiMmNhY2IzNjcwYjA5MGM3ZmRkOTM3ODViYWQxMDQ5OTIxNA==",
    5: "NjkyNTYyMDBfYzdiMzVlZTQ2MDc0ZDlhYzJkOTQ2YjIwNTdhNGQ3MWQ2MWNhMjA4NTkxY2EwY2JjZjJkMGZjN2ZiNGY4NmViZQ==",
    # ... etc
}

def clean_vtt_line(line):
    """Clean a single VTT caption line"""
    line = re.sub(r'<[^>]+>', '', line)
    line = re.sub(r'</?[a-z].*?>', '', line)
    return line.strip()

def download_vtt_chunk(chunk_num, signature):
    """Try to download a specific VTT chunk"""
    url = BASE_URL.format(chunk=chunk_num, signature=signature)

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

        return text_lines, True
    except Exception as e:
        return [], False

def main():
    print("=" * 70)
    print("COMPLETE VTT TRANSCRIPT DOWNLOADER")
    print("=" * 70)
    print("\n⚠ Note: Signatures may be time-limited or chunk-specific.")
    print("This script will try to download chunks using known signatures.\n")

    # Load all the URLs you provided
    known_urls = [
        ("4", "NjkyNTYyMDBfNmY2OTlhMTc0NTUwODMyODEyNDI4NTJiMTQxYTBiMmNhY2IzNjcwYjA5MGM3ZmRkOTM3ODViYWQxMDQ5OTIxNA=="),
        ("5", "NjkyNTYyMDBfYzdiMzVlZTQ2MDc0ZDlhYzJkOTQ2YjIwNTdhNGQ3MWQ2MWNhMjA4NTkxY2EwY2JjZjJkMGZjN2ZiNGY4NmViZQ=="),
        ("6", "NjkyNTYyMDBfODZiYTExYTljMGY2Zjc5ZTE5YmExMDU3NGJkOTk5MzM2YjA4MWZiNjZjYzJkNjJlM2RmMTJmNTlhNzQ2YjI5OA=="),
        ("7", "NjkyNTYyMDBfOWRhZGJkODdlZGNkYWU3NDk4YzM2NjNjZDk3MWFhYzBmZjkzYzkwMTUxOWNkYmI5YjNmMWQzZjQxNmEzOWQ2OA=="),
        ("8", "NjkyNTYyMDBfMWI2MzI0ZmY1NjQxZGE4NGU0OGI1ZmEzYjJmN2Y2M2M1OWY1NGUwYmNlYWJkNmI0MjIyMzViODA2YjUzNzEzOQ=="),
        ("9", "NjkyNTYyMDBfMGUzYjllMTlkYzdlNjU2NTk1MGIzMGVhMzBkYWIwNzRiYjIyYTAxNmE1ODY1ZDVlOWMxZTM3ZDgyZDI3MjMxNw=="),
        ("10", "NjkyNTYyMDBfYTc5N2JhMjY1NzA5NDIxZDUxY2JiZTY4MmFlYTBmNmI1NWU1YWQ1MjE4ZTNkZWU5ZTA3YTUxNWIxOWJlM2ExYg=="),
        ("11", "NjkyNTYyMDBfYjRkMmRkMWU1YTQ2NWI4NDYxMjRiYTJiNDRkMTk2NGY3M2IyNzg5M2EzNmVlOWJiNjY1N2I0ODZkMTEyYzEzNQ=="),
        ("12", "NjkyNTYyMDBfNGMwOWIyYjRhMzQ3MjYwZjdjYWVhNTQ2ODc0Y2MyNjAwYjQ2NGM3NDA2NGQ0ZTMzMDU5Zjk4YjUyMDBiZTZmNQ=="),
        ("13", "NjkyNTYyMDBfYWU0MTY2M2VjOGRhZDk0ZGE3MDFmNDA2ODMzMzY1OTFjN2U4MzZiMDNmM2Y5NDM2NTcxMjc0ODNhYWM0Mzk0NA=="),
        ("14", "NjkyNTYyMDBfYjU3ZmFlZGZmZmIzMGQ4MWQwYTU2MWVhOTViODc0N2FjM2FkMTMwMDI4NzgzYTY5ZTJkZmMyODYyMWZkOGRkMg=="),
        ("15", "NjkyNTYyMDBfZjc5ZDIyOTAxMTQxZmE0MmRiZjAyMzFlZDE4OTA3MjlmZjQ0NmU4MmExOTE3Zjg1ZDA4MWRjZDk2ZmE3ZWZiMw=="),
        ("16", "NjkyNTYyMDBfMGIyM2QwOTY1YzdmOTFjMmM4NjdkYjg4ZjM4ZjliZGMxYTJkZjQxNGE2ZmNjOGNmY2NlNzc0ZTk5NDFkODAyNQ=="),
        ("17", "NjkyNTYyMDBfZmUxODI5ZTgxMDBjYzdlZjdiMjVhYWU1YzViM2UxMWM5N2E3YzE2ZTVlZDU5NjA4ODU0MmI0ZDhkYTlkMThhMw=="),
        ("64", "NjkyNTYyMDBfN2JkZTc2N2ZjYWEzMzcyNmQ1ZTk0NjJhZjJkMmEyMTY5ZWY3MjVlNmM1YTQ3NTJmZDdkMGY4YzAzOTJlNzRiYw=="),
        ("65", "NjkyNTYyMDBfYjRkOTMzMzhjNDFkMjU0ZWI3NTVmMDk4MzJkNDJmYjY3MzlkZjg2MzkyMzQzODM0MmMyYzk5YzFiNTNmZTE4OQ=="),
        ("66", "NjkyNTYyMDBfNWU0YmRjNjNlYTA3NjhjMTYyNzU2M2M3MTI1NmI5Y2VjNmI0ZTk0ODYzYWMzNTA5Y2E0NGEyMjViNzAwNDdkZg=="),
        ("67", "NjkyNTYyMDBfZTBkZjcxMWFlMDliMmYyYWFiMGU5ZjgwY2JiYWM5MTgyMzVjMDgwNWVmMDM4OTUwMmU5OWQzYzFmNjlmNTg5Mw=="),
        ("68", "NjkyNTYyMDBfYTZlZDM1OGNiODRiZGJhZGYwMzg2NmM3NjNiNjk1ZDY3OTM3MmEyNzVkZGM3MzgwN2FhYjdlMDEzYzU4ZDI2NQ=="),
        ("69", "NjkyNTYyMDBfYTY3ZDRiODQ4MzM3YzMzYzgyMjJkZTFlMGI4MmIxNGIzODY0NDJmZjJmOWRkOTdhNjFhZDg2ZWEzMTg0MTIwMQ=="),
        ("70", "NjkyNTYyMDBfMTA4NzlkMTI4ZWNjYmMzMDg2ZWI4MmY5NTEwNjYwNjllOGQzMjczNDdiNWFiZGQ1OTJkZTAyZjcyMDk1N2ZkZQ=="),
        ("71", "NjkyNTYyMDBfZTlhMGVjNTNiY2JhYjMzOTI3MDkyM2JlYWNiOGQ4NWE1YTdjOTI0MmRkMGExZTE5NWNmZmIxNGY5YzRiYTJhZQ=="),
        ("72", "NjkyNTYyMDBfZDE5ZjA0YTdkMjYwNjIxOWUyODRmNWFkZTNmMmRiM2YyYzljMjhhZDJhYzBhMDJmYzc2YWY0MGVlMWE3MTYzNw=="),
        ("127", "NjkyNTYyMDBfM2Y0ZmIzMTQ0YWVjMTI0YTAxMmM1Yzc1NDIwOGI4YWI4ZmVkOGMyZWRkNTVjNDQ4YjM3NWM3Mjk5MTQyZTUwMg=="),
        ("128", "NjkyNTYyMDBfM2NkZWE5NmY5MjU4ZGE2YWIxMzQwYTU4YjhiMzc2MzY3ODVmYjdiNTEyNGIwMGJmMjhlYTExZWE2MWZkZmI2Yg=="),
        ("129", "NjkyNTYyMDBfODQ4ZTg1YTI1YjA4MjEzYjFhOTZkMThkMmUzYmEzYTFiZDU5YTU0YzZlOWMyMDUzMTBlOWUzNzJjOWNhNDIyNg=="),
        ("130", "NjkyNTYyMDBfYTZiYzI3YWUzMjlkM2FkYmZiYjVmNmYyOTBjNzkzZTQ4ZWU4ZTRiNWU0NjE0Mjk5ODVhNGEyYzQwOGU0ZTk3ZQ=="),
        ("131", "NjkyNTYyMDBfYzM1NjYwZmJhYmQ1Y2QwY2RiMDE2MzhmNzQwODJjZDdjMjZmZTVkODVmN2U2MGVjZGIyN2VjMDI1NjI1YzVjZg=="),
        ("132", "NjkyNTYyMDBfNWI0N2U4NzcwZjBkZTMyOTIzZTUxNDhhNWE2MzFkMWQxOGE5ZmUzOGIwMDk1OTMwY2M3ZmM5ZjY4ZjU3NWQxNw=="),
        ("133", "NjkyNTYyMDBfNjE0N2M2YTk1NWQ5NmJhMTg1YmM2OTQ1OTU1MjE0MjRjM2E1YTVlZDE3ZWJjMzVlNzRhMGEzOWZiZWM2MTU2NQ=="),
        ("134", "NjkyNTYyMDBfNDk0NTI4YzA4MTk0ZmZiMzdkYzUwMjIwZjE4YjQ1YTllMGJhZDU3YTI4YjA3ZWFhMzMwOTM4MDZmZmUzODA3Zg=="),
        ("135", "NjkyNTYyMDBfYThkYzA3OGYzMmI2OTc4ZTlhMjIyN2ExYWFhOWI2ODg4NDc5ZWZlYmNiODVlNzAxOTk0YzhiZWJjNjE3NDE5OQ=="),
        ("136", "NjkyNTYyMDBfNjczYjY0NzViZDI2ZjYyZjMxODEyZmI0ZWYxNGU4ZWFiNzkwZWY0OTQ2NWE1ZDg3ZWU0Zjg3MjE1MDAwYTFhOA=="),
        ("141", "NjkyNTYyMDBfNWM3ZDYyMjEzMmM1N2Q3N2QyMTMxNGYwZDg0ZjYzZDM3ZTZiNmY5NjA5YWUxMDE1NzY3YjdhOGJlMWJjNGE5Yg=="),
        ("142", "NjkyNTYyMDBfNzIzNGU2N2Q0ZWUzZjMwNjQ1MDgwM2UwNmU2YmY3OGU0MDc2ZjE4ZDhmZDYwN2E5YTA0NWJkYzhmZDNjZjU3Mw=="),
        ("143", "NjkyNTYyMDBfZjI4NDcyMDY0NjdhMGQ4MmVmZGUxZjc5NDk3NWQ2ODRjZjRiZWE3Yjk2ZGU0MDBmZGY2ZjU3NTJhMTk4ZjQ0Ng=="),
        ("144", "NjkyNTYyMDBfYWZjMGM3MmJhZTY2MWNiNjU2OGM3Mjg2ZDY2YmRiZTlkZTBiZDVlNThkYzRmZTAzYjZiMmMyNGJkOTg5MzIyYQ=="),
    ]

    print(f"Found {len(known_urls)} known VTT chunks")
    print("Downloading chunks in order...\n")
    print("-" * 70)

    all_text = []
    successful = 0
    failed = 0

    for chunk_str, signature in sorted(known_urls, key=lambda x: int(x[0])):
        chunk_num = int(chunk_str)
        print(f"  Chunk {chunk_num:3d}...", end=" ", flush=True)

        text_lines, success = download_vtt_chunk(chunk_num, signature)

        if success:
            all_text.extend(text_lines)
            successful += 1
            print("✓")
        else:
            failed += 1
            print("✗")

        time.sleep(0.1)  # Be polite to the server

    # Combine into single transcript
    full_transcript = '\n'.join(all_text)

    # Save to file
    output_file = 'rd_framework_complete_transcript.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print()
    print("=" * 70)
    print("✓ TRANSCRIPT EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\n📄 File saved: {output_file}")
    print(f"📊 Chunks successful: {successful}")
    print(f"📊 Chunks failed: {failed}")
    print(f"📊 Total characters: {len(full_transcript):,}")
    print(f"📊 Total words: {len(full_transcript.split()):,}")
    print(f"📊 Total lines: {len(all_text):,}")
    print()
    print("⚠ WARNING: This is only a PARTIAL transcript from the chunks you captured.")
    print("To get the COMPLETE transcript, you need to play through the entire video")
    print("and capture ALL VTT URLs from the Network tab.")
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
