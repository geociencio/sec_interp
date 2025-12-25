# Testing Guide for SecInterp Plugin

## Overview

This plugin includes two types of tests:
1. **Standalone tests** - Can run without QGIS installation
2. **Full tests** - Require QGIS environment

---

## Running Standalone Tests

These tests cover parsing and calculation functions that don't depend on QGIS:

```bash
# Activate virtual environment
cd /home/jmbernales/qgispluginsdev/sec_interp
source .venv/bin/activate

# Run standalone tests
uv run pytest tests/test_utils_standalone.py -v

# Run with coverage
uv run pytest tests/test_utils_standalone.py --cov=core.utils --cov-report=term-missing
```

**What's tested**:
- Strike parsing (numeric and quadrant notation)
- Dip parsing (numeric and with direction)
- Cardinal direction conversion
- Apparent dip calculation
- Elevation interpolation

---

## Running Full Tests (Requires QGIS)

Full tests require QGIS Python environment:

```bash
# Option 1: Using QGIS Python Console
# Open QGIS → Plugins → Python Console
# Run:
import sys
sys.path.insert(0, '/home/jmbernales/qgispluginsdev/sec_interp')
import pytest
pytest.main(['-v', 'tests/'])

# Option 2: Using QGIS Python directly
/usr/bin/python3-qgis -m pytest tests/ -v
```

**What's tested**:
- All standalone tests
- Validation functions
- Exporters (CSV, Shapefile, PDF, etc.)
- QGIS-dependent utilities

---

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures
├── test_utils_standalone.py     # No QGIS required ✓
├── test_utils.py                # Requires QGIS
├── test_validation.py           # Requires QGIS
└── test_exporters.py            # Requires QGIS
```

---

## Writing New Tests

### Standalone Test Example

```python
def test_my_function():
    \"\"\"Test description.\"\"\"
    from core.utils import my_function

    result = my_function(input_data)
    assert result == expected_value
```

### QGIS-Dependent Test Example

```python
from qgis.core import QgsVectorLayer

def test_qgis_function():
    \"\"\"Test with QGIS objects.\"\"\"
    layer = QgsVectorLayer("Point", "test", "memory")
    assert layer.isValid()
```

---

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run specific markers:
```bash
pytest -m unit          # Run only unit tests
pytest -m "not slow"    # Skip slow tests
```

---

## Coverage Reports

Generate coverage reports:

```bash
# Terminal report
uv run pytest tests/test_utils_standalone.py --cov=core --cov-report=term-missing

# HTML report
uv run pytest tests/test_utils_standalone.py --cov=core --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Continuous Integration

For CI/CD pipelines, use standalone tests:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install pytest pytest-cov
      - run: pytest tests/test_utils_standalone.py --cov
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'qgis'"

**Solution**: Use standalone tests or run from QGIS Python environment

### "ImportError: cannot import name 'X'"

**Solution**: Check that module is in PYTHONPATH:
```python
import sys
sys.path.insert(0, '/path/to/sec_interp')
```

### Tests pass locally but fail in CI

**Solution**: Ensure using standalone tests in CI, or install QGIS in CI environment

---

## Best Practices

1. **Keep tests fast** - Standalone tests should run in < 1 second
2. **Use fixtures** - Reuse test data via conftest.py
3. **Test edge cases** - Empty data, None values, invalid input
4. **Mock QGIS objects** - When possible, mock instead of using real QGIS
5. **Document assumptions** - Add comments explaining test logic

---

## Current Test Coverage

**Standalone Tests** (✓ Working):
- Strike parsing: 7 tests
- Dip parsing: 4 tests
- Cardinal conversion: 2 tests
- Apparent dip: 3 tests
- Interpolation: 4 tests

**Total**: 20 tests covering core parsing and calculation functions

**Next Steps**:
- Add validation tests (requires QGIS)
- Add exporter tests (requires QGIS)
- Increase coverage to >70%
