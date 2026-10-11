# Ecosystem Comparison — QGIS subsurface / geological-section plugins (INTERNAL)

> **Internal working document.** Not published, not mirrored. Snapshot of the QGIS
> plugin ecosystem relevant to SecInterp, compiled from `plugins.qgis.org` tags
> (`geology`, `cross-section`, `structural-geology`, `stereonet`, `borehole`,
> `hydrogeology`) and GitHub. **Data as of 2026-10-11.** Download counts are the
> portal's cumulative historical figure (adoption proxy, not active use).
>
> Companion to the public `docs/PLUGIN_REPORT_AND_COMPARISON_EN.md` (which covers
> 7 competitors); this one is the wide scan (~30 plugins).

## 1. Direct niche — geological section / profile

| Plugin | Author | Downloads | Latest | QGIS | Note |
| :--- | :--- | ---: | :--- | :--- | :--- |
| **qProf** | Alberti / Zanieri | **211,948** | 0.5.0 (exp 0.6.3) | legacy | Straight 2-point lines for geology; GPX; fold-axis |
| **SecInterp** | J. M. Bernales | **4,640** | 3.9.1 (v3.10.0 pending) | 3.28–4.99 | Integrated workflow; this project |
| **GeoProfile** | Silver Piedra | 5,397 | 1.0 (2025-08) | 3.x | Simple profile + geology, PDF |
| **GIS4Geology** | Uni Halle | — | 2023 (academic) | 3.x | Borehole-based sections |
| **Profile Interpreter** | QGeomodel | — | 0.1.3 | 3.40+ | Native elevation canvas; points only |
| **TopoProfile Studio** | F. Cetraro | 186 | 1.0 (2026-09) | — | Profiles + structural markers |
| **Geoscience Section Vert. Exag.** | N. Kern | 1,041 | 0.1 (2025) | — | Geoscience helper |
| **Elevation Profile** | junethtea | — | 1.9.3 | 4.x | Freemium, non-geological |
| **Profile Tool** | various | — | legacy | — | Purely topographic |
| **Isoliner3D** | Информ++ | 1,462 | 1.4.1 (2026-09) | — | 3D bed bodies + boreholes |
| **LandXML Road & Terrain** | E. Akello | 616 | 1.8.1 (2026-10) | — | Civil, not geological |

## 2. Drillhole / borehole

| Plugin | Author | Downloads | Latest | QGIS | Note |
| :--- | :--- | ---: | :--- | :--- | :--- |
| **Geoscience** | Roland Hill | **124,551** | 2.0 (2026-08) | **4.0–4.99** | Incumbent; desurvey + sections; **discontinued** in favour of OpenLog |
| **Midvatten** | Spångmyr / Källgården | 55,559 | 2.0.1 (2026-09) | 3.40–4.99 | Hydrogeology on SQLite/PostGIS |
| **OpenLog** | Apeiron (Oslandia-funded) | 21,314 | 2.0.1 (2026-09) | 3.x/4.x | **3D + section + log** drillhole views (Geoscience successor) |
| **GeODinQGIS** | Fugro | 23,266 | 3.0.2417 | — | Bridge to GeODin database |
| **geoCore** | T-Systems | 11,512 | 0.8.1 (2021) | — | Graphical drilling logs |
| **QGeoloGIS** | Oslandia | — | 1.4.0 (2020) | 2.18–3.99 | Stratigraphy + time series (dated) |
| **THYRSIS** | CEA / Oslandia | 6,115 | 2.3.0 | 3.22+ | Hydrogeological modelling |

## 3. Structural geology / stereonet

| Plugin | Author | Downloads | Latest | Note |
| :--- | :--- | ---: | :--- | :--- |
| **qgSurf** | Mauro Alberti | **82,880** | 4.4.0 (2026-08) | Planes/surfaces + **stereonet** + best-fit + DEM-plane intersection |
| **Stereonet** | Daniel Childs | 19,603 | 0.3 (2018) | Classic (mplstereonet, Kamb) |
| **GeoTrace / 2** | Thiele / Grose | 20,554 / 3,716 | 1.34 (2023) | Structural traces from rasters + stereonet; peer-reviewed |
| **Dip-Strike Tools** | Pennica / Cosentino | 5,632 | 0.2.2 (2026) | Dip-strike digitising/management |
| **DipStrike To KMZ** | Shyam Mishra | 1,215 | 1.0.2 (2026) | KMZ export |
| **Stereoplot** | UWA-CET | 938 | 1.0.1 (2026) | Interactive stereographic |
| **GeoStereonet** | Shyam Mishra | 813 | 1.2.0 (2026) | Kamb, Fisher, eigenvector, rose, fold axis |
| **GeolAttitude** | A. Frigeri | 411 | 0.2.13 (2026) | Plane attitude from DTM + uncertainty |
| **Structural Families Mapper** | RSRC | 294 | 1.0.1 (2026) | QA/QC + Rose/Schmidt/Wulff |
| **GeoDip** | P. Guzman | 137 | 1.0 (2026) | Dip / dip-direction plotting |
| **geocouche** | Mauro Alberti | — | — | `apsg`-based; folded into qgSurf |
| **StereonetStudio** | F. Cetraro | 32 | 1.0.0 (2026) | New |
| **Parallel Folds** | S. Tavani | — | 1.3 | Parallel folds + Schmidt |

## 4. 3D geological modelling

| Plugin / lib | Author | Downloads | Note |
| :--- | :--- | ---: | :--- |
| **LoopStructural** *(plugin)* | Lachlan Grose | 2,552 | QGIS interface to LoopStructural (implicit); 0.1.12 (2026) |
| **GemPy** | gempy-project | — (1.3k★) | Python library (not a QGIS plugin); fed via **GemGIS** |
| **ForGEO** | BRGM | 4,259 | Frontend to the BRGM geomodelling suite |
| **GeoCongo AI** | — | 275 | 3D mining resource modelling + RAG |

## 5. Geological mapping / field

| Plugin | Author | Downloads | Note |
| :--- | :--- | ---: | :--- |
| **Geology from points and lines** | G. Cosentino | 7,947 | Automated geological mapping |
| **Geology tools** | Cosentino / Pennica | 5,817 | Mapping + hydrology + seismic microzonation |
| **EIS QGIS Plugin** | Gispo | 8,910 | Mineral prospectivity mapping |
| **Geovita GIS Processing** | DPE | 8,109 | Geological/geotechnical algorithms |
| **FieldMove Project Importer** | G. Duclaux | 2,727 | FieldMove → QGIS |
| **Geochemistry Plotting Tools** | Jessell / Perret | 2,221 | Geochemical diagrams |
| **GEOL-QMAPS** | J. Perret | — | Field mapping QGIS+QField (peer-reviewed) |
| **CRAG** | BGS | 118 | Geological-map geodata |
| **fraXtex** | A. Fatihi | 680 | Fractures from orthophoto |

## 6. Head-to-head — the direct niche

| Capability | **SecInterp** | qProf | OpenLog | Geoscience | GeoProfile | GIS4Geology | Profile Interpreter |
| :--- | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| Topographic profile (DEM) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ native |
| Outcrop projection | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ❌ |
| Dip/strike + apparent dip | ✅ | ✅ | ❌ | ❌ | ✅ | ⚠️ | ❌ |
| Fold-axis | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Drillhole desurvey + intervals | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| In-profile polygon interpretation + undo/snap | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ |
| Editable interactive legend | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| DXF (CAD) export | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Z-aware 3D / CityJSON export | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 3D view / 3D section | ⚠️ export | ❌ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| GPX input | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Multi-line | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| i18n | **14** | 1–2 | 1 | 1 | 1–2 | 1 | 1 |
| QGIS 4 ready | ✅ | ⚠️ | ✅ | ✅ (2.0) | ⚠️ | ⚠️ | ✅ |
| Tests / architecture | 763 / Clean | few | — | some | — | — | minimal |

## 7. What changes vs the previous internal report

The published comparison (v3.9.1) covered 7 competitors; the real ecosystem is ~30
relevant plugins. New findings and corrections:

1. **OpenLog** (Apeiron/Oslandia, 21k) — a **new, active** direct competitor
   (3D + section + log drillhole views) and the declared successor to Geoscience's
   drill tools. Missing from the published report.
2. **Geoscience 2.0 is now QGIS 4-ready** (2026-08, `4.0–4.99`) → the "QGIS 4 ahead
   of competitors" claim is outdated.
3. The **stereonet space is crowded and mature** (qgSurf 83k, Stereonet 19.6k, plus
   2026 arrivals GeoStereonet/Stereoplot/Structural Families/GeolAttitude/GeoDip).
   It is **not** a cheap gap: adding one means competing with 6+ plugins.
4. **True 3D modelling** is served by **LoopStructural** (QGIS plugin) and **GemPy**.
   SecInterp *exports* 3D, it does not *model* 3D → the "3D" claim must be qualified.
5. **Adoption ≠ features**: SecInterp 4,640 vs qProf 211,948, Geoscience 124,551,
   qgSurf 82,880, Midvatten 55,559, OpenLog 21,314. We are "best engineering", not
   market leader.
6. **The niche heated up in 2026**: ~10 new plugins (LoopStructural, GeoStereonet,
   Stereoplot, GeolAttitude, GeoDip, TopoProfile Studio, StereonetStudio, Isoliner3D,
   fraXtex, LandXML tools).
7. **Portal state**: SecInterp is on **3.9.1**; **v3.10.0 is pending upload**.

## 8. Positioning (internal)

**Defensible moat:** the only plugin integrating topo + geology + structure +
drillhole + **in-situ polygon interpretation** + multi-format export; interactive
interpretation (undo/redo + snapping) + editable legend; DXF + Z-aware/CityJSON
export; engineering quality (Clean Architecture, 763 tests, 14 i18n, CI gates).

**Weaknesses vs the real ecosystem:** low adoption; **no stereonet/fold analysis**;
**no native 3D modelling/scene**; drillhole depth below Geoscience/OpenLog; single
section line; no GPX; broad scope with a bus-factor-1 risk.

## 9. Recommendations (internal)

1. **Do not chase** stereonet or 3D modelling head-on (mature/crowded markets).
   **Interoperate**: export attitudes to `mplstereonet`/qgSurf and feed
   GemPy/LoopStructural instead of reimplementing.
2. **Double down on the integrated workflow**: multi-section/batch, DB layers
   (PostGIS/SQLite), and a 3D bridge (feed LoopStructural) — no integrated competitor.
3. **Reframe the message**: "best *integrated workflow* + best engineering", not
   "#1 by market".
4. **Watch**: **OpenLog** (may subsume drillhole + section), **LoopStructural** (3D),
   **Geoscience 2.0** (now QGIS 4).
5. **Upload v3.10.0** to the portal (currently 3.9.1) — signals active maintenance
   against stalled competitors (QGeoloGIS 2020, geoCore 2021, Stereonet 2018).

## 10. Sources

- `plugins.qgis.org` tags: geology (66), cross-section (8), structural-geology,
  stereonet (5), borehole, hydrogeology; individual plugin pages and version JSON.
- GitHub: `rolandhill/geoscience`, `mauroalberti/qProf`, `mauroalberti/qgSurf` /
  `geocouche`, `lachlangrose/GeoTrace`, `mellow2334/GeoStereonet`, `Loop3D`,
  `gempy-project/gempy`, `swaxi/GEOL-QMAPS`, `pinogcosentino/Geology-tools`.
- Cross-references: `qgis-in-mineral-exploration.readthedocs.io`,
  Perret et al. 2024 (GEOL-QMAPS), Thiele et al. 2017 (GeoTrace).
