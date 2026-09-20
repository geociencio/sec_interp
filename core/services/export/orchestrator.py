"""Export orchestrator — thin facade delegating to handlers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.logger_config import get_logger

from .compat import ExportServiceCompatMixin
from .map_settings_factory import create_map_settings

logger = get_logger(__name__)


class ExportService(ExportServiceCompatMixin):
    """Service to orchestrate all export operations."""

    def __init__(self, controller: Any | None = None) -> None:
        """Initialize the export service.

        Args:
            controller: Optional reference to ProfileController for data access.

        """
        self.controller = controller
        self.access_control = AccessControlService()

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("ExportService", message)  # type: ignore[no-any-return]

    def export_data(
        self,
        output_folder: Path,
        params: PreviewParams,
        profile_data: list[tuple],
        geol_data: list[Any] | None,
        struct_data: list[Any] | None,
        drillhole_data: list[Any] | None = None,
        interp_data: list[Any] | None = None,
        export_options: dict[str, bool] | None = None,
    ) -> list[str]:
        """Export generated data to CSV and Shapefile formats."""
        if export_options is None:
            export_options = {
                "exp_topo": True,
                "exp_geol": True,
                "exp_struct": True,
                "exp_drill": True,
                "exp_interp": True,
            }

        logger.info(f"Export options: {export_options}")

        if not any(export_options.values()):
            logger.warning("All export options are disabled. Nothing will be exported.")
            return [self.tr("⚠ No export options selected. Check Settings tab.")]

        if not profile_data:
            raise DataMissingError(self.tr("No profile data available for export"))

        line_layer = params.line_layer
        if not line_layer:
            raise DataMissingError(self.tr("Section line layer not found in parameters"))

        result_msg = [self.tr("✓ Saving files...")]
        self._orchestrate_exports(
            output_folder,
            params,
            profile_data,
            geol_data,
            struct_data,
            drillhole_data,
            interp_data,
            export_options,
            result_msg,
        )

        result_msg.append(self.tr("\n✓ All files saved to:\n{0}").format(output_folder))
        return result_msg

    def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:
        """Return the resolved line and raster layer objects."""
        line_layer = params.line_layer
        if not line_layer or not line_layer.isValid():
            raise DataMissingError(self.tr("Section line layer not found or invalid"))
        raster_layer = params.raster_layer
        return line_layer, raster_layer

    def _orchestrate_exports(
        self,
        folder: Path,
        params: PreviewParams,
        profile_data: list[tuple],
        geol_data: list[Any] | None,
        struct_data: list[Any] | None,
        drillhole_data: list[Any] | None,
        interp_data: list[Any] | None,
        options: dict[str, Any],
        msg: list[str],
    ) -> None:
        """Call individual exporters based on options."""
        from sec_interp.exporters import CSVExporter

        from .handlers import axes as axes_h
        from .handlers import drillholes as dh_h
        from .handlers import drillholes_3d as dh3_h
        from .handlers import geology as geo_h
        from .handlers import interpretations as interp_h
        from .handlers import structures as struct_h
        from .handlers import topography as topo_h

        line_layer, raster_layer = self._resolve_layers(params)
        line_crs = line_layer.crs()

        export_settings = None
        if self.controller is not None:
            reload_func = getattr(self.controller, "reload_settings", None)
            if reload_func:
                reload_func()
            settings_obj = getattr(self.controller, "settings", None)
            if settings_obj:
                export_settings = getattr(settings_obj, "export", None)

        format_ext = ".shp"
        if export_settings:
            if export_settings.default_format == "GeoPackage":
                format_ext = ".gpkg"
            elif export_settings.default_format == "DXF":
                format_ext = ".dxf"

        csv_exporter = CSVExporter({})

        def topo_handler(settings=export_settings, ext=format_ext) -> None:
            topo_h.export_topography(
                folder, profile_data, line_crs, csv_exporter, msg, self.controller, settings, ext
            )
            axes_h.export_axes(folder, profile_data, line_crs, msg, self.controller, settings, ext)

        handlers = {
            "exp_topo": topo_handler,
            "exp_geol": lambda: geo_h.export_geology(
                folder,
                geol_data,
                line_crs,
                csv_exporter,
                msg,
                self.controller,
                export_settings,
                format_ext,
            ),
            "exp_struct": lambda: struct_h.export_structures(
                folder,
                struct_data,
                raster_layer,
                line_crs,
                csv_exporter,
                msg,
                options,
                self.controller,
                export_settings,
                format_ext,
            ),
            "exp_drill": lambda: dh_h.export_drillholes(
                folder, drillhole_data, line_crs, msg, self.controller, export_settings, format_ext
            ),
            "exp_drill_3d": lambda: dh3_h.export_drillholes_3d(
                folder,
                drillhole_data,
                line_crs,
                msg,
                options,
                self.controller,
                export_settings,
                format_ext,
            ),
            "exp_interp": lambda: interp_h.export_interpretations(
                folder,
                interp_data,
                line_layer,
                line_crs,
                msg,
                self.controller,
                export_settings,
                format_ext,
                self.access_control,
            ),
        }
        for opt, handler in handlers.items():
            if options.get(opt, True):
                handler()

    def get_map_settings(
        self,
        layers: list[Any],
        extent: Any,
        size: Any | None,
        background_color: Any,
    ) -> Any:
        """Create and configure QgsMapSettings for canvas or image export."""
        return create_map_settings(layers, extent, size, background_color)
