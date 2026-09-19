"""Processing logic for Drillhole Collars (pure computation)."""

from __future__ import annotations

import contextlib
from typing import Any

from sec_interp.core.domain import DrillholeProjection
from sec_interp.core.services.drillhole.projection_engine import ProjectionEngine


class CollarProcessor:
    """Handles pure projection of detached collar data."""

    def extract_and_project_detached(
        self,
        collar_data: dict[str, Any],
        line_points: list[tuple[float, float]],
        buffer_width: float,
        collar_id_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
    ) -> DrillholeProjection | None:
        """Project a detached collar onto the section line.

        Args:
            collar_data: Detached collar ``{"id", "point", "attributes"}``.
            line_points: Section line vertices as ``(x, y)`` tuples.
            buffer_width: Maximum horizontal projection buffer.
            collar_id_field: ID field name.
            collar_z_field: Collar elevation field name.
            collar_depth_field: Total depth field name.
            pre_sampled_z: Optional map of pre-sampled elevations.

        Returns:
            A :class:`DrillholeProjection` if within the buffer, else None.

        """
        point = collar_data.get("point")
        if not point:
            return None

        attrs = collar_data.get("attributes", {})
        hole_id = collar_data.get("id")
        if not hole_id:
            hole_id = attrs.get(collar_id_field)
        if not hole_id:
            return None

        z = self._extract_z(attrs, collar_z_field, hole_id, pre_sampled_z)
        depth = self._extract_depth(attrs, collar_depth_field)

        dist_along, offset = ProjectionEngine.project_point_to_line(point, line_points)

        if offset <= buffer_width:
            return DrillholeProjection(
                hole_id=str(hole_id),
                distance=dist_along,
                elevation=z,
                offset=offset,
                total_depth=depth,
            )
        return None

    def build_coordinate_map(
        self, collar_data: list[dict[str, Any]]
    ) -> dict[Any, tuple[float, float]]:
        """Build a mapping of hole IDs to collar coordinates."""
        collar_coords: dict[Any, tuple[float, float]] = {}
        for item in collar_data:
            hid = item.get("id")
            pt = item.get("point")
            if hid is not None and pt is not None:
                collar_coords[hid] = pt
        return collar_coords

    def _extract_z(
        self,
        attrs: dict[str, Any],
        z_field: str,
        hole_id: Any,
        pre_sampled: dict[Any, float] | None,
    ) -> float:
        """Extract collar Z with field and pre-sampled fallbacks."""
        z = 0.0
        if z_field:
            with contextlib.suppress(ValueError, TypeError):
                z = float(attrs.get(z_field, 0.0))
        if z == 0.0 and pre_sampled and hole_id in pre_sampled:
            z = pre_sampled[hole_id]
        return z

    def _extract_depth(self, attrs: dict[str, Any], depth_field: str) -> float:
        """Extract collar depth from attributes."""
        depth = 0.0
        if depth_field:
            with contextlib.suppress(ValueError, TypeError):
                depth = float(attrs.get(depth_field, 0.0))
        return depth
