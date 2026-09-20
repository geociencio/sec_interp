"""Persistence helpers for the settings page tabs."""

from __future__ import annotations

from typing import Any

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def load_settings(settings: Any, default_tab: Any, advanced_tab: Any) -> None:
    """Load persisted settings into the tab widgets.

    Args:
        settings: QgsSettings-compatible store.
        default_tab: DefaultTab instance.
        advanced_tab: AdvancedTab instance.

    """
    enabled_3d = settings.value("SecInterp/enable_3d", True, type=bool)
    advanced_tab.chk_enable_3d.setChecked(enabled_3d)

    default_tab.chk_exp_topo.setChecked(settings.value("SecInterp/exp_topo", True, type=bool))
    default_tab.chk_exp_geol.setChecked(settings.value("SecInterp/exp_geol", True, type=bool))
    default_tab.chk_exp_struct.setChecked(settings.value("SecInterp/exp_struct", True, type=bool))
    default_tab.chk_exp_drill.setChecked(settings.value("SecInterp/exp_drill", True, type=bool))
    default_tab.chk_exp_interp.setChecked(settings.value("SecInterp/exp_interp", True, type=bool))

    default_fmt = settings.value("SecInterp/export_format", "Shapefile", type=str)
    index = default_tab.combo_format.findText(default_fmt)
    if index >= 0:
        default_tab.combo_format.setCurrentIndex(index)

    default_tab.txt_naming.setText(
        settings.value("SecInterp/export_naming", "{filename}_{profile}", type=str)
    )

    advanced_tab.chk_3d_traces.setChecked(
        settings.value("SecInterp/drill_3d_traces", True, type=bool)
    )
    advanced_tab.chk_3d_intervals.setChecked(
        settings.value("SecInterp/drill_3d_intervals", True, type=bool)
    )
    advanced_tab.chk_3d_original.setChecked(
        settings.value("SecInterp/drill_3d_original", True, type=bool)
    )
    advanced_tab.chk_3d_projected.setChecked(
        settings.value("SecInterp/drill_3d_projected", False, type=bool)
    )


def save_settings(config_service: Any, default_tab: Any, advanced_tab: Any) -> None:
    """Persist the tab widget states through the config service.

    Args:
        config_service: ConfigService-compatible store.
        default_tab: DefaultTab instance.
        advanced_tab: AdvancedTab instance.

    """
    config_service.set("enable_3d", advanced_tab.chk_enable_3d.isChecked())

    config_service.set("exp_topo", default_tab.chk_exp_topo.isChecked())
    config_service.set("exp_geol", default_tab.chk_exp_geol.isChecked())
    config_service.set("exp_struct", default_tab.chk_exp_struct.isChecked())
    config_service.set("exp_drill", default_tab.chk_exp_drill.isChecked())
    config_service.set("exp_interp", default_tab.chk_exp_interp.isChecked())
    config_service.set("export_format", default_tab.combo_format.currentText())
    config_service.set("export_naming", default_tab.txt_naming.text())

    config_service.set("drill_3d_traces", advanced_tab.chk_3d_traces.isChecked())
    config_service.set("drill_3d_intervals", advanced_tab.chk_3d_intervals.isChecked())
    config_service.set("drill_3d_original", advanced_tab.chk_3d_original.isChecked())
    config_service.set("drill_3d_projected", advanced_tab.chk_3d_projected.isChecked())
