#!/usr/bin/env python3
"""
Job Application Tracker

Scans Gmail for job application emails and builds a database of:
- Applications (company, role, status)
- Contacts (recruiters, hiring managers)
- Correspondence (all emails per application)
- Interviews (scheduled, completed)
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()

from .gmail_client import GmailClient
from .gmail_oauth_handler import GmailOAuth2Handler
from .application_classifier import ApplicationClassifier, ApplicationEmailResult
from .supabase_gmail_client import SupabaseGmailClient


@dataclass
class ScanStats:
    """Statistics from a job scan."""
    total_scanned: int = 0
    job_related: int = 0
    applications_found: int = 0
    applications_created: int = 0
    applications_updated: int = 0
    contacts_added: int = 0
    interviews_found: int = 0
    errors: int = 0


class JobApplicationTracker:
    """Tracks job applications from Gmail."""

    # Search queries for job-related emails
    JOB_QUERIES = [
        'from:linkedin.com (application OR applied OR job)',
        'from:indeed.com (application OR applied)',
        'from:greenhouse.io',
        'from:lever.co',
        'from:workday.com',
        'subject:(application OR applied OR interview OR "phone screen" OR "offer letter")',
        'subject:(position OR opportunity OR role) from:recruiting',
        'subject:"thank you for applying"',
        'subject:"your application"',
        'subject:"interview" -newsletter -unsubscribe',
    ]

    def __init__(
        self,
        gmail_client: GmailClient = None,
        classifier: ApplicationClassifier = None,
        supabase_client: SupabaseGmailClient = None
    ):
        """Initialize tracker."""
        self.gmail = gmail_client or GmailClient()
        self.classifier = classifier or ApplicationClassifier()
        self.supabase = supabase_client or SupabaseGmailClient()

        # Cache for applications by (company, job_title)
        self._app_cache: Dict[Tuple[str, str], int] = {}

    def scan_for_applications(
        self,
        max_messages: int = 500,
        days_back: int = 730,  # 2 years
        dry_run: bool = False
    ) -> ScanStats:
        """
        Scan Gmail for job application emails.

        Args:
            max_messages: Maximum messages to scan
            days_back: How many days back to search
            dry_run: If True, don't write to database

        Returns:
            ScanStats with scan results
        """
        stats = ScanStats()

        # Build date filter
        after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

        print(f"Scanning for job applications (last {days_back} days, max {max_messages})...")

        # Collect all message IDs from various queries
        all_message_ids = set()

        for query in self.JOB_QUERIES:
            full_query = f"{query} after:{after_date}"
            print(f"  Query: {query[:50]}...")

            try:
                result = self.gmail.list_messages(
                    query=full_query,
                    max_results=min(200, max_messages)
                )
                messages = result.get('messages', [])
                for msg in messages:
                    all_message_ids.add(msg['id'])
            except Exception as e:
                print(f"    Error: {e}")
                stats.errors += 1

        print(f"Found {len(all_message_ids)} potential job emails")

        # Process each message
        processed = 0
        for msg_id in all_message_ids:
            if processed >= max_messages:
                break

            processed += 1
            stats.total_scanned += 1

            if processed % 50 == 0:
                print(f"  Processed {processed}/{len(all_message_ids)}...")

            try:
                # Get message
                message = self.gmail.get_message(msg_id)
                if not message:
                    continue

                headers = self.gmail.get_message_headers(message)
                body = self.gmail.get_message_body(message)

                sender_email = self._extract_email(headers.get('from', ''))
                subject = headers.get('subject', '')

                # Classify
                result = self.classifier.classify_email(
                    message_id=msg_id,
                    sender_email=sender_email,
                    subject=subject,
                    body=body,
                    headers=headers
                )

                if not result.is_job_related:
                    continue

                stats.job_related += 1

                # Print classification
                self._print_result(result, subject)

                if not dry_run:
                    # Process and store
                    self._process_job_email(result, message, headers, stats)

            except Exception as e:
                print(f"    Error processing {msg_id}: {e}")
                stats.errors += 1

        # Print summary
        self._print_summary(stats, dry_run)

        return stats

    def _process_job_email(
        self,
        result: ApplicationEmailResult,
        message: Dict,
        headers: Dict[str, str],
        stats: ScanStats
    ):
        """Process a classified job email and store in database."""

        # Skip if no company or job title extracted
        if not result.company_name:
            return

        # Get or create application
        app_id = self._get_or_create_application(result, headers, stats)

        if not app_id:
            return

        # Store correspondence
        self._store_correspondence(app_id, result, message, headers)

        # Store contact if we have info
        if result.contact_name or result.contact_email:
            self._store_contact(app_id, result, stats)

        # Store interview if this is an interview invite
        if result.email_type == 'interview_invite':
            self._store_interview(app_id, result, stats)

        # Update application status based on email type
        self._update_application_status(app_id, result)

    def _get_or_create_application(
        self,
        result: ApplicationEmailResult,
        headers: Dict[str, str],
        stats: ScanStats
    ) -> Optional[int]:
        """Get existing application or create new one."""

        company = result.company_name.strip()
        job_title = result.job_title or 'Unknown Position'

        # Check cache first
        cache_key = (company.lower(), job_title.lower())
        if cache_key in self._app_cache:
            return self._app_cache[cache_key]

        # Check database
        existing = self._find_application(company, job_title)
        if existing:
            self._app_cache[cache_key] = existing['id']
            stats.applications_updated += 1
            return existing['id']

        # Create new application
        email_date = self._parse_date(headers.get('date', ''))

        app_data = {
            'company_name': company,
            'company_domain': self._extract_domain(result.contact_email) if result.contact_email else None,
            'job_title': job_title,
            'job_id': result.job_id,
            'application_source': result.source or 'unknown',
            'applied_at': email_date.isoformat() if email_date else None,
            'status': result.inferred_status or 'applied',
            'last_activity_at': email_date.isoformat() if email_date else datetime.utcnow().isoformat(),
            'total_emails': 1,
        }

        app_id = self._create_application(app_data)
        if app_id:
            self._app_cache[cache_key] = app_id
            stats.applications_created += 1
            stats.applications_found += 1
            print(f"    ✓ New application: {company} - {job_title}")

        return app_id

    def _find_application(self, company: str, job_title: str) -> Optional[Dict]:
        """Find existing application by company and title."""
        try:
            result = self.supabase.client.table("gmail_job_applications").select("*").ilike(
                "company_name", f"%{company}%"
            ).ilike(
                "job_title", f"%{job_title}%"
            ).limit(1).execute()

            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error finding application: {e}")
            return None

    def _create_application(self, app_data: Dict) -> Optional[int]:
        """Create new application in database."""
        try:
            result = self.supabase.client.table("gmail_job_applications").insert(app_data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Error creating application: {e}")
            return None

    def _store_correspondence(
        self,
        app_id: int,
        result: ApplicationEmailResult,
        message: Dict,
        headers: Dict[str, str]
    ):
        """Store email correspondence for an application."""
        try:
            # Check if already stored
            existing = self.supabase.client.table("gmail_job_correspondence").select("id").eq(
                "message_id", result.message_id
            ).execute()

            if existing.data:
                return

            email_date = self._parse_date(headers.get('date', ''))

            corr_data = {
                'application_id': app_id,
                'message_id': result.message_id,
                'thread_id': message.get('threadId'),
                'subject': headers.get('subject', '')[:500],
                'sender_email': result.contact_email,
                'email_date': email_date.isoformat() if email_date else None,
                'direction': 'inbound',  # Could enhance to detect outbound
                'email_type': result.email_type,
                'extracted_data': {
                    'company': result.company_name,
                    'job_title': result.job_title,
                    'confidence': result.confidence,
                }
            }

            self.supabase.client.table("gmail_job_correspondence").insert(corr_data).execute()

            # Update email count on application
            self.supabase.client.table("gmail_job_applications").update({
                'total_emails': self.supabase.client.table("gmail_job_correspondence").select(
                    "id", count="exact"
                ).eq("application_id", app_id).execute().count or 1,
                'last_activity_at': email_date.isoformat() if email_date else datetime.utcnow().isoformat()
            }).eq("id", app_id).execute()

        except Exception as e:
            print(f"Error storing correspondence: {e}")

    def _store_contact(self, app_id: int, result: ApplicationEmailResult, stats: ScanStats):
        """Store contact information for an application."""
        try:
            if not result.contact_email:
                return

            # Check if contact exists
            existing = self.supabase.client.table("gmail_job_contacts").select("id").eq(
                "application_id", app_id
            ).eq(
                "email_address", result.contact_email.lower()
            ).execute()

            if existing.data:
                # Update last contact
                self.supabase.client.table("gmail_job_contacts").update({
                    'last_contact_at': datetime.utcnow().isoformat(),
                    'email_count': existing.data[0].get('email_count', 0) + 1
                }).eq("id", existing.data[0]['id']).execute()
                return

            # Create new contact
            contact_data = {
                'application_id': app_id,
                'email_address': result.contact_email.lower(),
                'display_name': result.contact_name,
                'job_title': result.contact_title,
                'phone': result.contact_phone,
                'first_contact_at': datetime.utcnow().isoformat(),
                'last_contact_at': datetime.utcnow().isoformat(),
                'email_count': 1,
            }

            self.supabase.client.table("gmail_job_contacts").insert(contact_data).execute()
            stats.contacts_added += 1

        except Exception as e:
            print(f"Error storing contact: {e}")

    def _store_interview(self, app_id: int, result: ApplicationEmailResult, stats: ScanStats):
        """Store interview information."""
        try:
            interview_data = {
                'application_id': app_id,
                'interview_type': result.interview_type or 'unknown',
                'scheduled_at': result.interview_date,
                'interviewer_names': result.interviewer_names or [],
                'status': 'scheduled',
                'source_message_id': result.message_id,
            }

            self.supabase.client.table("gmail_job_interviews").insert(interview_data).execute()
            stats.interviews_found += 1

            # Update interview count on application
            self.supabase.client.table("gmail_job_applications").update({
                'total_interviews': self.supabase.client.table("gmail_job_interviews").select(
                    "id", count="exact"
                ).eq("application_id", app_id).execute().count or 1,
                'status': 'interviewing'
            }).eq("id", app_id).execute()

        except Exception as e:
            print(f"Error storing interview: {e}")

    def _update_application_status(self, app_id: int, result: ApplicationEmailResult):
        """Update application status based on email type."""
        status_map = {
            'rejection': 'rejected',
            'offer': 'offer',
            'interview_invite': 'interviewing',
        }

        new_status = status_map.get(result.email_type)
        if new_status:
            try:
                self.supabase.client.table("gmail_job_applications").update({
                    'status': new_status,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq("id", app_id).execute()
            except Exception as e:
                print(f"Error updating status: {e}")

    def get_application_stats(self) -> Dict[str, Any]:
        """Get overall application statistics."""
        try:
            # Total applications
            total = self.supabase.client.table("gmail_job_applications").select(
                "id", count="exact"
            ).execute().count or 0

            # By status
            statuses = {}
            for status in ['applied', 'screening', 'interviewing', 'rejected', 'offer', 'withdrawn', 'ghosted']:
                count = self.supabase.client.table("gmail_job_applications").select(
                    "id", count="exact"
                ).eq("status", status).execute().count or 0
                statuses[status] = count

            # Total contacts
            contacts = self.supabase.client.table("gmail_job_contacts").select(
                "id", count="exact"
            ).execute().count or 0

            # Total interviews
            interviews = self.supabase.client.table("gmail_job_interviews").select(
                "id", count="exact"
            ).execute().count or 0

            # By source
            sources = {}
            for source in ['linkedin', 'indeed', 'direct', 'recruiter', 'greenhouse', 'lever']:
                count = self.supabase.client.table("gmail_job_applications").select(
                    "id", count="exact"
                ).eq("application_source", source).execute().count or 0
                if count > 0:
                    sources[source] = count

            return {
                'total_applications': total,
                'by_status': statuses,
                'total_contacts': contacts,
                'total_interviews': interviews,
                'by_source': sources,
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def list_applications(
        self,
        status: str = None,
        limit: int = 50,
        order_by: str = 'applied_at'
    ) -> List[Dict[str, Any]]:
        """List applications with optional filters."""
        try:
            query = self.supabase.client.table("gmail_job_applications").select("*")

            if status:
                query = query.eq("status", status)

            query = query.order(order_by, desc=True).limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error listing applications: {e}")
            return []

    def get_application_details(self, app_id: int) -> Dict[str, Any]:
        """Get full details for an application including contacts and correspondence."""
        try:
            # Get application
            app = self.supabase.client.table("gmail_job_applications").select("*").eq(
                "id", app_id
            ).execute().data

            if not app:
                return {}

            app = app[0]

            # Get contacts
            contacts = self.supabase.client.table("gmail_job_contacts").select("*").eq(
                "application_id", app_id
            ).execute().data or []

            # Get correspondence
            correspondence = self.supabase.client.table("gmail_job_correspondence").select("*").eq(
                "application_id", app_id
            ).order("email_date", desc=True).execute().data or []

            # Get interviews
            interviews = self.supabase.client.table("gmail_job_interviews").select("*").eq(
                "application_id", app_id
            ).order("scheduled_at", desc=True).execute().data or []

            return {
                'application': app,
                'contacts': contacts,
                'correspondence': correspondence,
                'interviews': interviews,
            }
        except Exception as e:
            print(f"Error getting application details: {e}")
            return {}

    def _extract_email(self, from_header: str) -> str:
        """Extract email from From header."""
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        return match.group().lower() if match else from_header.lower()

    def _extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address."""
        if not email or '@' not in email:
            return None
        return email.split('@')[1].lower()

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string."""
        if not date_str:
            return None
        try:
            # Try common formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def _print_result(self, result: ApplicationEmailResult, subject: str):
        """Print classification result."""
        emoji = {
            'application_confirm': '📨',
            'rejection': '❌',
            'interview_invite': '📅',
            'recruiter_outreach': '👋',
            'offer': '🎉',
            'general_job': '💼',
        }.get(result.email_type, '📧')

        subj_short = subject[:50] + '...' if len(subject) > 50 else subject
        company = result.company_name or 'Unknown'
        job = result.job_title or 'Unknown'

        print(f"  {emoji} [{result.email_type}] {company} - {job}")
        print(f"      Subject: {subj_short}")

    def _print_summary(self, stats: ScanStats, dry_run: bool):
        """Print scan summary."""
        mode = "[DRY RUN] " if dry_run else ""
        print(f"\n{mode}Job Application Scan Summary:")
        print(f"  Total scanned: {stats.total_scanned}")
        print(f"  Job-related emails: {stats.job_related}")
        print(f"  Applications found: {stats.applications_found}")
        print(f"  New applications: {stats.applications_created}")
        print(f"  Updated applications: {stats.applications_updated}")
        print(f"  Contacts added: {stats.contacts_added}")
        print(f"  Interviews found: {stats.interviews_found}")
        print(f"  Errors: {stats.errors}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Track job applications from Gmail')
    parser.add_argument('--scan', action='store_true', help='Scan for applications')
    parser.add_argument('--max', type=int, default=500, help='Max messages to scan')
    parser.add_argument('--days', type=int, default=730, help='Days to look back')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--stats', action='store_true', help='Show application stats')
    parser.add_argument('--list', action='store_true', help='List applications')
    parser.add_argument('--status', help='Filter by status')

    args = parser.parse_args()

    tracker = JobApplicationTracker()

    if args.scan:
        stats = tracker.scan_for_applications(
            max_messages=args.max,
            days_back=args.days,
            dry_run=args.dry_run
        )

    elif args.stats:
        stats = tracker.get_application_stats()
        print("\n=== Job Application Statistics ===")
        print(f"Total Applications: {stats.get('total_applications', 0)}")
        print(f"Total Contacts: {stats.get('total_contacts', 0)}")
        print(f"Total Interviews: {stats.get('total_interviews', 0)}")
        print("\nBy Status:")
        for status, count in stats.get('by_status', {}).items():
            if count > 0:
                print(f"  {status}: {count}")
        print("\nBy Source:")
        for source, count in stats.get('by_source', {}).items():
            print(f"  {source}: {count}")

    elif args.list:
        apps = tracker.list_applications(status=args.status)
        print(f"\n=== Applications ({len(apps)}) ===")
        for app in apps:
            status_emoji = {
                'applied': '📨',
                'screening': '🔍',
                'interviewing': '📅',
                'rejected': '❌',
                'offer': '🎉',
                'withdrawn': '🚫',
                'ghosted': '👻',
            }.get(app['status'], '❓')

            print(f"{status_emoji} {app['company_name']} - {app['job_title']}")
            print(f"   Status: {app['status']} | Emails: {app['total_emails']} | Interviews: {app['total_interviews']}")
            if app.get('applied_at'):
                print(f"   Applied: {app['applied_at'][:10]}")
            print()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
