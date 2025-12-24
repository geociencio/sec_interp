# Mejoramiento de Herramienta de Medición Multi-Punto

## Objetivo
Mejorar la herramienta de medición para permitir medir afloramientos siguiendo la traza a lo largo del perfil mediante clics sucesivos, finalizando con doble clic.

## Tareas

### Planificación
- [x] Analizar la implementación actual de `ProfileMeasureTool`
- [x] Diseñar la arquitectura para medición multi-punto
- [x] Crear plan de implementación detallado
- [x] Definir plan de verificación

### Implementación
- [x] Modificar `ProfileMeasureTool` para soportar múltiples puntos
- [x] Implementar detección de doble clic
- [x] Actualizar lógica de rubber band para polilíneas
- [x] Calcular distancia acumulada a lo largo de la traza
- [x] Actualizar señales para emitir mediciones multi-segmento

### Integrate with UI <!-- id: 4 -->
- [x] Update `main_dialog.py` to handle multi-point metrics <!-- id: 5 -->
- [x] Format results display (Total distance, Horiz. dist, Elev. change, Slope, Points count) <!-- id: 6 -->
- [x] Add "Finalizar" button to UI <!-- id: 8 -->
- [x] Connect button signal to tool <!-- id: 9 -->

### Verification <!-- id: 7 -->
- [x] Test multi-point measurement flow <!-- id: 10 -->
- [x] Verify metric calculations <!-- id: 11 -->
- [x] Verify finalization logic (button and state management) <!-- id: 12 -->
- [x] Probar medición con múltiples puntos (3+)
- [x] Verificar detección de doble clic
- [x] Verificar cálculo de distancias acumuladas
- [x] Verificar snapping en todos los puntos
- [x] Crear walkthrough con capturas de pantalla
