"""QGIS-agnostic layer metadata for validation."""

from __future__ import annotations

from dataclasses import dataclass, field

from sec_interp.core.domain import FieldType

# Geometry type keys (QGIS-agnostic).
GEOMETRY_POINT = "point"
GEOMETRY_LINE = "line"
GEOMETRY_POLYGON = "polygon"
GEOMETRY_UNKNOWN = "unknown"

# Layer kinds.
KIND_VECTOR = "vector"
KIND_RASTER = "raster"
KIND_UNKNOWN = "unknown"


@dataclass
class LayerMetadata:
    """Detached metadata describing a QGIS layer for validation.

    Produced by the GUI ``ValidationExtractor`` adapter so that the core
    validators never touch QGIS objects directly.

    Attributes:
        name: Layer name.
        is_valid: Whether the layer was valid at extraction time.
        kind: ``"vector"``, ``"raster"``, or ``"unknown"``.
        geometry_type: ``"point"``, ``"line"``, ``"polygon"``, or None.
        field_names: Ordered list of field names.
        field_types: Mapping of field name to :class:`FieldType`.
        band_count: Raster band count (0 for vectors).
        feature_count: Number of features (0 for rasters).
        crs_authid: CRS authority ID (e.g. ``"EPSG:4326"``).

    """

    name: str = ""
    is_valid: bool = False
    kind: str = KIND_UNKNOWN
    geometry_type: str | None = None
    field_names: list[str] = field(default_factory=list)
    field_types: dict[str, FieldType] = field(default_factory=dict)
    band_count: int = 0
    feature_count: int = 0
    crs_authid: str | None = None
