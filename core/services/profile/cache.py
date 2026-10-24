"""Cache-key builders for profile components.

Every input that can change a component's output must participate in its cache
key; otherwise changing a layer, field mapping or smoothing option reuses stale
data. This module centralizes those inputs so the controller and the tests use
one definition per component.
"""

from __future__ import annotations

import contextlib
import hashlib
from typing import Any

from sec_interp.core.domain import PreviewParams


def component_cache_key(**parts: Any) -> str:
    """Hash the named inputs of one profile component.

    Args:
        **parts: Named component inputs. Values with an ``id()`` method (QGIS
            layers) are represented by that ID.

    Returns:
        MD5 hash of the sorted ``name=value`` pairs.

    """
    hasher = hashlib.md5()  # nosec B324
    for name in sorted(parts):
        value = parts[name]
        if hasattr(value, "id") and not isinstance(value, (str, bytes)):
            with contextlib.suppress(AttributeError, RuntimeError, TypeError):
                value = value.id()
        hasher.update(f"{name}={value!r};".encode())
    return hasher.hexdigest()


def topography_cache_key(params: PreviewParams) -> str:
    """Return the cache key for the topographic profile component."""
    return component_cache_key(
        line_layer=params.line_layer,
        raster_layer=params.raster_layer,
        band_num=params.band_num,
        section_feature_id=params.section_feature_id,
        max_points=params.max_points,
    )


def geology_cache_key(params: PreviewParams) -> str:
    """Return the cache key for the geological profile component."""
    return component_cache_key(
        line_layer=params.line_layer,
        raster_layer=params.raster_layer,
        outcrop_layer=params.outcrop_layer,
        outcrop_name_field=params.outcrop_name_field,
        band_num=params.band_num,
        section_feature_id=params.section_feature_id,
        smooth=params.smooth,
        smooth_window=params.smooth_window if params.smooth else 0,
        max_points=params.max_points,
    )


def structures_cache_key(params: PreviewParams) -> str:
    """Return the cache key for the structural measurements component."""
    return component_cache_key(
        line_layer=params.line_layer,
        raster_layer=params.raster_layer,
        struct_layer=params.struct_layer,
        buffer_dist=params.buffer_dist,
        dip_field=params.dip_field,
        strike_field=params.strike_field,
        band_num=params.band_num,
        section_feature_id=params.section_feature_id,
    )


def drillholes_cache_key(params: PreviewParams) -> str:
    """Return the cache key for the drillhole projection component."""
    return component_cache_key(
        line_layer=params.line_layer,
        raster_layer=params.raster_layer,
        band_num=params.band_num,
        section_feature_id=params.section_feature_id,
        collar_layer=params.collar_layer,
        survey_layer=params.survey_layer,
        interval_layer=params.interval_layer,
        buffer_dist=params.buffer_dist,
        collar_id_field=params.collar_id_field,
        collar_use_geometry=params.collar_use_geometry,
        collar_x_field=params.collar_x_field,
        collar_y_field=params.collar_y_field,
        collar_z_field=params.collar_z_field,
        collar_depth_field=params.collar_depth_field,
        survey_id_field=params.survey_id_field,
        survey_depth_field=params.survey_depth_field,
        survey_azim_field=params.survey_azim_field,
        survey_incl_field=params.survey_incl_field,
        interval_id_field=params.interval_id_field,
        interval_from_field=params.interval_from_field,
        interval_to_field=params.interval_to_field,
        interval_lith_field=params.interval_lith_field,
    )
