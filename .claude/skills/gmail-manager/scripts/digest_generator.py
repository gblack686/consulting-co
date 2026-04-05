#!/usr/bin/env python3
"""
Email Digest Generator

Generates and sends HTML email digests summarizing inbox activity,
including important emails and auto-archived sales counts.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .gmail_client import GmailClient
from .email_summarizer import EmailSummarizer
from .supabase_gmail_client import SupabaseGmailClient


@dataclass
class DigestStats:
    """Statistics for digest."""
    total_emails: int = 0
    important_count: int = 0
    sales_archived: int = 0
    receipts_count: int = 0
    human_count: int = 0
    newsletter_count: int = 0


class DigestGenerator:
    """Generate and send email digests."""

    # Digest schedule (hours since midnight)
    SCHEDULE = {
        'morning': 7,
        'afternoon': 13,
        'evening': 18,
    }

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Digest - {digest_type}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a73e8;
            font-size: 24px;
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: #666;
            font-size: 14px;
            margin-bottom: 24px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }}
        .stat-box {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #1a73e8;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .stat-box.sales {{
            background: #fef2f2;
        }}
        .stat-box.sales .stat-number {{
            color: #dc2626;
        }}
        .stat-box.important {{
            background: #f0fdf4;
        }}
        .stat-box.important .stat-number {{
            color: #16a34a;
        }}
        .section {{
            margin-top: 24px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
            margin-bottom: 16px;
        }}
        .email-item {{
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            background: #f8f9fa;
        }}
        .email-item.important {{
            border-left: 4px solid #16a34a;
        }}
        .email-item.receipt {{
            border-left: 4px solid #2563eb;
        }}
        .email-item.human {{
            border-left: 4px solid #f59e0b;
        }}
        .email-from {{
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }}
        .email-subject {{
            color: #666;
            font-size: 13px;
            margin-top: 4px;
        }}
        .email-summary {{
            color: #888;
            font-size: 12px;
            margin-top: 8px;
            font-style: italic;
        }}
        .no-emails {{
            text-align: center;
            color: #666;
            padding: 24px;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #888;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📬 {digest_type} Email Digest</h1>
        <div class="subtitle">
            {date_range}
        </div>

        <div class="stats-grid">
            <div class="stat-box important">
                <div class="stat-number">{important_count}</div>
                <div class="stat-label">Important</div>
            </div>
            <div class="stat-box sales">
                <div class="stat-number">{sales_archived}</div>
                <div class="stat-label">Sales Archived</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{receipts_count}</div>
                <div class="stat-label">Receipts</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{human_count}</div>
                <div class="stat-label">From People</div>
            </div>
        </div>

        {important_section}

        {receipts_section}

        {human_section}

        <div class="footer">
            Generated by Gmail Manager • {timestamp}
        </div>
    </div>
</body>
</html>
"""

    EMAIL_ITEM_TEMPLATE = """
        <div class="email-item {item_class}">
            <div class="email-from">{sender}</div>
            <div class="email-subject">{subject}</div>
            {summary_html}
        </div>
"""

    SECTION_TEMPLATE = """
        <div class="section">
            <div class="section-title">{title}</div>
            {items}
        </div>
"""

    def __init__(
        self,
        gmail_client: GmailClient = None,
        supabase_client: SupabaseGmailClient = None,
        summarizer: EmailSummarizer = None,
        recipient_email: str = None
    ):
        """
        Initialize digest generator.

        Args:
            gmail_client: Gmail API client
            supabase_client: Supabase storage client
            summarizer: Email summarizer
            recipient_email: Email address to send digest to
        """
        self.gmail = gmail_client or GmailClient()
        self.supabase = supabase_client or SupabaseGmailClient()
        self.summarizer = summarizer or EmailSummarizer()
        self.recipient_email = recipient_email or os.getenv('DIGEST_RECIPIENT_EMAIL', 'gblack686@gmail.com')

    def generate_digest(
        self,
        digest_type: str = 'now',
        hours_back: int = None,
        include_summaries: bool = True
    ) -> Dict[str, Any]:
        """
        Generate digest data.

        Args:
            digest_type: 'morning', 'afternoon', 'evening', or 'now'
            hours_back: Hours to look back (auto-calculated if not provided)
            include_summaries: Whether to generate AI summaries

        Returns:
            Dict with digest data and HTML content
        """
        # Calculate time range
        if hours_back is None:
            hours_back = self._calculate_hours_back(digest_type)

        since = datetime.utcnow() - timedelta(hours=hours_back)

        # Get classifications from this period
        classifications = self.supabase.get_classifications(
            since_hours=hours_back,
            limit=500
        )

        # Categorize
        important_emails = []
        receipt_emails = []
        human_emails = []
        stats = DigestStats()

        for cls in classifications:
            stats.total_emails += 1
            classification = cls.get('classification', 'unknown')

            if classification == 'sales_solicitation':
                stats.sales_archived += 1
            elif classification == 'transactional':
                stats.receipts_count += 1
                receipt_emails.append(cls)
            elif classification == 'human_correspondence':
                stats.human_count += 1
                human_emails.append(cls)
                # Human emails are always important
                important_emails.append(cls)
            elif classification == 'newsletter_subscribed':
                stats.newsletter_count += 1

            if cls.get('is_important'):
                stats.important_count += 1
                if cls not in important_emails:
                    important_emails.append(cls)

        # Generate HTML
        html = self._generate_html(
            digest_type=digest_type,
            stats=stats,
            important_emails=important_emails[:10],  # Top 10
            receipt_emails=receipt_emails[:5],
            human_emails=human_emails[:10],
            hours_back=hours_back,
            include_summaries=include_summaries
        )

        return {
            'digest_type': digest_type,
            'html': html,
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat(),
            'hours_back': hours_back,
            'email_count': stats.total_emails,
        }

    def send_digest(
        self,
        digest_type: str = 'now',
        preview: bool = False,
        hours_back: int = None
    ) -> bool:
        """
        Generate and send digest email.

        Args:
            digest_type: Type of digest
            preview: If True, print HTML instead of sending
            hours_back: Hours to look back

        Returns:
            True if successful
        """
        # Generate digest
        digest_data = self.generate_digest(
            digest_type=digest_type,
            hours_back=hours_back
        )

        if preview:
            print("\n=== DIGEST PREVIEW ===\n")
            print(f"Type: {digest_type}")
            print(f"Recipient: {self.recipient_email}")
            print(f"Stats: {digest_data['stats']}")
            print("\n--- HTML Content ---\n")
            print(digest_data['html'][:2000] + "..." if len(digest_data['html']) > 2000 else digest_data['html'])
            return True

        # Create digest log entry
        log_id = self.supabase.create_digest_log(
            digest_type=digest_type,
            recipient_email=self.recipient_email,
            emails_summarized=digest_data['stats'].total_emails,
            important_count=digest_data['stats'].important_count,
            sales_archived_count=digest_data['stats'].sales_archived
        )

        # Send email
        subject = self._get_subject(digest_type, digest_data['stats'])

        sent = self.gmail.send_message(
            to=self.recipient_email,
            subject=subject,
            body=digest_data['html'],
            html=True
        )

        if sent:
            print(f"✓ Digest sent to {self.recipient_email}")
            if log_id:
                self.supabase.update_digest_log(
                    log_id, 'sent', datetime.utcnow()
                )
            return True
        else:
            print(f"✗ Failed to send digest")
            if log_id:
                self.supabase.update_digest_log(log_id, 'failed')
            return False

    def _calculate_hours_back(self, digest_type: str) -> int:
        """Calculate hours to look back based on digest type."""
        if digest_type == 'morning':
            # Look back to evening before (13 hours: 6pm to 7am)
            return 13
        elif digest_type == 'afternoon':
            # Look back to morning (6 hours: 7am to 1pm)
            return 6
        elif digest_type == 'evening':
            # Look back to afternoon (5 hours: 1pm to 6pm)
            return 5
        else:
            # 'now' - look back 8 hours
            return 8

    def _generate_html(
        self,
        digest_type: str,
        stats: DigestStats,
        important_emails: List[Dict],
        receipt_emails: List[Dict],
        human_emails: List[Dict],
        hours_back: int,
        include_summaries: bool
    ) -> str:
        """Generate HTML digest content."""

        # Build sections
        important_section = self._build_section(
            "⭐ Important Emails",
            important_emails,
            "important",
            include_summaries
        ) if important_emails else ""

        receipts_section = self._build_section(
            "🧾 Receipts & Orders",
            receipt_emails,
            "receipt",
            include_summaries
        ) if receipt_emails else ""

        human_section = self._build_section(
            "👤 From Real People",
            human_emails,
            "human",
            include_summaries
        ) if human_emails else ""

        # If no emails at all
        if not important_section and not receipts_section and not human_section:
            important_section = '<div class="no-emails">📭 No important emails in this period</div>'

        # Format date range
        now = datetime.now()
        since = now - timedelta(hours=hours_back)
        date_range = f"{since.strftime('%b %d, %I:%M %p')} - {now.strftime('%I:%M %p')}"

        # Build HTML
        html = self.HTML_TEMPLATE.format(
            digest_type=digest_type.title(),
            date_range=date_range,
            important_count=stats.important_count,
            sales_archived=stats.sales_archived,
            receipts_count=stats.receipts_count,
            human_count=stats.human_count,
            important_section=important_section,
            receipts_section=receipts_section,
            human_section=human_section,
            timestamp=now.strftime('%Y-%m-%d %H:%M')
        )

        return html

    def _build_section(
        self,
        title: str,
        emails: List[Dict],
        item_class: str,
        include_summaries: bool
    ) -> str:
        """Build an HTML section for emails."""
        items_html = ""

        for email in emails:
            summary_html = ""
            if include_summaries and email.get('reasoning'):
                summary_html = f'<div class="email-summary">{email.get("reasoning", "")}</div>'

            items_html += self.EMAIL_ITEM_TEMPLATE.format(
                item_class=item_class,
                sender=email.get('sender_email', 'Unknown'),
                subject=email.get('subject', 'No Subject')[:80],
                summary_html=summary_html
            )

        return self.SECTION_TEMPLATE.format(
            title=title,
            items=items_html
        )

    def _get_subject(self, digest_type: str, stats: DigestStats) -> str:
        """Generate email subject line."""
        type_emoji = {
            'morning': '🌅',
            'afternoon': '☀️',
            'evening': '🌙',
            'now': '📬'
        }.get(digest_type, '📬')

        important_text = f"{stats.important_count} important" if stats.important_count else "No important"
        sales_text = f"{stats.sales_archived} archived" if stats.sales_archived else ""

        if sales_text:
            return f"{type_emoji} {digest_type.title()} Digest: {important_text}, {sales_text}"
        return f"{type_emoji} {digest_type.title()} Digest: {important_text}"


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate and send email digest')
    parser.add_argument('--type', default='now', choices=['morning', 'afternoon', 'evening', 'now'])
    parser.add_argument('--preview', action='store_true', help='Preview without sending')
    parser.add_argument('--hours', type=int, help='Hours to look back')
    parser.add_argument('--to', help='Override recipient email')

    args = parser.parse_args()

    generator = DigestGenerator(
        recipient_email=args.to if args.to else None
    )

    generator.send_digest(
        digest_type=args.type,
        preview=args.preview,
        hours_back=args.hours
    )


if __name__ == '__main__':
    main()
