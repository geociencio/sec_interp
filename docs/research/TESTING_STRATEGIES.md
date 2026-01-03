# Estrategias de Testing para Plugins QGIS

Este documento analiza las diferentes estrategias de testing disponibles para el desarrollo de plugins QGIS, sus ventajas, desventajas y casos de uso recomendados.

## 📋 Tabla de Contenidos

1. [Enfoques de Testing](#enfoques-de-testing)
2. [Ventajas y Desventajas](#ventajas-y-desventajas)
3. [Comparativa Detallada](#comparativa-detallada)
4. [Estrategia Recomendada](#estrategia-recomendada)
5. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## Enfoques de Testing

### 1. unittest Estándar (con Mocks)

**Descripción**: Tests que corren fuera de QGIS usando mocks para simular las APIs de QGIS.

**Comando**:
```bash
PYTHONPATH=.. uv run python3 -m unittest discover sec_interp/tests
```

**Características**:
- Usa `unittest.mock` para simular `qgis.core`, `qgis.gui`, `iface`
- Corre en cualquier entorno Python
- Rápido y ligero
- Ideal para CI/CD

### 2. QGIS In-Process Testing

**Descripción**: Tests que corren dentro del entorno QGIS real, con acceso completo a las APIs.

**Comando**:
```bash
# Desde QGIS Python Console
exec(open('scripts/run_tests_in_qgis.py').read())

# O headless
qgis --nologo --code scripts/run_tests_in_qgis.py
```

**Características**:
- Acceso real a `iface`, `QgsMapCanvas`, etc.
- Sin mocks, APIs reales de C++/PyQt
- Requiere QGIS instalado
- Más lento pero más realista

---

## Ventajas y Desventajas

### 🟢 unittest Estándar (con Mocks)

#### Ventajas

1. **⚡ Velocidad Extrema**
   - Tests corren en milisegundos
   - Sin overhead de inicialización de QGIS
   - Perfecto para TDD (Test-Driven Development)

2. **✅ Simplicidad de Setup**
   - Solo requiere Python y dependencias del proyecto
   - No necesita QGIS instalado
   - Funciona en cualquier máquina

3. **🔄 Excelente para CI/CD**
   - Fácil integración con GitHub Actions, GitLab CI, etc.
   - Sin necesidad de configurar servidores de display
   - Reproducible en cualquier entorno

4. **🐛 Debugging Superior**
   - Breakpoints en IDE funcionan perfectamente
   - Stack traces claros
   - Fácil de aislar problemas

5. **🎯 Aislamiento Total**
   - Cada test es completamente independiente
   - No hay estado compartido entre tests
   - Resultados determinísticos

#### Desventajas

1. **⚠️ Mocks Pueden Mentir**
   - Los mocks no siempre replican el comportamiento real
   - Bugs en las APIs reales pueden pasar desapercibidos
   - Requiere mantener los mocks actualizados

2. **❌ No Puede Testear GUI**
   - Imposible testear componentes que requieren `iface` real
   - No se pueden verificar interacciones visuales
   - Limitado para widgets y herramientas de mapa

3. **🔍 Menor Cobertura de Integración**
   - No detecta problemas de integración con QGIS
   - No valida compatibilidad entre versiones
   - Puede dar falsos positivos

---

### 🟢 QGIS In-Process Testing

#### Ventajas

1. **✅ Realismo Total**
   - Pruebas contra APIs reales de C++/PyQt
   - Detecta bugs que los mocks no revelarían
   - Validación de compatibilidad real con QGIS

2. **🎨 Testing de GUI Completo**
   - Puedes testear `QgsMapCanvas`, `iface`, widgets
   - Verificación visual de renderizado
   - Testing de herramientas interactivas

3. **🔍 Debugging Visual**
   - Ves las capas renderizándose en tiempo real
   - Puedes inspeccionar el estado de QGIS
   - Útil para troubleshooting de visualización

4. **🔗 Integración End-to-End**
   - Pruebas de workflows completos de usuario
   - Validación de interacción con otros plugins
   - Detección de problemas de integración

5. **📸 Validación Visual**
   - Posibilidad de capturar screenshots
   - Comparación visual de resultados
   - Testing de estilos y simbología

#### Desventajas

1. **🐌 Lentitud Significativa**
   - Overhead de 5-10 segundos por inicialización de QGIS
   - Tests individuales más lentos
   - No práctico para TDD rápido

2. **⚙️ Setup Complejo**
   - Requiere QGIS instalado (no solo librerías Python)
   - En CI/CD necesita Xvfb (Linux) o configuración especial
   - Más difícil de automatizar

3. **🔀 Menor Aislamiento**
   - Estado compartido de QGIS entre tests
   - Tests pueden interferir entre sí
   - Resultados menos determinísticos

4. **🐛 Debugging Limitado**
   - No puedes usar breakpoints de IDE normalmente
   - Debugging principalmente con `print()`
   - Stack traces menos claros

5. **💻 No Portable**
   - Depende de la versión de QGIS instalada
   - Puede fallar por configuraciones locales
   - Requiere más recursos (RAM, CPU)

6. **🔧 Mantenimiento Adicional**
   - Necesita mantener scripts de ejecución
   - Configuración diferente por plataforma
   - Más puntos de fallo

---

## Comparativa Detallada

| Criterio | unittest Estándar | QGIS In-Process | Ganador |
|----------|-------------------|-----------------|---------|
| **Velocidad de Ejecución** | ⚡ <100ms por test | 🐌 5-10s overhead + test | unittest |
| **Setup Inicial** | ✅ `pip install` | ⚠️ Instalar QGIS completo | unittest |
| **Integración CI/CD** | ✅ Trivial | ⚠️ Requiere config especial | unittest |
| **Debugging** | ✅ IDE breakpoints | ⚠️ Print debugging | unittest |
| **Realismo de APIs** | ⚠️ Mocks | ✅ APIs reales | QGIS |
| **Testing de GUI** | ❌ Imposible | ✅ Completo | QGIS |
| **Aislamiento** | ✅ Total | ⚠️ Estado compartido | unittest |
| **TDD Workflow** | ✅ Excelente | ❌ Demasiado lento | unittest |
| **Detección de Bugs** | ⚠️ Solo lógica | ✅ Integración + GUI | QGIS |
| **Portabilidad** | ✅ Cualquier máquina | ⚠️ Depende de QGIS | unittest |
| **Recursos** | ✅ Mínimos | ⚠️ Alto (RAM/CPU) | unittest |
| **Mantenimiento** | ✅ Simple | ⚠️ Complejo | unittest |

**Puntuación Total**: unittest (9) vs QGIS In-Process (3)

---

## Estrategia Recomendada

### 🎯 Regla 90/10

Para el proyecto `sec_interp`, la estrategia óptima es:

#### 90% unittest Estándar (con Mocks)

**Usar para**:
- ✅ Tests de lógica de negocio (`core/services/`)
- ✅ Tests de utilidades (`core/utils/`)
- ✅ Tests de tipos y validaciones
- ✅ Tests de algoritmos
- ✅ Desarrollo iterativo rápido (TDD)
- ✅ CI/CD pipelines

**Ejemplo**:
```python
# tests/core/services/test_geology_service.py
def test_generate_geological_profile_returns_segments(self):
    service = GeologyService()
    segments = service.generate_geological_profile(
        line_lyr=mock_line,
        raster_lyr=mock_raster,
        outcrop_lyr=mock_outcrop,
        outcrop_name_field="unit"
    )
    self.assertGreater(len(segments), 0)
```

#### 10% QGIS In-Process

**Usar para**:
- ✅ Tests de componentes GUI críticos
- ✅ Validación de herramientas de dibujo (`InterpretationTool`)
- ✅ Tests de renderizado de preview
- ✅ Smoke tests antes de releases
- ✅ Validación de compatibilidad con versiones de QGIS

**Ejemplo**:
```python
# tests/gui/test_interpretation_tool_integration.py
# (Correr en QGIS Console)
def test_interpretation_tool_creates_polygon_on_canvas(self):
    tool = InterpretationTool(iface.mapCanvas())
    tool.activate()
    # Simular clicks en el canvas
    tool.canvasReleaseEvent(mock_event)
    # Verificar que se creó el polígono
    self.assertEqual(len(tool.current_polygon.vertices), 3)
```

---

## Ejemplos Prácticos

### Caso 1: Testing de Servicio de Geología

**Enfoque**: unittest estándar ✅

**Razón**: Lógica pura, sin dependencias de GUI, rápido para TDD.

```python
# tests/core/services/test_geology_service.py
class TestGeologyService(unittest.TestCase):
    def setUp(self):
        self.service = GeologyService()
        self.mock_line = MagicMock()
        self.mock_raster = MagicMock()

    def test_calculates_segments_correctly(self):
        result = self.service.generate_geological_profile(...)
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(s, GeologySegment) for s in result))
```

**Ventajas en este caso**:
- Corre en <50ms
- Fácil de debuggear
- Perfecto para TDD
- Funciona en CI/CD

---

### Caso 2: Testing de Herramienta de Interpretación

**Enfoque**: QGIS In-Process ✅

**Razón**: Requiere `iface`, `QgsMapCanvas`, interacción con el mapa.

```python
# tests/gui/test_interpretation_tool.py
# (Ejecutar con scripts/run_tests_in_qgis.py)
class TestInterpretationTool(unittest.TestCase):
    def setUp(self):
        self.canvas = iface.mapCanvas()
        self.tool = InterpretationTool(self.canvas)

    def test_tool_draws_polygon_on_canvas(self):
        self.tool.activate()
        # Simular clicks
        self.tool.canvasReleaseEvent(create_mock_event(100, 100))
        self.tool.canvasReleaseEvent(create_mock_event(200, 100))
        self.tool.canvasReleaseEvent(create_mock_event(150, 200))

        # Verificar que se dibujó
        self.assertIsNotNone(self.tool.rubber_band)
        self.assertEqual(self.tool.rubber_band.numberOfVertices(), 3)
```

**Ventajas en este caso**:
- Prueba la interacción real con el canvas
- Detecta bugs de renderizado
- Valida comportamiento de eventos de mouse

---

### Caso 3: Testing de Preview Renderer

**Enfoque Híbrido**: Ambos ✅

**unittest para lógica**:
```python
def test_renderer_calculates_extent_correctly(self):
    renderer = PreviewRenderer()
    layers = [mock_layer1, mock_layer2]
    extent = renderer._calculate_extent(layers)
    self.assertIsInstance(extent, QgsRectangle)
```

**QGIS In-Process para renderizado**:
```python
def test_renderer_displays_layers_on_canvas(self):
    renderer = PreviewRenderer(iface.mapCanvas())
    canvas, layers = renderer.render(topo_data, geol_data)
    # Verificar que las capas están en el canvas
    self.assertEqual(len(iface.mapCanvas().layers()), len(layers))
```

---

## 📊 Métricas de Éxito

### Para unittest Estándar
- ✅ Suite completa corre en <10 segundos
- ✅ >80% cobertura de código
- ✅ 0 fallos en CI/CD
- ✅ Tests corren en cualquier máquina

### Para QGIS In-Process
- ✅ Smoke tests pasan antes de cada release
- ✅ GUI crítica validada manualmente
- ✅ Compatibilidad verificada en QGIS LTR
- ✅ Screenshots de regresión visual

---

## 🎓 Conclusión

**El testing en QGIS es una herramienta complementaria, no un reemplazo del unittest estándar.**

- **Usa unittest estándar** como tu estrategia principal (90% de tests)
- **Usa QGIS in-process** estratégicamente para validación crítica (10% de tests)
- **Combina ambos** para máxima cobertura y confianza

**Recuerda**: Un test rápido que corre siempre es mejor que un test perfecto que nadie ejecuta.

---

**Referencias**:
- [TESTING_IN_QGIS.md](TESTING_IN_QGIS.md) - Guía de ejecución
- [.agent/workflows/run-tests.md](../../.agent/workflows/run-tests.md) - Workflow unittest
- [.agent/workflows/run-tests-in-qgis.md](../../.agent/workflows/run-tests-in-qgis.md) - Workflow QGIS
