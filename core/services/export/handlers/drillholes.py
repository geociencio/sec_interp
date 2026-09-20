"""Drillhole 2D export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_drillholes(
    folder: Path,
    data: list[Any] | None,
    crs: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export drillhole data (2D traces + intervals)."""
    if not data:
        return
    from sec_interp.exporters import (
        DrillholeIntervalVectorExporter,
        DrillholeTraceVectorExporter,
    )

    logger.info("✓ Saving drillhole data...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None

        traces_path, traces_layer = resolve_export_path(
            folder, "drillhole_traces", profile_name, pattern, ext
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

        intervals_path, intervals_layer = resolve_export_path(
            folder, "drillhole_intervals", profile_name, pattern, ext
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
