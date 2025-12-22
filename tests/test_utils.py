# -*- coding: utf-8 -*-
"""
Tests for core/utils.py
"""

import pytest
import math
from unittest.mock import Mock, patch, MagicMock

from core import utils as scu


class TestStrikeParsing:
    """Tests for strike parsing functions."""

    def test_parse_strike_numeric(self):
        """Test parsing numeric strike values."""
        assert scu.parse_strike(0) == 0
        assert scu.parse_strike(90) == 90
        assert scu.parse_strike(180) == 180
        assert scu.parse_strike(270) == 270
        assert scu.parse_strike(360) == 360

    def test_parse_strike_string_numeric(self):
        """Test parsing string numeric strike values."""
        assert scu.parse_strike("45") == 45.0
        assert scu.parse_strike("180") == 180.0

    def test_parse_strike_quadrant_ne(self, sample_strike_values):
        """Test parsing N-E quadrant notation."""
        result = scu.parse_strike("N 30 E")
        assert result == 30

    def test_parse_strike_quadrant_nw(self):
        """Test parsing N-W quadrant notation."""
        result = scu.parse_strike("N 45 W")
        assert result == 315  # 360 - 45

    def test_parse_strike_quadrant_se(self):
        """Test parsing S-E quadrant notation."""
        result = scu.parse_strike("S 60 E")
        assert result == 120  # 180 - 60

    def test_parse_strike_quadrant_sw(self):
        """Test parsing S-W quadrant notation."""
        result = scu.parse_strike("S 15 W")
        assert result == 195  # 180 + 15

    def test_parse_strike_invalid(self):
        """Test parsing invalid strike values."""
        assert scu.parse_strike(None) is None
        assert scu.parse_strike("invalid") is None
        assert scu.parse_strike("ABC") is None


class TestDipParsing:
    """Tests for dip parsing functions."""

    def test_parse_dip_numeric(self):
        """Test parsing numeric dip values."""
        dip, direction = scu.parse_dip("45")
        assert dip == 45.0
        assert direction is None

    def test_parse_dip_with_direction(self):
        """Test parsing dip with direction."""
        dip, direction = scu.parse_dip("45 NE")
        assert dip == 45.0
        assert direction == 45  # NE = 45 degrees

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
            dip, direction = scu.parse_dip(dip_str)
            assert dip == expected_dip
            assert direction == expected_dir

    def test_parse_dip_invalid(self):
        """Test parsing invalid dip values."""
        assert scu.parse_dip(None) == (None, None)
        assert scu.parse_dip("invalid") == (None, None)


class TestCardinalToAzimuth:
    """Tests for cardinal direction conversion."""

    def test_cardinal_to_azimuth_all_directions(self):
        """Test all cardinal directions."""
        assert scu.cardinal_to_azimuth("N") == 0
        assert scu.cardinal_to_azimuth("NE") == 45
        assert scu.cardinal_to_azimuth("E") == 90
        assert scu.cardinal_to_azimuth("SE") == 135
        assert scu.cardinal_to_azimuth("S") == 180
        assert scu.cardinal_to_azimuth("SW") == 225
        assert scu.cardinal_to_azimuth("W") == 270
        assert scu.cardinal_to_azimuth("NW") == 315

    def test_cardinal_to_azimuth_invalid(self):
        """Test invalid cardinal direction."""
        assert scu.cardinal_to_azimuth("INVALID") is None
        assert scu.cardinal_to_azimuth("") is None


class TestApparentDip:
    """Tests for apparent dip calculation."""

    def test_calculate_apparent_dip_perpendicular(self):
        """Test when section is perpendicular to strike."""
        # Strike = 90, Dip = 45, Section = 0 (perpendicular)
        result = scu.calculate_apparent_dip(90, 45, 0)
        # Should be close to true dip
        assert abs(result - 45) < 1.0

    def test_calculate_apparent_dip_parallel(self):
        """Test when section is parallel to strike."""
        # Strike = 90, Dip = 45, Section = 90 (parallel)
        result = scu.calculate_apparent_dip(90, 45, 90)
        # Should be close to 0
        assert abs(result) < 1.0

    def test_calculate_apparent_dip_45_degrees(self):
        """Test at 45 degree angle."""
        result = scu.calculate_apparent_dip(90, 45, 45)
        # Should be between 0 and 45
        assert 0 <= abs(result) <= 45


class TestInterpolation:
    """Tests for elevation interpolation."""

    def test_interpolate_elevation_exact_point(self, sample_profile_data):
        """Test interpolation at exact data point."""
        result = scu.interpolate_elevation(sample_profile_data, 100.0)
        assert result == 150.0

    def test_interpolate_elevation_midpoint(self, sample_profile_data):
        """Test interpolation at midpoint."""
        result = scu.interpolate_elevation(sample_profile_data, 50.0)
        # Should be average of 100 and 150
        assert result == 125.0

    def test_interpolate_elevation_beyond_range(self, sample_profile_data):
        """Test interpolation beyond data range."""
        result = scu.interpolate_elevation(sample_profile_data, 500.0)
        # Should return last elevation
        assert result == 140.0

    def test_interpolate_elevation_empty_data(self):
        """Test interpolation with empty data."""
        result = scu.interpolate_elevation([], 100.0)
        assert result == 0




class TestBufferGeometry:
    """Tests for create_buffer_geometry using native algorithm."""

    def test_create_buffer_geometry_basic(self):
        """Test basic buffer creation."""
        from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, QgsVectorLayer
        from unittest.mock import Mock, patch
        import core.utils.geometry

        # Create mock geometry - use Mock with proper setup instead of QgsGeometry instance
        mock_geom = Mock()
        mock_geom.isNull.return_value = False
        mock_geom.type.return_value = 1  # LineGeometry

        # Create mock CRS
        mock_crs = Mock()

        # Mock the processing result
        mock_buffer_geom = Mock()
        mock_buffer_geom.isNull.return_value = False
        mock_buffer_feat = Mock()
        mock_buffer_feat.geometry.return_value = mock_buffer_geom

        mock_buffer_layer = Mock()
        mock_buffer_layer.featureCount.return_value = 1
        mock_buffer_layer.getFeatures.return_value = iter([mock_buffer_feat])

        with patch("qgis.processing.run") as mock_run:
            mock_run.return_value = {"OUTPUT": mock_buffer_layer}

            # Call function
            result = scu.create_buffer_geometry(mock_geom, mock_crs, 100.0)

            # Verify processing.run was called
            mock_run.assert_called_once()
            assert result == mock_buffer_geom

    def test_create_buffer_geometry_invalid_input(self):
        """Test buffer creation with invalid geometry."""
        from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem

        mock_geom = Mock()
        mock_geom.isNull.return_value = True

        mock_crs = Mock()

        # Should raise ValueError
        with pytest.raises(ValueError, match="Geometry is null or invalid"):
            scu.create_buffer_geometry(mock_geom, mock_crs, 100.0)

    def test_create_buffer_geometry_no_features(self):
        """Test buffer creation when algorithm produces no features."""
        from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock, patch

        mock_geom = Mock()
        mock_geom.isNull.return_value = False
        mock_geom.type.return_value = 1  # LineGeometry

        mock_crs = Mock()

        # Mock empty result
        mock_buffer_layer = Mock()
        mock_buffer_layer.featureCount.return_value = 0

        with patch("qgis.processing.run") as mock_run:
            mock_run.return_value = {"OUTPUT": mock_buffer_layer}

            # Should raise ValueError
            with pytest.raises(ValueError, match="Resulting geometry from native:buffer is null"):
                scu.create_buffer_geometry(mock_geom, mock_crs, 100.0)

    def test_create_buffer_geometry_processing_error(self):
        """Test buffer creation when processing algorithm fails."""
        from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock, patch

        mock_geom = Mock()
        mock_geom.isNull.return_value = False
        mock_geom.type.return_value = 1  # LineGeometry

        mock_crs = Mock()

        # Mock processing failure
        with patch("qgis.processing.run") as mock_run:
            mock_run.side_effect = Exception("Processing failed")

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to create buffer"):
                scu.create_buffer_geometry(mock_geom, mock_crs, 100.0)


class TestSpatialFiltering:
    """Tests for filter_features_by_buffer using native algorithm."""

    def test_filter_features_by_buffer_basic(self):
        """Test basic spatial filtering."""
        from qgis.core import QgsVectorLayer, QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock, patch

        # Mock inputs
        mock_layer = Mock()
        mock_layer.isValid.return_value = True
        mock_layer.featureCount.return_value = 100
        mock_layer.getFeatures.return_value = iter([])

        mock_buffer_geom = Mock()
        mock_buffer_geom.isNull.return_value = False
        mock_buffer_geom.boundingBox.return_value = Mock()

        mock_crs = Mock()

        # Mock filtered result
        mock_filtered = Mock()
        mock_filtered.featureCount.return_value = 25
        
        with patch("qgis.processing.run") as mock_run:
            mock_run.return_value = {"OUTPUT": mock_filtered}

            # Call function
            result = scu.filter_features_by_buffer(
                mock_layer, mock_buffer_geom, mock_crs
            )

            # Verify
            assert result.featureCount() == 25
            mock_run.assert_called_once()
            
            # Verify correct algorithm was called
            call_args = mock_run.call_args
            assert call_args[0][0] == "native:extractbylocation"

    def test_filter_features_invalid_layer(self):
        """Test with invalid layer."""
        from qgis.core import QgsVectorLayer, QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock

        mock_layer = Mock()
        mock_layer.isValid.return_value = False

        mock_geom = Mock()
        mock_crs = Mock()

        with pytest.raises(ValueError, match="Invalid features layer"):
            scu.filter_features_by_buffer(mock_layer, mock_geom, mock_crs)

    def test_filter_features_invalid_buffer(self):
        """Test with invalid buffer geometry."""
        from qgis.core import QgsVectorLayer, QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock

        mock_layer = Mock()
        mock_layer.isValid.return_value = True

        mock_geom = Mock()
        mock_geom.isNull.return_value = True

        mock_crs = Mock()

        with pytest.raises(ValueError, match="Invalid buffer geometry"):
            scu.filter_features_by_buffer(mock_layer, mock_geom, mock_crs)

    def test_filter_features_processing_error(self):
        """Test when processing algorithm fails."""
        from qgis.core import QgsVectorLayer, QgsGeometry, QgsCoordinateReferenceSystem
        from unittest.mock import Mock, patch

        mock_layer = Mock()
        mock_layer.isValid.return_value = True
        mock_layer.getFeatures.return_value = iter([])

        mock_geom = Mock()
        mock_geom.isNull.return_value = False

        mock_crs = Mock()

        # Mock processing failure
        with patch("qgis.processing.run") as mock_run:
            mock_run.side_effect = Exception("Spatial index failed")

            with pytest.raises(RuntimeError, match="Failed to filter features"):
                scu.filter_features_by_buffer(mock_layer, mock_geom, mock_crs)
