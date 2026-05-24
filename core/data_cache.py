"""Cache system for SecInterp data.

Provides a hash-based caching mechanism for geological and topographic data.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.interfaces.cache_interface import ICacheService
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DataCache(ICacheService):
    """Memory-based cache service for storing processed profile data.

    Implements ICacheService. Supports categorized buckets ('topo', 'geol', 'struct', 'drill'),
    Time-To-Live (TTL) expiration, and arbitrary metadata (e.g., for LOD tracking).
    """

    DEFAULT_TTL_SECONDS = 3600

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("DataCache", message)  # type: ignore[no-any-return]

    def __init__(self, default_ttl: int = DEFAULT_TTL_SECONDS) -> None:
        """Initialize the data cache.

        Args:
            default_ttl: Default Time-To-Live in seconds for new entries.

        """
        # Buckets: 'topo', 'geol', 'struct', 'drill'
        self._buckets: dict[str, dict[str, dict[str, Any]]] = {
            "topo": {},
            "geol": {},
            "struct": {},
            "drill": {},
        }
        self.default_ttl = default_ttl
        logger.debug(f"CacheService initialized (Default TTL: {default_ttl}s)")

    def get_cache_key(self, params: dict[str, Any]) -> str:
        """Generate a unique MD5 hash key from input parameters.

        Args:
            params: Dictionary of parameters to hash.

        Returns:
            The generated MD5 hash string.

        """
        key_parts = []
        for k, v in sorted(params.items()):
            # Filter objects by ID or string representation
            if hasattr(v, "id"):
                key_parts.append(f"{k}:{v.id()}")
            elif hasattr(v, "source"):
                key_parts.append(f"{k}:{v.source()}")
            else:
                key_parts.append(f"{k}:{v!s}")

        return hashlib.sha256("".join(key_parts).encode("utf-8")).hexdigest()

    def get(self, bucket: str, key: str) -> Any | None:
        """Retrieve data from a specific cache bucket if not expired.

        Args:
            bucket: Name of the cache category (e.g., 'topo').
            key: Unique hash key for the entry.

        Returns:
            The cached data if valid and found, else None.

        """
        if bucket not in self._buckets:
            return None

        entry = self._buckets[bucket].get(key)
        if not entry:
            return None

        # Check TTL
        expiry = entry.get("expiry")
        if expiry and time.time() > expiry:
            logger.debug(f"Cache miss (TTL expired): {bucket}/{key}")
            del self._buckets[bucket][key]
            return None

        return entry.get("data")

    def set(
        self, bucket: str, key: str, data: Any, metadata: dict | None = None
    ) -> None:
        """Store data in a specific cache bucket with optional metadata.

        Args:
            bucket: Name of the cache category.
            key: Unique hash key for the entry.
            data: The data object to be cached.
            metadata: Optional dictionary for TTL or Level of Detail information.

        """
        if bucket not in self._buckets:
            self._buckets[bucket] = {}

        ttl = (metadata or {}).get("ttl", self.default_ttl)
        expiry = time.time() + ttl if ttl > 0 else None

        self._buckets[bucket][key] = {
            "data": data,
            "expiry": expiry,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }

    def invalidate(self, bucket: str | None = None, key: str | None = None) -> None:
        """Remove entries from the cache selectively or entirely.

        Args:
            bucket: Optional name of the bucket to invalidate.
            key: Optional specific entry key to remove within the bucket.

        """
        if bucket and bucket in self._buckets:
            if key:
                if key in self._buckets[bucket]:
                    del self._buckets[bucket][key]
                    logger.debug(f"Cache invalidated: {bucket}/{key}")
            else:
                self._buckets[bucket].clear()
                logger.debug(f"Bucket invalidated: {bucket}")
        elif not bucket:
            for _b_name, b_data in self._buckets.items():
                b_data.clear()
            logger.debug("Cache cleared entirely")

    def clear(self) -> None:
        """Clear all entries across all cache buckets."""
        self.invalidate()

    def get_metadata(self, bucket: str, key: str) -> dict[str, Any] | None:
        """Retrieve the metadata associated with a cached entry.

        Args:
            bucket: Name of the cache category.
            key: Unique hash key for the entry.

        Returns:
            Metadata dictionary if found, else None.

        """
        if bucket in self._buckets and key in self._buckets[bucket]:
            return self._buckets[bucket][key].get("metadata")
        return None

    def get_cache_size(self) -> dict[str, int]:
        """Get the number of entries in each bucket.

        Returns:
            Dictionary mapping bucket names to entry counts.

        """
        return {name: len(items) for name, items in self._buckets.items()}
