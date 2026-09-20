"""Interpretation attribute inheritance mixin (nearest geology/drillhole)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from qgis.core import QgsGeometry, QgsPointXY

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class InterpretationInheritanceMixin:
    """Inherit attributes from the geometrically nearest geology or drillhole data."""

    def apply_attribute_inheritance(
        self, interpretation: InterpretationPolygon, config: dict[str, Any]
    ) -> None:
        """Inherit attributes from nearest geology or drillhole data."""
        poly_geom = QgsGeometry.fromPolygonXY(
            [[QgsPointXY(x, y) for x, y in interpretation.vertices_2d]]
        )
        ref_point = poly_geom.centroid().asPoint()

        best_match = None
        min_dist = float("inf")

        if config.get("inherit_geology"):
            best_match, min_dist = self._check_geology_inheritance(ref_point, min_dist, best_match)

        if config.get("inherit_drillholes"):
            best_match, min_dist = self._check_drillhole_inheritance(
                ref_point, min_dist, best_match
            )

        if best_match:
            logger.info(f"Inherited attributes from {best_match['type']}: {best_match['name']}")
            interpretation.name = best_match["name"]
            interpretation.type = best_match["type"]
            if best_match["attrs"]:
                interpretation.attributes.update(best_match["attrs"])
            interpretation.color = self.dialog.layer_factory.get_color_for_unit(
                best_match["name"]
            ).name()

    def _check_geology_inheritance(
        self, ref_point: QgsPointXY, min_dist: float, best_match: dict[str, Any] | None
    ) -> tuple[dict[str, Any] | None, float]:
        """Search for nearest geological segment using QgsSpatialIndex.

        Args:
            ref_point: Reference point for distance calculation.
            min_dist: Current minimum distance found.
            best_match: Current best match found.

        Returns:
            Tuple of (new best match dictionary, new minimum distance).

        """
        geol_data = self._preview_cache.get("geol")
        if not geol_data:
            return best_match, min_dist

        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsSpatialIndex

        index = QgsSpatialIndex()
        feature_dict = {}
        for i, segment in enumerate(geol_data):
            if not segment.points:
                continue

            feat = QgsFeature(i)
            pts = [QgsPointXY(x, y) for x, y in segment.points]

            if len(pts) == 1:
                geom = QgsGeometry.fromPointXY(pts[0])
            else:
                geom = QgsGeometry.fromPolylineXY(pts)

            feat.setGeometry(geom)
            index.addFeature(feat)
            feature_dict[i] = (segment, geom)

        nearest_ids = index.nearestNeighbor(ref_point, 1)
        if nearest_ids:
            segment, geom = feature_dict[nearest_ids[0]]
            d = geom.distance(QgsGeometry.fromPointXY(ref_point))
            if d < min_dist:
                min_dist = d
                best_match = {
                    "name": segment.unit_name,
                    "type": "geology",
                    "attrs": segment.attributes,
                }

        return best_match, min_dist

    def _check_drillhole_inheritance(
        self, ref_point: QgsPointXY, min_dist: float, best_match: dict[str, Any] | None
    ) -> tuple[dict[str, Any] | None, float]:
        """Search for nearest drillhole interval using QgsSpatialIndex.

        Args:
            ref_point: Reference point for distance calculation.
            min_dist: Current minimum distance found.
            best_match: Current best match found.

        Returns:
            Tuple of (new best match dictionary, new minimum distance).

        """
        dh_data = self._preview_cache.get("drillhole")
        if not dh_data:
            return best_match, min_dist

        from qgis.core import QgsFeature, QgsSpatialIndex

        index = QgsSpatialIndex()
        feature_dict = {}
        for feat_id, (interval, geom) in enumerate(self._iter_drillhole_interval_geoms(dh_data)):
            feat = QgsFeature(feat_id)
            feat.setGeometry(geom)
            index.addFeature(feat)
            feature_dict[feat_id] = (interval, geom)

        nearest_ids = index.nearestNeighbor(ref_point, 1)
        if nearest_ids:
            interval, geom = feature_dict[nearest_ids[0]]
            d = geom.distance(QgsGeometry.fromPointXY(ref_point))
            if d < min_dist:
                min_dist = d
                best_match = {
                    "name": getattr(
                        interval,
                        "rock_unit",
                        getattr(interval, "unit_name", "Unknown"),
                    ),
                    "type": "drillhole",
                    "attrs": interval.attributes,
                }

        return best_match, min_dist

    def _iter_drillhole_interval_geoms(
        self, dh_data: list[Any]
    ) -> Iterator[tuple[Any, QgsGeometry]]:
        """Yield ``(interval, geometry)`` for every drillhole interval with points.

        Args:
            dh_data: List of drillhole records (tuples or objects).

        Yields:
            Tuples of (interval, QgsGeometry) ready to be added to a spatial index.

        """
        for dh in dh_data:
            for interval in self._extract_intervals_from_dh_data(dh):
                points = getattr(interval, "points", None)
                if not points:
                    continue

                pts = [QgsPointXY(x, y) for x, y in points]
                if len(pts) == 1:
                    geom = QgsGeometry.fromPointXY(pts[0])
                else:
                    geom = QgsGeometry.fromPolylineXY(pts)
                yield interval, geom

    def _extract_intervals_from_dh_data(self, dh: Any) -> list[Any]:
        """Safely extract intervals from various drillhole data formats.

        Args:
            dh: Drillhole data (tuple or object).

        Returns:
            List of interval objects.

        """
        if isinstance(dh, tuple):
            LEGACY_HOLE_SIZE = 5
            INTERVALS_INDEX_LEGACY = 4
            if len(dh) == LEGACY_HOLE_SIZE:
                return dh[INTERVALS_INDEX_LEGACY]
            MIN_COMPONENTS = 3
            if len(dh) >= MIN_COMPONENTS:
                return dh[2]
        return getattr(dh, "intervals", [])
