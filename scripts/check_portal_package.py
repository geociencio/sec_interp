#!/usr/bin/env python3
"""Validate a plugin ZIP against the plugins.qgis.org hard requirements.

The QGIS plugin repository is stricter than ``qgis-manage package --repo-check``:
it also checks the ZIP root layout, required metadata, LICENSE, size, prohibited
binaries/dev files and file permissions. This script mirrors those checks so a
release cannot be uploaded with an avoidable packaging error.

Usage:
    uv run python scripts/check_portal_package.py [dist/sec_interp.X.Y.Z.zip]
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

MAX_SIZE_BYTES = 25 * 1024 * 1024
PNG_HEADER_BYTES = 24
QGIS4_MAJOR = 4.0
ICON_MIN_PX = 32
STANDARD_MODES = frozenset({0o644, 0o755})
PROHIBITED_SUFFIXES = (".so", ".dll", ".exe", ".dylib", ".pyd", ".pyc", ".pyo")
DEV_DIRS = {
    ".git",
    ".agent",
    ".agent-state",
    ".github",
    ".venv",
    "venv",
    "build",
    "dist",
    "docs",
    "scripts",
    "tests",
    "test",
    "__pycache__",
}
REQUIRED_METADATA = (
    "name",
    "qgisMinimumVersion",
    "description",
    "about",
    "version",
    "author",
    "email",
    "repository",
)
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
_QGIS_VERSION_RE = re.compile(r"^\d+\.\d+$")
_ROOT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_ZIP_NAME_RE = re.compile(r"sec_interp\.(\d+\.\d+\.\d+)\.zip")


@dataclass
class Report:
    """Collected errors and warnings for one package."""

    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return True when no blocking error was found."""
        return not self.errors

    def error(self, message: str) -> None:
        """Record a blocking error."""
        self.errors.append(message)

    def warn(self, message: str) -> None:
        """Record a non-blocking warning."""
        self.warnings.append(message)


def parse_metadata(text: str) -> dict[str, str]:
    """Parse the flat ``key=value`` fields of a metadata.txt file."""
    data: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        raw_key = key.strip()
        data[raw_key] = value.strip()
        data.setdefault(raw_key.lower(), value.strip())
    return data


def _png_size(data: bytes) -> tuple[int, int] | None:
    """Return (width, height) for a PNG payload, or None."""
    if len(data) < PNG_HEADER_BYTES or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    try:
        width, height = struct.unpack(">II", data[16:PNG_HEADER_BYTES])
    except struct.error:
        return None
    return width, height


def _read_member(path: Path, name: str) -> bytes:
    """Read a member as bytes, returning b'' if missing."""
    try:
        with zipfile.ZipFile(path) as zf:
            return zf.read(name)
    except (KeyError, zipfile.BadZipFile):
        return b""


def _check_size(report: Report, path: Path, max_size_bytes: int) -> None:
    size = path.stat().st_size
    if size > max_size_bytes:
        report.error(
            f"ZIP is {size / 1024 / 1024:.1f} MB; plugins.qgis.org allows "
            f"{max_size_bytes / 1024 / 1024:.0f} MB"
        )


def _check_layout(names: list[str], report: Report) -> str | None:
    roots = {name.split("/", 1)[0] for name in names if "/" in name}
    if any("/" not in name for name in names):
        report.error("Files at the ZIP root; the plugin must live in its own folder")
    if len(roots) != 1:
        report.error(f"Expected one plugin folder, found {sorted(roots) or 'none'}")
        return None
    root = roots.pop()
    if not _ROOT_RE.fullmatch(root):
        report.error(
            f"Invalid plugin folder '{root}': use ASCII letters/digits/_/- "
            "and do not start with a digit"
        )
    return root


def _load_metadata(path: Path, root: str, report: Report) -> dict[str, str]:
    metadata_bytes = _read_member(path, f"{root}/metadata.txt")
    if not metadata_bytes:
        report.error("metadata.txt is missing")
        return {}
    try:
        return parse_metadata(metadata_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        report.error("metadata.txt is not valid UTF-8")
        return {}


def _check_metadata(report: Report, path: Path, metadata: dict[str, str]) -> None:
    for field_name in REQUIRED_METADATA:
        if not metadata.get(field_name):
            report.error(f"metadata.txt is missing required field '{field_name}'")

    version = metadata.get("version", "")
    if version and not _VERSION_RE.fullmatch(version):
        report.error(f"version '{version}' is not numeric X.Y.Z")
    match = _ZIP_NAME_RE.fullmatch(path.name)
    if match and version and match.group(1) != version:
        report.error(f"ZIP filename version {match.group(1)} does not match metadata {version}")

    minimum = metadata.get("qgisMinimumVersion", "")
    if minimum and not _QGIS_VERSION_RE.fullmatch(minimum):
        report.error(f"qgisMinimumVersion '{minimum}' is not X.Y")
    maximum = metadata.get("qgisMaximumVersion", "")
    if maximum and not _QGIS_VERSION_RE.fullmatch(maximum):
        report.error(f"qgisMaximumVersion '{maximum}' is not X.Y")
    elif maximum and float(maximum) < QGIS4_MAJOR:
        report.warn("qgisMaximumVersion < 4.0: not listed as QGIS 4 Ready")
    if "supportsqt6" in metadata:
        report.warn("supportsQt6 is deprecated; use qgisMaximumVersion >= 4.0")


def _check_required_files(path: Path, root: str, report: Report) -> None:
    if not _read_member(path, f"{root}/__init__.py"):
        report.error("__init__.py is missing")
    license_bytes = _read_member(path, f"{root}/LICENSE")
    if not license_bytes:
        report.error("LICENSE is missing (must be named exactly 'LICENSE')")
    elif not license_bytes.strip():
        report.error("LICENSE is empty")


def _check_entries(names: list[str], root: str, report: Report) -> None:
    if not any(name.startswith(f"{root}/README") for name in names):
        report.warn("README is not included in the package")
    for name in names:
        if name.lower().endswith(PROHIBITED_SUFFIXES):
            report.error(f"Prohibited binary in package: {name}")
        for part in name.split("/")[1:]:
            if part in DEV_DIRS:
                report.error(f"Development directory in package: {name}")
            if part.startswith("."):
                report.warn(f"Hidden file in package: {name}")


def _check_icon(metadata: dict[str, str], root: str, path: Path, report: Report) -> None:
    icon = metadata.get("icon", "")
    if not icon:
        return
    icon_bytes = _read_member(path, f"{root}/{icon}")
    if not icon_bytes:
        report.warn(f"metadata icon '{icon}' is not in the package")
        return
    size_px = _png_size(icon_bytes)
    if size_px and (size_px[0] < ICON_MIN_PX or size_px[1] < ICON_MIN_PX):
        report.warn(f"icon '{icon}' is only {size_px[0]}x{size_px[1]} px")


def _check_permissions(path: Path, report: Report) -> None:
    modes: Counter[int] = Counter()
    examples: dict[int, list[str]] = {}
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            mode = (info.external_attr >> 16) & 0o777
            if mode and mode not in STANDARD_MODES:
                modes[mode] += 1
                examples.setdefault(mode, []).append(info.filename)
    for mode, count in sorted(modes.items()):
        sample = ", ".join(examples[mode][:3])
        report.warn(
            f"{count} file(s) with permissions {mode:o} (e.g. {sample}); "
            "normalize to 0644/0755 before uploading"
        )


def check_zip(path: Path, max_size_bytes: int = MAX_SIZE_BYTES) -> Report:
    """Run the portal hard-requirement checks on ``path``."""
    report = Report(path=path)
    if not path.is_file():
        report.error(f"ZIP not found: {path}")
        return report
    _check_size(report, path, max_size_bytes)
    try:
        with zipfile.ZipFile(path) as zf:
            names = [name for name in zf.namelist() if not name.endswith("/")]
    except zipfile.BadZipFile:
        report.error("Not a valid ZIP archive")
        return report

    root = _check_layout(names, report)
    if root is None:
        return report
    metadata = _load_metadata(path, root, report)
    _check_metadata(report, path, metadata)
    _check_required_files(path, root, report)
    _check_entries(names, root, report)
    _check_icon(metadata, root, path, report)
    _check_permissions(path, report)
    return report


def _default_zip() -> Path | None:
    """Return the newest dist/sec_interp.*.zip, if any."""
    candidates = sorted(
        Path("dist").glob("sec_interp.*.zip"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def main(argv: list[str] | None = None) -> int:
    """Run the checker and print a PASS/FAIL summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", nargs="?", help="ZIP to check (default: newest dist)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--max-size-mb", type=float, default=25, help="Override the portal size limit"
    )
    args = parser.parse_args(argv)

    path = Path(args.zip_path) if args.zip_path else _default_zip()
    if path is None:
        print("❌ No dist/sec_interp.*.zip found", file=sys.stderr)
        return 1

    report = check_zip(path, int(args.max_size_mb * 1024 * 1024))
    if args.json:
        print(
            json.dumps(
                {
                    "path": str(report.path),
                    "ok": report.ok,
                    "errors": report.errors,
                    "warnings": report.warnings,
                },
                indent=2,
            )
        )
    else:
        print(f"📦 Portal package check: {report.path}")
        for warning in report.warnings:
            print(f"  ⚠️  {warning}")
        for error in report.errors:
            print(f"  ❌ {error}")
        print("✅ PASS" if report.ok else "❌ FAIL")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
