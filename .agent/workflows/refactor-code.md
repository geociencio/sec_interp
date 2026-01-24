---
description: Workflow guiado para refactorización de código con validación de complejidad
agent: Senior Architect
skills: [qgis-core, geological-logic]
validation: |
  - Verificar que complejidad ciclomática se redujo (CC < 15)
  - Confirmar que tests siguen pasando después de refactorización
  - Validar que no se introdujeron violaciones de arquitectura
---

Este workflow guía la refactorización de código siguiendo los estándares del proyecto y usando conocimiento especializado de skills.

## Cuándo Usar Este Workflow

- Cuando `qgis-analyzer` detecta métodos con CC > 15
- Cuando `AI_CONTEXT.md` identifica deuda técnica crítica
- Antes de añadir nuevas funcionalidades a módulos complejos


## Pasos de Refactorización

1. **Identificar Objetivo de Refactorización**:
   ```bash
   qgis-analyzer analyze .
   ```

   🤖 **Agent Action**: Analizar `analysis_results/PROJECT_SUMMARY.md` para identificar:
   - Métodos con alta complejidad ciclomática
   - Funciones sin type hints o docstrings
   - Violaciones de estándares QGIS

2. **Cargar Contexto Especializado**:

   🤖 **Agent Action**: Según el módulo a refactorizar, cargar skill apropiado:
   - **`core/services/geology_service.py`** → Usar skill **geological-logic**
   - **`core/services/drillhole_service.py`** → Usar skill **geological-logic** + **qgis-core**
   - **`gui/`** → Usar skill **ui-framework** + **qgis-core**

3. **Aplicar Refactorización**:

   Principios a seguir (según skill **qgis-core**):
   - Extraer métodos privados para lógica compleja
   - Usar `QgsTask` para operaciones pesadas
   - Mantener separación UI/Core estricta
   - Añadir type hints y docstrings Google-style

4. **Validar con Tests**:
   ```bash
   make docker-test
   ```

   🤖 **Agent Action**: Usar skill **qa-docker** para:
   - Verificar que todos los tests pasan
   - Identificar si hay tests faltantes para el código refactorizado
   - Sugerir nuevos tests si es necesario

5. **Verificar Métricas de Calidad**:
   ```bash
   qgis-analyzer analyze .
   ```

   🤖 **Agent Action**: Comparar métricas antes/después:
   - Complejidad ciclomática debe haber bajado
   - Type hint coverage debe haber aumentado
   - No deben aparecer nuevas violaciones

6. **Commit de Refactorización**:
   Usar workflow `/crea-commit` con mensaje tipo:
   ```
   refactor(core): reduce complexity in GeologyService.prepare_task_input

   - Extract validation logic to _validate_inputs (CC: 16 → 8)
   - Extract data collection to _extract_outcrop_data (CC: 16 → 6)
   - Add type hints and docstrings
   ```

## Ejemplo de Refactorización

**Antes** (CC = 21):
```python
def apply_attribute_inheritance(self, polygon, geology_data, drillhole_data):
    # 50+ líneas de lógica mezclada
    ...
```

**Después** (CC = 8):
```python
def apply_attribute_inheritance(
    self, polygon: QgsGeometry, geology_data: List[GeologySegment],
    drillhole_data: List[DrillholeData]
) -> Dict[str, Any]:
    """Apply attribute inheritance from nearest geological feature.

    Args:
        polygon: Target polygon geometry
        geology_data: List of geology segments
        drillhole_data: List of drillhole data

    Returns:
        Dictionary with inherited attributes
    """
    nearest_feature = self._find_nearest_feature(polygon, geology_data, drillhole_data)
    attributes = self._extract_attributes(nearest_feature)
    return self._format_attributes(attributes)

def _find_nearest_feature(self, polygon, geology_data, drillhole_data):
    # Lógica de búsqueda aislada
    ...
```

**Objetivo**: Código más mantenible, testeable y conforme a estándares QGIS.
