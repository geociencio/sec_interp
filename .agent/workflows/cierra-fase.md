---
description: Procedimiento formal para cerrar una fase de desarrollo mayor
agent: Senior Architect
skills: [qgis-core, qa-docker]
validation: |
  - Verificar que 361 tests pasan en Docker
  - Confirmar que documento de cierre está completo
  - Validar que métricas están documentadas
  - Verificar que deuda técnica está clasificada
---

# Workflow: Cierre de Fase

Este workflow documenta el proceso completo para cerrar formalmente una fase de desarrollo mayor (ej: v2.6.0 → v2.7.0).

## 1. Revisión Comprehensiva de Logros

🤖 **Agent Action**: Usar skill **qgis-core** para validar cumplimiento de estándares QGIS.

Analiza y documenta todos los objetivos completados durante la fase:

- **Infraestructura**: Nuevas herramientas, Docker, CI/CD, etc.
- **Funcionalidades**: Features implementadas y validadas.
- **Calidad**: Mejoras en tests, métricas de código, refactorizaciones.
- **Documentación**: Guías, arquitectura, ADRs creados o actualizados.

## 2. Identificación de Deuda Técnica

Clasifica la deuda técnica acumulada en tres niveles:

- **🔴 Crítica**: Bloquea funcionalidades o afecta estabilidad (debe resolverse antes del release).
- **🟡 Moderada**: Importante pero no bloqueante (prioridad para siguiente fase).
- **🟢 Menor**: Mejoras cosméticas o de mantenibilidad (backlog).

## 3. Métricas y Verificación Final

🤖 **Agent Action**: Analizar métricas y comparar con fase anterior.

Ejecuta el análisis completo del proyecto y documenta:

// turbo
```bash
uv run ai-ctx analyze --path .
```

Verifica que todos los tests pasen:

// turbo
```bash
make docker-test
```

🤖 **Agent Action**: Usar skill **qa-docker** para validar que 361 tests pasan.

Documenta las métricas clave:
- Tests totales y estado (361 tests)
- Pylint/Ruff score
- Complejidad ciclomática máxima
- Type hint coverage
- Docstring coverage

## 4. Creación del Documento de Cierre

Crea el documento formal en `docs/maintenance/phase_closure_vX.Y.Z.md` con:

```markdown
# Cierre de Fase - SecInterp vX.Y.Z
## Documento de Cierre Formal de Fase de Desarrollo

**Fecha de Cierre:** YYYY-MM-DD
**Versión Actual:** X.Y.Z
**Fase:** [Nombre descriptivo de la fase]
**Responsable:** [Nombre]

---

## 1. Resumen Ejecutivo
[Descripción de los objetivos principales y logros clave]

## 2. Logros Principales
[Desglose detallado por categoría]

## 3. Desafíos Enfrentados y Soluciones
[Problemas significativos y cómo se resolvieron]

## 4. Deuda Técnica Acumulada
[Clasificación por prioridad]

## 5. Métricas del Proyecto
[Tabla con métricas clave]

## 6. Conclusión y Recomendaciones
[Próximos pasos y prioridades para siguiente fase]
```

## 5. Actualización de Logs Maestros

Actualiza los siguientes archivos:

- **`docs/source/MAINTENANCE_LOG.md`**: Consolida todos los cambios de la fase en una entrada única.
- **`docs/CHANGELOG.md`**: Mueve todos los cambios de `[Unreleased]` a `[X.Y.Z] - YYYY-MM-DD`.
- **`docs/DEVELOPMENT_LOG.md`**: Añade entrada de cierre de fase en la parte superior.

## 6. Sincronización de Control de Versiones

Verifica el estado del repositorio:

```bash
git status
git log --oneline -10
```

Si hay commits pendientes de push:

```bash
git push origin main
```

Crea un tag de cierre de fase (opcional, si no es un release oficial):

```bash
git tag phase-vX.Y.Z -m "Phase X.Y.Z closure: [descripción breve]"
git push origin phase-vX.Y.Z
```

## 7. Comunicación con Stakeholders

Prepara un mensaje de cierre para stakeholders (si aplica):

- Resumen de logros principales
- Métricas de calidad
- Próximos pasos
- Timeline estimado para siguiente fase

## 8. Preparación para Siguiente Fase

Crea el archivo `.agent/next_steps.md` con:

- Deuda técnica priorizada
- Objetivos preliminares de la siguiente fase
- Comando para retomar: `/inicia-sesion`

---

**Filosofía**: Una fase no termina cuando el código funciona, sino cuando el conocimiento está documentado y la visión está clara para el siguiente ciclo.
