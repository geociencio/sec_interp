"""Drillhole projection component processor for the profile pipeline."""

from __future__ import annotations

from typing import Any

from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import DrillholeProjection, PreviewParams
from sec_interp.core.services.profile.cache import drillholes_cache_key
from sec_interp.core.services.profile.errors import ProfileServiceError
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def process_drillholes(
    params: PreviewParams,
    extractor: Any,
    service: Any,
    cache: DataCache,
    cache_meta: dict,
) -> list[DrillholeProjection] | None:
    """Project drillholes onto the section.

    Args:
        params: Preview parameters with collar/survey/interval inputs.
        extractor: Drillhole extractor adapter.
        service: Drillhole processing service.
        cache: Component cache.
        cache_meta: Metadata stored with a cache entry.

    Returns:
        Projected drillholes, or ``None`` when the context is unavailable.

    Raises:
        ProfileServiceError: If the extractor or service is unavailable.

    """
    drill_key = drillholes_cache_key(params)
    drillhole_data = cache.get("drill", drill_key)
    if drillhole_data:
        logger.debug("Cache hit: Drillholes")
        return drillhole_data  # type: ignore[no-any-return]

    if not service or not extractor:
        raise ProfileServiceError("drillhole service unavailable")

    survey_fields = {
        "id": params.survey_id_field,
        "depth": params.survey_depth_field,
        "azim": params.survey_azim_field,
        "incl": params.survey_incl_field,
    }
    interval_fields = {
        "id": params.interval_id_field,
        "from": params.interval_from_field,
        "to": params.interval_to_field,
        "lith": params.interval_lith_field,
    }
    context = extractor.extract_context(
        params.line_layer,
        params.buffer_dist,
        params.collar_layer,
        params.collar_id_field,
        params.collar_use_geometry,
        params.collar_x_field,
        params.collar_y_field,
        params.collar_z_field,
        params.collar_depth_field,
        params.survey_layer,
        survey_fields,
        params.interval_layer,
        interval_fields,
        params.raster_layer,
        params.band_num,
    )
    if context is None:
        return None

    _, drillhole_data = service.process_context(context)
    if drillhole_data:
        cache.set("drill", drill_key, drillhole_data, cache_meta)
    return drillhole_data  # type: ignore[no-any-return]
