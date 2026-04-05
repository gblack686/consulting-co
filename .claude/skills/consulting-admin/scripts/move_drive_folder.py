"""Move an existing Drive folder into a new parent (client subfolder)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.google_client import drive_service
from scripts.upload_session_to_drive import get_or_create_folder

MIME_FOLDER = "application/vnd.google-apps.folder"


def move_folder(folder_id: str, new_parent_id: str):
    drive = drive_service()
    # Get current parents
    f = drive.files().get(fileId=folder_id, fields="parents").execute()
    old_parents = ",".join(f.get("parents", []))
    drive.files().update(
        fileId=folder_id,
        addParents=new_parent_id,
        removeParents=old_parents,
        fields="id, parents"
    ).execute()
    print(f"Moved folder {folder_id} → parent {new_parent_id}")


if __name__ == "__main__":
    drive = drive_service()

    # 1. Get GBAutomation Clients folder
    root_id = get_or_create_folder(drive, "GBAutomation Clients")

    # 2. Create/get Erica Cruz client folder inside root
    client_id = get_or_create_folder(drive, "Erica Cruz", root_id)
    print(f"Client folder 'Erica Cruz': https://drive.google.com/drive/folders/{client_id}")

    # 3. Move existing session folder into client folder
    SESSION_FOLDER_ID = "1YZ2ckWOF6NSKK6WwgmrfTcxrxF01Rhbf"
    move_folder(SESSION_FOLDER_ID, client_id)

    print(f"\nDone. Session now at:")
    print(f"  GBAutomation Clients / Erica Cruz / Erica Creations — Session 2026-03-05")
    print(f"  https://drive.google.com/drive/folders/{SESSION_FOLDER_ID}")
