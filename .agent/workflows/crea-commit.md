---
description: How to commit changes cleanly (handling hooks)
agent: QA Engineer
skills: [qa-docker, commit-standards]
validation: |
  - Verificar que ruff y black pasan sin errores
  - Confirmar que ai-ctx analyze se ejecutó correctamente
  - Validar que el mensaje de commit sigue Conventional Commits
---
This workflow describes the process for committing changes, ensuring code quality standards are met without getting blocked by pre-commit hook conflicts.

1. **Preparación y Limpieza (Automático)**:
   Asegura que el código cumple con el estándar de ruff y black para evitar fallos en los hooks.
   // turbo
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   uv run black .
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

   🤖 **Agent Action**: Analizar métricas de calidad y alertar si:
   - Complejidad ciclomática aumentó significativamente
   - Docstring coverage bajó
   - Se detectaron nuevas violaciones de QGIS compliance

4. **Propuesta de Mensaje (Asistida por IA)**:

   🤖 **Agent Action**: Usar skill **commit-standards** para:
   - Analizar cambios preparados (`git diff --cached`)
   - Generar 2-3 opciones de mensajes siguiendo Conventional Commits
   - Validar formato: tipo correcto, scope apropiado, inglés, imperativo
   - Sugerir scope basado en archivos modificados (core, gui, export, etc.)
   - Alertar si hay breaking changes que requieren `!` o footer

   Ejemplo de sugerencias:
   ```text
   Opción 1: refactor(core): reduce complexity in GeologyService.prepare_task_input
   Opción 2: refactor(core): extract validation logic from GeologyService
   ```

5. **Commit**: Ejecuta el commit con el mensaje aprobado.
   ```bash
   git commit -m "type(scope): description" -m "detailed body"
   ```

   *Si el pre-commit hook persiste en fallar:*
   1. Revisa los mensajes de error detectados.
   2. Ejecuta `git add` de nuevo si hubo cambios automáticos.
   3. Repite el commit.

**Filosofía**: Cada commit es una unidad de valor limpio, documentado y validado métricamente.
