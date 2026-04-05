"""
Update the Google Workspace profile photo for greg@gbautomation.xyz.

Strategy (tried in order):
  1. People API — updateContactPhoto on "people/me"
       Requires: contacts or profile scope (already in god token via contacts.readonly? — worth trying)
  2. People API — raw PATCH via requests (bypasses googleapiclient scope check)
  3. Admin SDK Directory API — users.photos.update
       Requires: admin.directory.user scope (NOT in god token — will 403)

The god token scopes we have:
  - gmail.modify, gmail.send
  - drive
  - calendar
  - contacts.readonly          <-- People API read access
  - admin.directory.customer.readonly
  - admin.directory.domain.readonly
  - admin.reports.*

The People API updatePhoto endpoint (PATCH people/me:updateContactPhoto) requires
the "contacts" (read-write) scope, not contacts.readonly.

However, the People API also has a separate path for the *profile* photo
(as distinct from Contact photos). Profile photos on Google Workspace accounts
can be set via:
  - PATCH https://people.googleapis.com/v1/people/me:updateContactPhoto
    (needs contacts scope)
  - PUT  https://admin.googleapis.com/admin/directory/v1/users/{key}/photos/thumbnail
    (needs admin.directory.user scope)

Since neither write scope is in the god token, we make a raw authorized HTTP
request using the access token and let the server tell us which one works.
If both 403, we print clear instructions for adding the scope.
"""
import base64
import sys
import json
from pathlib import Path

# Allow running as a standalone script from any cwd
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from scripts.google_client import get_credentials
from PIL import Image
import io
import urllib.request
import urllib.error


LOGO_PATH = SKILL_ROOT / "assets" / "gb-logo.png"
USER_EMAIL = "greg@gbautomation.xyz"
MAX_DIM = 250


def load_and_resize(path: Path) -> tuple[bytes, int, int]:
    """Return (png_bytes, width, height) resized to MAX_DIM on longest side."""
    with Image.open(path) as img:
        img = img.convert("RGBA")
        w, h = img.size
        if w > MAX_DIM or h > MAX_DIM:
            ratio = MAX_DIM / max(w, h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            w, h = new_w, new_h
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), w, h


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii")


def b64std(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _raw_request(method: str, url: str, access_token: str, body: dict) -> dict:
    """Make an authorized JSON request without googleapiclient scope enforcement."""
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method=method,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {"status": "ok_empty_body"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {e.code} from {url}\nResponse: {error_body}"
        ) from e


def try_people_api(access_token: str, raw_bytes: bytes, width: int, height: int):
    """
    PATCH https://people.googleapis.com/v1/people/me:updateContactPhoto
    Requires contacts (read-write) scope.
    """
    url = "https://people.googleapis.com/v1/people/me:updateContactPhoto"
    body = {"photoBytes": b64std(raw_bytes)}
    return _raw_request("PATCH", url, access_token, body)


def try_admin_directory_api(access_token: str, raw_bytes: bytes, width: int, height: int):
    """
    PUT https://admin.googleapis.com/admin/directory/v1/users/{userKey}/photos/thumbnail
    Requires admin.directory.user scope.
    """
    from urllib.parse import quote
    encoded_user = quote(USER_EMAIL, safe="")
    url = f"https://admin.googleapis.com/admin/directory/v1/users/{encoded_user}/photos/thumbnail"
    body = {
        "photoData": b64url(raw_bytes),
        "mimeType": "IMAGE/PNG",
        "height": height,
        "width": width,
    }
    return _raw_request("PUT", url, access_token, body)


def update_photo():
    print(f"Loading logo from: {LOGO_PATH}")
    if not LOGO_PATH.exists():
        raise FileNotFoundError(f"Logo not found at {LOGO_PATH}")

    raw_bytes, width, height = load_and_resize(LOGO_PATH)
    print(f"Image prepared: {width}x{height} px, {len(raw_bytes):,} bytes")

    print("Authenticating via AWS god token...")
    creds = get_credentials()
    access_token = creds.token
    print(f"Access token obtained (first 20 chars): {access_token[:20]}...")

    # --- Attempt 1: People API updateContactPhoto ---
    print("\n[Attempt 1] People API — PATCH people/me:updateContactPhoto")
    try:
        result = try_people_api(access_token, raw_bytes, width, height)
        print("SUCCESS via People API!")
        print(json.dumps(result, indent=2))
        return result
    except RuntimeError as e:
        print(f"FAILED: {e}")

    # --- Attempt 2: Admin Directory API ---
    print("\n[Attempt 2] Admin Directory API — PUT users/{userKey}/photos/thumbnail")
    try:
        result = try_admin_directory_api(access_token, raw_bytes, width, height)
        print("SUCCESS via Admin Directory API!")
        print(json.dumps(result, indent=2))
        return result
    except RuntimeError as e:
        print(f"FAILED: {e}")

    # --- Both failed: print scope remediation steps ---
    print("\n" + "=" * 60)
    print("SCOPE REMEDIATION REQUIRED")
    print("=" * 60)
    print("""
Neither API succeeded with the current god token scopes.

To update a Google Workspace profile photo, the token needs one of:
  - https://www.googleapis.com/auth/contacts          (People API)
  - https://www.googleapis.com/auth/admin.directory.user  (Admin SDK)

Steps to add the scope to the god token:
  1. Go to: https://console.cloud.google.com/apis/credentials?project=gbautomationxyz
  2. Find the OAuth 2.0 Client ID used for the god token
  3. Add the required scope to the OAuth consent screen
  4. Re-authorize (run the OAuth flow) to get a new refresh_token with expanded scopes
  5. Update gbautomation/google/workspace-god-token in AWS Secrets Manager

Alternatively (fastest path):
  - Add admin.directory.user scope in Admin Console > Security > API Controls
  - Go to admin.google.com > Security > Access and data control > API controls
  - Under Domain-wide delegation, confirm the service account has the scope
""")
    sys.exit(1)


if __name__ == "__main__":
    update_photo()
