---
name: qgis-migration-4x
description: Expert guide for QGIS 4.x migration and agnostic API usage
---

# Skill: QGIS Migration & Future-Proofing (4.x)

Esta skill proporciona las directrices técnicas para preparar el código de SecInterp para la próxima versión mayor de QGIS (4.x), enfocándose en la eliminación de deuda técnica relacionada con cambios de API y dependencias de Qt.

## 1. Principio "API Agnostic"

El código debe ser agnóstico de la versión subyacente de Qt (Qt5 vs Qt6) siempre que sea posible. QGIS proporciona proxies para esto.

### Regla de Oro: Imports de Qt
❌ **PROHIBIDO**: Importar directamente de `PyQt5` o `PyQt6`.
✅ **OBLIGATORIO**: Importar desde `qgis.PyQt`.

**Ejemplo Incorrecto**:
```python
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
```

**Ejemplo Correcto**:
```python
from qgis.PyQt.QtCore import pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QWidget
```

Esto asegura que cuando QGIS migre a Qt6, el código funcionará sin cambios (siempre que QGIS mantenga el shim).

## 2. Cambios de API Detectados (v3 -> v4)

### 2.1. QgsProject
*   Evitar `QgsProject.instance()` en loops cerrados o métodos estáticos si es posible pasar la instancia explícitamente. Implementar inyección de dependencias.

### 2.2. Procesamiento en Segundo Plano
*   Cualquier cálculo que tome > 100ms debe usar `QgsTask`.
*   La UI nunca debe bloquearse.
*   Uso estricto de `QgsTask.fromFunction` o subclases de `QgsTask` con señales `finished`.

## 3. Estrategia de Refactorización

### Fase 1: Limpieza de Imports (Inmediato)
Ejecutar scripts o refactorizaciones manuales para normalizar todos los imports de `PyQt`.

### Fase 2: Eliminación de Deprecados (Continuo)
Monitorear los warnings de deprecación en la consola de QGIS y actuar inmediatamente.
*   Configurar `pytest` para fallar ante `DeprecationWarning` de módulos `qgis.*`.

### Fase 3: Recursos (resources.py)
Recompilar `resources.qrc` usando herramientas que soporten la abstracción de Qt, o asegurar que el compilador (`pyrcc5`) sea compatible con el entorno de ejecución.

## 4. Checklist de Migración

- [ ] Todos los imports de Qt provienen de `qgis.PyQt`.
- [ ] No hay uso de métodos marcados como `@deprecated` en la documentación de QGIS 3.34+.
- [ ] Los tests de integración corren sin emitir `DeprecationWarning`.
- [ ] La UI es responsive y no bloquea el hilo principal.
