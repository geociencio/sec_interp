"""Ordered profile-data generation pipeline."""

from __future__ import annotations

import time
from typing import Any, Callable

from sec_interp.core.domain import PreviewParams

ComponentProcessor = Callable[[PreviewParams, dict, list[str]], Any]
ProfileResult = tuple[
    list[tuple[float, float]],
    list[Any] | None,
    list[Any] | None,
    Any | None,
    list[str],
]


def build_profile_data(
    params: PreviewParams,
    topography: ComponentProcessor,
    geology: ComponentProcessor,
    structures: ComponentProcessor,
    drillholes: ComponentProcessor,
) -> ProfileResult:
    """Run the four profile components in their fixed order.

    Args:
        params: Validated preview parameters.
        topography: Topography processor callback.
        geology: Geology processor callback.
        structures: Structure processor callback.
        drillholes: Drillhole processor callback.

    Returns:
        ``(topography, geology, structures, drillholes, messages)``.

    """
    params.validate()
    messages: list[str] = []
    cache_meta = {
        "max_points": params.max_points,
        "canvas_width": params.canvas_width,
        "timestamp": time.time(),
    }

    profile_data = topography(params, cache_meta, messages)
    geol_data = geology(params, cache_meta, messages)
    struct_data = structures(params, cache_meta, messages)
    drillhole_data = drillholes(params, cache_meta, messages)

    return profile_data, geol_data, struct_data, drillhole_data, messages
