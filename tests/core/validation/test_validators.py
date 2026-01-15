"""Unit tests for validators module."""

import unittest

from sec_interp.core.exceptions import ValidationError
from sec_interp.core.validation.validators import (
    FieldValidator,
    coerce_type,
    validate_and_clamp,
    validate_non_empty,
    validate_non_negative,
    validate_percentage,
    validate_positive,
    validate_positive_int,
    validate_probability,
    validate_range,
)


class TestValidateRange(unittest.TestCase):
    """Tests for validate_range validator."""

    def test_value_within_range(self):
        """Test that values within range pass validation."""
        validator = validate_range(0.0, 100.0, "test_field")
        self.assertEqual(validator(50.0), 50.0)
        self.assertEqual(validator(0.0), 0.0)
        self.assertEqual(validator(100.0), 100.0)

    def test_value_below_range(self):
        """Test that values below range raise ValidationError."""
        validator = validate_range(0.0, 100.0, "test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator(-1.0)
        self.assertIn("test_field", str(ctx.exception))
        self.assertIn("between 0.0 and 100.0", str(ctx.exception))

    def test_value_above_range(self):
        """Test that values above range raise ValidationError."""
        validator = validate_range(0.0, 100.0, "test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator(101.0)
        self.assertIn("test_field", str(ctx.exception))

    def test_without_field_name(self):
        """Test validator works without field name."""
        validator = validate_range(0.0, 100.0)
        self.assertEqual(validator(50.0), 50.0)
        with self.assertRaises(ValidationError) as ctx:
            validator(150.0)
        self.assertIn("Value", str(ctx.exception))


class TestValidatePositive(unittest.TestCase):
    """Tests for validate_positive validator."""

    def test_positive_value(self):
        """Test that positive values pass validation."""
        validator = validate_positive("test_field")
        self.assertEqual(validator(1.0), 1.0)
        self.assertEqual(validator(0.1), 0.1)

    def test_zero_value(self):
        """Test that zero raises ValidationError."""
        validator = validate_positive("test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator(0.0)
        self.assertIn("must be positive", str(ctx.exception))

    def test_negative_value(self):
        """Test that negative values raise ValidationError."""
        validator = validate_positive("test_field")
        with self.assertRaises(ValidationError):
            validator(-1.0)


class TestValidateNonNegative(unittest.TestCase):
    """Tests for validate_non_negative validator."""

    def test_positive_value(self):
        """Test that positive values pass validation."""
        validator = validate_non_negative("test_field")
        self.assertEqual(validator(1.0), 1.0)

    def test_zero_value(self):
        """Test that zero passes validation."""
        validator = validate_non_negative("test_field")
        self.assertEqual(validator(0.0), 0.0)

    def test_negative_value(self):
        """Test that negative values raise ValidationError."""
        validator = validate_non_negative("test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator(-1.0)
        self.assertIn("must be non-negative", str(ctx.exception))


class TestValidateNonEmpty(unittest.TestCase):
    """Tests for validate_non_empty validator."""

    def test_non_empty_string(self):
        """Test that non-empty strings pass validation."""
        validator = validate_non_empty("test_field")
        self.assertEqual(validator("hello"), "hello")

    def test_string_with_whitespace(self):
        """Test that strings with leading/trailing whitespace are trimmed."""
        validator = validate_non_empty("test_field")
        self.assertEqual(validator("  hello  "), "hello")

    def test_empty_string(self):
        """Test that empty strings raise ValidationError."""
        validator = validate_non_empty("test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator("")
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_whitespace_only_string(self):
        """Test that whitespace-only strings raise ValidationError."""
        validator = validate_non_empty("test_field")
        with self.assertRaises(ValidationError):
            validator("   ")


class TestCoerceType(unittest.TestCase):
    """Tests for coerce_type validator."""

    def test_already_correct_type(self):
        """Test that values of correct type pass through unchanged."""
        validator = coerce_type(int, "test_field")
        self.assertEqual(validator(42), 42)

    def test_successful_coercion(self):
        """Test successful type coercion."""
        validator = coerce_type(float, "test_field")
        self.assertEqual(validator("10.5"), 10.5)
        self.assertEqual(validator(10), 10.0)

    def test_failed_coercion(self):
        """Test that failed coercion raises ValidationError."""
        validator = coerce_type(int, "test_field")
        with self.assertRaises(ValidationError) as ctx:
            validator("not_a_number")
        self.assertIn("must be int", str(ctx.exception))
        self.assertIn("str", str(ctx.exception))

    def test_coerce_to_string(self):
        """Test coercion to string (should always succeed)."""
        validator = coerce_type(str, "test_field")
        self.assertEqual(validator(42), "42")
        self.assertEqual(validator(3.14), "3.14")


class TestValidateAndClamp(unittest.TestCase):
    """Tests for validate_and_clamp validator."""

    def test_value_within_range(self):
        """Test that values within range pass through unchanged."""
        validator = validate_and_clamp(0.0, 100.0)
        self.assertEqual(validator(50.0), 50.0)

    def test_value_below_range(self):
        """Test that values below range are clamped to minimum."""
        validator = validate_and_clamp(0.0, 100.0)
        self.assertEqual(validator(-10.0), 0.0)

    def test_value_above_range(self):
        """Test that values above range are clamped to maximum."""
        validator = validate_and_clamp(0.0, 100.0)
        self.assertEqual(validator(150.0), 100.0)

    def test_string_coercion(self):
        """Test that string values are coerced to float before clamping."""
        validator = validate_and_clamp(0.0, 100.0)
        self.assertEqual(validator("50"), 50.0)


class TestFieldValidator(unittest.TestCase):
    """Tests for FieldValidator composite validator."""

    def test_single_validator(self):
        """Test FieldValidator with single validator."""
        validator = FieldValidator(validate_positive("test"))
        self.assertEqual(validator(10.0), 10.0)
        with self.assertRaises(ValidationError):
            validator(-1.0)

    def test_multiple_validators(self):
        """Test FieldValidator with multiple validators in sequence."""
        validator = FieldValidator(
            coerce_type(float, "value"), validate_positive("value")
        )
        self.assertEqual(validator("10.5"), 10.5)
        with self.assertRaises(ValidationError):
            validator("-5")

    def test_validator_chain(self):
        """Test that validators are applied in order."""
        validator = FieldValidator(
            coerce_type(float, "value"),
            validate_range(0.0, 100.0, "value"),
            validate_positive("value"),
        )
        self.assertEqual(validator("50"), 50.0)

        # Should fail at range check
        with self.assertRaises(ValidationError) as ctx:
            validator("150")
        self.assertIn("between", str(ctx.exception))


class TestConvenienceValidators(unittest.TestCase):
    """Tests for convenience validator factories."""

    def test_validate_percentage(self):
        """Test percentage validator (0-100)."""
        validator = validate_percentage("percent")
        self.assertEqual(validator("50"), 50.0)
        self.assertEqual(validator(0), 0.0)
        self.assertEqual(validator(100), 100.0)

        with self.assertRaises(ValidationError):
            validator(-1)
        with self.assertRaises(ValidationError):
            validator(101)

    def test_validate_probability(self):
        """Test probability validator (0-1)."""
        validator = validate_probability("prob")
        self.assertEqual(validator("0.5"), 0.5)
        self.assertEqual(validator(0), 0.0)
        self.assertEqual(validator(1), 1.0)

        with self.assertRaises(ValidationError):
            validator(-0.1)
        with self.assertRaises(ValidationError):
            validator(1.1)

    def test_validate_positive_int(self):
        """Test positive integer validator."""
        validator = validate_positive_int("count")
        self.assertEqual(validator("10"), 10)
        self.assertEqual(validator(5.9), 5)  # Truncates to int

        with self.assertRaises(ValidationError):
            validator(0)
        with self.assertRaises(ValidationError):
            validator(-1)


if __name__ == "__main__":
    unittest.main()
