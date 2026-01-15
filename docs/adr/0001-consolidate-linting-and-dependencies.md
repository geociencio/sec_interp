# ADR 0001: Consolidación de Linting y Gestión de Dependencias

## Estado
✅ Aceptado

## Contexto
El proyecto utilizaba múltiples herramientas para asegurar la calidad del código (`flake8`, `isort`, `pylint`, `black`) y mantenía listas duplicadas de dependencias de desarrollo (`requirements-dev.txt` y `pyproject.toml`). Esta redundancia provocaba:
1.  **Lentitud**: Ejecutar múltiples herramientas independientes aumentaba el tiempo de feedback.
2.  **Desincronización**: Riesgo de tener versiones de librerías diferentes en archivos duplicados.
3.  **Complejidad**: Dificultad para mantener múltiples configuraciones (`.flake8`, secciones en `pyproject.toml`).

## Decisión
Hemos decidido:
1.  **Unificar Calidad con Ruff**: Adoptar `ruff` como herramienta única para linting y formateo. Ruff reemplaza a `flake8`, `isort` y la mayoría de las reglas de `pylint`, ofreciendo una velocidad órdenes de magnitud superior.
2.  **Activar Reglas PLR**: Habilitar las reglas de Pylint (`PLR`) en Ruff para mantener el rigor en el análisis de complejidad (max-statements, max-branches, etc.), ajustando los umbrales para que coincidan con el estado actual del proyecto.
3.  **Fuente Única de Dependencias**: Eliminar `requirements-dev.txt` y centralizar todas las dependencias en `pyproject.toml` usando el estándar de `dependency-groups` de Python.
4.  **Adopción de UV**: Estandarizar el uso de `uv` para la gestión de entornos y sincronización de dependencias (`uv sync`).

## Consecuencias
### Positivas
*   **Velocidad**: El proceso de linting es ahora instantáneo.
*   **Simplicidad**: Menos archivos de configuración en la raíz del proyecto.
*   **Consistencia**: Al usar `uv sync`, todos los desarrolladores trabajan sobre un entorno idéntico definido en un solo lugar.

### Negativas / Riesgos
*   **Curva de Aprendizaje**: Los desarrolladores acostumbrados a `pip install -r requirements-dev.txt` deben aprender el flujo de `uv`.
*   **Límites de Complejidad**: La estrictez de las reglas `PLR` de Ruff puede requerir refactorizaciones en el futuro si se desean bajar los umbrales de complejidad permitidos.

## Referencias
*   [Ruff Documentation](https://docs.astral.sh/ruff/)
*   [UV Documentation](https://docs.astral.sh/uv/)
