"""Backward compatibility wrappers for ExportService private API."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ExportServiceCompatMixin:
    """Mixin providing legacy ``_export_*`` wrappers for tests."""

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
        from sec_interp.core.services.export.handlers import topography as topo_h

        topo_h.export_topography(
            folder, data, crs, csv_exporter, msg, self.controller, settings, ext
        )  # type: ignore[attr-defined]

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
        from sec_interp.core.services.export.handlers import geology as geo_h

        geo_h.export_geology(folder, data, crs, csv_exporter, msg, self.controller, settings, ext)  # type: ignore[attr-defined]

    def _export_structures(
        self,
        folder: Path,
        data: list[Any] | None,
        raster_layer: Any | None,
        crs: Any,
        csv_exporter: Any,
        msg: list[str],
        options: dict[str, Any] | None = None,
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        from sec_interp.core.services.export.handlers import structures as struct_h

        struct_h.export_structures(
            folder,
            data,
            raster_layer,
            crs,
            csv_exporter,
            msg,
            options or {},
            self.controller,  # type: ignore[attr-defined]
            settings,
            ext,
        )

    def _export_drillholes(
        self,
        folder: Path,
        data: list[Any] | None,
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        from sec_interp.core.services.export.handlers import drillholes as dh_h

        dh_h.export_drillholes(folder, data, crs, msg, self.controller, settings, ext)  # type: ignore[attr-defined]

    def _export_axes(
        self,
        folder: Path,
        data: list[tuple],
        crs: Any,
        msg: list[str],
        settings: Any | None = None,
        ext: str = ".shp",
    ) -> None:
        from sec_interp.core.services.export.handlers import axes as axes_h

        axes_h.export_axes(folder, data, crs, msg, self.controller, settings, ext)  # type: ignore[attr-defined]

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
        from sec_interp.core.services.export.handlers import interpretations as interp_h

        interp_h.export_interpretations(
            folder,
            data,
            line_layer,
            crs,
            msg,
            self.controller,
            settings,
            ext,
            self.access_control,  # type: ignore[attr-defined]
        )

    def _get_export_path(
        self, folder: Path, base_name: str, settings: Any | None, ext: str
    ) -> tuple[Path, str]:
        from sec_interp.core.services.export.path_resolver import (
            get_profile_name,
            resolve_export_path,
        )

        profile_name = get_profile_name(self.controller)  # type: ignore[attr-defined]
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        return resolve_export_path(folder, base_name, profile_name, pattern, ext)
