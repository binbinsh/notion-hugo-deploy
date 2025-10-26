#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from tqdm import tqdm

from notion_service import NotionClient
from hugo_converter import HugoConverter
from media_handler import MediaHandler
from logging_utils import setup_logging
from cache_manager import CacheManager

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


def test_notion_connection(notion_client: NotionClient) -> bool:
    """Test Notion connection"""
    print("🔍 Testing Notion connection...")

    result = notion_client.test_connection()

    if result['success']:
        db_info = result['database_info']
        print(f"✅ Successfully connected to Notion!")
        print(f"📊 Database Information:")
        print(f"   - Name: {db_info['title']}")
        print(f"   - ID: {db_info['id'][:8]}...{db_info['id'][-8:]}")
        print(f"   - Properties: {db_info['total_properties']}")
        print(f"   - Sample Posts: {db_info['sample_post_count']}")

        if result['warnings']:
            print(f"⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"   - {warning}")

        # Get statistics
        stats = notion_client.get_database_stats()
        if stats:
            print(f"📈 Database Statistics:")
            print(f"   - Published Posts: {stats.get('published_posts', 'Unknown')}")

        return True
    else:
        print(f"❌ Connection test failed!")
        if result['error']:
            print(f"   Error: {result['error']}")
        return False


def main():
    # Load environment variables
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Sync Notion posts to Hugo')
    parser.add_argument('--notion-token', default=os.getenv('NOTION_TOKEN'),
                        help='Notion API token')
    parser.add_argument('--database-id', default=os.getenv('NOTION_DATABASE_ID'),
                        help='Notion database ID')
    parser.add_argument('--content-dir', default='./content',
                        help='Hugo content directory')
    parser.add_argument('--static-dir', default='./static',
                        help='Hugo static directory')
    parser.add_argument('--clean', action='store_true',
                        help='Clean existing posts before sync')

    args = parser.parse_args()

    # Validate required parameters
    if not args.notion_token or not args.database_id:
        logger.error("NOTION_TOKEN and NOTION_DATABASE_ID are required")
        sys.exit(1)

    try:
        # Initialize components
        notion_client = NotionClient(args.notion_token, args.database_id)
        cache_manager = CacheManager()
        media_handler = MediaHandler(args.static_dir, cache_manager=cache_manager)
        hugo_converter = HugoConverter(args.content_dir, media_handler)

        # Test connection
        if not test_notion_connection(notion_client):
            sys.exit(1)

        # Clean existing posts
        if args.clean:
            logger.info("Cleaning existing posts...")
            hugo_converter.clean_posts_directory()

        # Fetch Notion posts (includes blocks to regenerate Markdown each run)
        logger.info("Fetching posts from Notion...")
        posts = notion_client.get_published_posts()
        logger.info(f"Found {len(posts)} published posts")

        # Build ID -> slug map for internal link rewriting
        id_to_slug = {}
        for p in posts:
            if getattr(p, 'id', None) and getattr(p, 'slug', None):
                # Store both hyphenated and compact IDs
                compact_id = p.id.replace('-', '')
                id_to_slug[p.id] = p.slug
                id_to_slug[compact_id] = p.slug

        # Provide mapping to converter
        if hasattr(hugo_converter, 'set_id_to_slug_mapping'):
            hugo_converter.set_id_to_slug_mapping(id_to_slug)

        # Convert posts
        success_count = 0
        with tqdm(total=len(posts), desc="Converting posts") as pbar:
            for post in posts:
                pbar.set_description(f"Converting: {post.title[:30]}...")
                if hugo_converter.convert_post(post):
                    success_count += 1
                    # Update per-post cache after successful conversion
                    cache_manager.update_post_cache(post.id, post.last_edited)
                pbar.update(1)
            else:
                logger.error(f"Failed to convert: {post.title}")

        # Summarize results
        logger.info(f"Successfully converted {success_count}/{len(posts)} posts")

        # Update last sync and persist cache
        cache_manager.update_last_sync()
        cache_manager.save_cache()

        if success_count < len(posts):
            sys.exit(1)

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
