# How to Run qgis-analyzer in Dev Container

I have configured the Dev Container to automatically install all project dependencies, including `qgis-plugin-analyzer`, using `uv`.

## Changes Made

- **Updated `Dockerfile`**: Now copies `pyproject.toml` and `uv.lock` and runs `uv sync` during the build process. This ensures dependencies are pre-installed in the image.
- **Updated `.devcontainer/devcontainer.json`**: Configured to build the image from the `Dockerfile` locally, rather than pulling a pre-built image.

## Verification Steps

To use the new configuration:

1. **Rebuild Container**: In VS Code, run the **Dev Containers: Rebuild Container** command.
2. **Open Terminal**: Once connected, open a terminal inside VS Code.
3. **Run Analyzer**: execute the command:
   ```bash
   qgis-analyzer --help
   ```
   Or to run the analysis on the project:
   ```bash
   qgis-analyzer
   ```

> [!NOTE]
> Examples of running tests inside the container:
> ```bash
> python -m unittest discover tests
> ```
> Since the virtual environment is added to `PATH`, you generally don't need `uv run`, but you can still use it if you prefer.
