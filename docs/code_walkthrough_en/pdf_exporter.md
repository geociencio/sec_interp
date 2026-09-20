---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - pdf_exporter.py
  - PDFExporter
cssclass: secinterp-note
---

# `exporters/pdf_exporter.py`

> [!abstract] One-line summary
> Exports **`QgsMapSettings` to PDF** with `QPdfWriter` + `QgsMapRendererCustomPainterJob`.

**Path**: `exporters/pdf_exporter.py` (79 lines)
**Class**: `PDFExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path: Path, map_settings: QgsMapSettings) -> bool:
    width = self.get_setting("width", 800)
    height = self.get_setting("height", 600)
    writer = QPdfWriter(str(output_path))
    writer.setResolution(300)
    writer.setPageSize(QPageSize(QSizeF(width, height), QPageSize.Unit.Point))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0))
    painter = QPainter()
    painter.begin(writer)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    map_settings.setOutputSize(QSize(writer.width(), writer.height()))
    map_settings.setOutputDpi(writer.resolution())
    job = QgsMapRendererCustomPainterJob(map_settings, painter)
    job.start()
    job.waitForFinished()
    painter.end()
    return True
```

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[vector_exporter]] — vector counterpart

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
