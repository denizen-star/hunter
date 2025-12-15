"""Simple file-based JSON cache utilities used by heavy analytics endpoints."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from app.utils.file_utils import ensure_dir_exists


def is_cache_stale(cache_path: Path, ttl_seconds: int = 300) -> bool:
    """
    Return True if the cache file should be regenerated.

    A cache entry is considered stale if:
    - The file does not exist, or
    - The file's modification time is older than ttl_seconds.
    """
    if not cache_path.exists():
        return True

    try:
        mtime = cache_path.stat().st_mtime
    except OSError:
        # If we can't stat the file for any reason, treat it as stale.
        return True

    age_seconds = time.time() - mtime
    return age_seconds > ttl_seconds


def get_cached_json(cache_path: Path) -> Optional[Any]:
    """Load JSON from cache_path if it exists; return None on any failure."""
    if not cache_path.exists():
        return None

    try:
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If the cache is unreadable or invalid JSON, ignore it.
        return None


def save_cached_json(cache_path: Path, data: Any) -> None:
    """Persist data as JSON to cache_path, creating parent directories as needed."""
    ensure_dir_exists(cache_path.parent)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


