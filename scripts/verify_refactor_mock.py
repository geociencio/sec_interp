import sys
import os
from unittest.mock import MagicMock, Mock

# --- Fix Sys Path ---
# Add parent directory to path so we can import 'sec_interp' as a package
sys.path.insert(0, os.path.dirname(os.getcwd()))

# --- Mock QGIS Environment ---
# We must mock qgis BEFORE importing any project modules
mock_qgis = MagicMock()
mock_core = MagicMock()
mock_gui = MagicMock()
mock_pyqt = MagicMock()
mock_processing = MagicMock()

sys.modules["qgis"] = mock_qgis
sys.modules["qgis.core"] = mock_core
sys.modules["qgis.gui"] = mock_gui
sys.modules["qgis.PyQt"] = mock_pyqt
sys.modules["qgis.PyQt.QtCore"] = MagicMock()
sys.modules["qgis.PyQt.QtGui"] = MagicMock()
sys.modules["qgis.PyQt.QtWidgets"] = MagicMock()
sys.modules["qgis.processing"] = mock_processing
# Also mock the top-level import "from qgis import processing"
mock_qgis.processing = mock_processing

# Mock scu to avoid complex geometry logic
mock_scu = MagicMock()
sys.modules["sec_interp.core.utils"] = mock_scu
# Need to ensure internal imports of scu don't fail if they import specific things
sys.modules["sec_interp.core.utils.sampling"] = mock_scu
sys.modules["sec_interp.core.utils.geometry"] = mock_scu

# Mock specific classes used by types and services
class MockQgsPointXY:
    def __init__(self, x, y):
        self.x_val = x
        self.y_val = y
    def x(self): return self.x_val
    def y(self): return self.y_val

class MockQgsGeometry:
    def lineLocatePoint(self, other):
        return 100.0 # Mock distance
    def interpolate(self, dist):
        # interpolate returns a Geometry (point)
        return MockQgsGeometry() # Mock point geometry
    def asPoint(self):
        return MockQgsPointXY(123.0, 456.0)
    def intersects(self, other):
        return True
    def isNull(self):
        return False
    def length(self):
        return 500.0
    def isMultipart(self):
        return False
    def asPolyline(self):
        return [MockQgsPointXY(0,0), MockQgsPointXY(10,10)]
    def wkbType(self):
        return 2 # LineString

class MockQgsRasterLayer:
    def dataProvider(self):
        return self
    def identify(self, point, format):
        mock_result = MagicMock()
        mock_result.results.return_value = {1: 50.0} # Mock elevation
        return mock_result
    def rasterUnitsPerPixelX(self):
        return 1.0

class MockQgsFeature:
    def __init__(self, attributes=None, geometry=None):
        self.attrs = attributes or {}
        self.geom = geometry or MockQgsGeometry()
        self._fields = MagicMock()
        self._fields.names.return_value = list(self.attrs.keys())
    
    def geometry(self):
        return self.geom
    
    def attributes(self):
        return list(self.attrs.values())
    
    def fields(self):
        return self._fields
    
    def __getitem__(self, key):
        if key not in self.attrs:
            raise KeyError(key)
        return self.attrs[key]

# Setup Core Mocks
mock_core.QgsPointXY = MockQgsPointXY
mock_core.QgsGeometry = MockQgsGeometry
mock_core.QgsRasterLayer = MockQgsRasterLayer
mock_core.QgsFeature = MockQgsFeature
mock_core.QgsRaster = MagicMock()
mock_core.QgsRaster.IdentifyFormatValue = 1
mock_core.QgsWkbTypes = MagicMock()
mock_core.QgsWkbTypes.LineString = 2
mock_core.QgsWkbTypes.LineString25D = 2147483650
mock_core.QgsWkbTypes.MultiLineString = 5
mock_core.QgsWkbTypes.MultiLineString25D = 2147483653

# --- Import Project Modules ---
# Now importing should work
# Note: scu is already mocked in sys.modules, so imports in services will get the mock
from sec_interp.core.types import StructureMeasurement, GeologySegment
from sec_interp.core.services.structure_service import StructureService
from sec_interp.core.services.geology_service import GeologyService

# --- Verification Tests ---

def test_structure_service():
    print("Testing StructureService...")
    
    # Configure SCU Mocks specifically for StructureService
    mock_scu.calculate_line_azimuth.return_value = 45.0
    mock_scu.parse_dip.return_value = (45.0, "")
    mock_scu.parse_strike.return_value = 90.0
    mock_scu.calculate_apparent_dip.return_value = 30.0
    # measureLine used in service? No, logic uses lineLocatePoint etc directly or via da
    # The refined service uses lineLocatePoint then interpolate then da.measureLine?
    # No, it uses lineLocatePoint which returns distance along line.
    # Ah, lines 442 in algorithms call struct service.
    # Service calls: scu.prepare_profile_context(line_lyr) -> line_geom, start, da
    mock_da = MagicMock()
    mock_da.measureLine.return_value = 150.0 # Mock projected distance
    mock_scu.prepare_profile_context.return_value = (MockQgsGeometry(), MockQgsPointXY(0,0), mock_da)
    mock_scu.create_buffer_geometry.return_value = MockQgsGeometry()
    
    service = StructureService()
    
    # Mock inputs
    line_layer = MagicMock()
    line_feat = MockQgsFeature(geometry=MockQgsGeometry())
    line_layer.getFeatures.return_value = iter([line_feat])
    
    raster_layer = MockQgsRasterLayer()
    
    struct_layer = MagicMock()
    struct_feat = MockQgsFeature(
        attributes={"dip": 45, "strike": 90, "type": "fault"},
        geometry=MockQgsGeometry()
    )
    struct_layer.getFeatures.return_value = iter([struct_feat])
    
    # Mock filter return
    mock_scu.filter_features_by_buffer.return_value = [struct_feat]
    
    # Debug
    print(f"Debug: line_feat type: {type(line_feat)}")
    print(f"Debug: line_feat geometry type: {type(line_feat.geometry())}")
    print(f"Debug: line_feat geometry isNull: {line_feat.geometry().isNull()}")
    
    # Run
    results = service.project_structures(
        line_lyr=line_layer,
        raster_lyr=raster_layer,
        struct_lyr=struct_layer,
        buffer_m=20,
        line_az=0,
        dip_field="dip",
        strike_field="strike",
        band_number=1
    )
    
    # Verify
    if not results:
        print("FAIL: No results returned")
        return
        
    first = results[0]
    print(f"Result type: {type(first)}")
    if isinstance(first, StructureMeasurement):
        print("PASS: Returns StructureMeasurement objects")
    else:
        print(f"FAIL: Returns {type(first)}")
        
    print(f"Attributes: {first.attributes}")
    if first.attributes["type"] == "fault":
        print("PASS: Attributes preserved")
    else:
        print("FAIL: Attributes lost")
        
    print(f"Elevation: {first.elevation}")
    if first.elevation == 50.0:
        print("PASS: Elevation sampled correct")
    else:
        print(f"FAIL: Elevation is {first.elevation}")

def test_geology_service():
    print("\nTesting GeologyService...")
    
    # Configure SCU Mocks for GeologyService
    mock_da = MagicMock()
    # measureLine used for start/end distances
    mock_da.measureLine.side_effect = [0.0, 10.0, 0.0, 100.0, 200.0] # Sequence of calls
    mock_scu.create_distance_area.return_value = mock_da
    
    # densify_line_by_interval -> geom
    mock_scu.densify_line_by_interval.return_value = MockQgsGeometry()
    # get_line_vertices -> list of points
    mock_scu.get_line_vertices.return_value = [MockQgsPointXY(0,0), MockQgsPointXY(10,10)]
    
    # interpolation utils
    # interpolate_elevation imported from sec_interp.core.utils.sampling (which is mock_scu)
    mock_scu.interpolate_elevation.return_value = 75.0
    
    service = GeologyService()
    
    # Mock inputs
    line_layer = MagicMock()
    line_feat = MockQgsFeature(geometry=MockQgsGeometry())
    line_layer.getFeatures.return_value = iter([line_feat])
    
    raster_layer = MockQgsRasterLayer()
    
    outcrop_layer = MagicMock()
    
    # Mock processing result
    # It returns a dict {"OUTPUT": layer}
    # Create a mock intersection layer with features
    intersection_layer = MagicMock()
    
    # Feature needs geometry and attributes
    inter_feat = MockQgsFeature(
        attributes={"unit_name": "Granite", "other": 1},
        geometry=MockQgsGeometry()
    )
    intersection_layer.getFeatures.return_value = iter([inter_feat])
    
    mock_processing.run.return_value = {"OUTPUT": intersection_layer}
    
    # Run
    results = service.generate_geological_profile(
        line_lyr=line_layer,
        raster_lyr=raster_layer,
        outcrop_lyr=outcrop_layer,
        outcrop_name_field="unit_name",
        band_number=1
    )
    
    # Verify
    if not results:
        print("FAIL: No results returned")
        return
        
    print(f"Result count: {len(results)}")
    first = results[0]
    print(f"Result type: {type(first)}")
    if isinstance(first, GeologySegment):
        print("PASS: Returns GeologySegment objects")
    else:
        print(f"FAIL: Returns {type(first)}")
    
    print(f"Unit Name: {first.unit_name}")
    if first.unit_name == "Granite":
        print("PASS: Unit name correct")
    else:
        print(f"FAIL: Unit name is {first.unit_name}")

    print(f"Points: {first.points}")
    if len(first.points) > 0:
        print("PASS: Points populated")
    else:
        print("FAIL: Points empty")

if __name__ == "__main__":
    try:
        test_structure_service()
        test_geology_service()
    except Exception as e:
        print(f"CRITICAL FAIL: {e}")
        import traceback
        traceback.print_exc()
