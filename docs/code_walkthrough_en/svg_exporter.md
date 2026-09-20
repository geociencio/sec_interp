---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - svg_exporter.py
  - SVGExporter
cssclass: secinterp-note
---

# `exporters/svg_exporter.py`

> [!abstract] One-line summary
> Exports **`QgsMapSettings` to SVG** with `QSvgGenerator` + `QgsMapRendererCustomPainterJob`.

**Path**: `exporters/svg_exporter.py` (85 lines)
**Class**: `SVGExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

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

## 🔗 Related notes

- [[base_exporter]] — contract

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
