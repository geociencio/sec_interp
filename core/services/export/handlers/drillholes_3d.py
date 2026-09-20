"""Drillhole 3D export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_drillholes_3d(
    folder: Path,
    data: list[Any] | None,
    crs: Any,
    msg: list[str],
    options: dict[str, Any],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export 3D drillhole traces and intervals."""
    if not data:
        return

    from sec_interp.exporters import (
        DrillholeInterval3DExporter,
        DrillholeTrace3DExporter,
    )

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

    profile_name = get_profile_name(controller)
    pattern = getattr(settings, "naming_pattern", None) if settings else None
    for type_flag, proj_flag, ExporterClass, base_name, use_proj, label in tasks:
        if options.get(type_flag, False) and options.get(proj_flag, False):
            path, path_layer = resolve_export_path(folder, base_name, profile_name, pattern, ext)
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
