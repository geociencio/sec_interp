# Informe de Fix: KeyError 'class' en Ai-Context-Core v2.5.0

## 🐛 Descripción del Bug
A pesar de la actualización a la v2.5.0, el ejecutable `ai-ctx analyze` falla con un error de tipo `KeyError: 'class'` (o se captura genéricamente en el engine como `'class'`) durante la fase de generación de reportes.

Este error ocurre específicamente cuando se detectan patrones de diseño que no tienen una clase asociada (por ejemplo, funciones decoradoras o patrones a nivel de módulo) y el generador de reportes intenta acceder a la clave `'class'` de forma directa en el diccionario del patrón.

## 🛠️ Diagnóstico Detallado

**Archivo afectado**: `ai_context_core/analyzer/reporting.py`
**Clases afectadas**: `SummaryGenerator` y `AICtxGenerator`.

### Punto de Falla 1: SummaryGenerator._build_patterns
En la versión 2.5.0, el código intenta interpolar `occ['class']` y `occ['module']` directamente:
```python
# reporting.py L290
res.append(
    f"- **{occ['class']}** in `{occ['module']}` ({occ['confidence']}%)"
)
```

### Punto de Falla 2: AICtxGenerator._add_patterns
Similar al anterior, falla al construir el archivo `AI_CONTEXT.md`:
```python
# reporting.py L428
self.lines.append(
    f"- **{o['class']}** in `{o['module']}` ({o['confidence']}%)"
)
```

## ✅ Solución Aplicada (Parche v2.5.0-patch)
Se recomienda el uso de `.get()` con fallbacks para manejar patrones que no definen una clase (como decoradores que usan `'name'`) o módulos desconocidos.

### Código sugerido para `SummaryGenerator`:
```python
for occ in occs[:5]:
    class_name = occ.get("class", occ.get("name", "N/A"))
    module_path = occ.get("module", "N/A")
    confidence = occ.get("confidence", 0)
    res.append(f"- **{class_name}** in `{module_path}` ({confidence}%)")
```

### Código sugerido para `AICtxGenerator`:
```python
for o in occs[:3]:
    class_name = o.get("class", o.get("name", "N/A"))
    module_path = o.get("module", "N/A")
    confidence = o.get("confidence", 0)
    self.lines.append(
        f"- **{class_name}** in `{module_path}` ({confidence}%)"
    )
```

## 📊 Impacto
- **Crítico**: Impide la generación total del reporte `PROJECT_SUMMARY.md` y `AI_CONTEXT.md` si se detecta cualquier decorador (como `@functools.wraps`).
- **Verificación**: Con este cambio, el análisis se completa correctamente en proyectos complejos como `sec_interp`.
