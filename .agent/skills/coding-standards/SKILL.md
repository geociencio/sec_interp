---
name: coding-standards
description: Estándares de codificación del proyecto, enfocados en el uso de pathlib, docstrings de Google y tipado estricto.
trigger: al escribir código Python, realizar refactorizaciones o definir rutas de archivos.
---

# Estándares de Codificación

Define las normas técnicas para asegurar un código Python moderno, mantenible y coherente en todo el plugin SecInterp.

## Cuándo usar este skill
- Al crear nuevos módulos o funciones en Python.
- Al realizar refactorizaciones de código existente.
- Al definir rutas de archivos o manipular el sistema de archivos.

## Grado de Libertad
- **Estricto**: El uso de `pathlib`, Google Docstrings y Type Hints es obligatorio.

## Workflow
1. **Tipado**: Añadir anotaciones de tipos (Type Hints) a todos los argumentos y retornos.
2. **Documentación**: Redactar docstrings siguiendo el formato de Google.
3. **Rutas**: Reemplazar manipulaciones de strings u `os.path` por objetos `pathlib.Path`.
4. **Validación**: Ejecutar `black .` y `ruff check .` para confirmar el cumplimiento.

## Instrucciones y Reglas

### Modern Python (Pathlib)
- NUNCA usar concatenación de strings para rutas.
- Usar `/` para unir rutas con `Path`.
- Ejemplo: `base_dir / "data" / "file.txt"`.

### Documentación (Google Style)
```python
def function(arg1: int) -> str:
    """Resumen corto.

    Args:
        arg1: Descripción del argumento.

    Returns:
        Descripción del retorno.
    """
```

### Calidad de Código
- Seguir principios SOLID.
- Mantener la complejidad ciclomática por debajo de 15.

## Checklist de Calidad
- [ ] ¿Se usa `pathlib` para todas las rutas?
- [ ] ¿Todas las funciones tienen Type Hints?
- [ ] ¿Los docstrings siguen el formato de Google?
- [ ] ¿El código pasa el chequeo de `ruff` y `black`?
