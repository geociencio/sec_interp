"""Input extraction and validation for the SecInterp plugin."""

from __future__ import annotations

import contextlib

from qgis.core import QgsMapLayer

from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import SecInterpError
from sec_interp.gui.adapters.layer_resolver import resolve_layer
from sec_interp.gui.preview_param_hasher import assemble_preview_params
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class InputValidationMixin:
    """Retrieve and validate dialog inputs, then arm layer notifications."""

    def _get_and_validate_inputs(self) -> PreviewParams | None:
        """Retrieve and validate inputs from the dialog."""
        values = self.dlg.get_selected_values()
        preview_options = self.dlg.get_preview_options()

        try:
            params = assemble_preview_params(
                values,
                preview_options,
                self.dlg.preview_widget.canvas.width(),
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
