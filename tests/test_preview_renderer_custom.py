
import pytest
from qgis.core import QgsVectorLayer, QgsGeometry
from sec_interp.gui.preview_renderer import PreviewRenderer

@pytest.fixture
def renderer():
    return PreviewRenderer()

def test_create_struct_layer_custom_length(renderer):
    """Test that _create_struct_layer uses the custom dip_line_length."""
    # Setup data: 1 point at dist=0, dip=45
    struct_data = [(0.0, 45.0)]
    reference_data = [(0.0, 100.0), (100.0, 200.0)]
    
    # Custom length
    custom_length = 50.0
    
    layer = renderer._create_struct_layer(
        struct_data, reference_data, vert_exag=1.0, dip_line_length=custom_length
    )
    
    assert layer is not None
    assert layer.featureCount() == 1
    
    feat = next(layer.getFeatures())
    geom = feat.geometry()
    
    # Check length of the line
    # Dip is 45 degrees, length should be 50.0
    # Line is from (0, 100) to (dx, 100-dy)
    # dx = 50 * cos(45) ~ 35.35
    # dy = 50 * sin(45) ~ 35.35
    
    length = geom.length()
    assert abs(length - custom_length) < 0.001

def test_create_struct_layer_default_length(renderer):
    """Test that _create_struct_layer uses default length when custom is None."""
    struct_data = [(0.0, 45.0)]
    # Range 100, default length should be 10% = 10.0
    reference_data = [(0.0, 100.0), (100.0, 200.0)] 
    
    layer = renderer._create_struct_layer(
        struct_data, reference_data, vert_exag=1.0, dip_line_length=None
    )
    
    assert layer is not None
    feat = next(layer.getFeatures())
    length = feat.geometry().length()
    
    assert abs(length - 10.0) < 0.001
