"""Geology extraction adapter (Extract phase).

Bridges the QGIS object world and the QGIS-agnostic core layer for geological
profiles. It reads the section line and outcrop layers, densifies and samples
the master profile, and intersects the section line with outcrop polygons —
returning a fully-detached :class:`GeologyContext` so ``GeologyService`` never
touches QGIS objects.
"""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsDistanceArea,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core import utils as scu
from sec_interp.core.domain import DomainGeometry
from sec_interp.core.domain.task_inputs import GeologyContext, OutcropSegments
from sec_interp.core.exceptions import DataMissingError, GeometryError, ValidationError
from sec_interp.core.utils.geometry_utils.extraction import extract_lines_from_geometry
from sec_interp.core.utils.geometry_utils.processing import calculate_segment_range
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class GeologyExtractor:
    """Extract geological data from QGIS layers into a QGIS-agnostic context."""

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("GeologyExtractor", message)  # type: ignore[no-any-return]

    def extract_context(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyContext:
        """Extract all geology data into a detached :class:`GeologyContext`.

        Args:
            line_lyr: The cross-section line vector layer.
            raster_lyr: The DEM raster layer.
            outcrop_lyr: The geological outcrop vector layer.
            outcrop_name_field: Attribute field name for unit names.
            band_number: Raster band to use for elevation sampling.

        Returns:
            A fully-detached :class:`GeologyContext`.

        """
        self._validate_inputs(line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number)

        line_geom, line_start = self._extract_line_info(line_lyr)
        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        master_profile_data, master_grid_dists_raw = self._generate_master_profile(
            line_geom, raster_lyr, band_number, da, line_start
        )
        master_grid_dists = [(d, (pt.x(), pt.y()), e) for d, pt, e in master_grid_dists_raw]

        outcrops: list[OutcropSegments] = []
        if outcrop_lyr:
            for item in self._extract_outcrop_data(line_geom, outcrop_lyr, outcrop_name_field):
                segments = self._intersect_outcrop(line_geom, line_start, da, item)
                outcrops.append(
                    OutcropSegments(
                        unit_name=item["unit_name"],
                        attributes=item["attrs"],
                        segments=segments,
                    )
                )

        return GeologyContext(
            master_profile_data=master_profile_data,
            master_grid_dists=master_grid_dists,
            outcrops=outcrops,
            tolerance=0.001,
        )

    def _validate_inputs(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int,
    ) -> None:
        """Validate input layers and parameters."""
        for lyr, name in [(line_lyr, "Line layer"), (raster_lyr, "Raster layer")]:
            if not lyr or not lyr.isValid():
                raise DataMissingError(
                    self.tr("Invalid layer: {0}. Please check input layers.").format(name),
                    {"layer": name},
                )

        if outcrop_lyr and not outcrop_lyr.isValid():
            raise DataMissingError(
                self.tr("Invalid layer: Outcrop layer. Please check input layers."),
                {"layer": "Outcrop layer"},
            )

        if band_number < 1:
            raise ValidationError(self.tr("Band number must be positive."))

        if band_number > raster_lyr.bandCount():
            raise ValidationError(
                self.tr("Band number {0} exceeds raster band count ({1}).").format(
                    band_number, raster_lyr.bandCount()
                )
            )

        if outcrop_lyr:
            idx = outcrop_lyr.fields().indexFromName(outcrop_name_field)
            if idx == -1:
                raise ValidationError(
                    self.tr("Field '{0}' not found in outcrop layer.").format(outcrop_name_field)
                )

    def _extract_line_info(self, line_lyr: QgsVectorLayer) -> tuple[QgsGeometry, QgsPointXY]:
        """Extract geometry and start point from the line layer."""
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError(
                self.tr("Line layer has no features"), {"layer": line_lyr.name()}
            )

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            raise GeometryError(self.tr("Line geometry is not valid"), {"layer": line_lyr.name()})

        if line_geom.isMultipart():
            line_start = line_geom.asMultiPolyline()[0][0]
        else:
            line_start = line_geom.asPolyline()[0]

        return line_geom, line_start

    def _generate_master_profile(
        self,
        line_geom: QgsGeometry,
        raster_lyr: QgsRasterLayer,
        band_number: int,
        da: QgsDistanceArea,
        line_start: QgsPointXY,
    ) -> tuple[list[tuple[float, float]], list[tuple[float, QgsPointXY, float]]]:
        """Densify the line and sample elevations from the raster."""
        try:
            interval = raster_lyr.rasterUnitsPerPixelX()
            master_densified = scu.densify_line_by_interval(line_geom, interval)
            grid_points = scu.get_line_vertices(master_densified)
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to densify line, using original vertices: {e}")
            grid_points = scu.get_line_vertices(line_geom)

        master_profile_data: list[tuple[float, float]] = []
        master_grid_dists: list[tuple[float, QgsPointXY, float]] = []
        current_dist = 0.0

        for i, pt in enumerate(grid_points):
            if i > 0:
                current_dist += da.measureLine(grid_points[i - 1], pt)

            val, ok = raster_lyr.dataProvider().sample(pt, band_number)
            elev = val if ok else 0.0

            master_profile_data.append((current_dist, elev))
            master_grid_dists.append((current_dist, pt, elev))

        return master_profile_data, master_grid_dists

    def _extract_outcrop_data(
        self,
        line_geom: QgsGeometry,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
    ) -> list[dict[str, Any]]:
        """Extract outcrop features intersecting the line bounding box."""
        outcrop_data: list[dict[str, Any]] = []
        line_bbox = line_geom.boundingBox()
        request = QgsFeatureRequest().setFilterRect(line_bbox)

        for feature in outcrop_lyr.getFeatures(request):
            if not feature.hasGeometry():
                continue

            attrs = scu.extract_feature_attributes(feature)
            try:
                unit_name = str(feature[outcrop_name_field])
            except KeyError:
                unit_name = "Unknown"

            outcrop_data.append(
                {
                    "wkt": feature.geometry().asWkt(),
                    "attrs": attrs,
                    "unit_name": unit_name,
                }
            )
        return outcrop_data

    def _intersect_outcrop(
        self,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        item: dict[str, Any],
    ) -> list[tuple[float, float, DomainGeometry]]:
        """Intersect a single outcrop with the line and return detached segments."""
        outcrop_geom = QgsGeometry.fromWkt(item["wkt"])
        intersection = line_geom.intersection(outcrop_geom)

        if intersection.isEmpty():
            return []

        segments: list[tuple[float, float, DomainGeometry]] = []
        for seg_geom in extract_lines_from_geometry(intersection):
            rng = calculate_segment_range(seg_geom, line_start, da)
            if not rng:
                continue
            dist_start, dist_end = rng
            segments.append((dist_start, dist_end, seg_geom.asWkt()))

        return segments
