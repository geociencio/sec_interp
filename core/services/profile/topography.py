"""Topographic-profile component processor for the profile pipeline."""

from __future__ import annotations

from typing import Any

from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import PreviewParams
from sec_interp.core.services.profile.cache import topography_cache_key
from sec_interp.core.services.profile.errors import (
    ProfileDataError,
    ProfileInputError,
    ProfileServiceError,
)
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def process_topography(
    params: PreviewParams,
    extractor: Any,
    cache: DataCache,
    cache_meta: dict,
) -> list[tuple[float, float]]:
    """Extract and cache the topographic profile.

    Args:
        params: Preview parameters with the section line and raster.
        extractor: Topography extractor adapter.
        cache: Component cache.
        cache_meta: Metadata stored with a cache entry.

    Returns:
        The (distance, elevation) profile.

    Raises:
        ProfileInputError: If the line or raster layer is missing.
        ProfileServiceError: If the extractor is unavailable.
        ProfileDataError: If extraction returns no points.

    """
    topo_key = topography_cache_key(params)
    profile_data = cache.get("topo", topo_key)
    if profile_data:
        logger.debug("Cache hit: Topography")
    else:
        line_lyr = params.line_layer
        raster_lyr = params.raster_layer
        if not line_lyr or not raster_lyr:
            raise ProfileInputError("topography layers missing")  # no-i18n
        if not extractor:
            raise ProfileServiceError("topography service unavailable")  # no-i18n

        profile_data = extractor.extract_profile(
            line_lyr,
            raster_lyr,
            params.band_num,
            feature_id=params.section_feature_id,
        )
        if not profile_data:
            raise ProfileDataError("empty topography profile")  # no-i18n

    cache.set("topo", topo_key, profile_data, cache_meta)
    return profile_data  # type: ignore[no-any-return]
