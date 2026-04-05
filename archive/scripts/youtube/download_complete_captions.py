"""
Download complete transcript from m3u8 manifest
"""

import urllib.request
import re
from urllib.parse import urljoin

MANIFEST_URL = "https://manifest-oci-us-ashburn-1-vop1.edgemv.mux.com/9opMNJdmqI161t3T02hEKij01idyGsrhdM1NPsejItVLSPHP86vX5TBpfdFXP6yGzqTsEFQEQ4tdL200hSD01aooXCEuL37IRg02mX00N1WyTze9A/rendition.m3u8?cdn=edgemv&expires=1764057600&skid=edgemv-default-1&signature=NjkyNTU4ZWJfNTkzOWNhMjVjOGE3MTkxYjVmYmI5ZTE4NzUwZTAzZjBjNzcyMTBhZDA1OWI5MzE4M2NhMDllOWRjOTdkOWI0Mg==&vsid=lFIfFh7Wm1KGc4c001Rse7lD9YzofwiD7Fcz4x80200FsWkEG2SEkEoj802bX2nbpcOTq3ug6ovNPv00"

def download_manifest():
    """Download the m3u8 manifest"""
    print("Downloading manifest...")
    try:
        with urllib.request.urlopen(MANIFEST_URL, timeout=30) as response:
            content = response.read().decode('utf-8')
        print(f"✓ Manifest downloaded ({len(content)} bytes)")
        return content
    except Exception as e:
        print(f"✗ Error downloading manifest: {e}")
        return None

def parse_manifest_for_subtitle_url(manifest_content):
    """Parse m3u8 to find subtitle playlist URL"""
    lines = manifest_content.split('\n')

    # Look for subtitle/caption media tags
    for i, line in enumerate(lines):
        if 'TYPE=SUBTITLES' in line or 'TYPE=CAPTIONS' in line or 'subtitle' in line.lower():
            print(f"Found subtitle reference: {line[:100]}...")
            # The URI should be in this line or the next
            uri_match = re.search(r'URI="([^"]+)"', line)
            if uri_match:
                return uri_match.group(1)
            # Sometimes it's on the next line
            if i + 1 < len(lines):
                uri_match = re.search(r'URI="([^"]+)"', lines[i + 1])
                if uri_match:
                    return uri_match.group(1)

    return None

def download_subtitle_playlist(subtitle_url):
    """Download the subtitle-specific playlist"""
    print(f"\nDownloading subtitle playlist...")
    print(f"URL: {subtitle_url[:100]}...")
    try:
        with urllib.request.urlopen(subtitle_url, timeout=30) as response:
            content = response.read().decode('utf-8')
        print(f"✓ Subtitle playlist downloaded ({len(content)} bytes)")
        return content, subtitle_url
    except Exception as e:
        print(f"✗ Error downloading subtitle playlist: {e}")
        return None, subtitle_url

def parse_subtitle_playlist(playlist_content, base_url):
    """Parse subtitle playlist to get all VTT chunk URLs"""
    lines = playlist_content.split('\n')
    vtt_urls = []

    # Get base URL directory
    base_dir = '/'.join(base_url.split('/')[:-1]) + '/'

    for line in lines:
        line = line.strip()
        # Look for .vtt files
        if line.endswith('.vtt') or '.vtt?' in line:
            # Construct full URL
            if line.startswith('http'):
                vtt_urls.append(line)
            else:
                # Relative URL - join with base
                full_url = urljoin(base_dir, line)
                vtt_urls.append(full_url)

    return vtt_urls

def extract_chunk_number(url):
    """Extract chunk number from URL"""
    match = re.search(r'/(\d+)\.vtt', url)
    return int(match.group(1)) if match else 999999

def clean_vtt_line(line):
    """Clean a single VTT caption line"""
    line = re.sub(r'<[^>]+>', '', line)
    line = re.sub(r'</?[a-z].*?>', '', line)
    return line.strip()

def download_and_parse_vtt(url, chunk_num):
    """Download VTT file and extract text content"""
    try:
        print(f"  Chunk {chunk_num:3d}...", end=" ")
        with urllib.request.urlopen(url, timeout=30) as response:
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

        print("✓")
        return text_lines
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def main():
    print("=" * 70)
    print("COMPLETE TRANSCRIPT EXTRACTOR FROM M3U8 MANIFEST")
    print("=" * 70)
    print()

    # Step 1: Download manifest
    manifest = download_manifest()
    if not manifest:
        print("\n✗ Failed to download manifest")
        return

    # Debug: Save manifest to file
    with open('manifest_debug.txt', 'w', encoding='utf-8') as f:
        f.write(manifest)
    print("(Saved manifest to manifest_debug.txt for inspection)")

    # Step 2: Parse manifest for subtitle URL
    subtitle_url = parse_manifest_for_subtitle_url(manifest)

    if not subtitle_url:
        print("\n⚠ No subtitle URL found in manifest")
        print("The manifest might not contain subtitle references.")
        print("Looking for any .vtt references in the manifest...")

        # Try to find any VTT references
        vtt_matches = re.findall(r'https?://[^\s"<>]+\.vtt[^\s"<>]*', manifest)
        if vtt_matches:
            print(f"Found {len(vtt_matches)} VTT URLs directly in manifest!")
            vtt_urls = vtt_matches
        else:
            print("\n✗ No VTT URLs found. This might be a video-only manifest.")
            print("You may need to find the subtitle track manifest separately.")
            return
    else:
        # Step 3: Download subtitle playlist
        subtitle_playlist, base_url = download_subtitle_playlist(subtitle_url)
        if not subtitle_playlist:
            print("\n✗ Failed to download subtitle playlist")
            return

        # Debug: Save subtitle playlist
        with open('subtitle_playlist_debug.txt', 'w', encoding='utf-8') as f:
            f.write(subtitle_playlist)
        print("(Saved subtitle playlist to subtitle_playlist_debug.txt)")

        # Step 4: Parse subtitle playlist for VTT URLs
        vtt_urls = parse_subtitle_playlist(subtitle_playlist, base_url)

    if not vtt_urls:
        print("\n✗ No VTT URLs found in subtitle playlist")
        return

    print(f"\n✓ Found {len(vtt_urls)} VTT chunks!")

    # Sort by chunk number
    sorted_urls = sorted(vtt_urls, key=extract_chunk_number)

    print(f"\nDownloading and parsing {len(sorted_urls)} VTT files:")
    print("-" * 70)

    all_text = []
    for url in sorted_urls:
        chunk_num = extract_chunk_number(url)
        text_lines = download_and_parse_vtt(url, chunk_num)
        all_text.extend(text_lines)

    # Combine into single transcript
    full_transcript = '\n'.join(all_text)

    # Save to file
    output_file = 'rd_framework_complete_transcript.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print()
    print("=" * 70)
    print("✓ COMPLETE TRANSCRIPT EXTRACTION FINISHED!")
    print("=" * 70)
    print(f"\n📄 File saved: {output_file}")
    print(f"📊 Total characters: {len(full_transcript):,}")
    print(f"📊 Total words: {len(full_transcript.split()):,}")
    print(f"📊 Total lines: {len(all_text):,}")
    print(f"📊 Total chunks: {len(sorted_urls)}")
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
