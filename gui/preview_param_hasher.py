"""Configuration hashing for preview change detection."""

from __future__ import annotations

import hashlib
from typing import Any

from sec_interp.core.domain import PreviewParams


def assemble_preview_params(
    values: dict[str, Any], preview_options: dict[str, Any], canvas_width: int
) -> PreviewParams:
    """Assemble PreviewParams from raw dialog values without side effects.

    Pure assembly step shared by input validation and preview-currency checks:
    no ``validate()`` call, no error dialogs, no layer-notification wiring, and
    no geometry reads (the hasher only uses layer ``.id()`` values and primitives,
    so this stays cheap enough to run on every UI state refresh).

    Args:
        values: Flattened page values (``get_selected_values()``).
        preview_options: Preview widget options (``get_preview_options()``).
        canvas_width: Current preview canvas width in pixels.

    Returns:
        Unvalidated PreviewParams.

    """
    return PreviewParams(
        raster_layer=values.get("raster_layer"),
        line_layer=values.get("crossline_layer"),
        band_num=values.get("selected_band", 1),
        buffer_dist=values.get("buffer_distance", 100.0),
        section_feature_id=values.get("section_feature_id"),
        outcrop_layer=values.get("outcrop_layer"),
        outcrop_name_field=values.get("outcrop_name_field"),
        struct_layer=values.get("structural_layer"),
        dip_field=values.get("dip_field"),
        strike_field=values.get("strike_field"),
        dip_scale_factor=values.get("dip_scale_factor", 1.0),
        collar_layer=values.get("collar_layer_obj"),
        collar_id_field=values.get("collar_id_field"),
        collar_use_geometry=values.get("collar_use_geometry", True),
        collar_x_field=values.get("collar_x_field"),
        collar_y_field=values.get("collar_y_field"),
        collar_z_field=values.get("collar_z_field"),
        collar_depth_field=values.get("collar_depth_field"),
        survey_layer=values.get("survey_layer_obj"),
        survey_id_field=values.get("survey_id_field"),
        survey_depth_field=values.get("survey_depth_field"),
        survey_azim_field=values.get("survey_azim_field"),
        survey_incl_field=values.get("survey_incl_field"),
        interval_layer=values.get("interval_layer_obj"),
        interval_id_field=values.get("interval_id_field"),
        interval_from_field=values.get("interval_from_field"),
        interval_to_field=values.get("interval_to_field"),
        interval_lith_field=values.get("interval_lith_field"),
        max_points=preview_options.get("max_points", 1000),
        auto_lod=preview_options.get("auto_lod", True),
        canvas_width=canvas_width,
    )


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
        hash_parts.append(str(params.section_feature_id))

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
