# Gmail + Google Drive Agent Setup
## greg@gbautomation.xyz (Google Workspace + Domain-Wide Delegation)

**Goal:** Service account that lets an agent read Gmail and organize Google Drive files for `greg@gbautomation.xyz` without browser login.

---

## Step 1 — Create a New GCP Project

1. Go to: https://console.cloud.google.com/projectcreate
2. Fill in:
   - **Project name:** `gbautomation-workspace`
   - **Organization:** `gbautomation.xyz` (if listed) or No organization
3. Click **Create** and wait ~30 seconds for it to provision
4. Make sure you're switched into the new project (dropdown at top)

---

## Step 2 — Enable Gmail + Drive APIs

Run both of these URLs while in your new project, or use the API Library:

1. **Gmail API:**
   https://console.cloud.google.com/apis/library/gmail.googleapis.com
   → Click **Enable**

2. **Google Drive API:**
   https://console.cloud.google.com/apis/library/drive.googleapis.com
   → Click **Enable**

---

## Step 3 — Create a Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **+ Create Service Account**
3. Fill in:
   - **Name:** `workspace-agent`
   - **ID:** `workspace-agent` (auto-filled)
   - **Description:** `Agent service account for Gmail + Drive access`
4. Click **Create and Continue**
5. Skip role grants for now → click **Done**

---

## Step 4 — Enable Domain-Wide Delegation on the Service Account

1. Click the `workspace-agent` service account you just created
2. Go to the **Details** tab
3. Under **Advanced settings**, check the box:
   ✅ **Enable Google Workspace Domain-wide Delegation**
4. Set **OAuth scopes product name** (display name): `GBAutomation Agent`
5. Click **Save**
6. **Copy the Client ID** shown — you'll need it in Step 6

---

## Step 5 — Download the Service Account JSON Key

1. Still on the service account page, go to **Keys** tab
2. Click **Add Key → Create new key**
3. Select **JSON** → click **Create**
4. A `.json` file downloads automatically — **keep this safe, treat like a password**
5. Open it and copy the entire contents

---

## Step 6 — Authorize in Google Admin Console (Domain-Wide Delegation)

1. Go to: https://admin.google.com → Security → Access and data control → **API controls**
2. Click **Manage Domain Wide Delegation** (at the bottom)
3. Click **Add new**
4. Fill in:
   - **Client ID:** (the one you copied in Step 4)
   - **OAuth scopes:** (paste these exactly, comma-separated)
     ```
     https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/drive
     ```
5. Click **Authorize**

> **Scope notes:**
> - `gmail.readonly` — read emails only
> - `gmail.modify` — read + label/move (needed to organize)
> - `drive` — full Drive access (create folders, move files)

---

## Step 7 — Store in AWS Secrets Manager

Once you have the JSON key file contents, paste them to Claude Code and it will store the secret as:
- **Secret name:** `gbautomation/google/workspace-agent-service-account`
- **Namespace:** consistent with existing `gbautomation/core/` pattern

---

## What the Agent Can Do With This

With the service account + domain-wide delegation, an agent can:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive'
]

credentials = service_account.Credentials.from_service_account_info(
    service_account_json,
    scopes=SCOPES,
    subject='greg@gbautomation.xyz'  # <-- impersonate this user
)

gmail = build('gmail', 'v1', credentials=credentials)
drive = build('drive', 'v3', credentials=credentials)

# Read emails
messages = gmail.users().messages().list(userId='me', q='is:unread').execute()

# Create a folder in Drive
folder = drive.files().create(body={
    'name': 'Organized by Agent',
    'mimeType': 'application/vnd.google-apps.folder'
}).execute()
```

---

## After Setup

Let Claude Code know when you have the JSON key and it will:
1. Store it in AWS Secrets Manager under `gbautomation/google/workspace-agent-service-account`
2. Write a reusable Python helper that builds authenticated Gmail + Drive clients
3. Wire it into whatever agent needs it
