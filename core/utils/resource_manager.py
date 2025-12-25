from __future__ import annotations


"""Resource management utilities for SecInterp.

This module provides context managers for handling temporary QGIS resources
and system files to ensure proper cleanup and prevent resource leaks.
"""

from collections.abc import Generator
import contextlib
import os
import tempfile
from typing import Optional

from qgis.core import QgsMapLayer, QgsProject, QgsVectorLayer

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


@contextlib.contextmanager
def temporary_memory_layer(
    uri: str, name: str, provider: str = "memory"
) -> Generator[QgsVectorLayer, None, None]:
    """Context manager for a temporary QGIS memory layer.

    The layer is created and optionally added to the project.
    It is automatically removed from the project and deleted when the context exits.

    Args:
        uri: Layer URI (e.g., "LineString?crs=EPSG:4326").
        name: Layer name for display.
        provider: Provider ID (default "memory").

    Yields:
        The created temporary layer.
    """
    layer = QgsVectorLayer(uri, name, provider)
    if not layer.isValid():
        logger.error(f"Failed to create temporary layer: {name} (URI: {uri})")
        yield layer
        return

    try:
        logger.debug(f"Created temporary layer: {name}")
        yield layer
    finally:
        if layer.isValid():
            # Ensure it's removed if it was added to the project
            if QgsProject.instance().mapLayer(layer.id()):
                QgsProject.instance().removeMapLayer(layer.id())
            logger.debug(f"Cleaned up temporary layer: {name}")


@contextlib.contextmanager
def temporary_file(
    suffix: Optional[str] = None, prefix: Optional[str] = None, dir: Optional[str] = None
) -> Generator[str, None, None]:
    """Context manager for a temporary file path.

    Creates a temporary file and yields its absolute path.
    The file is automatically deleted when the context exits.

    Args:
        suffix: File suffix.
        prefix: File prefix.
        dir: Directory to create the file in.

    Yields:
        Absolute path to the temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    os.close(fd)
    try:
        yield path
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.debug(f"Removed temporary file: {path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {path}: {e}")


class ResourceManager:
    """Consolidated resource manager for plugin-wide cleanup."""

    @staticmethod
    def cleanup_layer(layer: QgsMapLayer):
        """Standard way to safely remove a layer from the project.

        Args:
            layer: The QGIS map layer to remove.
        """
        if not layer:
            return
        try:
            QgsProject.instance().removeMapLayer(layer.id())
            logger.debug(f"Layer {layer.name()} ({layer.id()}) removed.")
        except Exception as e:
            logger.warning(f"Error removing layer {layer.id()}: {e}")
