"""Input extraction and validation for the SecInterp plugin."""

from __future__ import annotations

import contextlib

from qgis.core import QgsMapLayer

from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import SecInterpError
from sec_interp.gui.adapters.layer_resolver import resolve_layer
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class InputValidationMixin:
    """Retrieve and validate dialog inputs, then arm layer notifications."""

    def _get_and_validate_inputs(self) -> PreviewParams | None:
        """Retrieve and validate inputs from the dialog."""
        values = self.dlg.get_selected_values()
        preview_options = self.dlg.get_preview_options()

        try:
            params = PreviewParams(
                raster_layer=values.get("raster_layer"),
                line_layer=values.get("crossline_layer"),
                band_num=values.get("selected_band", 1),
                buffer_dist=values.get("buffer_distance", 100.0),
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
                canvas_width=self.dlg.preview_widget.canvas.width(),
            )
            params.validate()

            from sec_interp.core.validation.project_validator import ProjectValidator
            from sec_interp.gui.adapters.validation_extractor import build_validation_params

            ProjectValidator.validate_all(build_validation_params(params))
        except SecInterpError as e:
            self.dlg.handle_error(e, self.tr("Configuration Error"))
            return None
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.dlg.handle_error(e, self.tr("Input Processing Error"))
            return None
        except (MemoryError, SystemError, KeyboardInterrupt):
            raise
        except Exception as e:
            logger.exception("Unexpected error during input processing")
            self.dlg.handle_error(e, self.tr("Unexpected Error"))
            return None

        self.layer_notification_manager.connect(self._collect_active_layers(params))
        return params

    def disconnect_layer_notifications(self) -> None:
        """Disconnect the layer-change notification manager."""
        if getattr(self, "layer_notification_manager", None):
            with contextlib.suppress(Exception):
                self.layer_notification_manager.disconnect()

    def _collect_active_layers(self, params: PreviewParams) -> dict[str, QgsMapLayer]:
        """Collect all active layer objects from parameter IDs for monitoring."""
        mapping = {
            "topo": params.raster_layer,
            "section": params.line_layer,
            "geol": params.outcrop_layer,
            "struct": params.struct_layer,
            "drill_collar": params.collar_layer,
            "drill_survey": params.survey_layer,
            "drill_interval": params.interval_layer,
        }

        active_layers = {}
        for bucket, lid in mapping.items():
            if not lid:
                continue
            lyr = resolve_layer(lid)
            if lyr:
                active_layers[bucket] = lyr

        return active_layers
