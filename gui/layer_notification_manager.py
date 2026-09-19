"""Layer change notification wiring for automatic cache invalidation.

Lives in the GUI layer because it wires QGIS layer signals; it invokes the
core ``DataCache.invalidate`` method in response to those signals.
"""

from __future__ import annotations

import contextlib
from typing import Any

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_DRILL_BUCKETS = {"drill_collar", "drill_survey", "drill_interval"}


class LayerNotificationManager:
    """Connects layer ``dataChanged`` signals to cache invalidation."""

    def __init__(self, data_cache: Any) -> None:
        """Initialize the notification manager.

        Args:
            data_cache: The core DataCache to invalidate on layer changes.

        """
        self.data_cache = data_cache
        self._connected_layers: list[tuple[Any, Any]] = []

    def connect(self, layers: dict[str, Any]) -> None:
        """Connect cache invalidation to the given layers.

        Args:
            layers: Mapping of bucket name to QgsMapLayer objects.

        """
        self.disconnect()
        for bucket, layer in layers.items():
            if not layer:
                continue

            cache_bucket = "drill" if bucket in _DRILL_BUCKETS else bucket
            callback = self._create_invalidation_callback(cache_bucket)
            layer.dataChanged.connect(callback)
            self._connected_layers.append((layer, callback))
            logger.debug(
                f"Connected cache invalidation to layer: {layer.name()} -> bucket: {cache_bucket}"
            )

    def disconnect(self) -> None:
        """Disconnect all previously connected layer signals."""
        for layer, callback in self._connected_layers:
            with contextlib.suppress(Exception):
                layer.dataChanged.disconnect(callback)
        self._connected_layers.clear()
        logger.debug("Layer signals disconnected")

    def _create_invalidation_callback(self, bucket: str):
        """Create a callback for bucket-specific cache invalidation.

        The ``section`` bucket is the base geometry and invalidates all
        cache buckets.
        """

        def callback() -> None:
            """Invalidate the cache bucket."""
            if bucket == "section":
                return self.data_cache.invalidate()
            return self.data_cache.invalidate(bucket)

        return callback
