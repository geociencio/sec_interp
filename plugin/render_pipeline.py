"""Preview rendering pipeline for the SecInterp plugin."""

from __future__ import annotations

from typing import Any

from sec_interp.core.utils.sampling import smooth_profile_by_distance
from sec_interp.gui.adapters.geometry import raster_resolution_in_crs
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class RenderPipelineMixin:
    """Draw the interactive preview and filter its data by visibility options."""

    def draw_preview(
        self,
        topo_data: list,
        geol_data: list | None = None,
        struct_data: list | None = None,
        drillhole_data: list | None = None,
        max_points: int = 1000,
        vert_exag: float | None = None,
        **kwargs,
    ) -> None:
        """Draw enhanced interactive preview using native PyQGIS renderer."""
        if not self.dlg or not self.preview_renderer:
            logger.warning("Cannot draw preview: dialog or renderer missing.")
            return

        options = self.dlg.get_preview_options()
        if vert_exag is None:
            vert_exag = self.dlg.page_dem.vertexag_spin.value()
        dip_length = self._calculate_dip_length(struct_data)
        style = self.dlg.page_settings.symbology_tab.get_data()

        filtered = self._get_filtered_preview_data(
            topo_data, geol_data, struct_data, drillhole_data, options
        )

        smooth_data = None
        if options.get("smooth") and topo_data:
            smooth_data = smooth_profile_by_distance(
                topo_data, float(options.get("smooth_window", 0) or 0)
            )

        canvas, layers = self.preview_renderer.render(
            topo_data=filtered["topo"],
            geol_data=filtered["geol"],
            struct_data=filtered["struct"],
            vert_exag=vert_exag,
            dip_line_length=dip_length,
            max_points=max_points,
            preserve_extent=kwargs.get("preserve_extent", False),
            drillhole_data=filtered["drill"],
            interp_data=filtered["interp"],
            topo_color_mode=style.get("color_mode", "gradient"),
            topo_ramp_name=style.get("ramp_name"),
            topo_single_color=style.get("single_color_hex"),
            topo_smooth_data=smooth_data,
            layer_styles=style,
        )

        if canvas is None:
            logger.debug("draw_preview: Render skipped (lock active or no data)")
            return

        self.dlg.render_state.update(canvas, layers)

        side_panel = getattr(self.dlg.preview_widget, "side_panel", None)
        if side_panel is not None:
            side_panel.update_legend(self.preview_renderer, options.get("show_legend", True))
            side_panel.update_interpretations(getattr(self.dlg, "interpretations", None))
        symbology_tab = getattr(getattr(self.dlg, "page_settings", None), "symbology_tab", None)
        if symbology_tab is not None:
            symbology_tab.refresh_units()

    def _get_filtered_preview_data(
        self, topo: Any, geol: Any, struct: Any, drill: Any, options: dict
    ) -> dict:
        """Filter data based on visibility options.

        Args:
            topo: Topographic profile data.
            geol: Geological profile data.
            struct: Structural profile data.
            drill: Drillhole profile data.
            options: Dictionary of visibility flags.

        Returns:
            Dictionary containing only visible data components.

        """
        return {
            "topo": topo if options.get("show_topo", True) else None,
            "geol": geol if options.get("show_geol", True) else None,
            "struct": struct if options.get("show_struct", True) else None,
            "drill": drill if options.get("show_drillholes", True) else None,
            "interp": (
                self.dlg.interpretations if options.get("show_interpretations", True) else None
            ),
        }

    def _calculate_dip_length(self, struct_data: list | None) -> float | None:
        """Calculate dip line length based on scale factor and raster resolution.

        Args:
            struct_data: List of structural measurements.

        Returns:
            Calculated dip line length in map units, or None if not applicable.

        """
        if not struct_data:
            return None

        dip_scale = self.dlg.page_struct.scale_spin.value()
        if dip_scale <= 0:
            return None

        raster_layer = self.dlg.page_dem.raster_combo.currentLayer()
        if not raster_layer or not raster_layer.isValid():
            return None

        line_layer = self.dlg.page_section.line_combo.currentLayer()
        line_crs = line_layer.crs() if line_layer else None
        res = raster_resolution_in_crs(raster_layer, line_crs)
        if res and res > 0:
            return res * dip_scale
        return None
