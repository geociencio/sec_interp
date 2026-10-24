"""Layer and rubber-band cleanup helpers for PreviewRenderer."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsProject, QgsWkbTypes

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def cleanup_layers(renderer: Any, layers: list | None = None) -> None:
    """Safely remove transient layers from the project."""
    if layers is None:
        layers = renderer.layers

    project = QgsProject.instance()
    if not project or not layers:
        return

    valid_ids = get_valid_layer_ids(layers)
    if valid_ids:
        logger.debug(f"PreviewRenderer: Requesting removal of {len(valid_ids)} transient layers")
        try:
            project.removeMapLayers(valid_ids)
            logger.debug("PreviewRenderer map layer cleanup successful")
        except Exception as exc:
            logger.warning(f"Non-critical error during layer cleanup: {exc}")

    renderer.layers = []
    renderer.layer_factory.active_units = {}
    cleanup_rubber_bands(renderer)
    logger.debug("PreviewRenderer cleanup completed")


def get_valid_layer_ids(layers: list) -> list[str]:
    """Extract valid IDs from a list of layers, handling stale objects."""
    valid_ids = []
    for layer in layers:
        try:
            if layer and hasattr(layer, "id"):
                valid_ids.append(layer.id())
        except (RuntimeError, AttributeError):
            continue
    return valid_ids


def cleanup_rubber_bands(renderer: Any) -> None:
    """Thoroughly clean up interpretation rubber bands."""
    if not renderer.canvas or not renderer.canvas.scene():
        renderer.interpretation_rubbers = []
        return

    scene = renderer.canvas.scene()
    for rubber_band in renderer.interpretation_rubbers:
        if not rubber_band:
            continue
        try:
            rubber_band.hide()
            rubber_band.reset(QgsWkbTypes.GeometryType.PolygonGeometry)
            scene.removeItem(rubber_band)
        except Exception as exc:
            logger.warning(f"Failed to remove rubber band: {exc}")

    renderer.interpretation_rubbers = []
    logger.debug("PreviewRenderer cleanup completed")
