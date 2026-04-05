"""Gmail Manager Skill - Scripts package."""

from .gmail_oauth_handler import GmailOAuth2Handler
from .gmail_client import GmailClient
from .domain_extractor import DomainExtractor, ExtractedContact
from .supabase_gmail_client import SupabaseGmailClient
from .email_summarizer import EmailSummarizer
from .newsletter_manager import NewsletterManager
from .draft_generator import DraftGenerator
from .email_classifier import EmailClassifier, ClassificationResult
from .auto_archive import AutoArchiver
from .digest_generator import DigestGenerator

__all__ = [
    'GmailOAuth2Handler',
    'GmailClient',
    'DomainExtractor',
    'ExtractedContact',
    'SupabaseGmailClient',
    'EmailSummarizer',
    'NewsletterManager',
    'DraftGenerator',
    'EmailClassifier',
    'ClassificationResult',
    'AutoArchiver',
    'DigestGenerator',
]
