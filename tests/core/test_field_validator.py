"""Tests for field validation utilities."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import QgsVectorLayer, QgsField

from sec_interp.core.validation.field_validator import (
    validate_numeric_input,
    validate_integer_input,
    validate_angle_range,
    validate_field_exists,
    validate_field_type,
)
from sec_interp.core.domain import FieldType


class TestFieldValidator(BaseTestCase):
    """Tests for field_validator.py"""

    def test_validate_numeric_input(self):
        """Test numeric string validation."""
        # Valid
        is_valid, msg, val = validate_numeric_input("123.45")
        self.assertTrue(is_valid)
        self.assertEqual(val, 123.45)

        # Empty not allowed
        is_valid, msg, val = validate_numeric_input("", allow_empty=False)
        self.assertFalse(is_valid)

        # Empty allowed
        is_valid, msg, val = validate_numeric_input("", allow_empty=True)
        self.assertTrue(is_valid)
        self.assertIsNone(val)

        # Invalid string
        is_valid, msg, val = validate_numeric_input("abc")
        self.assertFalse(is_valid)

        # Range
        is_valid, msg, val = validate_numeric_input("50", min_val=0, max_val=100)
        self.assertTrue(is_valid)

        is_valid, msg, val = validate_numeric_input("-10", min_val=0)
        self.assertFalse(is_valid)

    def test_validate_integer_input(self):
        """Test integer string validation."""
        # Valid
        is_valid, msg, val = validate_integer_input("100")
        self.assertTrue(is_valid)
        self.assertEqual(val, 100)

        # Float in integer field
        is_valid, msg, val = validate_integer_input("123.45")
        self.assertFalse(is_valid)

        # Range
        is_valid, msg, val = validate_integer_input("200", max_val=100)
        self.assertFalse(is_valid)

    def test_validate_angle_range(self):
        """Test angle range validation."""
        is_valid, msg = validate_angle_range(45.0, "Angle")
        self.assertTrue(is_valid)

        is_valid, msg = validate_angle_range(400.0, "Angle")
        self.assertFalse(is_valid)
        self.assertIn("between 0.0 and 360.0", msg)

    def test_validate_field_exists(self):
        """Test field existence validation."""
        layer = QgsVectorLayer()
        # Mocking fields is already done in base_test.py/MockQgsMapLayer
        # But we need to ensure they exist for this test
        layer.fields().append(QgsField("id", FieldType.INT))  # FieldType.INT = 2
        layer.fields().append(
            QgsField("name", FieldType.STRING)
        )  # FieldType.STRING = 10

        is_valid, msg = validate_field_exists(layer, "id")
        self.assertTrue(is_valid)

        is_valid, msg = validate_field_exists(layer, "missing_field")
        self.assertFalse(is_valid)
        self.assertIn("not found", msg)

    def test_validate_field_type(self):
        """Test field data type validation."""
        layer = QgsVectorLayer()
        # "id" is FieldType.INT (1) in our mock
        # "id" is FieldType.INT (2) in our mock
        layer.fields().append(QgsField("id", FieldType.INT))

        is_valid, msg = validate_field_type(layer, "id", [FieldType.INT])
        self.assertTrue(is_valid)

        # Mismatch
        is_valid, msg = validate_field_type(layer, "id", [FieldType.STRING])
        self.assertFalse(is_valid)
        self.assertIn("Invalid data type", msg)

    def test_validate_field_type_not_found(self):
        """Test type validation for missing field."""
        layer = QgsVectorLayer()
        is_valid, msg = validate_field_type(layer, "unknown", [FieldType.INT])
        self.assertFalse(is_valid)
        self.assertIn("not found", msg)
