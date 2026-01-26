# Informe Técnico para Desarrolladores de Ai-Context-Core

## 🐛 Reporte de Bug: KeyError 'class' en v2.1.1

Se ha identificado un fallo crítico en la v2.1.1 que impide que los patrones detectados se muestren en el reporte final y en el archivo `AI_CONTEXT.md`.

### Diagnóstico
El error ocurre en `ai_context_core/cli.py` (línea 163 aprox.) dentro del método `show_specific`.
```python
# Error:
click.echo(f"- {name}: {o['class']} in {o['module']} ({o['confidence']}%)")
```
**Causa**: El diccionario de patrones detectado para ciertos módulos no contiene la clave `'class'`. Esto sucede comúnmente en patrones detectados a nivel de módulo (como **Observer** mediante signals) o cuando la heurística devuelve una estructura incompleta.

### Solución Sugerida
Implementar un acceso seguro mediante `.get()` con fallbacks:
```python
class_name = o.get('class', 'N/A')
module_path = o.get('module', 'N/A')
click.echo(f"- {name}: {class_name} in {module_path} ({o.get('confidence', 0)}%)")
```

---

## 🚀 Recomendaciones de Mejora (Heurística QGIS)

Para que la herramienta sea útil en el ecosistema de QGIS, se proponen las siguientes mejoras en `analyzer/ast_utils.py`:

### 1. Detección de Entry Points de QGIS
Actualmente solo se busca `if __name__ == "__main__"`. Los plugins de QGIS usan `classFactory`.

**Implementación propuesta**:
```python
def is_qgis_entry_point(node):
    return isinstance(node, ast.FunctionDef) and node.name == "classFactory"
```

### 2. Detección del Patrón Observer (PyQt)
Los plugins de QGIS dependen intensamente de señales y slots.

**Heurística sugerida**:
- Buscar asignaciones de `pyqtSignal()`.
- Si un módulo tiene >2 señales, clasificar con confianza 0.8 como **Observer**.

### 3. Soporte para el Workflow Local-First
Muchos agentes (como Antigravity) generan archivos de memoria interna.
- **Recomendación**: Permitir que `ai-ctx` integre información de archivos Markdown existentes (como `project_brain.md`) en la sección de arquitectura del reporte final para no perder el contexto cualitativo escrito por humanos/IA.

---

## 📊 Matriz de Prioridad para v2.2.0

| Prioridad | Problema | Impacto | Esfuerzo |
| :--- | :--- | :--- | :--- |
| 🔥 CRÍTICO | KeyError 'class' | Rompe el reporte final | Muy Bajo (1 min) |
| 🔥 ALTA | Entry Points QGIS | Reporte incompleto en plugins | Bajo (5-10 min) |
| ⚡ MEDIA | Observer Pattern | Falta de detalle arquitectónico | Medio (30 min) |
