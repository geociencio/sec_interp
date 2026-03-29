# -*- coding: utf-8 -*-
"""
Standalone tests for core/utils.py (no QGIS dependencies)
These tests can run without QGIS installation.
"""

from tests.base_test import BaseTestCase

# Import only the parsing functions
from sec_interp.core.utils import (
    parse_strike,
    parse_dip,
    cardinal_to_azimuth,
    calculate_apparent_dip,
    interpolate_elevation,
)


class TestStrikeParsingStandalone(BaseTestCase):
    """Tests for strike parsing functions."""

    def test_parse_strike_numeric(self):
        """Test parsing numeric strike values."""
        self.assertEqual(parse_strike(0), 0)
        self.assertEqual(parse_strike(90), 90)
        self.assertEqual(parse_strike(180), 180)
        self.assertEqual(parse_strike(270), 270)
        self.assertEqual(parse_strike(360), 360)

    def test_parse_strike_string_numeric(self):
        """Test parsing string numeric strike values."""
        self.assertEqual(parse_strike("45"), 45.0)
        self.assertEqual(parse_strike("180"), 180.0)

    def test_parse_strike_quadrant_ne(self):
        """Test parsing N-E quadrant notation."""
        result = parse_strike("N 30 E")
        self.assertEqual(result, 30)

    def test_parse_strike_quadrant_nw(self):
        """Test parsing N-W quadrant notation."""
        result = parse_strike("N 45 W")
        self.assertEqual(result, 315)  # 360 - 45

    def test_parse_strike_quadrant_se(self):
        """Test parsing S-E quadrant notation."""
        result = parse_strike("S 60 E")
        self.assertEqual(result, 120)  # 180 - 60

    def test_parse_strike_quadrant_sw(self):
        """Test parsing S-W quadrant notation."""
        result = parse_strike("S 15 W")
        self.assertEqual(result, 195)  # 180 + 15

    def test_parse_strike_combined_notation(self):
        """Test parsing strike from a combined strike/dip string."""
        # Strike should be extracted from the beginning, ignoring the comma and dip
        result = parse_strike("N 16ø W, 19ø SW")
        self.assertEqual(result, 344)  # N 16 W = 360 - 16

    def test_parse_strike_invalid(self):
        """Test parsing invalid strike values."""
        self.assertIsNone(parse_strike(None))
        self.assertIsNone(parse_strike("invalid"))
        self.assertIsNone(parse_strike("ABC"))


class TestDipParsingStandalone(BaseTestCase):
    """Tests for dip parsing functions."""

    def test_parse_dip_numeric(self):
        """Test parsing numeric dip values."""
        dip, direction = parse_dip("45")
        self.assertEqual(dip, 45.0)
        self.assertIsNone(direction)

    def test_parse_dip_with_direction(self):
        """Test parsing dip with direction."""
        dip, direction = parse_dip("45 NE")
        self.assertEqual(dip, 45.0)
        self.assertEqual(direction, 45)  # NE = 45 degrees

    def test_parse_dip_cardinal_directions(self):
        """Test all cardinal directions."""
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
            self.assertEqual(dip, expected_dip)
            self.assertEqual(direction, expected_dir)

    def test_parse_dip_combined_notation(self):
        """Test parsing dip from a combined strike/dip string."""
        # Dip should be found even if preceded by strike
        dip, direction = parse_dip("N 16ø W, 19ø SW")
        self.assertEqual(dip, 19.0)
        self.assertEqual(direction, 225)  # SW = 225

    def test_parse_dip_alternative_symbols(self):
        """Test parsing dip with various degree symbols."""
        self.assertEqual(parse_dip("45° NE")[0], 45.0)
        self.assertEqual(parse_dip("45º NE")[0], 45.0)
        self.assertEqual(parse_dip("45ø NE")[0], 45.0)

    def test_parse_dip_invalid(self):
        """Test parsing invalid dip values."""
        self.assertEqual(parse_dip(None), (None, None))
        self.assertEqual(parse_dip("invalid"), (None, None))


class TestCardinalToAzimuthStandalone(BaseTestCase):
    """Tests for cardinal direction conversion."""

    def test_cardinal_to_azimuth_all_directions(self):
        """Test all cardinal directions."""
        self.assertEqual(cardinal_to_azimuth("N"), 0)
        self.assertEqual(cardinal_to_azimuth("NE"), 45)
        self.assertEqual(cardinal_to_azimuth("E"), 90)
        self.assertEqual(cardinal_to_azimuth("SE"), 135)
        self.assertEqual(cardinal_to_azimuth("S"), 180)
        self.assertEqual(cardinal_to_azimuth("SW"), 225)
        self.assertEqual(cardinal_to_azimuth("W"), 270)
        self.assertEqual(cardinal_to_azimuth("NW"), 315)

    def test_cardinal_to_azimuth_invalid(self):
        """Test invalid cardinal direction."""
        self.assertIsNone(cardinal_to_azimuth("INVALID"))
        self.assertIsNone(cardinal_to_azimuth(""))


class TestApparentDipStandalone(BaseTestCase):
    """Tests for apparent dip calculation."""

    def test_calculate_apparent_dip_perpendicular(self):
        """Test when section is perpendicular to strike."""
        # Strike = 90, Dip = 45, Section = 0 (perpendicular)
        result = calculate_apparent_dip(90, 45, 0)
        # Should be close to true dip
        self.assertLess(abs(result - 45), 1.0)

    def test_calculate_apparent_dip_parallel(self):
        """Test when section is parallel to strike."""
        # Strike = 90, Dip = 45, Section = 90 (parallel)
        result = calculate_apparent_dip(90, 45, 90)
        # Should be close to 0
        self.assertLess(abs(result), 1.0)

    def test_calculate_apparent_dip_45_degrees(self):
        """Test at 45 degree angle."""
        result = calculate_apparent_dip(90, 45, 45)
        # Should be between 0 and 45
        self.assertTrue(0 <= abs(result) <= 45)


class TestInterpolationStandalone(BaseTestCase):
    """Tests for elevation interpolation."""

    def test_interpolate_elevation_exact_point(self):
        """Test interpolation at exact data point."""
        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0)]
        result = interpolate_elevation(sample_data, 100.0)
        self.assertEqual(result, 150.0)

    def test_interpolate_elevation_midpoint(self):
        """Test interpolation at midpoint."""
        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0)]
        result = interpolate_elevation(sample_data, 50.0)
        # Should be average of 100 and 150
        self.assertEqual(result, 125.0)

    def test_interpolate_elevation_beyond_range(self):
        """Test interpolation beyond data range."""
        sample_data = [(0.0, 100.0), (100.0, 150.0), (200.0, 120.0), (400.0, 140.0)]
        result = interpolate_elevation(sample_data, 500.0)
        # Should return last elevation
        self.assertEqual(result, 140.0)

    def test_interpolate_elevation_empty_data(self):
        """Test interpolation with empty data."""
        result = interpolate_elevation([], 100.0)
        self.assertEqual(result, 0)
