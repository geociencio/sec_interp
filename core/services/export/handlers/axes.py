"""Profile axes export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def export_axes(
    folder: Path,
    data: list[tuple],
    crs: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export profile axes."""
    from sec_interp.exporters import AxesVectorExporter

    logger.info("✓ Saving profile axes...")
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        path, path_layer = resolve_export_path(folder, "profile_axes", profile_name, pattern, ext)
        exporter = AxesVectorExporter({})
        ok = exporter.export(path, {"profile_data": data, "crs": crs}, layer_name=path_layer)
        if ok:
            msg.append(f"  - {path.relative_to(folder)}")
        else:
            logger.warning(f"Failed to write profile axes to {path}")
    except Exception as e:
        raise ExportError(f"Profile axes export failed: {e!s}") from e
