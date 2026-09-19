"""Tests for field validation utilities."""

from tests.base_test import BaseTestCase

from sec_interp.core.validation.field_validator import (
    validate_numeric_input,
    validate_integer_input,
    validate_angle_range,
    validate_field_exists,
    validate_field_type,
)
from sec_interp.core.validation.layer_metadata import KIND_VECTOR, LayerMetadata
from sec_interp.core.domain import FieldType


def _make_metadata(field_names, field_types):
    return LayerMetadata(
        name="Test",
        is_valid=True,
        kind=KIND_VECTOR,
        field_names=field_names,
        field_types=field_types,
    )


class TestFieldValidator(BaseTestCase):
    """Tests for field_validator.py"""

    def test_validate_numeric_input(self):
        """Test numeric string validation."""
        is_valid, msg, val = validate_numeric_input("123.45")
        self.assertTrue(is_valid)
        self.assertEqual(val, 123.45)

        is_valid, msg, val = validate_numeric_input("", allow_empty=False)
        self.assertFalse(is_valid)

        is_valid, msg, val = validate_numeric_input("", allow_empty=True)
        self.assertTrue(is_valid)
        self.assertIsNone(val)

        is_valid, msg, val = validate_numeric_input("abc")
        self.assertFalse(is_valid)

        is_valid, msg, val = validate_numeric_input("50", min_val=0, max_val=100)
        self.assertTrue(is_valid)

        is_valid, msg, val = validate_numeric_input("-10", min_val=0)
        self.assertFalse(is_valid)

    def test_validate_integer_input(self):
        """Test integer string validation."""
        is_valid, msg, val = validate_integer_input("100")
        self.assertTrue(is_valid)
        self.assertEqual(val, 100)

        is_valid, msg, val = validate_integer_input("123.45")
        self.assertFalse(is_valid)

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
        metadata = _make_metadata(
            ["id", "name"], {"id": FieldType.INT, "name": FieldType.STRING}
        )

        is_valid, msg = validate_field_exists(metadata, "id")
        self.assertTrue(is_valid)

        is_valid, msg = validate_field_exists(metadata, "missing_field")
        self.assertFalse(is_valid)
        self.assertIn("not found", msg)

    def test_validate_field_type(self):
        """Test field data type validation."""
        metadata = _make_metadata(["id"], {"id": FieldType.INT})

        is_valid, msg = validate_field_type(metadata, "id", [FieldType.INT])
        self.assertTrue(is_valid)

        is_valid, msg = validate_field_type(metadata, "id", [FieldType.STRING])
        self.assertFalse(is_valid)
        self.assertIn("Invalid data type", msg)

    def test_validate_field_type_not_found(self):
        """Test type validation for missing field."""
        metadata = _make_metadata([], {})
        is_valid, msg = validate_field_type(metadata, "unknown", [FieldType.INT])
        self.assertFalse(is_valid)
        self.assertIn("not found", msg)
