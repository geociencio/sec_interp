"""Structures export handler."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def _record_written(msg: list[str], path: Path, folder: Path) -> None:
    """Append a written-file line to the export summary."""
    msg.append(f"  - {path.relative_to(folder)}")


def _resolve_raster_resolution(raster_layer: Any | None) -> float:
    """Return a finite, positive raster resolution, or 1.0 as a safe fallback."""
    if not raster_layer or not raster_layer.isValid():
        return 1.0
    candidate = raster_layer.rasterUnitsPerPixelX()
    if isinstance(candidate, int | float) and math.isfinite(candidate) and candidate > 0:
        return float(candidate)
    logger.warning("Invalid raster resolution %r; using 1.0 for dip line length.", candidate)
    return 1.0


def export_structures(
    folder: Path,
    data: list[Any] | None,
    raster_layer: Any | None,
    crs: Any,
    csv_exporter: Any,
    msg: list[str],
    options: dict[str, Any],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export structural data."""
    if not data:
        return
    from sec_interp.exporters import StructureVectorExporter

    logger.info("✓ Saving structural profile...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        rows = [(s.distance, s.apparent_dip) for s in data]

        csv_path, csv_layer = resolve_export_path(
            folder, "structural_profile", profile_name, pattern, ".csv"
        )
        if csv_exporter.export(
            csv_path,
            {"headers": ["dist", "apparent_dip"], "rows": rows},
            layer_name=csv_layer,
        ):
            _record_written(msg, csv_path, folder)

        raster_res = _resolve_raster_resolution(raster_layer)

        vec_path, vec_layer = resolve_export_path(
            folder, "structural_measurements", profile_name, pattern, ext
        )
        vector_exporter = StructureVectorExporter({})
        if vector_exporter.export(
            vec_path,
            {
                "structural_data": data,
                "crs": crs,
                "dip_scale_factor": options.get("dip_scale", 4),
                "raster_res": raster_res,
            },
            layer_name=vec_layer,
        ):
            _record_written(msg, vec_path, folder)
        else:
            logger.warning(f"Failed to write vector structures to {vec_path}")

    except (OSError, ValueError, TypeError, DataMissingError) as e:
        logger.exception(f"Structure export failed: {e}")
        raise ExportError(f"Structure export failed: {e!s}") from e  # no-i18n
    except Exception as e:
        logger.exception("Unexpected system error during structure export")
        raise ExportError(f"Critical error exporting structures: {e}") from e  # no-i18n
