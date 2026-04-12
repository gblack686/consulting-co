"""
Sync Fish Group local session files to Google Drive.

Drive target structure (per client-folder-standard.md):
  GBAutomation Clients / Fish Group /
      Onboarding/
      Fish Group \u2014 Session {YYYY-MM-DD}/
          deliverables/
          diagrams/
          session_output/
      Intelligence/
      Proposals/
"""

import os
import sys
import mimetypes
from googleapiclient.http import MediaFileUpload

# Allow running as `python scripts/sync_fish_group.py` from consulting-admin/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import google_client, drive_manager

CLIENT_NAME = "Fish Group"

SESSION_DIR = (
    "C:/Users/gblac/OneDrive/Desktop/consulting-co"
    "/.claude/skills/consulting-intake/client-sessions/20260305-michael-fisch"
)

# (local_relative_path, session_date, drive_subfolder, drive_filename)
# session_date determines which "Fish Group \u2014 Session {date}/" folder the file goes into
FILES_TO_SYNC = [
    ("session_output/fish_group_deployment_report.pdf",  "2026-03-05", "deliverables", "fish_group_deployment_report.pdf"),
    ("PACKAGE_SUMMARY.md",                               "2026-03-05", "deliverables", "PACKAGE_SUMMARY.md"),
    ("diagrams/fish-group-architecture.png",             "2026-03-05", "diagrams",     "fish-group-architecture.png"),
    ("session_output/session-2-report-2026-03-12.md",    "2026-03-12", "deliverables", "session-2-report-2026-03-12.md"),
    ("session_output/workflow-catalog.md",               "2026-03-12", "deliverables", "workflow-catalog.md"),
    ("session_output/research-2026-03-26.md",            "2026-03-26", "deliverables", "research-2026-03-26.md"),
    ("session_output/my-second-brain-requirements.md",   "2026-04-02", "deliverables", "my-second-brain-requirements.md"),
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

    # Look for Fish Group or Michael Fisch
    client_folder_id = None
    for candidate_name in ["Fish Group", "Michael Fisch"]:
        qr = drive.files().list(
            q=(
                f"name='{candidate_name}' and mimeType='application/vnd.google-apps.folder'"
                f" and '{root_id}' in parents and trashed=false"
            ),
            fields="files(id, name)",
        ).execute()
        if qr.get("files"):
            client_folder_id = qr["files"][0]["id"]
            print(f"Found client folder: '{candidate_name}' ({drive_manager.get_folder_url(client_folder_id)})")
            break

    if not client_folder_id:
        print("No existing folder found — creating 'Fish Group'")
        client_folder_id = drive_manager.create_client_folder("Fish Group")
        print(f"Created: {drive_manager.get_folder_url(client_folder_id)}")

    print(f"\nExisting contents:")
    list_folder_contents(drive, client_folder_id)

    # Group files by session date to create/find session folders
    from collections import defaultdict
    by_session = defaultdict(list)
    for rel_path, session_date, subfolder, drive_name in FILES_TO_SYNC:
        by_session[session_date].append((rel_path, subfolder, drive_name))

    # Upload files into session-based folders
    print("\n=== Uploading files (session-based structure) ===")
    uploaded = []
    errors = []

    for session_date, files in sorted(by_session.items()):
        session_folder_name = f"{CLIENT_NAME} \u2014 Session {session_date}"
        print(f"\n  Session: {session_folder_name}")

        # Get or create session folder
        session_folder_id = drive_manager.get_or_create_folder(
            session_folder_name, parent_id=client_folder_id
        )

        # Cache subfolder IDs within this session folder
        subfolder_ids = {}

        for rel_path, subfolder, drive_name in files:
            # Get or create the subfolder (deliverables/, diagrams/, session_output/)
            if subfolder not in subfolder_ids:
                subfolder_ids[subfolder] = drive_manager.get_or_create_folder(
                    subfolder, parent_id=session_folder_id
                )

            local_path = os.path.join(SESSION_DIR, rel_path).replace("\\", "/")
            if not os.path.exists(local_path):
                errors.append((drive_name, f"LOCAL FILE NOT FOUND: {local_path}"))
                print(f"    SKIP  {drive_name}  (not found)")
                continue

            folder_id = subfolder_ids[subfolder]
            print(f"    Uploading {drive_name} -> {subfolder}/", end="", flush=True)
            try:
                url = upload_or_replace(drive, local_path, drive_name, folder_id)
                uploaded.append((session_date, subfolder, drive_name, url))
                print(f"  OK")
            except Exception as e:
                errors.append((drive_name, str(e)))
                print(f"  ERROR: {e}")

    # Summary
    print("\n=== Upload Summary ===")
    print(f"Client folder: {drive_manager.get_folder_url(client_folder_id)}")
    print(f"\nUploaded ({len(uploaded)}/{len(FILES_TO_SYNC)}):")
    for session_date, subfolder, name, url in uploaded:
        print(f"  Session {session_date}/{subfolder}/{name}")
        print(f"    {url}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    print("\n=== Final Drive Structure ===")
    list_folder_contents(drive, client_folder_id)


if __name__ == "__main__":
    main()
