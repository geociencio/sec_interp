"""Layer validation utilities."""
from qgis.core import (
    QgsMapLayer,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsProject,
)
# QVariant is a Qt data type required for QGIS field type validation
# It's not a UI component - it's used to represent generic field values
from qgis.PyQt.QtCore import QVariant  # type: ignore[import]
from .field_validator import validate_field_exists, validate_field_type

def validate_layer_exists(
    layer_name: str | None,
) -> tuple[bool, str, QgsMapLayer | None]:
    """Validate that a layer exists in the project."""
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
    """Validate that a vector layer has at least one feature."""
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
    """Validate that a vector layer has the expected geometry type."""
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
    """Validate that a raster band number is valid for the layer."""
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
    dip_field: str | None,
    strike_field: str | None
) -> tuple[bool, str]:
    """Validate specific requirements for the structural layer."""
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
            layer, dip_field, [QVariant.Int, QVariant.Double, QVariant.LongLong]
        )
        if not is_valid:
            return False, f"Dip field error: {msg}"

    if strike_field:
        is_valid, msg = validate_field_exists(layer, strike_field)
        if not is_valid:
            return False, msg

        is_valid, msg = validate_field_type(
            layer, strike_field, [QVariant.Int, QVariant.Double, QVariant.LongLong]
        )
        if not is_valid:
            return False, f"Strike field error: {msg}"

    return True, ""


def validate_layer_configuration(
    raster_layer: QgsMapLayer | None,
    line_layer: QgsVectorLayer | None,
    outcrop_layer: QgsVectorLayer | None = None,
    structural_layer: QgsVectorLayer | None = None,
    outcrop_field: str | None = None,
    struct_dip_field: str | None = None,
    struct_strike_field: str | None = None,
) -> tuple[bool, str]:
    """Validate the combination of selected layers."""
    # 1. Validate Required Layers
    if not raster_layer or not line_layer:
        return False, "Please select a raster and a line layer."

    if not raster_layer.isValid():
        return False, f"Raster layer '{raster_layer.name()}' is not valid."

    if not line_layer.isValid():
        return False, f"Line layer '{line_layer.name()}' is not valid."

    # 2. Validate Line Geometry
    is_valid, msg = validate_layer_geometry(line_layer, QgsWkbTypes.LineGeometry)
    if not is_valid:
        # Also accept MultiLineString
        is_valid_multi, _msg_multi = validate_layer_geometry(
            line_layer, QgsWkbTypes.MultiLineString
        )
        if not is_valid_multi:
            # Check if generic line type
            if QgsWkbTypes.geometryType(line_layer.wkbType()) != QgsWkbTypes.LineGeometry:
                return False, f"Cross-section layer must be a line layer. {msg}"

    # 3. Validate Optional Layers
    if outcrop_layer:
        if not outcrop_layer.isValid():
            return False, f"Outcrop layer '{outcrop_layer.name()}' is not valid."

        if outcrop_field:
            is_valid, msg = validate_field_exists(outcrop_layer, outcrop_field)
            if not is_valid:
                return False, msg

    if structural_layer:
        is_valid, msg = validate_structural_requirements(
            structural_layer,
            structural_layer.name(),
            struct_dip_field,
            struct_strike_field
        )
        if not is_valid:
            return False, msg

    return True, ""


def validate_crs_compatibility(layers: list[QgsMapLayer]) -> tuple[bool, str]:
    """Validate that all layers have compatible CRS."""
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
