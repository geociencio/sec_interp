---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - csv
aliases:
  - csv_exporter.py
  - CSVExporter
cssclass: secinterp-note
---

# `exporters/csv_exporter.py`

> [!abstract] Resumen en una línea
> Exporta datos tabulares a CSV (`headers` + `rows`) con `csv.writer`.

**Ruta**: `exporters/csv_exporter.py` (58 líneas)
**Clase**: `CSVExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #csv

---

## 🧱 API

```python
class CSVExporter(BaseExporter):
    def get_supported_extensions(self) -> list[str]: return [".csv"]
    def export(self, output_path: Path, data: dict[str, Any], layer_name=None) -> bool:
        headers = data.get("headers")
        rows = data.get("rows")
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
```

---

## 🔗 Notas relacionadas

- [[base_exporter]] — valida rutas
- [[vector_exporter]] — homólogo vectorial

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
