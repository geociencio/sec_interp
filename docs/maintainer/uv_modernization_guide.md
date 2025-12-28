# QGIS Plugin Modernization Guide with `uv`

This document details the standard procedure for modernizing the development environment of existing QGIS projects, migrating from `pip`/`requirements.txt` to `uv`/`pyproject.toml`.

## 1. Analysis and Cleanup Phase

Before migrating, identify and eliminate technical debt.

1.  **Dependency Audit**: Review `requirements.txt` and `requirements-dev.txt`.
2.  **Remove Obsolete Tools**:
    -   If `pb_tool.cfg` exists, plan its replacement.
    -   If fragile bash scripts (`deploy.sh`) exist, plan their replacement with `qgis-plugin-manager`.
    -   Identify scattered configuration files (`pytest.ini`, `.pylintrc`, `ruff.toml`).

## 2. Initialize `uv`

Centralize configuration in `pyproject.toml`.

1.  **Install uv** (if not installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Initialize Project**:
    ```bash
    uv init
    ```
3.  **Define Dependencies**:
    Edit `pyproject.toml` to include:
    -   `dependencies`: Runtime libraries (e.g., `PyQt5`, `requests`).
    -   `dependency-groups.dev`: Development tools.

    ```toml
    [project]
    name = "my-plugin"
    requires-python = ">=3.10"
    dependencies = ["PyQt5"]

    [dependency-groups]
    dev = [
        "pytest",
        "ruff",
        "qgis-plugin-ci",
        "qgis-plugin-manager @ git+https://github.com/geociencio/qgis-plugin-manager.git"
    ]
    ```

## 3. Configuration Migration

Move all scattered configurations to `pyproject.toml`.

1.  **Ruff (Linter/Formatter)**:
    Migrate rules from `ruff.toml` to `[tool.ruff]`.
2.  **Pytest**:
    Migrate `pytest.ini` to `[tool.pytest.ini_options]`.
3.  **Pylint** (if used):
    Migrate `.pylintrc` to `[tool.pylint]`.

**Action**: Delete old files once migrated.

## 4. Implement Modern Tools

Replace ad-hoc scripts with standard tools.

1.  **Local Management**: Use `qgis-plugin-manager`.
    -   Install: `uv add --group dev qgis-plugin-manager @ git+...`
    -   Deploy: `uv run qgis-manage deploy`
2.  **Packaging**: Use `qgis-plugin-ci`.
    -   Replace manual `git archive` or `zip` tasks.
    -   Package: `uv run qgis-plugin-ci package 1.0.0`

## 5. Update Makefile

Simplify the `Makefile` to act as a wrapper for `uv`.

```makefile
deploy:
    uv run qgis-manage deploy

test:
    uv run pytest

lint:
    uv run ruff check .
```

## 6. Synchronization

Finally, generate the virtual environment and lock file.

```bash
uv sync --all-groups
```

## Benefits
-   **Speed**: Environment installation in milliseconds.
-   **Reproducibility**: `uv.lock` ensures the same versions across all machines.
-   **Centralization**: A single file (`pyproject.toml`) governs the entire project.

## 7. Documentation Modernization

If your project uses Sphinx, modernize the build process.

1.  **Add Dependencies**:
    ```bash
    uv add --group doc sphinx sphinx-rtd-theme
    ```
2.  **Update Makefile**:
    ```makefile
    docs:
        uv run sphinx-build docs/source docs/build/html
    ```

## 8. CI/CD Integration

Modernize your GitHub Actions workflows to use `uv`.

Example `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - name: Install QGIS dependencies
        run: sudo apt-get install qgis
      - name: Run Tests
        run: uv run pytest
```

## 9. IDE Integration (VS Code)

To ensure VS Code uses the correct environment managed by `uv`:

1.  **Select Interpreter**:
    -   Press `Ctrl+Shift+P` -> `Python: Select Interpreter`.
    -   Choose the interpreter path: `./.venv/bin/python`.

2.  **Settings (`.vscode/settings.json`)**:
    Configure test discovery and linting to use `uv run`.

    ```json
    {
      "python.defaultInterpreterPath": ".venv/bin/python",
      "python.testing.pytestEnabled": true,
      "python.testing.pytestArgs": ["tests"],
      "python.analysis.typeCheckingMode": "basic"
    }
    ```

## 10. Automated Quality (Pre-commit)

Integrate pre-commit hooks managed by `uv`.

1.  **Add Dependency**:
    ```bash
    uv add --group dev pre-commit
    ```
2.  **Config**: Create `.pre-commit-config.yaml` with standard hooks (trailing-whitespace, end-of-file-fixer, ruff).
3.  **Install**:
    ```bash
    uv run pre-commit install
    ```
