# Proceso de Liberación (Release Process)

Este documento describe los pasos detallados para preparar y liberar una nueva versión del plugin **Sec Interp**, optimizado para generar paquetes limpios y profesionales.

## 1. Preparación del Entorno y Versión

1.  **Sincronizar Contexto**:
    *   Ejecutar `python analyze_project_optfixed.py` para obtener métricas actualizadas.
    *   Actualizar `.ai-context/project_brain.md` con los nuevos resultados.

2.  **Actualizar Versión**:
    *   **metadata.txt**: Incrementar `version=X.Y.Z` y actualizar la sección `changelog=`.
        *   > [!IMPORTANT]
        *   > El repositorio de QGIS usa `configparser`. Debes **escapar todos los signos de porcentaje (`%`) como `%%`** en las secciones `changelog` y `about` para evitar errores de interpretación.
    *   **docs/CHANGELOG.md**: Agregar la nueva versión al principio siguiendo el estándar [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
    *   **README.md**: Actualizar badges de versión y enlaces de descarga si aplica.

3.  **Documentación**:
    *   Actualizar `docs/USER_GUIDE.md` con capturas y descripciones de nuevas funciones.
    *   Asegurar que `LICENSE` esté presente y actualizado.

## 2. Empaquetado Limpio (Crucial)

Para evitar que archivos de desarrollo como `.git`, `tests/`, o configuraciones de herramientas (`.pylintrc`, etc.) terminen en el ZIP oficial, utilizamos el método de **`git archive`**.

1.  **Configurar Exclusiones**:
    *   Revisar `.gitattributes` y asegurarse de que todos los archivos internos tengan el flag `export-ignore`.
    *   Ejemplo en `.gitattributes`:
        ```text
        .ai-context/ export-ignore
        .gitattributes export-ignore
        tests/ export-ignore
        scripts/ export-ignore
        Makefile export-ignore
        .pylintrc export-ignore
        ```

2.  **Generar el Paquete**:
    *   Asegurarse de haber hecho commit de todos los cambios.
    *   Ejecutar el comando de empaquetado (definido en el `Makefile`):
        ```bash
        make package VERSION=main
        ```
    *   Renombrar el archivo para que sea descriptivo:
        ```bash
        mv sec_interp.zip sec_interp_vX.Y.Z.zip
        ```

3.  **Verificación del Contenido**:
    *   Listar el contenido para confirmar que no hay archivos basura:
        ```bash
        unzip -l sec_interp_vX.Y.Z.zip | head -n 20
        ```

## 3. Versionamiento y Git

1.  **Tagging**:
    *   Crear el tag oficial una vez el ZIP ha sido verificado:
        ```bash
        git tag vX.Y.Z -m "Release version X.Y.Z: Resumen de cambios"
        ```

2.  **Push**:
    *   Subir la rama principal y el tag:
        ```bash
        git push origin main
        git push origin vX.Y.Z
        ```

## 4. Publicación Final

1.  **GitHub Release**:
    *   Crear una "Release" en GitHub usando el tag recién subido.
    *   Adjuntar el archivo `sec_interp_vX.Y.Z.zip` como binario.
    *   Pegar el contenido del Changelog en la descripción.

2.  **QGIS Plugin Repository**:
    *   Subir el mismo archivo ZIP a [plugins.qgis.org](https://plugins.qgis.org/).
    *   Recuerda que el ZIP **debe** contener los archivos dentro de una carpeta llamada `sec_interp/` (esto lo hace automáticamente el comando `make package`).
