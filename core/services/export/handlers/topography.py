"""Topography export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.core.utils.sampling import smooth_profile_by_distance
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def _record_written(msg: list[str], path: Path, folder: Path) -> None:
    """Append a written-file line to the export summary."""
    msg.append(f"  - {path.relative_to(folder)}")


def _export_profile_pair(
    folder: Path,
    profile_name: str | None,
    pattern: str | None,
    stems: tuple[str, str],
    payloads: tuple[dict[str, Any], dict[str, Any]],
    csv_exporter: Any,
    vector_exporter: Any,
    msg: list[str],
    ext: str,
) -> None:
    """Export one CSV/vector pair and record the written files."""
    csv_stem, vec_stem = stems
    csv_payload, vec_payload = payloads

    csv_path, csv_layer = resolve_export_path(folder, csv_stem, profile_name, pattern, ".csv")
    if csv_exporter.export(csv_path, csv_payload, layer_name=csv_layer):
        _record_written(msg, csv_path, folder)
    else:
        logger.warning(f"Failed to write CSV topography to {csv_path}")

    vec_path, vec_layer = resolve_export_path(folder, vec_stem, profile_name, pattern, ext)
    if vector_exporter.export(vec_path, vec_payload, layer_name=vec_layer):
        _record_written(msg, vec_path, folder)
    else:
        logger.warning(f"Failed to write vector topography to {vec_path}")


def _smoothed_topography(data: list[tuple], options: dict[str, Any]) -> list[tuple] | None:
    """Return a distance-smoothed profile when smoothing is requested."""
    window = float(options.get("smooth_window", 0) or 0)
    if options.get("smooth") and window > 0 and data:
        return smooth_profile_by_distance(data, window)
    return None


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
        vector_exporter = ProfileLineVectorExporter({})

        _export_profile_pair(
            folder,
            profile_name,
            pattern,
            ("topo_profile", "profile_line"),
            (
                {"headers": ["dist", "elev"], "rows": data},
                {"profile_data": data, "crs": crs},
            ),
            csv_exporter,
            vector_exporter,
            msg,
            ext,
        )

        smoothed = _smoothed_topography(data, options or {})
        if smoothed:
            _export_profile_pair(
                folder,
                profile_name,
                pattern,
                ("topo_profile_smoothed", "profile_line_smoothed"),
                (
                    {"headers": ["dist", "elev"], "rows": smoothed},
                    {"profile_data": smoothed, "crs": crs},
                ),
                csv_exporter,
                vector_exporter,
                msg,
                ext,
            )

    except (OSError, ValueError, TypeError, DataMissingError) as e:
        logger.exception(f"Topography export failed: {e}")
        raise ExportError(f"Topography export failed: {e!s}") from e  # no-i18n
    except Exception as e:
        logger.exception("Unexpected system error during topography export")
        raise ExportError(f"Critical error exporting topography: {e}") from e  # no-i18n
