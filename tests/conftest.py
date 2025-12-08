# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_strike_values():
    """Sample strike values for testing."""
    return {
        "numeric": [0, 45, 90, 180, 270, 360],
        "quadrant": ["N 30 E", "N 45 W", "S 60 E", "S 15 W"],
        "invalid": ["invalid", None, "ABC"],
    }


@pytest.fixture
def sample_dip_values():
    """Sample dip values for testing."""
    return {
        "numeric": [0, 30, 45, 60, 90],
        "with_direction": ["45 NE", "30 SW", "60 N"],
        "invalid": ["invalid", None, "100", "-10"],
    }


@pytest.fixture
def sample_profile_data():
    """Sample topographic profile data."""
    return [
        (0.0, 100.0),
        (100.0, 150.0),
        (200.0, 120.0),
        (300.0, 180.0),
        (400.0, 140.0),
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for output files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return {
        "headers": ["distance", "elevation", "unit"],
        "rows": [
            [0.0, 100.0, "Unit A"],
            [100.0, 150.0, "Unit B"],
            [200.0, 120.0, "Unit A"],
        ],
    }
