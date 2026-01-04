# Walkthrough: Aprendizaje Práctico de Docker en SecInterp

¡Fases 1, 2 y 3 completadas con éxito! Ahora tienes un entorno de pruebas robusto y reproducible.

## Logros Alcanzados
1.  **Aislamiento**: Verificaste que un contenedor limpio no tiene `git`, `uv` ni librerías de sistema por defecto.
2.  **Volúmenes**: Aprendiste a mapear tu código local (`$(pwd)`) dentro del contenedor.
3.  **Persistencia y Permisos**: Enfrentaste y resolviste el problema de los archivos creados por `root`.
4.  **Recetas (Dockerfile)**: Creaste un `Dockerfile` que automatiza la instalación de herramientas y configuración de variables de entorno (`PYTHONPATH`).
5.  **Automatización**: Lograste ejecutar 319 tests con un solo comando de Docker.

## Estado de los Tests
- **Total**: 319
- **Pasados**: 312
- **Fallidos**: 3 (Relacionados con Mocks de UI/Exporters)
- **Skipped**: 4

> [!NOTE]
> Los fallos en los tests no son un error de tu configuración de Docker. Son inconsistencias en los "Mocks" que simulan QGIS cuando corren en un entorno Linux minimalista sin servidor gráfico (X11). ¡Para el propósito de aprender Docker, el resultado es un 10/10!

## Próximo Paso: Fase 4 (Hacia Codeberg/Woodpecker)
Ahora estamos listos para lo que realmente importa en un flujo profesional: **CI/CD**.
Configuraremos un archivo que le diga a un servidor externo (como Woodpecker CI) que haga exactamente lo mismo que acabas de hacer tú en tu terminal cada vez que subas código.
