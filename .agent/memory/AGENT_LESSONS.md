# Agent Learning Memory (SecInterp)

This file records technical lessons, user preferences, and solutions to complex problems. It uses a structured format for efficient retrieval by the agent system.

## 🧠 Lesson Log (YAML Structured)

```yaml
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

## ⚙️ Configuración Global de Preferencias

- **Language**: Communication (Spanish), Code/Commits/Docs (English).
- **Standards**: Google Docstrings, Pathlib, Strict Typing.
- **Workflow**: Starts with `/inicia-sesion`, Closes with `/cierra-sesion`.

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

## ⚙️ Configuración Global de Preferencias
...
---
*Last update: 2026-03-09 - Completion of GUI Coverage Expansion.*
```
