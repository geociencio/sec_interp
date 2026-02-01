---
name: data-science
description: Especialización en análisis de datos, limpieza, EDA y modelado estadístico.
trigger: al trabajar con archivos CSV, Excel, Parquet o bases de datos de análisis.
---
# Skill: Data Science (Standard)

## Propósito
Este skill proporciona directrices para transformar datos crudos en conocimiento accionable, asegurando la integridad, reproducibilidad y claridad del análisis.

## Cuándo usar este skill
- Al realizar un Análisis Exploratorio de Datos (EDA).
- Al limpiar o preprocesar datasets para modelos o reportes.
- Al generar visualizaciones estadísticas.

## Guía Operativa

### 1. Validación de Entrada (Sanity Check)
Antes de cualquier análisis, ejecuta el script de validación:
```bash
uv run python skills/data-science/scripts/validate_dataset.py --input path/to/dataset.csv
```

### 2. Flujo de Limpieza (Cleaning Pipeline)
- **Valores Nulos**: Decidir estrategia (imputación, eliminación o marcado) basada en el contexto del negocio.
- **Duplicados**: Identificar duplicados lógicos (no solo por hash de fila).
- **Tipado**: Asegurar que las columnas numéricas sean `float/int` y las fechas sean `datetime`.

### 3. Análisis Exploratorio (EDA)
Sigue el template [eda_template.py](examples/eda_template.py) para:
- Distribuciones de frecuencia.
- Correlaciones (Pearson/Spearman).
- Identificación de outliers (Z-score o IQR).

## Checklist de Calidad
- [ ] ¿Se han documentado las transformaciones realizadas a los datos?
- [ ] ¿Hay un reporte de calidad inicial (nulos, outliers)?
- [ ] ¿Las visualizaciones tienen títulos, etiquetas de ejes y leyendas claras?
- [ ] ¿El código es reproducible (seed fija para aleatoriedad)?
