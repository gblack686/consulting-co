"""
Create the Social Media Recon Tracker Google Sheet.

Columns: Client Name | Slug | Instagram | LinkedIn | Facebook | Status | Last Updated | Notes
Pre-populates with Patrick Bauer row.

The sheet lives in GBAutomation Clients root folder.
A poller script (poll_recon_sheet.py) checks for new/updated handles
and fires off research jobs to Sebastian on the Mac Mini.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "consulting-admin"))

from scripts import google_client

# GBAutomation brand colors
CREAM = {"red": 0.953, "green": 0.945, "blue": 0.906}       # #F3F1E7
TERRACOTTA = {"red": 0.851, "green": 0.467, "blue": 0.341}  # #D97757
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
DARK = {"red": 0.176, "green": 0.176, "blue": 0.176}        # #2D2D2D
LIGHT_GRAY = {"red": 0.91, "green": 0.898, "blue": 0.855}   # #E8E5DA

SHEET_TITLE = "Social Media Recon Tracker"

HEADERS = [
    "Client Name",
    "Slug",
    "Instagram",
    "LinkedIn",
    "Facebook",
    "Status",
    "Last Updated",
    "Notes",
]

# Status values for data validation
STATUSES = ["pending", "researching", "complete", "no-socials", "error"]

# Pre-populated rows
SEED_DATA = [
    [
        "Patrick Bauer",
        "patrick-bauer",
        "",  # No Instagram (confirmed)
        "https://www.linkedin.com/in/patrick-bauer-86a29527/",
        "",  # Facebook TBD
        "pending",
        "2026-04-05",
        "No IG confirmed by client. Check FB.",
    ],
    [
        "Garrett Shuster",
        "garrett-shuster",
        "@garrettshuster",
        "",
        "",
        "pending",
        "2026-04-05",
        "Fashion brand founder. IG is primary.",
    ],
]


def _header_format():
    return {
        "backgroundColor": TERRACOTTA,
        "textFormat": {
            "bold": True,
            "fontSize": 11,
            "foregroundColor": WHITE,
        },
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE",
    }


def _build_sheet_properties():
    return {
        "properties": {
            "title": "Recon Queue",
            "gridProperties": {
                "rowCount": 100,
                "columnCount": len(HEADERS),
                "frozenRowCount": 1,
            },
            "tabColorStyle": {"rgbColor": TERRACOTTA},
        }
    }


def create_sheet():
    sheets = google_client.sheets_service()
    drive = google_client.drive_service()

    body = {
        "properties": {
            "title": SHEET_TITLE,
            "locale": "en_US",
        },
        "sheets": [_build_sheet_properties()],
    }

    spreadsheet = sheets.spreadsheets().create(
        body=body,
        fields="spreadsheetId,spreadsheetUrl,sheets/properties/sheetId",
    ).execute()

    sid = spreadsheet["spreadsheetId"]
    url = spreadsheet["spreadsheetUrl"]
    sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]

    print(f"Created: {url}")

    # --- Write headers ---
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range="'Recon Queue'!A1",
        valueInputOption="RAW",
        body={"values": [HEADERS]},
    ).execute()

    # --- Write seed data ---
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range="'Recon Queue'!A2",
        valueInputOption="RAW",
        body={"values": SEED_DATA},
    ).execute()

    # --- Format header row ---
    requests = [
        # Header formatting
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                },
                "cell": {"userEnteredFormat": _header_format()},
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        # Auto-resize columns
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": len(HEADERS),
                }
            }
        },
        # Set column widths for key columns
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,  # Client Name
                    "endIndex": 1,
                },
                "properties": {"pixelSize": 180},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 2,  # Instagram
                    "endIndex": 3,
                },
                "properties": {"pixelSize": 180},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 3,  # LinkedIn
                    "endIndex": 4,
                },
                "properties": {"pixelSize": 320},
                "fields": "pixelSize",
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 7,  # Notes
                    "endIndex": 8,
                },
                "properties": {"pixelSize": 300},
                "fields": "pixelSize",
            }
        },
        # Data validation on Status column (F)
        {
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 100,
                    "startColumnIndex": 5,  # Status col
                    "endColumnIndex": 6,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": s} for s in STATUSES],
                    },
                    "showCustomUi": True,
                    "strict": True,
                },
            }
        },
        # Alternating row colors
        {
            "addBanding": {
                "bandedRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 100,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(HEADERS),
                    },
                    "rowProperties": {
                        "headerColor": TERRACOTTA,
                        "firstBandColor": WHITE,
                        "secondBandColor": CREAM,
                    },
                }
            }
        },
    ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sid,
        body={"requests": requests},
    ).execute()

    print(f"Formatted with GBAutomation branding.")
    print(f"Sheet ID: {sid}")
    print(f"URL: {url}")
    return sid, url


if __name__ == "__main__":
    sheet_id, sheet_url = create_sheet()
