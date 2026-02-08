# i18n String Detection Improvement Guide

Este documento detalla el estado actual de la detección de strings i18n en `ai-context-core` y propone mejoras técnicas para reducir falsos positivos y mejorar la precisión del QGIS Compliance Score.

## 1. Estado Actual (Analizador v3.1.1)

Actualmente, la lógica reside en `ai_context_core/analyzer/qgis_checkers/i18n_components/string_utils.py`.  La función `is_translatable_string` utiliza heurísticas básicas:

- **Filtros de exclusión**: Ignora strings vacíos, de un solo carácter, rutas (`/`, `./`, `\\`), URLs (`http://`) y placeholders (`{}`).
- **Criterio de inclusión**: Acepta cualquier string que contenga un **espacio** o signos de puntuación (`.,!?;`).

### Contexto de Llamada
El `I18nChecker` (`i18n.py`) ignora automáticamente strings dentro de llamadas a:
- Loggers (`debug`, `info`, `warning`, etc.).
- Excepciones estándar (`ValueError`, `RuntimeError`, etc.).

---

## 2. Puntos Débiles Identificados

1. **Diccionarios Técnicos**: Colecciones de configuración (ej. `{"key": "Technical Value"}`) son detectadas como strings de UI si el valor tiene un espacio.
2. **Nombres de Atributos/Columnas**: Strings cortos con puntuación (ej. `"data.value"`) son detectados incorrectamente.
3. **Falta de Contexto AST**: El analizador actual ve el `ast.Constant` (string) de forma aislada, sin saber si es una clave de diccionario, un argumento de una función técnica, o un valor por defecto.
4. **Strings Técnicos Complejos**: Nombres de capas QGIS por defecto o estilos (ej. `"Single Symbol"`) inflan el total de strings sin ser realmente contenido traducible de la aplicación.

---

## 3. Estrategias de Mejora Propuestas

### A. Mejoras en el Contexto del AST
Modificar el `GenericQGISComplianceVisitor` para rastrear en qué "contenedor" se encuentra el string:

```python
# Propuesta de lógica en el Visitor
def visit_Dict(self, node):
    # Marcar que estamos dentro de un diccionario para ignorar llaves técnicas
    self.context = "DICT_LITERAL"
    self.generic_visit(node)
    self.context = None

def visit_Call(self, node):
    # Expandir la lista de funciones ignoradas dinámicamente
    # o detectar decoradores específicos
    ...
```

### B. Heurísticas Basadas en Pattens de Naming
Implementar filtros para ignorar strings que sigan convenciones de código:

- **snake_case**: `data_extraction_tool` -> Ignorar.
- **camelCase**: `rasterLayerName` -> Ignorar.
- **PascalCase**: `PreviewRenderer` -> Ignorar.
- **UPPER_CASE**: `DEFAULT_PRECISION` -> Ignorar.

### C. Sistema de Marcado manual (Opt-out)
Soportar comentarios inline para que el desarrollador pueda excluir strings manualmente:

```python
ERROR_CODE = "technical.error.001"  # no-i18n
```

### D. Refinamiento de `is_translatable_string`
Mejorar la función con análisis de entropía o listas de palabras:

- **Entropía de texto**: Los strings técnicos tienen una distribución de caracteres distinta al lenguaje humano.
- **Detección de Idioma**: Usar heurísticas para verificar si el string contiene palabras comunes de un diccionario base (ES/EN).

---

## 4. Workaround para Desarrolladores

Mientras el analizador evoluciona, se recomienda:

1. **Usar `.analyzerignore`**: Excluir directorios que no contengan UI (ej. `core/validation`, `infrastructure/`).
2. **Centralizar Configuración**: Mover los diccionarios técnicos a archivos JSON/TOML externos, los cuales suelen ser ignorados por el escáner de Python.
3. **Encapsulamiento en `tr()`**: Asegurarse de que TODOS los mensajes destinados al usuario final estén envueltos en `self.tr()` o `QCoreApplication.translate()`.

---

> [!NOTE]
> Este documento debe ser revisado por el equipo de `ai-context-core` para la implementación de la v3.2.0+.
