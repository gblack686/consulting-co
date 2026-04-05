"""
One-shot sync: uploads Fish Group / Michael Fisch local session files
to their Google Drive folder under GBAutomation Clients.

Drive target structure:
  GBAutomation Clients / Michael Fisch /
      deliverables/
          fish_group_deployment_report.pdf
          session-2-report-2026-03-12.md
          workflow-catalog.md
          my-second-brain-requirements.md
          research-2026-03-26.md
          PACKAGE_SUMMARY.md
      diagrams/
          fish-group-architecture.png
"""

import os
import sys
import mimetypes
from googleapiclient.http import MediaFileUpload

# Allow running as `python scripts/sync_fish_group.py` from consulting-admin/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import google_client, drive_manager

SESSION_DIR = (
    "C:/Users/gblac/OneDrive/Desktop/consulting-co"
    "/.claude/skills/consulting-intake/client-sessions/20260305-michael-fisch"
)

# (local_relative_path, drive_subfolder, drive_filename)
FILES_TO_SYNC = [
    ("session_output/fish_group_deployment_report.pdf",  "deliverables", "fish_group_deployment_report.pdf"),
    ("session_output/session-2-report-2026-03-12.md",    "deliverables", "session-2-report-2026-03-12.md"),
    ("session_output/workflow-catalog.md",               "deliverables", "workflow-catalog.md"),
    ("session_output/my-second-brain-requirements.md",   "deliverables", "my-second-brain-requirements.md"),
    ("session_output/research-2026-03-26.md",            "deliverables", "research-2026-03-26.md"),
    ("diagrams/fish-group-architecture.png",             "diagrams",     "fish-group-architecture.png"),
    ("PACKAGE_SUMMARY.md",                               "deliverables", "PACKAGE_SUMMARY.md"),
]

MIME_MAP = {
    ".pdf":  "application/pdf",
    ".md":   "text/markdown",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".txt":  "text/plain",
}


def get_mime(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return MIME_MAP.get(ext, "application/octet-stream")


def find_existing_files(drive, folder_id: str) -> dict:
    """Return {name: file_id} for all files in a Drive folder."""
    results = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)",
        pageSize=200,
    ).execute()
    return {f["name"]: f["id"] for f in results.get("files", [])}


def upload_or_replace(drive, local_path: str, filename: str, folder_id: str) -> str:
    """Upload file; if a file with the same name already exists, delete it first."""
    existing = find_existing_files(drive, folder_id)

    if filename in existing:
        print(f"    Replacing existing file: {filename}")
        drive.files().delete(fileId=existing[filename]).execute()

    mime = get_mime(filename)
    metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime, resumable=False)
    f = drive.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
    return f["webViewLink"]


def list_folder_contents(drive, folder_id: str, indent: int = 0) -> None:
    """Recursively list folder contents."""
    results = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType, webViewLink)",
        pageSize=200,
        orderBy="name",
    ).execute()
    prefix = "  " * indent
    for f in results.get("files", []):
        kind = "(folder)" if f["mimeType"] == "application/vnd.google-apps.folder" else ""
        print(f"{prefix}  - {f['name']} {kind}")
        if f["mimeType"] == "application/vnd.google-apps.folder":
            list_folder_contents(drive, f["id"], indent + 1)


def main():
    drive = google_client.drive_service()

    print("=== Checking existing Drive structure ===")
    root_id = drive_manager.get_root_folder_id()
    print(f"Root folder (GBAutomation Clients): {drive_manager.get_folder_url(root_id)}")

    # Look for Michael Fisch or Fish Group
    client_folder_id = None
    for candidate_name in ["Michael Fisch", "Fish Group"]:
        qr = drive.files().list(
            q=(
                f"name='{candidate_name}' and mimeType='application/vnd.google-apps.folder'"
                f" and '{root_id}' in parents and trashed=false"
            ),
            fields="files(id, name)",
        ).execute()
        if qr.get("files"):
            client_folder_id = qr["files"][0]["id"]
            client_name_used = candidate_name
            print(f"Found existing client folder: '{candidate_name}' ({drive_manager.get_folder_url(client_folder_id)})")
            break

    if not client_folder_id:
        print("No existing folder found — creating 'Michael Fisch'")
        client_folder_id = drive_manager.create_client_folder("Michael Fisch")
        client_name_used = "Michael Fisch"
        print(f"Created: {drive_manager.get_folder_url(client_folder_id)}")

    print(f"\nExisting contents of '{client_name_used}':")
    list_folder_contents(drive, client_folder_id)

    # Ensure subfolders exist
    print("\n=== Creating/verifying subfolders ===")
    subfolder_ids = {}
    for subfolder_name in ["deliverables", "diagrams"]:
        fid = drive_manager.get_or_create_folder(subfolder_name, parent_id=client_folder_id)
        subfolder_ids[subfolder_name] = fid
        print(f"  {subfolder_name}/  -> {drive_manager.get_folder_url(fid)}")

    # Upload files
    print("\n=== Uploading files ===")
    uploaded = []
    errors = []

    for rel_path, subfolder, drive_name in FILES_TO_SYNC:
        local_path = os.path.join(SESSION_DIR, rel_path).replace("\\", "/")
        if not os.path.exists(local_path):
            errors.append((drive_name, f"LOCAL FILE NOT FOUND: {local_path}"))
            print(f"  SKIP  {drive_name}  (file not found: {local_path})")
            continue

        folder_id = subfolder_ids[subfolder]
        print(f"  Uploading {drive_name} -> {subfolder}/", end="", flush=True)
        try:
            url = upload_or_replace(drive, local_path, drive_name, folder_id)
            uploaded.append((subfolder, drive_name, url))
            print(f"  OK")
        except Exception as e:
            errors.append((drive_name, str(e)))
            print(f"  ERROR: {e}")

    # Summary
    print("\n=== Upload Summary ===")
    print(f"Client folder: {drive_manager.get_folder_url(client_folder_id)}")
    print(f"\nUploaded ({len(uploaded)}/{len(FILES_TO_SYNC)}):")
    for subfolder, name, url in uploaded:
        print(f"  {subfolder}/{name}")
        print(f"    {url}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    print("\n=== Final Drive Structure ===")
    list_folder_contents(drive, client_folder_id)


if __name__ == "__main__":
    main()
