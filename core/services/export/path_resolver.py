"""Path resolution for export operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def get_profile_name(controller: Any | None) -> str:
    """Return sanitized profile name derived from the section layer.

    Args:
        controller: Optional controller holding ``settings.section.layer_name``.

    Returns:
        Sanitized profile name, defaults to ``"profile"``.

    """
    profile_name = "profile"
    has_sect = (
        controller and hasattr(controller, "settings") and hasattr(controller.settings, "section")
    )
    if has_sect:
        sect = controller.settings.section
        if hasattr(sect, "layer_name") and sect.layer_name:
            profile_name = sect.layer_name
    return profile_name.replace("/", "_").replace("\\", "_")


def resolve_export_path(
    folder: Path,
    base_name: str,
    profile_name: str,
    naming_pattern: str | None,
    ext: str,
) -> tuple[Path, str]:
    """Generate unified output path and logical layer name.

    Args:
        folder: Base output directory.
        base_name: Logical export name (e.g. ``"topo_profile"``).
        profile_name: Sanitized profile/section name.
        naming_pattern: Optional pattern with ``{filename}`` and ``{profile}`` placeholders.
        ext: File extension including dot (``.csv``, ``.shp``, ``.gpkg``, ``.dxf``).

    Returns:
        Tuple of (filesystem Path, logical layer name).

    """
    new_name = base_name
    if naming_pattern:
        new_name = naming_pattern.format(filename=base_name, profile=profile_name)
        new_name = new_name.replace("/", "_").replace("\\", "_")

    if ext == ".gpkg":
        return folder / f"{profile_name}{ext}", new_name

    container_folder = folder / profile_name
    container_folder.mkdir(parents=True, exist_ok=True)
    return container_folder / f"{new_name}{ext}", new_name
