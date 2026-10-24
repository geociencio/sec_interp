"""Geological-profile component processor for the profile pipeline."""

from __future__ import annotations

from typing import Any

from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import GeologySegment, PreviewParams
from sec_interp.core.services.profile.cache import geology_cache_key
from sec_interp.core.services.profile.errors import (
    ProfileInputError,
    ProfileServiceError,
)
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def process_geology(
    params: PreviewParams,
    extractor: Any,
    service: Any,
    cache: DataCache,
    cache_meta: dict,
) -> list[GeologySegment] | None:
    """Extract and cache geological segments.

    Args:
        params: Preview parameters with the outcrop layer and smoothing.
        extractor: Geology extractor adapter.
        service: Geology segment builder.
        cache: Component cache.
        cache_meta: Metadata stored with a cache entry.

    Returns:
        Geological segments, possibly an empty list.

    Raises:
        ProfileInputError: If line, raster or outcrop layers are missing.
        ProfileServiceError: If the extractor or service is unavailable.

    """
    geol_key = geology_cache_key(params)
    geol_data = cache.get("geol", geol_key)
    if geol_data:
        logger.debug("Cache hit: Geology")
        return geol_data  # type: ignore[no-any-return]

    line_lyr = params.line_layer
    raster_lyr = params.raster_layer
    outcrop_lyr = params.outcrop_layer
    if not all([line_lyr, raster_lyr, outcrop_lyr]):
        raise ProfileInputError("geology layers missing")  # no-i18n
    if not service or not extractor:
        raise ProfileServiceError("geology service unavailable")  # no-i18n

    context = extractor.extract_context(
        line_lyr,
        raster_lyr,
        outcrop_lyr,
        params.outcrop_name_field,
        params.band_num,
        smoothing_window_m=float(params.smooth_window) if params.smooth else 0.0,
        feature_id=params.section_feature_id,
    )
    geol_data = service.build_segments(context)
    if geol_data:
        cache.set("geol", geol_key, geol_data, cache_meta)
    return geol_data  # type: ignore[no-any-return]
