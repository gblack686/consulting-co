#!/usr/bin/env python3
"""
Digest Runner

Standalone script for running email classification and digest generation.
Designed to be called by Windows Task Scheduler or cron.

Usage:
    python digest_runner.py --action classify-and-digest --type morning
    python digest_runner.py --action classify-only
    python digest_runner.py --action digest-only --type evening
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = script_dir.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# Setup logging
log_dir = script_dir.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'digest_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_classification(max_messages: int = 100, auto_archive: bool = True):
    """Run email classification and archiving."""
    logger.info(f"Starting classification (max={max_messages}, auto_archive={auto_archive})")

    try:
        from scripts.auto_archive import AutoArchiver

        archiver = AutoArchiver()

        # Setup labels if needed
        archiver.setup_labels()

        # Build sent contacts if empty
        from scripts.supabase_gmail_client import SupabaseGmailClient
        supabase = SupabaseGmailClient()
        contacts_count = supabase.get_sent_contacts_count()

        if contacts_count == 0:
            logger.info("No sent contacts found, building...")
            archiver.build_sent_contacts(max_messages=500)

        # Process inbox
        stats = archiver.process_inbox(
            max_messages=max_messages,
            dry_run=False,
            auto_archive=auto_archive
        )

        logger.info(f"Classification complete: {stats.total_processed} processed, "
                   f"{stats.sales_archived} archived")

        return stats

    except Exception as e:
        logger.error(f"Classification failed: {e}", exc_info=True)
        return None


def run_digest(digest_type: str = 'now', hours_back: int = None):
    """Generate and send digest email."""
    logger.info(f"Starting digest generation (type={digest_type})")

    try:
        from scripts.digest_generator import DigestGenerator

        generator = DigestGenerator()

        success = generator.send_digest(
            digest_type=digest_type,
            preview=False,
            hours_back=hours_back
        )

        if success:
            logger.info(f"Digest sent successfully")
        else:
            logger.error(f"Digest send failed")

        return success

    except Exception as e:
        logger.error(f"Digest generation failed: {e}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Gmail digest runner for scheduled execution'
    )
    parser.add_argument(
        '--action',
        choices=['classify-only', 'digest-only', 'classify-and-digest'],
        default='classify-and-digest',
        help='Action to perform'
    )
    parser.add_argument(
        '--type',
        choices=['morning', 'afternoon', 'evening', 'now'],
        default='now',
        help='Digest type (determines time range)'
    )
    parser.add_argument(
        '--max-messages',
        type=int,
        default=100,
        help='Maximum messages to classify'
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Classify without archiving'
    )
    parser.add_argument(
        '--hours',
        type=int,
        help='Override hours to look back for digest'
    )

    args = parser.parse_args()

    logger.info(f"=== Gmail Digest Runner Started ({args.action}) ===")
    start_time = datetime.now()

    try:
        if args.action in ['classify-only', 'classify-and-digest']:
            run_classification(
                max_messages=args.max_messages,
                auto_archive=not args.no_archive
            )

        if args.action in ['digest-only', 'classify-and-digest']:
            run_digest(
                digest_type=args.type,
                hours_back=args.hours
            )

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== Completed in {elapsed:.1f}s ===")

    except Exception as e:
        logger.error(f"Runner failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
