---
name: documentation-standards
description: Estándares para el mantenimiento de logs técnicos, registros de sesión e historial del proyecto.
trigger: al actualizar DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md o crear reportes de sesión en docs/maintenance/.
---

# Skill: Documentation Standards

Este skill define los formatos precisos para asegurar que todos los agentes (humanos o IA) mantengan una documentación coherente y profesional.

## 1. Mantenimiento de Logs de Sesión

### 1.1. `docs/DEVELOPMENT_LOG.md`
Este archivo es el registro cronológico inverso de **actividad diaria**.

**Formato:**
```markdown
## [YYYY-MM-DD] [TEMA CORTO]
- **Logro**: Una frase que resuma el impacto principal.
- **Cambios**:
    - Detalle técnico relevante 1 (mencionar módulos si aplica).
    - Detalle técnico relevante 2.
- **Calidad**: Estado de los tests (ej: 361/361 OK) y métricas de ruff/black.
- **Mantenimiento**: Link al log de mantenimiento [sesion_YYYY-MM-DD_tema.md](maintenance/sesion_YYYY-MM-DD_tema.md).
```

---

### 1.2. `docs/source/MAINTENANCE_LOG.md`
Este archivo es el registro estructural de **infraestructura y lanzamientos**.

**Regla de Niveles:**
- **Entradas Recientes (Fase en curso)**: Niveles `##` (H2).
- **Historial de Versiones (Project History)**: Niveles `###` (H3) bajo el encabezado principal de versión.

**Formato Entrada Reciente:**
```markdown
## [YYYY-MM-DD] [TITULO EN MAYÚSCULAS DE INFRAESTRUCTURA]
- **Cambios**: Resumen de cambios en infraestructura o motor.
- **Métricas/Impacto**: Qué mejoró tras esta sesión.
```

**Formato Historial (Project History):**
```markdown
### [vX.Y.Z] - YYYY-MM-DD
- **Resumen**: Descripción general del lanzamiento.
- **Logros Clave**:
    - Logro 1
    - Logro 2
- **Referencia**: Link a la fase closure o implementación plan.
```

---

### 1.3. `docs/maintenance/sesion_*.md`
Reporte técnico detallado de la sesión.

**Estructura Requerida:**
1. **Título**: `# Sesión de Mantenimiento: YYYY-MM-DD - [Título]`
2. **Resumen Técnico**: Párrafo breve del objetivo.
3. **Cambios Realizados**: Lista categorizada.
4. **Resultados de Verificación**: Estado de tests y linting.
5. **Impacto**: Consecuencia técnica del cambio.

---

## 2. Reglas de Redacción
1. **Idioma**: El contenido debe estar en **Español** (preferencia del usuario).
2. **Commit Style**: Los commits siguen siendo en **Inglés**.
3. **Markdown**: Usar negritas para resaltar términos clave y backticks para nombres de archivos o funciones.
4. **Fechas**: Siempre en formato `YYYY-MM-DD`.

## 3. Checklist de Auditoría
- [ ] ¿He usado el encabezado `## [YYYY-MM-DD]` correctamente?
- [ ] ¿He incluido el enlace al archivo de mantenimiento correspondiente?
- [ ] ¿El tono es técnico y preciso sin redundancias?
- [ ] ¿He actualizado la sección de "Project History" si es un cierre de fase?
