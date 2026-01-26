# Plan de Refactorización Arquitectónica Core (v2.9.1)

Este plan aborda la deuda técnica crítica identificada en los servicios principales y el sistema de tipos. El objetivo es reducir la complejidad ciclomática, mejorar la testabilidad y facilitar el mantenimiento futuro.

## Estrategia General
Se aplicará el principio de Responsabilidad Única (SRP) para descomponer servicios monolíticos en componentes especializados.

## Componentes Afectados

### 1. Sistema de Tipos (Prioridad 1 - Base)
**Estado Actual**: `core/types.py` monolítico.

**Cambios Propuestos**:
- Crear paquete `core/types/` (o mantener nombre pero dividir internamente si se prefiere, aunque el usuario sugirió estructura).
- Estructura Específica:
    - `core/types/domain_types.py`: Entidades centrales (`GeologySegment`, `StructureMeasurement`).
    - `core/types/task_inputs.py`: DTOs de entrada para tareas (`DrillholeTaskInput`, `GeologyTaskInput`).
    - `core/types/dtos.py`: Otros objetos de transferencia de datos.
- **Acción**: Renombrar/Mover `core/types.py` a `core/types/__init__.py` y redistribuir contenido.

### 2. Drillhole Service (Prioridad 2)
**Estado Actual**: Monolito en `core/services/drillhole_service.py`.

**Cambios Propuestos**:
- Crear paquete `core/services/drillhole/`.
- Estructura Específica:
    - `collar_processor.py`: Lógica de extracción y validación de collares (`_process_detached_collar_item`).
    - `survey_processor.py`: Procesamiento de datos de survey (`_process_survey_data`).
    - `interval_processor.py`: Procesamiento de intervalos litológicos (`_process_intervals`).
    - `projection_engine.py`: Matemática pura de proyección 2D/3D (`_project_point_to_line`, desurveying).
- `DrillholeService` (Facade): Se mantiene en `core/services/drillhole_service.py` (o `core/services/drillhole/service.py` re-exportado) para orquestar estos procesadores.

### 3. Geology Service (Prioridad 3) ✅ COMPLETADO
**Estado Actual**: Refactorización completada.

**Cambios Realizados**:
- Extraída lógica geométrica a `core/utils/geometry_utils/processing.py`
- Extraída lógica de extracción a `core/utils/geometry_utils/extraction.py`
- Reducida complejidad ciclomática en `GeologyService`
- Tests actualizados y validados (361 tests OK)

## Plan de Ejecución

### Fase 1: Reestructuración de Tipos
1. Crear estructura de carpetas `core/domain`.
2. Mover definiciones.
3. Actualizar imports en todo el proyecto (puede ser masivo).

### Fase 2: Descomposición de DrillholeService
1. Crear `DrillholeProjector` y mover lógica de proyección (`_project_single_detached_collar`, `_process_single_hole`).
2. Crear `DrillholeExtractor` y mover `prepare_task_input`, `_extract_attributes_agnostic`.
3. Conectar `DrillholeService` a estos nuevos componentes.

### Fase 3: Limpieza de GeologyService ✅ COMPLETADO
1. ✅ Extraídos métodos privados de geometría a `core/utils/geometry_utils`
2. ✅ Commit: `d32c017` - "refactor(core): extract geometry logic from GeologyService"

## Verificación
- Ejecución de suite de tests unitarios completa (208 tests) tras cada fase.
- Verificación de métricas `ai-ctx analyze` para confirmar reducción de CC.
