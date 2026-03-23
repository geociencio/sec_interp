# Sesión: Update ai-context-core v3.3.0
**Fecha**: 2026-03-22
**Tema**: `update_ai_context_core_v330`

## Objetivos Alcanzados
- Actualización de `ai-context-core` de v3.2.1 a v3.3.0.
- Resolución del bug de agregación de métricas globales (Score, Funciones, Clases, MI).
- Activación de la nueva auditoría de cumplimiento de estándares QGIS.
- Sincronización de la memoria del agente (`AGENT_LESSONS.md` y `agent_metrics.json`).

## Detalles Técnicos
- El comando verificado para el CLI es `uv run ai-ctx`.
- La actualización de `pyproject.toml` se realizó en las secciones de `project.dependencies` y `dependency-groups.dev`.
- Se confirmó que la v3.3.0 reporta correctamente los metadatos del proyecto sin el error de "ceros globales" presente en la v3.2.1.

## Métricas de Análisis (ai-ctx)
- **Quality Score**: 41.6/100
- **Functions**: 779
- **Classes**: 147
- **Avg Maintenance Index**: 39.4
- **QGIS Compliance Score**: 80.3/100

## QA
- Ruff y Conventional Commits validados durante el proceso de commit.
- `ai-ctx analyze` exitoso en el directorio raíz.
