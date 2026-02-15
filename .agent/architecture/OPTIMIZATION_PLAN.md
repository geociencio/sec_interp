# Plan de Optimización del Sistema Agentico (Gen 4)

Este documento detalla la evolución propuesta para el sistema `.agent` basada en el análisis de la fase v3.0.0.

## 1. Diagnóstico Actual

### Fortalezas
- ✅ **Modularidad**: Skills bien definidas y aisladas.
- ✅ **Workflows**: Cobertura completa del ciclo de vida de desarrollo.
- ✅ **Memoria**: `AGENT_LESSONS.md` captura conocimiento cualitativo.

### Brechas Identificadas
- ⚠️ **Métricas Estáticas**: `agent_metrics.json` no se actualiza automáticamente.
- ⚠️ **Falta de Automatización de Deuda**: No hay workflow para limpiezas masivas (linting).
- ⚠️ **Preparación Futura**: Falta conocimiento específico para la migración a QGIS 4.x.

## 2. Propuestas de Implementación

### A. Nuevas Skills

#### 1. `qgis-migration-4x`
- **Propósito**: Guía experta para la transición de API (v3 -> v4).
- **Contenido**: Mapeo de clases obsoletas, reemplazos de `PyQt5` por `qgis.PyQt`, patrones asíncronos obligatorios.

#### 2. `refactoring-patterns`
- **Propósito**: Patrones de diseño específicos para reducir complejidad ciclomática.
- **Contenido**: Estrategias para descomponer "God Classes" (como era `DrillholeService`).

### B. Nuevos Workflows

#### 1. `/fix-linting`
- **Propósito**: Automatizar la corrección de issues de estilo y estáticos.
- **Pasos**: Ejecución agresiva de `ruff --fix`, `black`, organización de imports.

#### 2. `/migrate-qgis4`
- **Propósito**: Workflow guiado para aplicar la skill `qgis-migration-4x`.

### C. Mejora de Memoria (Agentic Brain)

#### Automatización de Métricas
Actualizar el script o skill `agentic-memory` para que al cierre de sesión (`/cierra-sesion`):
1. Lea el reporte de `qgis-analyzer`.
2. Extraiga métricas clave (Score, Tests Pasados, CC Avg).
3. Añada un nuevo registro histórico en `agent_metrics.json`.

## 3. Hoja de Ruta

1. **Inmediato**: Implementar `/fix-linting` para limpiar v3.0.1.
2. **Corto Plazo**: Crear skill `qgis-migration-4x`.
3. **Mediano Plazo**: Automatizar actualización de `agent_metrics.json`.
