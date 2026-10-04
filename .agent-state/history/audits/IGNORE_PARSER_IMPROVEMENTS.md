# Recomendaciones Arquitectónicas: Refactorización de `ignore.py`

## Contexto Actual
El módulo `src/qgis_manager/ignore.py` en `qgis-plugin-manager` se encarga de parsear y evaluar qué archivos deben excluirse al empaquetar plugins de QGIS. Actualmente utiliza `fnmatch` nativo de Python para evitar dependencias externas, sumando reglas de `.gitignore`, `.qgisignore` y `pyproject.toml`.

## Hallazgos de la Auditoría (Auditoría: 2026-02-19)

### 1. Sistema Sumatorio vs Sobreescritura (Fallback Exclusivo)
**Código actual (`load_ignore_patterns`):**
```python
for ignore_name in [".gitignore", ".qgisignore"]:
    ignore_file = project_root / ignore_name
    if ignore_file.exists():
        # Añade TODAS las reglas encontradas
```
**Problema:** En el desarrollo de QGIS, a menudo el usuario quiere que Git ignore cosas fundamentales (como dependencias binarias estáticas) pero SÍ las quiere en el empaquetado final (`.qgisignore`). Al sumar todo el `.gitignore`, se fuerzan archivos en el ZIP que no deberían estar ahí, o por el contrario, se excluyen bibliotecas válidas.
**Expectativa:** Si existe `.qgisignore`, el empaquetador DEBE ignorar por completo el `.gitignore`. Solo debe hacer fallback a `.gitignore` si `.qgisignore` **no** está en la raíz del proyecto.

### 2. Limitaciones Estructurales de `fnmatch` (Recursividad Inexplícita)
**Código actual (`IgnoreMatcher.should_exclude`):**
```python
if fnmatch.fnmatch(path_str, p) or fnmatch.fnmatch(path_str, f"*/{p}"):
```
**Problema:** `fnmatch` no entiende de manera nativa la recursión profunda como lo hace Git.
- Si un usuario escribe en su ignore `logs/debug` y tiene el directorio `logs/debug/my_plugin.log`, el evaluador ve `path_str = "logs/debug/my_plugin.log"` y `p = "logs/debug"`.
- `fnmatch("logs/debug/my_plugin.log", "logs/debug")` es `False`.
- `fnmatch("logs/debug/my_plugin.log", "*/logs/debug")` es `False`.
**Consecuencia:** Archivos y directorios profundamente anidados "se escapan" al `.zip` a menos que el usuario los marque explícitamente con comodines (ej. `logs/debug/*`).

## Propuestas de Implementación (AI / Developer Instructions)

Para mantener la filosofía cero-dependencias (no agregar la librería `pathspec`), instruye al agente AI que ejecute la siguiente implementación en tu base de código:

### Fase 1: Corregir lógica de Carga de Ignore
En `load_ignore_patterns`, modifica la recopilación de `.gitignore`/`.qgisignore` para que sea **exclusiva**:

```python
    # 1. Tratar de cargar .qgisignore PRIMERO. Si existe, no leer .gitignore.
    ignore_loaded = False
    for ignore_name in [".qgisignore", ".gitignore"]:
        if ignore_loaded:
            break

        ignore_file = project_root / ignore_name
        if ignore_file.exists():
            try:
                with open(ignore_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
                ignore_loaded = True # Evita leer el siguiente
            except Exception:
                pass
```

### Fase 2: Robustecer Parser Matcher en `IgnoreMatcher`
Reemplaza la lógica central del `should_exclude` para emular un comportamiento compatible con `pathspec`:
En `should_exclude(self, path: Path) -> bool:`

```python
    def should_exclude(self, path: Path) -> bool:
        """Determines if a path should be excluded using fnmatch with Git-like semantics."""
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            return False

        path_str = str(rel_path).replace("\\", "/")
        parts = rel_path.parts

        for pattern in self.patterns:
            p = pattern.rstrip("/")
            is_root_relative = p.startswith("/")
            if is_root_relative:
                p = p[1:]

            if is_root_relative:
                # Modificado para emparejar si el path ES la carpeta o ESTÁ DENTRO de ella.
                if fnmatch.fnmatch(path_str, p) or path_str.startswith(p + "/"):
                    return True
            else:
                # Un patrón sin '/' al inicio como "logs" debe hacer match con
                # - Cualquier archivo "logs" en cualquier subcarpeta.
                # - Cualquier directorio "logs" en cualquier subcarpeta y TODOS SUS ENTRAMADOS
                if any(fnmatch.fnmatch(part, p) for part in parts):
                    return True

                # Match con ruta completa (ej "logs/*")
                if fnmatch.fnmatch(path_str, p) or fnmatch.fnmatch(path_str, f"*/{p}"):
                    return True

                # RECURSIVIDAD IMPLÍCITA: Si el path INICIA con el pattern más '/'
                # ej. Pattern es "logs/debug". El path es "logs/debug/file.txt".
                if path_str.startswith(f"{p}/") or f"/{p}/" in path_str:
                    return True

        return False
```

## Checklist Final para el Arquitecto / LLM
- [ ] Implementar la carga exclusiva explícita (`.qgisignore` anula silenciosamente `.gitignore`).
- [ ] Agregar el código de recursividad implícita al `IgnoreMatcher`.
- [ ] Incorporar tests rápidos creando directorios profundos (ej. `mkdir -p fake/nested/logs/debug`) y comprobando que se excluyen incluso si el patrón en el ignore text es solo `logs/debug` sin comodines.
- [ ] Bump de versión en `pyproject.toml` (ej. `0.6.2`).
