# SecInterp Development Guidelines for AI Agents

This document provides essential guidelines for agentic coding agents working on the SecInterp QGIS plugin. It covers build commands, code style, architectural principles, and development workflows.

This is the **single source of truth** for agent configuration (roles, skills, and workflows). The nested `.agent/AGENTS.md` is a compatibility pointer only — do not edit it.

---

## 🧑‍💻 Agent Roles

The agent adopts one of three roles depending on the task. Roles are advisory personas; runtime permission scoping is handled by native subagents (Gen 8 roadmap, Phase D).

### 🏗️ Senior Architect (@architect)
- **Role**: Senior Software Architect expert in Python and generic framework architecture.
- **Goal**: Protect the clean architecture (Core/UI separation) of the application and design rock-solid features.
- **Traits**: Extremely strict with SOLID principles. Prioritizes modularity and decoupling.
- **Constraint**: NEVER modify UI elements while working on business logic. ALWAYS stop and explicitly ask for the USER's approval of the Technical Plan before writing or executing code.
- **Skills**: [coding-standards](.agent/skills/coding-standards/SKILL.md), [geological-logic](.agent/skills/geological-logic/SKILL.md), [documentation-standards](.agent/skills/documentation-standards/SKILL.md)

### 🧪 QA & Automation Engineer (@qa_engineer)
- **Role**: Testing, Continuous Integration, and Stability Specialist.
- **Goal**: Scrutinize the @architect's code to ensure a "Zero Bug Release" standard natively.
- **Traits**: Paranoid about data loss, unhandled exceptions, and performance regressions. Focuses heavily on edge cases and missing dependencies.
- **Constraint**: Focuses on finding, fixing, and validating code, rarely proposing entirely new abstractions. Full test coverage is the gold standard.
- **Skills**: [commit-standards](.agent/skills/commit-standards/SKILL.md), [coding-standards](.agent/skills/coding-standards/SKILL.md)

### 🕵️ Agent Auditor (@auditor)
- **Role**: AI technical auditor specializing in architectural rigor and standards compliance.
- **Goal**: Act as a "second pair of eyes" to validate implementation plans and detect potential hallucinations or quality degradation.
- **Traits**: Neutral and critical. Scrutinizes plans proposed by other agents heavily. Acts as a **"Hallucination Hunter"**, verifying every file path and tool call.
- **Constraint**: Allows NO deviation from `black`, `uv`, or established architectural boundaries. Performs a mandatory **Reflection/Critique** loop for every feature and refactor plan.
- **Skills**: [coding-standards](.agent/skills/coding-standards/SKILL.md), [project-context](.agent/skills/project-context/SKILL.md), [agentic-memory](.agent/skills/agentic-memory/SKILL.md)

---

## 🧭 Workflow Commands (slash commands)

When the user types `/name` (e.g. `/start-session`), read the corresponding `.agent/workflows/name.md` file and execute its steps. Do NOT treat them as unknown commands.

<!-- WORKFLOWS_TABLE_START -->
| Command | Workflow file | Purpose |
| :--- | :--- | :--- |
| `/audit-plugin` | `.agent/workflows/audit-plugin.md` | Perform a full or partial plugin audit using qgis-plugin-analyzer v1.9.0+. |
| `/build-feature` | `.agent/workflows/build-feature.md` | Start the Autonomous AI Developer Pipeline sequence for a new feature. |
| `/close-phase` | `.agent/workflows/close-phase.md` | Formal procedure for closing a major development phase |
| `/close-session` | `.agent/workflows/close-session.md` | Procedure to end a work session, update logs, and archive results |
| `/create-commit` | `.agent/workflows/create-commit.md` | How to commit changes cleanly (handling hooks) |
| `/fix-linting` | `.agent/workflows/fix-linting.md` | Workflow to automatically correct linting and formatting issues |
| `/i18n-maintenance` | `.agent/workflows/i18n-maintenance.md` | Procedure for i18n maintenance and expansion (Translations) |
| `/ia-critic` | `.agent/workflows/ia-critic.md` | Workflow for critical review of implementation plans by the Agent Auditor |
| `/refactor-code` | `.agent/workflows/refactor-code.md` | Guided workflow for code refactoring with complexity validation |
| `/release-plugin` | `.agent/workflows/release-plugin.md` | Unified Release Workflow (QGIS Release Flow) - Generation 6 Standard |
| `/run-tests-in-qgis` | `.agent/workflows/run-tests-in-qgis.md` | How to run tests inside QGIS (integration testing) |
| `/run-tests` | `.agent/workflows/run-tests.md` | How to run unit tests reliably |
| `/start-phase` | `.agent/workflows/start-phase.md` | Formal procedure for starting a new major development phase |
| `/start-session` | `.agent/workflows/start-session.md` | Standard and robust procedure for starting a "Local First" development session |
| `/verify-standards` | `.agent/workflows/verify-standards.md` | Audits the consistency of the agentic system (Skills and Workflows) against the master standard. |
<!-- WORKFLOWS_TABLE_END -->

Full index: `.agent/workflows/index.md`

---

## 🚀 Build/Lint/Test Commands

### Core Commands
```bash
# Environment setup
make init                    # Initialize complete dev environment (proposed)
uv sync                     # Install dependencies

# Building and deployment
make compile                 # Compile resources and UI
make deploy                  # Deploy to QGIS plugins directory
make zip                     # Create distributable package

# Testing
make test                    # Run full test suite (unittest discovery)
uv run pytest tests/         # Alternative pytest runner
make docker-test             # Run 361+ tests in Docker environment

# Single test execution
uv run pytest tests/core/test_algorithms.py::test_intersection -v
uv run python -m unittest tests.test_geology_service.TestGeologyService.test_method
```

### Code Quality
```bash
make pylint                  # Run static analysis
make pep8                    # Run ruff style checking
uv run ruff check .          # Direct ruff linting
uv run ruff format .         # Auto-format code
pre-commit run --all-files   # Run all pre-commit hooks
```

---

## 🏗️ Architectural Principles

### Core/GUI Separation (CRITICAL)
The project follows a strict **Extract-then-Compute** pattern:

1. **GUI Layer (`/gui`)**: Extracts data from QGIS objects into DTOs
2. **Core Layer (`/core`)**: Processes using QGIS-agnostic types (WKT, dicts, primitives)
3. **Results**: Core returns validated DTOs, GUI converts back to QGIS if needed

#### NEVER do this in `/core`:
```python
# ❌ FORBIDDEN - Direct QGIS dependencies in core
from qgis.core import QgsVectorLayer, QgsProject
layer = QgsProject.instance().mapLayerByName("geology")

# ❌ FORBIDDEN - GUI dependencies
from qgis.gui import QgsMapTool
iface.mapCanvas().refresh()
```

#### ALWAYS do this in `/core`:
```python
# ✅ CORRECT - Use primitive types and WKT
def process_geology(geometry_wkt: str, attributes: dict) -> GeologySegment:
    # Pure business logic with thread-safe operations
    return GeologySegment(geometry=geometry_wkt, props=attributes)
```

### Thread Safety Requirements
- Core services must be thread-safe for background processing
- Use `QgsTask` for heavy operations in GUI layer
- No live QGIS objects in background threads
- Prefer WKT over QgsGeometry in core processing

---

## 📝 Code Style Guidelines

### Import Organization
```python
from __future__ import annotations  # REQUIRED in all modules

# Standard library
import os
import logging
from typing import Dict, List, Optional

# Third-party
from PyQt5.QtCore import QObject, Signal
from qgis.core import QgsVectorLayer, QgsFeature

# Local imports (absolute)
from sec_interp.core.exceptions import ValidationError
from sec_interp.core.types import ProfileData
```

### Type Annotations (REQUIRED)
```python
def calculate_intersection(
    line_wkt: str,
    polygon_wkt: str,
    tolerance: float = 0.001
) -> Optional[GeologySegment]:
    """Calculate line-polygon intersection.

    Args:
        line_wkt: Line geometry in WKT format
        polygon_wkt: Polygon geometry in WKT format
        tolerance: Intersection tolerance in map units

    Returns:
        GeologySegment if intersection exists, None otherwise

    Raises:
        ValidationError: If input geometries are invalid
    """
```

### Naming Conventions
```python
# Classes: PascalCase
class GeologyService:
class ValidationError:

# Functions/Variables: snake_case
def parse_strike_dip(data: dict) -> tuple[float, float]:
buffer_distance = 50.0

# Constants: UPPER_SNAKE_CASE
MAX_SAMPLES = 1000
DEFAULT_TOLERANCE = 0.001

# Private members: Leading underscore
def _validate_core_params(self, params: dict) -> bool:
```

### Error Handling Patterns
```python
# Use custom exception hierarchy
class ValidationError(SecInterpError):
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field

# Structured error handling
try:
    result = process_data(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    return False, e.message
except Exception as e:
    logger.exception(f"Unexpected error in process_data")
    raise
```

---

## 🔧 Development Workflow

### 1. Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/new-geological-algorithm

# 2. Make changes (following style guidelines)
# 3. Run quality checks
uv run ruff check .
uv run ruff format .
make pylint

# 4. Run tests
uv run pytest tests/core/test_new_feature.py -v
make docker-test  # Full integration test
```

### 2. Testing Strategy
```bash
# Core logic tests (standalone, no QGIS required)
uv run pytest tests/core/ -v

# Integration tests (require QGIS)
uv run pytest tests/integration/ -v

# Run with unittest (standard discovery)
uv run python -m unittest discover tests/ -p "test_*.py"

# Performance benchmarks
uv run pytest tests/benchmarks/ -v

# Single test with coverage
uv run pytest tests/core/test_algorithms.py::test_intersection -v --cov=core.algorithms
```

### 3. Testing Standards (unittest)
The project strictly uses the `unittest` framework with a **Mock-First** approach to ensure fast, isolated, and QGIS-independent unit tests.

#### Foundation: BaseTestCase
All test classes **MUST** inherit from `BaseTestCase` defined in `tests/base_test.py`.
```python
from tests.base_test import BaseTestCase

class TestMyModule(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Custom setup logic
```
- **Benefits**: Automatic environment setup, mock injection, and temporary directory management.
- **Cleanup**: `tearDown()` in `BaseTestCase` handles mock resets and file cleanup.

#### Naming Conventions
- **Files**: `test_*.py` (e.g., `test_geology_service.py`)
- **Classes**: `Test[ModuleName]` (e.g., `TestGeologyService`)
- **Methods**: `test_[behavior]` (e.g., `test_calculate_intersection_valid`)

#### The "Mock-First" Rule (CRITICAL)
Tests in `tests/core/` and `tests/gui/` should **never** require a real QGIS installation.
- Use `tests.base_test.mock_core` and `mock_gui` for QGIS interaction.
- Use `unittest.mock` for external dependencies (file system, network).
- **Prohibited**: Importing `qgis.testing` or requiring `xvfb` for unit tests.

#### Best Practices
1. **Assertion Styles**: Prefer `self.assertEqual`, `self.assertTrue`, `self.assertRaises` over bare `assert`.
2. **Layer Validation**: Always mock `layer.isValid()` to return `True` for valid test scenarios.
3. **WKT Communication**: Use WKT strings to mock geometries instead of complex `QgsGeometry` objects where possible.
4. **Isolation**: Ensure tests do not depend on each other's state.

### 4. Commit Standards
- Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Pre-commit hooks enforce formatting and commit message standards
- Each commit should pass tests locally

---

## 📊 Project Structure Overview

```
core/                    # 🧠 Pure business logic (QGIS-agnostic)
├── services/           # Data processing services
├── utils/              # Utility functions
├── types.py             # Domain types and DTOs
├── exceptions.py       # Custom exception hierarchy
└── validation/         # Validation framework

gui/                     # 🖥️ UI and QGIS interaction layer
├── tasks/              # Background processing (QgsTask)
├── tools/              # Interactive tools
├── ui/pages/           # UI components
└── services/           # GUI-specific services

exporters/               # 📤 Data export functionality
tests/                   # 🧪 Comprehensive test suite
├── core/               # Core logic tests (standalone)
├── integration/        # Full QGIS integration tests
└── benchmarks/         # Performance tests
```

---

## ⚡ Performance Guidelines

### 1. Core Processing
- Use NumPy for numerical operations where applicable
- Implement caching for expensive calculations
- Profile critical paths with `@performance_metrics.track()`

### 2. GUI Operations
- Use `QgsTask` for operations > 100ms
- Implement progress reporting for user feedback
- Batch QGIS operations to minimize canvas refreshes

---

## 🛡️ Quality Assurance

### 1. Code Quality Gates
- All code must pass `ruff check` and `ruff format`
- Pylint score > 8.0 required
- Test coverage > 80% for new features

### 2. Testing Requirements
- Unit tests for all new functions/classes
- Integration tests for QGIS interactions
- Performance tests for algorithmic changes

### 3. Documentation
- Docstrings following Google style for all public APIs
- Type annotations required for all function signatures
- Update relevant documentation for API changes

---

## 🔍 Debugging & Development Tips

### 1. QGIS Development
```bash
# Source QGIS environment for development
source /path/to/qgis/share/qgis/python/qgisenv.sh

# Debug QGIS plugins
export QGIS_DEBUG=3
export QGIS_LOG_FILE=qgis_debug.log
```

### 2. Common Issues
- **Import errors**: Ensure `uv sync` has been run and environment is activated
- **QGIS not found**: Check that QGIS Python environment matches development environment
- **Thread crashes**: Verify no QGIS GUI objects are used in background threads

---

## 🛠️ Agent Skills

Skills live in `.agent/skills/*/SKILL.md`. Read the relevant `SKILL.md` on demand; do not pre-load all of them.

| Skill | Description | When to use |
| :--- | :--- | :--- |
| [agentic-memory](.agent/skills/agentic-memory/SKILL.md) | Manages semantic memory (lessons, patterns, user preferences) for long-term effectiveness. | End of each significant session; when detecting repetitive error patterns or user preferences. |
| [changelog-generator](.agent/skills/changelog-generator/SKILL.md) | Creates user-facing changelogs from git commits. | Preparing release notes, updating CHANGELOG.md, `/release-plugin`, `/close-session`, `/close-phase`. |
| [coding-standards](.agent/skills/coding-standards/SKILL.md) | Project coding standards (pathlib, Google docstrings, strict typing). | Writing Python code, refactoring, defining file paths. |
| [commit-standards](.agent/skills/commit-standards/SKILL.md) | Clean, conventional commits with quality validation. | Creating commits, `/create-commit`. |
| [documentation-standards](.agent/skills/documentation-standards/SKILL.md) | Standards for technical logs, session records, and project history. | Updating DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md, session reports. |
| [geological-logic](.agent/skills/geological-logic/SKILL.md) | Drillhole data, section interpolation, 3-level validation. | Geological algorithms, data validation, drillhole processing. |
| [i18n-standards](.agent/skills/i18n-standards/SKILL.md) | Internationalization (i18n) standards and best practices. | User-facing strings, translation tools, triaging MISSING_I18N flags, `/i18n-maintenance`. |
| [project-context](.agent/skills/project-context/SKILL.md) | Purpose, architecture, and structure of SecInterp. | Starting tasks, requesting summaries, explaining architecture. |
| [qa-docker](.agent/skills/qa-docker/SKILL.md) | Dockerized testing and Mock-first QGIS testing. | Writing/executing tests, using mocks, Docker infrastructure. |
| [qgis-core](.agent/skills/qgis-core/SKILL.md) | QGIS API, plugin structure, asynchronous `QgsTask`. | PyQGIS, layers, CRS, QgsTask. |
| [qgis-migration-4x](.agent/skills/qgis-migration-4x/SKILL.md) | QGIS 4.x migration and agnostic API usage. | qgis.PyQt imports, Qt deprecation warnings, 4.x readiness. |
| [release-management](.agent/skills/release-management/SKILL.md) | QGIS plugin release process with quality validation. | Releases, versioning, `/release-plugin`. |
| [ui-framework](.agent/skills/ui-framework/SKILL.md) | Custom SecInterp UI (programmatic creation, premium aesthetics). | GUI widgets, layouts, CSS styles. |

---

## 📚 Key Resources

- **Architecture**: `docs/ARCHITECTURE_EN.md`
- **Core Distinction**: `docs/CORE_DISTINCTION_GUIDE_EN.md`
- **Agent Configuration**: this file (root `AGENTS.md`) — canonical
- **Skills**: `.agent/skills/*/SKILL.md`
- **Development**: `README_DEV.md`

---

## ⚠️ Critical Reminders

1. **NEVER** import `qgis.gui` in `/core` modules
2. **ALWAYS** follow the Extract-then-Compute pattern
3. **MAINTAIN** thread safety in core services
4. **USE** type annotations everywhere
5. **RUN** tests before committing changes
6. **FOLLOW** the established naming and formatting conventions

This project maintains high architectural standards to ensure long-term maintainability and performance. Respect these principles in all contributions.
