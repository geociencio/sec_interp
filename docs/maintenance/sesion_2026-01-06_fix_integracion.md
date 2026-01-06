# Walkthrough: Fix de Infraestructura de Tests de Integración

En esta sesión se ha estabilizado la ejecución de tests de integración dentro del entorno real de QGIS, resolviendo problemas de detección de rutas e interferencia de mocks.

## Cambios Realizados

### 1. Corrección de `scripts/run_tests_in_qgis.py`
Se añadió un bloque `try-except` para manejar la ausencia de la variable global `__file__` cuando se ejecuta el script desde la consola de QGIS o mediante el parámetro `--code`.

```python
try:
    SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
    PROJECT_ROOT = SCRIPT_DIR.parent
except NameError:
    PROJECT_ROOT = pathlib.Path(os.getcwd()).absolute()
```

### 2. Detección Inteligente en `tests/base_test.py`
Se modificó el sistema de mocks para detectar si `qgis.core` ya está disponible. Si lo está, se evita sobrescribir `sys.modules`, permitiendo que los tests de integración usen las librerías reales de QGIS.

```python
try:
    import qgis.core
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
```

### 3. Aislamiento de Tests de Integración
Se ajustó temporalmente el descubrimiento de tests en el runner de QGIS para centrarse en `tests/integration/`, evitando que los 300+ tests unitarios (diseñados para mocks) interfieran con el entorno real de QGIS.

## Verificación Exitosa

Se ejecutaron los tests mediante el comando:
```bash
qgis --nologo --code scripts/run_tests_in_qgis.py
```

### Resultados
- **Total Tests**: 10
- **Pass State**: ✅ SUCCESS (100%)
- **Componentes Validados**:
    - **QGIS Smoke**: Instanciación de capas y diálogos.
    - **Interpretation**: Ciclo de vida de persistencia en `QgsProject`.
    - **Measurement**: Cálculos reales de distancias y elevaciones.
    - **Export**: Lógica de proyección 3D a coordenadas reales.

## Conclusión
El proyecto ahora cuenta con una base sólida para el desarrollo de la versión 2.6.0, pudiendo validar cambios complejos (como la refactorización de exportadores) contra la API real de QGIS de forma automatizada.
