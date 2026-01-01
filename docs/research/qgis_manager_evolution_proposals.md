# Proposal: Evolution Plan for qgis-plugin-manager

This document outlines the strategic improvement plan for `qgis-plugin-manager`, focusing on integration with the existing team ecosystem (specifically `qgis-analyzer`) and enhancing the developer experience.

## 1. Quality Gates Integration (Orchestration)

Integrate `qgis-plugin-manager` with `qgis-analyzer` to enforce quality standards before deployment.

*   **Feature**: Add a `min_score` parameter in `pyproject.toml` or `config.toml`.
*   **Workflow**: When running `qgis-manage deploy`, the tool automatically triggers `qgis-analyzer`.
*   **Enforcement**: If the analyzer score is below the threshold, the deployment is aborted.
*   **Benefit**: Ensures that no substandard code reaches the local QGIS profile or the repository.

## 2. Interactive "Watch Mode" with Real-time Feedback

Create a live-development environment.

*   **Feature**: `qgis-manage watch` command.
*   **Workflow**:
    1.  Monitor changes in `.py`, `.qrc`, and `.md` files.
    2.  On change: Trigger `qgis-manage deploy`.
    3.  Simultaneously: Trigger `qgis-analyzer` and display the updated score in the console.
*   **Benefit**: Immediate feedback loop for both functionality and code quality.

## 3. Intelligent Dependency Vendoring

Solve the "third-party library" problem in QGIS environments.

*   **Feature**: `qgis-manage install` command or `vendoring` configuration.
*   **Workflow**:
    1.  Read requirements from `pyproject.toml` or `requirements.txt`.
    2.  Install dependencies into a specific `libs/` or `external/` folder inside the plugin.
    3.  Automatically inject a path-handling snippet into the plugin's `__init__.py`.
*   **Benefit**: Makes plugins truly self-contained and portable across different QGIS installations.

## 4. Standardized Team Templates

Ensure consistency across all organizational projects.

*   **Feature**: Remote template support for `qgis-manage init`.
*   **Workflow**:
    1.  Allow `init` to point to a central templates repository (e.g., `github.com/geociencio/templates`).
    2.  Provide specific blueprints for "Processing Algorithms", "GUI Tools", and "Map Tools".
*   **Benefit**: All projects start with the same high-quality base, including pre-configured `Makefile`, `docs/`, and `qgis-analyzer` rules.

## 5. Advanced Environment Profiles

Move beyond just simple QGIS profile folders.

*   **Feature**: Define per-environment configurations in `pyproject.toml` (e.g., `[tool.qgis-manager.profiles.dev]` vs `[tool.qgis-manager.profiles.release]`).
*   **Workflow**:
    - `dev`: Skip documentation compilation, enable debug symbols, no minification.
    - `release`: Strict validation, full documentation build, clean artifacts.
*   **Benefit**: Tailored workflows for different development stages.

## 6. Containerized Testing Support

Seamless cross-version compatibility verification.

*   **Feature**: Integration with Docker images (e.g., `qgis/qgis`).
*   **Workflow**: Run the plugin's test suite inside a containerized QGIS environment with a single command (`qgis-manage test --docker`).
*   **Benefit**: Verify compatibility with QGIS 3.22 LTR, 3.28, or 3.34+ without needing multiple local installations.

---
**Status**: Proposal for Review (Updated)
**Date**: 2025-12-29
🚀 Opciones de Mejora
1. Sistema de "Profiles" Avanzado
Actualmente el profile se limita al nombre de la carpeta en QGIS.

Mejora: Permitir definir en el
pyproject.toml
 configuraciones por perfil (ej: un perfil dev que no compile docs y un perfil release que haga validación estricta y limpieza profunda).
Beneficio: Flexibilidad total para diferentes etapas del desarrollo.
2. Auditoría de Código (Linting Integrado)
El comando validate solo revisa el metadata.txt.

Mejora: Integrar un comando qgis-manage check que ejecute internamente ruff o flake8-qgis (si existiera) para asegurar que el código sigue los estándares de PyQGIS.
Beneficio: Calidad de código garantizada antes de siquiera intentar un despliegue.
3. Manejo de Dependencias Externas (Vendoring)
Muchos plugins necesitan librerías de PyPI que no están en el QGIS del usuario.

Mejora: Implementar un sistema de "vendoring" automático donde qgis-manage instale dependencias específicas en una carpeta libs/ dentro del plugin y ajuste el
init
.py
 para incluirlas en el sys.path.
Beneficio: Elimina el dolor de cabeza de las dependencias en entornos QGIS restringidos.
4. Generación de Boilerplate (Templating)
El comando init es muy básico.

Mejora: Usar plantillas (tipo cookiecutter) para que el usuario pueda elegir entre "Plugin de Procesamiento", "Plugin con GUI (Qt)", o "Plugin de Herramienta de Mapa".
Beneficio: Ahorra horas de configuración inicial de archivos repetitivos.
5. Watch Mode (Live Reload)
Mejora: Un comando qgis-manage watch que monitoree cambios en los archivos
.py
, .qrc o
.md
 y ejecute deploy automáticamente.
Beneficio: Desarrollo ultra-rápido; haces un cambio en el código y en 1 segundo ya está actualizado en QGIS (solo faltaría darle al botón de "Reload" en QGIS).
