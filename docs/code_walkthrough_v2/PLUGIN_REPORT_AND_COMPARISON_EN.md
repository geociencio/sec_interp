# SecInterp — Comprehensive Plugin Report & Competitive Analysis

> **Technical Report: Features, Architecture, and Market Comparison**
> SecInterp v3.10.0 | Report Date: 2026-10-11

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Plugin Identity](#2-plugin-identity)
3. [Feature Inventory](#3-feature-inventory)
4. [Technical Architecture](#4-technical-architecture)
5. [Quality Metrics](#5-quality-metrics)
6. [Competitive Landscape](#6-competitive-landscape)
7. [Comparative Analysis Matrix](#7-comparative-analysis-matrix)
8. [Differentiators & Positioning](#8-differentiators--positioning)
9. [Target Users & Use Cases](#9-target-users--use-cases)
10. [Strengths, Weaknesses, Opportunities, Threats](#10-swot-analysis)
11. [Roadmap & Future Direction](#11-roadmap--future-direction)
12. [Conclusion](#12-conclusion)
13. [References](#13-references)

---

## 1. Executive Summary

**SecInterp** (Section Interpreter) is a professional-grade QGIS plugin for geological cross-section interpretation. Unlike most QGIS geological plugins — which are single-purpose profile generators — SecInterp offers an **integrated workflow** spanning topography extraction, geological outcrop projection, structural analysis, **3D drillhole desurveying and projection**, interactive interpretation digitizing, and multi-format CAD-ready export.

Its key technical differentiator is a **Clean Architecture implementation** (rare among QGIS plugins) with strict Core/GUI separation, 763 automated tests, 14-language i18n coverage, and full QGIS 4.x/Qt6 readiness.

### At a Glance

| Attribute | Value |
|-----------|-------|
| **Name** | Sec Interp (SecInterp) |
| **Version** | 3.10.0 |
| **Portal downloads** | ~4,640 (portal, 2026-10; adoption proxy, not active use) |
| **Author** | Juan M. Bernales |
| **License** | GPL v3 |
| **QGIS Minimum** | 3.28 LTR |
| **QGIS Maximum** | 4.99 |
| **Repository** | github.com/geociencio/sec_interp |
| **Documentation** | geociencio.github.io/sec_interp_docs |
| **Languages** | 14 (EN, ES, FR, DE, IT, PT_BR, RU, ZH_CN, JA, HI, ID, PL, NL, FI) |
| **Category** | Vector |
| **Tests** | 763 (Docker-verified) |
| **Architecture** | Clean Architecture (Core/GUI separation) |

---

## 2. Plugin Identity

### 2.1 Description

> **SecInterp** is a professional QGIS plugin designed for industrial-grade extraction and visualization of geological data. It empowers geologists to generate high-fidelity topographic profiles, project outcrops with structural integrity, and perform complex 3D drillhole analysis within a unified 2D cross-section environment.

### 2.2 Core Purpose

SecInterp bridges the gap between **GIS data** (DEMs, geological maps, structural measurements, drillhole databases) and **geological cross-section interpretation**. It automates the tedious data extraction step, freeing geologists to focus on interpretation.

### 2.3 Tags

`geology`, `mining`, `cross-section`, `borehole`, `drillhole`, `exploration`, `topography`, `profile`, `interpretation`, `dem`, `interpolation`, `digitizing`, `snapping`, `structural geology`, `subsurface`, `visualization`

---

## 3. Feature Inventory

### 3.1 Data Extraction

| Feature | Description | Input | Output |
|---------|-------------|-------|--------|
| **Topographic Profile** | Elevation sampling along section line | DEM raster (any band) | 2D profile with elevation |
| **Geological Outcrop Projection** | Intersects polygons with section plane | Polygon layer + lithology field | Colored geological intervals |
| **Structural Projection** | Projects dip/strike measurements | Point layer + dip/strike fields | Structural symbols + apparent dip |
| **Drillhole Desurveying** | 3D trajectory from collar + survey | Collar + Survey + Interval tables | 3D trace, projected to 2D |
| **Drillhole Intervals** | Projects lithology/assay intervals | Interval table + depth fields | Colored intervals along trace |

### 3.2 Visualization & Interaction

| Feature | Description |
|---------|-------------|
| **Real-time Preview** | Asynchronous rendering without UI freeze |
| **Adaptive LOD** | Detail increases on zoom (Douglas-Peucker + curvature) |
| **Parallel Processing** | Multi-threaded geological intersections |
| **Measurement Tool** | Multi-point polyline, 3D distance, slope, elevation change |
| **Vertex Snapping** | `QgsPointLocator`-based snapping (no project pollution) |
| **Interactive Interpretation** | Draw polygons directly on profile view |
| **Undo/Redo** | Right-click undo during interpretation drawing |
| **Auto-Color** | Automatic vivid color assignment for interpretations |
| **Legend Widget** | Dynamic, synchronized legend with visibility toggle |

### 3.3 Structural Geology

| Feature | Description |
|---------|-------------|
| **Dip/Strike Parsing** | Flexible parser for multiple notation formats |
| **Apparent Dip Calculation** | Corrects apparent dip for section orientation |
| **Buffer Zones** | Configurable search radius for structural data |
| **Dip Scale Factor** | Visual exaggeration control |

### 3.4 Drillhole Sub-system (v2.0+)

| Component | Function |
|-----------|----------|
| **Collar Processor** | Validates and transforms collar coordinates |
| **Survey Processor** | Interpolates azimuth/dip along hole |
| **Interval Processor** | Manages lithology/assay intervals |
| **Trajectory Engine** | Minimum curvature / tangential / balanced tangential methods |
| **Projection Engine** | 3D→2D section plane projection |
| **Vertical Hole Support** | Auto-handles vertical holes without survey |
| **Total Depth Calc** | Automatic depth computation |

### 3.5 Export Formats

| Format | 2D | 3D | Purpose |
|--------|:--:|:--:|---------|
| **Shapefile (SHP)** | ✅ | ✅ | GIS interchange |
| **GeoPackage (GPKG)** | ✅ | ✅ | Modern GIS, 3D Z-aware |
| **DXF** | ✅ | — | CAD integration (AutoCAD) |
| **CSV** | ✅ | — | Raw data, spreadsheets |
| **PDF** | ✅ | — | Publication-ready reports |
| **SVG** | ✅ | — | Vector graphics, editing |
| **PNG/JPG** | ✅ | — | Presentations, raster |
| **CityJSON** | — | ✅ | 3D city/geology models |

### 3.6 Internationalization

- **14 languages** with 100% coverage
- Auto-locale detection
- AST-based translation hygiene gate (`MISSING_I18N`)
- Master translation data version-controlled

### 3.7 Configuration & Persistence

- Multi-scope settings (project/global)
- Proactive auto-save on preview/accept
- Layer name fallback restoration
- "Reset to defaults" per section

### 3.8 Insights & Safety (v3.9)

| Feature | Description |
|---------|-------------|
| **DEM Band Statistics** | Read-only min/max/mean/NoData for the selected DEM band (bounded sample). |
| **Profile-vs-DEM Statistics** | Section min/max/mean and sample count at the DEM resolution. |
| **Profile Color Mode** | Gradient (color ramp) or single-color topographic profile styling. |
| **Adaptive Vertical Exaggeration** | Auto VE from profile aspect ratio and structural density (`0.5×–20×`), with manual override. |
| **Smoothed Topography** | Optional distance-window moving-average profile with matching smoothed geology. |
| **CRS Safety** | Mixed-CRS warning and a blocking check for mislabelled layer CRS. |

---

## 4. Technical Architecture

### 4.1 Pattern: Clean Architecture (Core/GUI Separation)

SecInterp is one of the **few QGIS plugins** implementing Clean Architecture:

```
┌─────────────────────────────────────────────────────┐
│  GUI LAYER (gui/)     — QGIS-DEPENDENT              │
│  Managers, Renderers, Tasks, Tools, Adapters        │
│  Extracts QGIS → DTOs, presents DTOs → QGIS         │
└──────────────────────┬──────────────────────────────┘
                       │ DTOs (WKT, tuples, dataclasses)
                       ▼
┌─────────────────────────────────────────────────────┐
│  CORE LAYER (core/)   — QGIS-AGNOSTIC               │
│  Services, Interfaces, Domain, Validation, Utils    │
│  Pure Python, thread-safe, testable without QGIS    │
└──────────────────────┬──────────────────────────────┘
                       │ DTOs
                       ▼
┌─────────────────────────────────────────────────────┐
│  EXPORTERS (exporters/) — Factory Pattern           │
│  BaseExporter + 11 format-specific exporters        │
└─────────────────────────────────────────────────────┘
```

### 4.2 Key Architectural Components

| Layer | Components |
|-------|------------|
| **GUI Managers (10)** | Signal, Input, Preview, Export, Interpretation, State, Settings, Tool, LayerNotification, UIStatus |
| **Renderers (7)** | Base, Topo, Geology, Drillhole, Structure, Interpretation, Color |
| **Async Tasks (3)** | TaskOrchestrator, GeologyTask, DrillholeTask |
| **Core Services (7)** | Geology, Structure, Drillhole, Export, Preview, VerticalExaggeration, AccessControl |
| **Interfaces (6)** | IGeology, IDrillhole, IStructure, IPreview, ICache, IRenderer3D |
| **Validators (11)** | Base, Pipeline, Layer, Field, Path, Project, ProjectValidators, Helpers, Validators, LayerMetadata, CrsPlausibility |
| **Exporters (11)** | Vector, DXF, Profile, CSV, Interpretation3D, Interpretation, Drillhole3D, Drillhole, PDF, SVG, Image |

### 4.3 Technical Highlights

- **Extract-then-Compute**: GUI extracts to DTOs → Core computes with pure Python → GUI presents
- **Dependency Injection**: Controller consumes interfaces (testable, mockable)
- **Thread Safety**: Heavy ops via `QgsTask`, no live QGIS objects in threads
- **QGIS 4.x Ready**: 100% scoped enums, `qgis.PyQt` agnostic imports
- **Security**: Path traversal protection, Bandit/detect-secrets clean

---

## 5. Quality Metrics

| Metric | Value |
|--------|-------|
| **Automated Tests** | 763 (100% pass in Docker) |
| **Code Quality Score** | 99.9/100 |
| **QGIS Compliance** | 85.0/100 |
| **Cyclomatic Complexity** | ≤ 10 (enforced) |
| **Docstring Coverage** | 100% (Google style) |
| **Return Type Hints** | 100% |
| **i18n Coverage** | 100% (14 languages) |
| **Signal Leaks** | 0 (from 22 in v3.0.1) |
| **Security Findings** | 0 critical (Bandit/detect-secrets) |
| **GUI Test Coverage** | 91% |

### Quality Infrastructure

```bash
make pre-release      # qt6-check + security-scan + docker-test
make security-scan    # Bandit + detect-secrets + Flake8 (Portal-compatible)
make qt6-check        # pyqgis4-checker (same tool as QGIS Portal)
uv run qgis-analyzer analyze . --report   # Deep architectural audit
```

---

## 6. Competitive Landscape

The QGIS geological cross-section niche has grown to **~30 relevant plugins** across
five clusters: geological sections, drillholes/boreholes, structural geology/stereonet,
3D modelling, and geological mapping. The direct-profile competitors are §6.1–§6.8; the
wider landscape added on 2026-10-11 follows in §6.9–§6.11. Download figures are the
portal's cumulative counts and are an **adoption proxy**, not active use.

### 6.1 qProf (Mauro Alberti & Marco Zanieri)

- **Adoption**: ~212,000 downloads (by far the most-used plugin in the niche)
- **Maturity**: Oldest (2013), most established
- **Strengths**: Multiple DEMs, GPX input, fold-axis projection, on-the-fly reprojection
- **Weaknesses**: Requires straight 2-point section lines for geological projection; older UI; no drillhole support
- **Architecture**: Traditional monolithic Python

### 6.2 Geoscience Plugin (Roland Hill)

- **Adoption**: ~124,500 downloads (the drillhole incumbent)
- **Maturity**: Well-established, drilling-focused
- **Strengths**: Professional drillhole desurveying, downhole data, section generation, QGIS project persistence
- **Weaknesses**: Drillhole-centric (not full interpretation); sections in separate canvas; no interactive digitizing
- **Architecture**: Traditional Python
- **2026 update**: v2.0 (2026-08) is now **QGIS 4.0–4.99 ready**, and the project is **discontinued in favour of OpenLog** (funded, Oslandia) — see §6.9.

### 6.3 GeoProfile (Silver Piedra)

- **Maturity**: New (2025, v1.0)
- **Strengths**: Simple UI, color matching to map, bedding/structural projection, PDF export
- **Weaknesses**: No drillholes, no interactive interpretation, limited formats
- **Architecture**: Traditional Python

### 6.4 GIS4Geology (Uni Halle)

- **Maturity**: Academic project (2023)
- **Strengths**: Borehole-based section creation, complex geometry digitizing
- **Weaknesses**: Limited interpolation (simple layers only), academic support
- **Architecture**: Traditional Python

### 6.5 Parallel Folds & Structural Tool (Stefano Tavani)

- **Maturity**: Active (v1.3)
- **Strengths**: Parallel fold digitization, stereonet (Schmidt), geometric constraints, SVG export
- **Weaknesses**: Fold-focused niche; no drillholes; limited general interpretation
- **Architecture**: Traditional Python

### 6.6 Profile Interpreter (QGeomodel)

- **Maturity**: New (2026, v0.1.3)
- **Strengths**: Native `QgsElevationProfileCanvas` integration, PointZ digitizing, data-agnostic
- **Weaknesses**: Only places points (no polygons); no data extraction; no export beyond layer; no snapping UI
- **Architecture**: Minimal, modern QGIS 3.40+ only

### 6.7 Elevation Profile (junethtea)

- **Maturity**: Active (v1.9.3)
- **Strengths**: High-precision DEM profiling, terrain smoothing, QGIS 4 ready, Pro tier
- **Weaknesses**: **Not geological** (network planning focus); no geology/structures/drillholes
- **Architecture**: Commercial freemium

### 6.8 Profile Tool (generic)

- **Maturity**: Very old, ubiquitous
- **Strengths**: Simple elevation profiles from multiple layers
- **Weaknesses**: Purely topographic; no geological features
- **Architecture**: Legacy

### 6.9 OpenLog (Apeiron, funded by Oslandia)

> Added 2026-10-11 — the most significant new direct competitor.

- **Adoption**: ~21,300 downloads, actively maintained (v2.0.1, 2026-09)
- **Strengths**: High-performance **drillhole visualisation in 3D, cross-section and log views**; it is the declared successor to the Geoscience drill tools
- **Weaknesses**: Drillhole/visualisation-centric; not a full map→section interpretation workflow
- **Relevance**: Directly overlaps SecInterp's drillhole module and its "display" value proposition

### 6.10 Structural geology & stereonet cluster

> Added 2026-10-11 — the space where SecInterp has **no** feature.

| Plugin | Downloads | Latest | Note |
|--------|-----------|--------|------|
| qgSurf (M. Alberti) | ~82,900 | 4.4.0 (2026-08) | Geological planes/surfaces + stereonet + best-fit |
| Stereonet (D. Childs) | ~19,600 | 0.3 (2018) | Classic mplstereonet/Kamb |
| GeoTrace / GeoTrace2 (Thiele/Grose) | ~20,600 / ~3,700 | 1.34 (2023) | Structural traces from rasters + stereonet |
| Dip-Strike Tools | ~5,600 | 0.2.2 (2026) | Dip-strike digitising |
| Stereoplot (UWA-CET) | ~940 | 1.0.1 (2026) | Interactive stereographic |
| GeoStereonet (S. Mishra) | ~810 | 1.2.0 (2026) | Kamb, Fisher, eigenvector, rose, fold-axis |
| GeolAttitude | ~410 | 0.2.13 (2026) | Attitude from DTMs + uncertainty |
| Structural Families Mapper | ~290 | 1.0.1 (2026) | QA/QC + Rose/Schmidt/Wulff |

SecInterp projects dip/strike but offers no stereonet or fold analysis; entering this
space means competing with 6+ mature plugins, so the pragmatic path is **export/
interoperation** (feed `mplstereonet`/qgSurf), not reimplementation.

### 6.11 3D geological modelling

> Added 2026-10-11 — SecInterp **exports** 3D but does not **model** 3D.

- **LoopStructural** (Lachlan Grose, ~2,550 downloads): QGIS interface to the
  LoopStructural implicit 3D modelling library (2026).
- **GemPy** (Python library, ~1.3k stars): implicit 3D structural modelling; GIS data
  is ingested via **GemGIS**.
- **ForGEO** (BRGM, ~4,300) and **GeoCongo AI** (~280) also cover 3D geomodelling.

These define the boundary of SecInterp's "3D" claim: it produces Z-aware exports, not
3D geological models or a 3D scene view.

---

## 7. Comparative Analysis Matrix

### 7.1 Core Capability Comparison

| Capability | **SecInterp** | qProf | Geoscience | GeoProfile | GIS4Geology | Parallel Folds | Profile Interpreter |
|------------|:-------------:|:-----:|:----------:|:----------:|:-----------:|:--------------:|:-------------------:|
| **Topographic profile (DEM)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ (native) |
| **GPX input** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Geological outcrop projection** | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ❌ |
| **Structural dip/strike projection** | ✅ | ✅ | ❌ | ✅ | ⚠️ | ✅ | ❌ |
| **Apparent dip calculation** | ✅ | ✅ | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| **Fold-axis projection** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Drillhole desurveying** | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Drillhole interval projection** | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Interactive interpretation (polygons)** | ✅ | ❌ | ❌ | ❌ | ⚠️ | ✅ | ❌ |
| **Interactive interpretation (points)** | ⚠️ | ❌ | ❌ | ❌ | ⚠️ | ⚠️ | ✅ |
| **Undo/Redo in drawing** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Vertex snapping** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Measurement tool** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Stereonet analysis** | ❌ | ⚠️ | ❌ | ❌ | ❌ | ✅ | ❌ |

Legend: ✅ Full · ⚠️ Partial · ❌ None

### 7.2 Export & Interoperability Comparison

| Export Format | **SecInterp** | qProf | Geoscience | GeoProfile | GIS4Geology | Parallel Folds |
|---------------|:-------------:|:-----:|:----------:|:----------:|:-----------:|:--------------:|
| Shapefile | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| GeoPackage | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| DXF (CAD) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| CSV | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| PDF | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| SVG | ✅ | ✅ | ❌ | ⚠️ | ❌ | ✅ |
| PNG/JPG | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **3D export (Z-aware)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **CityJSON** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 7.3 Technical & Quality Comparison

| Dimension | **SecInterp** | qProf | Geoscience | GeoProfile | GIS4Geology | Parallel Folds | Profile Interpreter |
|-----------|:-------------:|:-----:|:----------:|:----------:|:-----------:|:--------------:|:-------------------:|
| **Architecture** | Clean (Core/GUI) | Monolithic | Monolithic | Monolithic | Monolithic | Monolithic | Minimal |
| **Automated tests** | 763 | Few | Some | None | None | Few | Yes (small) |
| **Async processing** | ✅ QgsTask | ❌ | ⚠️ | ❌ | ❌ | ❌ | N/A |
| **Adaptive LOD** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | N/A |
| **i18n languages** | 14 | 1-2 | 1 | 1-2 | 1 | 1-2 | 1 |
| **QGIS 4.x ready** | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ |
| **Security scanned** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ |
| **Active maintenance** | ✅ (2026) | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **Documentation** | Extensive | Good | Good | Basic | Academic | Basic | Good |
| **License** | GPL v3 | GPL | GPL | GPL | GPL | GPL | GPL |

### 7.4 Scope Comparison (Radar Summary)

| Plugin | Topography | Geology | Structure | Drillhole | Interpretation | Export | Total Scope |
|--------|:----------:|:-------:|:---------:|:---------:|:--------------:|:------:|:-----------:|
| **SecInterp** | ●●● | ●●● | ●● | ●●● | ●●● | ●●● | **18/18** |
| Geoscience | ●● | ● | ○ | ●●● | ○ | ●● | 8/18 |
| qProf | ●●● | ●● | ●●● | ○ | ○ | ●● | 10/18 |
| GeoProfile | ●● | ●● | ●● | ○ | ○ | ●● | 8/18 |
| GIS4Geology | ●● | ●● | ● | ●● | ● | ● | 8/18 |
| Parallel Folds | ●● | ● | ●●● | ○ | ●● | ●● | 10/18 |
| Profile Interpreter | ○ | ○ | ○ | ● | ● | ○ | 2/18 |

Legend: ●●● Full · ●● Good · ● Basic · ○ None

### 7.5 Adoption snapshot (portal downloads, 2026-10)

Feature matrices show capability, not reach. The portal's cumulative download counts
(a crude adoption proxy) tell a different story and should temper any "market leader"
claim:

| Plugin | Downloads | Category |
|--------|----------:|----------|
| qProf | ~212,000 | Section/profile |
| Geoscience | ~124,500 | Drillhole |
| qgSurf | ~82,900 | Structural |
| Midvatten | ~55,600 | Hydrogeology |
| OpenLog | ~21,300 | Drillhole (3D) |
| **SecInterp** | **~4,640** | **Integrated section** |

SecInterp leads on **breadth and engineering**, not on adoption. The matrices above
also predate the 2026 expansion of the ecosystem (§6.9–§6.11); treat the competitor
columns as the direct-profile cluster only.

---

## 8. Differentiators & Positioning

### 8.1 Unique Selling Points (USPs)

1. **Integrated Workflow**: The only plugin covering topography + geology + structure + drillholes + interpretation + export in ONE tool
2. **3D Drillhole Support**: SecInterp, Geoscience and OpenLog desurvey drillholes; only SecInterp combines desurveying with interactive in-section interpretation.
3. **3D Export (Z-aware)**: Unique Z-aware GeoPackage/Shapefile and CityJSON export of interpretations and drillholes. This is **export**, not 3D modelling (see §6.11).
4. **Clean Architecture**: Only SecInterp uses Core/GUI separation among geological plugins
5. **Async + LOD**: Only SecInterp offers both background processing and adaptive level-of-detail
6. **14 Languages**: Widest i18n coverage in the niche
7. **763 Tests**: Highest test coverage among competitors
8. **QGIS 4.x Ready**: SecInterp was early on Qt6; competitors have since caught up (Geoscience 2.0 is now QGIS 4-ready), so this is parity rather than a lead.
9. **Interactive Drawing**: Only SecInterp + Parallel Folds offer in-profile polygon digitizing
10. **DXF Export**: Unique CAD integration for mining/engineering workflows

### 8.2 Positioning Statement

> **SecInterp** is the most complete open-source QGIS plugin for geological cross-section interpretation, targeting professional geologists in **mining, exploration, and structural geology** who need an integrated workflow from raw GIS data to CAD-ready deliverables.

### 8.3 Competitive Positioning Map

```
                        HIGH FEATURE BREADTH
                                ▲
                                │
    qProf ●                     │                        ● SecInterp
   Parallel Folds ●             │
                                │
    Geoscience ●                │
                                │
    GIS4Geology ●       GeoProfile ●
                                │              ● Profile Interpreter
                                └─────────────────────────────────────▶
                            LOW                    HIGH
                         ARCHITECTURE QUALITY
```

SecInterp occupies the **top-right quadrant**: maximum feature breadth AND highest architectural quality. (Breadth here refers to the direct-profile cluster; the wider 2026 ecosystem adds best-in-class single-purpose tools for stereonet and 3D modelling where SecInterp is absent — see §6.10–§6.11.)

---

## 9. Target Users & Use Cases

### 9.1 Primary Users

| User Type | Need | SecInterp Value |
|-----------|------|-----------------|
| **Exploration Geologist** | Quick cross-sections from map + drillholes | Integrated workflow, fast preview |
| **Mining Geologist** | Section interpretation + CAD export | DXF export, 3D export |
| **Structural Geologist** | Dip/strike projection, apparent dip | Dedicated structure service |
| **GIS Specialist** | Automate section generation | Batch export, settings persistence |
| **Academic Researcher** | Publication figures | PDF/SVG export, stereonet (future) |
| **Consultant** | Multi-client, multi-language deliverables | 14 languages, multi-format export |

### 9.2 Representative Use Cases

1. **Mining Resource Estimation**: Project drillhole intervals onto section, interpret ore body geometry, export to DXF for mine planning
2. **Exploration Targeting**: Combine outcrop mapping + structural measurements + drillholes to identify targets
3. **Academic Mapping**: Generate publication-ready cross-sections with structural data
4. **Infrastructure Geology**: Create sections along planned corridors (tunnels, roads)
5. **Hydrogeology**: Interpret aquifer geometry from borehole data

---

## 10. SWOT Analysis

### 10.1 Strengths

- ✅ **Most complete feature set** in the niche
- ✅ **Best architecture** (Clean, DI, testable)
- ✅ **Highest quality metrics** (763 tests, 99.9/100)
- ✅ **Widest i18n** (14 languages)
- ✅ **QGIS 4.x ready** ahead of competitors
- ✅ **Active maintenance** (frequent releases)
- ✅ **Comprehensive documentation**
- ✅ **Security-scanned** (Portal-compatible)

### 10.2 Weaknesses

- ❌ **Low adoption** (~4,640 downloads vs qProf's ~212,000) — best features, smallest installed base
- ❌ **No GPX input** (qProf has it)
- ❌ **No fold-axis projection** (qProf, Parallel Folds have it)
- ❌ **No stereonet** — and the space is crowded and mature (qgSurf, Stereonet, GeoStereonet, Stereoplot…; see §6.10)
- ❌ **No native 3D modelling/scene** — it exports 3D, it does not build 3D models (LoopStructural/GemPy; see §6.11)
- ❌ **Single section line** (qProf supports multiple profiles)
- ❌ **No database layer support** (Geoscience limitation too)
- ⚠️ **Complex UI** (many features → steeper learning curve)
- ⚠️ **Younger than qProf/Geoscience** (less battle-tested)

### 10.3 Opportunities

- 🔵 **Add stereonet analysis** (matches Parallel Folds)
- 🔵 **Add fold-axis projection** (matches qProf)
- 🔵 **Multi-section batch processing**
- 🔵 **Database connectivity** (PostGIS, SQLite)
- 🔵 **3D scene view integration** (QGIS 3D)
- 🔵 **Machine learning** (auto-interpretation)
- 🔵 **Cloud/enterprise licensing** (monetization)
- 🔵 **Plugin ecosystem** (extensions API)

### 10.4 Threats

- 🔴 **OpenLog** (Apeiron/Oslandia) — funded, active successor to Geoscience's drill tools; may subsume drillhole + section display
- 🔴 **Geoscience plugin** (still the drillhole incumbent, now QGIS 4-ready)
- 🔴 **qProf** (established, cited in literature, ~45× the adoption)
- 🔴 **LoopStructural / GemPy** — own the emerging 3D-modelling demand
- 🔴 **QGIS native elevation profile** improvements (could absorb features)
- 🔴 **Competitor i18n expansion**
- 🔴 **Maintenance burden** of broad feature set
- 🔴 **Single-maintainer risk** (bus factor)

---

## 11. Roadmap & Future Direction

Based on the CHANGELOG trajectory and competitive gaps:

### Near-term (v3.9 - v4.0)

| Priority | Feature | Rationale |
|----------|---------|-----------|
| High | **Stereonet (via interoperation)** | Export attitudes to `mplstereonet`/qgSurf instead of reimplementing; the space is crowded (§6.10) |
| High | **Multi-section batch** | Enterprise workflow demand |
| Medium | **3D bridge (feed LoopStructural/GemPy)** | Leverage existing Z-aware export into 3D modelling tools (§6.11) |
| Medium | **GPX input** | Match qProf; field data |
| Medium | **Fold-axis projection** | Match qProf; structural geology |
| Medium | **Database layers** | PostGIS/SQLite for enterprise |

### Mid-term (v4.x)

| Feature | Rationale |
|---------|-----------|
| **QGIS 3D scene integration** | Native 3D visualization |
| **Multi-line profiles** | Match qProf capability |
| **Plugin extension API** | Ecosystem growth |
| **Cloud sync** | Team collaboration |

### Long-term

| Feature | Rationale |
|---------|-----------|
| **AI-assisted interpretation** | Automation, differentiation |
| **Real-time collaboration** | Enterprise teams |
| **Web/desktop hybrid** | Broader reach |

---

## 12. Conclusion

SecInterp is the **most feature-complete and best-engineered** open-source QGIS plugin for geological cross-section interpretation. While competitors like qProf and Geoscience have specific strengths (fold-axis projection, drillhole desurveying respectively), **no single competitor matches SecInterp's integrated breadth** across topography, geology, structure, drillholes, interpretation, and export.

Its Clean Architecture, 763 tests, 14-language support, and QGIS 4.x readiness position it as a **reference implementation** for professional QGIS plugin development — not just a geological tool.

### Final Positioning

| Aspect | Verdict |
|--------|---------|
| **Feature completeness** | 🥇 #1 in niche |
| **Architecture quality** | 🥇 #1 in niche (and among top QGIS plugins overall) |
| **Test coverage** | 🥇 #1 in niche |
| **i18n** | 🥇 #1 in niche |
| **Drillhole depth** | 🥈 #2 (behind Geoscience) |
| **Fold/structural geometry** | 🥉 #3 (behind qProf, Parallel Folds) |
| **Maturity** | 🥉 #3 (behind qProf, Geoscience) |

**Recommended next steps** to consolidate leadership: add stereonet + fold-axis projection (close structural gaps) and multi-section batch processing (enterprise appeal).

---

## 13. References

### SecInterp
- Repository: https://github.com/geociencio/sec_interp
- Documentation: https://geociencio.github.io/sec_interp_docs/
- QGIS Plugin Page: https://plugins.qgis.org/plugins/sec_interp/

### Competitors
- **qProf**: https://github.com/mauroalberti/qProf
- **Geoscience**: https://rolandhill.github.io/geoscience/
- **GeoProfile**: https://github.com/silver9704/GeoProfile
- **GIS4Geology**: https://geo.uni-halle.de/en/appliedgeo-posts/2023/new-cross-section-tool-for-qgis-gis4geology/
- **Parallel Folds**: https://github.com/tavanistefano73-tech/parallel-folds
- **Profile Interpreter**: https://gitlab.com/qgeomodel/qgis-profile-interpreter
- **Elevation Profile**: https://github.com/junethtea/elevation-profile

### Competitors added 2026-10-11 (wider landscape)
- **OpenLog**: https://plugins.qgis.org/plugins/openlog/ (Apeiron/Oslandia; drillhole 3D/section/log)
- **qgSurf**: https://plugins.qgis.org/plugins/qgSurf/ · https://github.com/mauroalberti/geocouche (planes/surfaces + stereonet)
- **Stereonet**: https://plugins.qgis.org/plugins/qgis-stereonet/ (D. Childs)
- **GeoStereonet**: https://github.com/mellow2334/GeoStereonet
- **Stereoplot**: https://plugins.qgis.org/plugins/stereoplot/ (UWA-CET)
- **GeoTrace**: https://github.com/lachlangrose/GeoTrace (Thiele/Grose)
- **LoopStructural**: https://plugins.qgis.org/plugins/LoopStructural/ · https://github.com/Loop3D/LoopStructural
- **GemPy**: https://www.gempy.org/ · https://github.com/gempy-project/gempy
- **Midvatten**: https://plugins.qgis.org/plugins/midvatten/ (hydrogeology)
- **Geology tools**: https://github.com/pinogcosentino/Geology-tools
- **QGeoloGIS**: https://gitlab.com/Oslandia/qgis/QGeoloGIS
- **Isoliner3D**: https://plugins.qgis.org/plugins/isoliner3d/ (3D bed bodies + boreholes)
- **GEOL-QMAPS**: https://github.com/swaxi/GEOL-QMAPS (Perret et al. 2024, *Applied Computing and Geosciences*)

### Standards & Methodology
- QGIS Plugin Repository: https://plugins.qgis.org/
- QGIS Plugin Security Scanning: https://plugins.qgis.org/docs/security-scanning/
- Clean Architecture: Robert C. Martin (2017)
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/

---

*Report generated: 2026-10-11*
*SecInterp version analyzed: 3.10.0*
*See also: `ARCHITECTURE_EN.md`, `ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md`, `PLUGIN_ANALYSIS.md`*
