"""Prove that core business modules import without a QGIS installation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.base_test import BaseTestCase

_ROOT = Path(__file__).resolve().parents[2]


class TestCorePurity(BaseTestCase):
    """Core must be importable in the plain development venv."""

    def test_core_imports_without_qgis(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(_ROOT.parent)
        code = (
            "import sec_interp.core.controller as c; "
            "import sec_interp.core.services.export.orchestrator as e; "
            "print('CORE IMPORT OK', c.ProfileController.__name__, "
            "e.ExportService.__name__)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CORE IMPORT OK", result.stdout)
