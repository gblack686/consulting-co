#!/usr/bin/env python3
"""
Domain and Contact Extractor

Extracts unique email addresses and domains from Gmail messages.
Categorizes contacts and detects newsletters.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExtractedContact:
    """Represents an extracted email contact."""
    email_address: str
    domain: str
    display_name: Optional[str] = None
    source_type: str = 'inbox'  # 'inbox', 'sent', 'both'
    is_newsletter: bool = False
    category: Optional[str] = None
    first_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_seen_at: datetime = field(default_factory=datetime.utcnow)
    emails_received: int = 0
    emails_sent: int = 0


class DomainExtractor:
    """Extract and categorize email addresses and domains."""

    # Known newsletter/marketing domains
    NEWSLETTER_DOMAINS = {
        'mailchimp.com', 'mail.mailchimp.com',
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
    }

    # Known personal email domains
    PERSONAL_DOMAINS = {
        'gmail.com', 'googlemail.com',
        'yahoo.com', 'yahoo.co.uk', 'yahoo.ca',
        'hotmail.com', 'outlook.com', 'live.com', 'msn.com',
        'icloud.com', 'me.com', 'mac.com',
        'aol.com',
        'protonmail.com', 'proton.me',
        'fastmail.com', 'fastmail.fm',
        'zoho.com',
        'hey.com',
        'tutanota.com', 'tuta.io',
    }

    # System/no-reply patterns
    NOREPLY_PATTERNS = [
        r'noreply', r'no-reply', r'no_reply',
        r'donotreply', r'do-not-reply', r'do_not_reply',
        r'notifications?@',
        r'alerts?@',
        r'mailer-daemon',
        r'postmaster',
    ]

    def __init__(self):
        self._noreply_regex = re.compile(
            '|'.join(self.NOREPLY_PATTERNS),
            re.IGNORECASE
        )

    def extract_from_message(
        self,
        message: Dict,
        source: str = 'inbox'
    ) -> Dict[str, ExtractedContact]:
        """
        Extract all email addresses from a message.

        Args:
            message: Gmail message object
            source: 'inbox' or 'sent'

        Returns:
            Dict mapping email address to ExtractedContact
        """
        contacts = {}
        headers = self._get_headers(message)

        # Extract from relevant headers based on source
        if source == 'inbox':
            # For inbox, we care about who sent to us
            from_emails = self._parse_email_list(headers.get('from', ''))
            for email_addr, display_name in from_emails:
                contact = self._create_contact(
                    email_addr, display_name, 'inbox', message
                )
                contact.emails_received = 1
                contacts[email_addr.lower()] = contact

        elif source == 'sent':
            # For sent, we care about who we sent to
            to_emails = self._parse_email_list(headers.get('to', ''))
            cc_emails = self._parse_email_list(headers.get('cc', ''))

            for email_addr, display_name in to_emails + cc_emails:
                contact = self._create_contact(
                    email_addr, display_name, 'sent', message
                )
                contact.emails_sent = 1
                contacts[email_addr.lower()] = contact

        return contacts

    def _create_contact(
        self,
        email_addr: str,
        display_name: Optional[str],
        source: str,
        message: Dict
    ) -> ExtractedContact:
        """Create an ExtractedContact from parsed data."""
        domain = self._extract_domain(email_addr)

        contact = ExtractedContact(
            email_address=email_addr.lower(),
            domain=domain,
            display_name=display_name,
            source_type=source,
            is_newsletter=self._is_newsletter(email_addr, domain, message),
            category=self._categorize_domain(domain, email_addr),
        )

        return contact

    def _get_headers(self, message: Dict) -> Dict[str, str]:
        """Extract headers from message."""
        headers = {}
        payload = message.get('payload', {})
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        return headers

    def _parse_email_list(self, header_value: str) -> List[Tuple[str, Optional[str]]]:
        """
        Parse email addresses from a header value.

        Handles formats like:
        - simple@email.com
        - "Display Name" <email@example.com>
        - Display Name <email@example.com>
        - email@example.com, another@example.com

        Returns:
            List of (email_address, display_name) tuples
        """
        results = []

        if not header_value:
            return results

        # Pattern for "Name" <email> or Name <email>
        pattern = r'(?:"?([^"<]*)"?\s*)?<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?'

        matches = re.findall(pattern, header_value)

        for name, email_addr in matches:
            display_name = name.strip() if name and name.strip() else None
            results.append((email_addr, display_name))

        return results

    def _extract_domain(self, email_addr: str) -> str:
        """Extract domain from email address."""
        try:
            return email_addr.split('@')[1].lower()
        except IndexError:
            return ''

    def _is_newsletter(
        self,
        email_addr: str,
        domain: str,
        message: Dict
    ) -> bool:
        """
        Detect if an email is from a newsletter.

        Checks:
        - Domain against known newsletter platforms
        - List-Unsubscribe header
        - Sender patterns
        """
        # Check domain
        if domain in self.NEWSLETTER_DOMAINS:
            return True

        # Check for List-Unsubscribe header
        headers = self._get_headers(message)
        if 'list-unsubscribe' in headers:
            return True

        # Check for Precedence: bulk
        precedence = headers.get('precedence', '').lower()
        if precedence in ('bulk', 'list'):
            return True

        return False

    def _categorize_domain(self, domain: str, email_addr: str) -> str:
        """
        Categorize a domain/email.

        Categories:
        - personal: Personal email providers (gmail, yahoo, etc.)
        - newsletter: Known newsletter/marketing platforms
        - noreply: System/automated emails
        - corporate: Business domains
        - unknown: Cannot determine
        """
        if domain in self.PERSONAL_DOMAINS:
            return 'personal'

        if domain in self.NEWSLETTER_DOMAINS:
            return 'newsletter'

        if self._noreply_regex.search(email_addr):
            return 'noreply'

        # Assume business domain if not in known categories
        return 'corporate'

    def is_noreply(self, email_addr: str) -> bool:
        """Check if email is a no-reply address."""
        return bool(self._noreply_regex.search(email_addr.lower()))

    def merge_contacts(
        self,
        existing: ExtractedContact,
        new: ExtractedContact
    ) -> ExtractedContact:
        """
        Merge two contacts for the same email address.

        Updates counts and source type.
        """
        # Update source type
        if existing.source_type != new.source_type:
            existing.source_type = 'both'

        # Update counts
        existing.emails_received += new.emails_received
        existing.emails_sent += new.emails_sent

        # Update last seen
        if new.last_seen_at > existing.last_seen_at:
            existing.last_seen_at = new.last_seen_at

        # Keep first seen
        if new.first_seen_at < existing.first_seen_at:
            existing.first_seen_at = new.first_seen_at

        # Update display name if we didn't have one
        if not existing.display_name and new.display_name:
            existing.display_name = new.display_name

        # Update newsletter status (if either is newsletter)
        existing.is_newsletter = existing.is_newsletter or new.is_newsletter

        return existing

    def extract_domains_summary(
        self,
        contacts: Dict[str, ExtractedContact]
    ) -> Dict[str, Dict]:
        """
        Create a summary of domains from extracted contacts.

        Returns:
            Dict mapping domain to stats
        """
        domains = {}

        for contact in contacts.values():
            domain = contact.domain

            if domain not in domains:
                domains[domain] = {
                    'domain': domain,
                    'total_contacts': 0,
                    'emails_received': 0,
                    'emails_sent': 0,
                    'category': contact.category,
                    'is_blocked': False,
                }

            domains[domain]['total_contacts'] += 1
            domains[domain]['emails_received'] += contact.emails_received
            domains[domain]['emails_sent'] += contact.emails_sent

        return domains
