from __future__ import annotations

from typing import List, Optional, Tuple, Union

from qgis.core import (
    QgsMapLayer,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.types import FieldType

from .field_validator import validate_field_exists, validate_field_type


def validate_layer_exists(
    layer_name: Optional[str],
) -> tuple[bool, str, Optional[QgsMapLayer]]:
    """Validate that a layer with the given name exists in the current QGIS project.

    Args:
        layer_name: The name of the layer to search for.

    Returns:
        tuple: (is_valid, error_message, layer)
            - is_valid: True if at least one matching layer was found.
            - error_message: Error details if no layer was found.
            - layer: The first matching layer instance if valid, else None.
    """
    if not layer_name:
        return False, "Layer name is required", None

    layers = QgsProject.instance().mapLayersByName(layer_name)

    if not layers:
        return False, f"Layer '{layer_name}' not found in project", None

    layer = layers[0]

    if not layer.isValid():
        return False, f"Layer '{layer_name}' is not valid", None

    return True, "", layer


def validate_layer_has_features(layer: QgsVectorLayer) -> tuple[bool, str]:
    """Validate that a vector layer contains at least one feature.

    Args:
        layer: The QGIS vector layer to check.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if the layer has features.
            - error_message: Error details if the layer is empty.
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsVectorLayer):
        return False, "Layer is not a vector layer"

    if layer.featureCount() == 0:
        return False, f"Layer '{layer.name()}' has no features"

    return True, ""


def validate_layer_geometry(
    layer: QgsVectorLayer, expected_type: QgsWkbTypes.GeometryType
) -> tuple[bool, str]:
    """Validate that a vector layer matches the expected QGIS geometry type.

    Args:
        layer: The QGIS vector layer to check.
        expected_type: The required QgsWkbTypes.GeometryType.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if the geometry type matches.
            - error_message: Detailed error if types mismatch.
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsVectorLayer):
        return False, "Layer is not a vector layer"

    actual_type = QgsWkbTypes.geometryType(layer.wkbType())

    if actual_type != expected_type:
        type_names = {
            QgsWkbTypes.PointGeometry: "Point",
            QgsWkbTypes.LineGeometry: "Line",
            QgsWkbTypes.PolygonGeometry: "Polygon",
            QgsWkbTypes.UnknownGeometry: "Unknown",
            QgsWkbTypes.NullGeometry: "Null",
        }
        expected_name = type_names.get(expected_type, f"Type {expected_type}")
        actual_name = type_names.get(actual_type, f"Type {actual_type}")

        return False, (
            f"Geometry type mismatch for layer '{layer.name()}': "
            f"Found {actual_name}, but expected {expected_name}. "
            f"Please select a valid {expected_name.lower()} layer."
        )

    return True, ""


def validate_raster_band(layer: QgsRasterLayer, band_number: int) -> tuple[bool, str]:
    """Validate that a specified band number exists in the given raster layer.

    Args:
        layer: The QGIS raster layer to check.
        band_number: The 1-based index of the raster band.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if the band exists.
            - error_message: Error message if the band is out of range.
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsRasterLayer):
        return False, "Layer is not a raster layer"

    band_count = layer.bandCount()

    if band_number < 1 or band_number > band_count:
        return False, (
            f"Band number {band_number} is invalid. "
            f"Layer '{layer.name()}' has {band_count} band(s)"
        )

    return True, ""


def validate_structural_requirements(
    layer: QgsVectorLayer,
    layer_name: str,
    dip_field: Optional[str],
    strike_field: Optional[str],
) -> tuple[bool, str]:
    """Validate structural layer requirements (geometry and attribute fields).

    Args:
        layer: The QGIS point layer containing structural data.
        layer_name: Human-readable name of the layer.
        dip_field: Name of the attribute field containing dip values.
        strike_field: Name of the attribute field containing strike values.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if both geometry and fields are valid.
            - error_message: Detailed error if validation fails.
    """
    if not layer.isValid():
        return False, f"Structural layer '{layer_name}' is not valid."

    # Validate geometry (points)
    if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.PointGeometry:
        return False, "Structural layer must be a point layer."

    if dip_field:
        is_valid, msg = validate_field_exists(layer, dip_field)
        if not is_valid:
            return False, msg

        is_valid, msg = validate_field_type(
            layer, dip_field, [FieldType.INT, FieldType.DOUBLE, FieldType.LONG_LONG]
        )
        if not is_valid:
            return False, f"Dip field error: {msg}"

    if strike_field:
        is_valid, msg = validate_field_exists(layer, strike_field)
        if not is_valid:
            return False, msg

        is_valid, msg = validate_field_type(
            layer, strike_field, [FieldType.INT, FieldType.DOUBLE, FieldType.LONG_LONG]
        )
        if not is_valid:
            return False, f"Strike field error: {msg}"

    return True, ""


def validate_layer_configuration(
    raster_layer: Optional[QgsMapLayer],
    line_layer: Optional[QgsVectorLayer],
    outcrop_layer: Optional[QgsVectorLayer] = None,
    structural_layer: Optional[QgsVectorLayer] = None,
    outcrop_field: Optional[str] = None,
    struct_dip_field: Optional[str] = None,
    struct_strike_field: Optional[str] = None,
) -> bool:
    """Validate a complete set of layer inputs for the plugin.

    Args:
        raster_layer: The primary DEM layer.
        line_layer: The section line layer.
        outcrop_layer: Optional geological outcrop layer.
        structural_layer: Optional structural measurement layer.
        outcrop_field: Attribute field for geology units.
        struct_dip_field: Attribute field for dip values.
        struct_strike_field: Attribute field for strike values.

    Returns:
        bool: True if the entire configuration is valid.

    Raises:
        ValidationError: If any configuration check fails.
    """
    # 1. Validate Required Layers
    if not raster_layer or not line_layer:
        raise ValidationError("Please select a raster and a line layer.")

    if not raster_layer.isValid():
        raise ValidationError(f"Raster layer '{raster_layer.name()}' is not valid.")

    if not line_layer.isValid():
        raise ValidationError(f"Line layer '{line_layer.name()}' is not valid.")

    # 2. Validate Line Geometry
    is_valid, msg = validate_layer_geometry(line_layer, QgsWkbTypes.LineGeometry)
    if not is_valid:
        # Also accept MultiLineString
        is_valid_multi, _msg_multi = validate_layer_geometry(
            line_layer, QgsWkbTypes.MultiLineString
        )
        if not is_valid_multi:
            # Check if generic line type
            if (
                QgsWkbTypes.geometryType(line_layer.wkbType())
                != QgsWkbTypes.LineGeometry
            ):
                raise ValidationError(f"Cross-section layer must be a line layer. {msg}")

    # 3. Validate Optional Layers
    if outcrop_layer:
        if not outcrop_layer.isValid():
            raise ValidationError(f"Outcrop layer '{outcrop_layer.name()}' is not valid.")

        if outcrop_field:
            is_valid, msg = validate_field_exists(outcrop_layer, outcrop_field)
            if not is_valid:
                raise ValidationError(msg)

    if structural_layer:
        is_valid, msg = validate_structural_requirements(
            structural_layer,
            structural_layer.name(),
            struct_dip_field,
            struct_strike_field,
        )
        if not is_valid:
            raise ValidationError(msg)

    return True


def validate_crs_compatibility(layers: list[QgsMapLayer]) -> tuple[bool, str]:
    """Validate that a list of layers have compatible Coordinate Reference Systems.

    If layers have different CRSs, it returns a warning message instead of an error,
    as QGIS can reproject on-the-fly, but accuracy might be impaired.

    Args:
        layers: List of QgsMapLayer objects to compare.

    Returns:
        tuple: (is_compatible, message)
            - is_compatible: True if all layers share the same CRS.
            - message: Warning listing incompatible layers if any.
    """
    if not layers:
        return True, ""

    # Get first non-None layer CRS as reference
    reference_crs = None
    reference_layer = None
    for layer in layers:
        if layer and layer.isValid():
            reference_crs = layer.crs()
            reference_layer = layer
            break

    if not reference_crs:
        return True, ""

    # Check all other layers against reference
    incompatible = []
    for layer in layers:
        if layer and layer.isValid() and layer.crs() != reference_crs:
            incompatible.append(f"  - {layer.name()}: {layer.crs().authid()}")

    if incompatible:
        warning = (
            f"⚠ CRS mismatch detected!\n\n"
            f"Reference CRS: {reference_crs.authid()} ({reference_layer.name()})\n"
            f"Incompatible layers:\n" + "\n".join(incompatible) + "\n\n"
            "QGIS will reproject on-the-fly, but this may affect accuracy.\n"
            "Consider reprojecting all layers to the same CRS for best results."
        )
        return False, warning

    return True, ""
