"""3D QML styles for section topography, geology and structures."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from qgis.core import (
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

DEFAULT_TOPO_COLOR = "#2C3E50"
DEFAULT_STRUCTURE_COLOR = "#E74C3C"
DEFAULT_GEOLOGY_COLOR = "#27AE60"
DEFAULT_WIDTH = 2.0
DEFAULT_EXTRUSION = 1.0


def _qml_path(output_path: str | Path, layer_name: str | None) -> Path:
    """Return a sidecar path that does not collide inside a GeoPackage."""
    path = Path(output_path)
    if path.suffix.lower() == ".gpkg" and layer_name:
        return path.with_name(f"{path.stem}_{layer_name}.qml")
    return path.with_suffix(".qml")


def _material(color: str) -> Any:
    from qgis._3d import QgsPhongMaterialSettings

    material = QgsPhongMaterialSettings()
    qcolor = QColor(color)
    if not qcolor.isValid():
        qcolor = QColor(DEFAULT_TOPO_COLOR)
    material.setDiffuse(qcolor)
    material.setAmbient(qcolor.lighter(120))
    return material


def _save(layer: QgsVectorLayer, output_path: str | Path, layer_name: str | None) -> None:
    qml_path = _qml_path(output_path, layer_name)
    message, ok = layer.saveNamedStyle(str(qml_path))
    if not ok:
        logger.warning(f"Failed to save section 3D style: {message}")


def generate_line_style(
    output_path: str | Path,
    layer_name: str | None = None,
    color: str = DEFAULT_TOPO_COLOR,
) -> None:
    """Generate a 3D line style for topography."""
    try:
        from qgis._3d import QgsLine3DSymbol, QgsRuleBased3DRenderer

        symbol = QgsLine3DSymbol()
        symbol.setWidth(DEFAULT_WIDTH)
        symbol.setMaterialSettings(_material(color))
        root = QgsRuleBased3DRenderer.Rule(None)
        root.appendChild(QgsRuleBased3DRenderer.Rule(symbol, "", "topography"))
        layer = QgsVectorLayer("LineStringZ?crs=EPSG:4326", "temp_topo_3d", "memory")
        layer.setRenderer(
            QgsSingleSymbolRenderer(cast(Any, QgsLineSymbol.createSimple({"color": color})))
        )
        layer.setRenderer3D(QgsRuleBased3DRenderer(root))
        _save(layer, output_path, layer_name)
    except Exception as exc:
        logger.warning(f"Could not generate topography 3D style: {exc}")


def generate_geology_style(
    output_path: str | Path,
    units: dict[str, str],
    layer_name: str | None = None,
    extrusion_height: float = DEFAULT_EXTRUSION,
) -> None:
    """Generate a categorized 3D polygon style for geology units."""
    if not units:
        return
    try:
        from qgis._3d import QgsPolygon3DSymbol, QgsRuleBased3DRenderer

        root = QgsRuleBased3DRenderer.Rule(None)
        for unit, color in units.items():
            symbol = QgsPolygon3DSymbol()
            symbol.setExtrusionHeight(extrusion_height)
            symbol.setMaterialSettings(_material(color))
            expression = f"\"unit\" = '{unit.replace(chr(39), chr(39) * 2)}'"  # no-i18n
            root.appendChild(QgsRuleBased3DRenderer.Rule(symbol, expression, unit))
        layer = QgsVectorLayer("PolygonZ?crs=EPSG:4326", "temp_geol_3d", "memory")
        layer.setRenderer(
            QgsSingleSymbolRenderer(
                cast(Any, QgsFillSymbol.createSimple({"color": DEFAULT_GEOLOGY_COLOR}))
            )
        )
        layer.setRenderer3D(QgsRuleBased3DRenderer(root))
        _save(layer, output_path, layer_name)
    except Exception as exc:
        logger.warning(f"Could not generate geology 3D style: {exc}")


def generate_point_style(
    output_path: str | Path,
    layer_name: str | None = None,
    color: str = DEFAULT_STRUCTURE_COLOR,
) -> None:
    """Generate a 3D point style for structural measurements."""
    try:
        from qgis._3d import QgsPoint3DSymbol, QgsRuleBased3DRenderer

        symbol = QgsPoint3DSymbol()
        symbol.setShape(QgsPoint3DSymbol.Shape.Cylinder)
        symbol.setMaterialSettings(_material(color))
        root = QgsRuleBased3DRenderer.Rule(None)
        root.appendChild(QgsRuleBased3DRenderer.Rule(symbol, "", "structures"))
        layer = QgsVectorLayer("PointZ?crs=EPSG:4326", "temp_struct_3d", "memory")
        layer.setRenderer(
            QgsSingleSymbolRenderer(cast(Any, QgsMarkerSymbol.createSimple({"color": color})))
        )
        layer.setRenderer3D(QgsRuleBased3DRenderer(root))
        _save(layer, output_path, layer_name)
    except Exception as exc:
        logger.warning(f"Could not generate structures 3D style: {exc}")
