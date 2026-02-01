# Biblioteca de Snippets QGIS (Golden Snippets)

Repositorio de patrones de diseño y código de referencia para tareas comunes y complejas en el desarrollo de plugins de QGIS.

## 🚀 Procesamiento Asíncrono (QgsTask)

Patrón estándar para evitar bloqueos de la UI:

```python
from qgis.core import QgsTask, QgsApplication

class MyProcessorTask(QgsTask):
    def __init__(self, description, data):
        super().__init__(description, QgsTask.CanCancel)
        self.data = data

    def run(self):
        # Lógica pesada aquí
        return True

    def finished(self, result):
        if result:
            print("Tarea completada con éxito")
```

## 🗺️ Manejo de Geometrías (DTO/WKT)

Desacoplamiento core de PyQGIS:

```python
# En el Core (Agnóstico)
def process_geometry(wkt_string: str):
    # Procesar usando librerías matemáticas puras o WKT
    pass

# En la GUI (PyQGIS)
geom = QgsGeometry.fromWkt(wkt_result)
layer.addFeature(feature)
```

## 🧪 Estrategia de Mocking

Referencia rápida para tests unitarios locales:

```python
from unittest.mock import MagicMock
from qgis.core import QgsGeometry

# Mock de una capa vectorial
mock_layer = MagicMock()
mock_layer.isValid.return_value = True
mock_layer.featureCount.return_value = 10
```

## 🎨 Estética Premium (QSS)

Estilos comunes para widgets programáticos:

```css
QPushButton {
    background-color: #2c3e50;
    color: white;
    border-radius: 5px;
    padding: 8px;
}
QPushButton:hover {
    background-color: #34495e;
}
```
