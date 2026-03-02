---
description: Perform a full or partial plugin audit using qgis-plugin-analyzer v1.9.0+.
agent: Auditor
skills: [project-context, coding-standards, i18n-standards]
---

Este workflow ejecuta una serie de verificaciones estáticas especializadas para asegurar la calidad, seguridad y rendimiento del plugin.

### Pasos

1. **Análisis de Seguridad (Bandit & Secret Scan)**
   Escanea el código en busca de vulnerabilidades conocidas y secretos hardcodeados.
   ```bash
   uv run qgis-analyzer analyze security .
   ```

2. **Auditoría de Internacionalización (i18n)**
   Detecta cadenas de texto de usuario que no están envueltas en `self.tr()` o `QCoreApplication.translate()`.
   ```bash
   uv run qgis-analyzer analyze i18n .
   ```

3. **Análisis de Rendimiento (Performance)**
   Identifica bloqueos potenciales de la UI, bucles costosos y fugas de señales (Signal Leaks).
   ```bash
   uv run qgis-analyzer analyze performance .
   ```

4. **Verificación de Arquitectura (Opcional)**
   Analiza las dependencias entre módulos y el uso de la API de QGIS.
   ```bash
   uv run qgis-analyzer analyze architecture .
   ```

5. **Generación de Reporte (Opcional)**
   Genera un reporte HTML consolidado si se requieren detalles profundos.
   ```bash
   uv run qgis-analyzer analyze . --report
   ```
