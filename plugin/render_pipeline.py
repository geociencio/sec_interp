"""Preview rendering pipeline for the SecInterp plugin."""

from __future__ import annotations

from typing import Any

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
        **kwargs,
    ) -> None:
        """Draw enhanced interactive preview using native PyQGIS renderer."""
        if not self.dlg or not self.preview_renderer:
            logger.warning("Cannot draw preview: dialog or renderer missing.")
            return

        options = self.dlg.get_preview_options()
        vert_exag = self.dlg.page_dem.vertexag_spin.value()
        dip_length = self._calculate_dip_length(struct_data)

        filtered = self._get_filtered_preview_data(
            topo_data, geol_data, struct_data, drillhole_data, options
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
        )

        if canvas is None:
            logger.debug("draw_preview: Render skipped (lock active or no data)")
            return

        self.dlg.render_state.update(canvas, layers)

        if hasattr(self.dlg, "legend_widget"):
            self.dlg.legend_widget.update_legend(
                self.preview_renderer, options.get("show_legend", True)
            )

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
        if raster_layer and raster_layer.isValid():
            res = raster_layer.rasterUnitsPerPixelX()
            if res > 0:
                return res * dip_scale
        return None
