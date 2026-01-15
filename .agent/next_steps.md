# Next Steps: Validación Nivel 3 (Dominio)

## Estado Actual
- **Tests**: 363 tests PASANDO.
- **Validación**: Niveles 1 y 2 completados. El sistema ahora soporta acumulación de errores.

## Tareas Pendientes (Prioridad)
1. **Nivel 3: Domain Validation (Service Layer)**
    - Objetivo: Evitar operaciones costosas o inválidas en los servicios principales.
    - Archivos clave: `core/services/geology_service.py`, `core/services/drillhole_service.py`.
    - Tarea: Inyectar validaciones de dominio al inicio de los métodos principales (ej: `generate_profile`).

2. **Documentación**
    - Actualizar ADRs si hay cambios significativos en patrones de servicio.

## Comando de Retorno
Para iniciar la próxima sesión con el contexto adecuado:
```bash
@/inicia-sesion
```
(Y revisar este archivo para retomar el Nivel 3).
