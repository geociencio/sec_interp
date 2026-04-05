---
description: How to commit changes cleanly (handling hooks)
agent: QA Engineer
skills: [qa-standards, commit-standards]
validation: |
  - Verificar que los linters de formato pasan sin errores
  - Confirmar que el código estático es válido
  - Validar que el mensaje de commit sigue Conventional Commits
---
This workflow describes the process for committing changes, ensuring code quality standards are met without getting blocked by pre-commit hook conflicts.

1. **Preparación y Limpieza (Automático)**:
   Asegura que el código cumple con el estándar de formato y linting para evitar fallos en los hooks.
   // turbo
   ```bash
   # EJEMPLO PYTHON: uv run ruff check --fix . && uv run ruff format .
   # EJEMPLO JS: npm run lint:fix && npm run format
   {{LINTER_FIX_COMMAND}}
   ```

2. **Stage Changes**: Añade los archivos que deseas confirmar.
   ```bash
   git add .
   ```

3. **Sincronización de Calidad (Guardián)**:
   Verifica el impacto estático del código antes de hacer commit.
   // turbo
   ```bash
   # EJEMPLO: npm run build o un script de validación local
   {{PRE_COMMIT_CHECK_COMMAND}}
   ```

   🤖 **Agent Action**: Analizar métricas de calidad y alertar si:
   - Complejidad ciclomática aumentó significativamente
   - Cobertura de tests bajó (si aplica)
   - Se detectaron nuevas violaciones arquitectónicas graves

4. **Propuesta de Mensaje (Asistida por IA)**:

   🤖 **Agent Action**: Usar skill **commit-standards** para:
   - Analizar cambios preparados (`git diff --cached`)
   - Generar 2-3 opciones de mensajes siguiendo Conventional Commits
   - Validar formato: tipo correcto, scope apropiado, inglés, imperativo
   - Sugerir scope basado en archivos modificados (core, ui, api, etc.)
   - Alertar si hay breaking changes que requieren `!` o footer

   Ejemplo de sugerencias:
   ```text
   Opción 1: refactor(core): reduce complexity in authentication service
   Opción 2: feat(ui): add new user profile component
   ```

5. **Commit**: Ejecuta el commit con el mensaje aprobado.
   ```bash
   git commit -m "type(scope): description" -m "detailed body"
   ```

   *Si el pre-commit hook persiste en fallar:*
   1. Revisa los mensajes de error detectados.
   2. Ejecuta `git add` de nuevo si hubo cambios automáticos (linters).
   3. Repite el commit.

**Filosofía**: Cada commit es una unidad de valor limpio, descriptivo y validado estáticamente.
