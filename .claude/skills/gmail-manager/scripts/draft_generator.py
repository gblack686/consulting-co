#!/usr/bin/env python3
"""
Draft Generator

Uses Claude API to generate email drafts based on prompts,
context, and reply-to messages.
"""

import os
from typing import Dict, Any, Optional, List

from anthropic import Anthropic

from .gmail_client import GmailClient


class DraftGenerator:
    """Generate email drafts using Claude API."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    DEFAULT_SIGNATURE = """
Best regards"""

    def __init__(
        self,
        gmail_client: GmailClient,
        api_key: str = None,
        model: str = None
    ):
        """
        Initialize draft generator.

        Args:
            gmail_client: Gmail API client
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.gmail = gmail_client
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model or self.DEFAULT_MODEL
        self.signature = self.DEFAULT_SIGNATURE

    def set_signature(self, signature: str):
        """Set email signature to append to drafts."""
        self.signature = signature

    def generate_reply(
        self,
        message_id: str,
        instructions: str = None,
        tone: str = 'professional',
        include_original: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a reply draft to an existing message.

        Args:
            message_id: ID of message to reply to
            instructions: Specific instructions for the reply
            tone: Tone of reply (professional, casual, formal, friendly)
            include_original: Whether to quote original in reply

        Returns:
            Created draft object or None if failed
        """
        # Get original message
        original = self.gmail.get_message(message_id)
        if not original:
            print(f"Could not find message: {message_id}")
            return None

        headers = self._get_headers(original)
        original_body = self.gmail.get_message_body(original)
        original_subject = headers.get('subject', '')
        original_sender = headers.get('from', '')

        # Generate reply subject
        reply_subject = original_subject
        if not reply_subject.lower().startswith('re:'):
            reply_subject = f"Re: {reply_subject}"

        # Build prompt
        prompt = self._build_reply_prompt(
            original_subject=original_subject,
            original_sender=original_sender,
            original_body=original_body,
            instructions=instructions,
            tone=tone
        )

        # Generate reply body
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            reply_body = response.content[0].text.strip()

            # Add signature
            if self.signature:
                reply_body += f"\n{self.signature}"

            # Add quoted original if requested
            if include_original:
                quoted = self._quote_message(original_body, original_sender)
                reply_body += f"\n\n{quoted}"

            # Extract reply-to email
            reply_to = self._extract_email(original_sender)

            # Create draft
            draft = self.gmail.create_draft(
                to=reply_to,
                subject=reply_subject,
                body=reply_body,
                reply_to_message_id=message_id
            )

            return draft

        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def generate_new_email(
        self,
        to: str,
        topic: str,
        context: str = None,
        tone: str = 'professional',
        length: str = 'medium'
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a new email draft.

        Args:
            to: Recipient email address
            topic: What the email should be about
            context: Additional context or details
            tone: Tone (professional, casual, formal, friendly, persuasive)
            length: Desired length (short, medium, long)

        Returns:
            Created draft object or None if failed
        """
        prompt = self._build_new_email_prompt(
            to=to,
            topic=topic,
            context=context,
            tone=tone,
            length=length
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()

            # Parse subject and body from response
            subject, body = self._parse_email_response(content)

            # Add signature
            if self.signature:
                body += f"\n{self.signature}"

            # Create draft
            draft = self.gmail.create_draft(
                to=to,
                subject=subject,
                body=body
            )

            return draft

        except Exception as e:
            print(f"Error generating email: {e}")
            return None

    def suggest_responses(
        self,
        message_id: str,
        count: int = 3
    ) -> List[Dict[str, str]]:
        """
        Generate multiple response suggestions for a message.

        Args:
            message_id: ID of message to respond to
            count: Number of suggestions to generate

        Returns:
            List of {tone, summary, preview} dicts
        """
        # Get original message
        original = self.gmail.get_message(message_id)
        if not original:
            return []

        headers = self._get_headers(original)
        original_body = self.gmail.get_message_body(original)

        prompt = f"""Given this email, suggest {count} different ways to respond.
For each suggestion, provide:
1. The tone (e.g., "professional", "friendly", "apologetic")
2. A one-sentence summary of the approach
3. A preview of the first 1-2 sentences

Email:
Subject: {headers.get('subject', '')}
From: {headers.get('from', '')}

{original_body[:2000]}

Respond in this format for each suggestion:
---
Tone: [tone]
Approach: [summary]
Preview: [first sentences]
---"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            return self._parse_suggestions(response.content[0].text)

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []

    def _build_reply_prompt(
        self,
        original_subject: str,
        original_sender: str,
        original_body: str,
        instructions: str,
        tone: str
    ) -> str:
        """Build prompt for reply generation."""
        prompt = f"""Write a reply to this email.

Tone: {tone}
"""
        if instructions:
            prompt += f"Instructions: {instructions}\n"

        prompt += f"""
Original email:
From: {original_sender}
Subject: {original_subject}

{original_body[:3000]}

Write only the reply body (no subject line, no "Dear X" greeting unless appropriate for tone).
Be concise and direct. Do not include a signature."""

        return prompt

    def _build_new_email_prompt(
        self,
        to: str,
        topic: str,
        context: str,
        tone: str,
        length: str
    ) -> str:
        """Build prompt for new email generation."""
        length_guidance = {
            'short': '2-3 sentences',
            'medium': '1-2 short paragraphs',
            'long': '3-4 paragraphs'
        }.get(length, '1-2 paragraphs')

        prompt = f"""Write an email with these specifications:

To: {to}
Topic: {topic}
Tone: {tone}
Length: {length_guidance}
"""
        if context:
            prompt += f"Additional context: {context}\n"

        prompt += """
Respond in this format:
Subject: [subject line]

[email body]

Do not include a signature."""

        return prompt

    def _parse_email_response(self, content: str) -> tuple[str, str]:
        """Parse subject and body from generated response."""
        lines = content.strip().split('\n')

        subject = "No Subject"
        body_start = 0

        for i, line in enumerate(lines):
            if line.lower().startswith('subject:'):
                subject = line[8:].strip()
                body_start = i + 1
                # Skip empty line after subject
                if body_start < len(lines) and not lines[body_start].strip():
                    body_start += 1
                break

        body = '\n'.join(lines[body_start:]).strip()

        return subject, body

    def _parse_suggestions(self, content: str) -> List[Dict[str, str]]:
        """Parse response suggestions from Claude output."""
        suggestions = []
        current = {}

        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('---'):
                if current:
                    suggestions.append(current)
                    current = {}
            elif line.lower().startswith('tone:'):
                current['tone'] = line[5:].strip()
            elif line.lower().startswith('approach:'):
                current['summary'] = line[9:].strip()
            elif line.lower().startswith('preview:'):
                current['preview'] = line[8:].strip()

        if current:
            suggestions.append(current)

        return suggestions

    def _get_headers(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Extract headers from message."""
        headers = {}
        payload = message.get('payload', {})
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        return headers

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        import re
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_header)
        return match.group() if match else from_header

    def _quote_message(self, body: str, sender: str) -> str:
        """Create quoted message for reply."""
        quoted_lines = ['', f'On [date], {sender} wrote:', '']
        for line in body.split('\n')[:50]:  # Limit quoted lines
            quoted_lines.append(f'> {line}')

        return '\n'.join(quoted_lines)
