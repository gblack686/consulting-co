"""
Add report link columns to the existing Social Media Recon Tracker sheet.

New columns (I-L):
  I: LinkedIn Report    — public Drive link to LinkedIn research PPTX
  J: Instagram Report   — public Drive link to Instagram/personal-intel PPTX
  K: Facebook Report    — public Drive link to Facebook research PPTX
  L: Drive Folder       — link to client's research folder in GBAutomation Clients

Also updates Patrick Bauer row with his existing LinkedIn research deck link.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "consulting-admin"))

from scripts import google_client, drive_manager

SHEET_ID = "1QnCKwahlaUV-gi31d4NZmKk7nxrtkJQA4rOs8paH-pA"

# GBAutomation brand colors
TERRACOTTA = {"red": 0.851, "green": 0.467, "blue": 0.341}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
CREAM = {"red": 0.953, "green": 0.945, "blue": 0.906}

NEW_HEADERS = ["LinkedIn Report", "Instagram Report", "Facebook Report", "Drive Folder"]


def get_sheet_gid(sheets_svc, spreadsheet_id: str) -> int:
    """Get the sheetId (gid) of the first sheet."""
    meta = sheets_svc.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets/properties"
    ).execute()
    return meta["sheets"][0]["properties"]["sheetId"]


def find_or_create_research_folder(client_name: str) -> tuple[str, str]:
    """
    Ensure GBAutomation Clients / {client_name} / Research exists.
    Returns (research_folder_id, research_folder_url).
    """
    client_folder_id = drive_manager.create_client_folder(client_name)
    research_folder_id = drive_manager.get_or_create_folder("Research", parent_id=client_folder_id)
    return research_folder_id, drive_manager.get_folder_url(research_folder_id)


def make_file_public(file_id: str):
    """Make a Drive file publicly readable via link."""
    drive = google_client.drive_service()
    drive.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()


def upload_and_share(local_path: str, filename: str, folder_id: str, mime_type: str) -> str:
    """Upload file to Drive folder, make public, return view link."""
    drive = google_client.drive_service()
    from googleapiclient.http import MediaFileUpload

    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=False)
    f = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = f["id"]

    # Make publicly readable
    make_file_public(file_id)

    return f"https://drive.google.com/file/d/{file_id}/view"


def main():
    sheets = google_client.sheets_service()
    sheet_gid = get_sheet_gid(sheets, SHEET_ID)

    # --- Step 0: Expand grid if needed ---
    meta = sheets.spreadsheets().get(
        spreadsheetId=SHEET_ID,
        fields="sheets/properties"
    ).execute()
    current_cols = meta["sheets"][0]["properties"]["gridProperties"]["columnCount"]
    if current_cols < 12:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": [{
                "appendDimension": {
                    "sheetId": sheet_gid,
                    "dimension": "COLUMNS",
                    "length": 12 - current_cols,
                }
            }]},
        ).execute()
        print(f"Expanded grid from {current_cols} to 12 columns.")
    else:
        print(f"Grid already has {current_cols} columns — no expansion needed.")

    # --- Step 1: Write new headers in I1:L1 ---
    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="'Recon Queue'!I1:L1",
        valueInputOption="RAW",
        body={"values": [NEW_HEADERS]},
    ).execute()
    print("Added headers: " + ", ".join(NEW_HEADERS))

    # --- Step 2: Format new header cells to match existing ---
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_gid,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 8,   # col I
                    "endColumnIndex": 12,     # col L
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": TERRACOTTA,
                        "textFormat": {
                            "bold": True,
                            "fontSize": 11,
                            "foregroundColor": WHITE,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        # Widen report columns
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_gid,
                    "dimension": "COLUMNS",
                    "startIndex": 8,   # I
                    "endIndex": 12,    # L
                },
                "properties": {"pixelSize": 280},
                "fields": "pixelSize",
            }
        },
        # Note: banding already applied from create_recon_sheet — skip addBanding
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests},
    ).execute()
    print("Formatted new columns.")

    # --- Step 3: Upload pbauer's existing research deck & populate his row ---
    pbauer_deck = "C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/context/clients/patrick-bauer/Patrick Bauer - Client Research.pptx"

    if os.path.exists(pbauer_deck):
        print("\nUploading Patrick Bauer LinkedIn deck to Drive...")
        research_folder_id, research_folder_url = find_or_create_research_folder("Patrick Bauer")

        deck_url = upload_and_share(
            pbauer_deck,
            "Patrick Bauer - LinkedIn Research.pptx",
            research_folder_id,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        print(f"  Deck: {deck_url}")
        print(f"  Folder: {research_folder_url}")

        # Write links to pbauer row (row 2 = first data row)
        sheets.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range="'Recon Queue'!I2:L2",
            valueInputOption="RAW",
            body={"values": [[deck_url, "", "", research_folder_url]]},
        ).execute()
        print("  Updated pbauer row with report links.")
    else:
        print(f"\nWARN: pbauer deck not found at {pbauer_deck}")

    # --- Step 4: Create Garrett Shuster research folder ---
    print("\nCreating Garrett Shuster research folder...")
    gs_folder_id, gs_folder_url = find_or_create_research_folder("Garrett Shuster")
    print(f"  Folder: {gs_folder_url}")

    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="'Recon Queue'!L3",
        valueInputOption="RAW",
        body={"values": [[gs_folder_url]]},
    ).execute()
    print("  Updated Garrett Shuster row with folder link.")

    print("\nDone. Sheet updated with report columns.")
    print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")


if __name__ == "__main__":
    main()
