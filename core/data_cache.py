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

logger = get_logger(__name__)


class DataCache:
    """Cache for processed profile data to improve performance.
    
    Caches processed data to avoid re-computation when only
    visualization parameters (vert_exag, dip_scale) change.
    """

    def __init__(self):
        """Initialize empty cache."""
        self._cache = {}
        self._cache_key = None

    def get_cache_key(self, values):
        """Generate cache key from data-affecting input values.
        
        Only includes parameters that affect data processing,
        not visualization parameters like vert_exag or dip_scale.
        
        Args:
            values: Dictionary of input values from dialog
            
        Returns:
            Hash key for cache lookup
        """
        # Only include data-affecting parameters
        key_params = {
            'raster_layer': id(values.get('raster_layer_obj')),
            'line_layer': id(values.get('line_layer_obj')),
            'outcrop_layer': id(values.get('outcrop_layer_obj')),
            'structural_layer': id(values.get('structural_layer_obj')),
            'buffer': values.get('buffer'),
            'selected_band': values.get('selected_band'),
            'outcrop_field': values.get('outcrop_name_field'),
            'dip_field': values.get('dip_field'),
            'strike_field': values.get('strike_field'),
        }
        # Create hash from string representation
        key_str = '|'.join(f"{k}:{v}" for k, v in sorted(key_params.items()))
        return hash(key_str)

    def get(self, key):
        """Get cached data for given key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data dict or None if not found
        """
        return self._cache.get(key)

    def set(self, key, data):
        """Set cached data for given key.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        # Only keep one cache entry to limit memory
        self._cache.clear()
        self._cache[key] = data
        self._cache_key = key

    def clear(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_key = None
        logger.info("Cache cleared")
