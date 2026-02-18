# Guía de Despliegue y Mantenimiento: qgis-manage

Esta guía detalla el funcionamiento interno, las limitaciones conocidas y las mejores prácticas para el uso de la herramienta `qgis-manage` (basada en `qgis-plugin-manager`) en el proyecto SecInterp.

## 🚀 El Proceso de Despliegue (Deploy)

El comando `qgis-manage deploy` realiza las siguientes acciones:
1. Localiza el `metadata.txt` para identificar el "slug" del plugin.
2. Detecta el perfil de QGIS del sistema (Linux, macOS o Windows).
3. Crea un backup en la carpeta de perfiles (ej. `sec_interp.bak.2026...`).
4. **Copia selectiva**: Filtra carpetas basadas en una lista interna **hardcoded**.

### ⚠️ Problemas Críticos con el Deploy

#### 1. Exclusiones Rígidas (Shadowing)
La herramienta ignora automáticamente carpetas como `.agent`, `tests`, `scripts`, `tools` y `research`.
- **Problema**: Si un desarrollador añade una herramienta nueva en una carpeta no listada anteriormente (ej. `utils/deploy_helper`), esta se copiará al perfil de QGIS, aumentando el peso del plugin innecesariamente.
- **Inverso**: Si necesitas que un script de `scripts/` esté disponible en el plugin instalado para alguna función de depuración, `qgis-manage` **lo borrará** durante el despliegue.

#### 2. Acumulación de Backups
Cada `deploy` genera una nueva carpeta `.bak` en el directorio de plugins de QGIS.
- **Riesgo**: Agotamiento de espacio en disco en sesiones de desarrollo intensas.
- **Recomendación**: Usar el flag `--no-backup` una vez que la estructura del plugin sea estable.

---

## 🛠️ Compilación y Recursos (Compile)

### El "Bug" de PyQt5 en Resources
El comando `qgis-manage compile` utiliza `pyrcc5`, el cual genera código incompatible con los estándares modernos de QGIS que exigen el uso de `qgis.PyQt`.

#### Flujo de Error:
1. Ejecutas `qgis-manage compile`.
2. `resources/resources.py` se genera con `from PyQt5 import QtCore`.
3. El plugin falla al cargar en entornos QGIS estrictos o lanza avisos en el `qgis-analyzer`.

#### Solución Mandatoria (Manual/Scripted):
Después de cada compilación, se debe ejecutar:
```bash
sed -i 's/from PyQt5 import QtCore/from qgis.PyQt import QtCore/g' resources/resources.py
```

---

## 💡 Recomendaciones para Desarrolladores

### Para Desarrolladores Humanos
- **Validación Cruzada**: No asumas que `qgis-manage validate` es suficiente. Revisa siempre que el número de versión en `metadata.txt` coincida con `pyproject.toml`.
- **Limpieza de Backups**: Periódicamente limpia tu carpeta de plugins de QGIS:
  ```bash
  rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/*.bak.*
  ```
- **Uso de Hooks**: `qgis-manager` soporta hooks. Puedes configurar un `post-deploy` en el `pyproject.toml` para automatizar limpiezas adicionales.

### Para Asistentes de IA (Agentes)
- **Protocolo de Compilación**: Nunca compiles recursos sin un paso posterior de "parcheo" de imports.
- **Verificación de Entorno**: Antes de sugerir un `deploy`, verifica si el usuario está usando un perfil de QGIS personalizado y sugiere el flag `-p <nombre_perfil>` si es necesario.
- **Gestión de Archivos**: Si creas nuevos módulos, asegúrate de que no queden atrapados en las exclusiones por defecto si son necesarios para el runtime del plugin.

---

## 📋 Checklist de Despliegue Seguro

1. [ ] Ejecutar `qgis-manage clean` para evitar basura en el paquete.
2. [ ] Ejecutar `qgis-manage compile`.
3. [ ] **IMPORTANTE**: Parchear `resources.py` para usar `qgis.PyQt`.
4. [ ] Verificar `metadata.txt` con `qgis-manage validate`.
5. [ ] Ejecutar `deploy` y verificar en los logs de QGIS que no hay errores de importación.
