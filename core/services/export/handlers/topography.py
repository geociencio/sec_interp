"""Topography export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.core.utils.sampling import smooth_profile_by_distance
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_topography(
    folder: Path,
    data: list[tuple],
    crs: Any,
    csv_exporter: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
    options: dict[str, Any] | None = None,
) -> None:
    """Export topographic data (CSV + vector)."""
    from sec_interp.exporters import ProfileLineVectorExporter

    logger.info("✓ Saving topographic profile...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None

        csv_path, csv_layer = resolve_export_path(
            folder, "topo_profile", profile_name, pattern, ".csv"
        )
        csv_ok = csv_exporter.export(
            csv_path,
            {"headers": ["dist", "elev"], "rows": data},
            layer_name=csv_layer,
        )
        if csv_ok:
            msg.append(f"  - {csv_path.relative_to(folder)}")
        else:
            logger.warning(f"Failed to write CSV topography to {csv_path}")

        vec_path, vec_layer = resolve_export_path(
            folder, "profile_line", profile_name, pattern, ext
        )
        vector_exporter = ProfileLineVectorExporter({})
        vec_ok = vector_exporter.export(
            vec_path, {"profile_data": data, "crs": crs}, layer_name=vec_layer
        )
        if vec_ok:
            msg.append(f"  - {vec_path.relative_to(folder)}")
        else:
            logger.warning(f"Failed to write vector topography to {vec_path}")

        opts = options or {}
        window = float(opts.get("smooth_window", 0) or 0)
        if opts.get("smooth") and window > 0 and data:
            smoothed = smooth_profile_by_distance(data, window)
            sm_csv_path, sm_csv_layer = resolve_export_path(
                folder, "topo_profile_smoothed", profile_name, pattern, ".csv"
            )
            if csv_exporter.export(
                sm_csv_path,
                {"headers": ["dist", "elev"], "rows": smoothed},
                layer_name=sm_csv_layer,
            ):
                msg.append(f"  - {sm_csv_path.relative_to(folder)}")

            sm_vec_path, sm_vec_layer = resolve_export_path(
                folder, "profile_line_smoothed", profile_name, pattern, ext
            )
            if vector_exporter.export(
                sm_vec_path,
                {"profile_data": smoothed, "crs": crs},
                layer_name=sm_vec_layer,
            ):
                msg.append(f"  - {sm_vec_path.relative_to(folder)}")

    except (OSError, ValueError, TypeError, DataMissingError) as e:
        logger.exception(f"Topography export failed: {e}")
        raise ExportError(f"Topography export failed: {e!s}") from e
    except Exception as e:
        logger.exception("Unexpected system error during topography export")
        raise ExportError(f"Critical error exporting topography: {e}") from e
