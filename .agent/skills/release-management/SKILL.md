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
1. **Análisis de Calidad y Seguridad**:
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   uv run qgis-analyzer security --deep .
   ```
   - Validar: Score > 25, zero High-Severity security issues, sin violaciones críticas (CC > 20).
2. **Actualizar Badges**: Reflejar métricas en `README.md`.

### Fase 2: Versionado y Documentación

> [!IMPORTANT]
> **CHECKLIST COMPLETO DE DOCUMENTOS A ACTUALIZAR** (cada archivo en este orden):
>
> | # | Archivo | Qué actualizar |
> |:--|:--------|:--------------|
> | 1 | `metadata.txt` | `version` + `changelog` (escapar `%%`) |
> | 2 | `pyproject.toml` | `version` |
> | 3 | `README.md` | Badge `Version`, `Code Quality`, `QGIS Compliance`, `i18n`, sección "What's New" |
> | 4 | `docs/CHANGELOG.md` | Mover `[Unreleased]` a `[X.Y.Z]` con fecha |
> | 5 | `docs/docsec/CHANGELOG.md` | Ídem en español |
> | 6 | `docs/releases/RELEASE_NOTES_vX.Y.Z.md` | Crear nuevo archivo con highlights |
> | 7 | `docs/DEVELOPMENT_LOG.md` | Añadir entrada de cierre de versión |
> | 8 | `.agent/QUICK_REFERENCE.md` | Actualizar conteo de tests y métricas |

1. **Sincronización**: Actualizar `metadata.txt` (incluyendo changelog), `pyproject.toml` y `README.md`.
2. **Estándares de Versionamiento y Registro (CRÍTICO)**:
   - **[Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html)**:
     - MAJOR (X): Cambios incompatibles (Breaking Changes).
     - MINOR (Y): Nuevas funcionalidades retrocompatibles.
     - PATCH (Z): Correcciones de errores (Bugfixes).
   - **[Keep a Changelog](https://keepachangelog.com/es/1.0.0/)**:
     - Mantener los archivos `docs/CHANGELOG.md` y `docs/docsec/CHANGELOG.md` estrictamente alineados con este estándar.
     - Agrupar cambios lógicamente (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
3. **Notas de Versión**: Generar el release detallado en `docs/releases/RELEASE_NOTES_vX.Y.Z.md`.


### Fase 3: Verificación Técnica
1. Lograr 455+ tests pasando.
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
- [ ] ¿Los 455+ tests pasaron satisfactoriamente?
