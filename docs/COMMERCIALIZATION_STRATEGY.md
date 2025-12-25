# Estrategia de Comercialización para SecInterp

## Resumen Ejecutivo
El objetivo es separar las características "Básicas" (repositorio oficial de QGIS, gratuito) de las características "Avanzadas" (de pago/donación).

**Restricción Crítica:** Todos los plugins de QGIS deben licenciarse bajo la **GNU General Public License (GPL)** porque se vinculan con las bibliotecas de QGIS.
*   **Lo que esto significa:** No se puede impedir legalmente que un usuario comparta el código si ya lo tiene.
*   **La Oportunidad:** Se puede cobrar por el *acto* de descargar el binario/zip, por servicios de datos, o por conveniencia ("Sponsorware"). También se puede solicitar una "donación" para desbloquear funciones dentro de la app (License Key).

Este documento describe tres caminos viables para lograr su objetivo.

---

## Opción 1: El Modelo "Open Core" (Dos Plugins Separados)

Crear dos versiones distintas del plugin.

*   **`sec_interp_community`**: La versión en el Repositorio Oficial de QGIS. Contiene herramientas básicas.
*   **`sec_interp_pro`**: Un plugin separado (o una versión "completa" que sobreescribe la primera). Se distribuye a través de Gumroad, Stripe o un repositorio privado.

### Pros
*   **Separación Clara**: El código de la versión "gratuita" simplemente no contiene la lógica avanzada. No se puede "desbloquear" pirateando porque el código no está ahí.
*   **Repo Limpio**: El repo oficial se mantiene puramente GPL y enfocado en la comunidad.

### Contras
*   **Sobrecarga de Mantenimiento**: Debe mantener dos bases de código o un sistema de compilación complejo para excluir archivos/directorios.
*   **Confusión del Usuario**: Los usuarios pueden instalar ambos y tener conflictos. La migración de Free a Pro requiere una reinstalación.

### Implementación Sugerida
Usar una estrategia de ramas `git`.
*   `main`: Contiene la versión Pro completa.
*   `community`: Una rama donde se eliminan físicamente los directorios avanzados (ej. `core/advanced_geostats/`).
*   **Acción**: Liberar la rama `community` al QGIS Hub. Liberar el zip de la rama `main` a los usuarios de pago.

---

## Opción 2: El Modelo "Sponsorware" (Acceso Anticipado)

Todas las funciones eventualmente son gratuitas, pero los donantes las obtienen *antes*.

*   **Repo Público**: Contiene la versión `v1.0`.
*   **Canal Privado/Sponsor**: Contiene la versión `v1.1` con nuevas funciones (ej. Exportación de Sondajes).
*   **Flujo**: Cuando termine la `v1.2` (siguientes funciones), libera la `v1.1` al público general.

### Pros
*   **Buena Voluntad de la Comunidad**: No está "reteniendo" características para siempre, solo retrasándolas.
*   **Incentiva el Apoyo Recurrente**: Los usuarios pagan para mantenerse a la vanguardia.

### Contras
*   **Feedback Retrasado**: Las pruebas masivas ocurren meses después.
*   **Presión**: Debe construir constantemente *nuevas* características para mantener felices a los patrocinadores.

---

## Opción 3: Feature Flag en la App (Llave de Licencia) **[RECOMENDADA]**

Mantener un solo plugin en el repositorio de QGIS. Incluir *todo* el código, pero deshabilitar la interfaz de usuario (UI) para características avanzadas a menos que esté presente un "Supporter Token" (Llave de Donación).

*   **Mecanismo**: Un diálogo "Configuración > Ingresar Llave de Donación".
*   **Validación**:
    *   *Simple:* Un hash o verificación estática simple.
    *   *Online:* Consultar una API de Gumroad para verificar el email/licencia.
*   **El "Honor System"**: Dado que es Python, un usuario *podría* abrir el código y comentar la línea que bloquea la función.
    *   *Por qué está bien:* El 99% de los usuarios profesionales (geólogos/ingenieros) no hackearán su código; pagarán $20-$50 para ahorrar horas de trabajo.

### Pros
*   **Cero Mantenimiento Extra**: Una base de código, una liberación.
*   **Upsell (Venta sugestiva)**: Los usuarios gratuitos *ven* los elementos del menú "Avanzado" (en gris) y recuerdan constantemente lo que se están perdiendo.
*   **Actualización Fácil**: El usuario paga -> ingresa la llave -> acceso instantáneo. Sin reinstalar.

### Contras
*   **No es "Seguro"**: No es un DRM real. Es una "cerradura en la puerta" que cualquiera con un destornillador puede quitar. (Pero esto cumple totalmente con la licencia GPL).

---

## Plan de Acción Recomendado

Recomendamos la **Opción 3 (Feature Flag / Llave)** por las siguientes razones:
1.  **Visibilidad**: Pone el botón "Donar para Pro" justo enfrente de cada usuario gratuito.
2.  **Simplicidad**: El flujo de desarrollo más simple.
3.  **Flexibilidad**: Puede decidir más tarde hacer que una función sea gratuita simplemente cambiando un flag de configuración.

### Pasos de Implementación
1.  **Definir Características "Pro"**: Identificar qué `actions` en su GUI corresponden a tareas avanzadas (ej. Exportación a GeoPackage, Vista 3D de Sondajes).
2.  **Crear un Gestor de Licencias**: Una clase simple `LicenseService` que guarde una llave en `QgsSettings`.
3.  **Actualizaciones de UI**: En `main_dialog.py` (pseudocódigo):
    ```python
    if not self.license_service.has_pro_access():
        self.action_advanced_feature.setEnabled(False)
        self.action_advanced_feature.setToolTip("Disponible en Versión Pro (Done para desbloquear)")
        # Opcional: Conectar la acción a un diálogo que abra el link de donación
    ```
4.  **Distribución**: Configurar una página de Gumroad/Ko-fi que envíe una llave al comprar.
