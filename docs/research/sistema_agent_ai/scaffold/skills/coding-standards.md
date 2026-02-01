---
name: coding-standards
description: Estándares de codificación universales (Tipado, Pathlib, Google Docstrings).
trigger: al escribir o modificar código Python.
---
# Estándares de Codificación (Template)

## Cuándo usar este skill
- En cada operación de escritura de código.

## Grado de Libertad
- **Estricto**: Seguimiento obligatorio de PEP8 y estándares definidos.

## Workflow
1. Inyectar Type Hints.
2. Escribir Docstrings estilo Google.
3. Usar `pathlib` para rutas.

## Checklist de Calidad
- [ ] ¿Hay anotaciones de tipo?
- [ ] ¿Se usa Google Style para los docstrings?
- [ ] ¿El código es limpio y modular?
