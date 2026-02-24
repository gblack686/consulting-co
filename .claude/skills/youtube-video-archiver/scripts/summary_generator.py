"""
Summary Generator

Generates concise AI-powered summaries of video transcripts using Anthropic API,
with automatic fallback to Z.ai (OpenAI-compatible) if Anthropic auth fails.
"""

import os
from anthropic import Anthropic


class SummaryGenerator:
    """Generates summaries of transcripts using Anthropic API with Z.ai fallback."""

    def __init__(self, api_key: str = None):
        """Initialize summary generator with Anthropic primary and Z.ai fallback."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.zai_key = os.getenv("ZAI_API_KEY")
        self.client = None
        self.zai_client = None
        self.model = "claude-3-5-sonnet-20241022"
        self.zai_model = "glm-4-plus"

        # Set up Anthropic client
        if self.api_key:
            is_oauth = self.api_key.startswith("sk-ant-oat")
            self.client = Anthropic(api_key=self.api_key)
            if is_oauth:
                print("✓ Using Anthropic OAuth token (may need refresh if expired)")
            else:
                print("✓ Using Anthropic API for summaries")

        # Set up OpenAI fallback client
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if self.openai_key:
            from openai import OpenAI
            self.zai_client = OpenAI(api_key=self.openai_key)
            self.zai_model = "gpt-4o-mini"
            if not self.api_key:
                print("✓ Using OpenAI API for summaries")
            else:
                print("✓ OpenAI fallback configured")

        if not self.api_key and not self.openai_key:
            raise ValueError("Either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable required")

    def _query_claude(self, prompt: str, max_tokens: int = 1000) -> str:
        """Query API with automatic Z.ai fallback on Anthropic auth failure."""
        # Try Anthropic first
        if self.client:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                return ""
            except Exception as e:
                error_str = str(e)
                is_auth_error = (
                    "401" in error_str
                    or "authentication" in error_str.lower()
                    or "invalid x-api-key" in error_str.lower()
                    or "invalid_api_key" in error_str.lower()
                )
                if is_auth_error and self.zai_client:
                    print(f"⚠ Anthropic auth failed, falling back to Z.ai...")
                else:
                    print(f"Error querying Claude API: {e}")
                    raise

        # Z.ai fallback
        if self.zai_client:
            try:
                response = self.zai_client.chat.completions.create(
                    model=self.zai_model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"Error querying Z.ai API: {e}")
                raise

        raise ValueError("No available AI client")

    def generate_summary(
        self,
        transcript: str,
        title: str = "Video",
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a summary of a transcript.

        Args:
            transcript: Full transcript text
            title: Video title for context
            max_tokens: Maximum tokens for the summary

        Returns:
            Summary text
        """
        prompt = f"""Please provide a comprehensive but concise summary of the following video transcript.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript[:50000]}

SUMMARY:
Provide a clear, well-structured summary that:
1. Captures the main topic and key points
2. Includes important examples or data mentioned
3. Is concise but complete (ideally 150-300 words)
4. Uses clear bullet points or paragraphs for readability"""

        try:
            return self._query_claude(prompt, max_tokens=max_tokens)
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Return basic fallback summary from transcript
            words = transcript[:500].split()
            return f"Video titled '{title}'. Transcript preview: {' '.join(words[:50])}... (Full summary unavailable - valid API key required)"

    def generate_key_points(self, transcript: str, title: str = "Video") -> list[str]:
        """
        Extract key points from transcript.

        Args:
            transcript: Full transcript text
            title: Video title for context

        Returns:
            List of key points
        """
        prompt = f"""Extract the 5-10 most important key points from this video transcript.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript[:50000]}

Provide ONLY a numbered list of key points, one per line. Each point should be:
- A complete sentence
- Clear and standalone
- Factual and directly from the transcript"""

        try:
            text = self._query_claude(prompt, max_tokens=500)

            # Parse numbered list into individual points
            lines = text.split("\n")
            points = [
                line.strip().lstrip("0123456789.-) ").strip()
                for line in lines
                if line.strip()
            ]
            return points
        except Exception as e:
            print(f"Error extracting key points: {e}")
            return [f"Transcript available but key points extraction unavailable (valid API key required)"]

    def generate_metadata_summary(
        self,
        transcript: str,
        title: str = "Video"
    ) -> dict:
        """
        Generate structured metadata about the transcript.

        Args:
            transcript: Full transcript text
            title: Video title for context

        Returns:
            Dictionary with topic, tags, and category
        """
        prompt = f"""Analyze this video transcript and provide structured metadata.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript[:50000]}

Provide a JSON response with:
- topic: Main topic in 2-3 words
- category: Primary category (e.g., Technology, Business, Education, etc.)
- tags: List of 3-5 relevant tags
- key_terms: List of important terms/concepts mentioned

Format as valid JSON only, no extra text."""

        try:
            response_text = self._query_claude(prompt, max_tokens=300)

            # Parse JSON response
            import json
            # Extract JSON from response (handle markdown code blocks)
            if "```" in response_text:
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            metadata = json.loads(response_text.strip())
            return metadata
        except Exception as e:
            # Fallback - don't log error since it's expected without API key
            return {
                "topic": title[:50],
                "category": "General",
                "tags": ["youtube", "video"],
                "key_terms": []
            }
