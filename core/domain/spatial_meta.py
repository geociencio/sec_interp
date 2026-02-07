from __future__ import annotations

"""Spatial Meta Data for 3D and 2D projections."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SpatialMeta:
    """Carries spatial information for 3D/2D decoupling."""

    hole_id: str | None = None
    dist_along: float = 0.0
    offset: float = 0.0
    z: float = 0.0
    x_3d: float | None = None
    y_3d: float | None = None
    norm_x: float | None = None
    norm_y: float | None = None
    attributes: dict[str, Any] | None = None

    def to_vec3(self) -> tuple[float, float, float]:
        """Convert to 3D vector tuple."""
        return (self.x_3d or 0.0, self.y_3d or 0.0, self.z)

    def to_vec2_profile(self) -> tuple[float, float]:
        """Convert to Profile 2D vector (dist, z)."""
        return (self.dist_along, self.z)
