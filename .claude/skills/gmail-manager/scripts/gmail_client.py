#!/usr/bin/env python3
"""
Gmail API Client

Core wrapper for Gmail API operations including reading, modifying,
creating drafts, sending emails, and managing filters.
"""

import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .gmail_oauth_handler import GmailOAuth2Handler


class GmailClient:
    """Core Gmail API wrapper for all email operations."""

    def __init__(self, oauth_handler: GmailOAuth2Handler = None):
        """
        Initialize Gmail client.

        Args:
            oauth_handler: OAuth2 handler instance. Creates one if not provided.
        """
        self.oauth_handler = oauth_handler or GmailOAuth2Handler()
        self.service = None
        self._user_id = 'me'

    def _get_service(self):
        """Get or create Gmail API service."""
        if not self.service:
            credentials = self.oauth_handler.get_credentials()
            self.service = build('gmail', 'v1', credentials=credentials)
        return self.service

    # =========================================================================
    # Message Operations
    # =========================================================================

    def list_messages(
        self,
        query: str = '',
        max_results: int = 100,
        label_ids: List[str] = None,
        page_token: str = None
    ) -> Dict[str, Any]:
        """
        List messages matching a query.

        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
            max_results: Maximum number of messages to return
            label_ids: Filter by label IDs (e.g., ['INBOX', 'UNREAD'])
            page_token: Token for pagination

        Returns:
            Dict with 'messages' list and 'nextPageToken' if more results exist
        """
        service = self._get_service()

        try:
            kwargs = {
                'userId': self._user_id,
                'maxResults': max_results,
            }
            if query:
                kwargs['q'] = query
            if label_ids:
                kwargs['labelIds'] = label_ids
            if page_token:
                kwargs['pageToken'] = page_token

            result = service.users().messages().list(**kwargs).execute()

            return {
                'messages': result.get('messages', []),
                'nextPageToken': result.get('nextPageToken'),
                'resultSizeEstimate': result.get('resultSizeEstimate', 0)
            }
        except HttpError as e:
            print(f"Error listing messages: {e}")
            return {'messages': [], 'error': str(e)}

    def get_message(self, message_id: str, format: str = 'full') -> Optional[Dict[str, Any]]:
        """
        Get a single message by ID.

        Args:
            message_id: The message ID
            format: 'full', 'minimal', 'raw', or 'metadata'

        Returns:
            Message object or None if not found
        """
        service = self._get_service()

        try:
            message = service.users().messages().get(
                userId=self._user_id,
                id=message_id,
                format=format
            ).execute()
            return message
        except HttpError as e:
            print(f"Error getting message {message_id}: {e}")
            return None

    def get_message_body(self, message: Dict[str, Any]) -> str:
        """
        Extract the body text from a message object.

        Args:
            message: Message object from get_message()

        Returns:
            Decoded message body as string
        """
        payload = message.get('payload', {})

        # Try to get body from payload directly
        body_data = payload.get('body', {}).get('data')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')

        # Handle multipart messages
        parts = payload.get('parts', [])
        for part in parts:
            mime_type = part.get('mimeType', '')
            if mime_type == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            elif mime_type == 'text/html':
                # Fallback to HTML if no plain text
                data = part.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            elif mime_type.startswith('multipart/'):
                # Recursively check nested parts
                nested_parts = part.get('parts', [])
                for nested in nested_parts:
                    if nested.get('mimeType') == 'text/plain':
                        data = nested.get('body', {}).get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        return ''

    def get_message_headers(self, message: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract headers from a message object.

        Args:
            message: Message object from get_message()

        Returns:
            Dict of header name -> value
        """
        headers = {}
        payload = message.get('payload', {})
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        return headers

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        return self._modify_labels(message_id, remove_labels=['UNREAD'])

    def mark_as_unread(self, message_id: str) -> bool:
        """Mark a message as unread."""
        return self._modify_labels(message_id, add_labels=['UNREAD'])

    def archive_message(self, message_id: str) -> bool:
        """Archive a message (remove from INBOX)."""
        return self._modify_labels(message_id, remove_labels=['INBOX'])

    def trash_message(self, message_id: str) -> bool:
        """Move a message to trash."""
        service = self._get_service()
        try:
            service.users().messages().trash(
                userId=self._user_id,
                id=message_id
            ).execute()
            return True
        except HttpError as e:
            print(f"Error trashing message: {e}")
            return False

    def _modify_labels(
        self,
        message_id: str,
        add_labels: List[str] = None,
        remove_labels: List[str] = None
    ) -> bool:
        """Modify labels on a message."""
        service = self._get_service()

        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels

            service.users().messages().modify(
                userId=self._user_id,
                id=message_id,
                body=body
            ).execute()
            return True
        except HttpError as e:
            print(f"Error modifying labels: {e}")
            return False

    # =========================================================================
    # Draft Operations
    # =========================================================================

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        reply_to_message_id: str = None,
        html: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a draft email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            reply_to_message_id: Message ID to reply to (sets thread)
            html: If True, body is HTML content

        Returns:
            Draft object or None if failed
        """
        service = self._get_service()

        message = self._create_message(to, subject, body, cc, bcc, html)

        # Set thread ID if replying
        if reply_to_message_id:
            original = self.get_message(reply_to_message_id, format='metadata')
            if original:
                message['threadId'] = original.get('threadId')

        try:
            draft = service.users().drafts().create(
                userId=self._user_id,
                body={'message': message}
            ).execute()
            return draft
        except HttpError as e:
            print(f"Error creating draft: {e}")
            return None

    def list_drafts(self) -> List[Dict[str, Any]]:
        """List all drafts."""
        service = self._get_service()

        try:
            result = service.users().drafts().list(userId=self._user_id).execute()
            return result.get('drafts', [])
        except HttpError as e:
            print(f"Error listing drafts: {e}")
            return []

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft."""
        service = self._get_service()

        try:
            service.users().drafts().delete(
                userId=self._user_id,
                id=draft_id
            ).execute()
            return True
        except HttpError as e:
            print(f"Error deleting draft: {e}")
            return False

    # =========================================================================
    # Send Operations
    # =========================================================================

    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        html: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            html: If True, body is HTML content

        Returns:
            Sent message object or None if failed
        """
        service = self._get_service()

        message = self._create_message(to, subject, body, cc, bcc, html)

        try:
            sent = service.users().messages().send(
                userId=self._user_id,
                body=message
            ).execute()
            return sent
        except HttpError as e:
            print(f"Error sending message: {e}")
            return None

    def send_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Send a draft."""
        service = self._get_service()

        try:
            sent = service.users().drafts().send(
                userId=self._user_id,
                body={'id': draft_id}
            ).execute()
            return sent
        except HttpError as e:
            print(f"Error sending draft: {e}")
            return None

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        html: bool = False
    ) -> Dict[str, str]:
        """Create a message object for API."""
        if html:
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(body, 'html'))
        else:
            message = MIMEText(body)

        message['to'] = to
        message['subject'] = subject

        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw}

    # =========================================================================
    # Filter Operations
    # =========================================================================

    def create_filter(
        self,
        criteria: Dict[str, Any],
        actions: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Gmail filter.

        Args:
            criteria: Filter criteria (from, to, subject, query, etc.)
            actions: Filter actions (addLabelIds, removeLabelIds, forward, etc.)

        Returns:
            Filter object or None if failed
        """
        service = self._get_service()

        filter_body = {
            'criteria': criteria,
            'action': actions
        }

        try:
            result = service.users().settings().filters().create(
                userId=self._user_id,
                body=filter_body
            ).execute()
            return result
        except HttpError as e:
            print(f"Error creating filter: {e}")
            return None

    def list_filters(self) -> List[Dict[str, Any]]:
        """List all filters."""
        service = self._get_service()

        try:
            result = service.users().settings().filters().list(
                userId=self._user_id
            ).execute()
            return result.get('filter', [])
        except HttpError as e:
            print(f"Error listing filters: {e}")
            return []

    def delete_filter(self, filter_id: str) -> bool:
        """Delete a filter."""
        service = self._get_service()

        try:
            service.users().settings().filters().delete(
                userId=self._user_id,
                id=filter_id
            ).execute()
            return True
        except HttpError as e:
            print(f"Error deleting filter: {e}")
            return False

    # =========================================================================
    # Label Operations
    # =========================================================================

    def list_labels(self) -> List[Dict[str, Any]]:
        """List all labels."""
        service = self._get_service()

        try:
            result = service.users().labels().list(userId=self._user_id).execute()
            return result.get('labels', [])
        except HttpError as e:
            print(f"Error listing labels: {e}")
            return []

    def create_label(self, name: str) -> Optional[Dict[str, Any]]:
        """Create a new label."""
        service = self._get_service()

        try:
            label = service.users().labels().create(
                userId=self._user_id,
                body={'name': name}
            ).execute()
            return label
        except HttpError as e:
            print(f"Error creating label: {e}")
            return None

    # Gmail API predefined label colors
    LABEL_COLORS = {
        'sales_marketing': {
            'backgroundColor': '#fb4c2f',  # Red
            'textColor': '#ffffff'
        },
        'important': {
            'backgroundColor': '#16a766',  # Green
            'textColor': '#ffffff'
        },
        'receipts': {
            'backgroundColor': '#4a86e8',  # Blue
            'textColor': '#ffffff'
        },
        'human': {
            'backgroundColor': '#ffad47',  # Orange/Gold
            'textColor': '#ffffff'
        }
    }

    def create_label_with_color(
        self,
        name: str,
        color_key: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a label with optional color.

        Args:
            name: Label name
            color_key: Key from LABEL_COLORS (sales_marketing, important, receipts, human)

        Returns:
            Label object or None if failed
        """
        service = self._get_service()

        label_body = {
            'name': name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
        }

        if color_key and color_key in self.LABEL_COLORS:
            label_body['color'] = self.LABEL_COLORS[color_key]

        try:
            label = service.users().labels().create(
                userId=self._user_id,
                body=label_body
            ).execute()
            return label
        except HttpError as e:
            print(f"Error creating label with color: {e}")
            return None

    def get_or_create_label(
        self,
        name: str,
        color_key: str = None
    ) -> Optional[str]:
        """
        Get existing label ID or create new one with color.

        Args:
            name: Label name to find or create
            color_key: Color key if creating new label

        Returns:
            Label ID or None if failed
        """
        # Check existing labels
        labels = self.list_labels()
        for label in labels:
            if label.get('name', '').lower() == name.lower():
                return label['id']

        # Create new label
        new_label = self.create_label_with_color(name, color_key)
        return new_label['id'] if new_label else None

    def apply_label_to_message(self, message_id: str, label_id: str) -> bool:
        """
        Apply a label to a message.

        Args:
            message_id: Gmail message ID
            label_id: Label ID to apply

        Returns:
            True if successful
        """
        return self._modify_labels(message_id, add_labels=[label_id])

    def remove_label_from_message(self, message_id: str, label_id: str) -> bool:
        """
        Remove a label from a message.

        Args:
            message_id: Gmail message ID
            label_id: Label ID to remove

        Returns:
            True if successful
        """
        return self._modify_labels(message_id, remove_labels=[label_id])

    # =========================================================================
    # Profile Operations
    # =========================================================================

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """Get user's Gmail profile."""
        service = self._get_service()

        try:
            profile = service.users().getProfile(userId=self._user_id).execute()
            return profile
        except HttpError as e:
            print(f"Error getting profile: {e}")
            return None
