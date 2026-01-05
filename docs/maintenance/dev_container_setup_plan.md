# Configuración de Dev Container para SecInterp

Este plan establece un entorno de desarrollo reproducible dentro de un contenedor Docker, permitiendo que todas las dependencias y herramientas (como `uv`, `ruff`, y `black`) estén pre-configuradas.

## Cambios Propuestos

### Infraestructura de Contenedores

#### [NEW] [devcontainer.json](file:///home/jmbernales/qgispluginsdev/sec_interp/.devcontainer/devcontainer.json)
- Define la configuración para VS Code.
- Utiliza el `Dockerfile` existente en la raíz.
- Instala automáticamente extensiones útiles dentro del contenedor (Python, Ruff, Black).
- Ejecuta `uv sync` al crear el contenedor para preparar el entorno virtual.

#### [MODIFY] [Dockerfile](file:///home/jmbernales/qgispluginsdev/sec_interp/Dockerfile)
- Añadir dependencias de sistema mínimas si es necesario para facilitar el desarrollo (ej. `bash-completion`).
- Asegurar que el `PYTHONPATH` sea correcto para el montaje del volumen de VS Code.

## Plan de Verificación

### Manual Verification
1. Abrir el comando central de VS Code (`Ctrl+Shift+P`).
2. Seleccionar "Dev Containers: Reopen in Container".
3. Verificar que el terminal se abra dentro del contenedor.
4. Ejecutar `uv run python -m unittest discover tests` para confirmar que los tests pasan.
