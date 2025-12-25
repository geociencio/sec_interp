# Registro de Decisiones Técnicas

## 2025-12-17: Integración de ProjectAnalyzer con .ai-context
- **Decisión**: Utilizar los reportes de `analyze_project_optfixed.py` como fuente de verdad para el contexto de la IA.
- **Razón**: Mantener la información de arquitectura, complejidad y dependencias sincronizada con el código real sin intervención manual constante.
- **Cambios realizados**:
    - `project_brain.md`: Poblado con métricas, patrones y deuda técnica detectada.
    - `tech_stack.yaml`: Actualizado con versiones de Python, QGIS y PyQt5 detectadas.
    - `ai_workflow.py`: Modificado para incluir `AI_CONTEXT.md` (root) automáticamente en todos los prompts generados.
- **Impacto**: Mejora la precisión de las sugerencias de la IA al conocer la estructura exacta y los cuellos de botella del proyecto en tiempo real.

## 2025-12-17: Creación de Plantillas para Gemini
- **Decisión**: Crear plantillas YAML específicas para Gemini en `.ai-context/templates`.
- **Razón**: Aprovechar las capacidades de razonamiento profundo y multimodal de Gemini para tareas de optimización y refactorización.
- **Archivos**: `gemini_optimize.yaml`, `gemini_refactor.yaml`, `gemini_feature.yaml`.

## 2025-12-17: Sincronización Masiva de Contexto
- **Acción**: Ejecución de `analyze_project_optfixed.py` y actualización de `.ai-context/`.
- **Resultado**: Mejora en el Score de Calidad (82.3 -> 86.1).
- **Hallazgo**: Se detectó alta complejidad en `preview_renderer.py` y necesidad de modularizar `drillhole_service.py`.
- **Actualización**: Los archivos `project_brain.md` y `tech_stack.yaml` ahora reflejan el estado exacto del código tras las últimas limpiezas de archivos legados.

## 2025-12-17: Herramienta de Medición con Snapping Manual
- **Decisión**: Implementar `ProfileMeasureTool` utilizando `QgsPointLocator` en lugar de `QgsSnappingUtils` global.
- **Razón**: Evitar registrar capas de memoria temporales en el `QgsProject`, lo que ensucia el proyecto del usuario y genera advertencias de "scratch layers".
- **Resultado**: Snapping funcional y preciso sin afectar el estado del proyecto principal.
- **Mejora Adicional**: Robustecimiento de `ai_workflow.py` con soporte para normalización Unicode.

## 2025-12-17: Analizador de Cumplimiento QGIS
- **Decisión**: Integrar verificaciones de mejores prácticas de QGIS en `analyze_project_optfixed.py`.
- **Razón**: Asegurar que el plugin no solo sea "buen código Python", sino un "buen plugin de QGIS", facilitando la aprobación en el repositorio oficial.
- **Resultados**:
    - Detección automática de archivos obligatorios (`LICENSE`, `metadata.txt`).
    - Auditoría de arquitectura (separación UI/Core).
    - Sugerencias de uso de widgets nativos de QGIS.
- **Métrica**: Nuevo "QGIS Compliance Score" integrado en el reporte ejecutivo.

## 2025-12-17: Proceso de Liberación Definitivo (Clean Release)
- **Decisión**: Adoptar `git archive` junto con `.gitattributes` para la generación de paquetes ZIP.
- **Razón**: Garantizar que los paquetes de distribución estén libres de archivos de desarrollo, configuraciones IDE y metadatos de IA, cumpliendo con los estándares de limpieza de QGIS.
- **Artefactos**: `docs/RELEASE_PROCESS.md` y `.agent/workflows/release-plugin.md` creados para asegurar la repetibilidad.
