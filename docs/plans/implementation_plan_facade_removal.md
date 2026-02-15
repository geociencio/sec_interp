# Plan de Eliminación de Facades y Adopción de Inyección de Dependencias

Este plan detalla la transición de una arquitectura basada en Fachadas (Facades) que instancian sus propias dependencias a un modelo de **Inyección de Dependencias (DI)**. Esto mejorará la testabilidad, permitirá el uso de mocks más limpios y reducirá el acoplamiento en la capa `core`.

## Objetivos
1. Modificar `DrillholeService` y `GeologyService` para aceptar sus procesadores/motores vía constructor.
2. Centralizar la instanciación de dependencias en el `ProfileController`.
3. Eliminar métodos "pasamanos" (forwarding methods) que no añaden valor lógico.
4. Mantener compatibilidad temporal mediante valores por defecto en los constructores.

## Proposed Changes

### [Component] Core Services (Dep. Injection)

#### [MODIFY] [drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/drillhole_service.py)
- Refactorizar el constructor para aceptar `CollarProcessor`, `SurveyProcessor`, `IntervalProcessor`, `DataFetcher` y `TrajectoryEngine` como argumentos opcionales.
- Documentar las interfaces esperadas.

#### [MODIFY] [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py)
- Refactorizar el constructor para aceptar `ProfileSampler` y `OutcropProcessor`.

### [Component] Orchestration Layer

#### [MODIFY] [controller.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/controller.py)
- Actualizar la inicialización del `ProfileController` para crear los procesadores especializados y pasarlos a los servicios correspondientes.
- Actuar como el "Compositor de la Aplicación" (Application Root).

### [Component] Testing Infrastructure

#### [MODIFY] [test_drillhole_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/tests/core/test_drillhole_service.py)
- Actualizar los tests para inyectar Mocks directamente en el constructor del servicio, eliminando la necesidad de `patch` internos en el futuro.

## Verification Plan

### Automated Tests
- Ejecutar la suite completa de tests de `core` para asegurar que la inyeccion por defecto sigue funcionando.
- Crear un nuevo test unitario para `DrillholeService` que demuestre la inyección de un mock puro sin usar `unittest.mock.patch`.

```bash
# Validación de tests core
PYTHONPATH=.. uv run python3 -m unittest discover tests/core
```

### Manual Verification
- Abrir el plugin en QGIS y realizar una previsualización de perfiles (geología y sondajes) para validar que la orquestación sigue operativa tras el cambio de cableado.
