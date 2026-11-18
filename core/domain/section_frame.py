"""Pure section frame for mapping profile coordinates to map coordinates."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SectionFrame:
    """Geometric frame of a 2D section projected into map space.

    A section frame maps a profile coordinate ``(distance, elevation)`` to a
    map coordinate ``(east, north, elevation)``. It is deliberately QGIS-free
    so it can be shared by all exporters and tested without a QGIS runtime.

    ``vertical_exaggeration`` is metadata only: ``to_map`` always returns the
    true elevation. Consumers that need an exaggerated view should scale Z at
    render time and record the factor in the export manifest.

    Attributes:
        origin_x: Easting of the section start point.
        origin_y: Northing of the section start point.
        azimuth_rad: Section direction in radians, measured counter-clockwise
            from east in the projected CRS.
        crs_authid: CRS authority identifier (for example ``EPSG:32614``).
        length: Horizontal section length in map units.
        vertical_exaggeration: Metadata factor for consumers that scale Z.

    """

    origin_x: float
    origin_y: float
    azimuth_rad: float
    crs_authid: str
    length: float
    vertical_exaggeration: float = 1.0

    def __post_init__(self) -> None:
        """Validate numeric fields and the section length."""
        values = {
            "origin_x": self.origin_x,
            "origin_y": self.origin_y,
            "azimuth_rad": self.azimuth_rad,
            "length": self.length,
            "vertical_exaggeration": self.vertical_exaggeration,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.length <= 0:
            raise ValueError("length must be greater than zero")
        if self.vertical_exaggeration <= 0:
            raise ValueError("vertical_exaggeration must be greater than zero")

    @classmethod
    def from_endpoints(
        cls,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        crs_authid: str = "",
        vertical_exaggeration: float = 1.0,
    ) -> SectionFrame:
        """Build a frame from the two endpoints of a section line.

        Args:
            start_x: Easting of the first endpoint.
            start_y: Northing of the first endpoint.
            end_x: Easting of the second endpoint.
            end_y: Northing of the second endpoint.
            crs_authid: CRS authority identifier.
            vertical_exaggeration: Metadata factor for Z scaling.

        Returns:
            A validated section frame.

        Raises:
            ValueError: If the endpoints are identical or a value is invalid.

        """
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy)
        if length <= 0:
            raise ValueError("section endpoints must be distinct")
        return cls(
            origin_x=start_x,
            origin_y=start_y,
            azimuth_rad=math.atan2(dy, dx),
            crs_authid=crs_authid,
            length=length,
            vertical_exaggeration=vertical_exaggeration,
        )

    @property
    def azimuth_deg(self) -> float:
        """Return the section azimuth in degrees."""
        return math.degrees(self.azimuth_rad)

    def to_map(self, distance: float, elevation: float) -> tuple[float, float, float]:
        """Map profile coordinates to map coordinates.

        Args:
            distance: Horizontal distance from the section start.
            elevation: True elevation (Z).

        Returns:
            A tuple ``(east, north, elevation)``.

        Raises:
            ValueError: If the input coordinates are not finite.

        """
        if not math.isfinite(distance) or not math.isfinite(elevation):
            raise ValueError("distance and elevation must be finite")
        east = self.origin_x + distance * math.cos(self.azimuth_rad)
        north = self.origin_y + distance * math.sin(self.azimuth_rad)
        return east, north, elevation
