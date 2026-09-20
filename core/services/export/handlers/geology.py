"""Geology export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_geology(
    folder: Path,
    data: list[Any] | None,
    crs: Any,
    csv_exporter: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export geological data."""
    if not data:
        return
    from sec_interp.exporters import GeologyVectorExporter

    logger.info("✓ Saving geological profile...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        rows = [(p[0], p[1], s.unit_name) for s in data for p in s.points]

        csv_path, csv_layer = resolve_export_path(
            folder, "geol_profile", profile_name, pattern, ".csv"
        )
        csv_ok = csv_exporter.export(
            csv_path,
            {"headers": ["dist", "elev", "geology"], "rows": rows},
            layer_name=csv_layer,
        )
        if csv_ok:
            msg.append(f"  - {csv_path.relative_to(folder)}")

        vec_path, vec_layer = resolve_export_path(
            folder, "geol_profile", profile_name, pattern, ext
        )
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
