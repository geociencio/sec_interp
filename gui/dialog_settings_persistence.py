"""Settings persistence manager for SecInterp main dialog."""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any

from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog

logger = get_logger(__name__)


class DialogSettingsPersistence:
    """Manages saving and loading of dialog settings using QgsSettings and Project entries.

    Pages expose a ``dump()``/``load()``/``reset()`` protocol so this manager
    no longer reaches into individual page widgets by attribute name.
    """

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize settings persistence manager."""
        self.dialog = dialog
        self.config = None
        if hasattr(self.dialog, "plugin_instance") and self.dialog.plugin_instance:
            self.config = self.dialog.plugin_instance.controller.config_service

    def _data_pages(self) -> list[Any]:
        """Return the configuration pages with persistable state."""
        return [
            self.dialog.page_section,
            self.dialog.page_dem,
            self.dialog.page_geology,
            self.dialog.page_struct,
            self.dialog.page_drillhole,
            self.dialog.page_interpretation,
        ]

    def load_settings(self) -> None:
        """Load user settings from previous session."""
        for page in self._data_pages():
            page.load(self._read_page(page))
        self._load_output_settings()
        self.dialog.preview_widget.load(self._read_page(self.dialog.preview_widget))
        self._load_unit_style()
        self._load_symbology()

    def _symbology_tab(self) -> Any:
        """Return the settings Symbology tab, if available."""
        return getattr(getattr(self.dialog, "page_settings", None), "symbology_tab", None)

    def _save_symbology(self) -> None:
        """Persist the per-layer symbology in the project."""
        tab = self._symbology_tab()
        if tab is None:
            return
        data = tab.get_data()
        if isinstance(data, dict):
            self._set_setting("symbology", json.dumps(data))

    def _load_symbology(self) -> None:
        """Restore the per-layer symbology from the project."""
        tab = self._symbology_tab()
        if tab is None:
            return
        data = self._parse_persisted_value("symbology")
        if isinstance(data, dict):
            tab.load(data)

    def _unit_color_manager(self) -> Any:
        """Return the preview renderer's ColorManager, if available."""
        plugin = getattr(self.dialog, "plugin_instance", None)
        renderer = getattr(plugin, "preview_renderer", None)
        factory = getattr(renderer, "layer_factory", None)
        return getattr(factory, "color_manager", None)

    def _save_unit_style(self) -> None:
        """Persist per-unit color overrides and hidden flags."""
        manager = self._unit_color_manager()
        if manager is None:
            return
        try:
            self._set_setting("unit_style", json.dumps(manager.dump()))
        except (TypeError, ValueError) as e:
            logger.warning("Could not persist unit style: %s", e)

    def _load_unit_style(self) -> None:
        """Restore per-unit color overrides and hidden flags."""
        manager = self._unit_color_manager()
        if manager is None:
            return
        data = self._parse_persisted_value("unit_style")
        if isinstance(data, dict):
            manager.load(data)

    def save_settings(self) -> None:
        """Save user settings for next session."""
        if not self.config:
            return

        for page in self._data_pages():
            self._write_page(page, page.dump())
        self._save_output_settings()
        self._write_page(self.dialog.preview_widget, self.dialog.preview_widget.dump())
        self._save_unit_style()
        self._save_symbology()

        # Trigger a fresh reload of settings in the controller
        if self.config and hasattr(self.dialog, "plugin_instance"):
            with contextlib.suppress(Exception):
                self.dialog.plugin_instance.controller.reload_settings()

    def reset_pages(self) -> None:
        """Reset all dialog inputs in pages to their default values."""
        for page in self._data_pages():
            page.reset()

        self.dialog.output_widget.setFilePath("")

        if hasattr(self.dialog, "page_settings"):
            self.dialog.page_settings._reset_export_defaults()

    def reset_preview(self) -> None:
        """Reset preview settings to defaults."""
        self.dialog.preview_widget.reset()

    # --- Page protocol helpers ---

    def _write_page(self, page: Any, data: dict[str, Any]) -> None:
        """Persist a page's dumped values."""
        layer_keys = getattr(page, "layer_keys", frozenset())
        for key, value in data.items():
            if key in layer_keys:
                self._save_layer_value(key, value)
            elif isinstance(value, dict | list):
                self._set_setting(key, json.dumps(value))
            else:
                self._set_setting(key, value)

    def _read_page(self, page: Any) -> dict[str, Any]:
        """Read persisted values and resolve layers for a page."""
        layer_keys = getattr(page, "layer_keys", frozenset())
        data: dict[str, Any] = {}
        for key in page.dump():
            if key in layer_keys:
                data[key] = self._resolve_layer_value(key)
            else:
                data[key] = self._parse_persisted_value(key)
        return data

    def _parse_persisted_value(self, key: str) -> Any:
        """Read a value, transparently decoding JSON arrays/objects."""
        val = self._get_setting(key)
        if isinstance(val, str) and val[:1] in ("[", "{"):
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return val
        return val

    def _save_layer_value(self, key: str, layer: Any) -> None:
        """Store a layer reference as ID + name."""
        if layer:
            self._set_setting(key, layer.id())
            self._set_setting(f"{key}_name", layer.name())
        else:
            self._set_setting(key, "")
            self._set_setting(f"{key}_name", "")

    def _resolve_layer_value(self, key: str) -> Any:
        """Resolve a stored layer ID/name back into a layer."""
        layer_id = self._get_setting(key)
        layer_name = self._get_setting(f"{key}_name")
        return self._find_layer_by_id_or_name(layer_id, layer_name)

    # --- Output widget ---

    def _load_output_settings(self) -> None:
        last_dir = self._get_setting("last_output_dir")
        if last_dir:
            self.dialog.output_widget.setFilePath(str(last_dir))

    def _save_output_settings(self) -> None:
        self._set_setting("last_output_dir", self.dialog.output_widget.filePath())

    # --- Storage handlers ---

    def _get_setting(self, key: str, default: Any = None) -> Any:
        val, ok = self.dialog.project.readEntry("SecInterp", key, "")
        if not ok or val in (None, "", "None", "NULL"):
            val, ok = self.dialog.project.readEntry("SecInterpUI", key, "")
        if ok and val not in (None, "", "None", "NULL"):
            parsed = self._parse_setting_value(val)
            if parsed is not None:
                return parsed
        if self.config:
            try:
                val = self.config.get(key, default)
                parsed = self._parse_setting_value(val)
                if parsed is not None:
                    return parsed
            except Exception as e:
                logger.warning(f"Failed to read setting '{key}': {e}")
        return default

    def _set_setting(self, key: str, value: Any) -> None:
        if value is None:
            value = ""
        self.dialog.project.writeEntry("SecInterp", key, str(value))
        if self.config:
            self.config.set(key, value)

    def _parse_setting_value(self, val: Any) -> Any:
        if val in (None, "", "None", "NULL"):
            return None
        val_str = str(val).lower()
        if val_str == "true":
            return True
        if val_str == "false":
            return False
        try:
            if "." in str(val):
                return float(val)
            return int(val)
        except (ValueError, TypeError):
            return val

    def _find_layer_by_id_or_name(self, layer_id: Any, layer_name: Any) -> Any:
        if not layer_id and not layer_name:
            return None
        layer = self._find_layer_by_id(layer_id)
        if layer:
            return layer
        return self._find_layer_by_name(layer_name)

    def _find_layer_by_id(self, layer_id: Any) -> Any:
        if not layer_id:
            return None
        return self.dialog.project.mapLayer(str(layer_id))

    def _find_layer_by_name(self, layer_name: Any) -> Any:
        if not layer_name:
            return None
        for lyr in self.dialog.project.mapLayers().values():
            if lyr.name() == layer_name:
                return lyr
        return None
