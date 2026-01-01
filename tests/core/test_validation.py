# -*- coding: utf-8 -*-
"""
Tests for core/validation.py
"""

from tests.base_test import BaseTestCase
from sec_interp.core import validation as vu
from pathlib import Path


class TestNumericValidation(BaseTestCase):
    """Tests for numeric input validation."""

    def test_validate_numeric_input_valid(self):
        """Test valid numeric inputs."""
        self.assertEqual(vu.validate_numeric_input("123"), (True, "", 123.0))
        self.assertEqual(vu.validate_numeric_input("45.5"), (True, "", 45.5))
        self.assertEqual(vu.validate_numeric_input("-10"), (True, "", -10.0))

    def test_validate_numeric_input_invalid(self):
        """Test invalid numeric inputs."""
        is_valid, error, _ = vu.validate_numeric_input("abc")
        self.assertFalse(is_valid)
        self.assertIn("valid number", error.lower())

        is_valid, error, _ = vu.validate_numeric_input("")
        self.assertFalse(is_valid)

    def test_validate_numeric_input_with_range(self):
        """Test numeric validation with range."""
        is_valid, error, value = vu.validate_numeric_input("50", min_val=0, max_val=100)
        self.assertTrue(is_valid)
        self.assertEqual(value, 50.0)

        is_valid, error, _ = vu.validate_numeric_input("150", min_val=0, max_val=100)
        self.assertFalse(is_valid)
        self.assertIn("at most", error.lower())


class TestIntegerValidation(BaseTestCase):
    """Tests for integer input validation."""

    def test_validate_integer_input_valid(self):
        """Test valid integer inputs."""
        self.assertEqual(vu.validate_integer_input("123"), (True, "", 123))
        self.assertEqual(vu.validate_integer_input("0"), (True, "", 0))

    def test_validate_integer_input_invalid(self):
        """Test invalid integer inputs."""
        is_valid, error, _ = vu.validate_integer_input("45.5")
        self.assertFalse(is_valid)

        is_valid, error, _ = vu.validate_integer_input("abc")
        self.assertFalse(is_valid)


class TestAngleValidation(BaseTestCase):
    """Tests for angle range validation."""

    def test_validate_angle_range_valid(self):
        """Test valid angle values."""
        self.assertEqual(vu.validate_angle_range(0.0, "Dip"), (True, ""))
        self.assertEqual(vu.validate_angle_range(180.0, "Dip"), (True, ""))
        self.assertEqual(vu.validate_angle_range(360.0, "Dip"), (True, ""))

    def test_validate_angle_range_invalid(self):
        """Test invalid angle values."""
        is_valid, error = vu.validate_angle_range(-10.0, "Dip")
        self.assertFalse(is_valid)

        is_valid, error = vu.validate_angle_range(400.0, "Dip")
        self.assertFalse(is_valid)


class TestOutputPathValidation(BaseTestCase):
    """Tests for output path validation."""

    def test_validate_output_path_valid(self):
        """Test valid output path."""
        # Use simple temp dir from tempfile logic or self.output_dir
        # self.output_dir is a Path object from BaseTestCase.setUp
        is_valid, error, path = vu.validate_output_path(str(self.output_dir))
        self.assertTrue(is_valid)
        self.assertEqual(path, self.output_dir)

    def test_validate_output_path_nonexistent(self):
        """Test non-existent path."""
        nonexistent = self.output_dir / "nonexistent"
        is_valid, error, _ = vu.validate_output_path(str(nonexistent))
        self.assertFalse(is_valid)
        self.assertTrue("not exist" in error.lower() or "does not exist" in error.lower())

    def test_validate_output_path_not_directory(self):
        """Test path that is a file, not directory."""
        file_path = self.output_dir / "test.txt"
        file_path.write_text("test")
        is_valid, error, _ = vu.validate_output_path(str(file_path))
        self.assertFalse(is_valid)
        self.assertIn("directory", error.lower())
