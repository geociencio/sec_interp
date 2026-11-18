"""QGIS 3D section export handler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

DATA_KEYS = ("profile_data", "geology_data", "structural_data")


def _payload_has_data(payload: dict[str, Any]) -> bool:
    """Return whether a layer payload contains exportable data."""
    return any(payload.get(key) for key in DATA_KEYS)


def _read_section_geometry(line_layer: Any) -> Any:
    """Return the first geometry of the section line layer."""
    if not line_layer or not line_layer.isValid():
        raise DataMissingError("Invalid section line layer for 3D export")  # no-i18n
    features = line_layer.getFeatures()
    try:
        return next(features).geometry()
    except StopIteration as exc:
        raise DataMissingError("Section line layer has no features") from exc  # no-i18n


def _build_tasks(
    profile_data: list[tuple],
    geol_data: list[Any] | None,
    struct_data: list[Any] | None,
) -> list[tuple[str, str, Any, dict[str, Any]]]:
    """Build the layer tasks without importing QGIS at module load."""
    from sec_interp.exporters import (
        Geology3DExporter,
        Structure3DExporter,
        Topography3DExporter,
    )

    return [
        (
            "topography_3d",
            "topography_3d",
            Topography3DExporter({}),
            {"profile_data": profile_data},
        ),
        (
            "geology_3d",
            "geology_3d",
            Geology3DExporter({}),
            {"geology_data": geol_data},
        ),
        (
            "structures_3d",
            "structures_3d",
            Structure3DExporter({}),
            {"structural_data": struct_data},
        ),
    ]


def _export_gpkg(
    folder: Path,
    tasks: list[tuple[str, str, Any, dict[str, Any]]],
    frame: Any,
    crs: Any,
    section_id: str,
    profile_name: str,
    pattern: str | None,
    msg: list[str],
) -> None:
    """Write all 3D layers into the profile GeoPackage."""
    path, _ = resolve_export_path(folder, "section_3d", profile_name, pattern, ".gpkg")
    written = False
    for _, layer_name, exporter, payload in tasks:
        if not _payload_has_data(payload):
            continue
        data = {**payload, "frame": frame, "crs": crs, "section_id": section_id}
        if exporter.export(path, data, layer_name=layer_name):
            written = True
    if written:
        msg.append(f"  - {path.relative_to(folder)} (3D)")


def _write_layer(
    folder: Path,
    stem: str,
    layer_name: str,
    exporter: Any,
    payload: dict[str, Any],
    frame: Any,
    crs: Any,
    section_id: str,
    profile_name: str,
    pattern: str | None,
    ext: str,
    msg: list[str],
) -> bool:
    """Write one 3D layer and record it in the export summary."""
    path, path_layer = resolve_export_path(folder, stem, profile_name, pattern, ext)
    data = {**payload, "frame": frame, "crs": crs, "section_id": section_id}
    ok = exporter.export(path, data, layer_name=layer_name or path_layer)
    if ok:
        msg.append(f"  - {path.relative_to(folder)} (3D)")
    else:
        logger.warning(f"Failed to write 3D layer {layer_name} to {path}")
    return bool(ok)


def _export_separate(
    folder: Path,
    tasks: list[tuple[str, str, Any, dict[str, Any]]],
    frame: Any,
    crs: Any,
    section_id: str,
    profile_name: str,
    pattern: str | None,
    ext: str,
    msg: list[str],
) -> None:
    """Write one file per 3D layer for Shapefile/DXF output."""
    for stem, layer_name, exporter, payload in tasks:
        if not _payload_has_data(payload):
            continue
        _write_layer(
            folder,
            stem,
            layer_name,
            exporter,
            payload,
            frame,
            crs,
            section_id,
            profile_name,
            pattern,
            ext,
            msg,
        )


def export_section_3d(
    folder: Path,
    profile_data: list[tuple],
    geol_data: list[Any] | None,
    struct_data: list[Any] | None,
    line_layer: Any,
    crs: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
) -> None:
    """Export the complete section as QGIS 3D layers.

    The GeoPackage path is shared by all layers; Shapefile/DXF outputs use one
    file per layer.
    """
    if not profile_data and not geol_data and not struct_data:
        return

    from sec_interp.exporters.interpretation_3d.geometry import build_section_frame

    try:
        section_geom = _read_section_geometry(line_layer)
        crs_authid = crs.authid() if hasattr(crs, "authid") else ""
        frame = build_section_frame(section_geom, crs_authid)
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        tasks = _build_tasks(profile_data, geol_data, struct_data)

        if ext == ".gpkg":
            _export_gpkg(
                folder,
                tasks,
                frame,
                crs,
                profile_name,
                profile_name,
                pattern,
                msg,
            )
        else:
            _export_separate(
                folder,
                tasks,
                frame,
                crs,
                profile_name,
                profile_name,
                pattern,
                ext,
                msg,
            )
    except DataMissingError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during QGIS 3D section export")
        raise ExportError(f"QGIS 3D section export failed: {exc}") from exc  # no-i18n
