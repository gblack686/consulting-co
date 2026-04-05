"""
Convert VTT/SRT caption files to clean text transcript
Usage: python convert_vtt_to_text.py <caption_file_or_url>
"""

import re
import sys
import urllib.request

def clean_vtt_content(content):
    """Clean VTT file content to plain text"""
    lines = content.split('\n')
    transcript = []

    for line in lines:
        line = line.strip()

        # Skip WEBVTT header
        if line.startswith('WEBVTT'):
            continue

        # Skip timestamp lines
        if '-->' in line:
            continue

        # Skip numeric cue identifiers
        if line.isdigit():
            continue

        # Skip empty lines
        if not line:
            continue

        # Skip style/NOTE lines
        if line.startswith(('STYLE', 'NOTE', 'Kind:', 'Language:')):
            continue

        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)

        # Remove VTT styling tags like <c>, <v>, etc.
        line = re.sub(r'</?[a-z].*?>', '', line)

        # Add to transcript
        transcript.append(line)

    return '\n'.join(transcript)

def clean_srt_content(content):
    """Clean SRT file content to plain text"""
    lines = content.split('\n')
    transcript = []

    skip_next = False
    for line in lines:
        line = line.strip()

        # Skip sequence numbers
        if line.isdigit():
            skip_next = True
            continue

        # Skip timestamp lines
        if '-->' in line:
            continue

        # Skip empty lines
        if not line:
            skip_next = False
            continue

        if not skip_next:
            # Remove HTML tags
            line = re.sub(r'<[^>]+>', '', line)
            transcript.append(line)

    return '\n'.join(transcript)

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_vtt_to_text.py <file_path_or_url>")
        print("\nExamples:")
        print("  python convert_vtt_to_text.py captions.vtt")
        print("  python convert_vtt_to_text.py https://example.com/video/captions.vtt")
        sys.exit(1)

    source = sys.argv[1]

    # Check if it's a URL
    if source.startswith('http://') or source.startswith('https://'):
        print(f"Downloading from URL: {source}")
        try:
            with urllib.request.urlopen(source) as response:
                content = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error downloading: {e}")
            sys.exit(1)
    else:
        # It's a local file
        print(f"Reading file: {source}")
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    # Detect format and clean
    if 'WEBVTT' in content or source.endswith('.vtt'):
        print("Detected VTT format")
        clean_text = clean_vtt_content(content)
    elif source.endswith('.srt') or '-->' in content[:200]:
        print("Detected SRT format")
        clean_text = clean_srt_content(content)
    else:
        print("Unknown format, attempting VTT parsing...")
        clean_text = clean_vtt_content(content)

    # Save output
    output_file = 'transcript_clean.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(clean_text)

    print(f"\n✓ Transcript saved to: {output_file}")
    print(f"✓ Character count: {len(clean_text)}")
    print(f"✓ Word count: {len(clean_text.split())}")
    print("\n--- Preview (first 500 chars) ---")
    print(clean_text[:500] + "..." if len(clean_text) > 500 else clean_text)

if __name__ == "__main__":
    main()
