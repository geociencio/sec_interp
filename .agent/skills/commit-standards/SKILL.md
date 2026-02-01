---
name: commit-standards
description: Estándares para la creación de commits limpios y convencionales con validación de calidad.
trigger: al crear commits, escribir mensajes de commit o usar el workflow /crea-commit
---

# Estándares de Commit

Estandariza el historial de Git asegurando que cada cambio sea rastreable, legible y cumpla con las normas de calidad antes de ser integrado.

## Cuándo usar este skill
- Al redactar mensajes de commit para cambios en el código o documentación.
- Antes de realizar un `git commit` para asegurar que se han cumplido los pasos de calidad.
- Al usar el workflow `/crea-commit` o `/crea-el-comit`.

## Grado de Libertad
- **Estricto**: El formato Conventional Commits y las reglas de idioma (EN para el mensaje) deben seguirse al pie de la letra.

## Workflow
1. **Validación Previa**: Ejecutar linters (`ruff`, `black`) y validación de métricas (`ai-ctx analyze`).
2. **Pruebas**: Confirmar que los tests pasan (`make docker-test`).
3. **Formateo**: Redactar el mensaje siguiendo la especificación de Conventional Commits.
4. **Revisión**: Verificar que el mensaje use el tiempo imperativo y descripción en minúsculas.

## Instrucciones y Reglas

### Regla de Idioma
> [!IMPORTANT]
> Todos los mensajes de commit DEBEN escribirse en **Inglés**.

### Formato Conventional Commits
```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Tipos de Commit
| Tipo | Uso | Ejemplo |
|:-----|:------|:--------|
| `feat` | Nueva funcionalidad | `feat(ui): add legend visibility toggle` |
| `fix` | Corrección de error | `fix(drillhole): correct azimuth calculation` |
| `refactor` | Cambio de código (ni fix ni feat) | `refactor(core): reduce complexity in service` |
| `docs` | Solo documentación | `docs(api): update docstrings` |
| `style` | Formateo, espacios | `style: apply black formatting` |
| `test` | Añadir/corregir tests | `test(integration): add coverage` |
| `chore` | Tareas de mantenimiento | `chore: update uv dependencies` |

## Checklist de Calidad
- [ ] ¿El mensaje está en inglés e imperativo?
- [ ] ¿Se han ejecutado `ruff` y `black`?
- [ ] ¿Los tests pasan satisfactoriamente?
- [ ] ¿El score de calidad no ha disminuido críticamente?
