# /***************************************************************************
#  SecInterp
#                                  A QGIS plugin
#  Data extraction for geological interpretation.
#                               -------------------
#         begin                : 2025-11-15
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sec_interp.logger_config import get_logger

from .types import GeologyData, ProfileData, StructureData


logger = get_logger(__name__)


class DataCache:
    """Cache for storing processed profile data.

    This cache stores topographic, geological, and structural profile data
    to avoid redundant processing when parameters haven't changed.
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._topo_cache: dict[str, ProfileData] = {}
        self._geol_cache: dict[str, GeologyData] = {}
        self._struct_cache: dict[str, StructureData] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def get_cache_key(self, params: dict[str, Any]) -> str:
        """Generate a unique cache key from parameters.

        Args:
            params: Dictionary of input parameters

        Returns:
            String representation of the parameters hash
        """
        # Create a stable string representation
        # Exclude QGIS objects that change memory address but represent same data
        # For now, we use a simple string representation of the params dict
        # In a production environment, we might want to hash the actual data IDs

        # Filter out objects that shouldn't be part of the key or convert them
        key_parts = []
        for k, v in sorted(params.items()):
            if k.endswith("_obj") or k in [
                "raster_layer",
                "outcrop_layer",
                "structural_layer",
                "crossline_layer",
            ]:
                # Skip raw QGIS objects or use their ID/source if available
                if hasattr(v, "id"):
                    key_parts.append(f"{k}:{v.id()}")
                elif hasattr(v, "source"):
                    key_parts.append(f"{k}:{v.source()}")
                else:
                    key_parts.append(f"{k}:{v!s}")
            else:
                key_parts.append(f"{k}:{v!s}")

        import hashlib

        return hashlib.md5("".join(key_parts).encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get all cached data for a key.

        Args:
            key: Cache key

        Returns:
            Dictionary with profile_data, geol_data, struct_data or None if not found
        """
        if key not in self._topo_cache:
            return None

        return {
            "profile_data": self._topo_cache.get(key),
            "geol_data": self._geol_cache.get(key),
            "struct_data": self._struct_cache.get(key),
        }

    def set(self, key: str, data: dict[str, Any]) -> None:
        """Set all cache data for a key.

        Args:
            key: Cache key
            data: Dictionary containing profile_data, geol_data, etc.
        """
        if "profile_data" in data:
            self._topo_cache[key] = data["profile_data"]
        if "geol_data" in data:
            self._geol_cache[key] = data["geol_data"]
        if "struct_data" in data:
            self._struct_cache[key] = data["struct_data"]

    def get_topographic_profile(self, key: str) -> Optional[ProfileData]:
        """Get cached topographic profile data.

        Args:
            key: Cache key (typically hash of input parameters)

        Returns:
            Cached profile data or None if not found
        """
        return self._topo_cache.get(key)

    def set_topographic_profile(self, key: str, data: ProfileData) -> None:
        """Store topographic profile data in cache.

        Args:
            key: Cache key
            data: Profile data to cache
        """
        self._topo_cache[key] = data

    def get_geological_profile(self, key: str) -> Optional[GeologyData]:
        """Get cached geological profile data.

        Args:
            key: Cache key

        Returns:
            Cached geology data or None if not found
        """
        return self._geol_cache.get(key)

    def set_geological_profile(self, key: str, data: GeologyData) -> None:
        """Store geological profile data in cache.

        Args:
            key: Cache key
            data: Geology data to cache
        """
        self._geol_cache[key] = data

    def get_structural_data(self, key: str) -> Optional[StructureData]:
        """Get cached structural data.

        Args:
            key: Cache key

        Returns:
            Cached structure data or None if not found
        """
        return self._struct_cache.get(key)

    def set_structural_data(self, key: str, data: StructureData) -> None:
        """Store structural data in cache.

        Args:
            key: Cache key
            data: Structure data to cache
        """
        self._struct_cache[key] = data

    def get_metadata(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached metadata for a profile.

        Args:
            key: Cache key

        Returns:
            Cached metadata or None if not found
        """
        return self._metadata.get(key)

    def set_metadata(self, key: str, metadata: dict[str, Any]) -> None:
        """Store metadata for a profile.

        Args:
            key: Cache key
            metadata: Metadata dictionary to cache
        """
        self._metadata[key] = metadata

    def invalidate(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries.

        Args:
            pattern: Optional pattern to match keys. If None, clears all cache.
        """
        if pattern is None:
            # Clear all caches
            self._topo_cache.clear()
            self._geol_cache.clear()
            self._struct_cache.clear()
            self._metadata.clear()
        else:
            # Clear entries matching pattern
            self._topo_cache = {
                k: v for k, v in self._topo_cache.items() if pattern not in k
            }
            self._geol_cache = {
                k: v for k, v in self._geol_cache.items() if pattern not in k
            }
            self._struct_cache = {
                k: v for k, v in self._struct_cache.items() if pattern not in k
            }
            self._metadata = {
                k: v for k, v in self._metadata.items() if pattern not in k
            }

    def clear(self) -> None:
        """Clear all cached data."""
        self.invalidate()

    def get_cache_size(self) -> dict[str, int]:
        """Get the size of each cache.

        Returns:
            Dictionary with cache names and their sizes
        """
        return {
            "topographic": len(self._topo_cache),
            "geological": len(self._geol_cache),
            "structural": len(self._struct_cache),
            "metadata": len(self._metadata),
        }
