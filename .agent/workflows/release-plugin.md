---
description: Proceso unificado de liberación (QGIS Release Flow) basado en la guía de IA
---

Sigue este flujo de 5 fases para realizar una liberación oficial del plugin SecInterp.

### Fase 1: Calidad y Preparación
1. **Analizar Calidad**: Ejecutar `uv run qgis-analyzer . -o analysis_results`.
2. **Actualizar Badges**: Actualizar `Code Quality` y `QGIS Compliance` en `README.md` según los resultados.

### Fase 2: Versionamiento y Documentación
1. **Sincronizar Versión**:
   - Actualizar `version` y `changelog` en `metadata.txt`.
   - Actualizar `version` en `pyproject.toml`.
   - Actualizar el badge de versión en `README.md`.
2. **Changelog Técnico**: Mover `[Unreleased]` a la nueva versión en `docs/CHANGELOG.md`.
3. **Notas de Lanzamiento**:
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

### Fase 3: Verificación
1. **Linting**: `uv run ruff check --fix . && uv run ruff format .`
2. **Tests**: `PYTHONPATH=.. uv run python3 -m unittest discover tests` (319+ tests).

### Fase 4: Git y Tagging
1. **Commit de Preparación**:
   `git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/source/MAINTENANCE_LOG.md`
   `git commit -m "chore(release): prepare vX.Y.Z"`
2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Fase 5: Empaquetado y Distribución
1. **Build ZIP**: `make package VERSION=main` (Verificar en `dist/`).
2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file /tmp/release_notes.md dist/*.zip dist/*.sha256 --draft
   ```
3. **Portal QGIS**: Subir el ZIP a [plugins.qgis.org](https://plugins.qgis.org/).
