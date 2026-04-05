"""
Google Workspace auth helper.
Loads the god token from AWS Secrets Manager and returns authenticated service clients.
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SECRET_ID = "gbautomation/google/workspace-god-token"
REGION = "us-east-1"

_creds = None


def get_credentials() -> Credentials:
    global _creds
    if _creds and _creds.valid:
        return _creds

    from .secret_cache import get_secret
    secret = get_secret(SECRET_ID, region=REGION)

    creds = Credentials(
        token=None,
        refresh_token=secret["refresh_token"],
        token_uri=secret["token_uri"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=secret["scopes"],
    )
    # Force refresh to get a valid access token
    creds.refresh(Request())
    _creds = creds
    return creds


def gmail_service():
    return build("gmail", "v1", credentials=get_credentials())


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


def docs_service():
    return build("docs", "v1", credentials=get_credentials())


def calendar_service():
    return build("calendar", "v3", credentials=get_credentials())


def sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


def people_service():
    return build("people", "v1", credentials=get_credentials())


def meet_service():
    return build("meet", "v2", credentials=get_credentials())


def tasks_service():
    return build("tasks", "v1", credentials=get_credentials())
