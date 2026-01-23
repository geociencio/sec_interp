---
description: Proceso unificado de liberación (QGIS Release Flow) basado en la guía de IA
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards]
validation: |
  - Verificar que 361 tests pasan en Docker
  - Confirmar que qgis-analyzer score > 25/100
  - Validar que versiones están sincronizadas en 3 archivos
  - Verificar que ZIP se generó correctamente
---

Sigue este flujo de 5 fases para realizar una liberación oficial del plugin SecInterp.

### Fase 1: Calidad y Preparación

🤖 **Agent Action**: Usar skill **release-management** para validar checklist completo de pre-release.

1. **Analizar Calidad**: Ejecutar `uv run qgis-analyzer . -o analysis_results`.

   🤖 **Agent Action**: Verificar que:
   - Overall Plugin Score > 25/100
   - No hay métodos con CC > 20
   - No hay violaciones críticas de QGIS compliance

2. **Actualizar Badges**: Actualizar `Code Quality` y `QGIS Compliance` en `README.md` según los resultados.

### Fase 2: Versionamiento y Documentación

🤖 **Agent Action**: Usar skill **release-management** para sincronizar versiones automáticamente.

1. **Sincronizar Versión**:
   - Actualizar `version` y `changelog` en `metadata.txt`.
   - Actualizar `version` en `pyproject.toml`.
   - Actualizar el badge de versión en `README.md`.

   🤖 **Agent Action**: Validar que las 3 versiones coinciden exactamente.

2. **Changelog Técnico**: Mover `[Unreleased]` a la nueva versión en `docs/CHANGELOG.md`.

3. **Notas de Lanzamiento**:
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

   🤖 **Agent Action**: Generar release notes estructuradas siguiendo template de skill **release-management**.

### Fase 3: Verificación

🤖 **Agent Action**: Usar skill **qa-docker** para validar tests y skill **commit-standards** para linting.

1. **Linting & Formatting**: `uv run ruff check --fix . && uv run ruff format . && uv run black .`
2. **Tests**: `make docker-test` (361+ tests deben pasar).

   🤖 **Agent Action**: Alertar si algún test falla o si hay regresión en cobertura.

### Fase 4: Git y Tagging

🤖 **Agent Action**: Usar skill **commit-standards** para mensaje de commit.

1. **Commit de Preparación**:
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Fase 5: Empaquetado y Distribución

🤖 **Agent Action**: Usar skill **release-management** para validar artifacts y proceso de publicación.

1. **Build ZIP**: `make package VERSION=main` (Verificar en `dist/`).

   🤖 **Agent Action**: Validar contenido del ZIP:
   - metadata.txt tiene versión correcta
   - No hay archivos __pycache__ o .pyc
   - No hay archivos de tests

2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip dist/*.sha256 --draft
   ```

3. **Portal QGIS**: Subir el ZIP a [plugins.qgis.org](https://plugins.qgis.org/).

   🤖 **Agent Action**: Recordar validar post-publicación:
   - Plugin aparece en QGIS Plugin Manager
   - Versión es correcta
   - Changelog es visible
