"""Fetch and export a Google Doc transcript to plain text."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.google_client import drive_service

def fetch_transcript(file_id: str) -> str:
    drive = drive_service()
    content = drive.files().export(fileId=file_id, mimeType="text/plain").execute()
    return content.decode("utf-8")

if __name__ == "__main__":
    file_id = sys.argv[1]
    text = fetch_transcript(file_id)
    print(text)
