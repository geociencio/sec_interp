# /***************************************************************************
#  QGIS Plugin Analyzer - Test Runner
#                                  A QGIS plugin testing utility
#  Runs unit tests inside the QGIS Python Console environment.
#                               -------------------
#         begin                : 2026-01-03
#         git sha              : $Format:%H$
#         copyright            : (C) 2026 by Juan M Bernales
#         email                : juanbernales@gmail.com
#         co-developed with    : Antigravity AI
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
QGIS In-Process Test Runner
===========================

This script is designed to be run INSIDE the QGIS Python Console.
It allows you to execute the project's unit tests using the
active QGIS environment (with access to iface, qgis.core, etc.).

Usage:
    1. Open QGIS.
    2. Open Python Console (Plugins -> Python Console).
    3. Open this script in the editor.
    4. Run script (Play button).
"""

import sys
import os
import unittest
import logging
import pathlib

# --- CONFIGURATION ---
# Auto-detect project root. Handle cases where __file__ is undefined (QGIS Console/--code)
try:
    SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
    PROJECT_ROOT = SCRIPT_DIR.parent
except NameError:
    # Fallback to current working directory if run from project root
    PROJECT_ROOT = pathlib.Path(os.getcwd()).absolute()
    # Check if we are actually in the root by looking for metadata.txt
    if not (PROJECT_ROOT / "metadata.txt").exists():
        # Try one more: maybe we are in scripts/?
        if PROJECT_ROOT.name == "scripts":
            PROJECT_ROOT = PROJECT_ROOT.parent

TESTS_DIR = PROJECT_ROOT / "tests"


def setup_environment():
    """Configures sys.path to include the project parent directory.

    This allows 'sec_interp' package to be imported correctly,
    since the package is located at PROJECT_ROOT/sec_interp.
    """
    # Add parent directory to python path so 'sec_interp' can be imported
    parent_path = str(PROJECT_ROOT.parent)
    if parent_path not in sys.path:
        print(f"📦 Adding to sys.path: {parent_path}")
        sys.path.insert(0, parent_path)

    # Configure logging to show in QGIS Console
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s",
        force=True,  # Override existing handlers
    )


def run_tests():
    """Discovers and runs tests."""
    print("=" * 60)
    print("🚀 Starting Test Run in QGIS Environment")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print("=" * 60)

    setup_environment()

    # Create Test Loader
    loader = unittest.TestLoader()

    # Discover tests
    if not TESTS_DIR.exists():
        print(f"❌ Error: Test directory not found at {TESTS_DIR}")
        return

    suite = loader.discover(
        start_dir=str(TESTS_DIR / "integration"), pattern="test_*.py"
    )

    # Run Tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ SUCCESS: All tests passed!")
    else:
        print("\n❌ FAILURE: Some tests failed.")


if __name__ == "__console__":
    run_tests()
elif __name__ == "__main__":
    # Also allow running from CLI for verification
    run_tests()
