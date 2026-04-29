"""Configuration hashing for preview change detection."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


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

        def get_id(layer: Any) -> str:
            """Extract ID from a layer object or string.

            Args:
                layer: QgsMapLayer object or string ID.

            Returns:
                Layer ID string.

            """
            if isinstance(layer, str):
                return layer
            return layer.id() if hasattr(layer, "id") else "None"

        # Geometric & Layer IDs
        hash_parts.append(get_id(params.line_layer))
        hash_parts.append(get_id(params.raster_layer))
        hash_parts.append(get_id(params.outcrop_layer))
        hash_parts.append(get_id(params.struct_layer))
        hash_parts.append(get_id(params.collar_layer))
        hash_parts.append(get_id(params.survey_layer))
        hash_parts.append(get_id(params.interval_layer))

        # Core Settings
        hash_parts.append(str(params.band_num))
        hash_parts.append(str(params.buffer_dist))

        # Structure Settings
        hash_parts.append(str(params.dip_field))
        hash_parts.append(str(params.strike_field))
        hash_parts.append(str(params.dip_scale_factor))

        # Drillhole Settings
        hash_parts.append(str(params.collar_id_field))
        hash_parts.append(str(params.collar_use_geometry))

        # LOD Params
        hash_parts.append(str(params.max_points))
        hash_parts.append(str(params.canvas_width))
        hash_parts.append(str(params.auto_lod))

        # Join and hash
        combined = "|".join(hash_parts)
        return hashlib.sha256(combined.encode()).hexdigest()
