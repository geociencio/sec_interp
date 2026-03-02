---
description: Procedure for i18n maintenance and expansion (Translations)
agent: QA Engineer
skills: [i18n-standards, project-context]
---

# Workflow: Mantenimiento de i18n

Este workflow asegura que las traducciones estén sincronizadas con el código y se expandan siguiendo el estándar de "Master Data".

## Pasos

1. **Sincronizar Cadenas**:
   // turbo
   Ejecutar `./scripts/update-strings.sh "<locales>"` para extraer las últimas cadenas del código fuente.

2. **Validar Cadenas sin Traducir**:
   Ejecutar `python3 scripts/i18n_diagnostic.py` para ver qué archivos tienen más cadenas pendientes.

3. **Actualizar Datos Maestros (JSON)**:
   - Si es un idioma nuevo: Crear `scripts/i18n/master_data/<lang>.json`.
   - Si es un idioma existente: Actualizar el JSON correspondiente con las nuevas claves detectadas.

4. **Aplicar Traducciones**:
   // turbo
   Ejecutar `python3 scripts/i18n/apply_full.py <lang> scripts/i18n/master_data/<lang>.json` para inyectar los cambios en el archivo `.ts`.

5. **Compilar y Publicar**:
   // turbo
   Ejecutar `lrelease i18n/SecInterp_<lang>.ts` para generar el binario `.qm`.

6. **Actualizar Metadatos**:
   Asegurar que `metadata.txt` refleje los cambios en la sección `changelog` y el conteo de idiomas.
