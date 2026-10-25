# Guía de Despliegue y Mantenimiento: qgis-manage

Esta guía detalla el funcionamiento interno, las limitaciones conocidas y las mejores prácticas para el uso de la herramienta `qgis-manage` (basada en `qgis-plugin-manager`) en el proyecto SecInterp.

## 🚀 El Proceso de Despliegue (Deploy)

El comando `qgis-manage deploy` realiza las siguientes acciones:
1. Localiza el `metadata.txt` para identificar el "slug" del plugin.
2. Detecta el perfil de QGIS del sistema (Linux, macOS o Windows).
3. Crea un backup en la carpeta de perfiles (ej. `sec_interp.bak.20261025100912.123456`).
4. **Copia selectiva**: sincroniza solo los archivos cambiados (tamaño + contenido; desde 0.11.0 también un manifiesto de huellas).

### ⚠️ Problemas Críticos con el Deploy

#### 1. Exclusiones Rígidas (Shadowing)
La herramienta ignora automáticamente carpetas como `.agent`, `tests`, `scripts`, `tools` y `research`.
- **Problema**: Si un desarrollador añade una herramienta nueva en una carpeta no listada anteriormente (ej. `utils/deploy_helper`), esta se copiará al perfil de QGIS, aumentando el peso del plugin innecesariamente.
- **Inverso**: Si necesitas que un script de `scripts/` esté disponible en el plugin instalado para alguna función de depuración, `qgis-manage` **lo borrará** durante el despliegue.

#### 2. Backups
Cada `deploy` genera una nueva carpeta `.bak` en el directorio de plugins de QGIS.
- **Rotación (0.10.0+)**: se conservan automáticamente los N backups más recientes (`max_backups`, 1 en SecInterp).
- **Colisiones (0.10.1+)**: el timestamp incluye microsegundos y sufijo anticolisión; ya no fallan dos deploys en el mismo segundo.
- **Reflink (0.11.0+)**: en Linux intenta `cp -a --reflink=auto` antes de `copytree` (backup casi gratis en btrfs/xfs).
- **Limpieza total**: `qgis-manage deploy --purge-backups --yes` purga y continúa sin preguntar (en 0.9.x era un no-op). Ojo: tras purgar, el propio deploy crea un backup nuevo.
- **Recomendación**: Usar `--no-backup` una vez que la estructura del plugin sea estable.

#### 3. Manifiesto de deploy (0.11.0+)
El manifiesto se guarda en `.qgis-manage/deploy-manifest.json` (ignorado por Git y por `.qgisignore`) y evita releer contenido sin cambios. En un plugin pequeño (340 archivos) es neutro o algo más lento que `--no-manifest`; en árboles grandes gana. Usa `--dry-run` para ver copias/borrados/backup sin tocar el destino.

#### 4. Hooks y confianza (`--trust`)
`deploy` **no ejecuta** hooks del proyecto (`plugin_hooks.py`) salvo que se pase `--trust`; `package` tampoco instala dependencias declaradas sin ese flag. Desde 0.12.0 los hooks son **no-shell por defecto** (`HookPolicy.shell=False`): la sintaxis de shell requiere opt-in explícito. SecInterp no usa hooks, así que no se necesita `--trust` en el flujo normal. No añadir `--trust` a ciegas en CI: solo es seguro en un checkout que controlas.

---

## 🛠️ Compilación y Recursos (Compile)

### Imports de Qt en Resources/UI
`pyrcc5`/`pyuic5` generan históricamente `from PyQt5 ...`, que no es el estándar de QGIS (`qgis.PyQt`).

#### Estado en 0.10.0+
`qgis-manage compile` **auto-parchea** las salidas de `rcc` y `uic` (`patch_resource_file`, `patch_ui_file`). Ya **no** hace falta el `sed` manual:

```bash
qgis-manage compile --type resources --type translations --jobs 4
```

Verificación (debe salir 0):
```bash
grep -c "from PyQt5\|from PySide" resources/resources.py
```

Desde 0.11.0 la compilación es **atómica**: escribe a temporal y solo reemplaza si cambian los bytes, y omite los `.qm` más nuevos que su `.ts`. Aun así, el `resources.py` versionado se generó con otro build de `pyrcc` (comillas + mtimes embebidos), por lo que el Makefile solo lo reconstruye cuando cambian el `.qrc` o el icono.

#### Versiones anteriores (≤ 0.9.x)
Sí era necesario parchear a mano tras compilar:
```bash
sed -i 's/from PyQt5 import QtCore/from qgis.PyQt import QtCore/g' resources/resources.py
```

### `--type` repetible (0.10.1+)
Desde 0.10.1 `--type` se puede repetir:
```bash
qgis-manage compile --type resources --type translations
```
En 0.10.0 y anteriores solo se aplicaba el último valor (`--type resources --type translations` compilaba únicamente traducciones); usa una invocación por tipo si trabajas con esa versión.

### `clean` y archivos versionados
`qgis-manage clean` elimina los `.py` generados junto a cada `.qrc`/`.ui` y **todos** los `*.cpg`/`*.qpj`. En este repositorio eso incluye `resources/resources.py` y los sidecars de `examples/sample_data/*.cpg`, así que:
- `qgis-manage clean --dry-run --keep-generated` para inspeccionar (protege los `.py`, no los `.cpg`).
- `make clean` usa una limpieza propia (cachés + `help/html`) que **no borra archivos versionados**.

---

## 💡 Recomendaciones para Desarrolladores

### Para Desarrolladores Humanos
- **Validación Cruzada**: No asumas que `qgis-manage validate` es suficiente. Revisa siempre que el número de versión en `metadata.txt` coincida con `pyproject.toml`. Desde 0.10.0 el validador exige `True`/`False` en los campos booleanos (p. ej. `hasProcessingProvider`) y versiones `X.Y.Z`; `--strict --repo` añade el gate del portal.
- **Empaquetado**: `package --repo-check` valida licencia/binarios/campos; `--stamp` inyecta `version`, `commitSha1`, `commitNumber`, `dateTime` y `experimental` solo en el ZIP, y `--release-version` exige que coincida con `metadata.txt` salvo que uses `--stamp`/`--sync-version`.
- **Limpieza de Backups**: Prefiere `qgis-manage deploy --purge-backups --yes`; el borrado manual ya no es necesario:
  ```bash
  qgis-manage deploy --purge-backups --yes
  ```
- **Uso de Hooks**: `qgis-manager` soporta hooks (`plugin_hooks.py`), pero `deploy` los omite salvo que se pase `--trust`. Desde 0.12.0 son no-shell por defecto: la sintaxis de shell requiere `HookPolicy(shell=True)`. Configura el hook y ejecuta `uv run qgis-manage deploy --trust` solo en un checkout propio.

### Para Asistentes de IA (Agentes)
- **Protocolo de Compilación**: En 0.10.0+ no añadas un `sed` posterior; en 0.10.1+ puedes repetir `--type`:
  `qgis-manage compile --type resources --type translations --jobs 4`.
- **Verificación de Entorno**: Antes de sugerir un `deploy`, verifica si el usuario está usando un perfil de QGIS personalizado y sugiere el flag `-p <nombre_perfil>` si es necesario. `deploy --dry-run` muestra copias/borrados/backup sin mutar el destino.
- **Gestión de Archivos**: Si creas nuevos módulos, asegúrate de que no queden atrapados en las exclusiones por defecto si son necesarios para el runtime del plugin.

---

## 📋 Checklist de Despliegue Seguro

1. [ ] Limpiar con `qgis-manage clean --dry-run --keep-generated` y revisar la salida. **Ojo**: el `clean` real borra los `.py` generados y los `*.cpg`/`*.qpj`; en SecInterp usa `make clean`, que preserva los archivos versionados.
2. [ ] Ejecutar `qgis-manage compile --type resources --type translations --jobs 4`.
3. [ ] Verificar que `resources/resources.py` usa `qgis.PyQt` (en 0.10.0+ es automático).
4. [ ] Verificar `metadata.txt` con `qgis-manage validate --strict --repo`.
5. [ ] Opcional: `qgis-manage deploy --dry-run` para revisar copias/borrados y el backup.
6. [ ] Ejecutar `deploy` y verificar en los logs de QGIS que no hay errores de importación.
