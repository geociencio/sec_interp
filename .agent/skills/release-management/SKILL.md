---
name: release-management
description: Estándares para el proceso de liberación del plugin QGIS con validación de calidad.
trigger: al preparar lanzamientos, actualizar versiones o usar el workflow /release-plugin
---

# Gestión de Releases (Versión Completa)

Controla el ciclo de vida de las versiones del plugin, garantizando que cada entrega cumpla con los estándares del repositorio de QGIS y el proyecto.

## Cuándo usar este skill
- Al finalizar una fase de desarrollo y preparar una nueva versión.
- Al actualizar `metadata.txt` o `pyproject.toml`.
- Al generar notas de versión o actualizar el changelog.
- Al usar el workflow `/release-plugin`.

## Grado de Libertad
- **Estricto**: El proceso de 5 fases y los requisitos de puntuación de calidad son innegociables.

## Workflow Detallado

### Fase 1: Calidad y Preparación
1. **Análisis de Calidad**:
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   ```
   - Validar: Score > 25, sin violaciones críticas (CC > 20), sin imports legacy de PyQt5.
2. **Actualizar Badges**: Reflejar métricas en `README.md`.

### Fase 2: Versionado y Documentación
1. **Sincronización**: Actualizar `metadata.txt` (incluyendo changelog), `pyproject.toml` y `README.md`.
2. **Reglas Semver**:
   - MAJOR (X): Cambios incompatibles.
   - MINOR (Y): Nuevas funcionalidades.
   - PATCH (Z): Correcciones.
3. **Notas de Versión**: Generar en `docs/releases/RELEASE_NOTES_vX.Y.Z.md` usando la plantilla estándar.

### Fase 3: Verificación Técnica
1. Lograr 361+ tests pasando.
2. Ejecutar `make docker-test` para entorno aislado.
3. Actualizar `AI_CONTEXT.md` vía `uv run ai-ctx analyze`.

### Fase 4: Git y Etiquetado
1. Commit de release: `chore(release): prepare vX.Y.Z`.
2. Etiqueta: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Fase 5: Empaquetado y Distribución
1. Build: `make package VERSION=main`.
2. Validar ZIP en `dist/`: Sin `__pycache__`, sin archivos de tests.
3. Carga: Subir a [plugins.qgis.org](https://plugins.qgis.org/) y crear draft en GitHub.

## Instrucciones y Reglas

### Detalle de Archivos Críticos
- **metadata.txt**: Debe contener `version`, `qgisMinimumVersion` y el `changelog` formateado.
- **pyproject.toml**: El campo `version` debe coincidir exactamente.

### Plantilla de Release Notes
```markdown
# Release vX.Y.Z - [Title]
Highlights:
- **feat**: ...
- **fix**: ...
Published Artifacts: `sec_interp.X.Y.Z.zip`
```

## Checklist de Calidad
- [ ] ¿El Quality Score es superior a 25/100?
- [ ] ¿Se han actualizado todas las referencias de versión?
- [ ] ¿El archivo ZIP ha sido verificado (sin basura técnica)?
- [ ] ¿Se han seguido las reglas de Git Tagging?
- [ ] ¿Los 361+ tests pasaron satisfactoriamente?
