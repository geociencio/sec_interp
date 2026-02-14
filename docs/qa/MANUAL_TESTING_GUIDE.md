# Guía de Pruebas Manuales - SecInterp v2.11.0

## 🎯 Objetivos de la Sesión
Validar la estabilidad del plugin tras los cambios recientes y asegurar que el flujo principal de trabajo sea robusto.

## 🧪 Casos de Prueba Críticos

### 1. Flujo Básico de Sección
- [ ] **Selección de Línea**: Seleccionar una línea de sección válida y calcular perfil.
- [ ] **Generación de Sección**: Verificar que se genera la topografía correctamente.
- [ ] **Guardado**: Guardar la sección como un nuevo archivo `.shp` o en memoria.

### 2. Previsualización (Preview)
- [ ] **Renderizado**: Activar "Generar Preview" y verificar que no hay lag excesivo.
- [ ] **Capas**: Alternar visibilidad de Topografía, Geología y Sondajes.
- [ ] **Zoom/Pan**: Hacer zoom en el canvas de preview.
    - *Verificar*: El nivel de detalle (LOD) se ajusta al soltar el zoom.
- [ ] **Cierre**: Cerrar el diálogo mientras se genera un preview (Prueba de regresión del Hotfix).

### 3. Interpretación
- [ ] **Digitalización**: Dibujar una polilínea sobre la sección.
- [ ] **Atributos**: Asignar litología/código a la interpretación.
- [ ] **Edición**: Modificar vértices de una interpretación existente.

### 4. Sondajes (Drillholes)
- [ ] **Proyección**: Verificar que los sondajes se proyectan correctamente según la distancia de buffer.
- [ ] **Hats**: Verificar la visualización de "sombreros" (hats) de litología a lo largo del trazo.

## 🐛 Reporte de Errores
Si encuentras un error, por favor proporciona:
1.  **Acción**: Qué estabas haciendo (clic, drag, cierre de ventana).
2.  **Mensaje**: El error mostrado en la barra de mensajes de QGIS o en el log.
3.  **Traceback**: Si hay un crash completo, copia el stack trace (como el anterior).

---
*Generado automáticamente para la sesión de QA v2.11.0*
