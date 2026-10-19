# Testing Guide for the SecInterp Plugin

## Overview

The suite uses the standard-library **`unittest`** framework with a **Mock-First**
approach: `tests/core/`, `tests/gui/` and `tests/exporters/` run without a QGIS
installation. `tests/integration/` uses a real `QgsApplication` and runs in the QGIS
Docker image.

- **778 tests** across 122 files.
- Test base class: `tests/base_test.py::BaseTestCase` (mock injection, temp dirs,
  cleanup).
- QGIS/PyQt mocks: `tests/mocks/`.
- Current inventory: [`tests/TESTING_STATUS.md`](TESTING_STATUS.md).

---

## Running the suite

```bash
# Full local suite (mock-first, no QGIS required)
PYTHONPATH=.. uv run python3 -m unittest discover tests

# A single module or test
PYTHONPATH=.. uv run python3 -m unittest tests.core.test_algorithms -v
PYTHONPATH=.. uv run python3 -m unittest \
  tests.core.test_algorithms.TestAlgorithms.test_intersection -v

# By category
PYTHONPATH=.. uv run python3 -m unittest discover tests/core
PYTHONPATH=.. uv run python3 -m unittest discover tests/gui
PYTHONPATH=.. uv run python3 -m unittest discover tests/exporters
PYTHONPATH=.. uv run python3 -m unittest discover tests/agentic

# Integration tests (real QGIS; Docker is recommended)
PYTHONPATH=.. FORCE_MOCKS=0 uv run python3 -m unittest discover tests/integration

# Full health check in the QGIS container
make docker-test
```

`forge.toml` also records the canonical commands under
`[project] test_command` and `test_command_docker`.

---

## Test structure

```
tests/
├── base_test.py          # BaseTestCase + mock wiring
├── mocks/                # QGIS/PyQt mock implementations
├── core/                 # Pure logic (no QGIS)
├── gui/                  # GUI/pages/managers (mocked)
├── exporters/            # Export formats (mocked)
├── integration/          # Real QgsApplication + QGIS API
├── benchmarks/           # Performance checks
├── agentic/              # Agentic tooling tests
└── TESTING_STATUS.md     # Generated inventory and counts
```

---

## Writing new tests

Inherit from `BaseTestCase` and follow the `test_<behavior>` naming convention:

```python
from tests.base_test import BaseTestCase


class TestMyFeature(BaseTestCase):
    def test_my_function_handles_empty_input(self):
        from sec_interp.core.utils import my_function

        self.assertEqual(my_function([]), [])
```

Rules:

1. **Mock-first**: never require a real QGIS installation in `tests/core/` or
   `tests/gui/`; use `tests.base_test` and `tests.mocks`.
2. **No invented mock methods**: a mock must mirror the real Qt/PyGIS API. If a method
   does not exist in the real class, do not add it to satisfy production code.
3. **WKT over geometry objects** at the core boundary.
4. **Isolation**: each test must be independent; clean up files and signal connections.
5. **Assertions**: use `self.assertEqual`, `self.assertTrue`, `self.assertRaises`, etc.
6. **Process isolation**: do not mix mock-based and real-QGIS tests in the same process.

---

## Coverage

`coverage` is configured in `pyproject.toml` but is not a mandatory dependency. If it is
installed:

```bash
PYTHONPATH=.. uv run coverage run -m unittest discover tests
uv run coverage report
```

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'qgis'`**: the mock bootstrap did not run.
  Import the test through `tests/__init__.py`/`BaseTestCase`, or use the integration
  suite only inside the QGIS Docker image.
- **`ImportError` for `sec_interp.*`**: run from the repository root with
  `PYTHONPATH=..`.
- **A mock test passes but real QGIS crashes**: verify that the mocked method exists on
  the real Qt class and smoke-test the path in QGIS.
- **Tests pass locally but fail in Docker**: run `make docker-test`; the integration
  categories run with `FORCE_MOCKS=0` against the real QGIS API.
