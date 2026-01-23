---
description: How to run tests inside QGIS (integration testing)
agent: QA Engineer
skills: [qa-docker]
validation: |
  - Verificar que QGIS está instalado correctamente
  - Confirmar que tests se descubren y ejecutan
  - Validar que no hay errores de importación
---
This workflow describes how to run tests inside the QGIS environment using the real QGIS APIs (no mocks). This is useful for integration testing and GUI component verification.

## When to Use This

🤖 **Agent Action**: Usar skill **qa-docker** para determinar si tests requieren QGIS real o mocks.

Use QGIS in-process testing when:
- Testing GUI components that require `iface`
- Verifying actual QGIS API behavior (not mocked)
- Visual debugging of layer rendering
- Integration tests with real QGIS environment

For standard unit tests, use the `run-tests.md` workflow instead (faster, better for CI/CD).

## Steps

1. Open QGIS application.

2. Open the Python Console:
   - Menu: `Plugins → Python Console`
   - Or keyboard shortcut: `Ctrl+Alt+P`

3. In the Python Console, click the **"Show Editor"** button (notepad icon).

4. Open the test runner script:
   ```
   scripts/run_tests_in_qgis.py
   ```

5. Click the **Run Script** button (Play icon ▶️).

6. Watch the test output in the console. The script will:
   - Auto-detect the project root
   - Add the parent directory to `sys.path` for package resolution
   - Discover all `test_*.py` files in `tests/`
   - Run them with `unittest.TextTestRunner`

## Expected Output

```
============================================================
🚀 Starting Test Run in QGIS Environment
📂 Project Root: /path/to/sec_interp
============================================================
📦 Adding to sys.path: /path/to/qgispluginsdev
test_example (tests.test_module.TestClass) ... ok
...
----------------------------------------------------------------------
Ran X tests in Y.ZZZs

✅ SUCCESS: All tests passed!
```

## Headless Execution (CI/CD)

For automated testing without GUI:

```bash
qgis --nologo --code scripts/run_tests_in_qgis.py
```

**Note**: Requires proper QGIS installation and may need Xvfb on Linux.

## Troubleshooting

- **Import errors**: Verify that `sys.path` includes the parent directory
- **QGIS not found**: Ensure QGIS is properly installed
- **Tests not discovered**: Check that test files follow `test_*.py` naming convention
