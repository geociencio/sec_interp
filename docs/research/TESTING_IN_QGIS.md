# Testing Inside QGIS (No Mocks Required) 🌍

If you want to run tests that interact with the real `qgis` API (without mocking), you can execute them directly inside the **QGIS Runtime** (e.g., via the Python Console).

## Why do this?
- **Real Integration**: Verify that your code works with the actual C++ bindings.
- **No Mocks**: `qgis.core`, `iface`, and `qgis.gui` are fully available.
- **Visual Feedback**: You can see layers being loaded or UI widgets appearing.
- **GUI Testing**: Test components that require the actual QGIS interface.

## When to Use This Approach

### ✅ Use QGIS In-Process Testing For:
- Testing GUI components that require `iface`
- Verifying actual QGIS API behavior (not mocked)
- Visual debugging of layer rendering
- Integration tests with real QGIS environment

### ⚠️ Use Standard unittest (with mocks) For:
- Unit tests of business logic
- CI/CD pipelines (faster, no GUI required)
- Rapid test-driven development
- Testing core algorithms without QGIS dependencies

## Workflow

### 1. The Test Runner Script
The project includes `scripts/run_tests_in_qgis.py` which auto-detects the project structure and configures the environment correctly.

**Key features**:
- Auto-detects project root using `pathlib`
- Adds parent directory to `sys.path` for `sec_interp` package resolution
- Configures logging for QGIS console output
- Discovers all `test_*.py` files in the `tests/` directory

### 2. Execution in QGIS
1. Open **QGIS**.
2. Open the **Python Console** (`Ctrl+Alt+P` or `Plugins → Python Console`).
3. Click the **"Show Editor"** button (notepad icon).
4. Open the `scripts/run_tests_in_qgis.py` file.
5. Click **Run Script** (Play button ▶️).

### 3. CI/CD (Headless)
For CI, you can use `qgis_process` or launch QGIS with a startup script:

```bash
qgis --nologo --code scripts/run_tests_in_qgis.py
```

**Note**: Headless testing requires proper QGIS installation and may need additional configuration for display servers (Xvfb on Linux).

## Comparison with Standard Testing

| Aspect | Standard unittest | QGIS In-Process |
|--------|------------------|-----------------|
| **Command** | `PYTHONPATH=.. uv run python3 -m unittest discover` | Run script in QGIS Console |
| **Speed** | Fast | Slower (QGIS startup) |
| **Dependencies** | Mocked QGIS APIs | Real QGIS APIs |
| **Use Case** | Unit tests, CI/CD | Integration, GUI testing |
| **Debugging** | IDE debugger | QGIS Console + print |

---
**See also**: `.agent/workflows/run-tests.md` for standard testing workflow.
