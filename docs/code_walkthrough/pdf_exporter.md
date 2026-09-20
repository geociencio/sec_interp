---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - pdf
aliases:
  - pdf_exporter.py
  - PDFExporter
cssclass: secinterp-note
---

# `exporters/pdf_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **`QgsMapSettings` a PDF** con `QPdfWriter` + `QgsMapRendererCustomPainterJob`.

**Ruta**: `exporters/pdf_exporter.py` (79 líneas)
**Clase**: `PDFExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #pdf

---

## 🧱 `export()` — flujo

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

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[vector_exporter]] — homólogo vectorial

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
