# Plan de Implementación - Fase v3.3.0 (Calidad Estricta e i18n)

## Objetivo General

Elevar la calidad técnica del plugin mediante la cobertura de tipos de retorno, la resolución de lagunas de internacionalización (i18n) y la refactorización de funciones críticas con alta complejidad.

---

## User Review Required

> [!IMPORTANT]
> **Decisiones Críticas para Revisión**
>
> 1. **Prioridad de Type Hints**: ¿Iniciamos por la capa `core/` o `gui/`?
> 2. **i18n Scope**: ¿Debemos resolver únicamente el código fuente core o también actualizar las traducciones en todos los idiomas soportados durante esta fase?
> 3. **QGIS Portal**: El upload `sec_interp.3.2.0.zip` al portal oficial (`plugins.qgis.org`) quedó pendiente del cierre anterior. ¿Se incluye como Objetivo 0 de esta fase?

---

## Proposed Changes

### Objetivo 1: Cobertura de Return Type Hints (Meta: ≥ 70%)

#### Contexto
La cobertura actual de return type hints es 44.9% (ci. v3.2.0). La capa GUI es la que más contribuye al déficit.

#### Componentes a Implementar

##### [MODIFY] core/ (servicios y utilidades)
Completar anotaciones de retorno en funciones de servicios que aún carecen de tipo explícito.

##### [MODIFY] gui/ (diálogos y widgets)
Priorizar métodos de manejadores de señales, callbacks de Qt y factories.

#### Estimación Detallada

| Componente | Esfuerzo | Prioridad |
|-----------|----------|------|
| `core/services/` | 0.5 días | Alta |
| `core/utils/` | 0.5 días | Alta |
| `gui/` (managers) | 1 día | Alta |
| `gui/` (dialogs / pages) | 1 día | Media |

---

### Objetivo 2: Auditoría y Limpieza de i18n

#### Contexto
895 hallazgos de `MISSING_I18N` detectados por `qgis-analyzer`. La mayoría puede ser en archivos de test o scripts, pero el core debe ser auditado.

#### Componentes a Implementar

##### [MODIFY] core/ y gui/
Envolver en `tr()` todas las cadenas visibles al usuario que aún no estén internacionalizadas.

##### [MODIFY] i18n/*.po
Actualizar archivos de traducción con los nuevos strings, al menos para `es` y `en`.

#### Estimación Detallada

| Componente | Esfuerzo | Prioridad |
|-----------|----------|------|
| Auditoría automática (`qgis-analyzer`) | 0.5 días | Alta |
| Fix strings en `core/` y `gui/` | 1 día | Media |
| Actualización `.po` (es, en) | 0.5 días | Media |

---

### Objetivo 3: Refactorización de Hotspots de Complejidad

#### Contexto
Existen 3 funciones catalogadas como `HIGH_COMPLEXITY` por `qgis-analyzer`. Estas deben ser refactorizadas para bajar la complejidad ciclomática y mejorar la testeabilidad.

#### Componentes a Implementar

##### [MODIFY] Hotspots a identificar con análisis
Se ejecutará `qgis-analyzer analyze .` para identificar los 3 hotspots exactos.

#### Estimación Detallada

| Componente | Esfuerzo | Prioridad |
|-----------|----------|------|
| Identificación de hotspots | 0.25 días | Alta |
| Refactorización (3 funciones) | 0.75 días | Alta |

---

### Objetivo 4 (Opcional): QGIS Portal Upload

#### Contexto
El release v3.2.0 fue subido a GitHub pero no al portal oficial de QGIS. Este paso completa el ciclo de release.

---

## Verification Plan

### 1. Automatizado
```bash
make docker-test          # ≥ 450 tests al 100%
uv run ai-ctx analyze --path .  # Mejoría en métricas vs. baseline 3.2.0
uv run qgis-analyzer analyze .  # Reducción de MISSING_I18N y HIGH_COMPLEXITY
```

### 2. Manual
- Navegar la UI para verificar que los labels y mensajes sigan correctamente traducidos.

---

## Estimación de Esfuerzo Total

| Objetivo | Esfuerzo | Prioridad |
|----------|----------|-----------|
| Return Type Hints | 3 días | Alta |
| i18n Audit & Fix | 2 días | Media |
| CC Hotspots | 1 día | Alta |
| QGIS Portal Upload | 0.5 días | Baja |
| **Total** | **~6.5 días** | — |

---

## Métricas Base (desde cierre v3.2.0)

| Métrica | Valor Base |
|:--------|:----------:|
| Tests | 450 / 450 ✅ |
| Quality Score | 72.6 / 100 |
| Type Hints (Params) | 73.7% |
| Type Hint (Returns) | 44.9% 🔴 |
| Docstring Coverage | 85.6% |
| MISSING_I18N | 895 |
| HIGH_COMPLEXITY functions | 3 |
