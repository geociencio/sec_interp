"""Structure extraction adapter (Extract phase).

Bridges the QGIS object world and the QGIS-agnostic core layer for structural
measurements. It reads the section line and structure layers, buffers the line,
filters features within the buffer, and samples raster elevations — returning
plain tuples/dicts so ``StructureService`` never touches QGIS objects.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.gui.adapters import geometry


@dataclass
class SectionContext:
    """Extracted section data (QGIS-agnostic primitives).

    Attributes:
        line_points: Section line vertices as ``(x, y)`` tuples.
        line_start: First vertex of the section line.
        line_azimuth: Compass bearing of the section line.
        structures: Detached structures as ``{"point": (x, y), "attributes": {...}}``.

    """

    line_points: list[tuple[float, float]] = field(default_factory=list)
    line_start: tuple[float, float] = (0.0, 0.0)
    line_azimuth: float = 0.0
    structures: list[dict[str, Any]] = field(default_factory=list)


class StructureExtractor:
    """Extract structure-related data from QGIS layers into primitives."""

    def extract_section_and_structures(
        self,
        line_lyr: QgsVectorLayer,
        struct_lyr: QgsVectorLayer,
        buffer_m: float,
    ) -> SectionContext | None:
        """Extract the section line geometry and structures within the buffer.

        Args:
            line_lyr: The cross-section line vector layer.
            struct_lyr: The structural measurements vector layer.
            buffer_m: Buffer distance (in line-layer units).

        Returns:
            A :class:`SectionContext` of primitives, or None if the line layer
            has no valid geometry.

        """
        line_geom = self._read_line_geometry(line_lyr)
        if line_geom is None:
            return None

        line_points, line_start, line_azimuth = self.extract_line(line_geom)
        structures = self.detach_structures(struct_lyr, line_geom, buffer_m)

        return SectionContext(
            line_points=line_points,
            line_start=line_start,
            line_azimuth=line_azimuth,
            structures=structures,
        )

    def extract_line(
        self, line_geom: QgsGeometry
    ) -> tuple[list[tuple[float, float]], tuple[float, float], float]:
        """Extract ``(line_points, line_start, line_azimuth)`` from a geometry.

        Args:
            line_geom: The section line geometry.

        Returns:
            A tuple of line vertices, the start vertex, and the compass bearing.

        """
        line_points = self._extract_line_points(line_geom)
        line_start = line_points[0] if line_points else (0.0, 0.0)
        line_azimuth = self._calculate_azimuth(line_points)
        return line_points, line_start, line_azimuth

    def detach_structures(
        self,
        struct_lyr: QgsVectorLayer,
        line_geom: QgsGeometry,
        buffer_m: float,
    ) -> list[dict[str, Any]]:
        """Buffer the line and extract structures within it.

        Returns a list of ``{"point": (x, y), "attributes": {...}}`` dicts.
        """
        if not struct_lyr or not struct_lyr.isValid():
            return []

        buffer_geom = line_geom.buffer(buffer_m, 25)
        request = QgsFeatureRequest().setFilterRect(buffer_geom.boundingBox())

        detached: list[dict[str, Any]] = []
        for feature in struct_lyr.getFeatures(request):
            if not feature.hasGeometry() or not feature.geometry().intersects(buffer_geom):
                continue
            point = self._feature_point(feature)
            if point is None:
                continue
            detached.append(
                {
                    "point": point,
                    "attributes": self._extract_attributes(feature),
                }
            )
        return detached

    def make_elevation_sampler(
        self,
        raster_lyr: QgsRasterLayer,
        line_lyr: QgsVectorLayer | None = None,
        band_number: int = 1,
    ) -> Callable[[float, float], float]:
        """Return an ``(x, y) -> elevation`` sampler reprojecting to the raster CRS.

        Structural points live in the section line CRS. When the DEM uses a
        different CRS (on-the-fly reprojection) they must be transformed before
        sampling, otherwise every elevation comes back as 0. The transform is
        resolved once here and reused for every point.
        """
        transform = self._sampling_transform(raster_lyr, line_lyr)

        def sampler(x: float, y: float) -> float:
            return self._sample_at(raster_lyr, x, y, band_number, transform)

        return sampler

    def sample_elevation(
        self,
        raster_lyr: QgsRasterLayer,
        x: float,
        y: float,
        band_number: int = 1,
        line_lyr: QgsVectorLayer | None = None,
    ) -> float:
        """Sample a single elevation value from a raster layer.

        Args:
            raster_lyr: The DEM raster layer.
            x: X coordinate to sample (in the section line CRS).
            y: Y coordinate to sample (in the section line CRS).
            band_number: Raster band index (default 1).
            line_lyr: Section line layer, used to reproject the point.

        Returns:
            The sampled elevation, or 0.0 if the raster is invalid or the point
            is out of bounds.

        """
        transform = self._sampling_transform(raster_lyr, line_lyr)
        return self._sample_at(raster_lyr, x, y, band_number, transform)

    def _sampling_transform(
        self, raster_lyr: QgsRasterLayer, line_lyr: QgsVectorLayer | None
    ) -> Any | None:
        """Return the line-CRS -> raster-CRS transform, or None when unneeded."""
        line_crs = None
        if line_lyr is not None:
            try:
                line_crs = line_lyr.crs()
            except (AttributeError, RuntimeError):
                line_crs = None
        return geometry.build_sampling_transform(line_crs, raster_lyr)

    def _sample_at(
        self,
        raster_lyr: QgsRasterLayer,
        x: float,
        y: float,
        band_number: int,
        transform: Any | None,
    ) -> float:
        """Sample one raster value, reprojecting the point when needed."""
        if not raster_lyr or not raster_lyr.isValid():
            return 0.0

        try:
            point = QgsPointXY(x, y)
            if transform is not None:
                point = transform.transform(point)
            ident = raster_lyr.dataProvider().identify(
                point, QgsRaster.IdentifyFormat.IdentifyFormatValue
            )
            if ident.isValid():
                val = ident.results().get(band_number)
                if val is not None:
                    return float(val)
        except (AttributeError, ValueError, TypeError):
            pass
        return 0.0

    def _read_line_geometry(self, line_lyr: QgsVectorLayer) -> QgsGeometry | None:
        """Read and validate the first feature geometry of the line layer."""
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            return None

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            return None
        return line_geom

    def _extract_line_points(self, geometry: QgsGeometry) -> list[tuple[float, float]]:
        """Extract ``(x, y)`` tuples from a single/multi-part line geometry."""
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            polyline = parts[0] if parts else []
        else:
            polyline = geometry.asPolyline()
        return [(p.x(), p.y()) for p in polyline]

    def _calculate_azimuth(self, points: list[tuple[float, float]]) -> float:
        """Calculate the compass bearing from the first two vertices."""
        MIN_REQUIRED_POINTS = 2
        if len(points) < MIN_REQUIRED_POINTS:
            return 0.0
        p1, p2 = points[0], points[1]
        azimuth = math.degrees(math.atan2(p2[0] - p1[0], p2[1] - p1[1]))
        if azimuth < 0:
            azimuth += 360
        return azimuth

    def _feature_point(self, feature: QgsFeature) -> tuple[float, float] | None:
        """Return a representative ``(x, y)`` point for a feature's geometry."""
        geom = feature.geometry()
        if not geom or geom.isNull():
            return None

        if geom.type() == QgsWkbTypes.GeometryType.PointGeometry:
            pt = geom.asPoint()
        else:
            centroid = geom.centroid()
            if centroid.isNull():
                return None
            pt = centroid.asPoint()

        return (pt.x(), pt.y())

    def _extract_attributes(self, feature: QgsFeature) -> dict[str, Any]:
        """Extract feature attributes into a sanitized Python dictionary."""
        if not hasattr(feature, "fields"):
            return {}

        names = feature.fields().names()
        raw_values = feature.attributes()
        sanitized: dict[str, Any] = {}
        for name, val in zip(names, raw_values, strict=False):
            if val is None or str(val) == "NULL":
                sanitized[name] = None
            elif isinstance(val, int | float | str | bool):
                sanitized[name] = val
            else:
                sanitized[name] = str(val)
        return sanitized
