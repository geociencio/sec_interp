---
description: Procedimiento estándar y robusto para iniciar una sesión de desarrollo "Local First"
agent: Tech Lead
skills: [project-context, qa-standards]
validation: |
  - Verificar que los tests configurados pasen correctamente
  - Confirmar que el contexto del AI está sincronizado
  - Validar que no hay regresiones de calidad críticas
---

Este workflow optimiza el inicio del desarrollo asegurando un entorno sincronizado, **contextualizado** y validado.

1.  **Sintonización de Contexto (CRÍTICO)**:
    Actualiza y lee el contexto para entender "dónde nos quedamos".
    // turbo
    ```bash
    cat .agent/next_steps.md
    ```

    🤖 **Agent Action**: Revisar `AI_CONTEXT.md` (si existe) y `project-context` para identificar:
    - Deuda técnica crítica o decisiones arquitectónicas pendientes
    - Violaciones de arquitectura
    - Qué componente fue modificado en la sesión anterior

    Revisa los siguientes archivos en este orden (si existen en el proyecto):
    *   `docs/ROADMAP.md`: **Mapa de Ruta Maestro**. Fuente de verdad sobre tareas completadas.
    *   `.agent/next_steps.md`: **El Testigo**. Punto exacto donde se detuvo la sesión anterior.
    *   `docs/DEVELOPMENT_LOG.md`: Ver resumen de la última sesión.

2.  **Sincronización de Entorno (Local)**:
    Asegura dependencias actualizadas.
    // turbo
    ```bash
    # EJEMPLO PYTHON: uv sync
    # EJEMPLO JS: npm install
    {{SYNC_DEPENDENCIES_COMMAND}}
    ```

    🤖 **Agent Action**: Verificar que no hay conflictos de dependencias tras la actualización.

3.  **Verificación de Estado (Sanity Check)**:
    Confirma que el sistema está estable ("en verde"). Los tests principales deben pasar.

    // turbo
    ```bash
    # EJEMPLO PYTHON: make test
    # EJEMPLO Gral: npm run test
    {{MASTER_TEST_COMMAND}}
    ```

    🤖 **Agent Action**: Usar skill **qa-standards** para interpretar posibles fallos en el estado base del proyecto (ramas rotas).

## Resultado Esperado
- Entorno local limpio, sincronizado y validado.
- Mapa mental claro de las tareas pendientes (`next_steps.md`).
- Agente operando con los perfiles, dependencias y skills correctos cargados.

**Filosofía**: Empezar a codificar sabiendo *exactamente* qué pasó ayer y con la seguridad de que la rama no compila con errores.
