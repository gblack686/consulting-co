#!/usr/bin/env python3
"""
Email Summarizer

Uses Claude API to generate summaries, extract key points,
and identify action items from emails.
"""

import os
import re
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime

from anthropic import Anthropic


class EmailSummarizer:
    """Generate AI summaries of emails using Claude API."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize summarizer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use for summarization
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model or self.DEFAULT_MODEL

    def summarize_email(
        self,
        subject: str,
        body: str,
        sender: str,
        sender_name: str = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a single email.

        Args:
            subject: Email subject
            body: Email body text
            sender: Sender email address
            sender_name: Sender display name

        Returns:
            Dict with summary, key_points, action_items, sentiment, category
        """
        # Clean body text
        clean_body = self._clean_email_body(body)

        # Truncate if too long
        if len(clean_body) > 10000:
            clean_body = clean_body[:10000] + "\n...[truncated]"

        sender_display = f"{sender_name} <{sender}>" if sender_name else sender

        prompt = f"""Analyze this email and provide:
1. A concise summary (2-3 sentences)
2. Key points (bullet list, max 5)
3. Action items for the recipient (if any)
4. Sentiment (positive, negative, neutral, or urgent)
5. Category (personal, work, newsletter, transactional, promotional, notification, other)

Email:
From: {sender_display}
Subject: {subject}

{clean_body}

Respond in this exact JSON format:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2"],
    "action_items": ["action 1", "action 2"],
    "sentiment": "neutral",
    "category": "work"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            content = response.content[0].text
            result = self._parse_json_response(content)

            return {
                "summary": result.get("summary", "Unable to summarize"),
                "key_points": result.get("key_points", []),
                "action_items": result.get("action_items", []),
                "sentiment": result.get("sentiment", "neutral"),
                "category": result.get("category", "other"),
            }

        except Exception as e:
            print(f"Error summarizing email: {e}")
            return {
                "summary": f"Error generating summary: {str(e)}",
                "key_points": [],
                "action_items": [],
                "sentiment": "neutral",
                "category": "other",
            }

    def summarize_thread(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize an entire email thread.

        Args:
            messages: List of message dicts with subject, body, sender, date

        Returns:
            Dict with thread_summary, participants, timeline, action_items
        """
        if not messages:
            return {"thread_summary": "Empty thread", "participants": [], "action_items": []}

        # Build thread context
        thread_text = ""
        participants = set()

        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            participants.add(sender)
            date = msg.get('date', '')
            body = self._clean_email_body(msg.get('body', ''))[:2000]

            thread_text += f"\n---\nFrom: {sender}\nDate: {date}\n{body}\n"

        # Truncate if too long
        if len(thread_text) > 15000:
            thread_text = thread_text[:15000] + "\n...[truncated]"

        prompt = f"""Analyze this email thread and provide:
1. A summary of the entire conversation (3-4 sentences)
2. Key decisions or outcomes
3. Outstanding action items
4. Current status (resolved, pending, needs response, etc.)

Thread ({len(messages)} messages):
{thread_text}

Respond in JSON format:
{{
    "thread_summary": "...",
    "key_decisions": ["..."],
    "action_items": ["..."],
    "status": "pending"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            result = self._parse_json_response(content)

            return {
                "thread_summary": result.get("thread_summary", ""),
                "participants": list(participants),
                "message_count": len(messages),
                "key_decisions": result.get("key_decisions", []),
                "action_items": result.get("action_items", []),
                "status": result.get("status", "unknown"),
            }

        except Exception as e:
            print(f"Error summarizing thread: {e}")
            return {
                "thread_summary": f"Error: {str(e)}",
                "participants": list(participants),
                "message_count": len(messages),
                "action_items": [],
            }

    def extract_action_items(self, body: str) -> List[str]:
        """
        Extract action items from email body.

        Args:
            body: Email body text

        Returns:
            List of action item strings
        """
        clean_body = self._clean_email_body(body)

        if len(clean_body) > 5000:
            clean_body = clean_body[:5000]

        prompt = f"""Extract any action items, requests, or tasks from this email.
Only include clear, actionable items directed at the recipient.
Return as a JSON array of strings. If no action items, return empty array.

Email:
{clean_body}

Respond with only the JSON array:
["action 1", "action 2"]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            # Extract JSON array
            import json
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []

        except Exception as e:
            print(f"Error extracting action items: {e}")
            return []

    def classify_email(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """
        Classify an email's type and urgency.

        Args:
            subject: Email subject
            body: Email body (can be truncated)
            sender: Sender email

        Returns:
            Dict with category, urgency, is_newsletter, requires_response
        """
        clean_body = self._clean_email_body(body)[:3000]

        prompt = f"""Classify this email:

From: {sender}
Subject: {subject}
Body preview: {clean_body[:1000]}

Respond in JSON format:
{{
    "category": "work|personal|newsletter|promotional|transactional|notification|spam",
    "urgency": "high|medium|low",
    "is_newsletter": true/false,
    "requires_response": true/false,
    "suggested_labels": ["label1", "label2"]
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            return self._parse_json_response(content)

        except Exception as e:
            print(f"Error classifying email: {e}")
            return {
                "category": "unknown",
                "urgency": "medium",
                "is_newsletter": False,
                "requires_response": False,
            }

    def _clean_email_body(self, body: str) -> str:
        """Clean email body for better summarization."""
        if not body:
            return ""

        # Remove excessive whitespace
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = re.sub(r' {2,}', ' ', body)

        # Remove common email signatures/footers
        signature_patterns = [
            r'--\s*\n.*',  # Standard signature delimiter
            r'Sent from my (?:iPhone|iPad|Android).*',
            r'Get Outlook for (?:iOS|Android).*',
            r'________________________________.*',  # Outlook separator
        ]

        for pattern in signature_patterns:
            body = re.sub(pattern, '', body, flags=re.DOTALL | re.IGNORECASE)

        # Remove quoted replies (lines starting with >)
        body = re.sub(r'^>.*$', '', body, flags=re.MULTILINE)

        # Remove URLs (keep text, remove links)
        body = re.sub(r'https?://\S+', '[link]', body)

        return body.strip()

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from Claude's response."""
        import json

        # Try to extract JSON from response
        try:
            # First try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in response
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

        return {}

    def hash_body(self, body: str) -> str:
        """Generate a hash of the email body for deduplication."""
        clean = self._clean_email_body(body)
        return hashlib.sha256(clean.encode()).hexdigest()
