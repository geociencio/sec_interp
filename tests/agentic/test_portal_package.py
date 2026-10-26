"""Tests for the QGIS portal package checker."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from tests.base_test import BaseTestCase

_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "check_portal_package", _ROOT / "scripts" / "check_portal_package.py"
)
assert _SPEC and _SPEC.loader
portal = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = portal
_SPEC.loader.exec_module(portal)

_METADATA = """[general]
name=Sec Interp
qgisMinimumVersion=3.28
qgisMaximumVersion=4.99
description=Data extraction for geological interpretation
about=Data extraction from DEM, geological outcrops and structural points.
version=3.12.0
author=Juan M Bernales
email=juanbernales@gmail.com
repository=https://github.com/geociencio/sec_interp
homepage=https://geociencio.github.io/sec_interp_docs/
icon=icon.png
"""


class TestPortalPackage(BaseTestCase):
    """The checker must mirror plugins.qgis.org hard requirements."""

    def setUp(self) -> None:
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def _build(
        self,
        files: dict[str, bytes] | None = None,
        metadata: str = _METADATA,
        mode: int = 0o644,
        filename: str = "sec_interp.3.12.0.zip",
        root: str = "sec_interp",
    ) -> Path:
        package = {
            "metadata.txt": metadata.encode(),
            "__init__.py": b"def classFactory(iface):\n    return None\n",
            "LICENSE": b"GPL-2.0-or-later\n",
            "README.md": b"# SecInterp\n",
            "icon.png": b"\x89PNG\r\n\x1a\n" + b"\x00" * 16,
        }
        package.update(files or {})
        path = self.tmp / filename
        with zipfile.ZipFile(path, "w") as zf:
            for name, data in package.items():
                info = zipfile.ZipInfo(f"{root}/{name}")
                info.external_attr = (mode & 0o777) << 16
                zf.writestr(info, data)
        return path

    def test_valid_package_passes(self) -> None:
        report = portal.check_zip(self._build())
        self.assertTrue(report.ok, report.errors)

    def test_missing_license_is_error(self) -> None:
        path = self._build({"LICENSE": b""})
        report = portal.check_zip(path)
        self.assertFalse(report.ok)
        self.assertTrue(any("LICENSE" in error for error in report.errors))

    def test_prohibited_binary_is_error(self) -> None:
        report = portal.check_zip(self._build({"gui/bad.pyc": b"x"}))
        self.assertFalse(report.ok)
        self.assertTrue(any("Prohibited binary" in error for error in report.errors))

    def test_dev_directory_is_error(self) -> None:
        report = portal.check_zip(self._build({"tests/test_x.py": b"pass\n"}))
        self.assertFalse(report.ok)
        self.assertTrue(any("Development directory" in error for error in report.errors))

    def test_missing_repository_is_error(self) -> None:
        metadata = _METADATA.replace("repository=https://github.com/geociencio/sec_interp\n", "")
        report = portal.check_zip(self._build(metadata=metadata))
        self.assertFalse(report.ok)
        self.assertTrue(any("repository" in error for error in report.errors), report.errors)

    def test_restrictive_mode_warns(self) -> None:
        report = portal.check_zip(self._build(mode=0o600))
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(any("permissions" in warning for warning in report.warnings))

    def test_filename_version_mismatch_is_error(self) -> None:
        report = portal.check_zip(self._build(filename="sec_interp.3.12.1.zip"))
        self.assertFalse(report.ok)
        self.assertTrue(any("does not match metadata" in error for error in report.errors))

    def test_qgis3_only_range_warns(self) -> None:
        metadata = _METADATA.replace("qgisMaximumVersion=4.99", "qgisMaximumVersion=3.99")
        report = portal.check_zip(self._build(metadata=metadata))
        self.assertTrue(report.ok, report.errors)
        self.assertTrue(any("QGIS 4 Ready" in warning for warning in report.warnings))

    def test_wrong_root_folder_is_error(self) -> None:
        report = portal.check_zip(self._build(root="9bad"))
        self.assertFalse(report.ok)
        self.assertTrue(any("Invalid plugin folder" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
