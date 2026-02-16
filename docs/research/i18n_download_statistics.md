# Investigación de Descargas y Estrategia de i18n: SecInterp

## 1. Análisis de Descargas vs. Cobertura Actual

Basado en las estadísticas proporcionadas y el estado actual del plugin (v3.0.0), este es el panorama de cobertura:

| Rango | País | Descargas | Idioma Principal | Estado i18n |
| :--- | :--- | :--- | :--- | :--- |
| 1 | United States | 344 | Inglés (EN) | ✅ Soportado (Base) |
| 2 | Singapore | 82 | EN / Chino / Malayo | ✅ Soportado (EN/ZH) |
| 3 | Indonesia | 74 | Indonesio (ID) | ✅ Soportado |
| 4 | Italy | 51 | Italiano (IT) | ✅ Soportado |
| 5 | Brazil | 39 | Portugués (PT_BR) | ✅ Soportado |
| 6 | India | 38 | Hindi / EN / Otros | ❌ **No soportado (Hindi)** |
| 7 | China | 37 | Chino (ZH_CN) | ✅ Soportado |
| 8 | Australia | 32 | Inglés (EN) | ✅ Soportado |
| 9 | Mexico | 30 | Español (ES) | ✅ Soportado |
| 10 | Canada | 23 | EN / Francés (FR) | ✅ Soportado |

### Brechas Críticas Identificadas (Top 20)
*   **India (#6 - 38 descargas):** El mercado de mayor crecimiento sin soporte nativo (Hindi).
*   **Finlandia (#12 - 20 descargas):** Sorprendente volumen para su población; indica adopción institucional.
*   **Japón (#14 - 18 descargas):** Comunidad QGIS muy activa que prefiere interfaces localizadas.
*   **Polonia (#16 - 16 descargas):** Hub importante de geociencias en Europa del Este.

---

## 2. Sugerencias Estratégicas de i18n

### Prioridad A: Expansión de Idiomas (Roadmap)
1.  **Hindi (hi):** Implementar de inmediato usando la infraestructura actual (`apply_full.py`). India es un mercado estratégico para minería y geotecnia.
2.  **Japonés (ja):** La comunidad de QGIS en Japón es una de las más organizadas. La localización aquí suele aumentar drásticamente la retención.
3.  **Polaco (pl) / Finés (fi):** Consolidar el dominio en el mercado europeo.

### Prioridad B: Mejoras Técnicas
*   **Detección de Locale Inteligente:** Asegurar que el plugin no solo detecte el idioma de QGIS, sino que sugiera el idioma basado en el locale del sistema si hay una mejor coincidencia.
*   **Integración con Transifex/Crowdin:** Dado el éxito global (20+ países), mover las traducciones a una plataforma colaborativa permitiría que usuarios de países como Letonia (#18) o Marruecos (#20) contribuyan voluntariamente.
*   **Soporte RTL (Right-to-Left):** Si se planea expandir a Marruecos con Árabe, es necesario auditar la UI para layouts RTL.

### Prioridad C: Documentación y SEO Regional
*   **READMEs localizados:** Crear versiones de `README.md` en los 5 idiomas principales (EN, ES, ZH, ID, IT) para mejorar el SEO en el repositorio de plugins de QGIS.

---

## 3. Conclusión de la Investigación
SecInterp tiene una penetración balanceada: fuerte en **EE.UU./Anglosfera** (45% de descargas), pero con una tracción notable en **Sudeste Asiático** (Singapur + Indonesia = 156 descargas). La decisión de soportar `id` y `zh` fue extremadamente acertada.

**Recomendación inmediata:** Iniciar la generación de `master_data/hi.json` y `master_data/ja.json` para capturar el mercado de India y Japón en la próxima versión menor.
