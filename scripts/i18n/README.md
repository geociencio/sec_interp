# Sistema de Internacionalización (i18n) de SecInterp

Este directorio contiene la lógica para gestionar las traducciones del plugin SecInterp en múltiples idiomas. El sistema combina las herramientas estándar de Qt con un motor de "Master Data" para automatizar y normalizar las traducciones.

## Estructura del DirectorIO

- `master_data/`: Contiene archivos JSON (ej. `es.json`, `fr.json`) que actúan como "memoria de traducción" maestra.
- `apply_full.py`: Script principal que inyecta las traducciones de `master_data/` en los archivos `.ts`.
- `clean_translations.py`: Normaliza y embellece el XML de los archivos `.ts` para evitar ruido en el control de versiones.
- `update_metadata_languages.py`: Sincroniza automáticamente la lista de idiomas soportados en el archivo `metadata.txt` del plugin.
- `auto_translate_*.py`: (Opcional) Scripts para integración con servicios de traducción automática (ej. DeepL).

## Flujo de Trabajo

El flujo de trabajo está integrado en el `Makefile` del proyecto para facilitar su ejecución:

1.  **Extracción de Cadenas**:
    ```bash
    make transup
    ```
    Este comando ejecuta internamente:
    - `pylupdate5`: Escanea el código fuente y genera/actualiza los archivos `.ts` en la carpeta `i18n/`.
    - `apply_full.py`: Busca cada cadena original en los archivos JSON de `master_data/` y, si existe una traducción, la introduce en el `.ts` quitando la marca de "unfinished".
    - `clean_translations.py`: Limpia el XML resultante.
    - `update_metadata_languages.py`: Actualiza el archivo `metadata.txt`.

2.  **Traducción de Nuevas Cadenas**:
    - Si hay cadenas nuevas que no están en `master_data/`, aparecerán como `type="unfinished"` en los archivos `.ts`.
    - La recomendación es añadir la traducción al archivo JSON correspondiente en `master_data/` y volver a ejecutar `make transup`.

3.  **Compilación**:
    ```bash
    make transcompile
    ```
    Genera los archivos `.qm` binarios que QGIS carga en tiempo de ejecución.

## Reglas de Oro

- **Nunca edites los archivos `.qm`** directamente; son binarios generados.
- **Evita editar los archivos `.ts` manualmente** si puedes añadir la traducción a `master_data/`. El sistema de inyección sobrescribirá los cambios manuales en el siguiente `make transup`.
- **Cadenas en el código**: Siempre envuelve los textos de la interfaz con `self.tr("Texto")` para que sean detectables.
- **Entidades HTML**: El script `apply_full.py` está diseñado para manejar automáticamente la conversión de entidades como `&apos;` o `&gt;`, por lo que en los archivos JSON puedes usar caracteres normales (`'`, `>`, `<`).
