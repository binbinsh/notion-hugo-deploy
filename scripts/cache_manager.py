import json
import os
import re
import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional

class CacheManager:
    def __init__(self, cache_file: str = ".notion_cache.json"):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self.logger = logging.getLogger(__name__)

    def _load_cache(self) -> Dict:
        """Load cache data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Best-effort sanity defaults
                    data.setdefault("last_sync", None)
                    data.setdefault("posts", {})
                    data.setdefault("media", {})
                    logging.getLogger(__name__).debug(
                        f"Loaded cache from {self.cache_file}: posts={len(data.get('posts', {}))}, media={len(data.get('media', {}))}"
                    )
                    return data
            except Exception:
                # If corrupt, fall through to new cache
                logging.getLogger(__name__).warning(f"Failed to read cache file {self.cache_file}; starting fresh")
        logging.getLogger(__name__).debug("Initialized new in-memory cache")
        return {
            "last_sync": None,
            "posts": {},
            "media": {}
        }

    def save_cache(self):
        """Save cache data"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache_data, f, indent=2, default=str)
        logging.getLogger(__name__).debug(
            f"Saved cache to {self.cache_file}: posts={len(self.cache_data.get('posts', {}))}, media={len(self.cache_data.get('media', {}))}"
        )

    def should_update_post(self, post_id: str, last_edited: datetime) -> bool:
        """Check whether a post needs updating"""
        if post_id not in self.cache_data["posts"]:
            return True

        cached_time = datetime.fromisoformat(self.cache_data["posts"][post_id])
        return last_edited > cached_time

    def update_post_cache(self, post_id: str, last_edited: datetime):
        """Update post cache"""
        self.cache_data["posts"][post_id] = last_edited.isoformat()

    def get_cached_media(self, url: str) -> Optional[str]:
        """Get cached media file path by normalized media key."""
        key = self.normalize_media_key(url)
        media = self.cache_data.get("media", {})
        value = media.get(key)
        if value:
            logging.getLogger(__name__).debug(f"Cache lookup HIT for media key {key} -> {value}")
        else:
            logging.getLogger(__name__).debug(f"Cache lookup MISS for media key {key}")
        return value

    def cache_media(self, url: str, local_path: str):
        """Cache media file path using normalized media key"""
        key = self.normalize_media_key(url)
        self.cache_data.setdefault("media", {})[key] = local_path
        logging.getLogger(__name__).debug(f"Cached media key {key} -> {local_path}")

    def update_last_sync(self):
        """Update last sync time"""
        self.cache_data["last_sync"] = datetime.now().isoformat()
        logging.getLogger(__name__).debug(f"Updated last_sync -> {self.cache_data['last_sync']}")

    def get_last_sync(self) -> Optional[datetime]:
        """Get last sync time as datetime if present"""
        value = self.cache_data.get("last_sync")
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def normalize_media_key(self, url: str) -> str:
        """Return a stable key for media URLs.

        - Notion-hosted: notion:<uuid>
        - External: url:<md5(url)>
        """
        m = re.search(r"secure\.notion-static\.com/([0-9a-fA-F\-]{36})/", url)
        if m:
            return f"notion:{m.group(1).lower()}"
        return f"url:{hashlib.md5(url.encode()).hexdigest()}"
