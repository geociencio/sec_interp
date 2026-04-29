"""Export service for SecInterp.

This module provides a service to orchestrate all export operations,
including data (Shapefile, CSV) and preview (PNG, PDF, SVG) exports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import QgsMapSettings, QgsRectangle

from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ExportService:
    """Service to orchestrate all export operations."""

    def __init__(self, controller: Any | None = None) -> None:
        """Initialize the export service.

        Args:
            controller: Optional reference to ProfileController for data access.

        """
        self.controller = controller
        self.access_control = AccessControlService()

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
        """Export generated data to CSV and Shapefile formats.

        Args:
            output_folder: Destination directory for all exported files.
            params: Correctly validated parameters for the export run.
            profile_data: Topographic profile points (dist, elevation).
            geol_data: List of GeologySegment objects.
            struct_data: List of StructureMeasurement objects.
            drillhole_data: Optional list of drillhole data.
            interp_data: Optional list of InterpretationPolygon objects.
            export_options: Dictionary of flags 'exp_topo', 'exp_geol', etc.

        """
        if export_options is None:
            export_options = {
                "exp_topo": True,
                "exp_geol": True,
                "exp_struct": True,
                "exp_drill": True,
                "exp_interp": True,
            }

        # Log parameters for debugging
        logger.info(f"Export options: {export_options}")

        if not any(export_options.values()):
            logger.warning("All export options are disabled. Nothing will be exported.")
            return ["⚠ No export options selected. Check Settings tab."]

        if not profile_data:
            raise DataMissingError("No profile data available for export")

        line_layer = params.line_layer
        if not line_layer:
            raise DataMissingError("Section line layer not found in parameters")

        result_msg = ["✓ Saving files..."]
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

        result_msg.append(f"\n✓ All files saved to:\n{output_folder}")
        return result_msg

    def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:
        """Resolve layer IDs to QgsMapLayer objects.

        Args:
            params: Preview parameters containing optional layer references
                (either QgsMapLayer objects or string IDs).

        Returns:
            Tuple of (line_layer, raster_layer). Raises DataMissingError if
            the section line layer is missing or invalid.

        Raises:
            DataMissingError: If the section line layer is not found or invalid.

        """
        from qgis.core import (
            QgsProject,
        )  # noqa: PLC0415 (lazy: avoids IDE false positives)

        project = QgsProject.instance()

        line_layer = None
        if params.line_layer:
            line_layer = (
                project.mapLayer(params.line_layer)
                if isinstance(params.line_layer, str)
                else params.line_layer
            )

        if not line_layer or not line_layer.isValid():
            raise DataMissingError("Section line layer not found or invalid")

        raster_layer = None
        if params.raster_layer:
            raster_layer = (
                project.mapLayer(params.raster_layer)
                if isinstance(params.raster_layer, str)
                else params.raster_layer
            )

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
        line_layer, raster_layer = self._resolve_layers(params)
        line_crs = line_layer.crs()

        # Get settings or defaults
        export_settings = None
        if self.controller is not None:
            # Ensure settings are current in the controller
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

        from sec_interp.exporters import CSVExporter  # noqa: PLC0415 (lazy, testable)

        csv_exporter = CSVExporter({})

        def topo_handler(settings=export_settings, ext=format_ext) -> None:
            """Handle topographic and axes export."""
            self._export_topography(
                folder, profile_data, line_crs, csv_exporter, msg, settings, ext
            )
            self._export_axes(folder, profile_data, line_crs, msg, settings, ext)

        handlers = {
            "exp_topo": topo_handler,
            "exp_geol": lambda: self._export_geology(
                folder,
                geol_data,
                line_crs,
                csv_exporter,
                msg,
                export_settings,
                format_ext,
            ),
            "exp_struct": lambda: self._export_structures(
                folder,
                struct_data,
                raster_layer,
                line_crs,
                csv_exporter,
                msg,
                options,
                export_settings,
                format_ext,
            ),
            "exp_drill": lambda: self._export_drillholes(
                folder,
                drillhole_data,
                line_crs,
                msg,
                export_settings,
                format_ext,
            ),
            "exp_drill_3d": lambda: self._export_drillholes_3d(
                folder,
                drillhole_data,
                line_crs,
                msg,
                options,
                export_settings,
                format_ext,
            ),
            "exp_interp": lambda: self._export_interpretations(
                folder,
                interp_data,
                line_layer,
                line_crs,
                msg,
                export_settings,
                format_ext,
            ),
        }
        for opt, handler in handlers.items():
            if options.get(opt, True):
                handler()

    def _export_topography(
        self,
        folder: Path,
        data: list[tuple],
        crs: Any,
        csv_exporter: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export topographic data."""
        from sec_interp.exporters import ProfileLineVectorExporter

        logger.info("✓ Saving topographic profile...")
        try:
            csv_path, csv_layer = self._get_export_path(folder, "topo_profile", settings, ".csv")
            csv_ok = csv_exporter.export(
                csv_path,
                {"headers": ["dist", "elev"], "rows": data},
                layer_name=csv_layer,
            )
            if csv_ok:
                msg.append(f"  - {csv_path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write CSV topography to {csv_path}")

            vec_path, vec_layer = self._get_export_path(folder, "profile_line", settings, ext)
            vector_exporter = ProfileLineVectorExporter({})
            vec_ok = vector_exporter.export(
                vec_path, {"profile_data": data, "crs": crs}, layer_name=vec_layer
            )
            if vec_ok:
                msg.append(f"  - {vec_path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write vector topography to {vec_path}")

        except (OSError, ValueError, TypeError, DataMissingError) as e:
            logger.exception(f"Topography export failed: {e}")
            raise ExportError(f"Topography export failed: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected system error during topography export")
            raise ExportError(f"Critical error exporting topography: {e}") from e

    def _export_geology(
        self,
        folder: Path,
        data: list[Any] | None,
        crs: Any,
        csv_exporter: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export geological data."""
        if not data:
            return
        from sec_interp.exporters import GeologyVectorExporter

        logger.info("✓ Saving geological profile...")
        try:
            rows = [(p[0], p[1], s.unit_name) for s in data for p in s.points]
            csv_path, csv_layer = self._get_export_path(folder, "geol_profile", settings, ".csv")
            csv_ok = csv_exporter.export(
                csv_path,
                {"headers": ["dist", "elev", "geology"], "rows": rows},
                layer_name=csv_layer,
            )
            if csv_ok:
                msg.append(f"  - {csv_path.relative_to(folder)}")

            vec_path, vec_layer = self._get_export_path(folder, "geol_profile", settings, ext)
            vector_exporter = GeologyVectorExporter({})
            vec_ok = vector_exporter.export(
                vec_path, {"geology_data": data, "crs": crs}, layer_name=vec_layer
            )
            if vec_ok:
                msg.append(f"  - {vec_path.relative_to(folder)}")
            else:
                logger.warning(
                    f"Failed to write vector geology to {vec_path} (likely no intersections)"
                )

        except (OSError, ValueError, TypeError, DataMissingError) as e:
            logger.exception(f"Geology export failed: {e}")
            raise ExportError(f"Geology export failed: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected system error during geology export")
            raise ExportError(f"Critical error exporting geology: {e}") from e

    def _export_structures(
        self,
        folder: Path,
        data: list[Any] | None,
        raster_layer: Any | None,
        crs: Any,
        csv_exporter: Any,
        msg: list[str],
        options: dict[str, Any],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export structural data."""
        if not data:
            return
        from sec_interp.exporters import StructureVectorExporter

        logger.info("✓ Saving structural profile...")
        try:
            rows = [(s.distance, s.apparent_dip) for s in data]
            csv_path, csv_layer = self._get_export_path(
                folder, "structural_profile", settings, ".csv"
            )
            csv_ok = csv_exporter.export(
                csv_path,
                {"headers": ["dist", "apparent_dip"], "rows": rows},
                layer_name=csv_layer,
            )
            if csv_ok:
                msg.append(f"  - {csv_path.relative_to(folder)}")

            raster_res = 1.0
            if raster_layer and raster_layer.isValid():
                raster_res = raster_layer.rasterUnitsPerPixelX()

            vec_path, vec_layer = self._get_export_path(
                folder, "structural_measurements", settings, ext
            )
            vector_exporter = StructureVectorExporter({})
            vec_ok = vector_exporter.export(
                vec_path,
                {
                    "structural_data": data,
                    "crs": crs,
                    "dip_scale_factor": options.get("dip_scale", 4),
                    "raster_res": raster_res,
                },
                layer_name=vec_layer,
            )
            if vec_ok:
                msg.append(f"  - {vec_path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write vector structures to {vec_path}")

        except (OSError, ValueError, TypeError, DataMissingError) as e:
            logger.exception(f"Structure export failed: {e}")
            raise ExportError(f"Structure export failed: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected system error during structure export")
            raise ExportError(f"Critical error exporting structures: {e}") from e

    def _export_drillholes(
        self,
        folder: Path,
        data: list[Any] | None,
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export drillhole data (2D)."""
        if not data:
            return
        from sec_interp.exporters import (
            DrillholeIntervalVectorExporter,
            DrillholeTraceVectorExporter,
        )

        logger.info("✓ Saving drillhole data...")
        try:
            # 1. Standard 2D Export
            traces_path, traces_layer = self._get_export_path(
                folder, "drillhole_traces", settings, ext
            )
            traces_exporter = DrillholeTraceVectorExporter({})
            traces_ok = traces_exporter.export(
                traces_path,
                {"drillhole_data": data, "crs": crs},
                layer_name=traces_layer,
            )
            if traces_ok:
                msg.append(f"  - {traces_path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write drillhole traces to {traces_path}")

            intervals_path, intervals_layer = self._get_export_path(
                folder, "drillhole_intervals", settings, ext
            )
            intervals_exporter = DrillholeIntervalVectorExporter({})
            intervals_ok = intervals_exporter.export(
                intervals_path,
                {"drillhole_data": data, "crs": crs},
                layer_name=intervals_layer,
            )
            if intervals_ok:
                msg.append(f"  - {intervals_path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write drillhole intervals to {intervals_path}")

        except (OSError, ValueError, TypeError, DataMissingError) as e:
            logger.exception(f"Drillhole export failed: {e}")
            raise ExportError(f"Drillhole export failed: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected system error during drillhole export")
            raise ExportError(f"Critical error exporting drillholes: {e}") from e

    def _export_drillholes_3d(
        self,
        folder: Path,
        data: list[Any] | None,
        crs: Any,
        msg: list[str],
        options: dict[str, Any],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export 3D drillhole traces and intervals."""
        if not data:
            return

        from sec_interp.exporters import (
            DrillholeInterval3DExporter,
            DrillholeTrace3DExporter,
        )

        # Declarative task list: (type_flag, projection_flag, ExporterClass,
        #                          filename_base, use_projected, label)
        tasks: list[tuple[str, str, Any, str, bool, str]] = [
            (
                "drill_3d_traces",
                "drill_3d_original",
                DrillholeTrace3DExporter,
                "drillhole_traces_3d_real",
                False,
                "3D Real",
            ),
            (
                "drill_3d_traces",
                "drill_3d_projected",
                DrillholeTrace3DExporter,
                "drillhole_traces_3d_projected",
                True,
                "3D Proj",
            ),
            (
                "drill_3d_intervals",
                "drill_3d_original",
                DrillholeInterval3DExporter,
                "drillhole_intervals_3d_real",
                False,
                "3D Real",
            ),
            (
                "drill_3d_intervals",
                "drill_3d_projected",
                DrillholeInterval3DExporter,
                "drillhole_intervals_3d_projected",
                True,
                "3D Proj",
            ),
        ]

        for type_flag, proj_flag, ExporterClass, base_name, use_proj, label in tasks:
            if options.get(type_flag, False) and options.get(proj_flag, False):
                path, path_layer = self._get_export_path(folder, base_name, settings, ext)
                exporter = ExporterClass({})
                ok = exporter.export(
                    path,
                    {"drillhole_data": data, "crs": crs, "use_projected": use_proj},
                    layer_name=path_layer,
                )
                if ok:
                    msg.append(f"  - {path.relative_to(folder)} ({label})")
                else:
                    logger.warning(f"Failed to write 3D drillhole data to {path} ({label})")

    def _export_interpretations(
        self,
        folder: Path,
        data: list[Any] | None,
        line_layer: Any,
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export interpretation data."""
        if not data:
            logger.info("No interpretations provided for export.")
            return

        from sec_interp.exporters import Interpretation2DExporter

        logger.info("✓ Saving interpretation data...")
        try:
            # 2D Export (Standard) - Now supports SHP, GPKG, DXF via scu.create_vector_writer
            path, path_layer = self._get_export_path(folder, "interpretations", settings, ext)
            exporter = Interpretation2DExporter({})
            ok = exporter.export(path, {"interpretations": data, "crs": crs}, layer_name=path_layer)
            if ok:
                msg.append(f"  - {path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write 2D interpretations to {path}")

            # 3D Export (Restricted Feature)
            if self.access_control.can_export_3d():
                self._export_interpretations_3d(folder, data, line_layer, crs, msg, settings, ext)
            else:
                logger.info("3D Export features are restricted for this user.")

        except Exception as e:
            logger.exception(f"Interpretation export failed: {e}")
            raise ExportError(f"Interpretation export failed: {e!s}") from e

    def _export_interpretations_3d(
        self,
        folder: Path,
        data: list[Any],
        line_layer: Any,
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export interpretation polygons to 3D space."""
        from sec_interp.exporters import Interpretation3DExporter

        logger.info("✓ Saving 3D interpretation data...")
        # Get section line geometry
        if line_layer and line_layer.isValid():
            line_geom = next(line_layer.getFeatures()).geometry()

            path, path_layer = self._get_export_path(folder, "interpretations_3d", settings, ext)
            exporter = Interpretation3DExporter({})

            ok = exporter.export(
                str(path),
                {"interpretations": data, "section_line": line_geom, "crs": crs},
                layer_name=path_layer,
            )
            if ok:
                msg.append(f"  - {path.relative_to(folder)} (3D)")
            else:
                logger.warning(f"Failed to write 3D interpretations to {path}")
        else:
            logger.warning("Invalid section line layer, skipping 3D export.")

    def _export_axes(
        self,
        folder: Path,
        data: list[tuple],
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        """Export profile axes."""
        from sec_interp.exporters import AxesVectorExporter

        logger.info("✓ Saving profile axes...")
        try:
            path, path_layer = self._get_export_path(folder, "profile_axes", settings, ext)
            exporter = AxesVectorExporter({})
            ok = exporter.export(path, {"profile_data": data, "crs": crs}, layer_name=path_layer)
            if ok:
                msg.append(f"  - {path.relative_to(folder)}")
            else:
                logger.warning(f"Failed to write profile axes to {path}")
        except Exception as e:
            raise ExportError(f"Profile axes export failed: {e!s}") from e

    def _get_export_path(
        self, folder: Path, base_name: str, settings: Any | None, ext: str
    ) -> tuple[Path, str]:
        """Generate unified output path and logical layer name."""
        profile_name = "profile"
        ctrl = self.controller
        has_sect = ctrl and hasattr(ctrl, "settings") and hasattr(ctrl.settings, "section")

        if has_sect:
            sect = ctrl.settings.section
            if hasattr(sect, "layer_name") and sect.layer_name:
                profile_name = sect.layer_name

        profile_name = profile_name.replace("/", "_").replace("\\", "_")

        new_name = base_name
        if settings and settings.naming_pattern:
            new_name = settings.naming_pattern.format(filename=base_name, profile=profile_name)
            new_name = new_name.replace("/", "_").replace("\\", "_")

        if ext == ".gpkg":
            return folder / f"{profile_name}{ext}", new_name

        container_folder = folder / profile_name
        container_folder.mkdir(parents=True, exist_ok=True)
        return container_folder / f"{new_name}{ext}", new_name

    def get_map_settings(
        self,
        layers: list[Any],
        extent: QgsRectangle,
        size: Any | None,
        background_color: Any,
    ) -> QgsMapSettings:
        """Create and configure QgsMapSettings for canvas or image export.

        Args:
            layers: List of map layers to be rendered.
            extent: The spatial extent (bounding box) of the view.
            size: Optional output size in pixels (QSize).
            background_color: The background color for the render (QColor).

        Returns:
            A configured QgsMapSettings instance ready for rendering.

        """
        map_settings = QgsMapSettings()
        map_settings.setLayers(layers)
        map_settings.setExtent(extent)
        if size is not None:
            map_settings.setOutputSize(size)
        map_settings.setBackgroundColor(background_color)
        return map_settings
