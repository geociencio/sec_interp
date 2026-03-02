---
description: Proceso unificado de liberación (QGIS Release Flow) basado en la guía de IA
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards, i18n-standards]
validation: |
  - Verificar que 455+ tests pasan en Docker
  - Confirmar que qgis-analyzer score > 25/100
  - Asegurar Zero High-Severity Security Findings (`security --deep`)
  - Validar que versiones están sincronizadas en 3 archivos
  - Verificar que ZIP se generó correctamente
---

Sigue este flujo de 5 fases para realizar una liberación oficial del plugin SecInterp.

### Fase 1: Calidad y Preparación

🤖 **Agent Action**: Usar skill **release-management** para validar checklist completo de pre-release.

1. **Analizar Calidad**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   ```

   🤖 **Agent Action**: Verificar que:
   - Overall Plugin Score > 25/100
   - No hay violaciones críticas de QGIS compliance
   - **Nota**: Descartar falsos positivos de i18n en docstrings si `core/` tiene cobertura 100%.

2. **Actualizar Badges**: Actualizar `Code Quality` y `QGIS Compliance` en `README.md` según los resultados.

### Fase 2: Versionamiento y Documentación

🤖 **Agent Action**: Usar skill **release-management** para sincronizar versiones automáticamente.

1. **Sincronizar Versión (Semantic Versioning)**:
   - Acatar `X.Y.Z` (Major.Minor.Patch).
   - Actualizar `version` y `changelog` explícitamente en `metadata.txt`.
     - ⚠️ **CRÍTICO**: Escapar todo `%` como `%%` en el changelog (e.g., `100%%` no `100%`).
   - Actualizar `version` en `pyproject.toml`.
   - Actualizar el badge de versión en `README.md`.

   🤖 **Agent Action**: Validar que las 3 versiones coinciden exactamente.

2. **Changelog Técnico (Keep A Changelog)**: Mover `[Unreleased]` a la nueva versión en `docs/CHANGELOG.md` y sincronizar `docs/docsec/CHANGELOG.md` (Español) usando los tipos válidos (`Added`, `Changed`, `Fixed`, etc).

3. **Notas de Lanzamiento**:
   // turbo
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

   🤖 **Agent Action**: Generar release notes estructuradas siguiendo template de skill **release-management**.

### Fase 3: Verificación

🤖 **Agent Action**: Usar skill **qa-docker** para validar tests y skill **commit-standards** para linting.

1. **Security Scan** (Deep Audit):
   // turbo
   ```bash
   uv run qgis-analyzer security --deep .
   ```

   🤖 **Agent Action**: Revisar reportes de seguridad. No se permiten hallazgos de severidad ALTA para proceder.

2. **Linting & Formatting**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run black .
   ```
   **Nota**: Documentar issues de linting menores (como F821/W503 en reportes externos) para fix posterior si no bloquean funcionalidad.
3. **Tests**:
   // turbo
   ```bash
   make docker-test
   ```
   (455+ tests deben pasar).

   🤖 **Agent Action**: Alertar si algún test falla o si hay regresión en cobertura.

### Fase 4: Git y Tagging

🤖 **Agent Action**: Usar skill **commit-standards** para mensaje de commit.

1. **Commit de Preparación**:
   Asegurar que `.qgisignore` está actualizado y optimizado.
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md docs/docsec/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md .qgisignore
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Fase 5: Empaquetado y Distribución

🤖 **Agent Action**: Usar skill **release-management** para validar artifacts y proceso de publicación.

1. **Validar `metadata.txt`**:
   // turbo
   ```bash
   uv run qgis-analyzer metadata .
   ```

2. **Validar `pyproject.toml`**:
   // turbo
   ```bash
   uv run qgis-analyzer pyproject .
   ```

3. **Quick Scan (Linting & Security)**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . --strict
   ```

4. **Build ZIP Optimizado**:
   // turbo
   ```bash
   make package VERSION=main
   ```
   (Verificar en `dist/`).

   🤖 **Agent Action**:
   - Validar contenido del ZIP (sin logs, sin `sample_data`, sin caches).
   - **Métrica Clave**: El tamaño del paquete debe ser < 500KB (Idealmente ~220KB).
   - Verificar `sha256` checksum.

2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip dist/*.sha256 --draft
   ```

3. **Portal QGIS**: Subir el ZIP a [plugins.qgis.org](https://plugins.qgis.org/).

   🤖 **Agent Action**: Recordar validar post-publicación:
   - Plugin aparece en QGIS Plugin Manager
   - Versión es correcta
   - Changelog es visible

## Resultado Esperado
- Versión oficial publicada en el repositorio de QGIS y GitHub.
- Documentación y tags de Git sincronizados.
- Plugin validado técnicamente con métricas visibles.
