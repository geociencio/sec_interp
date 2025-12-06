# Proceso de Liberación (Release Process)

Este documento describe los pasos para preparar y liberar una nueva versión del plugin **Sec Interp**.

## 1. Preparación

1.  **Actualizar Versión**:
    *   Editar `metadata.txt`.
    *   Incrementar el número de versión en `version=X.Y`.
    *   Agregar una nueva entrada en la sección `changelog=` con la fecha y los cambios más importantes.

2.  **Actualizar Documentación**:
    *   Asegurarse de que `README.md` y otros documentos estén actualizados.
    *   Generar la documentación de ayuda si es necesario: `make doc`.

3.  **Compilar Traducciones**:
    *   Ejecutar `make transup` para actualizar los archivos `.ts`.
    *   Traducir las nuevas cadenas en Qt Linguist.
    *   Ejecutar `make transcompile` para generar los archivos `.qm`.

## 2. Empaquetado

1.  **Limpiar**:
    *   Ejecutar `make clean` para eliminar archivos temporales y compilados anteriores.

2.  **Generar Zip**:
    *   Ejecutar `make zip`.
    *   Esto creará un archivo `sec_interp.zip` en el directorio raíz (o donde especifique el Makefile).

## 3. Verificación

1.  **Instalación Local**:
    *   Instalar el zip generado en QGIS (Complementos -> Instalar a partir de ZIP).
    *   Verificar que el plugin carga correctamente y que la nueva versión se muestra en el administrador.

2.  **Pruebas Finales**:
    *   Ejecutar un flujo de trabajo completo (crear perfil, vista previa, exportación) para asegurar que no hay regresiones.

## 4. Publicación

1.  **Git Tag**:
    *   Crear un tag en git para la versión:
        ```bash
        git tag -a vX.Y -m "Release version X.Y"
        git push origin vX.Y
        ```

2.  **GitHub Release**:
    *   Crear una nueva "Release" en GitHub asociada al tag.
    *   Subir el archivo `sec_interp.zip` como binario adjunto.
    *   Copiar el changelog a la descripción de la release.

3.  **Repositorio Oficial (Opcional)**:
    *   Si se publica en el repositorio oficial de QGIS, subir el zip a plugins.qgis.org.
