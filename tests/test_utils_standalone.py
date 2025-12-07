# -*- coding: utf-8 -*-
"""
Standalone tests for core/utils.py (no QGIS dependencies)
These tests can run without QGIS installation.
"""

import pytest
import math


# Import only the parsing functions (no QGIS dependencies)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestStrikeParsing:
    """Tests for strike parsing functions."""

    def test_parse_strike_numeric(self):
        """Test parsing numeric strike values."""
        from core.utils import parse_strike

        assert parse_strike(0) == 0
        assert parse_strike(90) == 90
        assert parse_strike(180) == 180
        assert parse_strike(270) == 270
        assert parse_strike(360) == 360

    def test_parse_strike_string_numeric(self):
        """Test parsing string numeric strike values."""
        from core.utils import parse_strike

        assert parse_strike("45") == 45.0
        assert parse_strike("180") == 180.0

    def test_parse_strike_quadrant_ne(self):
        """Test parsing N-E quadrant notation."""
        from core.utils import parse_strike

        result = parse_strike("N 30 E")
        assert result == 30

    def test_parse_strike_quadrant_nw(self):
        """Test parsing N-W quadrant notation."""
        from core.utils import parse_strike

        result = parse_strike("N 45 W")
        assert result == 315  # 360 - 45

    def test_parse_strike_quadrant_se(self):
        """Test parsing S-E quadrant notation."""
        from core.utils import parse_strike

        result = parse_strike("S 60 E")
        assert result == 120  # 180 - 60

    def test_parse_strike_quadrant_sw(self):
        """Test parsing S-W quadrant notation."""
        from core.utils import parse_strike

        result = parse_strike("S 15 W")
        assert result == 195  # 180 + 15

    def test_parse_strike_invalid(self):
        """Test parsing invalid strike values."""
        from core.utils import parse_strike

        assert parse_strike(None) is None
        assert parse_strike("invalid") is None
        assert parse_strike("ABC") is None


class TestDipParsing:
    """Tests for dip parsing functions."""

    def test_parse_dip_numeric(self):
        """Test parsing numeric dip values."""
        from core.utils import parse_dip

        dip, direction = parse_dip("45")
        assert dip == 45.0
        assert direction is None

    def test_parse_dip_with_direction(self):
        """Test parsing dip with direction."""
        from core.utils import parse_dip

        dip, direction = parse_dip("45 NE")
        assert dip == 45.0
        assert direction == 45  # NE = 45 degrees

    def test_parse_dip_cardinal_directions(self):
        """Test all cardinal directions."""
        from core.utils import parse_dip

        test_cases = [
            ("30 N", 30.0, 0),
            ("45 NE", 45.0, 45),
            ("60 E", 60.0, 90),
            ("30 SE", 30.0, 135),
            ("45 S", 45.0, 180),
            ("60 SW", 60.0, 225),
            ("30 W", 30.0, 270),
            ("45 NW", 45.0, 315),
        ]
        for dip_str, expected_dip, expected_dir in test_cases:
            dip, direction = parse_dip(dip_str)
            assert dip == expected_dip
            assert direction == expected_dir

    def test_parse_dip_invalid(self):
        """Test parsing invalid dip values."""
        from core.utils import parse_dip

        assert parse_dip(None) == (None, None)
        assert parse_dip("invalid") == (None, None)


class TestCardinalToAzimuth:
    """Tests for cardinal direction conversion."""

    def test_cardinal_to_azimuth_all_directions(self):
        """Test all cardinal directions."""
        from core.utils import cardinal_to_azimuth

        assert cardinal_to_azimuth("N") == 0
        assert cardinal_to_azimuth("NE") == 45
        assert cardinal_to_azimuth("E") == 90
        assert cardinal_to_azimuth("SE") == 135
        assert cardinal_to_azimuth("S") == 180
        assert cardinal_to_azimuth("SW") == 225
        assert cardinal_to_azimuth("W") == 270
        assert cardinal_to_azimuth("NW") == 315

    def test_cardinal_to_azimuth_invalid(self):
        """Test invalid cardinal direction."""
        from core.utils import cardinal_to_azimuth

        assert cardinal_to_azimuth("INVALID") is None
        assert cardinal_to_azimuth("") is None


class TestApparentDip:
    """Tests for apparent dip calculation."""

    def test_calculate_apparent_dip_perpendicular(self):
        """Test when section is perpendicular to strike."""
        from core.utils import calculate_apparent_dip

        # Strike = 90, Dip = 45, Section = 0 (perpendicular)
        result = calculate_apparent_dip(90, 45, 0)
        # Should be close to true dip
        assert abs(result - 45) < 1.0

    def test_calculate_apparent_dip_parallel(self):
        """Test when section is parallel to strike."""
        from core.utils import calculate_apparent_dip

        # Strike = 90, Dip = 45, Section = 90 (parallel)
        result = calculate_apparent_dip(90, 45, 90)
        # Should be close to 0
        assert abs(result) < 1.0

    def test_calculate_apparent_dip_45_degrees(self):
        """Test at 45 degree angle."""
        from core.utils import calculate_apparent_dip

        result = calculate_apparent_dip(90, 45, 45)
        # Should be between 0 and 45
        assert 0 <= abs(result) <= 45


class TestInterpolation:
    """Tests for elevation interpolation."""

    def test_interpolate_elevation_exact_point(self):
        """Test interpolation at exact data point."""
        from core.utils import interpolate_elevation

        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0)]
        result = interpolate_elevation(sample_data, 100.0)
        assert result == 150.0

    def test_interpolate_elevation_midpoint(self):
        """Test interpolation at midpoint."""
        from core.utils import interpolate_elevation

        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0)]
        result = interpolate_elevation(sample_data, 50.0)
        # Should be average of 100 and 150
        assert result == 125.0

    def test_interpolate_elevation_beyond_range(self):
        """Test interpolation beyond data range."""
        from core.utils import interpolate_elevation

        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0), (400.0, 140.0)]
        result = interpolate_elevation(sample_data, 500.0)
        # Should return last elevation
        assert result == 140.0

    def test_interpolate_elevation_empty_data(self):
        """Test interpolation with empty data."""
        from core.utils import interpolate_elevation

        result = interpolate_elevation([], 100.0)
        assert result == 0
