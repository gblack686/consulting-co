"""
Upload a local client session folder to Google Drive.

Usage:
    python -m scripts.upload_session_to_drive <local_session_path> [--parent-name "GBAutomation Clients"]

Creates:
    GBAutomation Clients/
    └── {client-slug} — Session {YYYY-MM-DD}/
        ├── workspace/
        ├── session_output/
        └── diagrams/

Returns the Drive folder URL.
"""

import sys
import os
import mimetypes
from pathlib import Path
from googleapiclient.http import MediaFileUpload

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.google_client import drive_service


MIME_FOLDER = "application/vnd.google-apps.folder"


def get_or_create_folder(drive, name: str, parent_id: str = None) -> str:
    """Return folder ID, creating it if it doesn't exist."""
    q = f"name = '{name}' and mimeType = '{MIME_FOLDER}' and trashed = false"
    if parent_id:
        q += f" and '{parent_id}' in parents"

    results = drive.files().list(q=q, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {"name": name, "mimeType": MIME_FOLDER}
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = drive.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_file(drive, local_path: Path, parent_id: str) -> str:
    """Upload a single file to Drive, return file ID."""
    mime, _ = mimetypes.guess_type(str(local_path))
    if mime is None:
        mime = "text/plain"

    metadata = {"name": local_path.name, "parents": [parent_id]}
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=False)
    f = drive.files().create(body=metadata, media_body=media, fields="id").execute()
    return f["id"]


def upload_directory(drive, local_dir: Path, drive_parent_id: str) -> dict:
    """Recursively upload a directory tree. Returns {rel_path: file_id}."""
    uploaded = {}
    folder_cache = {local_dir: drive_parent_id}

    for item in sorted(local_dir.rglob("*")):
        if item.is_dir():
            rel_parent = item.parent
            parent_drive_id = folder_cache[rel_parent]
            fid = get_or_create_folder(drive, item.name, parent_drive_id)
            folder_cache[item] = fid
        else:
            rel_parent = item.parent
            parent_drive_id = folder_cache.get(rel_parent)
            if parent_drive_id is None:
                # Shouldn't happen with rglob sorted, but handle gracefully
                parent_drive_id = drive_parent_id
            fid = upload_file(drive, item, parent_drive_id)
            uploaded[str(item.relative_to(local_dir))] = fid
            print(f"  ✓ {item.relative_to(local_dir)}")

    return uploaded


def upload_session(local_session_path: str, parent_folder_name: str = "GBAutomation Clients",
                   client_name: str = None) -> str:
    """
    Upload a session folder to Drive under a per-client subfolder.
    Structure: parent / {client_name} / {session_name}
    Returns the URL of the created session folder.
    """
    local_path = Path(local_session_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Session folder not found: {local_session_path}")

    drive = drive_service()

    # Derive session folder name from slug
    slug = local_path.name  # e.g. 20260305-erica-creations
    parts = slug.split("-", 1)
    if len(parts) == 2:
        date_str = parts[0]
        slug_client = parts[1].replace("-", " ").title()
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        drive_folder_name = f"{slug_client} — Session {formatted_date}"
    else:
        drive_folder_name = slug

    # Try to read client name from client_profile.json if not provided
    if not client_name:
        profile_path = local_path / "session_output" / "client_profile.json"
        if profile_path.exists():
            import json
            with open(profile_path) as f:
                profile = json.load(f)
            client_name = profile.get("name", slug_client if len(parts) == 2 else slug)
        else:
            client_name = slug_client if len(parts) == 2 else slug

    print(f"\nUploading to Drive: {parent_folder_name} / {client_name} / {drive_folder_name}")

    # 1. Get or create root parent folder
    parent_id = get_or_create_folder(drive, parent_folder_name)

    # 2. Get or create client subfolder
    client_id = get_or_create_folder(drive, client_name, parent_id)

    # 3. Get or create session folder inside client folder
    session_id = get_or_create_folder(drive, drive_folder_name, client_id)

    # 3. Upload all files
    uploaded = upload_directory(drive, local_path, session_id)

    folder_url = f"https://drive.google.com/drive/folders/{session_id}"
    print(f"\n=== UPLOADED {len(uploaded)} files ===")
    print(f"Drive folder: {folder_url}")
    return folder_url


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload session folder to Google Drive")
    parser.add_argument("session_path", help="Local path to client session folder")
    parser.add_argument("--parent-name", default="GBAutomation Clients",
                        help="Name of parent Drive folder (default: GBAutomation Clients)")
    args = parser.parse_args()

    url = upload_session(args.session_path, args.parent_name)
    print(f"\nOpen in browser: {url}")
