# Implementation Plan: Adaptive Vertical Exaggeration

**Phase**: v3.7.0 — Goal 2.2
**Status**: Planned
**Created**: 2026-07-20

---

## Objetivo

Reemplazar el `vertexag_spin` estático (0.1–100, default 1.0) por un sistema que calcule automáticamente la exageración vertical óptima basada en las proporciones del perfil geológico y la densidad de datos estructurales, con opción de override manual.

---

## 1. Algoritmo Adaptivo (Core)

**Archivo nuevo**: `core/services/vertical_exaggeration_service.py`

### 1.1 Exageración base por relación de aspecto

```
aspect_ratio = elevation_range / distance_range

Si aspect_ratio > 0.5:   → vert_exag = 1.0   (perfil ya es verticalmente expresivo)
Si aspect_ratio > 0.1:   → vert_exag = 2.0   (compresión moderada)
Si aspect_ratio > 0.02:  → vert_exag = 5.0   (compresión fuerte)
Si aspect_ratio <= 0.02: → vert_exag = 10.0  (compresión extrema)
```

La intuición geológica: si el perfil tiene 1000m de largo y solo 20m de relieve (ratio 0.02), se necesita 10x para que las estructuras sean visibles. Si tiene 100m de relieve en 200m (ratio 0.5), 1x es suficiente.

### 1.2 Factor de densidad estructural

```
structural_density = len(struct_data) / distance_range  (estructuras por metro)

Si density > 0.1 (1 estructura cada 10m):  multiplier = 0.7   (reducir, ya hay detalle)
Si density > 0.01:                         multiplier = 1.0
Si density <= 0.01:                        multiplier = 1.3   (aumentar, estructuras dispersas)
```

### 1.3 Fórmula final

```
adaptive_ve = clamp(base_ve * density_multiplier, 0.5, 20.0)
```

Redondeado a 1 decimal. El clamp asegura que nunca sea menor a 0.5 ni mayor a 20.0.

---

## 2. Cambios en la Interfaz (GUI)

**Archivo**: `gui/ui/pages/dem_page.py`

### 2.1 Añadir toggle Auto/Manual

```python
# Nuevo checkbox junto al spin
self.auto_ve_check = QCheckBox(self.tr("Auto"))
self.auto_ve_check.setChecked(True)  # Auto por defecto
self.auto_ve_check.toggled.connect(self._on_auto_ve_toggled)

def _on_auto_ve_toggled(self, checked):
    self.vertexag_spin.setEnabled(not checked)  # Deshabilitar spin en modo Auto
```

Layout:
```
Vert. Exag.  [Auto ✓]  [1.0]  (spin deshabilitado si Auto=True)
```

### 2.2 Placeholder visual en modo Auto

Cuando `auto_ve_check` está activo, el spin muestra el último valor calculado (read-only) con tooltip: "Calculado automáticamente según geometría del perfil".

---

## 3. Flujo de Datos

```
1. Usuario hace clic en "Preview"
2. PreviewService.generate_all() → PreviewResult (con topo, struct, geol)
3. NUEVO: VerticalExaggerationService.calculate(topo, struct) → adaptive_ve
4. Si auto_ve_check=True: usar adaptive_ve
   Si auto_ve_check=False: usar vertexag_spin.value() (manual)
5. Pasar vert_exag a PreviewRenderer.render()
```

El punto de inserción es en `sec_interp_plugin.py` entre la generación del PreviewResult y la llamada a `preview_renderer.render()`.

---

## 4. Cambios Específicos por Archivo

| Archivo | Cambio | Tipo |
|---|---|---|
| `core/services/vertical_exaggeration_service.py` | **Nuevo**: `VerticalExaggerationService` con `calculate(topo, struct) → float` | Core |
| `core/config.py` | Añadir `DEFAULT_AUTO_VE = True` | Core |
| `gui/ui/pages/dem_page.py` | Añadir `auto_ve_check`, toggle handler, exponer ambos valores en `get_data()` | GUI |
| `sec_interp_plugin.py` | Insertar cálculo adaptivo entre `generate_all()` y `render()` | GUI |
| `gui/dialog_settings_persistence.py` | Persistir `auto_ve` y `vert_exag` en QgsSettings | GUI |
| `gui/main_dialog_config.py` | Añadir `AUTO_VERTICAL_EXAGGERATION = True` | GUI |

---

## 5. Validación y Límites

- `adaptive_ve` clamp: [0.5, 20.0] — más restrictivo que el rango manual [0.1, 100.0]
- Si `struct_data` está vacío o es None, el factor de densidad = 1.0 (no afecta)
- Si `topo_data` está vacío, retornar `DEFAULT_VERT_EXAG = 1.0`
- El valor se redondea a 1 decimal para consistencia con el spin actual

---

## 6. Tests Requeridos (Core)

| Test | Descripción |
|---|---|
| `test_calculate_flat_profile` | Perfil 5000m largo, 20m relieve → VE > 5.0 |
| `test_calculate_steep_profile` | Perfil 200m largo, 100m relieve → VE ≈ 1.0 |
| `test_dense_structures_reduce_ve` | Muchas estructuras → multiplicador < 1.0 |
| `test_sparse_structures_increase_ve` | Pocas estructuras → multiplicador > 1.0 |
| `test_empty_struct_data` | Sin datos estructurales → factor densidad = 1.0 |
| `test_empty_topo_data` | Sin topografía → retorna default 1.0 |
| `test_clamp_bounds` | Valores extremos se mantienen en [0.5, 20.0] |

---

## 7. Orden de Implementación

1. **Fase 1 (Core)**: Crear `VerticalExaggerationService` + tests unitarios
2. **Fase 2 (GUI)**: Añadir `auto_ve_check` a `dem_page.py` + toggle + `get_data()`
3. **Fase 3 (Integración)**: Insertar lógica en `sec_interp_plugin.py`
4. **Fase 4 (Persistencia)**: Guardar/cargar `auto_ve` en settings y proyecto
5. **Fase 5 (Verificación)**: Docker tests completos, validación visual en QGIS

---

## 8. No-Alcance (Out of Scope)

- Exageración variable por zonas del perfil (non-uniform VE)
- Ajuste automático del `dip_scale_factor`
- Machine learning o heurísticas complejas de distribución geológica
