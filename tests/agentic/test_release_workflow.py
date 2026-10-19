"""Guards for the scheduled release workflow quality gates."""

import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _ROOT / ".github" / "workflows" / "scheduled-release.yml"


class TestScheduledReleaseGates(unittest.TestCase):
    """The release train must run the same gates as CI before packaging."""

    @classmethod
    def setUpClass(cls):
        cls.text = _WORKFLOW.read_text(encoding="utf-8")

    def test_runs_ruff_and_mypy(self):
        self.assertIn("uv run --frozen ruff check .", self.text)
        self.assertIn("UV_FROZEN=1 make mypy", self.text)

    def test_runs_security_and_i18n(self):
        self.assertIn("make security-scan", self.text)
        self.assertIn("i18n-check", self.text)

    def test_runs_docs_and_analyzer(self):
        self.assertIn("python3 scripts/check_docs.py", self.text)
        self.assertIn("uv run qgis-analyzer analyze . --max-cc 10", self.text)

    def test_quality_gates_precede_packaging(self):
        quality = self.text.index("Quality gates")
        package = self.text.index("Build package")
        self.assertLess(quality, package)

    def test_quality_gates_precede_docker_tests(self):
        quality = self.text.index("Quality gates")
        tests = self.text.index("Run tests (Docker")
        self.assertLess(quality, tests)


if __name__ == "__main__":
    unittest.main()
