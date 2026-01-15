"""Tests for validation_helpers module."""

import unittest
from sec_interp.core.exceptions import ValidationError
from sec_interp.core.validation.validation_helpers import (
    DependencyRule,
    RichValidationError,
    ValidationContext,
    validate_dependencies,
    validate_reasonable_ranges,
)


class TestValidationContext(unittest.TestCase):
    """Test suite for ValidationContext."""

    def test_add_error(self):
        ctx = ValidationContext()
        ctx.add_error("Test Error", "field_a", extra="info")

        self.assertTrue(ctx.has_errors)
        self.assertEqual(len(ctx.errors), 1)
        err = ctx.errors[0]
        self.assertEqual(err.message, "Test Error")
        self.assertEqual(err.field_name, "field_a")
        self.assertEqual(err.severity, "error")
        # Direct context check might depend on implementation details, usually not exposed directly by attributes unless dataclass
        # But RichValidationError is a dataclass
        self.assertEqual(err.context["extra"], "info")

    def test_add_warning(self):
        ctx = ValidationContext()
        ctx.add_warning("Test Warning")

        self.assertFalse(ctx.has_errors)
        self.assertTrue(ctx.has_warnings)
        self.assertEqual(ctx.warnings[0].severity, "warning")

    def test_raise_if_errors(self):
        ctx = ValidationContext()
        ctx.add_error("Bad")
        with self.assertRaises(ValidationError):
            ctx.raise_if_errors()

    def test_no_raise_if_only_warnings(self):
        ctx = ValidationContext()
        ctx.add_warning("Just a warning")
        try:
            ctx.raise_if_errors()
        except ValidationError:
            self.fail("Should not raise ValidationError for warnings only")


class TestDependencyRule(unittest.TestCase):
    """Test suite for DependencyRule."""

    def test_rule_passed(self):
        ctx = ValidationContext()
        flag = True
        value = "filled"

        rule = DependencyRule(
            condition=lambda: flag,
            check=lambda: bool(value),
            error_message="Value missing",
            target_field="value",
        )
        rule.validate(ctx)
        self.assertFalse(ctx.has_errors)

    def test_rule_failed(self):
        ctx = ValidationContext()
        flag = True
        value = ""

        rule = DependencyRule(
            condition=lambda: flag,
            check=lambda: bool(value),
            error_message="Value missing",
            target_field="value",
        )
        rule.validate(ctx)
        self.assertTrue(ctx.has_errors)
        self.assertEqual(ctx.errors[0].message, "Value missing")
        self.assertEqual(ctx.errors[0].field_name, "value")

    def test_rule_ignored(self):
        """Condition false, should skip check."""
        ctx = ValidationContext()
        flag = False
        value = ""  # Invalid if checked

        rule = DependencyRule(
            condition=lambda: flag,
            check=lambda: bool(value),
            error_message="Value missing",
        )
        rule.validate(ctx)
        self.assertFalse(ctx.has_errors)


class TestValidateReasonableRanges(unittest.TestCase):
    """Test reasonable ranges helper."""

    def test_valid_ranges(self):
        data = {"vert_exag": 1.0, "scale": 1000, "buffer": 100, "dip_scale": 1.0}
        warnings = validate_reasonable_ranges(data)
        self.assertEqual(len(warnings), 0)

    def test_extreme_values(self):
        data = {"vert_exag": 20.0, "buffer": 6000}  # High  # High
        warnings = validate_reasonable_ranges(data)
        self.assertTrue(len(warnings) >= 2)
        self.assertTrue(any("Vertical exaggeration" in w for w in warnings))
        self.assertTrue(any("Buffer distance" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
