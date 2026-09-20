"""Interpretations export handler (2D + 3D)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_interpretations(
    folder: Path,
    data: list[Any] | None,
    line_layer: Any,
    crs: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
    access_control: Any | None,
) -> None:
    """Export interpretation data (2D mandatory, 3D gated)."""
    if not data:
        logger.info("No interpretations provided for export.")
        return

    from sec_interp.exporters import Interpretation2DExporter

    logger.info("✓ Saving interpretation data...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        path, path_layer = resolve_export_path(
            folder, "interpretations", profile_name, pattern, ext
        )
        exporter = Interpretation2DExporter({})
        ok = exporter.export(path, {"interpretations": data, "crs": crs}, layer_name=path_layer)
        if ok:
            msg.append(f"  - {path.relative_to(folder)}")
        else:
            logger.warning(f"Failed to write 2D interpretations to {path}")

        if access_control and access_control.can_export_3d():
            _export_interpretations_3d(
                folder, data, line_layer, crs, msg, controller, settings, ext
            )
        else:
            logger.info("3D Export features are restricted for this user.")

    except Exception as e:
        logger.exception(f"Interpretation export failed: {e}")
        raise ExportError(f"Interpretation export failed: {e!s}") from e


def _export_interpretations_3d(
    folder: Path,
    data: list[Any],
    line_layer: Any,
    crs: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export interpretation polygons to 3D space."""
    from sec_interp.exporters import Interpretation3DExporter

    logger.info("✓ Saving 3D interpretation data...")
    if line_layer and line_layer.isValid():
        line_geom = next(line_layer.getFeatures()).geometry()

        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        path, path_layer = resolve_export_path(
            folder, "interpretations_3d", profile_name, pattern, ext
        )
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
