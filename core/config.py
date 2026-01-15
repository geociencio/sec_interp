from typing import Any

from qgis.core import QgsSettings

from sec_interp.core.models.settings_model import PluginSettings
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service to handle plugin configuration and persistent settings."""

    PREFIX = "SecInterp/"

    # Non-persistent constants
    SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg"]
    SUPPORTED_VECTOR_FORMATS = [".shp"]
    SUPPORTED_DOCUMENT_FORMATS = [".pdf", ".svg"]

    def __init__(self):
        """Initialize the Configuration Service with QgsSettings."""
        self.settings = QgsSettings()
        self._current_settings: PluginSettings | None = None

    def get_all_settings(self) -> PluginSettings:
        """Load and return all settings as a validated PluginSettings object."""
        if self._current_settings is None:
            self._current_settings = self._load_from_qgs_settings()
        return self._current_settings

    def _load_from_qgs_settings(self) -> PluginSettings:
        """Gather all settings from QgsSettings and create a validated model."""
        data = {}
        # We could implement a more sophisticated mapping here if needed.
        # For now, we'll rely on the existing get() pattern to populate categories.

        # Section
        data["section"] = {
            "layer_id": self.get("section_layer", ""),
            "layer_name": self.get("section_layer_name", ""),
            "buffer_dist": self.get("buffer_dist", 100.0),
        }

        # DEM
        data["dem"] = {
            "layer_id": self.get("dem_layer", ""),
            "layer_name": self.get("dem_layer_name", ""),
            "band": self.get("dem_band", 1),
            "scale": self.get("scale", 50000.0),
            "vert_exag": self.get("vert_exag", 1.0),
        }

        # Geology
        data["geology"] = {
            "layer_id": self.get("geol_layer", ""),
            "layer_name": self.get("geol_layer_name", ""),
            "field": self.get("geol_field", ""),
        }

        # Structure
        data["structure"] = {
            "layer_id": self.get("struct_layer", ""),
            "layer_name": self.get("struct_layer_name", ""),
            "dip_field": self.get("struct_dip_field", ""),
            "strike_field": self.get("struct_strike_field", ""),
            "dip_scale_factor": self.get("dip_scale_factor", 1.0),
        }

        # Drillhole
        data["drillhole"] = {
            "collar_layer_id": self.get("dh_collar_layer", ""),
            "collar_layer_name": self.get("dh_collar_layer_name", ""),
            "collar_id_field": self.get("dh_collar_id", ""),
            "use_geom": self.get("dh_use_geom", True),
            "collar_x_field": self.get("dh_collar_x", ""),
            "collar_y_field": self.get("dh_collar_y", ""),
            "collar_z_field": self.get("dh_collar_z", ""),
            "collar_depth_field": self.get("dh_collar_depth", ""),
            "survey_layer_id": self.get("dh_survey_layer", ""),
            "survey_layer_name": self.get("dh_survey_layer_name", ""),
            "survey_id_field": self.get("dh_survey_id", ""),
            "survey_depth_field": self.get("dh_survey_depth", ""),
            "survey_azim_field": self.get("dh_survey_azim", ""),
            "survey_incl_field": self.get("dh_survey_incl", ""),
            "interval_layer_id": self.get("dh_interval_layer", ""),
            "interval_layer_name": self.get("dh_interval_layer_name", ""),
            "interval_id_field": self.get("dh_interval_id", ""),
            "interval_from_field": self.get("dh_interval_from", ""),
            "interval_to_field": self.get("dh_interval_to", ""),
            "interval_lith_field": self.get("dh_interval_lith", ""),
            "export_3d_traces": self.get("drill_3d_traces", True),
            "export_3d_intervals": self.get("drill_3d_intervals", True),
            "export_3d_original": self.get("drill_3d_original", True),
            "export_3d_projected": self.get("drill_3d_projected", False),
        }

        # Interpretation
        import json

        custom_fields_str = self.get("interp_custom_fields", "[]")
        try:
            custom_fields = json.loads(custom_fields_str)
        except (ValueError, TypeError):
            custom_fields = []

        data["interpretation"] = {
            "inherit_geol": self.get("interp_inherit_geol", True),
            "inherit_drill": self.get("interp_inherit_drill", True),
            "custom_fields": custom_fields,
        }

        # Preview
        data["preview"] = {
            "show_topo": self.get("show_topo", True),
            "show_geol": self.get("show_geol", True),
            "show_struct": self.get("show_struct", True),
            "show_drillholes": self.get("show_drillholes", True),
            "show_interpretations": self.get("show_interpretations", True),
            "auto_lod": self.get("auto_lod", False),
            "adaptive_sampling": self.get("adaptive_sampling", True),
            "max_points": self.get("max_points", 10000),
        }

        data["last_output_dir"] = self.get("last_output_dir", "")

        try:
            return PluginSettings.from_dict(data)
        except Exception:
            logger.exception("Failed to validate settings during load. Using defaults.")
            return PluginSettings()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key (without prefix).
            default: Optional default value if not found in settings or defaults.

        Returns:
            The configuration value from settings or its default value.

        """
        full_key = self.PREFIX + key

        # Internal static defaults for backward compatibility if needed
        # (Though we prefer the model now)
        static_defaults = {
            "scale": 50000.0,
            "vert_exag": 1.0,
            "buffer_dist": 100.0,
            "dip_scale_factor": 1.0,
            "last_output_dir": "",
            "dpi": 300,
            "preview_width": 800,
            "preview_height": 600,
            "sampling_interval": 10.0,
            "export_quality": 95,
            "auto_lod": True,
            "max_preview_points": 10000,
            "max_points": 10000,
            "dh_use_geom": True,
            "interp_inherit_geol": True,
            "interp_inherit_drill": True,
            "show_topo": True,
            "show_geol": True,
            "show_struct": True,
            "show_drillholes": True,
            "show_interpretations": True,
            "adaptive_sampling": True,
            "dem_band": 1,
        }

        if default is None:
            default = static_defaults.get(key)

        value = self.settings.value(full_key, None)
        if value is None:
            value = self.settings.value("/SecInterp/" + key, default)

        # QgsSettings can return string representations of bools
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            if value.lower() == "false":
                return False

        return value

    def set(self, key: str, value: Any) -> None:
        """Store a configuration value.

        Args:
            key: The configuration key (without prefix).
            value: The value to persist in settings.

        """
        full_key = self.PREFIX + key
        self.settings.setValue(full_key, value)
        self.settings.sync()
        # Invalidate current settings cache so it's reloaded if needed
        self._current_settings = None
        logger.debug(f"Config set: {full_key} = {value}")

    def reset_defaults(self) -> None:
        """Reset all known persistent settings to their default values."""
        logger.info("Configuration reset to defaults initiated")
        self.set("scale", 50000.0)
        self.set("vert_exag", 1.0)
        self.set("buffer_dist", 100.0)
        self.set("show_topo", True)
        self.set("show_geol", True)
        self.set("show_struct", True)
        self.set("show_drillholes", True)
        self.set("show_interpretations", True)
        self.set("interp_inherit_geol", True)
        self.set("interp_inherit_drill", True)
        self.set("dh_use_geom", True)
        self.set("auto_lod", False)
        self.set("adaptive_sampling", True)
        self.set("max_points", 10000)
        self.set("dem_band", 1)
