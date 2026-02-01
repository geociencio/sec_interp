# Análisis Técnico Detallado y Propuesta de Solución: ai-context-core (v3.0.1)

Este documento proporciona una disección técnica de dos problemas críticos identificados en `ai-context-core` v3.0.1 durante su uso en proyectos de gran escala y plugins de QGIS.

---

## 1. Crash Crítico: `KeyError: 'complexity'` en el Agregador

### 🔍 Síntoma y Diagnóstico
Durante la fase de consolidación de resultados (al generar `project_context.json`), el CLI termina abruptamente con una excepción no capturada:
```python
File "ai_context/aggregator.py", line 142, in aggregate_metrics
    total_complexity += module['complexity']
KeyError: 'complexity'
```

### 🧬 Causa Raíz
El motor de análisis marca los archivos que fallan durante el parseo (AST) con un flag `syntax_error: true`. Sin embargo, el objeto de resultado para estos archivos **no contiene el esquema completo de claves métricas**. El agregador itera sobre todos los archivos e intenta acceder a `complexity` de forma directa sin verificar si el análisis fue exitoso.

### 🛠️ Solución Propuesta (Parche de Robustez)

#### A. Implementación de Acceso Seguro
Modificar el bucle de agregación para manejar la ausencia de métricas:
```python
# Ejemplo de corrección sugerida
for module in modules:
    if module.get('syntax_error'):
        continue  # O manejar métricas nulas
    total_complexity += module.get('complexity', 0)
```

#### B. Normalización del DTO de Resultado
Asegurar que el método `analyze_file` devuelva un esquema consistente incluso en caso de error:
```python
{
    "path": "path/to/file.py",
    "complexity": 0,
    "sloc": 0,
    "syntax_error": true,
    "error_message": "...",
    "type_hints": {"coverage": 0}
}
```

---

## 2. Bug de Parser: Falso Positivo en Error de Sintaxis ('translate')

### 🔍 Síntoma
Archivos PyQGIS que utilizan la API de traducción estándar de Qt son marcados con `Syntax Error: 'translate'`.
**Ejemplo de código disparador:**
```python
# sec_interp_plugin.py
from qgis.PyQt.QtCore import QCoreApplication
...
self.menu = QCoreApplication.translate("Context", "Message")
```

### 🧬 Causa Raíz
El analizador de `ai-context-core` parece utilizar un rastreador basado en AST para contar usos de internacionalización (i18n). Este rastreador falla al encontrar una llamada a `translate` que no sigue el patrón `self.tr()` o `self.translate()`. El error se propaga hacia arriba y se captura genéricamente como un error de sintaxis del archivo, cuando en realidad es un fallo del **visitante AST** de la herramienta.

### 🛠️ Solución Propuesta (Mejora del Parser)

#### A. Ampliación del AST Visitor
Actualizar el `NodeVisitor` encargado de i18n para reconocer llamadas calificadas:
- `Call -> Attribute (value: Name('QCoreApplication'), attr: 'translate')`
- `Call -> Attribute (value: Attribute(Name('QtCore'), attr: 'QCoreApplication'), attr: 'translate')`

#### B. Aislamiento de Errores de Plugins
Los fallos en plugins secundarios (i18n, seguridad, patrones) **no deben invalidar las métricas core**.
```python
try:
    i18n_metrics = i18n_analyzer.visit(tree)
except Exception:
    # Registrar el error internamente pero permitir que el análisis de complejidad continúe
    self.log_warning("Failed to parse i18n for", file_path)
    i18n_metrics = {}
```

---
**Reportado por**: Antigravity (IA Agent) | **Estado**: Solicitud de revisión técnica.
