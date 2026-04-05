#!/usr/bin/env python3
"""
Email Classifier

AI-powered email classification to identify sales solicitations,
transactional emails, human correspondence, and more.
"""

import os
import re
import json
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from datetime import datetime

from anthropic import Anthropic


@dataclass
class ClassificationResult:
    """Result of email classification."""
    message_id: str
    classification: str  # sales_solicitation, transactional, human_correspondence, etc.
    confidence: float
    reasoning: str
    is_important: bool
    suggested_action: str  # archive, keep, flag


class EmailClassifier:
    """AI-powered email classification engine."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    # Classification categories
    CATEGORIES = {
        'sales_solicitation': {
            'description': 'Unsolicited sales outreach, cold emails, promotional offers',
            'priority': 'low',
            'action': 'archive'
        },
        'transactional': {
            'description': 'Receipts, order confirmations, shipping notifications, purchase-related',
            'priority': 'high',
            'action': 'keep'
        },
        'human_correspondence': {
            'description': 'Real person-to-person email communication',
            'priority': 'high',
            'action': 'keep'
        },
        'newsletter_subscribed': {
            'description': 'Newsletter user likely subscribed to',
            'priority': 'medium',
            'action': 'keep'
        },
        'automated_notification': {
            'description': 'App notifications, GitHub, calendar, automated alerts',
            'priority': 'medium',
            'action': 'keep'
        }
    }

    # Known sales/outreach platform domains
    SALES_DOMAINS = {
        # Sales engagement platforms
        'apollo.io', 'outreach.io', 'salesloft.com', 'hubspot.com',
        'mailshake.com', 'lemlist.com', 'woodpecker.co', 'reply.io',
        'yesware.com', 'mixmax.com', 'streak.com', 'close.com',
        # B2B marketing
        'marketo.com', 'pardot.com', 'eloqua.com', 'drift.com',
        # Cold email services
        'instantly.ai', 'smartlead.ai', 'snov.io', 'hunter.io',
        # Lead generation
        'zoominfo.com', 'lusha.com', 'leadfeeder.com',
    }

    # Known transactional/receipt domains
    TRANSACTIONAL_DOMAINS = {
        # E-commerce
        'amazon.com', 'ebay.com', 'shopify.com', 'etsy.com',
        'walmart.com', 'target.com', 'bestbuy.com', 'costco.com',
        'newegg.com', 'wayfair.com', 'homedepot.com', 'lowes.com',
        # Payments/receipts
        'stripe.com', 'paypal.com', 'square.com', 'venmo.com',
        'intuit.com', 'quickbooks.com', 'bill.com',
        # Shipping
        'ups.com', 'fedex.com', 'usps.com', 'dhl.com',
        # Services/subscriptions
        'uber.com', 'lyft.com', 'doordash.com', 'grubhub.com',
        'netflix.com', 'spotify.com', 'apple.com', 'google.com',
    }

    # Sales language patterns
    SALES_PATTERNS = [
        r'schedule a (call|demo|meeting)',
        r'limited time offer',
        r'exclusive (offer|deal|discount)',
        r'(increase|boost|grow) your (revenue|sales|business)',
        r'free (trial|demo|consultation)',
        r'(quick|brief) (call|chat|intro)',
        r'saw your (company|profile|linkedin)',
        r'reaching out because',
        r'i\'d love to (connect|chat|discuss)',
        r'can i get 15 minutes',
        r'let me know if you\'re open to',
    ]

    # Receipt/transactional patterns
    RECEIPT_PATTERNS = [
        r'order (confirmation|confirmed|number|#)',
        r'receipt for (your )?purchase',
        r'shipping (confirmation|update|notification)',
        r'your (order|package) (has been|is|was)',
        r'tracking (number|information|update)',
        r'invoice #?\d+',
        r'payment (received|confirmed|successful)',
        r'thank you for your (order|purchase)',
        r'delivery (update|notification|scheduled)',
    ]

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize classifier.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model or self.DEFAULT_MODEL

        # Compile regex patterns
        self._sales_regex = [re.compile(p, re.IGNORECASE) for p in self.SALES_PATTERNS]
        self._receipt_regex = [re.compile(p, re.IGNORECASE) for p in self.RECEIPT_PATTERNS]

        # Known contacts cache (populated from sent mail)
        self._known_contacts: Set[str] = set()

    def set_known_contacts(self, contacts: Set[str]):
        """Set known contacts from sent mail for detection."""
        self._known_contacts = {c.lower() for c in contacts}

    def is_known_sender(self, email_address: str) -> bool:
        """Check if sender is in known contacts."""
        return email_address.lower() in self._known_contacts

    def classify_email(
        self,
        message_id: str,
        sender_email: str,
        subject: str,
        body: str,
        has_thread: bool = False,
        headers: Dict[str, str] = None
    ) -> ClassificationResult:
        """
        Classify an email using heuristics and AI.

        Args:
            message_id: Gmail message ID
            sender_email: Sender's email address
            subject: Email subject
            body: Email body text
            has_thread: Whether email is part of existing thread
            headers: Email headers dict

        Returns:
            ClassificationResult with classification details
        """
        headers = headers or {}
        sender_domain = self._extract_domain(sender_email)

        # Quick heuristic checks first
        heuristic_result = self._heuristic_classify(
            sender_email, sender_domain, subject, body, has_thread, headers
        )

        if heuristic_result and heuristic_result['confidence'] >= 0.9:
            # High confidence heuristic match
            return ClassificationResult(
                message_id=message_id,
                classification=heuristic_result['classification'],
                confidence=heuristic_result['confidence'],
                reasoning=heuristic_result['reasoning'],
                is_important=self._is_important(heuristic_result['classification']),
                suggested_action=self.CATEGORIES[heuristic_result['classification']]['action']
            )

        # Use AI for uncertain cases
        ai_result = self._ai_classify(
            sender_email=sender_email,
            subject=subject,
            body=body[:3000],  # Limit body length
            is_known_sender=self.is_known_sender(sender_email),
            has_thread=has_thread,
            domain_category=self._categorize_domain(sender_domain)
        )

        return ClassificationResult(
            message_id=message_id,
            classification=ai_result['classification'],
            confidence=ai_result['confidence'],
            reasoning=ai_result['reasoning'],
            is_important=ai_result.get('is_important', False),
            suggested_action=ai_result.get('suggested_action', 'keep')
        )

    def _heuristic_classify(
        self,
        sender_email: str,
        sender_domain: str,
        subject: str,
        body: str,
        has_thread: bool,
        headers: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Apply heuristic rules for quick classification."""

        # Check for transactional/receipt patterns first
        if sender_domain in self.TRANSACTIONAL_DOMAINS:
            for pattern in self._receipt_regex:
                if pattern.search(subject) or pattern.search(body[:500]):
                    return {
                        'classification': 'transactional',
                        'confidence': 0.95,
                        'reasoning': f'Known transactional domain ({sender_domain}) with receipt pattern'
                    }

        # Check for sales domain
        if sender_domain in self.SALES_DOMAINS:
            return {
                'classification': 'sales_solicitation',
                'confidence': 0.95,
                'reasoning': f'Known sales platform domain: {sender_domain}'
            }

        # Check for sales patterns in subject/body
        sales_pattern_count = 0
        for pattern in self._sales_regex:
            if pattern.search(subject) or pattern.search(body[:1000]):
                sales_pattern_count += 1

        if sales_pattern_count >= 2:
            return {
                'classification': 'sales_solicitation',
                'confidence': 0.85,
                'reasoning': f'Multiple sales patterns detected ({sales_pattern_count})'
            }

        # Known sender + thread = likely human correspondence
        if self.is_known_sender(sender_email) and has_thread:
            return {
                'classification': 'human_correspondence',
                'confidence': 0.9,
                'reasoning': 'Known sender with existing conversation'
            }

        # Known sender without thread
        if self.is_known_sender(sender_email):
            return {
                'classification': 'human_correspondence',
                'confidence': 0.8,
                'reasoning': 'Known sender (in sent contacts)'
            }

        # Check List-Unsubscribe header for newsletter
        if 'list-unsubscribe' in headers:
            # Could be newsletter or sales
            if any(pattern.search(subject) for pattern in self._sales_regex):
                return {
                    'classification': 'sales_solicitation',
                    'confidence': 0.75,
                    'reasoning': 'Has unsubscribe link with sales patterns'
                }
            return {
                'classification': 'newsletter_subscribed',
                'confidence': 0.7,
                'reasoning': 'Has List-Unsubscribe header'
            }

        # Fake reply trick detection (Re: with no thread)
        if subject.lower().startswith('re:') and not has_thread:
            return {
                'classification': 'sales_solicitation',
                'confidence': 0.85,
                'reasoning': 'Fake reply (Re: without actual thread history)'
            }

        return None  # Use AI for uncertain cases

    def _ai_classify(
        self,
        sender_email: str,
        subject: str,
        body: str,
        is_known_sender: bool,
        has_thread: bool,
        domain_category: str
    ) -> Dict[str, Any]:
        """Use Claude AI for classification."""

        prompt = f"""Classify this email into ONE of these categories:

1. SALES_SOLICITATION - Unsolicited sales, cold outreach, promotional offers I didn't ask for
2. TRANSACTIONAL - Receipts, order confirmations, shipping notifications, purchase-related
3. HUMAN_CORRESPONDENCE - Real person-to-person email communication
4. NEWSLETTER_SUBSCRIBED - Newsletter I likely subscribed to
5. AUTOMATED_NOTIFICATION - App notifications, calendar invites, automated alerts

Context signals:
- Sender in my contacts (sent mail): {is_known_sender}
- Thread has prior messages: {has_thread}
- Domain type: {domain_category}

Email:
From: {sender_email}
Subject: {subject}

{body[:2000]}

Respond with JSON only:
{{
    "classification": "SALES_SOLICITATION|TRANSACTIONAL|HUMAN_CORRESPONDENCE|NEWSLETTER_SUBSCRIBED|AUTOMATED_NOTIFICATION",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "is_important": true/false,
    "suggested_action": "archive|keep|flag"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            result = self._parse_json_response(content)

            # Normalize classification to lowercase with underscore
            classification = result.get('classification', 'AUTOMATED_NOTIFICATION').lower()

            return {
                'classification': classification,
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', 'AI classification'),
                'is_important': result.get('is_important', False),
                'suggested_action': result.get('suggested_action', 'keep')
            }

        except Exception as e:
            print(f"AI classification error: {e}")
            return {
                'classification': 'automated_notification',
                'confidence': 0.3,
                'reasoning': f'AI error, defaulting: {str(e)}',
                'is_important': False,
                'suggested_action': 'keep'
            }

    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address."""
        try:
            return email_address.split('@')[1].lower()
        except (IndexError, AttributeError):
            return ''

    def _categorize_domain(self, domain: str) -> str:
        """Categorize a domain."""
        if domain in self.SALES_DOMAINS:
            return 'sales_platform'
        if domain in self.TRANSACTIONAL_DOMAINS:
            return 'transactional'
        if domain.endswith(('.com', '.net', '.org', '.io')):
            return 'corporate'
        return 'unknown'

    def _is_important(self, classification: str) -> bool:
        """Determine if classification is important."""
        category = self.CATEGORIES.get(classification, {})
        return category.get('priority') in ('high',)

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return {}

    def batch_classify(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[ClassificationResult]:
        """
        Classify multiple messages.

        Args:
            messages: List of message dicts with id, sender, subject, body, etc.

        Returns:
            List of ClassificationResult objects
        """
        results = []

        for msg in messages:
            result = self.classify_email(
                message_id=msg['id'],
                sender_email=msg.get('sender_email', ''),
                subject=msg.get('subject', ''),
                body=msg.get('body', ''),
                has_thread=msg.get('has_thread', False),
                headers=msg.get('headers', {})
            )
            results.append(result)

        return results
