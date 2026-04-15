"""
Fix Fish Group Drive folder structure.

Tasks:
1. Create missing session folders (2026-03-19, 2026-03-26, 2026-04-02, 2026-04-09)
   each with subfolders: deliverables/, diagrams/, session_output/
2. Move files from top-level deliverables/ into correct session deliverables/
3. Create Intelligence/ and Proposals/ folders at Fish Group root
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.google_client import drive_service

FISH_GROUP_FOLDER_ID = "1K6CIz8xFWRA8KkZgkCvZ3kQZa0dQJfPH"
TOP_LEVEL_DELIVERABLES_ID = "1fv8g6QsgDVSLsQgfzADGDlN26xc_AUn-"
TOP_LEVEL_DIAGRAMS_ID = "1yW-rRYpkRKnGJhoNv3xyXew81vlGUOLL"

SESSION_FOLDERS = [
    "Fish Group — Session 2026-03-19",
    "Fish Group — Session 2026-03-26",
    "Fish Group — Session 2026-04-02",
    "Fish Group — Session 2026-04-09",
]

SESSION_SUBFOLDERS = ["deliverables", "diagrams", "session_output"]

# Maps filename (as it appears in Drive) to destination session name
FILE_MOVE_MAP = {
    "research-2026-03-26.md": "Fish Group — Session 2026-03-26",
    "session-2-report-2026-03-12.md": "Fish Group — Session 2026-03-12",
    "my-second-brain-requirements.md": "Fish Group — Session 2026-04-02",
    "workflow-catalog.md": "Fish Group — Session 2026-03-12",
    "PACKAGE_SUMMARY.md": "Fish Group — Session 2026-03-05",
}

ROOT_FOLDERS_TO_CREATE = ["Intelligence", "Proposals"]


def get_or_create_folder(drive, name: str, parent_id: str) -> str:
    """Get existing folder by name under parent, or create it."""
    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    results = drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        print(f"  [exists] {name} (id: {files[0]['id']})")
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = drive.files().create(body=metadata, fields="id").execute()
    print(f"  [created] {name} (id: {folder['id']})")
    return folder["id"]


def list_files_in_folder(drive, folder_id: str) -> list[dict]:
    """List all non-folder files in a folder."""
    query = (
        f"'{folder_id}' in parents and trashed=false "
        f"and mimeType != 'application/vnd.google-apps.folder'"
    )
    results = drive.files().list(
        q=query,
        fields="files(id, name, mimeType, parents)",
        pageSize=100
    ).execute()
    return results.get("files", [])


def list_all_in_folder(drive, folder_id: str) -> list[dict]:
    """List everything (files + folders) in a folder."""
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive.files().list(
        q=query,
        fields="files(id, name, mimeType, parents)",
        pageSize=100
    ).execute()
    return results.get("files", [])


def move_file(drive, file_id: str, old_parent_id: str, new_parent_id: str, file_name: str):
    """Move a file from old_parent to new_parent."""
    drive.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields="id, parents"
    ).execute()
    print(f"  [moved] {file_name} -> {new_parent_id}")


def main():
    drive = drive_service()
    print("\n=== Fish Group Drive Restructure ===\n")

    # Step 1: Inventory existing session folders under Fish Group
    print("--- Inventorying existing Fish Group folders ---")
    all_fish_items = list_all_in_folder(drive, FISH_GROUP_FOLDER_ID)
    existing_folders = {
        item["name"]: item["id"]
        for item in all_fish_items
        if item["mimeType"] == "application/vnd.google-apps.folder"
    }
    print(f"Found {len(existing_folders)} existing folders:")
    for name, fid in existing_folders.items():
        print(f"  {name}: {fid}")

    # Step 2: Create missing session folders with subfolders
    print("\n--- Creating missing session folders ---")
    session_folder_ids = dict(existing_folders)  # start with existing

    for session_name in SESSION_FOLDERS:
        print(f"\n  Session: {session_name}")
        session_id = get_or_create_folder(drive, session_name, FISH_GROUP_FOLDER_ID)
        session_folder_ids[session_name] = session_id

        # Create subfolders
        for sub in SESSION_SUBFOLDERS:
            get_or_create_folder(drive, sub, session_id)

    # Also ensure existing session folders have all subfolders
    existing_session_names = [
        k for k in existing_folders.keys()
        if k.startswith("Fish Group — Session")
    ]
    print("\n--- Ensuring existing session folders have subfolders ---")
    for session_name in existing_session_names:
        session_id = existing_folders[session_name]
        print(f"\n  Session: {session_name}")
        for sub in SESSION_SUBFOLDERS:
            get_or_create_folder(drive, sub, session_id)

    # Step 3: Create Intelligence/ and Proposals/ at Fish Group root
    print("\n--- Creating root-level Intelligence/ and Proposals/ folders ---")
    for folder_name in ROOT_FOLDERS_TO_CREATE:
        get_or_create_folder(drive, folder_name, FISH_GROUP_FOLDER_ID)

    # Step 4: Move files from top-level deliverables/ to correct session deliverables/
    print("\n--- Moving files from top-level deliverables/ ---")
    top_level_files = list_files_in_folder(drive, TOP_LEVEL_DELIVERABLES_ID)
    print(f"Files in top-level deliverables/ ({len(top_level_files)}):")
    for f in top_level_files:
        print(f"  {f['name']} (id: {f['id']})")

    for f in top_level_files:
        fname = f["name"]
        if fname in FILE_MOVE_MAP:
            target_session = FILE_MOVE_MAP[fname]
            # Get the session folder ID
            target_session_id = session_folder_ids.get(target_session)
            if not target_session_id:
                # Try to find it from Drive
                target_session_id = get_or_create_folder(drive, target_session, FISH_GROUP_FOLDER_ID)
                session_folder_ids[target_session] = target_session_id
            # Get or create deliverables subfolder in that session
            target_deliverables_id = get_or_create_folder(drive, "deliverables", target_session_id)
            move_file(drive, f["id"], TOP_LEVEL_DELIVERABLES_ID, target_deliverables_id, fname)
        else:
            print(f"  [skip] {fname} — not in move map, leaving in place")

    # Step 5: Handle top-level diagrams/ folder
    print("\n--- Checking top-level diagrams/ folder ---")
    diagram_files = list_files_in_folder(drive, TOP_LEVEL_DIAGRAMS_ID)
    print(f"Files in top-level diagrams/ ({len(diagram_files)}):")
    for f in diagram_files:
        print(f"  {f['name']} (id: {f['id']}) — listed as duplicate, leaving in place")

    print("\n=== Done ===\n")
    print("Summary:")
    print(f"  Session folders created/verified: {len(SESSION_FOLDERS)}")
    print(f"  Root folders created: {ROOT_FOLDERS_TO_CREATE}")
    print(f"  Files moved: {sum(1 for f in top_level_files if f['name'] in FILE_MOVE_MAP)}")
    print(f"\nFish Group root: https://drive.google.com/drive/folders/{FISH_GROUP_FOLDER_ID}")


if __name__ == "__main__":
    main()
