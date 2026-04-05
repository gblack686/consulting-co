#!/usr/bin/env python3
"""
Auto-Archive Workflow

Processes inbox emails, classifies them, and automatically archives
sales/marketing emails with appropriate labels.
"""

import os
import re
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .gmail_client import GmailClient
from .gmail_oauth_handler import GmailOAuth2Handler
from .email_classifier import EmailClassifier, ClassificationResult
from .supabase_gmail_client import SupabaseGmailClient


@dataclass
class ArchiveStats:
    """Statistics from an archive run."""
    total_processed: int = 0
    sales_archived: int = 0
    transactional_kept: int = 0
    human_kept: int = 0
    newsletter_kept: int = 0
    automated_kept: int = 0
    errors: int = 0


class AutoArchiver:
    """Automated email classification and archiving workflow."""

    # Label names and their color keys
    LABELS = {
        'sales': ('Sales/Marketing', 'sales_marketing'),
        'receipts': ('Receipts', 'receipts'),
        'important': ('Important', 'important'),
        'human': ('Human', 'human'),
    }

    def __init__(
        self,
        gmail_client: GmailClient = None,
        classifier: EmailClassifier = None,
        supabase_client: SupabaseGmailClient = None
    ):
        """
        Initialize auto-archiver.

        Args:
            gmail_client: Gmail API client
            classifier: Email classifier
            supabase_client: Supabase storage client
        """
        self.gmail = gmail_client or GmailClient()
        self.classifier = classifier or EmailClassifier()
        self.supabase = supabase_client or SupabaseGmailClient()

        # Label ID cache
        self._label_ids: Dict[str, str] = {}

    def setup_labels(self) -> Dict[str, str]:
        """
        Create Gmail labels with colors if they don't exist.

        Returns:
            Dict mapping label key to label ID
        """
        print("Setting up Gmail labels...")

        for key, (name, color_key) in self.LABELS.items():
            label_id = self.gmail.get_or_create_label(name, color_key)
            if label_id:
                self._label_ids[key] = label_id
                print(f"  ✓ {name}: {label_id}")
            else:
                print(f"  ✗ Failed to create label: {name}")

        return self._label_ids

    def build_sent_contacts(self, max_messages: int = 1000) -> int:
        """
        Scan sent mail to build known contacts database.

        Args:
            max_messages: Maximum sent messages to scan

        Returns:
            Number of contacts added
        """
        print(f"Building sent contacts from up to {max_messages} sent messages...")

        # List sent messages
        result = self.gmail.list_messages(
            label_ids=['SENT'],
            max_results=max_messages
        )

        messages = result.get('messages', [])
        contacts_added = 0

        for i, msg_info in enumerate(messages):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(messages)} sent messages...")

            message = self.gmail.get_message(msg_info['id'], format='metadata')
            if not message:
                continue

            headers = self.gmail.get_message_headers(message)
            to_header = headers.get('to', '')

            # Extract email addresses from To header
            email_pattern = r'[\w.+-]+@[\w.-]+\.\w+'
            emails = re.findall(email_pattern, to_header)

            for email in emails:
                # Try to extract display name
                display_name = None
                name_match = re.search(r'"?([^"<]+)"?\s*<' + re.escape(email) + '>', to_header)
                if name_match:
                    display_name = name_match.group(1).strip()

                if self.supabase.upsert_sent_contact(email, display_name):
                    contacts_added += 1

        print(f"  ✓ Added/updated {contacts_added} sent contacts")
        return contacts_added

    def process_inbox(
        self,
        max_messages: int = 50,
        dry_run: bool = False,
        auto_archive: bool = True
    ) -> ArchiveStats:
        """
        Process inbox emails: classify, label, and optionally archive.

        Args:
            max_messages: Maximum messages to process
            dry_run: If True, don't make any changes
            auto_archive: If True, archive sales emails

        Returns:
            ArchiveStats with processing results
        """
        stats = ArchiveStats()

        # Ensure labels exist
        if not dry_run and not self._label_ids:
            self.setup_labels()

        # Load known contacts for classifier
        known_contacts = self.supabase.get_all_sent_contacts()
        self.classifier.set_known_contacts(known_contacts)
        print(f"Loaded {len(known_contacts)} known contacts for classification")

        # Get unread inbox messages
        result = self.gmail.list_messages(
            query='is:unread',
            label_ids=['INBOX'],
            max_results=max_messages
        )

        messages = result.get('messages', [])
        print(f"Found {len(messages)} unread inbox messages to process")

        if not messages:
            print("No messages to process")
            return stats

        for msg_info in messages:
            try:
                # Get full message
                message = self.gmail.get_message(msg_info['id'])
                if not message:
                    stats.errors += 1
                    continue

                headers = self.gmail.get_message_headers(message)
                body = self.gmail.get_message_body(message)
                thread_id = message.get('threadId')

                sender_email = self._extract_email(headers.get('from', ''))
                subject = headers.get('subject', '')

                # Check if part of existing thread (more than 1 message)
                has_thread = self._has_existing_thread(thread_id)

                # Classify the email
                classification = self.classifier.classify_email(
                    message_id=msg_info['id'],
                    sender_email=sender_email,
                    subject=subject,
                    body=body,
                    has_thread=has_thread,
                    headers=headers
                )

                stats.total_processed += 1

                # Print classification result
                action = "WOULD " if dry_run else ""
                self._print_classification(
                    subject, sender_email, classification, action
                )

                if not dry_run:
                    # Store classification in database
                    self._store_classification(
                        classification, thread_id, sender_email, subject
                    )

                    # Apply label and archive based on classification
                    self._apply_actions(
                        msg_info['id'], classification, auto_archive, stats
                    )
                else:
                    # Just count for dry run
                    self._count_classification(classification, stats)

            except Exception as e:
                print(f"  Error processing message: {e}")
                stats.errors += 1

        # Print summary
        self._print_summary(stats, dry_run)

        return stats

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        return match.group().lower() if match else from_header.lower()

    def _has_existing_thread(self, thread_id: str) -> bool:
        """Check if thread has multiple messages."""
        try:
            # This is a simplified check - in production you'd query the thread
            # For now, we'll assume it's a thread if the ID exists
            return bool(thread_id)
        except Exception:
            return False

    def _print_classification(
        self,
        subject: str,
        sender: str,
        result: ClassificationResult,
        action_prefix: str = ""
    ):
        """Print classification result."""
        emoji = {
            'sales_solicitation': '🚫',
            'transactional': '🧾',
            'human_correspondence': '👤',
            'newsletter_subscribed': '📰',
            'automated_notification': '🔔',
        }.get(result.classification, '❓')

        action_str = result.suggested_action.upper()
        conf = f"{result.confidence:.0%}"

        # Truncate subject for display
        subj_display = subject[:50] + '...' if len(subject) > 50 else subject

        print(f"  {emoji} [{result.classification}] ({conf}) {action_prefix}{action_str}")
        print(f"     From: {sender}")
        print(f"     Subject: {subj_display}")
        print(f"     Reason: {result.reasoning}")
        print()

    def _store_classification(
        self,
        result: ClassificationResult,
        thread_id: str,
        sender_email: str,
        subject: str
    ):
        """Store classification result in Supabase."""
        data = {
            'message_id': result.message_id,
            'thread_id': thread_id,
            'sender_email': sender_email,
            'subject': subject[:500],
            'classification': result.classification,
            'confidence': result.confidence,
            'reasoning': result.reasoning[:500] if result.reasoning else None,
            'is_important': result.is_important,
            'action_taken': result.suggested_action,
        }
        self.supabase.store_classification(data)

    def _apply_actions(
        self,
        message_id: str,
        result: ClassificationResult,
        auto_archive: bool,
        stats: ArchiveStats
    ):
        """Apply labels and archive based on classification."""
        classification = result.classification

        if classification == 'sales_solicitation':
            # Apply red Sales/Marketing label
            if 'sales' in self._label_ids:
                self.gmail.apply_label_to_message(
                    message_id, self._label_ids['sales']
                )

            # Archive if enabled
            if auto_archive:
                self.gmail.archive_message(message_id)
                self.gmail.mark_as_read(message_id)

            stats.sales_archived += 1

        elif classification == 'transactional':
            # Apply Receipts label
            if 'receipts' in self._label_ids:
                self.gmail.apply_label_to_message(
                    message_id, self._label_ids['receipts']
                )
            stats.transactional_kept += 1

        elif classification == 'human_correspondence':
            # Apply Human label for real correspondence
            if 'human' in self._label_ids:
                self.gmail.apply_label_to_message(
                    message_id, self._label_ids['human']
                )
            stats.human_kept += 1

        elif classification == 'newsletter_subscribed':
            stats.newsletter_kept += 1

        elif classification == 'automated_notification':
            stats.automated_kept += 1

    def _count_classification(self, result: ClassificationResult, stats: ArchiveStats):
        """Count classification for dry run."""
        classification = result.classification

        if classification == 'sales_solicitation':
            stats.sales_archived += 1
        elif classification == 'transactional':
            stats.transactional_kept += 1
        elif classification == 'human_correspondence':
            stats.human_kept += 1
        elif classification == 'newsletter_subscribed':
            stats.newsletter_kept += 1
        elif classification == 'automated_notification':
            stats.automated_kept += 1

    def _print_summary(self, stats: ArchiveStats, dry_run: bool):
        """Print processing summary."""
        mode = "[DRY RUN] " if dry_run else ""
        print(f"\n{mode}Processing Summary:")
        print(f"  Total processed: {stats.total_processed}")
        print(f"  Sales/Marketing archived: {stats.sales_archived}")
        print(f"  Transactional (receipts): {stats.transactional_kept}")
        print(f"  Human correspondence: {stats.human_kept}")
        print(f"  Newsletters: {stats.newsletter_kept}")
        print(f"  Automated notifications: {stats.automated_kept}")
        print(f"  Errors: {stats.errors}")


def main():
    """CLI entry point for auto-archive."""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-archive sales emails')
    parser.add_argument('--max', type=int, default=50, help='Max messages to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
    parser.add_argument('--no-archive', action='store_true', help='Label only, do not archive')
    parser.add_argument('--setup-labels', action='store_true', help='Only setup labels')
    parser.add_argument('--build-contacts', action='store_true', help='Build sent contacts DB')

    args = parser.parse_args()

    archiver = AutoArchiver()

    if args.setup_labels:
        archiver.setup_labels()
        return

    if args.build_contacts:
        archiver.build_sent_contacts(max_messages=1000)
        return

    stats = archiver.process_inbox(
        max_messages=args.max,
        dry_run=args.dry_run,
        auto_archive=not args.no_archive
    )


if __name__ == '__main__':
    main()
