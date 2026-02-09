from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer


class PreviewParamHasher:
    """Handles unique hash calculation for preview parameters."""

    @staticmethod
    def calculate_hash(params: Any) -> str:
        """Calculate a unique hash for preview parameters.

        Args:
            params: PreviewParams object containing layer references and settings.

        Returns:
            SHA256 hash string.

        """
        hash_parts = []

        def get_id(layer: QgsVectorLayer | None) -> str:
            return layer.id() if layer and layer.isValid() else "None"

        # Geometric & Layer IDs
        hash_parts.append(get_id(params.line_layer))
        hash_parts.append(get_id(params.raster_layer))
        hash_parts.append(get_id(params.outcrop_layer))
        hash_parts.append(get_id(params.structure_layer))
        hash_parts.append(get_id(params.drillhole_trace_layer))
        hash_parts.append(get_id(params.drillhole_interval_layer))

        # Settings
        hash_parts.append(str(params.vert_exag))
        hash_parts.append(str(params.buffer_width))
        hash_parts.append(str(params.use_geometry))
        hash_parts.append(str(params.max_points))
        hash_parts.append(str(params.use_adaptive_sampling))
        hash_parts.append(str(params.dip_line_length))

        # Join and hash
        combined = "|".join(hash_parts)
        return hashlib.sha256(combined.encode()).hexdigest()
