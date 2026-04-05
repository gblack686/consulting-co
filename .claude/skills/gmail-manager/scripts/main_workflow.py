#!/usr/bin/env python3
"""
Gmail Manager Workflow

Main orchestration script for Gmail management operations.
Provides CLI interface for all Gmail skill capabilities.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)

from scripts.gmail_oauth_handler import GmailOAuth2Handler
from scripts.gmail_client import GmailClient
from scripts.domain_extractor import DomainExtractor, ExtractedContact
from scripts.supabase_gmail_client import SupabaseGmailClient
from scripts.email_summarizer import EmailSummarizer
from scripts.newsletter_manager import NewsletterManager
from scripts.draft_generator import DraftGenerator
from scripts.auto_archive import AutoArchiver
from scripts.digest_generator import DigestGenerator
from scripts.email_classifier import EmailClassifier
from scripts.job_application_tracker import JobApplicationTracker
from scripts.application_classifier import ApplicationClassifier


class GmailManagerWorkflow:
    """Orchestrates Gmail management operations."""

    def __init__(self, credentials_file: str = None, config: Dict = None):
        """
        Initialize workflow.

        Args:
            credentials_file: Path to OAuth credentials JSON
            config: Configuration dict (optional)
        """
        self.config = config or {}

        # Initialize OAuth handler
        creds_file = credentials_file or self.config.get(
            'credentials_file', 'gmail_client_secret.json'
        )
        self.oauth = GmailOAuth2Handler(credentials_file=creds_file)

        # Initialize clients (lazy loaded)
        self._gmail = None
        self._supabase = None
        self._summarizer = None
        self._newsletter_mgr = None
        self._draft_gen = None
        self._archiver = None
        self._digest_gen = None
        self._classifier = None
        self._job_tracker = None
        self._extractor = DomainExtractor()

        # Stats tracking
        self.stats = {
            'messages_processed': 0,
            'contacts_extracted': 0,
            'summaries_generated': 0,
            'drafts_created': 0,
        }

    @property
    def gmail(self) -> GmailClient:
        """Lazy-load Gmail client."""
        if not self._gmail:
            self._gmail = GmailClient(self.oauth)
        return self._gmail

    @property
    def supabase(self) -> SupabaseGmailClient:
        """Lazy-load Supabase client."""
        if not self._supabase:
            self._supabase = SupabaseGmailClient()
        return self._supabase

    @property
    def summarizer(self) -> EmailSummarizer:
        """Lazy-load email summarizer."""
        if not self._summarizer:
            self._summarizer = EmailSummarizer()
        return self._summarizer

    @property
    def newsletter_mgr(self) -> NewsletterManager:
        """Lazy-load newsletter manager."""
        if not self._newsletter_mgr:
            self._newsletter_mgr = NewsletterManager(self.gmail, self.supabase)
        return self._newsletter_mgr

    @property
    def draft_gen(self) -> DraftGenerator:
        """Lazy-load draft generator."""
        if not self._draft_gen:
            self._draft_gen = DraftGenerator(self.gmail)
        return self._draft_gen

    @property
    def archiver(self) -> AutoArchiver:
        """Lazy-load auto-archiver."""
        if not self._archiver:
            self._archiver = AutoArchiver(
                gmail_client=self.gmail,
                classifier=self.classifier,
                supabase_client=self.supabase
            )
        return self._archiver

    @property
    def digest_gen(self) -> DigestGenerator:
        """Lazy-load digest generator."""
        if not self._digest_gen:
            self._digest_gen = DigestGenerator(
                gmail_client=self.gmail,
                supabase_client=self.supabase,
                summarizer=self.summarizer
            )
        return self._digest_gen

    @property
    def classifier(self) -> EmailClassifier:
        """Lazy-load email classifier."""
        if not self._classifier:
            self._classifier = EmailClassifier()
        return self._classifier

    @property
    def job_tracker(self) -> JobApplicationTracker:
        """Lazy-load job application tracker."""
        if not self._job_tracker:
            self._job_tracker = JobApplicationTracker(
                gmail_client=self.gmail,
                supabase_client=self.supabase
            )
        return self._job_tracker

    # =========================================================================
    # Contact Extraction
    # =========================================================================

    def extract_contacts(
        self,
        source: str = 'inbox',
        max_results: int = 500,
        query: str = None
    ) -> Dict[str, Any]:
        """
        Extract unique contacts from inbox or sent mail.

        Args:
            source: 'inbox' or 'sent'
            max_results: Maximum messages to process
            query: Additional Gmail search query

        Returns:
            Dict with extraction stats
        """
        print(f"Extracting contacts from {source}...")

        # Build query
        if source == 'sent':
            label_query = 'in:sent'
        else:
            label_query = 'in:inbox'

        full_query = f"{label_query} {query}" if query else label_query

        # Get messages
        result = self.gmail.list_messages(query=full_query, max_results=max_results)
        messages = result.get('messages', [])

        print(f"Found {len(messages)} messages to process")

        contacts = {}
        domains = {}

        for i, msg_ref in enumerate(messages):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(messages)} messages...")

            message = self.gmail.get_message(msg_ref['id'], format='metadata')
            if not message:
                continue

            # Extract contacts from this message
            msg_contacts = self._extractor.extract_from_message(message, source)

            # Merge with existing contacts
            for email_addr, contact in msg_contacts.items():
                if email_addr in contacts:
                    contacts[email_addr] = self._extractor.merge_contacts(
                        contacts[email_addr], contact
                    )
                else:
                    contacts[email_addr] = contact

            self.stats['messages_processed'] += 1

        # Store contacts in Supabase
        print(f"Storing {len(contacts)} contacts to Supabase...")
        store_stats = self.supabase.upsert_contacts_batch(list(contacts.values()))

        # Extract and store domains
        domains = self._extractor.extract_domains_summary(contacts)
        for domain_data in domains.values():
            self.supabase.upsert_domain(domain_data)

        self.stats['contacts_extracted'] = len(contacts)

        return {
            'source': source,
            'messages_processed': len(messages),
            'contacts_found': len(contacts),
            'domains_found': len(domains),
            'stored': store_stats,
        }

    # =========================================================================
    # Email Summarization
    # =========================================================================

    def summarize_inbox(
        self,
        max_results: int = 50,
        unread_only: bool = True,
        skip_newsletters: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Summarize recent emails.

        Args:
            max_results: Maximum emails to summarize
            unread_only: Only summarize unread emails
            skip_newsletters: Skip detected newsletters

        Returns:
            List of summary objects
        """
        print("Summarizing inbox emails...")

        # Build query
        query_parts = ['in:inbox']
        if unread_only:
            query_parts.append('is:unread')

        query = ' '.join(query_parts)

        result = self.gmail.list_messages(query=query, max_results=max_results)
        messages = result.get('messages', [])

        print(f"Found {len(messages)} messages to process")

        summaries = []

        for i, msg_ref in enumerate(messages):
            message_id = msg_ref['id']

            # Skip if already summarized
            if self.supabase.summary_exists(message_id):
                continue

            message = self.gmail.get_message(message_id)
            if not message:
                continue

            headers = self._get_headers(message)
            body = self.gmail.get_message_body(message)

            # Skip newsletters if requested
            if skip_newsletters:
                if 'list-unsubscribe' in headers:
                    continue

            print(f"  Summarizing: {headers.get('subject', 'No Subject')[:50]}...")

            # Generate summary
            summary_data = self.summarizer.summarize_email(
                subject=headers.get('subject', ''),
                body=body,
                sender=headers.get('from', ''),
            )

            # Store summary
            summary_record = {
                'message_id': message_id,
                'thread_id': message.get('threadId'),
                'subject': headers.get('subject', ''),
                'sender_email': self._extract_email(headers.get('from', '')),
                'sender_name': self._extract_name(headers.get('from', '')),
                'received_at': headers.get('date'),
                'summary': summary_data['summary'],
                'key_points': summary_data['key_points'],
                'action_items': summary_data['action_items'],
                'sentiment': summary_data['sentiment'],
                'category': summary_data['category'],
            }

            self.supabase.store_summary(summary_record)
            summaries.append(summary_record)
            self.stats['summaries_generated'] += 1

            if (i + 1) % 10 == 0:
                print(f"  Generated {len(summaries)} summaries...")

        print(f"Generated {len(summaries)} summaries")
        return summaries

    # =========================================================================
    # Newsletter Management
    # =========================================================================

    def detect_newsletters(self, max_messages: int = 200) -> List[Dict[str, Any]]:
        """Detect newsletter senders in inbox."""
        print("Detecting newsletters...")
        newsletters = self.newsletter_mgr.detect_newsletters(max_messages=max_messages)
        print(f"Found {len(newsletters)} newsletter senders")
        return newsletters

    def block_sender(self, sender: str, action: str = 'archive') -> Dict[str, Any]:
        """Block or auto-archive emails from a sender."""
        print(f"Creating {action} filter for: {sender}")
        result = self.newsletter_mgr.create_block_filter(sender, action=action)
        if result:
            print(f"Filter created: {result.get('id')}")
            return {'success': True, 'filter_id': result.get('id')}
        return {'success': False}

    def unsubscribe(self, message_id: str) -> Dict[str, Any]:
        """Get unsubscribe info for a message."""
        return self.newsletter_mgr.get_unsubscribe_link(message_id)

    # =========================================================================
    # Draft & Send
    # =========================================================================

    def create_draft(
        self,
        to: str,
        topic: str,
        context: str = None,
        tone: str = 'professional'
    ) -> Optional[Dict[str, Any]]:
        """Create an AI-generated email draft."""
        print(f"Generating draft to: {to}")
        draft = self.draft_gen.generate_new_email(
            to=to,
            topic=topic,
            context=context,
            tone=tone
        )
        if draft:
            self.stats['drafts_created'] += 1
            print(f"Draft created: {draft.get('id')}")
        return draft

    def create_reply_draft(
        self,
        message_id: str,
        instructions: str = None,
        tone: str = 'professional'
    ) -> Optional[Dict[str, Any]]:
        """Create an AI-generated reply draft."""
        print(f"Generating reply to message: {message_id}")
        draft = self.draft_gen.generate_reply(
            message_id=message_id,
            instructions=instructions,
            tone=tone
        )
        if draft:
            self.stats['drafts_created'] += 1
            print(f"Reply draft created: {draft.get('id')}")
        return draft

    def send_email(
        self,
        to: str,
        subject: str,
        body: str
    ) -> Optional[Dict[str, Any]]:
        """Send an email."""
        print(f"Sending email to: {to}")
        return self.gmail.send_message(to=to, subject=subject, body=body)

    # =========================================================================
    # Mark as Read
    # =========================================================================

    def mark_as_read(
        self,
        query: str = None,
        message_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Mark messages as read."""
        marked = 0

        if message_ids:
            for msg_id in message_ids:
                if self.gmail.mark_as_read(msg_id):
                    marked += 1
        elif query:
            result = self.gmail.list_messages(query=query, max_results=100)
            for msg in result.get('messages', []):
                if self.gmail.mark_as_read(msg['id']):
                    marked += 1

        print(f"Marked {marked} messages as read")
        return {'marked': marked}

    # =========================================================================
    # Classification & Auto-Archive
    # =========================================================================

    def setup_labels(self) -> Dict[str, str]:
        """Setup Gmail labels with colors for classification."""
        print("Setting up Gmail labels...")
        return self.archiver.setup_labels()

    def build_sent_contacts(self, max_messages: int = 1000) -> int:
        """Build sent contacts database from sent mail."""
        print(f"Building sent contacts (max {max_messages} messages)...")
        return self.archiver.build_sent_contacts(max_messages=max_messages)

    def classify_inbox(
        self,
        max_messages: int = 50,
        dry_run: bool = False,
        auto_archive: bool = True
    ) -> Dict[str, Any]:
        """
        Classify inbox emails and optionally auto-archive sales.

        Args:
            max_messages: Maximum messages to process
            dry_run: If True, preview without changes
            auto_archive: If True, archive sales emails

        Returns:
            Dict with classification stats
        """
        print(f"Classifying inbox (max={max_messages}, dry_run={dry_run}, auto_archive={auto_archive})")
        stats = self.archiver.process_inbox(
            max_messages=max_messages,
            dry_run=dry_run,
            auto_archive=auto_archive
        )
        return {
            'total_processed': stats.total_processed,
            'sales_archived': stats.sales_archived,
            'transactional_kept': stats.transactional_kept,
            'human_kept': stats.human_kept,
            'newsletter_kept': stats.newsletter_kept,
            'automated_kept': stats.automated_kept,
            'errors': stats.errors,
        }

    def send_digest(
        self,
        digest_type: str = 'now',
        preview: bool = False,
        hours_back: int = None
    ) -> bool:
        """
        Generate and send email digest.

        Args:
            digest_type: 'morning', 'afternoon', 'evening', or 'now'
            preview: If True, print preview instead of sending
            hours_back: Override hours to look back

        Returns:
            True if successful
        """
        print(f"Generating {digest_type} digest...")
        return self.digest_gen.send_digest(
            digest_type=digest_type,
            preview=preview,
            hours_back=hours_back
        )

    # =========================================================================
    # Job Application Tracking
    # =========================================================================

    def scan_job_applications(
        self,
        max_messages: int = 500,
        days_back: int = 730,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Scan Gmail for job application emails.

        Args:
            max_messages: Maximum messages to scan
            days_back: Days to look back (default 2 years)
            dry_run: Preview without saving

        Returns:
            Dict with scan statistics
        """
        print(f"Scanning for job applications (last {days_back} days)...")
        stats = self.job_tracker.scan_for_applications(
            max_messages=max_messages,
            days_back=days_back,
            dry_run=dry_run
        )
        return {
            'total_scanned': stats.total_scanned,
            'job_related': stats.job_related,
            'applications_found': stats.applications_found,
            'applications_created': stats.applications_created,
            'contacts_added': stats.contacts_added,
            'interviews_found': stats.interviews_found,
            'errors': stats.errors,
        }

    def get_job_stats(self) -> Dict[str, Any]:
        """Get job application statistics."""
        return self.job_tracker.get_application_stats()

    def list_job_applications(
        self,
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List job applications."""
        return self.job_tracker.list_applications(status=status, limit=limit)

    def get_job_application(self, app_id: int) -> Dict[str, Any]:
        """Get full details for a job application."""
        return self.job_tracker.get_application_details(app_id)

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        db_stats = self.supabase.get_stats()
        return {
            **self.stats,
            **db_stats,
        }

    def print_stats(self):
        """Print statistics summary."""
        stats = self.get_stats()
        print("\n=== Gmail Manager Statistics ===")
        print(f"Total contacts: {stats.get('total_contacts', 0)}")
        print(f"Total domains: {stats.get('total_domains', 0)}")
        print(f"Newsletter contacts: {stats.get('newsletter_contacts', 0)}")
        print(f"Email summaries: {stats.get('total_summaries', 0)}")
        print(f"Session - Messages processed: {stats.get('messages_processed', 0)}")
        print(f"Session - Contacts extracted: {stats.get('contacts_extracted', 0)}")
        print(f"Session - Summaries generated: {stats.get('summaries_generated', 0)}")
        print(f"Session - Drafts created: {stats.get('drafts_created', 0)}")

    # =========================================================================
    # Helpers
    # =========================================================================

    def _get_headers(self, message: Dict) -> Dict[str, str]:
        """Extract headers from message."""
        headers = {}
        payload = message.get('payload', {})
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        return headers

    def _extract_email(self, from_header: str) -> Optional[str]:
        """Extract email address from From header."""
        import re
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        return match.group().lower() if match else None

    def _extract_name(self, from_header: str) -> Optional[str]:
        """Extract display name from From header."""
        import re
        match = re.match(r'"?([^"<]+)"?\s*<', from_header)
        return match.group(1).strip() if match else None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Gmail Manager - Manage your Gmail with AI assistance'
    )

    parser.add_argument(
        '--credentials', '-c',
        default='gmail_client_secret.json',
        help='Path to OAuth credentials JSON file'
    )

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with Gmail')

    # Extract contacts command
    extract_parser = subparsers.add_parser('extract-contacts', help='Extract contacts')
    extract_parser.add_argument(
        '--source', choices=['inbox', 'sent'], default='inbox',
        help='Source to extract from'
    )
    extract_parser.add_argument(
        '--max', type=int, default=500,
        help='Maximum messages to process'
    )
    extract_parser.add_argument('--query', help='Additional search query')

    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize emails')
    summarize_parser.add_argument(
        '--max', type=int, default=50,
        help='Maximum emails to summarize'
    )
    summarize_parser.add_argument(
        '--all', action='store_true',
        help='Include read emails (default: unread only)'
    )
    summarize_parser.add_argument(
        '--include-newsletters', action='store_true',
        help='Include newsletters'
    )

    # Newsletter detection command
    newsletters_parser = subparsers.add_parser('newsletters', help='Manage newsletters')
    newsletters_parser.add_argument(
        '--detect', action='store_true',
        help='Detect newsletter senders'
    )
    newsletters_parser.add_argument('--block', help='Block/archive a sender')
    newsletters_parser.add_argument(
        '--action', choices=['archive', 'trash'], default='archive',
        help='Action for block filter'
    )

    # Create draft command
    draft_parser = subparsers.add_parser('create-draft', help='Create email draft')
    draft_parser.add_argument('--to', required=True, help='Recipient email')
    draft_parser.add_argument('--topic', required=True, help='Email topic/subject')
    draft_parser.add_argument('--context', help='Additional context')
    draft_parser.add_argument(
        '--tone', default='professional',
        choices=['professional', 'casual', 'formal', 'friendly'],
        help='Email tone'
    )

    # Reply draft command
    reply_parser = subparsers.add_parser('reply', help='Create reply draft')
    reply_parser.add_argument('--message-id', required=True, help='Message ID to reply to')
    reply_parser.add_argument('--instructions', help='Reply instructions')
    reply_parser.add_argument('--tone', default='professional')

    # Send command
    send_parser = subparsers.add_parser('send', help='Send an email')
    send_parser.add_argument('--to', required=True, help='Recipient email')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body')

    # Mark as read command
    read_parser = subparsers.add_parser('mark-read', help='Mark messages as read')
    read_parser.add_argument('--query', help='Gmail search query')
    read_parser.add_argument('--ids', nargs='+', help='Specific message IDs')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')

    # Setup labels command
    labels_parser = subparsers.add_parser('setup-labels', help='Create Gmail labels with colors')

    # Build sent contacts command
    contacts_parser = subparsers.add_parser('build-sent-contacts', help='Build sent contacts DB')
    contacts_parser.add_argument(
        '--max', type=int, default=1000,
        help='Maximum sent messages to scan'
    )

    # Classify command
    classify_parser = subparsers.add_parser('classify', help='Classify and auto-archive inbox')
    classify_parser.add_argument(
        '--max', type=int, default=50,
        help='Maximum messages to classify'
    )
    classify_parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview classifications without making changes'
    )
    classify_parser.add_argument(
        '--no-archive', action='store_true',
        help='Label emails but do not archive sales'
    )

    # Digest command
    digest_parser = subparsers.add_parser('digest', help='Generate and send email digest')
    digest_parser.add_argument(
        '--type', default='now',
        choices=['morning', 'afternoon', 'evening', 'now'],
        help='Digest type (determines time range)'
    )
    digest_parser.add_argument(
        '--preview', action='store_true',
        help='Preview digest without sending'
    )
    digest_parser.add_argument(
        '--hours', type=int,
        help='Override hours to look back'
    )

    # Schedule digest command
    schedule_parser = subparsers.add_parser('schedule-digest', help='Setup Windows Task Scheduler')

    # Job application tracking commands
    job_scan_parser = subparsers.add_parser('job-scan', help='Scan for job applications')
    job_scan_parser.add_argument(
        '--max', type=int, default=500,
        help='Maximum messages to scan'
    )
    job_scan_parser.add_argument(
        '--days', type=int, default=730,
        help='Days to look back (default 2 years)'
    )
    job_scan_parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview without saving'
    )

    job_stats_parser = subparsers.add_parser('job-stats', help='Show job application stats')

    job_list_parser = subparsers.add_parser('job-list', help='List job applications')
    job_list_parser.add_argument(
        '--status',
        choices=['applied', 'screening', 'interviewing', 'rejected', 'offer', 'withdrawn', 'ghosted'],
        help='Filter by status'
    )
    job_list_parser.add_argument(
        '--limit', type=int, default=50,
        help='Maximum applications to show'
    )

    job_details_parser = subparsers.add_parser('job-details', help='Show application details')
    job_details_parser.add_argument('--id', type=int, required=True, help='Application ID')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    # Initialize workflow
    workflow = GmailManagerWorkflow(credentials_file=args.credentials)

    # Execute action
    if args.action == 'auth':
        workflow.oauth.authenticate()
        print("Authentication successful!")
        print(f"Token info: {workflow.oauth.get_token_info()}")

    elif args.action == 'extract-contacts':
        result = workflow.extract_contacts(
            source=args.source,
            max_results=args.max,
            query=args.query
        )
        print(json.dumps(result, indent=2))

    elif args.action == 'summarize':
        summaries = workflow.summarize_inbox(
            max_results=args.max,
            unread_only=not args.all,
            skip_newsletters=not args.include_newsletters
        )
        for s in summaries[:5]:  # Print first 5
            print(f"\n--- {s['subject'][:50]} ---")
            print(f"Summary: {s['summary']}")
            if s['action_items']:
                print(f"Actions: {', '.join(s['action_items'])}")

    elif args.action == 'newsletters':
        if args.detect:
            newsletters = workflow.detect_newsletters()
            print("\nDetected Newsletter Senders:")
            for nl in newsletters[:20]:
                print(f"  [{nl['count']} emails] {nl['email']}")
                if nl['unsubscribe_link']:
                    print(f"    Unsubscribe: {nl['unsubscribe_link'][:60]}...")
        elif args.block:
            result = workflow.block_sender(args.block, action=args.action)
            print(json.dumps(result, indent=2))

    elif args.action == 'create-draft':
        draft = workflow.create_draft(
            to=args.to,
            topic=args.topic,
            context=args.context,
            tone=args.tone
        )
        if draft:
            print(f"Draft created! ID: {draft.get('id')}")

    elif args.action == 'reply':
        draft = workflow.create_reply_draft(
            message_id=args.message_id,
            instructions=args.instructions,
            tone=args.tone
        )
        if draft:
            print(f"Reply draft created! ID: {draft.get('id')}")

    elif args.action == 'send':
        result = workflow.send_email(
            to=args.to,
            subject=args.subject,
            body=args.body
        )
        if result:
            print(f"Email sent! ID: {result.get('id')}")

    elif args.action == 'mark-read':
        result = workflow.mark_as_read(
            query=args.query,
            message_ids=args.ids
        )
        print(json.dumps(result, indent=2))

    elif args.action == 'stats':
        workflow.print_stats()

    elif args.action == 'setup-labels':
        labels = workflow.setup_labels()
        print("\nLabels created/verified:")
        for key, label_id in labels.items():
            print(f"  {key}: {label_id}")

    elif args.action == 'build-sent-contacts':
        count = workflow.build_sent_contacts(max_messages=args.max)
        print(f"\nSent contacts built: {count}")

    elif args.action == 'classify':
        result = workflow.classify_inbox(
            max_messages=args.max,
            dry_run=args.dry_run,
            auto_archive=not args.no_archive
        )
        print("\nClassification Results:")
        print(json.dumps(result, indent=2))

    elif args.action == 'digest':
        success = workflow.send_digest(
            digest_type=args.type,
            preview=args.preview,
            hours_back=args.hours
        )
        if success:
            print("Digest operation completed successfully")
        else:
            print("Digest operation failed")

    elif args.action == 'schedule-digest':
        # Generate and run the scheduler setup script
        script_dir = Path(__file__).parent.parent
        setup_script = script_dir / 'setup_scheduler.bat'

        if setup_script.exists():
            print(f"Running scheduler setup: {setup_script}")
            import subprocess
            subprocess.run(['cmd', '/c', str(setup_script)], cwd=str(script_dir))
        else:
            print("Creating scheduler setup script...")
            # Generate the script
            python_exe = sys.executable
            scripts_path = Path(__file__).parent
            runner_script = scripts_path / 'digest_runner.py'

            bat_content = f'''@echo off
echo Setting up Gmail Digest scheduled tasks...

REM Morning digest at 7:00 AM
schtasks /create /tn "Gmail Digest - Morning" /tr "\\"{python_exe}\\" \\"{runner_script}\\" --action classify-and-digest --type morning" /sc daily /st 07:00 /f

REM Afternoon digest at 1:00 PM
schtasks /create /tn "Gmail Digest - Afternoon" /tr "\\"{python_exe}\\" \\"{runner_script}\\" --action classify-and-digest --type afternoon" /sc daily /st 13:00 /f

REM Evening digest at 6:00 PM
schtasks /create /tn "Gmail Digest - Evening" /tr "\\"{python_exe}\\" \\"{runner_script}\\" --action classify-and-digest --type evening" /sc daily /st 18:00 /f

echo.
echo Scheduled tasks created:
schtasks /query /tn "Gmail Digest - Morning"
schtasks /query /tn "Gmail Digest - Afternoon"
schtasks /query /tn "Gmail Digest - Evening"

echo.
echo Done! Gmail digests will run 3x daily.
pause
'''
            with open(setup_script, 'w') as f:
                f.write(bat_content)

            print(f"Created: {setup_script}")
            print("Run this script as Administrator to create scheduled tasks.")
            print(f"\nTo run manually: {setup_script}")

    elif args.action == 'job-scan':
        result = workflow.scan_job_applications(
            max_messages=args.max,
            days_back=args.days,
            dry_run=args.dry_run
        )
        print("\nJob Scan Results:")
        print(json.dumps(result, indent=2))

    elif args.action == 'job-stats':
        stats = workflow.get_job_stats()
        print("\n=== Job Application Statistics ===")
        print(f"Total Applications: {stats.get('total_applications', 0)}")
        print(f"Total Contacts: {stats.get('total_contacts', 0)}")
        print(f"Total Interviews: {stats.get('total_interviews', 0)}")
        print("\nBy Status:")
        for status, count in stats.get('by_status', {}).items():
            if count > 0:
                emoji = {'applied': '📨', 'screening': '🔍', 'interviewing': '📅',
                         'rejected': '❌', 'offer': '🎉', 'withdrawn': '🚫', 'ghosted': '👻'}.get(status, '❓')
                print(f"  {emoji} {status}: {count}")
        print("\nBy Source:")
        for source, count in stats.get('by_source', {}).items():
            print(f"  {source}: {count}")

    elif args.action == 'job-list':
        apps = workflow.list_job_applications(status=args.status, limit=args.limit)
        print(f"\n=== Applications ({len(apps)}) ===")
        for app in apps:
            status_emoji = {'applied': '📨', 'screening': '🔍', 'interviewing': '📅',
                           'rejected': '❌', 'offer': '🎉', 'withdrawn': '🚫', 'ghosted': '👻'}.get(app['status'], '❓')
            print(f"\n{status_emoji} [{app['id']}] {app['company_name']} - {app['job_title']}")
            print(f"   Status: {app['status']} | Emails: {app['total_emails']} | Interviews: {app['total_interviews']}")
            if app.get('applied_at'):
                print(f"   Applied: {app['applied_at'][:10]} | Source: {app.get('application_source', 'unknown')}")

    elif args.action == 'job-details':
        details = workflow.get_job_application(args.id)
        if not details:
            print(f"Application {args.id} not found")
        else:
            app = details['application']
            print(f"\n=== {app['company_name']} - {app['job_title']} ===")
            print(f"Status: {app['status']}")
            print(f"Applied: {app.get('applied_at', 'Unknown')[:10] if app.get('applied_at') else 'Unknown'}")
            print(f"Source: {app.get('application_source', 'Unknown')}")
            print(f"Emails: {app['total_emails']} | Interviews: {app['total_interviews']}")

            if details['contacts']:
                print(f"\n--- Contacts ({len(details['contacts'])}) ---")
                for contact in details['contacts']:
                    print(f"  {contact.get('display_name', 'Unknown')} <{contact['email_address']}>")
                    if contact.get('job_title'):
                        print(f"    Title: {contact['job_title']}")
                    print(f"    Emails: {contact.get('email_count', 0)}")

            if details['interviews']:
                print(f"\n--- Interviews ({len(details['interviews'])}) ---")
                for interview in details['interviews']:
                    print(f"  {interview.get('interview_type', 'Unknown')} - {interview.get('scheduled_at', 'TBD')[:10] if interview.get('scheduled_at') else 'TBD'}")
                    print(f"    Status: {interview.get('status', 'unknown')}")

            if details['correspondence']:
                print(f"\n--- Recent Correspondence ({len(details['correspondence'])}) ---")
                for corr in details['correspondence'][:5]:
                    print(f"  [{corr.get('email_type', 'unknown')}] {corr.get('subject', 'No subject')[:60]}")


if __name__ == '__main__':
    main()
