"""3D QML styles for drillhole traces and intervals."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from qgis.core import QgsLineSymbol, QgsSingleSymbolRenderer, QgsVectorLayer
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

DEFAULT_COLOR = "#3498DB"
DEFAULT_LINE_WIDTH = 2.0


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
        qcolor = QColor(DEFAULT_COLOR)
    material.setDiffuse(qcolor)
    material.setAmbient(qcolor.lighter(120))
    return material


def _new_layer() -> QgsVectorLayer:
    return QgsVectorLayer("LineStringZ?crs=EPSG:4326", "temp_3d_style", "memory")


def _save(layer: QgsVectorLayer, qml_path: Path) -> None:
    message, ok = layer.saveNamedStyle(str(qml_path))
    if not ok:
        logger.warning(f"Failed to save drillhole 3D style: {message}")


def generate_trace_style(
    output_path: str | Path,
    layer_name: str | None = None,
    color: str = DEFAULT_COLOR,
) -> None:
    """Generate a single-symbol 3D tube style for drillhole traces."""
    try:
        from qgis._3d import QgsLine3DSymbol, QgsRuleBased3DRenderer

        symbol = QgsLine3DSymbol()
        symbol.setWidth(DEFAULT_LINE_WIDTH)
        symbol.setMaterialSettings(_material(color))

        root = QgsRuleBased3DRenderer.Rule(None)
        root.appendChild(QgsRuleBased3DRenderer.Rule(symbol, "", "trace"))
        layer = _new_layer()
        layer.setRenderer(
            QgsSingleSymbolRenderer(cast(Any, QgsLineSymbol.createSimple({"color": color})))
        )
        layer.setRenderer3D(QgsRuleBased3DRenderer(root))
        _save(layer, _qml_path(output_path, layer_name))
    except Exception as exc:
        logger.warning(f"Could not generate drillhole trace 3D style: {exc}")


def generate_interval_style(
    output_path: str | Path,
    units: dict[str, str],
    layer_name: str | None = None,
) -> None:
    """Generate a categorized 3D tube style for drillhole intervals."""
    if not units:
        return
    try:
        from qgis._3d import QgsLine3DSymbol, QgsRuleBased3DRenderer

        root = QgsRuleBased3DRenderer.Rule(None)
        for unit, color in units.items():
            symbol = QgsLine3DSymbol()
            symbol.setWidth(DEFAULT_LINE_WIDTH)
            symbol.setMaterialSettings(_material(color))
            expression = f"\"unit\" = '{unit.replace(chr(39), chr(39) * 2)}'"  # no-i18n
            root.appendChild(QgsRuleBased3DRenderer.Rule(symbol, expression, unit))

        layer = _new_layer()
        layer.setRenderer(
            QgsSingleSymbolRenderer(cast(Any, QgsLineSymbol.createSimple({"color": DEFAULT_COLOR})))
        )
        layer.setRenderer3D(QgsRuleBased3DRenderer(root))
        _save(layer, _qml_path(output_path, layer_name))
    except Exception as exc:
        logger.warning(f"Could not generate drillhole interval 3D style: {exc}")
