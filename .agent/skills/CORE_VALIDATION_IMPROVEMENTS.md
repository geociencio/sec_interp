# Recomendaciones Arquitectónicas: core.py & validation.py

## Áreas de Auditoría (Auditoría: 2026-02-19)
Se han revisado los módulos principales `core.py` (Manejo de Operaciones de Build y Deploy) y `validation.py` (Cumplimiento de Estándares de QGIS) en el repositorio `qgis-plugin-manager`.

## Hallazgo 1: Construcción de Paquetes Asíncrona / I/O Blocking
**Módulo:** `src/qgis_manager/core.py` (Función `create_plugin_package`)

**Problema:** La recolección de archivos y la compresión en ZIP se realizan en el hilo principal de manera síncrona:
```python
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for item, arcname in items_to_zip:
        zipf.write(item, arcname)
```
Si bien los plugins de QGIS suelen ser ligeros (<5MB), durante lanzamientos automatizados esto bloquea completamente la interfaz de la terminal.
**Recomendación (Fase 1 - Optimización):**
Considerar extraer el proceso de compresión a un `ThreadPoolExecutor` (simil a como se hizo en la traducción masiva `qgis-manage compile`), o en su defecto, implementar `zipfile.ZIP_LZMA` si se busca hiper-optimizar el tamaño del payload sin importar el costo de CPU (QGIS soporta ambos, pero DEFLATED es más estándar).

## Hallazgo 2: Riesgo de Bucle Infinito en Simlinks Perversos
**Módulo:** `src/qgis_manager/core.py` (Función `sync_directory` y `create_plugin_package`)

**Problema:** Actualmente usas `rglob("*")` y `iterdir()` de pathlib confiando en el `IgnoreMatcher`. Sin embargo, si un usuario crea un Symlink circular en su directorio de desarrollo, tu iterador puede colapsar por recursión infinita o empaquetarlo inadvertidamente provocando redundancia masiva.
**Recomendación (Fase 1 - Seguridad):**
En `get_source_files` y los iteradores de empaquetado, filtra explícitamente los simlinks o utiliza `os.walk` manejando `followlinks=False`.

```python
# Modificación en core.py:452
if file_path.is_file() and not file_path.is_symlink() and not matcher.should_exclude(file_path):
```

## Hallazgo 3: Validación de Metadata Demasiado Superficial
**Módulo:** `src/qgis_manager/validation.py`

**Problema:** La función `validate_metadata` es exhaustiva revisando presencia, pero superficial revisando *contenido* para los estándares de QGIS Plugin Repository v3.
**Limitaciones Actuales:**
1. No valida estrictamente el tamaño y dimensiones del `icon.png` (idealmente debe ser 128x128px o 256x256px y cuadrado).
2. Valida Booleanos revisando si son 'True' o 'False' (en string) pero la API XML de QGIS a menudo falla si tienen comillas en vez del valor primitivo. (e.g., `experimental=False` vs `experimental="False"`).
3. `validate_version` asume formato numérico estricto (`^\d+\.\d+(\.\d+)?$`), pero el repositorio de QGIS acepta pre-releases en metadata bajo ciertas condiciones (ej. `v3.1.0-alpha.1`).

**Recomendación (Fase 2 - Cumplimiento Rígido de QGIS):**
Implementar verificaciones avanzadas:

```python
# Ejemplo de validación semver extendida en validation.py:86
def validate_version(version_str: str) -> bool:
    # Soporte para Semantic Versioning completo incluyendo prereleases y build metadata
    pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-zA-Z0-9-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][a-zA-Z0-9-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    return bool(re.match(pattern, version_str))
```

## Hallazgo 4: Falta de Limpieza de Caches del Sistema
**Módulo:** `src/qgis_manager/core.py` (Función `clean_artifacts`)

**Problema:** Eliminas `__pycache__` y `.pyc`. No obstante, QGIS 3.x a menudo compila dinámicamente archivos `.ui` dentro de `.qgis3/python/plugins/...`.
**Recomendación:** Expandir la funcionalidad `clean` para purgar también `.pytest_cache`, `.ruff_cache` y archivos generados temporalmente por bibliotecas espaciales (`*.qpj`, `*.cpg` ocultos) si están bajo el control de versiones local antes de empaquetar.

## Checklist para el Desarrollador/AI

1. [ ] **core.py:** Aplicar blindaje contra symlinks en `create_plugin_package()` e iteradores recursivos.
2. [ ] **validation.py:** Reemplazar el RegEx manual de versión por la especificación oficial SemVer (o depender nativamente de la librería `packaging` incluida en Python moderno).
3. [ ] **core.py:** Enriquecer `clean_artifacts()` para abarcar los `.cache` generados típicamente por las herramientas de desarrollo especificadas (pytest, ruff, black).
