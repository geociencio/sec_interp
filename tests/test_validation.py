# -*- coding: utf-8 -*-
"""
Tests for core/validation.py
"""


from core import validation as vu


class TestNumericValidation:
    """Tests for numeric input validation."""

    def test_validate_numeric_input_valid(self):
        """Test valid numeric inputs."""
        assert vu.validate_numeric_input("123") == (True, "", 123.0)
        assert vu.validate_numeric_input("45.5") == (True, "", 45.5)
        assert vu.validate_numeric_input("-10") == (True, "", -10.0)

    def test_validate_numeric_input_invalid(self):
        """Test invalid numeric inputs."""
        is_valid, error, _ = vu.validate_numeric_input("abc")
        assert not is_valid
        assert "numeric" in error.lower()

        is_valid, error, _ = vu.validate_numeric_input("")
        assert not is_valid

    def test_validate_numeric_input_with_range(self):
        """Test numeric validation with range."""
        is_valid, error, value = vu.validate_numeric_input("50", min_val=0, max_val=100)
        assert is_valid
        assert value == 50.0

        is_valid, error, _ = vu.validate_numeric_input("150", min_val=0, max_val=100)
        assert not is_valid
        assert "range" in error.lower()


class TestIntegerValidation:
    """Tests for integer input validation."""

    def test_validate_integer_input_valid(self):
        """Test valid integer inputs."""
        assert vu.validate_integer_input("123") == (True, "", 123)
        assert vu.validate_integer_input("0") == (True, "", 0)

    def test_validate_integer_input_invalid(self):
        """Test invalid integer inputs."""
        is_valid, error, _ = vu.validate_integer_input("45.5")
        assert not is_valid

        is_valid, error, _ = vu.validate_integer_input("abc")
        assert not is_valid


class TestAngleValidation:
    """Tests for angle range validation."""

    def test_validate_angle_range_valid(self):
        """Test valid angle values."""
        assert vu.validate_angle_range("0") == (True, "", 0.0)
        assert vu.validate_angle_range("180") == (True, "", 180.0)
        assert vu.validate_angle_range("360") == (True, "", 360.0)

    def test_validate_angle_range_invalid(self):
        """Test invalid angle values."""
        is_valid, error, _ = vu.validate_angle_range("-10")
        assert not is_valid

        is_valid, error, _ = vu.validate_angle_range("400")
        assert not is_valid


class TestOutputPathValidation:
    """Tests for output path validation."""

    def test_validate_output_path_valid(self, temp_output_dir):
        """Test valid output path."""
        is_valid, error, path = vu.validate_output_path(str(temp_output_dir))
        assert is_valid
        assert path == temp_output_dir

    def test_validate_output_path_nonexistent(self, tmp_path):
        """Test non-existent path."""
        nonexistent = tmp_path / "nonexistent"
        is_valid, error, _ = vu.validate_output_path(str(nonexistent))
        assert not is_valid
        assert "not exist" in error.lower() or "does not exist" in error.lower()

    def test_validate_output_path_not_directory(self, tmp_path):
        """Test path that is a file, not directory."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")
        is_valid, error, _ = vu.validate_output_path(str(file_path))
        assert not is_valid
        assert "directory" in error.lower()
