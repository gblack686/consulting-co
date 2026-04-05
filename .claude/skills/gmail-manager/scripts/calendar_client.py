#!/usr/bin/env python3
"""
Google Calendar Client for Interview Tracking

Fetches calendar events to identify actual interviews and sync with job application data.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from googleapiclient.discovery import build
from gmail_oauth_handler import GmailOAuth2Handler


@dataclass
class InterviewEvent:
    """Represents a calendar interview event."""
    event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    company_name: Optional[str] = None
    attendees: List[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    interview_type: Optional[str] = None  # phone, video, onsite, technical, etc.

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class CalendarClient:
    """Client for Google Calendar API focused on interview tracking."""

    # Keywords that indicate an interview
    INTERVIEW_KEYWORDS = [
        'interview', 'phone screen', 'technical', 'onsite', 'hiring',
        'recruiter call', 'intro call', 'meet the team', 'panel',
        'behavioral', 'case study', 'coding', 'system design',
        'final round', 'offer call', 'debrief'
    ]

    # Patterns to extract company names from event titles
    COMPANY_PATTERNS = [
        r'(?:interview|call|screen|chat)\s+(?:with|@|at)\s+(.+?)(?:\s*[-–—]|\s*$)',
        r'(.+?)\s+(?:interview|phone screen|technical|onsite)',
        r'(.+?)\s*[-–—:]\s*(?:interview|call|screen)',
        r'(?:Re:|Fwd:)?\s*(.+?)\s+Interview',
    ]

    def __init__(self, credentials_file: str = None):
        """Initialize Calendar client."""
        if credentials_file:
            self.oauth_handler = GmailOAuth2Handler(credentials_file=credentials_file)
        else:
            self.oauth_handler = GmailOAuth2Handler()

        self.service = None

    def connect(self) -> bool:
        """Connect to Google Calendar API."""
        try:
            creds = self.oauth_handler.authenticate()
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Failed to connect to Calendar API: {e}")
            return False

    def get_interviews(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        calendar_id: str = 'primary'
    ) -> List[InterviewEvent]:
        """
        Fetch interview events from calendar.

        Args:
            start_date: Start of date range (default: 2 years ago)
            end_date: End of date range (default: today + 30 days)
            calendar_id: Calendar to search (default: primary)

        Returns:
            List of InterviewEvent objects
        """
        if not self.service:
            if not self.connect():
                return []

        # Default date range: 2 years ago to 30 days from now
        if start_date is None:
            start_date = datetime.now() - timedelta(days=730)
        if end_date is None:
            end_date = datetime.now() + timedelta(days=30)

        interviews = []
        page_token = None

        while True:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=250,
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                if self._is_interview(event):
                    interview = self._parse_event(event)
                    if interview:
                        interviews.append(interview)

            page_token = events_result.get('nextPageToken')
            if not page_token:
                break

        return interviews

    def _is_interview(self, event: Dict[str, Any]) -> bool:
        """Check if an event is likely an interview."""
        title = event.get('summary', '').lower()
        description = event.get('description', '').lower()

        # Check title and description for interview keywords
        text = f"{title} {description}"

        for keyword in self.INTERVIEW_KEYWORDS:
            if keyword in text:
                return True

        return False

    def _parse_event(self, event: Dict[str, Any]) -> Optional[InterviewEvent]:
        """Parse a calendar event into an InterviewEvent."""
        try:
            title = event.get('summary', 'Unknown')

            # Parse start/end times
            start = event.get('start', {})
            end = event.get('end', {})

            start_time = self._parse_datetime(start)
            end_time = self._parse_datetime(end)

            if not start_time:
                return None

            # Extract attendees
            attendees = []
            for attendee in event.get('attendees', []):
                email = attendee.get('email', '')
                if email and not email.endswith('calendar.google.com'):
                    attendees.append(email)

            # Extract meeting link
            meeting_link = None
            if event.get('hangoutLink'):
                meeting_link = event['hangoutLink']
            elif event.get('conferenceData', {}).get('entryPoints'):
                for entry in event['conferenceData']['entryPoints']:
                    if entry.get('entryPointType') == 'video':
                        meeting_link = entry.get('uri')
                        break

            # Try to extract company name
            company_name = self._extract_company(title, attendees, event.get('description', ''))

            # Determine interview type
            interview_type = self._determine_interview_type(title, event.get('description', ''))

            return InterviewEvent(
                event_id=event.get('id', ''),
                title=title,
                start_time=start_time,
                end_time=end_time,
                company_name=company_name,
                attendees=attendees,
                location=event.get('location'),
                description=event.get('description'),
                meeting_link=meeting_link,
                interview_type=interview_type
            )
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None

    def _parse_datetime(self, dt_dict: Dict[str, str]) -> Optional[datetime]:
        """Parse datetime from Google Calendar format."""
        if 'dateTime' in dt_dict:
            # Has time component
            dt_str = dt_dict['dateTime']
            # Remove timezone for parsing
            if '+' in dt_str:
                dt_str = dt_str[:dt_str.rfind('+')]
            elif dt_str.endswith('Z'):
                dt_str = dt_str[:-1]
            try:
                return datetime.fromisoformat(dt_str)
            except:
                return None
        elif 'date' in dt_dict:
            # All-day event
            try:
                return datetime.strptime(dt_dict['date'], '%Y-%m-%d')
            except:
                return None
        return None

    def _extract_company(
        self,
        title: str,
        attendees: List[str],
        description: str
    ) -> Optional[str]:
        """Try to extract company name from event details."""
        # Try patterns on title
        for pattern in self.COMPANY_PATTERNS:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up common prefixes/suffixes
                company = re.sub(r'^(Re:|Fwd:|FW:)\s*', '', company, flags=re.IGNORECASE)
                company = company.strip(' -–—:')
                if company and len(company) > 2:
                    return company

        # Try to extract from attendee domains
        for email in attendees:
            if '@' in email:
                domain = email.split('@')[1]
                # Skip common email providers
                if domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']:
                    # Convert domain to company name
                    company = domain.split('.')[0].title()
                    return company

        return None

    def _determine_interview_type(self, title: str, description: str) -> str:
        """Determine the type of interview from title/description."""
        text = f"{title} {description}".lower()

        if 'phone screen' in text or 'phone call' in text:
            return 'phone_screen'
        elif 'technical' in text or 'coding' in text or 'system design' in text:
            return 'technical'
        elif 'onsite' in text or 'on-site' in text or 'in-person' in text:
            return 'onsite'
        elif 'panel' in text:
            return 'panel'
        elif 'final' in text:
            return 'final_round'
        elif 'behavioral' in text or 'culture' in text:
            return 'behavioral'
        elif 'hiring manager' in text or 'meet the team' in text:
            return 'hiring_manager'
        elif 'recruiter' in text or 'intro' in text:
            return 'recruiter_screen'
        else:
            return 'interview'

    def get_interviews_by_company(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, List[InterviewEvent]]:
        """
        Get interviews grouped by company.

        Returns:
            Dict mapping company names to lists of interviews
        """
        interviews = self.get_interviews(start_date, end_date)

        by_company = {}
        for interview in interviews:
            company = interview.company_name or 'Unknown'
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(interview)

        return by_company

    def get_interview_summary(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Get a summary of all interviews.

        Returns:
            Summary dict with counts, companies, types, etc.
        """
        interviews = self.get_interviews(start_date, end_date)

        companies = set()
        types = {}
        by_month = {}

        for interview in interviews:
            if interview.company_name:
                companies.add(interview.company_name)

            itype = interview.interview_type or 'unknown'
            types[itype] = types.get(itype, 0) + 1

            month_key = interview.start_time.strftime('%Y-%m')
            by_month[month_key] = by_month.get(month_key, 0) + 1

        return {
            'total_interviews': len(interviews),
            'unique_companies': len(companies),
            'companies': sorted(companies),
            'by_type': types,
            'by_month': dict(sorted(by_month.items())),
            'interviews': interviews
        }


def sync_calendar_with_applications():
    """
    Sync calendar interviews with job application database.

    This updates the gmail_job_applications table with accurate interview counts
    based on actual calendar events.
    """
    import os
    from supabase import create_client

    print("Connecting to Calendar...")
    calendar = CalendarClient()
    if not calendar.connect():
        print("Failed to connect to Calendar. You may need to re-authenticate.")
        return

    print("Fetching interviews from calendar...")
    summary = calendar.get_interview_summary()

    print(f"\nFound {summary['total_interviews']} interview events")
    print(f"At {summary['unique_companies']} unique companies")

    # Connect to Supabase directly
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables required")
        return summary

    db = create_client(supabase_url, supabase_key)

    # Group interviews by company
    by_company = calendar.get_interviews_by_company()

    print("\nUpdating application records...")
    updated = 0

    for company, interviews in by_company.items():
        if not company or company == 'Unknown':
            continue

        # Find matching application (try exact and fuzzy match)
        result = db.table('gmail_job_applications').select('id, company_name, total_interviews').ilike('company_name', f'%{company}%').execute()

        if result.data:
            for app in result.data:
                actual_count = len(interviews)
                if app.get('total_interviews') != actual_count:
                    db.table('gmail_job_applications').update({
                        'total_interviews': actual_count
                    }).eq('id', app['id']).execute()
                    print(f"  Updated {app['company_name']}: {app.get('total_interviews', 0)} -> {actual_count} interviews")
                    updated += 1

    print(f"\nUpdated {updated} application records")
    return summary


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'sync':
        sync_calendar_with_applications()
    else:
        # Just show interview summary
        calendar = CalendarClient()
        if calendar.connect():
            summary = calendar.get_interview_summary()

            print(f"\n=== Interview Summary ===")
            print(f"Total interviews: {summary['total_interviews']}")
            print(f"Unique companies: {summary['unique_companies']}")

            print(f"\nBy Type:")
            for itype, count in sorted(summary['by_type'].items(), key=lambda x: -x[1]):
                print(f"  {itype}: {count}")

            print(f"\nBy Month:")
            for month, count in summary['by_month'].items():
                print(f"  {month}: {count}")

            print(f"\nCompanies interviewed with:")
            for company in summary['companies']:
                print(f"  - {company}")
