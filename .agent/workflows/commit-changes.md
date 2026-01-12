---
description: How to commit changes cleanly (handling hooks)
---
This workflow describes the process for committing changes, ensuring code quality standards are met without getting blocked by pre-commit hook conflicts.

1. **Preparación y Limpieza (Automático)**:
   Asegura que el código cumple con el estándar de ruff para evitar fallos en los hooks.
   // turbo
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   ```

2. **Stage Changes**: Añade los archivos que deseas confirmar.
   ```bash
   git add .
   ```

3. **Sincronización de Calidad (Guardián)**:
   Registra el impacto de los cambios en el Cerebro del Proyecto antes de guardar.
   // turbo
   ```bash
   uv run ai-ctx analyze --path .
   ```

4. **Propuesta de Mensaje (Asistida por IA)**:
   Si el usuario pide un commit, la IA debe:
   - Analizar los cambios preparados (`git diff --cached`).
   - Sugerir al menos 2 opciones de mensajes siguiendo las [Commit Guidelines](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/docsec/COMMIT_GUIDELINES.md) (Inglés, Convencional).
   - Indicar si hay cambios críticos en las métricas (ej: aumento súbito de complejidad).

5. **Commit**: Ejecuta el commit con el mensaje aprobado.
   ```bash
   git commit -m "type: description" -m "detailed body"
   ```

   *Si el pre-commit hook persiste en fallar:*
   1. Revisa los mensajes de error detectados.
   2. Ejecuta `git add` de nuevo si hubo cambios automáticos.
   3. Repite el commit.

**Filosofía**: Cada commit es una unidad de valor limpio, documentado y validado métricamente.
