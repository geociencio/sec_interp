# Roadmap Técnico: Refactorización y Mejora de qgis-manage

Este documento está dirigido a los desarrolladores y mantenedores de la herramienta `qgis-manage` (paquete `qgis-manager`). Describe las estrategias técnicas para resolver las limitaciones identificadas.

---

## 1. Flexibilidad de Archivos mediante `.pluginignore`

### El Problema
Las exclusiones están hardcoded en `discovery.get_source_files` y `core.create_plugin_package`.

### Solución Propuesta
Implementar un sistema de filtrado basado en patrones (tipo `.gitignore`).

**Pasos de Implementación**:
1.  Crear un módulo `ignore.py` que utilice la librería `pathspec`.
2.  Añadir una función `load_ignore_patterns(root_path: Path)` que busque un archivo `.pluginignore`.
3.  Si no existe, cargar una lista de exclusiones por defecto (las actuales).
4.  Refactorizar `get_source_files` para aceptar un objeto `PathSpec`.

```python
# Propuesta de cambio en discovery.py
def get_source_files(project_root: Path, spec: PathSpec):
    for item in project_root.iterdir():
        if spec.match_file(item.name):
            continue
        yield item
```

---

## 2. Modernización de Compilación (RCC)

### El Problema
Dependencia forzada de `pyrcc5` y generación de imports incompatibles.

### Solución Propuesta
Abstractizar el compilador de recursos y añadir un post-procesador de código.

**Pasos de Implementación**:
1.  **Configuración**: Añadir en `config.py` soporte para detectar el compilador en el `pyproject.toml` (ej. `[tool.qgis-manager.compiler]`).
2.  **Detección Dinámica**: Si no se especifica, buscar en el PATH por orden de preferencia: `pyside6-rcc`, `pyrcc5`.
3.  **Post-Processor**: Implementar una función que lea el archivo `.py` generado y ejecute el reemplazo de `PyQt5` por `qgis.PyQt`.

```python
def patch_resource_file(py_file: Path):
    content = py_file.read_text()
    new_content = content.replace("from PyQt5 import", "from qgis.PyQt import")
    py_file.write_text(new_content)
```

---

## 3. Validación Estructural Profunda

### El Problema
`validation.py` solo valida el contenido textual de `metadata.txt`.

### Solución Propuesta
Extender `ValidationResult` para incluir chequeos de sistema de archivos.

**Nuevos Chequeos a Implementar**:
-   **Icon Check**: Verificar que el archivo definido en `icon=...` existe en el root.
-   **Resource Check**: Si hay un `resources.qrc`, verificar que existe un archivo `.py` compilado asociado.
-   **Structure Check**: Asegurar que existe un `__init__.py` con la función `classFactory`.
-   **Slug Validation**: Alertar si el nombre del directorio actual difiere significativamente del slug generado por el nombre del plugin.

---

## 4. Optimización de Backups y Despliegue

### El Problema
Backups infinitos y lentitud por copia recursiva indiscriminada.

### Solución Propuesta
1.  **Rotación de Backups**: Limitar a los últimos N backups (configurable, default: 3).
2.  **Detección de Cambios**: Usar timestamps o hashes para copiar solo archivos modificados (similar a `rsync`).
3.  **Flag de Limpieza**: Añadir un comando `qgis-manage deploy --purge-backups` para limpiar versiones antiguas.

---

## 5. Arquitectura de Hooks Mejorada

### El Problema
Los hooks actuales son limitados y difíciles de depurar.

### Solución Propuesta
Permitir hooks definidos en Python además de comandos de shell.
- Buscar un archivo `plugin_hooks.py` en el root del proyecto.
- Ejecutar funciones específicas (ej. `pre_deploy`, `post_package`) pasando el contexto del proyecto como argumento.
