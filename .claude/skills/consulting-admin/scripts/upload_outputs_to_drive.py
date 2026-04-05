"""Upload the agency chart and deployment report to the Michael Fisch Drive folder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.google_client import drive_service
from scripts.upload_session_to_drive import get_or_create_folder, upload_file

OUTPUT = Path(__file__).parent.parent / "output"

def main():
    drive = drive_service()

    # Navigate to: GBAutomation Clients / Michael Fisch / Michael Fisch — Session 2026-03-05
    root_id = get_or_create_folder(drive, "GBAutomation Clients")
    client_id = get_or_create_folder(drive, "Michael Fisch", root_id)
    session_id = get_or_create_folder(drive, "Michael Fisch — Session 2026-03-05", client_id)

    # Create a "deliverables" subfolder
    deliverables_id = get_or_create_folder(drive, "deliverables", session_id)

    files = [
        OUTPUT / "agency_comparison.png",
        OUTPUT / "fish_group_deployment_report.html",
    ]

    for f in files:
        fid = upload_file(drive, f, deliverables_id)
        print(f"  ✓ {f.name}")

    url = f"https://drive.google.com/drive/folders/{deliverables_id}"
    print(f"\nDone. Deliverables folder: {url}")

if __name__ == "__main__":
    main()
