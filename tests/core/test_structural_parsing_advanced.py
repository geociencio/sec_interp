# -*- coding: utf-8 -*-
"""
Advanced tests for structural parsing in SecInterp.
Focuses on edge cases, combined notations, and messy data strings.
"""

from tests.base_test import BaseTestCase
from sec_interp.core.utils import parse_strike, parse_dip


class TestStructuralParsingAdvanced(BaseTestCase):
    """Advanced tests for strike and dip parsing."""

    def test_combined_notation_with_comma(self):
        """Test parsing combined strike/dip with a comma separator."""
        strike_str = "N 16ø W, 19ø SW"
        self.assertEqual(parse_strike(strike_str), 344.0)  # N 16 W = 360 - 16

        dip, direction = parse_dip(strike_str)
        self.assertEqual(dip, 19.0)
        self.assertEqual(direction, 225.0)  # SW = 225

    def test_combined_notation_with_slash(self):
        """Test parsing combined strike/dip with a slash separator."""
        strike_str = "125/45SE"
        self.assertEqual(parse_strike(strike_str), 125.0)

        dip, direction = parse_dip(strike_str)
        self.assertEqual(dip, 45.0)
        self.assertEqual(direction, 135.0)  # SE = 135

    def test_combined_notation_with_dash(self):
        """Test parsing combined strike/dip with a dash separator."""
        strike_str = "045-30NE"
        self.assertEqual(parse_strike(strike_str), 45.0)

        dip, direction = parse_dip(strike_str)
        self.assertEqual(dip, 30.0)
        self.assertEqual(direction, 45.0)  # NE = 45

    def test_varied_degree_symbols(self):
        """Test string with mixed degree symbols."""
        # Using °, º, and ø interchangeably
        test_str = "N 45° E / 30º SE"
        self.assertEqual(parse_strike(test_str), 45.0)

        dip, direction = parse_dip(test_str)
        self.assertEqual(dip, 30.0)
        self.assertEqual(direction, 135.0)

        test_str_2 = "S 15ø W; 60ø NW"
        self.assertEqual(parse_strike(test_str_2), 195.0)  # S 15 W = 180 + 15

        dip, direction = parse_dip(test_str_2)
        self.assertEqual(dip, 60.0)
        self.assertEqual(direction, 315.0)  # NW = 315

    def test_partial_data_dip_only(self):
        """Test parsing when only dip is present in a string."""
        # Some users might only have dip data in a string field
        dip_str = "Dip: 45 SE"
        # parse_strike might fail to find a valid strike pattern
        self.assertIsNone(parse_strike(dip_str))

        dip, direction = parse_dip(dip_str)
        self.assertEqual(dip, 45.0)
        self.assertEqual(direction, 135.0)

    def test_partial_data_strike_only(self):
        """Test parsing when only strike is present in a string."""
        strike_str = "Strike: N 30 E"
        self.assertEqual(parse_strike(strike_str), 30.0)

        dip, direction = parse_dip(strike_str)
        self.assertIsNone(dip)

    def test_messy_delimiters_and_spaces(self):
        """Test strings with unusual spacing and delimiters."""
        test_cases = [
            ("N30E , 45SW", 30.0, 45.0, 225.0),
            ("  S15W/60NW  ", 195.0, 60.0, 315.0),
            ("N45E|30SE", 45.0, 30.0, 135.0),
        ]

        for s_str, expected_strike, expected_dip, expected_dir in test_cases:
            self.assertEqual(parse_strike(s_str), expected_strike)
            dip, direction = parse_dip(s_str)
            self.assertEqual(dip, expected_dip)
            self.assertEqual(direction, expected_dir)

    def test_invalid_ranges(self):
        """Test handling of values outside normal ranges."""
        # Strike > 360 (should ideally wrap or return as is depending on logic)
        # Current logic for numeric strings: float(val) % 360
        self.assertEqual(parse_strike("400"), 40.0)

        # Dip > 90 (physically impossible but should handle it)
        # Current logic: float(val)
        dip, _ = parse_dip("120 SE")
        self.assertEqual(dip, 120.0)

    def test_alpha_prefix_strip(self):
        """Test stripping alphabetic prefixes."""
        self.assertEqual(parse_strike("Stk: 45"), 45.0)
        self.assertEqual(parse_dip("D: 30")[0], 30.0)
