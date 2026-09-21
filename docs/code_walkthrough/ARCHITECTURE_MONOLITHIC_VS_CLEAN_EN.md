# SecInterp Architecture: Monolithic vs Clean Architecture Comparison

> **Technical Analysis: Why SecInterp Moved Away from Traditional QGIS Plugin Patterns**
> Version 3.8.0 | Last Updated: 2026-09-20

---

## Executive Summary

SecInterp **does not follow** the traditional monolithic QGIS plugin pattern. Since version 3.0+, it implements **Clean Architecture (Hexagonal/Ports & Adapters)** with strict **Core/GUI separation**. This document explains the differences, rationale, and practical implications.

---

## 1. Traditional QGIS Plugin (Monolithic Pattern)

### Typical Structure
```
my_plugin/
├── __init__.py
├── my_plugin.py              # Plugin entry point
├── my_plugin_dialog.py       # 2000+ lines: UI + Logic mixed
├── my_plugin_dialog_base.ui  # Qt Designer file
└── resources.py
```

### Code Characteristics

```python
# ❌ TYPICAL MONOLITHIC PLUGIN - my_plugin_dialog.py

class MyPluginDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setup_ui()
        self.connect_signals()

    def connect_signals(self):
        self.btn_process.clicked.connect(self.process_data)

    def process_data(self):
        # QGIS DEPENDENCIES EVERYWHERE IN BUSINESS LOGIC
        layer = QgsProject.instance().mapLayersByName("geology")[0]
        dem_layer = QgsProject.instance().mapLayersByName("dem")[0]

        # PROCESSING MIXED WITH QGIS API CALLS
        results = []
        for feat in layer.getFeatures():
            geom = feat.geometry()           # QGIS Geometry
            attrs = feat.attributes()        # QGIS Attributes
            profile = self.extract_profile(dem_layer, geom)  # More QGIS
            intersections = self.calculate_intersections(geom) # Logic + QGIS

            # DIRECT GUI MANIPULATION IN LOGIC
            self.progress_bar.setValue(i)
            QApplication.processEvents()     # UI blocking workaround

            results.append(self.create_output_feature(intersections))

        # DIRECT LAYER CREATION IN LOGIC
        output_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "results", "memory")
        provider = output_layer.dataProvider()
        provider.addFeatures(results)
        QgsProject.instance().addMapLayer(output_layer)

        # CANVAS REFRESH IN LOGIC
        self.iface.mapCanvas().refresh()
        self.status_bar.showMessage("Done!")

    def extract_profile(self, dem_layer, geometry):
        # QGIS RASTER API MIXED WITH ALGORITHM
        provider = dem_layer.dataProvider()
        # ... sampling logic intertwined with QGIS calls
        return samples

    def calculate_intersections(self, geometry):
        # PURE LOGIC POLLUTED WITH QGIS
        layer = QgsProject.instance().mapLayersByName("structures")[0]
        for feat in layer.getFeatures():
            if geometry.intersects(feat.geometry()):  # QGIS Geometry ops
                # ... calculation
        return results

    def create_output_feature(self, data):
        feat = QgsFeature()  # QGIS Feature
        feat.setGeometry(QgsGeometry.fromWkt(data.wkt))  # QGIS Geometry
        feat.setAttributes(data.attrs)
        return feat
```

### Problems with This Approach

| Problem | Impact |
|---------|--------|
| **Untestable without QGIS** | Requires full QGIS environment, `xvfb`, slow CI |
| **UI blocks during processing** | `QApplication.processEvents()` hacks, frozen UI |
| **Impossible to reuse logic** | Coupled to `QgsFeature`, `QgsGeometry`, `QgsProject` |
| **Single point of failure** | Change in UI breaks logic; change in QGIS API breaks both |
| **No parallelism** | Everything runs on main thread |
| **Technical debt accumulates** | 5000+ line dialog classes common |
| **QGIS version migration painful** | All files touch QGIS API |

---

## 2. SecInterp Clean Architecture (Current)

### Structure
```
sec_interp/
├── core/                    # ⚙️ PURE PYTHON - Zero QGIS
│   ├── interfaces/          # Contracts (ABCs)
│   ├── services/            # Business logic implementations
│   ├── domain/              # DTOs, Entities (dataclasses)
│   ├── validation/          # Validation pipeline
│   └── utils/               # Pure utilities
│
├── gui/                     # 🖥️ QGIS-DEPENDENT LAYER
│   ├── main_dialog.py       # Orchestrates managers only
│   ├── managers/            # 10 specialized managers
│   ├── tasks/               # QgsTask background workers
│   ├── renderers/           # Canvas rendering
│   └── tools/               # QgsMapTool implementations
│
└── exporters/               # 📤 Format-specific output
```

### Code Characteristics

#### Core Layer (Zero QGIS Imports)
```python
# ✅ SECINTERP CORE - core/services/geology_service.py
# NO: from qgis.core import *
# YES: Pure Python, type hints, dataclasses

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from core.interfaces.geology_interface import IGeologyService
from core.domain import ProfileData, GeologySegment
from core.exceptions import ValidationError


@dataclass(frozen=True)
class IntersectionResult:
    """Immutable result - no QGIS types."""
    segment: GeologySegment
    intersection_point: tuple[float, float]  # (x, y) tuples, not QgsPoint
    confidence: float


class GeologyService(IGeologyService):
    """Pure business logic - testable without QGIS."""

    def __init__(self, tolerance: float = 0.001):
        self.tolerance = tolerance

    def calculate_intersections(
        self,
        profile: ProfileData,
        geology_units: List[GeologyUnit]
    ) -> List[IntersectionResult]:
        """
        Pure algorithm - only WKT strings, tuples, primitives.
        Zero QGIS dependencies.
        """
        results = []
        profile_line = wkt_to_shapely(profile.geometry_wkt)

        for unit in geology_units:
            polygon = wkt_to_shapely(unit.geometry_wkt)
            intersection = profile_line.intersection(polygon)

            if not intersection.is_empty:
                results.append(IntersectionResult(
                    segment=GeologySegment(
                        geometry=shapely_to_wkt(intersection),
                        properties=unit.properties
                    ),
                    intersection_point=(intersection.x, intersection.y),
                    confidence=self._calculate_confidence(intersection)
                ))

        return results

    def _calculate_confidence(self, geom) -> float:
        # Pure math - no QGIS
        return min(1.0, geom.length / self.tolerance)
```

#### GUI Layer (Extract → Compute → Present)
```python
# ✅ SECINTERP GUI - gui/dialog_preview_manager.py
# QGIS imports ALLOWED here - this is the adapter layer

from __future__ import annotations
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry
from qgis.gui import QgsMapCanvas
from PyQt5.QtCore import QObject, pyqtSignal

from core.interfaces import IPreviewService, IGeologyService
from core.domain import ProfileData, GeologyUnit
from gui.tasks.geology_task import GeologyTask


class PreviewManager(QObject):
    """Extracts QGIS data → DTOs → Calls Core → Presents results."""

    preview_ready = pyqtSignal(object)  # Emits RenderDTO

    def __init__(self, canvas: QgsMapCanvas, preview_service: IPreviewService,
                 geology_service: IGeologyService):
        super().__init__()
        self.canvas = canvas
        self.preview_service = preview_service
        self.geology_service = geology_service

    def generate_preview(self, profile_layer: QgsVectorLayer,
                         geology_layer: QgsVectorLayer):
        """
        EXTRACT: QGIS → DTOs (only place QGIS types appear)
        """
        profile_dto = self._extract_profile(profile_layer)
        geology_dtos = self._extract_geology_units(geology_layer)

        # COMPUTE: Delegate to Core via Interface (async via QgsTask)
        task = GeologyTask(
            profile=profile_dto,
            geology_units=geology_dtos,
            service=self.geology_service
        )
        task.result_ready.connect(self._on_core_result)
        QgsApplication.taskManager().addTask(task)

    def _extract_profile(self, layer: QgsVectorLayer) -> ProfileData:
        """Extract QGIS data into pure DTO."""
        feat = next(layer.getFeatures())
        return ProfileData(
            geometry_wkt=feat.geometry().asWkt(),  # QGIS → WKT string
            crs=layer.crs().authid(),
            sampling_distance=self.settings.sampling_distance
        )

    def _extract_geology_units(self, layer: QgsVectorLayer) -> List[GeologyUnit]:
        """Extract QGIS features into pure DTOs."""
        units = []
        for feat in layer.getFeatures():
            units.append(GeologyUnit(
                geometry_wkt=feat.geometry().asWkt(),  # QGIS → WKT
                properties=dict(feat.attributes()),
                unit_id=feat.id()
            ))
        return units

    def _on_core_result(self, results: List[IntersectionResult]):
        """
        PRESENT: Core DTOs → QGIS Visualization
        """
        # Convert Core results to QGIS memory layers for display
        render_dto = self.preview_service.prepare_render_data(results)
        self._create_preview_layers(render_dto)
        self.preview_ready.emit(render_dto)

    def _create_preview_layers(self, render_dto: RenderDTO):
        """Only place where QgsFeature/QgsGeometry are created."""
        layer = QgsVectorLayer("LineString?crs=" + render_dto.crs, "preview", "memory")
        provider = layer.dataProvider()

        for segment in render_dto.segments:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromWkt(segment.geometry_wkt))
            feat.setAttributes(segment.properties)
            provider.addFeature(feat)

        QgsProject.instance().addMapLayer(layer)
        self.canvas.refresh()
```

#### Dependency Injection (Controller)
```python
# ✅ SECINTERP CORE - core/controller.py
# Orchestrates services via interfaces

from __future__ import annotations
from core.interfaces import (
    IProfileService, IGeologyService, IDrillholeService,
    IExportService, IPreviewService
)
from core.services import (
    ProfileService, GeologyService, DrillholeService,
    ExportService, PreviewService
)


class ProfileController:
    """Central orchestrator - only knows interfaces."""

    def __init__(
        self,
        profile_service: IProfileService = None,
        geology_service: IGeologyService = None,
        drillhole_service: IDrillholeService = None,
        export_service: IExportService = None,
        preview_service: IPreviewService = None
    ):
        # Dependency Injection - easy to mock in tests
        self.profile_service = profile_service or ProfileService()
        self.geology_service = geology_service or GeologyService()
        self.drillhole_service = drillhole_service or DrillholeService()
        self.export_service = export_service or ExportService()
        self.preview_service = preview_service or PreviewService()

    def process_section(self, profile_dto: ProfileData) -> SectionResult:
        # Pure orchestration - no QGIS, no logic
        topography = self.profile_service.extract_topography(profile_dto)
        geology = self.geology_service.calculate_intersections(topography)
        drillholes = self.drillhole_service.project_to_section(profile_dto)
        return SectionResult(topography, geology, drillholes)
```

---

## 3. Detailed Comparison Matrix

| Dimension | Monolithic Plugin | SecInterp Clean Architecture |
|-----------|-------------------|------------------------------|
| **File Organization** | 1-3 large files | 121 focused modules |
| **Max File Size** | 2000-5000 lines | <300 lines (enforced) |
| **QGIS Imports** | Everywhere | Only in `gui/`, `exporters/` |
| **Core Logic Location** | Mixed in dialog | `core/services/` |
| **Data Types in Logic** | `QgsFeature`, `QgsGeometry` | WKT strings, tuples, dataclasses |
| **Testing** | Integration only (slow) | Unit (core) + Integration (gui) |
| **Test Speed** | 30-60 seconds | <5 seconds (core unit tests) |
| **Threading** | Main thread + `processEvents()` | `QgsTask` background workers |
| **UI Responsiveness** | Freezes during computation | Never blocks (async tasks) |
| **Mocking in Tests** | Difficult/impossible | Trivial (interfaces + BaseTestCase) |
| **QGIS 3→4 Migration** | Rewrite entire plugin | Only `gui/` + `exporters/` |
| **Logic Reuse** | Copy-paste | Import `core` in any Python app |
| **Parallel Development** | UI dev blocks logic dev | UI & Core developed independently |
| **Onboarding** | "Read the 3000-line dialog" | "Read interface + one service" |

---

## 4. Data Flow: Extract-then-Compute Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER ACTION                                  │
│                    (clicks "Generate Preview")                      │
└────────────────────────────┬────────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GUI LAYER - EXTRACT PHASE                                           │
│  dialog_preview_manager.py                                          │
│  ├── Gets QgsVectorLayer from QGIS                                  │
│  ├── Iterates features: feat.geometry().asWkt()                    │
│  ├── Builds ProfileData, GeologyUnit DTOs (dataclasses)            │
│  └── NO BUSINESS LOGIC HERE - only extraction                       │
└────────────────────────────┬────────────────────────────────────────┘
                             ▼ DTOs (pure Python)
┌─────────────────────────────────────────────────────────────────────┐
│ CORE LAYER - COMPUTE PHASE (Background Thread via QgsTask)         │
│  tasks/geology_task.py → GeologyService.calculate_intersections()  │
│  ├── Receives: ProfileData, List[GeologyUnit]                      │
│  ├── Uses: Shapely, NumPy, pure Python algorithms                  │
│  ├── Zero QGIS imports - thread-safe                               │
│  └── Returns: List[IntersectionResult] (DTOs)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             ▼ DTOs (pure Python)
┌─────────────────────────────────────────────────────────────────────┐
│ GUI LAYER - PRESENT PHASE                                           │
│  dialog_preview_manager.py._on_core_result()                       │
│  ├── Receives Core DTOs                                            │
│  ├── Calls PreviewService.prepare_render_data()                    │
│  ├── Creates QgsVectorLayer, QgsFeature for visualization          │
│  ├── Adds to QgsProject, refreshes canvas                          │
│  └── Emits signal for UI update                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Testing Strategy Comparison

### Monolithic Plugin Testing
```python
# ❌ MONOLITHIC - Requires QGIS, slow, fragile
class TestMyPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Need full QGIS initialization
        from qgis.testing import start_app
        start_app()
        cls.iface = get_qgis_iface()

    def test_process_data(self):
        # Load real layers, real project
        layer = QgsVectorLayer("test_data/geology.gpkg", "geology", "ogr")
        QgsProject.instance().addMapLayer(layer)

        dialog = MyPluginDialog(self.iface)
        dialog.process_data()  # Runs on main thread!

        # Check QGIS project state
        output = QgsProject.instance().mapLayersByName("results")[0]
        self.assertEqual(output.featureCount(), 10)
```

### SecInterp Testing (Mock-First)
```python
# ✅ SECINTERP CORE - No QGIS, fast, isolated
class TestGeologyService(BaseTestCase):  # Inherits mock injection
    def setUp(self):
        super().setUp()
        self.service = GeologyService(tolerance=0.001)

    def test_calculate_intersections_valid(self):
        # Pure DTOs - no QGIS
        profile = ProfileData(
            geometry_wkt="LINESTRING(0 0, 100 0)",
            crs="EPSG:4326",
            sampling_distance=10
        )
        units = [GeologyUnit(
            geometry_wkt="POLYGON((50 -10, 50 10, 60 10, 60 -10, 50 -10))",
            properties={"unit_name": "Sandstone"},
            unit_id=1
        )]

        results = self.service.calculate_intersections(profile, units)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].segment.properties["unit_name"], "Sandstone")
        self.assertAlmostEqual(results[0].intersection_point[0], 50, places=1)

# ✅ SECINTERP GUI - With QGIS mocks (BaseTestCase provides)
class TestPreviewManager(BaseTestCase):
    def test_generate_preview_calls_core(self):
        # Mock Core services
        mock_geology = self.mock_core.geology_service
        mock_geology.calculate_intersections.return_value = [
            IntersectionResult(...)
        ]

        manager = PreviewManager(canvas=self.mock_canvas,
                                 preview_service=self.mock_preview,
                                 geology_service=mock_geology)

        manager.generate_preview(self.mock_profile_layer, self.mock_geology_layer)

        # Verify Core was called with correct DTOs
        mock_geology.calculate_intersections.assert_called_once()
        args = mock_geology.calculate_intersections.call_args[0]
        self.assertIsInstance(args[0], ProfileData)
```

---

## 6. Migration Path: From Monolithic to Clean

### If You Have a Monolithic Plugin Today

| Phase | Action | Files Affected |
|-------|--------|----------------|
| **1. Extract DTOs** | Create `core/domain/` with dataclasses for all data structures | New: `core/domain/` |
| **2. Define Interfaces** | Create `core/interfaces/` ABCs for each service | New: `core/interfaces/*.py` |
| **3. Move Logic** | Move algorithms to `core/services/` implementing interfaces | Move: dialog logic → `core/services/` |
| **4. Remove QGIS from Core** | Replace `QgsGeometry` → WKT, `QgsFeature` → dict/dataclass | Edit: `core/services/*.py` |
| **5. Create GUI Managers** | Split dialog into specialized managers | New: `gui/*_manager.py` |
| **6. Wire DI** | Create `ProfileController` injecting services | New: `core/controller.py` |
| **7. Add QgsTask** | Move heavy ops to background tasks | New: `gui/tasks/*.py` |
| **8. Add Tests** | Unit tests for core, integration for gui | New: `tests/core/`, `tests/gui/` |

### Incremental Migration (Recommended)
```python
# Phase 1: Keep dialog, extract ONE service
class MyPluginDialog(QDialog):
    def process_data(self):
        # OLD: inline logic
        # NEW: delegate to service
        from core.services.geology_service import GeologyService
        service = GeologyService()
        results = service.calculate_intersections(profile_dto, units)
        self.present_results(results)  # Still in dialog
```

---

## 7. When to Use Each Approach

### Use Monolithic If:
- ✅ Simple plugin (<500 lines total)
- ✅ One-time throwaway tool
- ✅ Team has no architecture experience
- ✅ Must ship in 2 days

### Use Clean Architecture If:
- ✅ Plugin >2000 lines or growing
- ✅ Complex geological/scientific algorithms
- ✅ Need for automated testing/CI
- ✅ Multiple developers
- ✅ Long-term maintenance (years)
- ✅ QGIS version upgrades expected
- ✅ Logic may be reused outside QGIS

---

## 8. SecInterp-Specific Benefits Realized

### Performance
- **361+ tests** run in <30 seconds in Docker
- **LOD rendering** handles 100k+ features at 60fps
- **Background processing** keeps UI responsive during 30s+ computations

### Maintainability
- **Zero critical Bandit findings** (security scanner)
- **Zero detect-secrets findings** above baseline
- **Pylint score >9.0** consistently
- **Single responsibility**: each manager/service <300 lines

### Extensibility
- **Added 3D export** without touching Core logic
- **Added drillhole support** via new sub-system
- **Added 10 managers** without modifying existing ones

### Team Velocity
- **Backend dev** works on `core/` (no QGIS install needed)
- **Frontend dev** works on `gui/` (mock Core via interfaces)
- **Parallel PRs** without merge conflicts

---

## 9. Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Clean Architecture = Overengineering" | For complex domains, it **reduces** total code via reuse |
| "Interfaces add boilerplate" | They **enable** testing, mocking, parallel dev |
| "DTOs are verbose" | They **document** contracts, catch bugs at compile time |
| "QgsTask is complex" | It's **simpler** than `processEvents()` hacks |
| "Can't use QGIS algorithms" | Core uses **Shapely/NumPy**; GUI wraps QGIS processing |

---

## 10. References

- **Clean Architecture**: Robert C. Martin, *Clean Architecture* (2017)
- **Hexagonal Architecture**: Alistair Cockburn, *Ports and Adapters* (2005)
- **QGIS Plugin Best Practices**: [QGIS Plugin Development](https://docs.qgis.org/)
- **SecInterp Codebase**: `/core`, `/gui`, `/exporters`, `/tests`
- **Project Standards**: `AGENTS.md`, `.agent/skills/coding-standards/`

---

## Appendix: Quick Reference - Where Things Live

| Need to... | Go to... |
|------------|----------|
| Add new geological algorithm | `core/services/geology_service.py` |
| Add new export format | `exporters/` (inherit `BaseExporter`) |
| Modify UI layout | `gui/ui/pages/` |
| Change how layers are validated | `core/validation/layer_validator.py` |
| Add new map tool | `gui/tools/` |
| Fix rendering bug | `gui/renderers/` |
| Add background processing | `gui/tasks/` |
| Change data structure | `core/domain/` |
| Modify settings persistence | `gui/dialog_settings_persistence.py` |

---

*Document maintained as part of SecInterp architecture documentation.*
*See also: `ARCHITECTURE_EN.md`, `CORE_DISTINCTION_GUIDE_EN.md`, `ARCHITECTURE.mmd`*
