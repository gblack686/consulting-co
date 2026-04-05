#!/usr/bin/env python3
"""
OAuth2 Handler for Gmail API

Manages the OAuth2 authentication flow for connecting to user's Gmail account.
Handles token creation, refresh, and storage.
"""

import os
import pickle
from pathlib import Path
from typing import Optional, Dict, Any

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GmailOAuth2Handler:
    """Manages OAuth2 authentication for Gmail API."""

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.settings.basic',
        'https://www.googleapis.com/auth/calendar.readonly',
    ]

    def __init__(
        self,
        credentials_file: str = 'gmail_client_secret.json',
        token_file: str = None
    ):
        """
        Initialize OAuth2 handler.

        Args:
            credentials_file: Path to OAuth2 client secret JSON from Google Cloud Console
            token_file: Path to store/retrieve OAuth2 access tokens
        """
        self.credentials_file = credentials_file

        # Default token file in skill's .tokens directory
        if token_file is None:
            skill_dir = Path(__file__).parent.parent
            token_file = str(skill_dir / '.tokens' / 'gmail_oauth.pkl')

        self.token_file = token_file
        self.credentials = None

        # Create token directory if it doesn't exist
        token_dir = Path(self.token_file).parent
        token_dir.mkdir(parents=True, exist_ok=True)

    def authenticate(self) -> Credentials:
        """
        Authenticate with Gmail API.

        Returns existing token if valid, otherwise initiates OAuth2 flow.

        Returns:
            google.oauth2.credentials.Credentials: Authenticated credentials
        """
        # Try to load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                self.credentials = pickle.load(f)

            # Refresh if expired
            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self._save_token()
                    return self.credentials
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    # Fall through to re-authenticate

            # Return if valid
            if self.credentials.valid:
                return self.credentials

        # Check that credentials file exists
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"OAuth credentials file not found: {self.credentials_file}\n"
                "Please download client_secret.json from Google Cloud Console."
            )

        # Initiate OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES
        )

        self.credentials = flow.run_local_server(port=0)
        self._save_token()

        return self.credentials

    def _save_token(self):
        """Save credentials to file for future use."""
        with open(self.token_file, 'wb') as f:
            pickle.dump(self.credentials, f)

    def is_authenticated(self) -> bool:
        """Check if valid credentials exist."""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as f:
                    creds = pickle.load(f)
                if creds.valid:
                    return True
                elif creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    return True
            except Exception:
                pass
        return False

    def get_credentials(self) -> Optional[Credentials]:
        """Get current credentials, authenticating if necessary."""
        if not self.credentials or not self.credentials.valid:
            self.authenticate()
        return self.credentials

    def clear_token(self):
        """Clear stored token (for logout/re-authentication)."""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        self.credentials = None
        print("Token cleared. Re-authentication required.")

    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current token."""
        if not os.path.exists(self.token_file):
            return None

        try:
            with open(self.token_file, 'rb') as f:
                creds = pickle.load(f)
            return {
                'valid': creds.valid,
                'expired': creds.expired,
                'token': creds.token[:20] + '...' if creds.token else None,
                'expiry': str(creds.expiry) if creds.expiry else None,
                'scopes': creds.scopes if hasattr(creds, 'scopes') else self.SCOPES,
            }
        except Exception as e:
            return {'error': str(e)}


def setup_oauth_credentials(credentials_file: str = 'gmail_client_secret.json') -> str:
    """
    Helper to set up OAuth credentials from client_secret JSON.

    Args:
        credentials_file: Path to client_secret JSON file

    Returns:
        Path where credentials were stored
    """
    handler = GmailOAuth2Handler(credentials_file=credentials_file)

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")

    print(f"Setting up Gmail OAuth2 with credentials from: {credentials_file}")
    print("Opening browser for authentication...")
    print(f"Requesting scopes: {handler.SCOPES}")

    creds = handler.authenticate()

    print("Authentication successful!")
    print(f"Token saved to: {handler.token_file}")

    return handler.token_file


if __name__ == '__main__':
    import sys

    creds_file = sys.argv[1] if len(sys.argv) > 1 else 'gmail_client_secret.json'
    setup_oauth_credentials(creds_file)
