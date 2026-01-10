# /***************************************************************************
#  QGIS Plugin Analyzer - Benchmark Runner
#  Runs benchmark tests inside the QGIS Python Console environment.
#  ***************************************************************************/

"""
QGIS In-Process Benchmark Runner
================================

Usage:
    qgis --nologo --code scripts/run_benchmarks.py
"""

import sys
import os
import unittest
import logging
import pathlib

# --- CONFIGURATION ---
try:
    SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
    PROJECT_ROOT = SCRIPT_DIR.parent
except NameError:
    PROJECT_ROOT = pathlib.Path(os.getcwd()).absolute()
    if not (PROJECT_ROOT / "metadata.txt").exists():
        if PROJECT_ROOT.name == "scripts":
            PROJECT_ROOT = PROJECT_ROOT.parent

TESTS_DIR = PROJECT_ROOT / "tests"


def setup_environment():
    """Configures sys.path."""
    parent_path = str(PROJECT_ROOT.parent)
    if parent_path not in sys.path:
        print(f"📦 Adding to sys.path: {parent_path}")
        sys.path.insert(0, parent_path)

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(message)s",
        force=True,
    )


def run_benchmarks():
    """Discovers and runs benchmark tests."""
    print("=" * 60)
    print(f"⏱️  Starting Benchmark Run in QGIS Environment")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print("=" * 60)

    setup_environment()

    loader = unittest.TestLoader()

    if not TESTS_DIR.exists():
        print(f"❌ Error: Test directory not found at {TESTS_DIR}")
        return

    # Discover tests in tests/benchmarks
    suite = loader.discover(
        start_dir=str(TESTS_DIR / "benchmarks"), pattern="test_*.py"
    )

    # Run Tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ SUCCESS: All benchmarks passed!")
        # We exit with 0 to signal success to CI
        # sys.exit(0) # Careful with sys.exit inside QGIS if running interactively
    else:
        print("\n❌ FAILURE: Some benchmarks failed.")
        # sys.exit(1)


if __name__ == "__console__":
    run_benchmarks()
elif __name__ == "__main__":
    run_benchmarks()
    # Explicitly exit QGIS if running headless
    from qgis.core import QgsApplication

    QgsApplication.exitQgis()
