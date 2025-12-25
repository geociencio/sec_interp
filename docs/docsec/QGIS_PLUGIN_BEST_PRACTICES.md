# Mejores Prácticas para el Desarrollo de Plugins de QGIS

**Última actualización:** Diciembre 2024
**Versión de QGIS:** 3.0+
**Lenguaje:** Python 3.6+

---

## 📋 Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Arquitectura y Diseño](#arquitectura-y-diseño)
3. [Calidad del Código](#calidad-del-código)
4. [Gestión de Dependencias](#gestión-de-dependencias)
5. [Interfaz de Usuario](#interfaz-de-usuario)
6. [Testing y Validación](#testing-y-validación)
7. [Optimización de Rendimiento](#optimización-de-rendimiento)
8. [Documentación](#documentación)
9. [Publicación y Distribución](#publicación-y-distribución)
10. [Herramientas de Desarrollo](#herramientas-de-desarrollo)

---

## 1. Estructura del Proyecto

### 📁 Archivos Obligatorios

Todo plugin de QGIS debe incluir como mínimo:

```
mi_plugin/
├── __init__.py           # Punto de entrada del plugin
├── metadata.txt          # Metadatos del plugin
├── LICENSE              # Archivo de licencia (obligatorio desde junio 2024)
└── main_plugin.py       # Lógica principal del plugin
```

### 📁 Estructura Recomendada

Para proyectos más complejos:

```
mi_plugin/
├── __init__.py
├── metadata.txt
├── LICENSE
├── README.md
├── requirements.txt
├── requirements-dev.txt
│
├── core/                # Lógica de negocio
│   ├── __init__.py
│   ├── algorithms.py
│   └── utils.py
│
├── gui/                 # Interfaz de usuario
│   ├── __init__.py
│   ├── dialogs.py
│   └── widgets.py
│
├── processing/          # Algoritmos de Processing Framework
│   ├── __init__.py
│   └── my_algorithm.py
│
├── resources/           # Recursos (iconos, UI, etc.)
│   ├── icons/
│   ├── ui/
│   └── resources.qrc
│
├── i18n/               # Archivos de traducción
│   ├── plugin_es.ts
│   └── plugin_es.qm
│
├── tests/              # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_algorithms.py
│   └── test_integration.py
│
└── docs/               # Documentación
    └── user_guide.md
```

### 🔑 Archivos Clave

#### `__init__.py`

```python
def classFactory(iface):
    """
    Función obligatoria llamada por QGIS para crear la instancia del plugin.

    Args:
        iface: Interfaz de QGIS (QgisInterface)

    Returns:
        Instancia del plugin
    """
    from .main_plugin import MyPlugin
    return MyPlugin(iface)
```

#### `metadata.txt`

```ini
[general]
name=Mi Plugin
qgisMinimumVersion=3.0
description=Descripción breve del plugin
version=0.1.0
author=Tu Nombre
email=tu@email.com

about=Descripción detallada del plugin y sus funcionalidades

tracker=https://github.com/usuario/plugin/issues
repository=https://github.com/usuario/plugin
homepage=https://github.com/usuario/plugin

# Tags separados por comas
tags=geology,analysis,vector

# Categoría del plugin
category=Vector

# Icono del plugin (ruta relativa)
icon=resources/icons/icon.png

# Experimental o estable
experimental=True

# Deprecado (opcional)
deprecated=False

# Soporte para Qt6
hasProcessingProvider=no
server=False
```

---

## 2. Arquitectura y Diseño

### 🏗️ Principios de Diseño

#### Separación de Responsabilidades

**✅ HACER:**
```python
# Separar lógica de UI
class MyAlgorithm:
    """Lógica pura sin dependencias de UI"""
    def process_data(self, input_layer, parameters):
        # Procesamiento de datos
        return result

class MyDialog(QDialog):
    """UI que usa la lógica"""
    def __init__(self):
        super().__init__()
        self.algorithm = MyAlgorithm()

    def run(self):
        result = self.algorithm.process_data(self.layer, self.params)
        self.display_result(result)
```

**❌ EVITAR:**
```python
# Mezclar lógica con UI
class MyDialog(QDialog):
    def run(self):
        # Procesamiento mezclado con UI
        for feature in layer.getFeatures():
            # ... procesamiento complejo ...
            self.progress_bar.setValue(i)  # UI mezclada
```

#### Patrón MVC/MVP

Implementar separación entre:
- **Model:** Lógica de datos y procesamiento
- **View:** Interfaz de usuario (Qt widgets)
- **Controller/Presenter:** Coordinación entre Model y View

### 🔌 Uso del Processing Framework

Para algoritmos que pueden ejecutarse en batch o desde la consola:

```python
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink
)

class MyProcessingAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    BUFFER_DISTANCE = 'BUFFER_DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        """Define inputs y outputs"""
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                'Input layer',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BUFFER_DISTANCE,
                'Buffer distance',
                QgsProcessingParameterNumber.Double,
                defaultValue=10.0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Output layer'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Ejecuta el algoritmo"""
        # Obtener parámetros
        source = self.parameterAsSource(parameters, self.INPUT, context)
        distance = self.parameterAsDouble(parameters, self.BUFFER_DISTANCE, context)

        # Crear sink para output
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            source.fields(), source.wkbType(), source.sourceCrs()
        )

        # Procesar features
        total = source.featureCount()
        for current, feature in enumerate(source.getFeatures()):
            # Verificar cancelación
            if feedback.isCanceled():
                break

            # Procesar feature
            buffered = feature.geometry().buffer(distance, 5)
            feature.setGeometry(buffered)
            sink.addFeature(feature)

            # Actualizar progreso
            feedback.setProgress(int(current * 100 / total))

        return {self.OUTPUT: dest_id}

    def name(self):
        return 'mybuffer'

    def displayName(self):
        return 'My Buffer Algorithm'

    def group(self):
        return 'Vector tools'

    def groupId(self):
        return 'vectortools'

    def createInstance(self):
        return MyProcessingAlgorithm()
```

**Ventajas del Processing Framework:**
- ✅ Ejecución en batch automática
- ✅ Integración con Model Builder
- ✅ Soporte para multithreading
- ✅ Validación automática de inputs
- ✅ Interfaz gráfica generada automáticamente

---

## 3. Calidad del Código

### 📏 Estándares de Código

#### PEP 8 Compliance

Usar herramientas de linting:

```bash
# Verificar estilo
pycodestyle mi_plugin/

# Formatear código automáticamente
black mi_plugin/

# Análisis estático
pylint mi_plugin/

# Verificación completa
flake8 mi_plugin/
```

#### Configuración de `.pylintrc`

```ini
[MASTER]
ignore=CVS,.git,__pycache__

[MESSAGES CONTROL]
disable=C0111,  # missing-docstring
        R0903,  # too-few-public-methods
        R0913   # too-many-arguments

[FORMAT]
max-line-length=100
indent-string='    '

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
```

### 📝 Convenciones de Nombres

```python
# Módulos y paquetes: lowercase_with_underscores
import my_module

# Clases: CapitalizedWords
class MyPluginDialog:
    pass

# Funciones y métodos: lowercase_with_underscores
def calculate_distance():
    pass

# Constantes: UPPERCASE_WITH_UNDERSCORES
MAX_BUFFER_DISTANCE = 1000.0

# Variables privadas: _leading_underscore
class MyClass:
    def __init__(self):
        self._private_var = None
```

### 🧹 Refactorización

**Reglas:**
- Métodos/funciones no deben exceder una pantalla (~50 líneas)
- Evitar duplicación de código (DRY - Don't Repeat Yourself)
- Extraer lógica compleja a funciones auxiliares
- Usar comprehensions cuando sea apropiado

**Ejemplo de refactorización:**

```python
# ❌ ANTES: Código repetitivo
def process_points(layer):
    features = []
    for feature in layer.getFeatures():
        if feature.geometry().type() == QgsWkbTypes.PointGeometry:
            if feature['value'] > 100:
                features.append(feature)
    return features

def process_lines(layer):
    features = []
    for feature in layer.getFeatures():
        if feature.geometry().type() == QgsWkbTypes.LineGeometry:
            if feature['value'] > 100:
                features.append(feature)
    return features

# ✅ DESPUÉS: Refactorizado
def filter_features_by_geometry_and_value(layer, geom_type, min_value):
    """
    Filtra features por tipo de geometría y valor mínimo.

    Args:
        layer: QgsVectorLayer a filtrar
        geom_type: Tipo de geometría (QgsWkbTypes)
        min_value: Valor mínimo del campo 'value'

    Returns:
        Lista de features que cumplen los criterios
    """
    return [
        feature for feature in layer.getFeatures()
        if feature.geometry().type() == geom_type
        and feature['value'] > min_value
    ]

# Uso
points = filter_features_by_geometry_and_value(
    layer, QgsWkbTypes.PointGeometry, 100
)
lines = filter_features_by_geometry_and_value(
    layer, QgsWkbTypes.LineGeometry, 100
)
```

---

## 4. Gestión de Dependencias

### 📦 Dependencias Externas

#### Estrategias para Manejar Dependencias

1. **Bibliotecas Incluidas en QGIS:**
   - Preferir usar bibliotecas ya disponibles en QGIS
   - Ejemplos: numpy, scipy, matplotlib, pandas

2. **Bibliotecas Puras Python:**
   - Pueden incluirse mediante vendoring (copiar al plugin)
   - Cuidado con conflictos de versiones

3. **Bibliotecas con Compilación:**
   - Solicitar instalación manual al usuario
   - Documentar claramente en README

#### `requirements.txt`

```txt
# Dependencias core (ya en QGIS)
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.3.0

# Dependencias específicas del plugin
# (incluir solo si no están en QGIS)
python-slugify>=8.0.0
```

#### `requirements-dev.txt`

```txt
-r requirements.txt

# Herramientas de desarrollo
black>=23.0.0
pylint>=2.15.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-qgis>=2.0.0
```

### 🔒 Gestión de Versiones

Usar versionado semántico (SemVer):

```
MAJOR.MINOR.PATCH

1.0.0 - Primera versión estable
1.1.0 - Nueva funcionalidad (compatible)
1.1.1 - Corrección de bugs
2.0.0 - Cambios incompatibles
```

---

## 5. Interfaz de Usuario

### 🎨 Diseño de UI

#### Opciones para Crear UI

1. **Qt Designer (.ui files):**
   ```bash
   # Compilar archivos .ui a Python
   pyuic5 -o ui_dialog.py dialog.ui
   ```

2. **Programática (Recomendado para plugins simples):**
   ```python
   class MyDialog(QDialog):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.setup_ui()

       def setup_ui(self):
           layout = QVBoxLayout()

           # Widgets
           self.layer_combo = QgsMapLayerComboBox()
           self.layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)

           self.buffer_spin = QDoubleSpinBox()
           self.buffer_spin.setRange(0.0, 1000.0)
           self.buffer_spin.setValue(10.0)

           # Agregar a layout
           layout.addWidget(QLabel("Select Layer:"))
           layout.addWidget(self.layer_combo)
           layout.addWidget(QLabel("Buffer Distance:"))
           layout.addWidget(self.buffer_spin)

           self.setLayout(layout)
   ```

#### Widgets Personalizados de QGIS

Usar widgets nativos de QGIS para mejor integración:

```python
from qgis.gui import (
    QgsMapLayerComboBox,
    QgsFieldComboBox,
    QgsFileWidget,
    QgsProjectionSelectionWidget,
    QgsColorButton,
    QgsExtentGroupBox
)

# Selector de capas con filtros
layer_combo = QgsMapLayerComboBox()
layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)

# Selector de campos
field_combo = QgsFieldComboBox()
field_combo.setLayer(selected_layer)
field_combo.setFilters(QgsFieldProxyModel.Numeric)

# Selector de archivos/directorios
file_widget = QgsFileWidget()
file_widget.setStorageMode(QgsFileWidget.SaveFile)
file_widget.setFilter("Shapefiles (*.shp)")

# Selector de CRS
crs_selector = QgsProjectionSelectionWidget()
crs_selector.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
```

### 🎯 Guías de Interfaz Humana (HIG)

**Principios:**
- Agrupar elementos relacionados
- Usar capitalización apropiada en etiquetas
- Evitar group boxes con un solo widget
- Proporcionar tooltips descriptivos
- Usar layouts responsivos (grid, form)

```python
# ✅ Buena práctica
group_box = QGroupBox("Processing Options")
layout = QFormLayout()
layout.addRow("Input Layer:", self.layer_combo)
layout.addRow("Buffer Distance:", self.buffer_spin)
layout.addRow("Output File:", self.file_widget)
group_box.setLayout(layout)

# Tooltips descriptivos
self.buffer_spin.setToolTip(
    "Distance in layer units to buffer features"
)
```

---

## 6. Testing y Validación

### 🧪 Estrategia de Testing

#### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures de pytest
├── test_algorithms.py       # Tests unitarios
├── test_integration.py      # Tests de integración
└── test_ui.py              # Tests de UI
```

#### Tests Unitarios

```python
import pytest
from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY

from my_plugin.core.algorithms import calculate_buffer

class TestBufferAlgorithm:
    """Tests para el algoritmo de buffer"""

    @pytest.fixture
    def point_layer(self):
        """Crea una capa de puntos para testing"""
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "test", "memory")
        provider = layer.dataProvider()

        # Agregar features
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(0, 0)))
        provider.addFeatures([feature])

        return layer

    def test_buffer_distance(self, point_layer):
        """Verifica que el buffer tenga la distancia correcta"""
        result = calculate_buffer(point_layer, distance=10.0)

        assert result is not None
        assert result.featureCount() == 1

        # Verificar área del buffer (aproximadamente π * r²)
        feature = next(result.getFeatures())
        area = feature.geometry().area()
        expected_area = 3.14159 * (10.0 ** 2)

        assert abs(area - expected_area) < 1.0  # Tolerancia

    def test_buffer_empty_layer(self):
        """Verifica manejo de capa vacía"""
        empty_layer = QgsVectorLayer("Point?crs=EPSG:4326", "empty", "memory")
        result = calculate_buffer(empty_layer, distance=10.0)

        assert result.featureCount() == 0

    def test_buffer_invalid_distance(self, point_layer):
        """Verifica validación de distancia negativa"""
        with pytest.raises(ValueError):
            calculate_buffer(point_layer, distance=-10.0)
```

#### Tests de Integración con QGIS

```python
import pytest
from qgis.core import QgsApplication
from qgis.testing import start_app

# Iniciar aplicación QGIS para tests
@pytest.fixture(scope='session')
def qgis_app():
    """Inicia QGIS para tests de integración"""
    app = start_app()
    yield app
    app.exitQgis()

def test_plugin_loads(qgis_app):
    """Verifica que el plugin se carga correctamente"""
    from my_plugin import classFactory

    plugin = classFactory(qgis_app.iface)
    assert plugin is not None

    plugin.initGui()
    # Verificar que se agregaron acciones
    assert len(plugin.actions) > 0

    plugin.unload()
```

#### Configuración de pytest

`conftest.py`:
```python
import pytest
import sys
from pathlib import Path

# Agregar directorio del plugin al path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

@pytest.fixture(scope='session')
def qgis_iface():
    """Mock de QgisInterface para tests"""
    from qgis.testing.mocked import get_iface
    return get_iface()
```

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=my_plugin
    --cov-report=html
    --cov-report=term
```

### 🔍 Continuous Integration

`.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install QGIS
      run: |
        sudo apt-get update
        sudo apt-get install -y qgis python3-qgis

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest tests/

    - name: Run linting
      run: |
        pylint my_plugin/
        black --check my_plugin/
```

---

## 7. Optimización de Rendimiento

### ⚡ Optimización de Consultas de Features

#### Solicitar Solo Datos Necesarios

```python
# ❌ EVITAR: Cargar todo
for feature in layer.getFeatures():
    # Carga todos los atributos y geometría
    process(feature)

# ✅ MEJOR: Sin geometría si no se necesita
request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
for feature in layer.getFeatures(request):
    process(feature)

# ✅ MEJOR: Solo atributos específicos
request = QgsFeatureRequest()
request.setSubsetOfAttributes(['name', 'value'], layer.fields())
for feature in layer.getFeatures(request):
    process(feature)

# ✅ MEJOR: Filtrar en la fuente
request = QgsFeatureRequest()
request.setFilterExpression('"value" > 100')
for feature in layer.getFeatures(request):
    process(feature)
```

### 🗺️ Uso de Índices Espaciales

```python
from qgis.core import QgsSpatialIndex

# Crear índice espacial
index = QgsSpatialIndex(layer.getFeatures())

# Búsqueda rápida por bounding box
bbox = QgsRectangle(0, 0, 100, 100)
candidate_ids = index.intersects(bbox)

# Obtener features candidatos
for fid in candidate_ids:
    feature = layer.getFeature(fid)
    # Verificación precisa
    if feature.geometry().intersects(search_geometry):
        process(feature)
```

### 💾 Operaciones en Batch

```python
# ❌ EVITAR: Ediciones individuales
layer.startEditing()
for feature in layer.getFeatures():
    feature['new_field'] = calculate_value(feature)
    layer.updateFeature(feature)
layer.commitChanges()

# ✅ MEJOR: Usar provider para batch updates
layer.startEditing()
provider = layer.dataProvider()

# Preparar cambios
attr_map = {}
for feature in layer.getFeatures():
    attr_map[feature.id()] = {
        field_index: calculate_value(feature)
    }

# Aplicar todos los cambios de una vez
provider.changeAttributeValues(attr_map)
layer.commitChanges()
```

### 🧵 Thread Safety

```python
class MyAlgorithm(QgsProcessingAlgorithm):

    def flags(self):
        """
        Deshabilitar threading si hay problemas de thread-safety
        """
        # Por defecto, los algoritmos corren en thread separado
        # Si hay crashes, deshabilitar threading:
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
```

### 💡 Capas en Memoria para Resultados Intermedios

```python
# Crear capa en memoria para resultados temporales
temp_layer = QgsVectorLayer(
    "Point?crs=EPSG:4326&field=id:integer&field=value:double",
    "temp_results",
    "memory"
)

# Procesar y agregar features
provider = temp_layer.dataProvider()
features = []
for i in range(1000):
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
    feature.setAttributes([i, i * 2.0])
    features.append(feature)

# Agregar en batch
provider.addFeatures(features)
temp_layer.updateExtents()
```

---

## 8. Documentación

### 📚 Documentación del Código

#### Docstrings Estilo Google

```python
def calculate_azimuth(point1, point2):
    """
    Calcula el azimut entre dos puntos.

    El azimut se calcula como el ángulo desde el norte (0°) en sentido
    horario hasta la línea que conecta los dos puntos.

    Args:
        point1 (QgsPointXY): Punto de inicio
        point2 (QgsPointXY): Punto final

    Returns:
        float: Azimut en grados (0-360)

    Raises:
        ValueError: Si los puntos son idénticos

    Example:
        >>> p1 = QgsPointXY(0, 0)
        >>> p2 = QgsPointXY(1, 1)
        >>> azimuth = calculate_azimuth(p1, p2)
        >>> print(f"Azimuth: {azimuth:.2f}°")
        Azimuth: 45.00°

    Note:
        Los puntos deben estar en el mismo sistema de coordenadas.
    """
    if point1 == point2:
        raise ValueError("Points must be different")

    dx = point2.x() - point1.x()
    dy = point2.y() - point1.y()

    azimuth = math.degrees(math.atan2(dx, dy))
    return (azimuth + 360) % 360
```

### 📖 README.md

Estructura recomendada:

```markdown
# Nombre del Plugin

Breve descripción de una línea.

## Descripción

Descripción detallada de las funcionalidades del plugin.

## Características

- Feature 1
- Feature 2
- Feature 3

## Instalación

### Desde el Repositorio Oficial de QGIS

1. Abrir QGIS
2. Ir a Plugins > Manage and Install Plugins
3. Buscar "Nombre del Plugin"
4. Hacer clic en "Install"

### Instalación Manual

1. Descargar el plugin
2. Extraer a la carpeta de plugins de QGIS
3. Reiniciar QGIS

## Uso

### Ejemplo Básico

1. Paso 1
2. Paso 2
3. Paso 3

### Ejemplo Avanzado

Descripción de uso avanzado con capturas de pantalla.

## Requisitos

- QGIS 3.0 o superior
- Python 3.6+
- Dependencias adicionales (si aplica)

## Desarrollo

### Configuración del Entorno

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements-dev.txt
```

### Ejecutar Tests

```bash
pytest tests/
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## Licencia

GPL v2 o posterior

## Autor

Nombre del Autor
- Email: email@example.com
- GitHub: @usuario

## Agradecimientos

- Persona/Proyecto 1
- Persona/Proyecto 2
```

### 📝 Documentación de Usuario

Crear guías de usuario en `docs/`:

```
docs/
├── user_guide.md
├── tutorials/
│   ├── basic_workflow.md
│   └── advanced_features.md
├── api/
│   └── api_reference.md
└── images/
    ├── screenshot1.png
    └── screenshot2.png
```

---

## 9. Publicación y Distribución

### 📤 Requisitos para Publicación

#### Archivos Obligatorios

1. **LICENSE** (texto plano, sin extensión)
2. **metadata.txt** completo y válido
3. **README.md** o documentación equivalente

#### Validación de metadata.txt

```bash
# Verificar que todos los campos obligatorios estén presentes
grep -E "^(name|description|version|qgisMinimumVersion|author|email)=" metadata.txt
```

#### Preparar para Publicación

```bash
# Limpiar archivos innecesarios
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Crear archivo zip
zip -r mi_plugin.zip mi_plugin/ \
    -x "*.git*" \
    -x "*__pycache__*" \
    -x "*.pyc" \
    -x "*/.venv/*" \
    -x "*/tests/*"
```

### 🚀 Publicar en el Repositorio Oficial

1. **Obtener OSGEO ID:**
   - Registrarse en https://www.osgeo.org/community/getting-started-osgeo/osgeo_userid/

2. **Subir Plugin:**
   - Ir a https://plugins.qgis.org/
   - Login con OSGEO ID
   - Upload plugin ZIP

3. **Completar Información:**
   - Descripción detallada
   - Tags apropiados
   - Enlaces a repositorio y tracker
   - Capturas de pantalla

### 📋 Checklist Pre-Publicación

- [ ] Todos los tests pasan
- [ ] Código pasa linting (pylint, black, flake8)
- [ ] Documentación actualizada
- [ ] README.md completo
- [ ] LICENSE incluido
- [ ] metadata.txt válido y completo
- [ ] Versión actualizada en metadata.txt
- [ ] CHANGELOG.md actualizado
- [ ] Screenshots actualizados
- [ ] Plugin probado en QGIS limpio
- [ ] Dependencias documentadas
- [ ] Links en metadata.txt funcionan

---

## 10. Herramientas de Desarrollo

### 🛠️ Herramientas Esenciales

#### Plugin Builder

Genera estructura inicial del plugin:

```bash
# Instalar desde QGIS Plugin Manager
# Plugins > Manage and Install Plugins > Search "Plugin Builder"
```

#### Plugin Reloader

Recarga plugin sin reiniciar QGIS:

```bash
# Instalar desde QGIS Plugin Manager
# Muy útil durante desarrollo
```

#### pb_tool

Herramienta CLI para gestión de plugins:

```bash
# Instalar
pip install pb_tool

# Inicializar
pb_tool create

# Compilar recursos
pb_tool compile

# Desplegar a QGIS
pb_tool deploy

# Crear ZIP
pb_tool zip
```

### 🔧 Makefile

Ejemplo de `Makefile` para automatización:

```makefile
PLUGINNAME = mi_plugin
PY_FILES = $(wildcard *.py) $(wildcard core/*.py) $(wildcard gui/*.py)
UI_FILES = $(wildcard resources/ui/*.ui)
RESOURCE_FILES = $(wildcard resources/*.qrc)

COMPILED_UI_FILES = $(patsubst resources/ui/%.ui, ui_%.py, $(UI_FILES))
COMPILED_RESOURCE_FILES = $(patsubst resources/%.qrc, %_rc.py, $(RESOURCE_FILES))

.PHONY: all clean deploy test lint format

all: compile

compile: $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

ui_%.py: resources/ui/%.ui
	pyuic5 -o $@ $<

%_rc.py: resources/%.qrc
	pyrcc5 -o $@ $<

deploy: compile
	mkdir -p $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
	cp -r * $(HOME)/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)/
	@echo "Plugin deployed to QGIS"

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -f $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)

test:
	pytest tests/ -v --cov=$(PLUGINNAME)

lint:
	pylint $(PY_FILES)
	pycodestyle $(PY_FILES)

format:
	black $(PY_FILES)
	isort $(PY_FILES)

zip: clean compile
	zip -r $(PLUGINNAME).zip $(PLUGINNAME)/ \
		-x "*.git*" "*__pycache__*" "*.pyc" "*/.venv/*" "*/tests/*"
```

### 🐛 Debugging

#### Logging en QGIS

```python
from qgis.core import QgsMessageLog, Qgis

def log_message(message, level=Qgis.Info):
    """
    Registra mensaje en QGIS Message Log.

    Args:
        message (str): Mensaje a registrar
        level (Qgis.MessageLevel): Nivel del mensaje
    """
    QgsMessageLog.logMessage(
        message,
        'Mi Plugin',
        level=level
    )

# Uso
log_message("Processing started", Qgis.Info)
log_message("Warning: Large dataset", Qgis.Warning)
log_message("Error occurred", Qgis.Critical)
```

#### Python Debugger

```python
# Insertar breakpoint
import pdb; pdb.set_trace()

# O en Python 3.7+
breakpoint()
```

#### Remote Debugging con PyCharm/VS Code

```python
# PyCharm
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

# VS Code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [QGIS Python Plugin Development](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/index.html)
- [PyQGIS Developer Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [QGIS API Documentation](https://qgis.org/pyqgis/master/)
- [Processing Framework](https://docs.qgis.org/latest/en/docs/user_manual/processing/index.html)

### Comunidad

- [QGIS Stack Exchange](https://gis.stackexchange.com/questions/tagged/qgis)
- [QGIS Developers Mailing List](https://lists.osgeo.org/mailman/listinfo/qgis-developer)
- [QGIS GitHub](https://github.com/qgis/QGIS)

### Herramientas

- [Plugin Builder](https://plugins.qgis.org/plugins/pluginbuilder3/)
- [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/)
- [cookiecutter-qgis-plugin](https://github.com/wonder-sk/cookiecutter-qgis-plugin)
- [pytest-qgis](https://github.com/opengisch/pytest-qgis)

---

## 📄 Licencia

Este documento está bajo licencia Creative Commons Attribution 4.0 International (CC BY 4.0).

---

**Última actualización:** Diciembre 2024
**Mantenido por:** Comunidad QGIS
