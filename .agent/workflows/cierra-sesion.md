---
description: Procedimiento para finalizar una sesión de trabajo, actualizar logs y archivar resultados
---
Este workflow automatiza el cierre de una sesión de trabajo, asegurando que todos los progresos técnicos y registros de mantenimiento estén sincronizados y archivados correctamente antes del commit final.

1.  **Resumen de la Sesión**: Identifica las tareas completadas y los cambios técnicos significativos realizados durante la sesión.

2.  **Actualizar Registro de Desarrollo**: Añade una entrada al archivo `docs/DEVELOPMENT_LOG.md` con la fecha actual y un resumen de las actividades.
    *   Formato: `## [YYYY-MM-DD] - Título de la Sesión (HH:MM)`

3.  **Actualizar Registro de Mantenimiento**: Si la sesión incluyó cambios que afectan a la versión o hitos importantes, añade una entrada en `docs/source/MAINTENANCE_LOG.md`.

4.  **Archivar Walkthrough**: Copia el contenido del `walkthrough.md` de la sesión actual a un nuevo archivo en `docs/maintenance/`.
    *   Nombre recomendado: `sesion_YYYY-MM-DD_HH-MM.md` o un nombre descriptivo similar.

5.  **Commit Final**: Realiza un commit que incluya la actualización de los logs y el archivo del walkthrough.
    *   Mensaje recomendado: `docs: update development logs and archive session walkthrough`

// turbo
6.  **Verificación**: Ejecuta los tests unitarios un última vez para asegurar que los cambios en la documentación no afectaron accidentalmente nada.
    ```bash
    PYTHONPATH=.. uv run python3 -m unittest discover tests
    ```

---
