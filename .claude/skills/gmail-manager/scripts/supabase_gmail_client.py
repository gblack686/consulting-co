#!/usr/bin/env python3
"""
Supabase Gmail Client

Manages storage and retrieval of Gmail contacts, domains, summaries, and filters in Supabase.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from supabase import create_client

from .domain_extractor import ExtractedContact


class SupabaseGmailClient:
    """Manages Gmail data storage in Supabase."""

    def __init__(self, url: str = None, key: str = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase URL
            key: Supabase service key
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required"
            )

        self.client = create_client(self.url, self.key)

    # =========================================================================
    # Contact Operations
    # =========================================================================

    def upsert_contact(self, contact: ExtractedContact) -> bool:
        """
        Insert or update a contact.

        Args:
            contact: ExtractedContact object

        Returns:
            True if successful
        """
        try:
            # Check if contact exists
            result = self.client.table("gmail_contacts").select("*").eq(
                "email_address", contact.email_address
            ).execute()

            if result.data:
                # Update existing
                existing = result.data[0]
                update_data = {
                    "last_seen_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "emails_received": existing['emails_received'] + contact.emails_received,
                    "emails_sent": existing['emails_sent'] + contact.emails_sent,
                }

                # Update source type if needed
                if existing['source_type'] != contact.source_type:
                    if existing['source_type'] != 'both':
                        update_data['source_type'] = 'both'

                # Update display name if we have a new one
                if contact.display_name and not existing.get('display_name'):
                    update_data['display_name'] = contact.display_name

                # Update newsletter status
                if contact.is_newsletter and not existing['is_newsletter']:
                    update_data['is_newsletter'] = True

                self.client.table("gmail_contacts").update(update_data).eq(
                    "email_address", contact.email_address
                ).execute()
            else:
                # Insert new
                insert_data = {
                    "email_address": contact.email_address,
                    "domain": contact.domain,
                    "display_name": contact.display_name,
                    "source_type": contact.source_type,
                    "first_seen_at": contact.first_seen_at.isoformat(),
                    "last_seen_at": contact.last_seen_at.isoformat(),
                    "emails_received": contact.emails_received,
                    "emails_sent": contact.emails_sent,
                    "is_newsletter": contact.is_newsletter,
                    "is_unsubscribed": False,
                    "category": contact.category,
                }
                self.client.table("gmail_contacts").insert(insert_data).execute()

            return True
        except Exception as e:
            print(f"Error upserting contact {contact.email_address}: {e}")
            return False

    def upsert_contacts_batch(self, contacts: List[ExtractedContact]) -> Dict[str, int]:
        """
        Batch upsert multiple contacts.

        Args:
            contacts: List of ExtractedContact objects

        Returns:
            Dict with 'inserted', 'updated', 'errors' counts
        """
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}

        for contact in contacts:
            try:
                # Check existence
                result = self.client.table("gmail_contacts").select("email_address").eq(
                    "email_address", contact.email_address
                ).execute()

                if result.data:
                    stats['updated'] += 1
                else:
                    stats['inserted'] += 1

                if self.upsert_contact(contact):
                    pass  # Already counted
                else:
                    stats['errors'] += 1
            except Exception as e:
                print(f"Error processing contact {contact.email_address}: {e}")
                stats['errors'] += 1

        return stats

    def get_contacts(
        self,
        source_type: str = None,
        category: str = None,
        is_newsletter: bool = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get contacts with optional filters.

        Args:
            source_type: Filter by source ('inbox', 'sent', 'both')
            category: Filter by category
            is_newsletter: Filter newsletters
            limit: Max results
            offset: Pagination offset

        Returns:
            List of contact records
        """
        try:
            query = self.client.table("gmail_contacts").select("*")

            if source_type:
                query = query.eq("source_type", source_type)
            if category:
                query = query.eq("category", category)
            if is_newsletter is not None:
                query = query.eq("is_newsletter", is_newsletter)

            query = query.order("last_seen_at", desc=True)
            query = query.range(offset, offset + limit - 1)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting contacts: {e}")
            return []

    def get_contact_by_email(self, email_address: str) -> Optional[Dict[str, Any]]:
        """Get a single contact by email."""
        try:
            result = self.client.table("gmail_contacts").select("*").eq(
                "email_address", email_address.lower()
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting contact: {e}")
            return None

    def mark_unsubscribed(self, email_address: str) -> bool:
        """Mark a contact as unsubscribed."""
        try:
            self.client.table("gmail_contacts").update({
                "is_unsubscribed": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("email_address", email_address.lower()).execute()
            return True
        except Exception as e:
            print(f"Error marking unsubscribed: {e}")
            return False

    # =========================================================================
    # Domain Operations
    # =========================================================================

    def upsert_domain(self, domain_data: Dict[str, Any]) -> bool:
        """
        Insert or update a domain.

        Args:
            domain_data: Dict with domain, total_contacts, emails_received, etc.

        Returns:
            True if successful
        """
        try:
            domain = domain_data['domain']

            result = self.client.table("gmail_domains").select("*").eq(
                "domain", domain
            ).execute()

            if result.data:
                # Update
                existing = result.data[0]
                update_data = {
                    "total_contacts": domain_data.get('total_contacts', existing['total_contacts']),
                    "emails_received": existing['emails_received'] + domain_data.get('emails_received', 0),
                    "emails_sent": existing['emails_sent'] + domain_data.get('emails_sent', 0),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                if domain_data.get('category'):
                    update_data['category'] = domain_data['category']

                self.client.table("gmail_domains").update(update_data).eq(
                    "domain", domain
                ).execute()
            else:
                # Insert
                insert_data = {
                    "domain": domain,
                    "total_contacts": domain_data.get('total_contacts', 1),
                    "emails_received": domain_data.get('emails_received', 0),
                    "emails_sent": domain_data.get('emails_sent', 0),
                    "category": domain_data.get('category'),
                    "is_blocked": domain_data.get('is_blocked', False),
                }
                self.client.table("gmail_domains").insert(insert_data).execute()

            return True
        except Exception as e:
            print(f"Error upserting domain {domain_data.get('domain')}: {e}")
            return False

    def get_domains(
        self,
        category: str = None,
        is_blocked: bool = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get domains with optional filters."""
        try:
            query = self.client.table("gmail_domains").select("*")

            if category:
                query = query.eq("category", category)
            if is_blocked is not None:
                query = query.eq("is_blocked", is_blocked)

            query = query.order("emails_received", desc=True).limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting domains: {e}")
            return []

    def block_domain(self, domain: str) -> bool:
        """Mark a domain as blocked."""
        try:
            self.client.table("gmail_domains").update({
                "is_blocked": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("domain", domain.lower()).execute()
            return True
        except Exception as e:
            print(f"Error blocking domain: {e}")
            return False

    # =========================================================================
    # Email Summary Operations
    # =========================================================================

    def store_summary(self, summary_data: Dict[str, Any]) -> bool:
        """
        Store an email summary.

        Args:
            summary_data: Dict with message_id, summary, key_points, etc.

        Returns:
            True if successful
        """
        try:
            # Check if summary exists
            result = self.client.table("gmail_email_summaries").select("id").eq(
                "message_id", summary_data['message_id']
            ).execute()

            if result.data:
                # Update
                self.client.table("gmail_email_summaries").update(summary_data).eq(
                    "message_id", summary_data['message_id']
                ).execute()
            else:
                # Insert
                self.client.table("gmail_email_summaries").insert(summary_data).execute()

            return True
        except Exception as e:
            print(f"Error storing summary: {e}")
            return False

    def get_summaries(
        self,
        sender_email: str = None,
        thread_id: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get email summaries with optional filters."""
        try:
            query = self.client.table("gmail_email_summaries").select("*")

            if sender_email:
                query = query.eq("sender_email", sender_email)
            if thread_id:
                query = query.eq("thread_id", thread_id)

            query = query.order("received_at", desc=True).limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting summaries: {e}")
            return []

    def summary_exists(self, message_id: str) -> bool:
        """Check if a summary exists for a message."""
        try:
            result = self.client.table("gmail_email_summaries").select("id").eq(
                "message_id", message_id
            ).execute()
            return bool(result.data)
        except Exception:
            return False

    # =========================================================================
    # Filter Tracking Operations
    # =========================================================================

    def store_filter(self, filter_data: Dict[str, Any]) -> bool:
        """Store a Gmail filter record."""
        try:
            self.client.table("gmail_filters").insert(filter_data).execute()
            return True
        except Exception as e:
            print(f"Error storing filter: {e}")
            return False

    def get_filters(self, filter_type: str = None) -> List[Dict[str, Any]]:
        """Get stored filter records."""
        try:
            query = self.client.table("gmail_filters").select("*")

            if filter_type:
                query = query.eq("filter_type", filter_type)

            query = query.eq("is_active", True)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting filters: {e}")
            return []

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        try:
            contacts = self.client.table("gmail_contacts").select(
                "id", count="exact"
            ).execute()

            domains = self.client.table("gmail_domains").select(
                "id", count="exact"
            ).execute()

            summaries = self.client.table("gmail_email_summaries").select(
                "id", count="exact"
            ).execute()

            newsletters = self.client.table("gmail_contacts").select(
                "id", count="exact"
            ).eq("is_newsletter", True).execute()

            return {
                "total_contacts": contacts.count or 0,
                "total_domains": domains.count or 0,
                "total_summaries": summaries.count or 0,
                "newsletter_contacts": newsletters.count or 0,
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    # =========================================================================
    # Email Classification Operations
    # =========================================================================

    def store_classification(self, classification_data: Dict[str, Any]) -> bool:
        """
        Store an email classification result.

        Args:
            classification_data: Dict with message_id, classification, confidence, etc.

        Returns:
            True if successful
        """
        try:
            # Check if classification exists
            result = self.client.table("gmail_email_classifications").select("id").eq(
                "message_id", classification_data['message_id']
            ).execute()

            if result.data:
                # Update
                update_data = {
                    "classification": classification_data.get('classification'),
                    "confidence": classification_data.get('confidence'),
                    "reasoning": classification_data.get('reasoning'),
                    "is_important": classification_data.get('is_important'),
                    "action_taken": classification_data.get('action_taken'),
                    "label_applied": classification_data.get('label_applied'),
                }
                self.client.table("gmail_email_classifications").update(update_data).eq(
                    "message_id", classification_data['message_id']
                ).execute()
            else:
                # Insert
                self.client.table("gmail_email_classifications").insert(classification_data).execute()

            return True
        except Exception as e:
            print(f"Error storing classification: {e}")
            return False

    def get_classification(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get classification for a specific message."""
        try:
            result = self.client.table("gmail_email_classifications").select("*").eq(
                "message_id", message_id
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting classification: {e}")
            return None

    def get_classifications(
        self,
        classification: str = None,
        is_important: bool = None,
        limit: int = 100,
        since_hours: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get classifications with optional filters.

        Args:
            classification: Filter by classification type
            is_important: Filter by importance
            limit: Max results
            since_hours: Only get classifications from last N hours

        Returns:
            List of classification records
        """
        try:
            query = self.client.table("gmail_email_classifications").select("*")

            if classification:
                query = query.eq("classification", classification)
            if is_important is not None:
                query = query.eq("is_important", is_important)
            if since_hours:
                from datetime import timedelta
                cutoff = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
                query = query.gte("created_at", cutoff)

            query = query.order("created_at", desc=True).limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting classifications: {e}")
            return []

    def get_unclassified_count(self, since_hours: int = 24) -> int:
        """Get count of emails not yet classified in time period."""
        try:
            from datetime import timedelta
            cutoff = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()

            result = self.client.table("gmail_email_classifications").select(
                "id", count="exact"
            ).gte("created_at", cutoff).execute()

            return result.count or 0
        except Exception as e:
            print(f"Error getting unclassified count: {e}")
            return 0

    # =========================================================================
    # Sent Contacts Operations (Known Contacts)
    # =========================================================================

    def upsert_sent_contact(self, email_address: str, display_name: str = None) -> bool:
        """
        Add or update a sent contact (for known sender detection).

        Args:
            email_address: Email address sent to
            display_name: Optional display name

        Returns:
            True if successful
        """
        try:
            email_lower = email_address.lower()

            result = self.client.table("gmail_sent_contacts").select("*").eq(
                "email_address", email_lower
            ).execute()

            if result.data:
                # Update
                existing = result.data[0]
                update_data = {
                    "last_sent_at": datetime.utcnow().isoformat(),
                    "emails_sent_count": existing.get('emails_sent_count', 0) + 1,
                }
                if display_name and not existing.get('display_name'):
                    update_data['display_name'] = display_name

                self.client.table("gmail_sent_contacts").update(update_data).eq(
                    "email_address", email_lower
                ).execute()
            else:
                # Insert
                insert_data = {
                    "email_address": email_lower,
                    "display_name": display_name,
                    "first_sent_at": datetime.utcnow().isoformat(),
                    "last_sent_at": datetime.utcnow().isoformat(),
                    "emails_sent_count": 1,
                    "is_trusted": True,
                }
                self.client.table("gmail_sent_contacts").insert(insert_data).execute()

            return True
        except Exception as e:
            print(f"Error upserting sent contact: {e}")
            return False

    def get_all_sent_contacts(self) -> set:
        """
        Get all sent contact email addresses as a set.
        Used for efficient "known sender" lookups.

        Returns:
            Set of lowercase email addresses
        """
        try:
            all_contacts = set()
            offset = 0
            limit = 1000

            while True:
                result = self.client.table("gmail_sent_contacts").select(
                    "email_address"
                ).range(offset, offset + limit - 1).execute()

                if not result.data:
                    break

                for row in result.data:
                    all_contacts.add(row['email_address'].lower())

                if len(result.data) < limit:
                    break

                offset += limit

            return all_contacts
        except Exception as e:
            print(f"Error getting sent contacts: {e}")
            return set()

    def is_known_sender(self, email_address: str) -> bool:
        """Check if an email address is in sent contacts."""
        try:
            result = self.client.table("gmail_sent_contacts").select("id").eq(
                "email_address", email_address.lower()
            ).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error checking known sender: {e}")
            return False

    def get_sent_contacts_count(self) -> int:
        """Get total count of sent contacts."""
        try:
            result = self.client.table("gmail_sent_contacts").select(
                "id", count="exact"
            ).execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting sent contacts count: {e}")
            return 0

    # =========================================================================
    # Digest Log Operations
    # =========================================================================

    def create_digest_log(
        self,
        digest_type: str,
        recipient_email: str,
        emails_summarized: int = 0,
        important_count: int = 0,
        sales_archived_count: int = 0
    ) -> Optional[int]:
        """
        Create a new digest log entry.

        Args:
            digest_type: 'morning', 'afternoon', 'evening', or 'now'
            recipient_email: Email address digest was sent to
            emails_summarized: Total emails in digest
            important_count: Count of important emails
            sales_archived_count: Count of sales emails archived

        Returns:
            Digest log ID or None if failed
        """
        try:
            insert_data = {
                "digest_type": digest_type,
                "recipient_email": recipient_email,
                "emails_summarized": emails_summarized,
                "important_count": important_count,
                "sales_archived_count": sales_archived_count,
                "status": "pending",
            }

            result = self.client.table("gmail_digest_log").insert(insert_data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Error creating digest log: {e}")
            return None

    def update_digest_log(
        self,
        digest_id: int,
        status: str,
        sent_at: datetime = None
    ) -> bool:
        """
        Update a digest log entry.

        Args:
            digest_id: ID of the digest log
            status: New status ('sent', 'failed', 'pending')
            sent_at: Timestamp when sent

        Returns:
            True if successful
        """
        try:
            update_data = {"status": status}
            if sent_at:
                update_data["sent_at"] = sent_at.isoformat()

            self.client.table("gmail_digest_log").update(update_data).eq(
                "id", digest_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating digest log: {e}")
            return False

    def get_last_digest(self, digest_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Get the most recent digest log entry.

        Args:
            digest_type: Optional filter by type

        Returns:
            Digest log record or None
        """
        try:
            query = self.client.table("gmail_digest_log").select("*")

            if digest_type:
                query = query.eq("digest_type", digest_type)

            query = query.eq("status", "sent").order("sent_at", desc=True).limit(1)

            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting last digest: {e}")
            return None

    def get_digest_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent digest history."""
        try:
            result = self.client.table("gmail_digest_log").select("*").order(
                "created_at", desc=True
            ).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting digest history: {e}")
            return []

    # =========================================================================
    # Enhanced Statistics
    # =========================================================================

    def get_classification_stats(self, since_hours: int = 24) -> Dict[str, Any]:
        """
        Get classification statistics.

        Args:
            since_hours: Time period in hours

        Returns:
            Dict with stats by classification type
        """
        try:
            from datetime import timedelta
            cutoff = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()

            # Get all classifications in period
            result = self.client.table("gmail_email_classifications").select(
                "classification"
            ).gte("created_at", cutoff).execute()

            stats = {
                'total': 0,
                'sales_solicitation': 0,
                'transactional': 0,
                'human_correspondence': 0,
                'newsletter_subscribed': 0,
                'automated_notification': 0,
            }

            if result.data:
                for row in result.data:
                    stats['total'] += 1
                    classification = row.get('classification', 'unknown')
                    if classification in stats:
                        stats[classification] += 1

            return stats
        except Exception as e:
            print(f"Error getting classification stats: {e}")
            return {}
