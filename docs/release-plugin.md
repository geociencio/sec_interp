---
description: Proceso para crear una liberación (release) limpia del plugin de QGIS
---

Este flujo de trabajo guía la preparación, empaquetado y publicación de una nueva versión.

### 1. Preparación de Metadatos
// turbo
1. Actualizar `metadata.txt` con la nueva versión y el log de cambios.
2. Actualizar `docs/CHANGELOG.md` con los detalles técnicos.
3. Ejecutar `python analyze_project_optfixed.py` para sincronizar métricas.

### 2. Configuración de Exclusiones
1. Revisar `.gitattributes` para asegurar que los nuevos archivos de desarrollo tengan `export-ignore`.
   - Se deben ignorar: `.ai-context/`, `.git/`, `tests/`, `Makefile`, `scripts/`, `.pylintrc`, `.flake8`, `.analyzerignore`.

### 3. Generación del ZIP (Clean Build)
// turbo
1. Hacer commit de todos los cambios de preparación: `git commit -am "chore(release): prepare version X.Y.Z"`.
2. Ejecutar el comando de paquete: `make package VERSION=main`.
3. Renombrar el archivo: `mv sec_interp.zip sec_interp_vX.Y.Z.zip`.

### 4. Verificación y Tagging
1. Verificar el contenido del ZIP: `unzip -l sec_interp_vX.Y.Z.zip`.
2. Crear y subir el tag:
   ```bash
   git tag vX.Y.Z -m "Release description"
   git push origin main && git push origin vX.Y.Z
   ```

### 5. Publicación en Repositorios
1. Subir a GitHub Releases adjuntando el ZIP.
2. Subir a [plugins.qgis.org](https://plugins.qgis.org/) para distribución general.
