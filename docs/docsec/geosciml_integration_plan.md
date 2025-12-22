# GeoSciML Integration Plan for SecInterp

## Overview

This document outlines the implementation strategy for adding GeoSciML (Geoscience Markup Language) export capabilities to the SecInterp QGIS plugin, enabling standardized geological data exchange.

## Goals

1. Export geological cross-section interpretations in GeoSciML 4.1 format
2. Support basic geological units and structural features
3. Integrate with existing export infrastructure
4. Maintain backward compatibility with current Shapefile exports

## Phase 1: Foundation (v2.3.0)

### 1.1 Research & Dependencies

**Tasks:**
- Study GeoSciML 4.1 specification (http://www.geosciml.org/)
- Evaluate Python XML libraries (lxml vs xml.etree)
- Review CGI vocabularies for lithology and structure types
- Analyze OneGeology implementation examples

**Dependencies:**
```python
# Add to requirements.txt
lxml>=4.9.0  # Robust XML generation with namespace support
```

### 1.2 Data Model Mapping

Map SecInterp internal data structures to GeoSciML concepts:

| SecInterp Entity | GeoSciML Class | Priority |
|------------------|----------------|----------|
| Geology segments | `gsml:GeologicUnit` | High |
| Structure measurements | `gsml:ShearDisplacementStructure` | High |
| Drillhole traces | `gsml:Borehole` | Medium |
| Drillhole intervals | `gsml:BoreholeInterval` | Medium |
| Section line | `gsml:GeologicSection` | Low |

### 1.3 Core Exporter Implementation

**New Module:** `exporters/geosciml_exporter.py`

```python
from dataclasses import dataclass
from typing import List, Optional
from lxml import etree
from qgis.core import QgsFeature

@dataclass
class GeoSciMLConfig:
    """Configuration for GeoSciML export."""
    namespace_prefix: str = "gsml"
    version: str = "4.1"
    include_vocabularies: bool = True
    coordinate_system: str = "EPSG:4326"  # WGS84 for interoperability

class GeoSciMLExporter:
    """Export geological data to GeoSciML format."""
    
    def __init__(self, config: GeoSciMLConfig = None):
        self.config = config or GeoSciMLConfig()
        self._setup_namespaces()
    
    def _setup_namespaces(self):
        """Define XML namespaces."""
        self.nsmap = {
            'gsml': 'http://www.opengis.net/gsml/4.1/GeoSciML-Core',
            'gml': 'http://www.opengis.net/gml/3.2',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }
    
    def export_geologic_units(
        self, 
        geology_segments: List[GeologySegment],
        output_path: str
    ) -> bool:
        """Export geology segments as GeologicUnit features."""
        root = self._create_root_collection()
        
        for segment in geology_segments:
            unit = self._create_geologic_unit(segment)
            root.append(unit)
        
        return self._write_xml(root, output_path)
    
    def _create_geologic_unit(self, segment: GeologySegment):
        """Convert a GeologySegment to a gsml:GeologicUnit element."""
        unit = etree.Element(
            f"{{{self.nsmap['gsml']}}}GeologicUnit",
            attrib={f"{{{self.nsmap['gml']}}}id": f"unit_{segment.id}"}
        )
        
        # Add name
        name = etree.SubElement(unit, f"{{{self.nsmap['gml']}}}name")
        name.text = segment.lithology or "Unknown"
        
        # Add composition
        composition = self._create_composition(segment.lithology)
        unit.append(composition)
        
        # Add geometry (2D section trace)
        shape = self._create_geometry(segment.geometry)
        unit.append(shape)
        
        return unit
    
    def _create_composition(self, lithology: str):
        """Create composition element with lithology."""
        comp = etree.Element(f"{{{self.nsmap['gsml']}}}composition")
        part = etree.SubElement(comp, f"{{{self.nsmap['gsml']}}}CompositionPart")
        
        # Link to CGI Simple Lithology vocabulary
        litho = etree.SubElement(part, f"{{{self.nsmap['gsml']}}}lithology")
        litho.set(f"{{{self.nsmap['xsi']}}}href", 
                  f"http://resource.geosciml.org/classifier/cgi/lithology/{lithology.lower()}")
        
        return comp
    
    def _create_geometry(self, qgs_geometry):
        """Convert QGIS geometry to GML."""
        shape = etree.Element(f"{{{self.nsmap['gsml']}}}shape")
        
        # Convert to GML LineString or Polygon
        gml_geom = self._qgs_to_gml(qgs_geometry)
        shape.append(gml_geom)
        
        return shape
    
    def _qgs_to_gml(self, qgs_geometry):
        """Convert QgsGeometry to GML representation."""
        # Simplified - full implementation would handle all geometry types
        coords = qgs_geometry.asPolyline()
        
        linestring = etree.Element(f"{{{self.nsmap['gml']}}}LineString")
        pos_list = etree.SubElement(linestring, f"{{{self.nsmap['gml']}}}posList")
        
        # Format: x1 y1 x2 y2 ...
        pos_list.text = " ".join(f"{pt.x()} {pt.y()}" for pt in coords)
        
        return linestring
    
    def _create_root_collection(self):
        """Create root FeatureCollection element."""
        root = etree.Element(
            f"{{{self.nsmap['gsml']}}}GSML",
            nsmap=self.nsmap
        )
        root.set(
            f"{{{self.nsmap['xsi']}}}schemaLocation",
            "http://www.opengis.net/gsml/4.1/GeoSciML-Core "
            "http://schemas.opengis.net/gsml/4.1/geosciml.xsd"
        )
        return root
    
    def _write_xml(self, root, output_path: str) -> bool:
        """Write XML tree to file with pretty formatting."""
        try:
            tree = etree.ElementTree(root)
            tree.write(
                output_path,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to write GeoSciML: {e}")
            return False
```

### 1.4 Integration with Export System

**Modify:** `exporters/__init__.py`

```python
def get_exporter(format_type: str, **kwargs):
    """Factory function for exporters."""
    exporters = {
        'csv': CSVExporter,
        'shp': ShapefileExporter,
        'geosciml': GeoSciMLExporter,  # NEW
    }
    # ... rest of implementation
```

**Modify:** `gui/main_dialog_export.py`

Add GeoSciML option to export format dropdown:

```python
def _setup_export_formats(self):
    """Populate export format combo."""
    formats = [
        ("Shapefile (*.shp)", "shp"),
        ("CSV (*.csv)", "csv"),
        ("GeoSciML (*.xml)", "geosciml"),  # NEW
    ]
    # ...
```

## Phase 2: Enhanced Features (v2.4.0)

### 2.1 Vocabulary Integration

- Implement CGI Simple Lithology mapper
- Add age/chronostratigraphy support
- Support custom vocabulary extensions

### 2.2 Structural Features

Export structural measurements as:
- `gsml:ShearDisplacementStructure` (faults)
- `gsml:Foliation` (planar structures)
- `gsml:Fold` (if interpreted)

### 2.3 Metadata Enrichment

Add support for:
- Observer information
- Observation method
- Quality/confidence indicators
- Source references

## Phase 3: Advanced Integration (v2.5.0)

### 3.1 WFS Publishing

- Generate WFS-compatible GeoSciML
- Add QGIS Server integration guide
- Support for GetFeature requests

### 3.2 Import Capabilities

- Parse GeoSciML from external sources
- Import from OneGeology WFS services
- Merge with local interpretations

## Testing Strategy

### Unit Tests

```python
# tests/test_geosciml_exporter.py
def test_export_simple_unit():
    """Test basic GeologicUnit export."""
    segment = GeologySegment(
        id=1,
        lithology="granite",
        geometry=create_test_linestring()
    )
    
    exporter = GeoSciMLExporter()
    success = exporter.export_geologic_units([segment], "/tmp/test.xml")
    
    assert success
    assert validate_geosciml("/tmp/test.xml")
```

### Integration Tests

- Export real cross-section data
- Validate against GeoSciML XSD schema
- Test import into GeoServer/MapServer

## Documentation Requirements

1. **User Guide Section**: "Exporting to GeoSciML"
2. **API Documentation**: Full docstrings for new classes
3. **Tutorial**: Step-by-step example with sample data
4. **Vocabulary Guide**: Mapping local terms to CGI vocabularies

## Success Criteria

- [ ] Export geological units to valid GeoSciML 4.1 XML
- [ ] Pass XSD schema validation
- [ ] Successfully import into QGIS from exported file
- [ ] Compatible with OneGeology portal requirements
- [ ] Performance: Export 1000 features in < 5 seconds

## Resources

- **GeoSciML Specification**: http://www.geosciml.org/
- **CGI Vocabularies**: http://resource.geosciml.org/
- **OneGeology Cookbook**: http://onegeology.org/docs/technical/
- **INSPIRE Geology Guidelines**: https://inspire.ec.europa.eu/

## Timeline Estimate

- **Phase 1 (Basic Export)**: 3-4 weeks
- **Phase 2 (Enhanced Features)**: 2-3 weeks
- **Phase 3 (Advanced)**: 4-6 weeks

**Total**: ~10-13 weeks for full implementation

---

*Created: 2025-12-22*  
*Target Version: 2.3.0 (Phase 1)*
