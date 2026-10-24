"""Structural-measurement component processor for the profile pipeline."""

from __future__ import annotations

from typing import Any

from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import PreviewParams, StructureMeasurement
from sec_interp.core.services.profile.cache import structures_cache_key
from sec_interp.core.services.profile.errors import ProfileServiceError
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def process_structures(
    params: PreviewParams,
    extractor: Any,
    service: Any,
    cache: DataCache,
    cache_meta: dict,
) -> list[StructureMeasurement] | None:
    """Project structural measurements onto the section.

    Args:
        params: Preview parameters with the section and structure layers.
        extractor: Structure extractor adapter.
        service: Structure projection service.
        cache: Component cache.
        cache_meta: Metadata stored with a cache entry.

    Returns:
        Projected measurements, an empty list when nothing falls in the
        buffer, or ``None`` when the section/context cannot be built.

    Raises:
        ProfileServiceError: If the extractor or service is unavailable.

    """
    struct_key = structures_cache_key(params)
    struct_data = cache.get("struct", struct_key)
    if struct_data:
        logger.debug("Cache hit: Structure")
        return struct_data  # type: ignore[no-any-return]

    line_lyr = params.line_layer
    struct_lyr = params.struct_layer
    raster_lyr = params.raster_layer
    if not line_lyr or not struct_lyr:
        return None

    if not service or not extractor:
        raise ProfileServiceError("structure service unavailable")

    ctx = extractor.extract_section_and_structures(line_lyr, struct_lyr, params.buffer_dist)
    if ctx is None:
        return None

    elevation_sampler = extractor.make_elevation_sampler(raster_lyr, line_lyr, params.band_num)
    struct_data = service.project_structures(
        line_points=ctx.line_points,
        struct_data=ctx.structures,
        elevation_sampler=elevation_sampler,
        line_az=ctx.line_azimuth,
        dip_field=params.dip_field,
        strike_field=params.strike_field,
    )
    if struct_data:
        cache.set("struct", struct_key, struct_data, cache_meta)
    return struct_data  # type: ignore[no-any-return]
