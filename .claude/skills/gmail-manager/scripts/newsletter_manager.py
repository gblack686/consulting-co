#!/usr/bin/env python3
"""
Newsletter Manager

Handles newsletter detection, unsubscribe link extraction,
and Gmail filter creation for blocking/auto-archiving.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from .gmail_client import GmailClient
from .supabase_gmail_client import SupabaseGmailClient


class NewsletterManager:
    """Manage newsletter subscriptions and filters."""

    # Known newsletter/marketing email domains
    NEWSLETTER_DOMAINS = {
        'mailchimp.com', 'mail.mailchimp.com', 'mailchi.mp',
        'convertkit.com', 'convertkit.net',
        'substack.com',
        'buttondown.email',
        'mailgun.org', 'mailgun.net',
        'sendgrid.net', 'sendgrid.com',
        'constantcontact.com',
        'hubspot.com', 'hubspotemail.net',
        'mailerlite.com',
        'getresponse.com',
        'aweber.com',
        'klaviyo.com',
        'drip.com',
        'activecampaign.com',
        'campaignmonitor.com',
        'sendinblue.com', 'brevo.com',
        'beehiiv.com',
        'ghost.io',
        'revue.email',
        'tinyletter.com',
        'sendy.co',
        'mailjet.com',
        'sparkpost.com',
        'postmarkapp.com',
        'amazonses.com',
    }

    def __init__(
        self,
        gmail_client: GmailClient,
        supabase_client: SupabaseGmailClient = None
    ):
        """
        Initialize newsletter manager.

        Args:
            gmail_client: Gmail API client
            supabase_client: Optional Supabase client for tracking
        """
        self.gmail = gmail_client
        self.db = supabase_client

    def detect_newsletters(
        self,
        max_messages: int = 100,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect newsletter emails in inbox.

        Args:
            max_messages: Maximum messages to scan
            days_back: How many days back to search

        Returns:
            List of detected newsletter senders with stats
        """
        # Query for potential newsletters
        query = f"newer_than:{days_back}d"

        result = self.gmail.list_messages(query=query, max_results=max_messages)
        messages = result.get('messages', [])

        newsletters = {}

        for msg_ref in messages:
            message = self.gmail.get_message(msg_ref['id'], format='metadata')
            if not message:
                continue

            headers = self._get_headers(message)

            # Check if newsletter
            is_newsletter, reason = self._is_newsletter(headers, message)

            if is_newsletter:
                sender = headers.get('from', 'Unknown')
                sender_email = self._extract_email(sender)

                if sender_email not in newsletters:
                    newsletters[sender_email] = {
                        'email': sender_email,
                        'name': self._extract_name(sender),
                        'count': 0,
                        'unsubscribe_link': None,
                        'unsubscribe_mailto': None,
                        'detection_reason': reason,
                        'sample_subject': headers.get('subject', ''),
                    }

                newsletters[sender_email]['count'] += 1

                # Try to get unsubscribe info
                if not newsletters[sender_email]['unsubscribe_link']:
                    unsub = self._parse_unsubscribe_header(
                        headers.get('list-unsubscribe', '')
                    )
                    newsletters[sender_email]['unsubscribe_link'] = unsub.get('url')
                    newsletters[sender_email]['unsubscribe_mailto'] = unsub.get('mailto')

        return sorted(
            newsletters.values(),
            key=lambda x: x['count'],
            reverse=True
        )

    def _is_newsletter(
        self,
        headers: Dict[str, str],
        message: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Determine if an email is a newsletter.

        Returns:
            Tuple of (is_newsletter: bool, reason: str)
        """
        # Check List-Unsubscribe header
        if 'list-unsubscribe' in headers:
            return True, "List-Unsubscribe header"

        # Check Precedence header
        precedence = headers.get('precedence', '').lower()
        if precedence in ('bulk', 'list'):
            return True, f"Precedence: {precedence}"

        # Check sender domain
        sender = headers.get('from', '')
        sender_email = self._extract_email(sender)
        if sender_email:
            domain = sender_email.split('@')[-1].lower()
            if domain in self.NEWSLETTER_DOMAINS:
                return True, f"Known newsletter domain: {domain}"

        # Check for common newsletter patterns in subject
        subject = headers.get('subject', '').lower()
        newsletter_patterns = [
            r'newsletter',
            r'weekly digest',
            r'daily digest',
            r'weekly roundup',
            r'issue #?\d+',
            r'edition #?\d+',
            r'unsubscribe',
        ]
        for pattern in newsletter_patterns:
            if re.search(pattern, subject):
                return True, f"Subject pattern: {pattern}"

        return False, ""

    def _get_headers(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Extract headers from message."""
        headers = {}
        payload = message.get('payload', {})
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        return headers

    def _extract_email(self, from_header: str) -> Optional[str]:
        """Extract email address from From header."""
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        return match.group().lower() if match else None

    def _extract_name(self, from_header: str) -> Optional[str]:
        """Extract display name from From header."""
        # Try "Name" <email> format
        match = re.match(r'"?([^"<]+)"?\s*<', from_header)
        if match:
            return match.group(1).strip()
        return None

    def _parse_unsubscribe_header(self, header: str) -> Dict[str, Optional[str]]:
        """
        Parse List-Unsubscribe header.

        Handles formats:
        - <mailto:unsubscribe@example.com>
        - <https://example.com/unsubscribe>
        - <mailto:...>, <https://...>
        """
        result = {'url': None, 'mailto': None}

        if not header:
            return result

        # Find all URLs and mailto links
        mailto_match = re.search(r'<mailto:([^>]+)>', header)
        url_match = re.search(r'<(https?://[^>]+)>', header)

        if mailto_match:
            result['mailto'] = f"mailto:{mailto_match.group(1)}"

        if url_match:
            result['url'] = url_match.group(1)

        return result

    def get_unsubscribe_link(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get unsubscribe information for a specific message.

        Args:
            message_id: Gmail message ID

        Returns:
            Dict with unsubscribe_url and/or unsubscribe_mailto
        """
        message = self.gmail.get_message(message_id, format='full')
        if not message:
            return None

        headers = self._get_headers(message)
        unsub = self._parse_unsubscribe_header(headers.get('list-unsubscribe', ''))

        # Also try to find unsubscribe link in body
        if not unsub['url']:
            body = self.gmail.get_message_body(message)
            url = self._find_unsubscribe_in_body(body)
            if url:
                unsub['url'] = url

        return {
            'message_id': message_id,
            'sender': headers.get('from', ''),
            'subject': headers.get('subject', ''),
            'unsubscribe_url': unsub.get('url'),
            'unsubscribe_mailto': unsub.get('mailto'),
        }

    def _find_unsubscribe_in_body(self, body: str) -> Optional[str]:
        """Find unsubscribe link in email body."""
        if not body:
            return None

        # Pattern for unsubscribe links
        patterns = [
            r'href=["\']?(https?://[^"\'>\s]*unsubscribe[^"\'>\s]*)["\']?',
            r'(https?://[^\s<>"]*unsubscribe[^\s<>"]*)',
            r'href=["\']?(https?://[^"\'>\s]*opt-out[^"\'>\s]*)["\']?',
        ]

        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def create_block_filter(
        self,
        sender: str,
        action: str = 'archive',
        reason: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Gmail filter to block/archive emails from a sender.

        Args:
            sender: Email address or domain to block
            action: 'archive' (skip inbox), 'trash' (delete), or 'read' (mark as read)
            reason: Optional reason for creating filter

        Returns:
            Filter object if created successfully
        """
        # Determine criteria (email or domain)
        if '@' in sender:
            criteria = {'from': sender}
        else:
            # Domain - match any email from this domain
            criteria = {'from': f'@{sender}'}

        # Determine actions
        if action == 'trash':
            actions = {'addLabelIds': ['TRASH']}
        elif action == 'read':
            actions = {'removeLabelIds': ['UNREAD']}
        else:  # archive
            actions = {'removeLabelIds': ['INBOX']}

        # Create filter in Gmail
        gmail_filter = self.gmail.create_filter(criteria, actions)

        if gmail_filter and self.db:
            # Track filter in Supabase
            self.db.store_filter({
                'gmail_filter_id': gmail_filter.get('id'),
                'filter_type': action,
                'target_email': sender if '@' in sender else None,
                'target_domain': sender if '@' not in sender else None,
                'criteria': criteria,
                'actions': actions,
                'reason': reason,
            })

            # Mark contact as unsubscribed if email
            if '@' in sender:
                self.db.mark_unsubscribed(sender)

        return gmail_filter

    def create_auto_archive_filter(self, sender: str) -> Optional[Dict[str, Any]]:
        """Create filter to auto-archive (skip inbox) from sender."""
        return self.create_block_filter(sender, action='archive')

    def create_delete_filter(self, sender: str) -> Optional[Dict[str, Any]]:
        """Create filter to auto-delete from sender."""
        return self.create_block_filter(sender, action='trash')

    def unsubscribe_via_mailto(self, mailto_link: str) -> Optional[Dict[str, Any]]:
        """
        Send an unsubscribe email using mailto link.

        Args:
            mailto_link: mailto: URL from List-Unsubscribe header

        Returns:
            Sent message info if successful
        """
        if not mailto_link or not mailto_link.startswith('mailto:'):
            return None

        # Parse mailto link
        mailto_link = mailto_link[7:]  # Remove 'mailto:'

        # Handle mailto:email?subject=xxx format
        if '?' in mailto_link:
            email, params = mailto_link.split('?', 1)
            subject = ''
            body = ''

            for param in params.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key.lower() == 'subject':
                        subject = value
                    elif key.lower() == 'body':
                        body = value
        else:
            email = mailto_link
            subject = 'Unsubscribe'
            body = 'Please unsubscribe me from this mailing list.'

        # Send the email
        return self.gmail.send_message(
            to=email,
            subject=subject,
            body=body or 'Unsubscribe'
        )

    def list_blocked_senders(self) -> List[Dict[str, Any]]:
        """List all senders with active block/archive filters."""
        filters = self.gmail.list_filters()

        blocked = []
        for f in filters:
            criteria = f.get('criteria', {})
            action = f.get('action', {})

            # Check if this is a block/archive filter
            removes_inbox = 'INBOX' in action.get('removeLabelIds', [])
            adds_trash = 'TRASH' in action.get('addLabelIds', [])

            if removes_inbox or adds_trash:
                sender = criteria.get('from', '')
                if sender:
                    blocked.append({
                        'filter_id': f.get('id'),
                        'sender': sender,
                        'action': 'trash' if adds_trash else 'archive',
                    })

        return blocked

    def remove_block(self, filter_id: str) -> bool:
        """Remove a block filter."""
        return self.gmail.delete_filter(filter_id)
