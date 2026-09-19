"""Validation extraction adapter (Extract phase).

Bridges the QGIS object world and the QGIS-agnostic core validation layer by
converting ``QgsVectorLayer``/``QgsRasterLayer`` objects (and project lookups)
into detached :class:`LayerMetadata` records.
"""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsMapLayer,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import (
    GEOMETRY_LINE,
    GEOMETRY_POINT,
    GEOMETRY_POLYGON,
    GEOMETRY_UNKNOWN,
    KIND_RASTER,
    KIND_UNKNOWN,
    KIND_VECTOR,
    LayerMetadata,
)

_GEOMETRY_MAP = {
    QgsWkbTypes.GeometryType.PointGeometry: GEOMETRY_POINT,
    QgsWkbTypes.GeometryType.LineGeometry: GEOMETRY_LINE,
    QgsWkbTypes.GeometryType.PolygonGeometry: GEOMETRY_POLYGON,
}


def resolve_layer_metadata(layer_ref: Any) -> LayerMetadata | None:
    """Resolve a layer reference to detached metadata.

    Args:
        layer_ref: A layer object, ID, or name.

    Returns:
        A :class:`LayerMetadata`, or None if the layer cannot be resolved.

    """
    layer = _resolve_layer(layer_ref)
    if layer is None:
        return None
    return extract_layer_metadata(layer)


def extract_layer_metadata(layer: QgsMapLayer) -> LayerMetadata:
    """Extract detached metadata from a QGIS layer object."""
    if isinstance(layer, QgsVectorLayer):
        return extract_vector_metadata(layer)
    if isinstance(layer, QgsRasterLayer):
        return extract_raster_metadata(layer)
    return LayerMetadata(name=layer.name(), is_valid=layer.isValid(), kind=KIND_UNKNOWN)


def extract_vector_metadata(layer: QgsVectorLayer) -> LayerMetadata:
    """Extract detached metadata from a vector layer."""
    metadata = LayerMetadata(
        name=layer.name(),
        is_valid=layer.isValid(),
        kind=KIND_VECTOR,
        feature_count=layer.featureCount(),
    )
    if not layer.isValid():
        return metadata

    metadata.geometry_type = _GEOMETRY_MAP.get(
        QgsWkbTypes.geometryType(layer.wkbType()), GEOMETRY_UNKNOWN
    )

    for f in layer.fields():
        metadata.field_names.append(f.name())
        metadata.field_types[f.name()] = _to_field_type(f.type())

    crs = layer.crs()
    if crs.isValid():
        metadata.crs_authid = crs.authid()

    return metadata


def extract_raster_metadata(layer: QgsRasterLayer) -> LayerMetadata:
    """Extract detached metadata from a raster layer."""
    metadata = LayerMetadata(
        name=layer.name(),
        is_valid=layer.isValid(),
        kind=KIND_RASTER,
        band_count=layer.bandCount(),
    )
    if not layer.isValid():
        return metadata

    crs = layer.crs()
    if crs.isValid():
        metadata.crs_authid = crs.authid()

    return metadata


def _resolve_layer(layer_ref: Any) -> QgsMapLayer | None:
    """Resolve a layer reference to a QGIS layer object."""
    if isinstance(layer_ref, QgsMapLayer):
        return layer_ref

    if not layer_ref:
        return None

    if isinstance(layer_ref, str):
        project = QgsProject.instance()
        layer = project.mapLayer(layer_ref)
        if layer is not None:
            return layer
        for lyr in project.mapLayers().values():
            if lyr.name() == layer_ref:
                return lyr
    return None


def _to_field_type(qvariant_type: Any) -> FieldType:
    """Convert a QVariant type value to a :class:`FieldType`."""
    try:
        return FieldType(int(qvariant_type))
    except (ValueError, TypeError):
        return FieldType.NULL


def build_validation_params(params: Any) -> Any:
    """Build a :class:`ValidationParams` from a ``PreviewParams`` object.

    Converts each QGIS layer reference held by ``params`` into detached
    :class:`LayerMetadata` records.

    Args:
        params: A ``PreviewParams`` instance holding QGIS layer references.

    Returns:
        A :class:`ValidationParams` with detached layer metadata.

    """
    from sec_interp.core.validation.project_validator import ValidationParams

    return ValidationParams(
        raster_layer=resolve_layer_metadata(params.raster_layer),
        band_number=params.band_num,
        line_layer=resolve_layer_metadata(params.line_layer),
        buffer_dist=float(params.buffer_dist),
        outcrop_layer=resolve_layer_metadata(params.outcrop_layer),
        outcrop_field=params.outcrop_name_field,
        struct_layer=resolve_layer_metadata(params.struct_layer),
        struct_dip_field=params.dip_field,
        struct_strike_field=params.strike_field,
        dip_scale_factor=params.dip_scale_factor,
        collar_layer=resolve_layer_metadata(params.collar_layer),
        collar_id=params.collar_id_field,
        collar_use_geom=params.collar_use_geometry,
        collar_x=params.collar_x_field,
        collar_y=params.collar_y_field,
        survey_layer=resolve_layer_metadata(params.survey_layer),
        survey_id=params.survey_id_field,
        survey_depth=params.survey_depth_field,
        survey_azim=params.survey_azim_field,
        survey_incl=params.survey_incl_field,
        interval_layer=resolve_layer_metadata(params.interval_layer),
        interval_id=params.interval_id_field,
        interval_from=params.interval_from_field,
        interval_to=params.interval_to_field,
        interval_lith=params.interval_lith_field,
    )
