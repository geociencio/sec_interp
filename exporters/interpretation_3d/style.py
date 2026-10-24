"""QML and 3D renderer configuration for 3D interpretation exports."""

from __future__ import annotations

from pathlib import Path

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsFillSymbol,
    QgsRendererCategory,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def generate_qml_style(
    shp_path: Path | str,
    interpretations: list[InterpretationPolygon],
    fields: list[QgsField],
    crs: QgsCoordinateReferenceSystem,
) -> None:
    """Generate a QML style file for the exported shapefile."""
    try:
        import qgis._3d  # noqa: F401

        has_3d = True
    except ImportError:
        has_3d = False

    shp_path = Path(shp_path)
    qml_path = shp_path.with_suffix(".qml")

    layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}&z=yes", "temp_style", "memory")
    provider = layer.dataProvider()
    if provider is not None:
        provider.addAttributes(fields)
    layer.updateFields()

    setup_2d_renderer(layer, interpretations)
    if has_3d:
        try:
            configure_3d_renderer(layer, interpretations)
        except Exception as exc:
            logger.warning(f"Failed to configure 3D renderer: {exc}")

    message, ok = layer.saveNamedStyle(str(qml_path))
    if ok:
        logger.info(f"Generated QML style: {qml_path}")
    else:
        logger.warning(f"Failed to save QML style: {message}")


def setup_2d_renderer(layer: QgsVectorLayer, interpretations: list[InterpretationPolygon]) -> None:
    """Set up a categorized 2D renderer for the layer."""
    categories = []
    unique_units = {polygon.name: polygon.color for polygon in interpretations}

    for name, color_hex in unique_units.items():
        color = QColor(color_hex)
        if not color.isValid():
            color = QColor("#FF0000")

        symbol = QgsFillSymbol.createSimple(
            {
                "color": (f"{color.red()},{color.green()},{color.blue()},180"),
                "outline_color": (
                    f"{color.darker(150).red()},"
                    f"{color.darker(150).green()},"
                    f"{color.darker(150).blue()}"
                ),
                "outline_width": "0.3",
            }
        )
        categories.append(QgsRendererCategory(name, symbol, name))

    renderer = QgsCategorizedSymbolRenderer("name", categories)
    layer.setRenderer(renderer)


def configure_3d_renderer(
    layer: QgsVectorLayer, interpretations: list[InterpretationPolygon]
) -> None:
    """Set up a rule-based 3D renderer for the layer."""
    from qgis._3d import (
        QgsPhongMaterialSettings,
        QgsPolygon3DSymbol,
        QgsRuleBased3DRenderer,
    )

    root_rule = QgsRuleBased3DRenderer.Rule(None)
    unique_units = {polygon.name: polygon.color for polygon in interpretations}

    for name, color_hex in unique_units.items():
        color = QColor(color_hex)
        if not color.isValid():
            color = QColor("#FF0000")

        material = QgsPhongMaterialSettings()
        material.setDiffuse(color)
        material.setAmbient(color.lighter(120))

        symbol_3d = QgsPolygon3DSymbol()
        symbol_3d.setMaterialSettings(material)

        filter_expr = f"\"name\" = '{name}'"  # no-i18n
        rule = QgsRuleBased3DRenderer.Rule(symbol_3d, filter_expr, name)
        root_rule.appendChild(rule)

    renderer_3d = QgsRuleBased3DRenderer(root_rule)
    layer.setRenderer3D(renderer_3d)
    logger.debug(f"Configured Rule-Based 3D renderer in QML with {len(unique_units)} categories")
