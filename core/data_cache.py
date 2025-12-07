# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SecInterp
                                 A QGIS plugin
 Data extraction for geological interpretation
                              -------------------
        begin                : 2025-11-15
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Juan M Bernales
        email                : juanbernales@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from sec_interp.logger_config import get_logger
from typing import Optional, Dict, Any
from .types import ProfileData, GeologyData, StructureData


logger = get_logger(__name__)


class DataCache:
    """Cache for storing processed profile data.
    
    This cache stores topographic, geological, and structural profile data
    to avoid redundant processing when parameters haven't changed.
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._topo_cache: Dict[str, ProfileData] = {}
        self._geol_cache: Dict[str, GeologyData] = {}
        self._struct_cache: Dict[str, StructureData] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

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

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached metadata for a profile.
        
        Args:
            key: Cache key
            
        Returns:
            Cached metadata or None if not found
        """
        return self._metadata.get(key)

    def set_metadata(self, key: str, metadata: Dict[str, Any]) -> None:
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
            self._topo_cache = {k: v for k, v in self._topo_cache.items() if pattern not in k}
            self._geol_cache = {k: v for k, v in self._geol_cache.items() if pattern not in k}
            self._struct_cache = {k: v for k, v in self._struct_cache.items() if pattern not in k}
            self._metadata = {k: v for k, v in self._metadata.items() if pattern not in k}

    def clear(self) -> None:
        """Clear all cached data."""
        self.invalidate()

    def get_cache_size(self) -> Dict[str, int]:
        """Get the size of each cache.
        
        Returns:
            Dictionary with cache names and their sizes
        """
        return {
            'topographic': len(self._topo_cache),
            'geological': len(self._geol_cache),
            'structural': len(self._struct_cache),
            'metadata': len(self._metadata),
        }
