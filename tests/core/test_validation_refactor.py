import sys
from unittest.mock import MagicMock

# Mock QGIS and PyQt before importing any project modules
mock_qgis = MagicMock()
sys.modules["qgis"] = mock_qgis
sys.modules["qgis.core"] = MagicMock()
sys.modules["qgis.gui"] = MagicMock()
sys.modules["qgis.PyQt"] = MagicMock()
sys.modules["qgis.PyQt.QtCore"] = MagicMock()
sys.modules["qgis.PyQt.QtWidgets"] = MagicMock()
sys.modules["qgis.PyQt.QtGui"] = MagicMock()

import pytest
from pathlib import Path
from core.validation.field_validator import (
    validate_numeric_input,
    validate_integer_input,
    validate_angle_range,
)
from core.validation.path_validator import validate_output_path


class TestRefactoredFieldValidation:
    """Tests for field_validator module."""

    def test_numeric_input(self):
        assert validate_numeric_input("123") == (True, "", 123.0)
        assert validate_numeric_input("abc")[0] is False
        assert validate_numeric_input("150", min_val=0, max_val=100)[0] is False

    def test_integer_input(self):
        assert validate_integer_input("123") == (True, "", 123)
        assert validate_integer_input("12.5")[0] is False

    def test_angle_range(self):
        assert validate_angle_range(45, "Dip") == (True, "")
        assert validate_angle_range(400, "Dip")[0] is False


class TestRefactoredPathValidation:
    """Tests for path_validator module."""

    def test_valid_path(self, tmp_path):
        is_valid, _, path = validate_output_path(str(tmp_path))
        assert is_valid
        assert path == tmp_path
