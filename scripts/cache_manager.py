import json
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, Optional

class CacheManager:
    def __init__(self, cache_file: str = ".notion_cache.json"):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "last_sync": None,
            "posts": {},
            "media": {}
        }

    def save_cache(self):
        """Save cache data"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache_data, f, indent=2, default=str)

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
        return media.get(key)

    def cache_media(self, url: str, local_path: str):
        """Cache media file path using normalized media key"""
        key = self.normalize_media_key(url)
        self.cache_data.setdefault("media", {})[key] = local_path

    def update_last_sync(self):
        """Update last sync time"""
        self.cache_data["last_sync"] = datetime.now().isoformat()

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
