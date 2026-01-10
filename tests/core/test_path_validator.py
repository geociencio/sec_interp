"""Tests for path validation utilities."""

import os
from pathlib import Path
from tests.base_test import BaseTestCase
from sec_interp.core.validation.path_validator import (
    validate_safe_output_path,
    validate_output_path,
)


class TestPathValidator(BaseTestCase):
    """Tests for path_validator.py"""

    def test_validate_safe_output_path_basic(self):
        """Test basic path validation."""
        # Valid path (not necessarily existing)
        path = os.path.join(self.test_dir, "test_file.txt")
        is_valid, msg, resolved = validate_safe_output_path(path)
        self.assertTrue(is_valid)
        self.assertIsInstance(resolved, Path)

        # Empty path
        is_valid, msg, resolved = validate_safe_output_path("")
        self.assertFalse(is_valid)
        self.assertIn("required", msg)

    def test_validate_safe_output_path_security(self):
        """Test security checks (null bytes, traversal)."""
        # Null byte
        is_valid, msg, resolved = validate_safe_output_path("path\0with\0null")
        self.assertFalse(is_valid)
        self.assertIn("null bytes", msg)

        # Directory traversal
        is_valid, msg, resolved = validate_safe_output_path("../../etc/passwd")
        self.assertFalse(is_valid)
        self.assertIn("directory traversal", msg)

    def test_validate_safe_output_path_sandbox(self):
        """Test base directory restriction (sandboxing)."""
        base = Path(self.test_dir)
        inside = base / "inside.txt"
        outside = Path("/tmp/outside.txt")

        # Inside sandbox
        is_valid, msg, resolved = validate_safe_output_path(str(inside), base_dir=base)
        self.assertTrue(is_valid)

        # Outside sandbox
        is_valid, msg, resolved = validate_safe_output_path(str(outside), base_dir=base)
        self.assertFalse(is_valid)
        self.assertIn("escapes base directory", msg)

    def test_validate_safe_output_path_creation(self):
        """Test automatic directory creation."""
        new_dir = os.path.join(self.test_dir, "new_subdir")

        # Must exist but doesn't
        is_valid, msg, resolved = validate_safe_output_path(new_dir, must_exist=True)
        self.assertFalse(is_valid)

        # Create if missing
        is_valid, msg, resolved = validate_safe_output_path(
            new_dir, create_if_missing=True
        )
        self.assertTrue(is_valid)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

    def test_validate_safe_output_path_is_dir(self):
        """Test that existing path must be a directory."""
        file_path = os.path.join(self.test_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("test")

        is_valid, msg, resolved = validate_safe_output_path(file_path)
        self.assertFalse(is_valid)
        self.assertIn("not a directory", msg)

    def test_validate_output_path_convenience(self):
        """Test the convenience wrapper."""
        # Existing dir
        is_valid, msg, resolved = validate_output_path(self.test_dir)
        self.assertTrue(is_valid)

        # Missing dir
        missing = os.path.join(self.test_dir, "missing_convenience")
        is_valid, msg, resolved = validate_output_path(missing)
        self.assertFalse(is_valid)
