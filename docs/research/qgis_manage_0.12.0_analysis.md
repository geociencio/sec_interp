# Análisis técnico: qgis-manage 0.10.0 → 0.12.0

> **Fecha**: 2026-10-25
> **Versión analizada**: `qgis-manage` 0.12.0 (PyPI, 2026-10-25)
> **Versiones intermedias**: 0.10.1, 0.11.0 (mismo día)
> **Entorno**: Linux (Manjaro), Python 3.12, proyecto `sec_interp` 3.11.0
> **Método**: lectura del código instalado + mediciones reproducibles sobre este
> repositorio (340 archivos desplegados, ZIP de 2.4 MB). Cifras locales (SSD);
> sirven para comparar órdenes de magnitud.
> **Documento histórico**: no forma parte de la documentación activa auditada por
> `scripts/check_docs.py`. Sustituye al análisis previo de 0.10.0.

---

## 1. Resumen ejecutivo

Las releases 0.10.1, 0.11.0 y 0.12.0 implementan **casi todas** las
recomendaciones del análisis de 0.10.0:

- **0.10.1** corrigió los tres fallos de correctitud: backups con microsegundos,
  `--type` repetible, guard de `--release-version`, `deploy --yes`, `clean`
  seguro (`--dry-run`, `--keep-generated`).
- **0.11.0** añadió el manifiesto de deploy, backups con reflink, frescura de
  compilación y poda del escaneo de `--repo-check`.
- **0.12.0** añadió `--json`, `ignore check`/`--explain`, `deploy --dry-run`,
  `profiles list`, `package --require-docs` y `analyze --max-cc`, y cambió el
  default de hooks a **no-shell** (breaking, sin impacto aquí).

Quedan **tres limitaciones** relevantes para plugins multilingües/complejos:
`--require-docs` asume `help/html/index.html`; `clean` borra `.cpg`/`.qpj`
versionados; y `profiles list` solo enumera QGIS 3. Además, el manifiesto de
deploy es neutro o algo más lento en plugins pequeños.

---

## 2. Qué se corrigió respecto a 0.10.0

| Hallazgo de 0.10.0 | Estado en 0.12.0 | Verificación |
| :--- | :--- | :--- |
| Backup colisionaba dentro del mismo segundo | **Corregido**: `%f` + sufijo anticolisión y reflink | 3 deploys consecutivos `rc=0` |
| `--type` no repetible (last-wins) | **Corregido**: `action="append"` | `compile --type resources --type translations` compila ambas familias |
| `--release-version` no sincronizaba metadata | **Corregido**: falla salvo `--stamp`/`--sync-version` | `rc=1` con mensaje claro |
| `--purge-backups` no interactivo | **Corregido**: `deploy --yes` | `rc=0` sin TTY |
| `clean` borraba `resources.py` | **Mitigado**: `--dry-run`, `--keep-generated`, aviso si está en Git | `keep resources/resources.py` en dry-run |
| `--repo-check` recorría `.venv`/`docs` | **Corregido**: un `os.walk` que poda directorios ignorados | 3 193 ms → **671 ms** |
| Deploy releía todo el contenido | **Mitigado**: manifiesto de huellas | ver §3 (neutro en plugin pequeño) |
| Compilación reescribía archivos idénticos | **Corregido**: salida temporal + comparación de bytes; `.qm` solo si el `.ts` es más nuevo | árbol limpio tras `make compile` |

También se incorporaron capacidades nuevas: `deploy --dry-run`, `profiles list`,
`ignore check`/`--explain`, `--json` en `validate`/`analyze`/`package`, y
`package --require-docs`.

---

## 3. Mediciones 0.10.0 vs 0.12.0

| Flujo | 0.10.0 | 0.12.0 | Δ |
| :--- | ---: | ---: | ---: |
| `package` | 577 ms | 609 ms | ≈ (ruido) |
| `package --repo-check` | **3 193 ms** | **671 ms** | **4.8× más rápido** |
| `package --repo-check --stamp` (CI completo) | — | 676 ms | — |
| `deploy` con backup (sin cambios) | 454 ms | 442–446 ms | ≈ |
| `deploy --no-manifest` (sin backup) | 423 ms | 425 ms | ≈ |
| `deploy` con manifiesto (sin backup) | — | 455 ms | +30 ms |
| `compile --type translations` (13 `.ts`, desde cero, `--jobs 4`) | 132 ms | 128 ms | ≈ |
| `compile --type translations` con `.qm` al día | 132 ms | **111 ms** | skip de frescura |
| Deploys consecutivos en el mismo segundo | `rc=1` | `rc=0` | corregido |

El manifiesto vive en `.qgis-manage/deploy-manifest.json` (165 KB para 340
archivos) y se guarda en cada deploy: en un plugin pequeño el coste de
serializar/leer el JSON compensa la lectura de contenido. En árboles grandes
(miles de archivos, cientos de MB) sí debería ganar; para este repositorio,
`--no-manifest` es ligeramente más rápido hoy.

---

## 4. Limitaciones encontradas en 0.12.0

### 4.1 `--require-docs` asume un layout concreto

Comprueba `help/html/index.html`. SecInterp publica la ayuda por idioma
(`help/html/en/index.html`, `help/html/es/index.html`, …) sin índice raíz, así
que el flag da un **falso negativo**:

```text
❌ --require-docs: help/html/index.html is missing.
```

Recomendación upstream: aceptar una ruta configurable
(`[tool.qgis-manager] docs_entry`) o considerar válido cualquier
`help/html/*/index.html`. Mientras tanto, SecInterp no usa el flag y mantiene
`make zip` dependiente de `docs`.

### 4.2 `clean` borra archivos versionados que no son `.py`

`clean --keep-generated` protege los `.py` generados, pero no los sidecars de
QGIS (`*.cpg`, `*.qpj`). Este repositorio versiona
`examples/sample_data/{area,geologia,pts,secc1}.cpg`, que `clean` eliminaría:

```text
remove examples/sample_data/area.cpg
keep resources/resources.py
```

Recomendación upstream: `--keep-tracked` (o excluir todo archivo rastreado) y
aplicar el mismo aviso que ya existe para `.py` generados. SecInterp usa un
`clean` propio que solo borra cachés y `help/html`.

### 4.3 `profiles list` solo enumera QGIS 3

No acepta `--qgis-version`; en un proyecto que despliega a QGIS 4 la salida no
incluye el perfil de destino:

```text
Profiles for QGIS 3:
  default   .../QGIS3/profiles/default   19 plugins
```

Recomendación upstream: `--qgis-version 3|4|all` (o listar ambos por defecto).

### 4.4 Hooks no-shell por defecto (breaking)

`HookPolicy.shell` pasa a `False`: los comandos con sintaxis de shell requieren
`HookPolicy(shell=True)` explícito. SecInterp no tiene `plugin_hooks.py`, así que
no hay impacto, pero conviene documentarlo para plugins que sí los usan.

### 4.5 Detalles menores

- `ignore check <path>` responde `excluded` sin indicar la regla ganadora;
  `--explain` solo detalla el caso incluido. Útil para depurar `.qgisignore`.
- `.qgis-manage/` está en `DEFAULT_EXCLUDE_PATTERNS` (no se empaqueta ni
  despliega) pero no se añade a `.gitignore` automáticamente; el proyecto debe
  ignorarlo.

---

## 5. Estado de las recomendaciones previas

| Recomendación (0.10.0) | Estado |
| :--- | :--- |
| Microsegundos en backups | ✅ 0.10.1 |
| `--type` repetible | ✅ 0.10.1 |
| Guard `--release-version` | ✅ 0.10.1 |
| `deploy --purge-backups --yes` | ✅ 0.10.1 |
| `clean --dry-run` / no borrar versionados | ⚠️ parcial (`--keep-generated` solo `.py`) |
| Poda del escaneo de binarios | ✅ 0.11.0 (4.8×) |
| Manifiesto de deploy | ✅ 0.11.0 (neutro en plugins pequeños) |
| Backups reflink | ✅ 0.11.0 |
| Frescura de compilación | ✅ 0.11.0 |
| `--json`, `ignore check`, `deploy --dry-run`, `profiles list`, `analyze --max-cc` | ✅ 0.12.0 |
| `package --require-docs` | ⚠️ layout rígido |
| Hooks shell desactivado por defecto | ✅ 0.12.0 (breaking) |

---

## 6. Acciones aplicadas en SecInterp (0.12.0)

1. **Dependencia**: `qgis-manage>=0.12.0` (lock 0.12.0).
2. **Makefile `compile`**: usa `--type resources --type translations` en una sola
   invocación cuando hay que reconstruir recursos; si no, solo traducciones. Se
   mantiene el guard por `.qrc`/`icon.png` porque el `resources.py` versionado se
   generó con otro build de `pyrcc` (comillas + mtimes embebidos) y una
   recompilación siempre difiere en bytes.
3. **Makefile `clean`**: limpieza propia (cachés + `help/html`) para no borrar
   `resources.py` ni los `.cpg` versionados; documentado el motivo.
4. **Makefile `zip`**: `package --repo-check`.
5. **CI de release**: `package --repo-check --stamp --release-version` (stamp
   garantiza que el `metadata.txt` empaquetado coincide con la versión).
6. **`.gitignore`/`.qgisignore`**: `.qgis-manage/` (manifiesto de deploy).
7. **`[tool.qgis-manager]`**: `qgis_version = 4`, `max_backups = 1`,
   `auto_compile = false`.

---

## 7. Recomendaciones upstream restantes

| Prioridad | Mejora | Motivo |
| :--- | :--- | :--- |
| **P0** | `clean --keep-tracked` (o no borrar `.cpg`/`.qpj` versionados) | pérdida de datos en repos con sample data |
| **P1** | `package --require-docs <path>` / aceptar `help/html/*/index.html` | plugins multilingües |
| **P1** | `profiles list --qgis-version 3\|4\|all` | proyectos QGIS 4 |
| **P2** | Manifiesto: reescribir solo si cambia y comprimir/clave por directorio | reduce el overhead en plugins pequeños |
| **P2** | `ignore check --explain` también para el caso excluido | depuración de `.qgisignore` |
| **P2** | `.qgis-manage/` autoañadido a `.gitignore` o `qgis-manage init` | evitar ruido en `git status` |

---

## 8. Reproducción

```bash
# Packaging y gate de repositorio (comparar con 0.10.0: 3.2 s)
time .venv/bin/qgis-manage package -o /tmp/pkg --repo-check

# Guard de versión
.venv/bin/qgis-manage package -o /tmp/pkg --release-version 9.9.9   # rc=1

# Deploy consecutivo (0.10.0 fallaba con File exists)
.venv/bin/qgis-manage deploy --no-compile --qgis-version 4 --profile /tmp/dep
.venv/bin/qgis-manage deploy --no-compile --qgis-version 4 --profile /tmp/dep
.venv/bin/qgis-manage deploy --dry-run --qgis-version 4 --profile /tmp/dep

# Manifiesto vs escaneo completo
time .venv/bin/qgis-manage deploy --no-compile --no-backup --qgis-version 4 --profile /tmp/d
time .venv/bin/qgis-manage deploy --no-compile --no-backup --qgis-version 4 --profile /tmp/d --no-manifest

# Frescura de compilación
time .venv/bin/qgis-manage compile --type translations --jobs 4

# Limpieza segura
.venv/bin/qgis-manage clean --dry-run --keep-generated
.venv/bin/qgis-manage ignore check graphify-out
```

> **Nota**: en entornos con `/tmp` efímero por invocación, crear y usar los
> directorios temporales dentro de la misma llamada de shell.
