# Sesión de Mantenimiento - 2026-02-01
## Tema: Refactorización de ExportService y Estandarización de Herramientas

### ✅ Objetivos Completados
1.  **Refactorización de `export_service.py`**:
    *   Descomposición de `_export_drillholes` y `_export_interpretations`.
    *   Extracción de lógica 3D a métodos especializados.
    *   Reducción de la Complejidad Ciclomática (CC) de >60 a nivel saludable (<10 en métodos clave).
2.  **Estandarización de Herramientas**:
    *   Definición de roles: `ai-ctx` para mantenimiento diario/CC y `qgis-analyzer` para auditoría experta de QGIS.
    *   Actualización de Workflows (`refactor-code.md`) y guías de desarrollo.
3.  **Framework Export Kit**:
    *   Actualización de `UPGRADE_FRAMEWORK_GEN2.md` con la distinción de herramientas y código fuente completo.

### 📊 Métricas Finales
- **Maintainability**: 100/100
- **Docstring Coverage**: 65.9%
- **Type Hint Coverage (Params)**: 76.0%

### 🛠️ Decisiones Técnicas
- Se pospone el parche de importación legacy en `resources/resources.py` hasta la migración a QGIS 4.x por pragmatismo (archivo auto-generado).

### 🧪 Validación
- 110 tests core OK.
- 16 tests de integración OK.
- Entorno: Docker.
