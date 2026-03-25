# Agent Learning Memory (SecInterp)

This file records technical lessons, user preferences, and solutions to complex problems. It uses a structured format for efficient retrieval by the agent system.

## 🧠 Lesson Log (YAML Structured)

```yaml
  - date: 2026-03-25
    category: TECHNICAL
    topic: GeoPackage Append & Layer Names (v3.4.0)
    lesson: "The QGIS GeoPackage driver successfully appends new distinct layers into an existing .gpkg file if the `layerName` option is populated via `QgsVectorFileWriter.SaveVectorOptions`. If `layerName` is omitted and the target file exists, the layer will blindly overwrite or merge into the first available table."
    action: "Always enforce supplying a layer_name to create_vector_writer when targeting GeoPackage outputs, and pass overwrite_layer=False when intended to append."

  - date: 2026-03-25
    category: ARCHITECTURE
    topic: Vector Layer Synchronization (v3.4.0)
    lesson: "In-memory layer updates inside QGIS require a strict transaction boundary (`startEditing`, `deleteFeatures`, `addFeatures`, `commitChanges`) to guarantee atomicity and correct signal emission for the canvas renderers. Bypassing these boundaries leads to phantom geometries."
    action: "Encapsulate live QgsVectorLayer mutation in unified save_to_layer and sync_from_layer routines and explicitly clear cache logic to keep the Domain DTOs synced with UI state."

  - date: 2026-03-19
    category: TESTING
    topic: Docker-based Verification (QGIS Headless)
    lesson: "Verifying QGIS-dependent functionality (like DXF/GPKG export) is impossible in local environments lacking the full QGIS/PyQt stack. Relying on mocks only validates the orchestration logic, not the file driver compatibility."
    action: "Always use `make docker-test` or run reproduction scripts inside the QGIS Docker container (`docker run -v ...`) to confirm actual file creation and driver-specific behavior."

  - date: 2026-03-19
    category: ARCHITECTURE
    topic: Exporter Signature Consistency
    lesson: "Mixing generic and specialized exporters in the same service (like `ExportService`) without a common interface for the `export` data payload leads to brittle logic and runtime TypeErrors."
    action: "Standardize on specialized exporters that already encapsulate the format-specific logic (DXF/GPKG) and avoid special-casing format extensions in the orchestration service."

  - date: 2026-03-16
    category: TOOLING
    topic: Static Analysis Parser Failures
    lesson: "Tools relying on Regex for code parsing, like the current version of `qgis-plugin-analyzer`, frequently fail on multi-line function signatures (e.g., those formatted by `black`). This leads to severe false positives in Type Hint coverage reports."
    action: "Do not blindly trust static analysis metrics that drop inexplicably. Always verify the true source code using the Python `ast` module before attempting massive, potentially redundant refactors."

  - date: 2026-03-15
    category: TECHNICAL
    topic: DXF Export Limitations (v3.4.0)
    lesson: "The OGR DXF driver fails when creating arbitrary fields. Stripping fields is necessary for geometry-only exports to avoid termination errors."
    action: "Centralize DXF field stripping in the primary I/O utility (io.py) and ensure DXFExporter handles empty attribute sets gracefully."

  - date: 2026-03-15
    category: ARCHITECTURE
    topic: Drillhole Interval Integrity (v3.4.0)
    lesson: "Densification of trajectories is insufficient for short geological intervals. Explicit endpoint interpolation is mandatory to ensure every segment has topological consistency."
    action: "Mandate interpolation at exact interval depths in TrajectoryEngine to guarantee valid segment geometry generation."

  - date: 2026-03-15
    category: TECHNICAL
    topic: Export Setting Persistence (v3.4.0)
    lesson: "Synchronizing UI widgets via QgsSettings requires standardized prefixes (SecInterp/) and coordination with ConfigService to ensure multi-scope persistence."
    action: "Standardize all persistence keys to use the SecInterp/ prefix for both UI state and core config."

  - date: 2026-03-12
    category: TECHNICAL
    topic: Deterministic Lifecycle Cleanup
    lesson: "In QGIS plugins with complex UI/Tool interactions, relying on Python's garbage collector or implicit deletion is insufficient. Explicit and ordered cleanup in closeEvent is required to prevent orphaned GraphicsItems (rubber bands) and signal leaks."
    action: "Orchestrate a cleanup sequence in closeEvent for all managers and tools. Implement a specialized cleanup_finalized() for tools to ensure canvas hygiene."

  - date: 2026-03-12
    category: ARCHITECTURE
    topic: DTO vs Tuple Flow
    lesson: "Data flow using tuples becomes unmanageable as the project grows. Standardizing on Dataclasses (DTOs) for service returns improves readability and simplifies background task preparation (Extract-then-Compute)."
    action: "Migrate all legacy tuple-based service returns to explicit Dataclasses (e.g., DrillholeProjection)."

  - date: 2026-03-12
    category: DEPLOYMENT
    topic: Deployment Exclusions
    lesson: "Active development creates many noise files (coverage reports, Pyre configs, analyzer logs). If not explicitly excluded in .qgisignore or similar, they bloat the production environment."
    action: "Maintain a strict .qgisignore synchronized with recently adopted Dev/QA tools."

  - date: 2026-03-09
    category: TESTING
    topic: Iterative Mocking for Arithmetic
    lesson: "Complex Qt objects like QRectF/QSizeF used in layouts often undergo arithmetic operations or comparisons (e.g., max()). Mocking them requires returning numeric types for width/height/x/y to prevent TypeErrors."
    action: "Enrich qt_mocks.py with basic numeric return values for dimensional methods (width, height, etc.) to support layout-heavy tests."

  - date: 2026-03-09
    category: TESTING
    topic: Patch Specificity for Local Imports
    lesson: "Classes imported locally inside functions (e.g., InterpretationPropertiesDialog) must be patched using the absolute path of the calling module where the lookup occurs, not the module of origin."
    action: "Always verify if a class is imported at the module level or inside a method before defining the patch target path."

  - date: 2026-03-09
    category: TESTING
    topic: Dynamic Mock Return Values
    lesson: "QgsProject.readEntry returns (value, bool). In complex persistence flows with multiple calls, using fixed side_effects ensures that each specific setting (e.g., layers, bands, colors) is correctly simulated."
    action: "Use side_effect lists or dynamic functions for readEntry mocks to verify multi-scope setting fallbacks (SecInterp vs SecInterpUI)."

  - date: 2026-03-08
    category: TESTING
    topic: Qt Object Mocks
    lesson: "When testing exporters like ImageExporter or PDFExporter, native Qt objects like QImage, QPainter, or QPdfWriter require precise mock attributes (e.g. SmoothPixmapTransform, save) to avoid exceptions."
    action: "Always enrich tests/mocks/qt_mocks.py with the specific methods and attributes that the QGIS custom painter jobs expect."

  - date: 2026-03-08
    category: ARCHITECTURE
    topic: System Standardization & Reflection
    lesson: "A purely English-based agentic system improves context injection and reduces parsing ambiguity. Implementing formalized reflection loops (post-execution) allows for better semantic memory retention."
    action: "Adopt English as the universal standard for internal system files. Maintain a mandatory reflection phase in all core workflows."

  - date: 2026-02-01
    category: ARCHITECTURE
    topic: Skill Localization
    lesson: "Over-simplification of Skills during translations can cause loss of technical manuals."
    action: "Keep technical cores in English; operational structure in Spanish."

  - date: 2026-02-19
    category: ARCHITECTURE
    topic: Resilience & Lazy Loading
    lesson: "When implementing experimental features or heavy domain services, use a SafeLoader/Lazy Loading pattern to prevent cascading failures during plugin initialization. This ensures the core plugin remains functional even if a specific module fails to load (e.g., due to missing dependencies)."
    action: "Implement SafeLoader for all optional or heavy services and use demand-based instantiation. IMPROVEMENT: Support constructor arguments in lazy_load."

  - date: 2026-02-25
    category: TECHNICAL
    topic: Data Modeling and Typing
    lesson: "Using tuples for complex data transfer makes code unreadable and hard to refactor (index-based access)."
    action: "Mandatory use of Dataclasses (entities) for all service returns. Avoid list[tuple]."

  - date: 2026-02-28
    category: ARCHITECTURE
    topic: Layer Caching and Mock Integrity
    lesson: "When centralizing layer resolution with caching (LayerResolver), mock layers must have unique IDs across tests to prevent cross-test cache pollution."
    action: "Implement a global UNIQUE_ID_COUNTER in test mocks and call LayerResolver.clear_cache() in BaseTestCase.setUp()."

  - date: 2026-02-28
    category: TECHNICAL
    topic: Strict QGIS Validation in Mocks
    lesson: "Strict validators use layer.wkbType() and check for formal QgsField existence. Mocks must support setWkbType and formal field addition to pass production-grade validation."
    action: "Update MockQgsMapLayer to support WKB types and use real QgsField objects instead of simpler mocks when validation is involved."



  - date: 2026-02-01
    category: TECHNICAL
    topic: QgsGeometry Mocking
    lesson: "Mocking QgsGeometry requires care with methods like pointN or is3D."
    action: "Prefer unittest for this project according to user preference."

  - date: 2026-02-05
    category: USER_PREFERENCE
    topic: Development Tools
    lesson: "Preference for black (formatting), uv (dependencies), and programmatic UI (no .ui)."
    action: "Apply these standards in every new GUI implementation."

  - date: 2026-02-05
    category: ARCHITECTURE
    topic: Agentic Brain Evolution
    lesson: "Gen 3 introduces self-criticism (Auditor) and semantic memory for greater cognitive stability."
    action: "Invoke /ia-critic after planning and /cierra-sesion for continuous learning."
  - date: 2026-02-15
    category: QUALITY
    topic: qgis-analyzer Context
    lesson: "The QGIS analyzer includes the tests/ folder in the global typing score, which can distort the perception of production quality."
    action: "Perform breakdowns by folder to validate compliance of production code (core/gui)."

  - date: 2026-02-15
    category: TECHNICAL
    topic: QGIS Signal Leaks
    lesson: "Signals connected to map tools (MapTools) or dialog pages must be explicitly disconnected to avoid leaks and erratic behavior."
    action: "Always implement a disconnect_signals() method invoked when closing the context."

## ⚙️ Global Preference Configuration

- **Language**: Communication (Spanish), Code/Commits/Docs (English).
- **Standards**: Google Docstrings, Pathlib, Strict Typing.
- **Workflow**: Starts with `/start-session`, Closes with `/close-session`.

---
  - date: 2026-02-16
    category: TECHNICAL
    topic: Signal Tracing vs Mocks
    lesson: "Using wrappers to connect signals (like sm._connect_checked) can break unit tests if they expect direct calls to the slot Mock. Signals connected via wrappers are not detected by `assert_called_with` of Mock objects."
    action: "For methods that are mocks in unit tests, maintain direct signal connections without tracking wrappers, or orchestrate selective disconnection."

  - date: 2026-02-18
    category: TECHNICAL
    topic: qgis-manage Build Rigidity
    lesson: "The qgis-manage tool has hardcoded exclusions and depends on pyrcc5 (PyQt5), which generates automatic technical debt in resources.py."
    action: "After compiling resources, always apply an import patch (sed) and verify that no necessary files are missing in deployment due to hidden exclusions."

  - date: 2026-02-18
    category: USER_PREFERENCE
    topic: Fast Deployment
    lesson: "For fast iterations that do not require changes in resources or translations, it is preferred to avoid compilation."
    action: "Use the command: 'uv run qgis-manage deploy --no-compile'"

  - date: 2026-03-03
    category: WORKFLOW
    topic: Phase Initialization
    lesson: "A standard phase initialization must include a baseline quality scan (ai-ctx) and a full test suite validation (docker) before any code change to ensure a healthy starting point."
    action: "Adopt /inicia-fase as the mandatory gate for major version increments, documenting quality gaps as 'Objective 0'."

---
  - date: 2026-03-15
    topic: "QGIS 4.x Readiness & MCP Integration"
    lesson: "Removing hard PyQt5 dependencies is critical for Qt6 compatibility, as QGIS provides the runtime. Hardcoding versions in pyproject.toml causes orchestration deadlocks in modernized environments."
    action: "Maintenance of 'Optional Dependency' status for PyQt during transition, and total removal for v4.0 environments."
  - date: 2026-03-15
    topic: "MCP Native Orchestration"
    lesson: "Structural Tool Calls via MCP (scripts/mcp_server.py) reduce hallucination rates compared to raw markdown skill reading by providing a strict JSON-RPC interface for procedural knowledge."
    action: "Expand mcp_server.py to cover all validation-heavy core logic."
  - date: 2026-03-15
    topic: "Refactoring Regressions"
    lesson: "Large architectural changes in v3.4.0 (Unified I/O) changed internal method signatures of ExportService, breaking unit tests that mocked these private methods."
    action: "Always run the full core test suite (make test) immediately after refactoring internal orchestration methods."

  - date: 2026-03-22
    category: TOOLING
    topic: ai-context-core v3.3.0 CLI & Features
    lesson: "The CLI executable for `ai-context-core` is `ai-ctx`, not `ai-context`. The v3.3.0 update fixes previous aggregation bugs where global metrics (Functions, Classes, MI) were reported as zero."
    action: "Always use `uv run ai-ctx` for project analysis. Leverage the new 'QGIS Standards Compliance' section to audit plugin best practices and i18n coverage."

---
*Last update: 2026-03-22 - Generation 5 Memory Reflection.*
> [!NOTE]
> Lessons from 2026-03-15 and earlier in this log have been consolidated into specialized `SKILL.md` files as part of the self-evolving memory workflow.
```
