#!/usr/bin/env python3
"""
QGIS In-Process Test Runner (Gen 8).

Runs integration or benchmark tests inside the QGIS Python Console / headless
QGIS. Merges the former `run_tests_in_qgis.py` (integration) and
`run_benchmarks.py` (benchmarks) into a single suite-parameterized runner.

Usage:
    qgis --nologo --code scripts/run_in_qgis.py --suite integration
    qgis --nologo --code scripts/run_in_qgis.py --suite benchmarks

Or from the QGIS Python Console, call `run_suite("integration")`.
"""

import logging
import os
import pathlib
import sys

DEFAULT_SUITE = "integration"


def _resolve_suite(argv: list[str]) -> str:
    """Resolve the target test suite from CLI arguments."""
    if "--suite" in argv:
        try:
            return argv[argv.index("--suite") + 1]
        except IndexError:
            pass
    for arg in argv:
        if arg in ("integration", "benchmarks"):
            return arg
    return DEFAULT_SUITE


try:
    SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
    PROJECT_ROOT = SCRIPT_DIR.parent
except NameError:
    PROJECT_ROOT = pathlib.Path(os.getcwd()).absolute()
    if not (PROJECT_ROOT / "metadata.txt").exists():
        if PROJECT_ROOT.name == "scripts":
            PROJECT_ROOT = PROJECT_ROOT.parent

TESTS_DIR = PROJECT_ROOT / "tests"


def setup_environment() -> None:
    """Configure sys.path and logging for the QGIS in-process run."""
    parent_path = str(PROJECT_ROOT.parent)
    if parent_path not in sys.path:
        print(f"📦 Adding to sys.path: {parent_path}")
        sys.path.insert(0, parent_path)
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s",
        force=True,
    )


def run_suite(suite: str) -> None:
    """Discover and run all tests in `tests/<suite>`."""
    import unittest

    print("=" * 60)
    print(f"🚀 Starting {suite} test run in QGIS Environment")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print("=" * 60)

    setup_environment()

    suite_dir = TESTS_DIR / suite
    if not suite_dir.exists():
        print(f"❌ Error: Test directory not found at {suite_dir}")
        return

    loader = unittest.TestLoader()
    suite_obj = loader.discover(start_dir=str(suite_dir), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite_obj)

    if result.wasSuccessful():
        print("\n✅ SUCCESS: All tests passed!")
    else:
        print("\n❌ FAILURE: Some tests failed.")


if __name__ == "__console__":
    run_suite(_resolve_suite(sys.argv))
elif __name__ == "__main__":
    run_suite(_resolve_suite(sys.argv))
    # Explicitly exit QGIS when running headless (adopted from run_benchmarks.py).
    try:
        from qgis.core import QgsApplication

        QgsApplication.exitQgis()
    except Exception:  # noqa: BLE001
        pass
