"""Tests for InterpretationService."""

import pytest
from unittest.mock import MagicMock
from qgis.core import QgsGeometry, QgsPoint, QgsLineString, QgsPointXY

from sec_interp.core.services.interpretation_service import InterpretationService
from sec_interp.core.types import InterpretationPolygon
from sec_interp.core.exceptions import ValidationError


class TestInterpretationService:
    @pytest.fixture
    def service(self):
        return InterpretationService()

    @pytest.fixture
    def section_line(self):
        # A simple straight line from (0,0) to (100,0)
        points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        return QgsGeometry.fromPolylineXY(points)

    @pytest.fixture
    def sample_polygon_2d(self):
        # Simple rectangle in profile (distance, elevation)
        # Dist: 10 to 20, Elev: 50 to 60
        vertices = [
            (10.0, 60.0),
            (20.0, 60.0),
            (20.0, 50.0),
            (10.0, 50.0),
            (10.0, 60.0),
        ]
        return InterpretationPolygon(
            id="poly1",
            name="Test Unit",
            type="lithology",
            vertices_2d=vertices,
            attributes={"notes": "test"},
            color="#FF0000"
        )

    def test_interpolate_point_on_line(self, service, section_line):
        """Test utility to get X,Y for a distance."""
        pt = service.interpolate_point_on_line(50.0, section_line)
        assert pt is not None
        assert pt.x() == 50.0
        assert pt.y() == 0.0

    def test_project_2d_to_25d_basic(self, service, section_line, sample_polygon_2d):
        """Test basic projection to 2.5D geometry."""
        crs = MagicMock()
        result = service.project_2d_to_25d(sample_polygon_2d, section_line, crs)
        
        assert result.id == sample_polygon_2d.id
        assert result.name == sample_polygon_2d.name
        assert not result.geometry.isNull()
        
        # Verify geometry type (Polygon)
        geom = result.geometry.constGet()
        assert geom.isMeasure()  # Checks for M coordinate
        
        # Check first point: dist 10, elev 60 -> (10, 0, 0, 60)
        ring = geom.exteriorRing()
        assert ring.numPoints() >= 5
        
        p1 = ring.pointN(0)
        assert p1.x() == 10.0
        assert p1.y() == 0.0
        assert p1.m() == 60.0

    def test_project_2d_to_25d_with_exaggeration(self, service, section_line, sample_polygon_2d):
        """Test projection with vertical exaggeration reversal."""
        crs = MagicMock()
        # Profil showing elev 60, but exaggeration is 2.0 -> Real elev is 30.
        result = service.project_2d_to_25d(sample_polygon_2d, section_line, crs, vertical_exag=2.0)
        
        ring = result.geometry.constGet().exteriorRing()
        p1 = ring.pointN(0)
        assert p1.m() == 30.0 # 60 / 2.0

    def test_invalid_inputs(self, service, section_line, sample_polygon_2d):
        """Test error handling for invalid inputs."""
        crs = MagicMock()
        
        # Null geometry
        with pytest.raises(ValidationError, match="Invalid section line geometry"):
            service.project_2d_to_25d(sample_polygon_2d, QgsGeometry(), crs)
            
        # Empty vertices
        sample_polygon_2d.vertices_2d = []
        with pytest.raises(ValidationError, match="Interpretation has no vertices"):
            service.project_2d_to_25d(sample_polygon_2d, section_line, crs)
