"""Section-feature resolution and profile-context helpers."""

from __future__ import annotations

from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
)

from sec_interp.core.exceptions import GeometryError
from sec_interp.gui.adapters.geometry_crs import create_distance_area
from sec_interp.gui.adapters.geometry_lines import (
    get_line_vertices,
    section_line_start_point,
)


def resolve_section_feature(
    line_lyr: QgsVectorLayer | None,
    feature_id: int | None = None,
) -> QgsFeature | None:
    """Return the section feature to use (first by default, or ``feature_id``).

    This is the single resolution point for the section line, so every extractor
    picks the same feature. ``None`` returns the first feature; a fid filters by
    it. Defensive: an invalid layer or a missing feature returns ``None``.
    """
    if not line_lyr or not line_lyr.isValid():
        return None
    try:
        request = QgsFeatureRequest()
        if feature_id is not None:
            request.setFilterFid(int(feature_id))
        else:
            request.setLimit(1)
        return next(line_lyr.getFeatures(request), None)
    except (AttributeError, TypeError, ValueError, RuntimeError, StopIteration):
        return None


def resolve_section_geometry(
    line_lyr: QgsVectorLayer | None,
    feature_id: int | None = None,
) -> QgsGeometry | None:
    """Return the section feature geometry, or ``None`` when unavailable."""
    feature = resolve_section_feature(line_lyr, feature_id)
    if feature is None:
        return None
    try:
        geometry = feature.geometry()
    except (AttributeError, RuntimeError):
        return None
    if geometry is None or geometry.isNull():
        return None
    return geometry


def prepare_profile_context(
    line_lyr: QgsVectorLayer,
    feature_id: int | None = None,
) -> tuple[QgsGeometry, QgsPointXY, QgsDistanceArea]:
    """Prepare a common context for profile calculation operations."""
    line_feat = resolve_section_feature(line_lyr, feature_id)
    if not line_feat:
        raise GeometryError("Line layer has no features", {"layer": line_lyr.name()})  # no-i18n

    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})  # no-i18n

    try:
        if not get_line_vertices(line_geom):
            raise GeometryError(
                "Line geometry has no vertices",  # no-i18n
                {"layer": line_lyr.name()},
            )
    except ValueError as e:
        raise GeometryError(str(e), {"layer": line_lyr.name()}) from e

    line_start = section_line_start_point(line_geom)
    da = create_distance_area(line_lyr.crs())
    return line_geom, line_start, da


def line_length(line_lyr: QgsVectorLayer, feature_id: int | None = None) -> float | None:
    """Return the length of the section feature's geometry in a line layer."""
    line_geom = resolve_section_geometry(line_lyr, feature_id)
    if line_geom is None:
        return None
    return line_geom.length()
