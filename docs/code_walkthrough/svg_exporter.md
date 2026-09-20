---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - svg
aliases:
  - svg_exporter.py
  - SVGExporter
cssclass: secinterp-note
---

# `exporters/svg_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **`QgsMapSettings` a SVG** con `QSvgGenerator` + `QgsMapRendererCustomPainterJob`.

**Ruta**: `exporters/svg_exporter.py` (85 líneas)
**Clase**: `SVGExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #svg

---

## 🧱 `export()` — flujo

```python
def export(self, output_path: Path, map_settings) -> bool:
    generator = QSvgGenerator()
    generator.setFileName(str(output_path))
    generator.setSize(QSize(width, height))
    generator.setViewBox(QRectF(0, 0, width, height))
    generator.setTitle(title)
    generator.setDescription(description)
    painter = QPainter(generator)
    job = QgsMapRendererCustomPainterJob(map_settings, painter)
    job.start()
    job.waitForFinished()
```

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
