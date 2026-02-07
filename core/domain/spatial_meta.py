"""Spatial Meta Data for 3D and 2D projections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SpatialMeta:
    """Carrying spatial metadata for 3D/2D decoupling.

    This DTO acts as a universal bridge between raw spatial data and various
    renderers (2D profiling or 3D engines), carrying coordinates, normalization
    vectors, and original attributes without layer dependencies.

    Attributes:
        hole_id: Unique identifier for the drillhole.
        dist_along: Distance along the section line (station).
        offset: Orthogonal distance from the section line.
        z: Elevation or vertical coordinate.
        x_3d: X coordinate in global 3D space.
        y_3d: Y coordinate in global 3D space.
        norm_x: Normalized X component of the orientation vector.
        norm_y: Normalized Y component of the orientation vector.
        attributes: Original feature attributes for contextual display.

    """

    hole_id: str | None = None
    dist_along: float = 0.0
    offset: float = 0.0
    z: float = 0.0
    x_3d: float | None = None
    y_3d: float | None = None
    x_proj: float | None = None
    y_proj: float | None = None
    norm_x: float | None = None
    norm_y: float | None = None
    attributes: dict[str, Any] | None = None

    def to_vec3(self) -> tuple[float, float, float]:
        """Convert spatial data to a 3D vector tuple (X, Y, Z)."""
        return (self.x_3d or 0.0, self.y_3d or 0.0, self.z)

    def to_vec2_profile(self) -> tuple[float, float]:
        """Convert spatial data to a 2D profile vector (Distance, Z)."""
        return (self.dist_along, self.z)
