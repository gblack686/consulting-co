#!/usr/bin/env python3
"""
Job Application Email Classifier

Identifies and classifies job application related emails including:
- Application confirmations
- Rejections
- Interview invitations
- Recruiter outreach
- Offer letters
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ApplicationEmailResult:
    """Result of classifying a job-related email."""
    message_id: str
    is_job_related: bool
    email_type: str  # 'application_confirm', 'rejection', 'interview_invite', 'recruiter_outreach', 'offer', 'general_job', 'not_job'
    confidence: float

    # Extracted data
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_id: Optional[str] = None
    source: Optional[str] = None  # 'linkedin', 'indeed', 'greenhouse', 'lever', 'direct', etc.

    # Interview details (if applicable)
    interview_date: Optional[str] = None
    interview_type: Optional[str] = None
    interviewer_names: List[str] = field(default_factory=list)

    # Contact info
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    # Status inference
    inferred_status: Optional[str] = None  # 'applied', 'screening', 'interviewing', 'rejected', 'offer'

    reasoning: str = ""


class ApplicationClassifier:
    """Classifies emails related to job applications."""

    # Known job platform domains
    JOB_PLATFORMS = {
        'linkedin.com': 'linkedin',
        'indeed.com': 'indeed',
        'greenhouse.io': 'greenhouse',
        'lever.co': 'lever',
        'workday.com': 'workday',
        'icims.com': 'icims',
        'jobvite.com': 'jobvite',
        'smartrecruiters.com': 'smartrecruiters',
        'ashbyhq.com': 'ashby',
        'recruiterbox.com': 'recruiterbox',
        'bamboohr.com': 'bamboohr',
        'jazz.co': 'jazz',
        'breezy.hr': 'breezy',
        'recruitee.com': 'recruitee',
        'hire.withgoogle.com': 'google_hire',
        'jobs.lever.co': 'lever',
        'boards.greenhouse.io': 'greenhouse',
        'myworkday.com': 'workday',
        'taleo.net': 'taleo',
        'successfactors.com': 'successfactors',
        'wd5.myworkdayjobs.com': 'workday',
        'app.ashbyhq.com': 'ashby',
    }

    # Patterns indicating job-related emails
    APPLICATION_PATTERNS = [
        r'application\s+(received|submitted|confirmed)',
        r'thank\s+you\s+for\s+(applying|your\s+application)',
        r'we\s+received\s+your\s+application',
        r'your\s+application\s+(for|to)',
        r'applied\s+(for|to)\s+.+\s+(position|role|job)',
    ]

    REJECTION_PATTERNS = [
        r'after\s+careful\s+consideration',
        r'decided\s+to\s+(move\s+forward|proceed)\s+with\s+other',
        r'not\s+(moving|proceeding)\s+forward',
        r'position\s+has\s+been\s+filled',
        r'will\s+not\s+be\s+(moving|proceeding)',
        r'unfortunately',
        r'regret\s+to\s+inform',
        r'other\s+candidates',
        r'not\s+selected',
    ]

    INTERVIEW_PATTERNS = [
        r'schedule\s+(an?\s+)?interview',
        r'interview\s+(request|invitation|scheduled)',
        r'would\s+like\s+to\s+(schedule|set\s+up|arrange)',
        r'phone\s+screen',
        r'video\s+(call|interview)',
        r'technical\s+(interview|screen)',
        r'on-?site\s+interview',
        r'next\s+(steps|round)',
        r'meet\s+(with|the)\s+team',
    ]

    OFFER_PATTERNS = [
        r'offer\s+(letter|of\s+employment)',
        r'pleased\s+to\s+(offer|extend)',
        r'job\s+offer',
        r'compensation\s+package',
        r'start\s+date',
        r'offer\s+details',
    ]

    RECRUITER_PATTERNS = [
        r'i\s+came\s+across\s+your\s+(profile|resume)',
        r'saw\s+your\s+(profile|background)',
        r'reaching\s+out\s+(about|regarding)\s+.+\s+(opportunity|position|role)',
        r'i\s+have\s+an?\s+(exciting\s+)?opportunity',
        r'perfect\s+(fit|match)\s+for',
        r'your\s+(experience|background)\s+(is|would\s+be)',
        r'client\s+(is\s+looking|has\s+an?\s+opening)',
    ]

    def __init__(self, api_key: str = None):
        """Initialize classifier."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def classify_email(
        self,
        message_id: str,
        sender_email: str,
        subject: str,
        body: str,
        headers: Dict[str, str] = None
    ) -> ApplicationEmailResult:
        """
        Classify an email as job-related and extract relevant info.

        Args:
            message_id: Gmail message ID
            sender_email: Sender's email address
            subject: Email subject
            body: Email body text
            headers: Optional email headers

        Returns:
            ApplicationEmailResult with classification and extracted data
        """
        headers = headers or {}

        # First, quick heuristic check
        heuristic_result = self._heuristic_classify(sender_email, subject, body)

        if not heuristic_result['is_job_related']:
            return ApplicationEmailResult(
                message_id=message_id,
                is_job_related=False,
                email_type='not_job',
                confidence=heuristic_result['confidence'],
                reasoning=heuristic_result['reasoning']
            )

        # Use AI for detailed classification and extraction
        if self.client:
            return self._ai_classify(
                message_id=message_id,
                sender_email=sender_email,
                subject=subject,
                body=body,
                heuristic_type=heuristic_result['type']
            )

        # Fallback to heuristic-only result
        return ApplicationEmailResult(
            message_id=message_id,
            is_job_related=True,
            email_type=heuristic_result['type'],
            confidence=heuristic_result['confidence'],
            source=heuristic_result.get('source'),
            reasoning=heuristic_result['reasoning']
        )

    def _heuristic_classify(
        self,
        sender_email: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """Quick heuristic classification."""
        sender_lower = sender_email.lower()
        subject_lower = subject.lower()
        body_lower = body.lower()[:3000]  # First 3000 chars
        combined = f"{subject_lower} {body_lower}"

        # Check sender domain for known platforms
        source = None
        for domain, platform in self.JOB_PLATFORMS.items():
            if domain in sender_lower:
                source = platform
                break

        # Check patterns
        email_type = 'not_job'
        confidence = 0.0
        reasoning = ""

        # Application confirmation
        for pattern in self.APPLICATION_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                email_type = 'application_confirm'
                confidence = 0.85
                reasoning = f"Matches application pattern: {pattern}"
                break

        # Rejection
        if email_type == 'not_job':
            for pattern in self.REJECTION_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    email_type = 'rejection'
                    confidence = 0.80
                    reasoning = f"Matches rejection pattern: {pattern}"
                    break

        # Interview invite
        if email_type == 'not_job':
            for pattern in self.INTERVIEW_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    email_type = 'interview_invite'
                    confidence = 0.85
                    reasoning = f"Matches interview pattern: {pattern}"
                    break

        # Offer
        if email_type == 'not_job':
            for pattern in self.OFFER_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    email_type = 'offer'
                    confidence = 0.80
                    reasoning = f"Matches offer pattern: {pattern}"
                    break

        # Recruiter outreach
        if email_type == 'not_job':
            for pattern in self.RECRUITER_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    email_type = 'recruiter_outreach'
                    confidence = 0.75
                    reasoning = f"Matches recruiter pattern: {pattern}"
                    break

        # Check if from job platform even if no pattern match
        if email_type == 'not_job' and source:
            email_type = 'general_job'
            confidence = 0.70
            reasoning = f"From job platform: {source}"

        # Job-related keywords in subject
        job_keywords = ['job', 'position', 'role', 'opportunity', 'career', 'hiring', 'recruit', 'application', 'interview']
        if email_type == 'not_job':
            for keyword in job_keywords:
                if keyword in subject_lower:
                    email_type = 'general_job'
                    confidence = 0.60
                    reasoning = f"Job keyword in subject: {keyword}"
                    break

        is_job_related = email_type != 'not_job'

        return {
            'is_job_related': is_job_related,
            'type': email_type,
            'confidence': confidence,
            'source': source,
            'reasoning': reasoning
        }

    def _ai_classify(
        self,
        message_id: str,
        sender_email: str,
        subject: str,
        body: str,
        heuristic_type: str
    ) -> ApplicationEmailResult:
        """Use AI for detailed classification and entity extraction."""

        # Truncate body for API
        body_truncated = body[:4000] if len(body) > 4000 else body

        prompt = f"""Analyze this email and extract job application information.

SENDER: {sender_email}
SUBJECT: {subject}
BODY:
{body_truncated}

Classify this email and extract all relevant job application details. Return a JSON object with:

{{
    "is_job_related": true/false,
    "email_type": "application_confirm" | "rejection" | "interview_invite" | "recruiter_outreach" | "offer" | "general_job" | "not_job",
    "confidence": 0.0-1.0,
    "company_name": "extracted company name or null",
    "job_title": "extracted job title/position or null",
    "job_id": "job requisition ID if mentioned or null",
    "source": "linkedin" | "indeed" | "greenhouse" | "lever" | "workday" | "direct" | "recruiter" | "other" | null,
    "interview_date": "YYYY-MM-DD if mentioned or null",
    "interview_type": "phone_screen" | "technical" | "behavioral" | "onsite" | "video" | "final" | null,
    "interviewer_names": ["list of interviewer names if mentioned"],
    "contact_name": "recruiter or contact person name or null",
    "contact_title": "their job title if mentioned or null",
    "contact_phone": "phone number if mentioned or null",
    "inferred_status": "applied" | "screening" | "interviewing" | "rejected" | "offer" | null,
    "reasoning": "brief explanation of classification"
}}

Focus on extracting:
1. Company name (look for company names, not just ATS platform names)
2. Job title (the specific role being applied for)
3. Any dates or times for interviews
4. Contact information of recruiters/hiring managers
5. Interview details if this is an interview invite

Return ONLY the JSON object, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # Parse JSON
            if result_text.startswith('```'):
                result_text = re.sub(r'^```json?\n?', '', result_text)
                result_text = re.sub(r'\n?```$', '', result_text)

            data = json.loads(result_text)

            return ApplicationEmailResult(
                message_id=message_id,
                is_job_related=data.get('is_job_related', True),
                email_type=data.get('email_type', heuristic_type),
                confidence=data.get('confidence', 0.8),
                company_name=data.get('company_name'),
                job_title=data.get('job_title'),
                job_id=data.get('job_id'),
                source=data.get('source'),
                interview_date=data.get('interview_date'),
                interview_type=data.get('interview_type'),
                interviewer_names=data.get('interviewer_names', []),
                contact_name=data.get('contact_name'),
                contact_title=data.get('contact_title'),
                contact_email=sender_email,
                contact_phone=data.get('contact_phone'),
                inferred_status=data.get('inferred_status'),
                reasoning=data.get('reasoning', '')
            )

        except Exception as e:
            # Fallback on error
            return ApplicationEmailResult(
                message_id=message_id,
                is_job_related=True,
                email_type=heuristic_type,
                confidence=0.7,
                reasoning=f"AI extraction failed: {e}"
            )

    def is_linkedin_application(self, sender_email: str, subject: str) -> bool:
        """Check if email is from LinkedIn about a job application."""
        return (
            'linkedin.com' in sender_email.lower() and
            any(kw in subject.lower() for kw in ['application', 'applied', 'job', 'position'])
        )

    def extract_company_from_linkedin(self, body: str) -> Optional[str]:
        """Try to extract company name from LinkedIn application email."""
        # LinkedIn format: "Your application was sent to [Company]"
        patterns = [
            r'application\s+(?:was\s+)?sent\s+to\s+([A-Z][A-Za-z0-9\s&\-\.]+)',
            r'applied\s+(?:for\s+.+\s+)?at\s+([A-Z][A-Za-z0-9\s&\-\.]+)',
            r'([A-Z][A-Za-z0-9\s&\-\.]+)\s+viewed\s+your\s+application',
        ]

        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                company = match.group(1).strip()
                # Clean up common suffixes
                company = re.sub(r'\s+(Inc|LLC|Ltd|Corp|Co)\.*$', '', company, flags=re.IGNORECASE)
                return company

        return None


def main():
    """CLI for testing classification."""
    import argparse

    parser = argparse.ArgumentParser(description='Classify job application emails')
    parser.add_argument('--test', action='store_true', help='Run test classification')

    args = parser.parse_args()

    if args.test:
        classifier = ApplicationClassifier()

        # Test cases
        tests = [
            {
                'sender': 'jobs-noreply@linkedin.com',
                'subject': 'Your application was sent to OpenAI',
                'body': 'Your application for Senior Data Engineer at OpenAI was sent.'
            },
            {
                'sender': 'recruiting@company.com',
                'subject': 'Interview Request - Software Engineer',
                'body': 'We would like to schedule a phone screen for next week.'
            },
            {
                'sender': 'newsletter@company.com',
                'subject': 'Weekly Update',
                'body': 'Here is your weekly newsletter with the latest news.'
            }
        ]

        for test in tests:
            result = classifier.classify_email(
                message_id='test123',
                sender_email=test['sender'],
                subject=test['subject'],
                body=test['body']
            )
            print(f"\nSubject: {test['subject']}")
            print(f"Type: {result.email_type} ({result.confidence:.0%})")
            print(f"Company: {result.company_name}")
            print(f"Reasoning: {result.reasoning}")


if __name__ == '__main__':
    main()
