from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class ICacheService(Protocol):
    """Abstract protocol for the Processing Data Cache Service."""

    def get(self, bucket: str, key: str) -> Optional[Any]:
        """Retrieve data from a specific cache bucket.

        Args:
            bucket: The cache category (e.g., 'topo', 'geol').
            key: Unique key for the parameter set.

        Returns:
            The cached data or None if not found or expired.
        """
        ...

    def set(
        self, bucket: str, key: str, data: Any, metadata: Optional[dict] = None
    ) -> None:
        """Store data in a specific cache bucket.

        Args:
            bucket: The cache category.
            key: Unique key for the parameter set.
            data: The data to cache.
            metadata: Optional metadata (e.g., TTL, LOD info).
        """
        ...

    def invalidate(self, bucket: Optional[str] = None, key: Optional[str] = None) -> None:
        """Invalidate cache entries.

        Args:
            bucket: If provided, only invalidate this bucket.
            key: If provided, only invalidate this specific key.
        """
        ...

    def clear(self) -> None:
        """Clear the entire cache."""
        ...

    def get_metadata(self, bucket: str, key: str) -> Optional[dict[str, Any]]:
        """Retrieve metadata for a cached entry.

        Args:
            bucket: The cache category.
            key: Unique key for the entry.

        Returns:
            Dictionary containing entry metadata or None if not found.
        """
        ...
