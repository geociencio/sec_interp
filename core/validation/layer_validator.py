"""Spatial validation for layers (QGIS-agnostic)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import (
    GEOMETRY_LINE,
    GEOMETRY_POINT,
    GEOMETRY_POLYGON,
    KIND_RASTER,
    KIND_VECTOR,
    LayerMetadata,
)

from .field_validator import validate_field_exists, validate_field_type

if TYPE_CHECKING:
    from sec_interp.core.validation.validation_helpers import ValidationContext

_TYPE_NAMES = {
    GEOMETRY_POINT: "Point",
    GEOMETRY_LINE: "Line",
    GEOMETRY_POLYGON: "Polygon",
}


def validate_layer_has_features(metadata: LayerMetadata) -> tuple[bool, str]:
    """Validate that a vector layer contains at least one feature."""
    if not metadata or not metadata.is_valid:
        return False, "Layer is not valid"

    if metadata.kind != KIND_VECTOR:
        return False, "Layer is not a vector layer"

    if metadata.feature_count == 0:
        return False, f"Layer '{metadata.name}' has no features"

    return True, ""


def validate_layer_geometry(metadata: LayerMetadata, expected_type: str) -> tuple[bool, str]:
    """Validate that a vector layer matches the expected geometry type."""
    if not metadata or not metadata.is_valid:
        return False, "Layer is not valid"

    if metadata.kind != KIND_VECTOR:
        return False, "Layer is not a vector layer"

    if metadata.geometry_type != expected_type:
        expected_name = _TYPE_NAMES.get(expected_type, f"Type {expected_type}")
        actual_name = _TYPE_NAMES.get(metadata.geometry_type, metadata.geometry_type)

        return False, (
            f"Geometry type mismatch for layer '{metadata.name}': "
            f"Found {actual_name}, but expected {expected_name}. "
            f"Please select a valid {expected_name.lower()} layer."
        )

    return True, ""


def validate_raster_band(metadata: LayerMetadata, band_number: int) -> tuple[bool, str]:
    """Validate that a specified band number exists in the raster layer."""
    if not metadata or not metadata.is_valid:
        return False, "Layer is not valid"

    if metadata.kind != KIND_RASTER:
        return False, "Layer is not a raster layer"

    band_count = metadata.band_count
    if band_number < 1 or band_number > band_count:
        return False, (
            f"Band number {band_number} is invalid. Layer '{metadata.name}' "
            f"has {band_count} band(s)"
        )

    return True, ""


def validate_structural_requirements(
    metadata: LayerMetadata,
    dip_field: str | None,
    strike_field: str | None,
    context: ValidationContext | None = None,
) -> tuple[bool, str]:
    """Validate structural layer requirements (geometry and attribute fields)."""
    is_valid, msg = _check_struct_layer_validity(metadata)
    if not is_valid:
        if context:
            context.add_error(msg)
        return False, msg

    for field, label in [(dip_field, "Dip"), (strike_field, "Strike")]:
        if field:
            is_valid, msg = _validate_struct_field(metadata, field, label)
            if not is_valid:
                if context:
                    context.add_error(msg)
                return False, msg

    return True, ""


def _check_struct_layer_validity(metadata: LayerMetadata) -> tuple[bool, str]:
    """Check if the structural layer is valid and has point geometry."""
    if not metadata.is_valid:
        return False, f"Structural layer '{metadata.name}' is not valid."

    if metadata.geometry_type != GEOMETRY_POINT:
        return False, "Structural layer must be a point layer."
    return True, ""


def validate_geology_requirements(
    metadata: LayerMetadata,
    field_name: str | None,
    context: ValidationContext | None = None,
) -> tuple[bool, str]:
    """Validate geology layer requirements (polygons and attribute field)."""
    is_valid, error = _check_geology_layer_validity(metadata)
    if not is_valid:
        if context:
            context.add_error(error, "geology_layer")
        return False, error

    if not field_name:
        msg = "Geology unit field is required when geology layer is selected"
        if context:
            context.add_error(msg, "geology_field")
        return False, msg

    is_valid, error = validate_field_exists(metadata, field_name)
    if not is_valid:
        if context:
            context.add_error(error, "geology_field")
        return False, error

    return True, ""


def _check_geology_layer_validity(metadata: LayerMetadata) -> tuple[bool, str]:
    """Check if the geology layer is valid and has polygon geometry."""
    if not metadata.is_valid:
        return False, f"Geology layer '{metadata.name}' is not valid."

    is_valid, error = validate_layer_geometry(metadata, GEOMETRY_POLYGON)
    if not is_valid:
        return False, error

    is_valid, error = validate_layer_has_features(metadata)
    if not is_valid:
        return False, error
    return True, ""


def _validate_struct_field(
    metadata: LayerMetadata, field_name: str, label: str
) -> tuple[bool, str]:
    """Validate a specific structural field existence and type."""
    is_valid, msg = validate_field_exists(metadata, field_name)
    if not is_valid:
        return False, msg

    is_valid, msg = validate_field_type(
        metadata,
        field_name,
        [FieldType.INT, FieldType.DOUBLE, FieldType.LONG_LONG, FieldType.STRING],
    )
    if not is_valid:
        return False, f"{label} field error: {msg}"

    return True, ""


def validate_crs_compatibility(metadata_list: list[LayerMetadata]) -> tuple[bool, str]:
    """Validate that a list of layers have compatible Coordinate Reference Systems.

    If layers have different CRSs, it returns a warning message instead of an error.
    """
    valid = [m for m in metadata_list if m and m.is_valid]
    if not valid:
        return True, ""

    ref = valid[0]
    incompatible = [
        f"  - {m.name}: {m.crs_authid}" for m in valid if m.crs_authid != ref.crs_authid
    ]

    if incompatible:
        warning = (
            f"⚠ CRS mismatch detected!\n\n"
            f"Reference CRS: {ref.crs_authid} ({ref.name})\n"
            f"Incompatible layers:\n" + "\n".join(incompatible) + "\n\n"
            "QGIS will reproject on-the-fly, but this may affect accuracy.\n"
        )
        return False, warning

    return True, ""
