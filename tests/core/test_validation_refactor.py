from tests.base_test import BaseTestCase
from unittest.mock import MagicMock

# qgis imports handled by BaseTestCase

from sec_interp.core.validation.field_validator import (
    validate_numeric_input,
    validate_integer_input,
    validate_angle_range,
)
from sec_interp.core.validation.path_validator import validate_output_path


class TestRefactoredFieldValidation(BaseTestCase):
    """Tests for field_validator module."""

    def test_numeric_input(self):
        self.assertEqual(validate_numeric_input("123"), (True, "", 123.0))
        self.assertFalse(validate_numeric_input("abc")[0])
        self.assertFalse(validate_numeric_input("150", min_val=0, max_val=100)[0])

    def test_integer_input(self):
        self.assertEqual(validate_integer_input("123"), (True, "", 123))
        self.assertFalse(validate_integer_input("12.5")[0])

    def test_angle_range(self):
        self.assertEqual(validate_angle_range(45, "Dip"), (True, ""))
        self.assertFalse(validate_angle_range(400, "Dip")[0])


class TestRefactoredPathValidation(BaseTestCase):
    """Tests for path_validator module."""

    def test_valid_path(self):
        # use self.output_dir from BaseTestCase
        is_valid, _, path = validate_output_path(str(self.output_dir))
        self.assertTrue(is_valid)
        self.assertEqual(path, self.output_dir)
