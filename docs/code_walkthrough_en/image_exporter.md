---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - image_exporter.py
  - ImageExporter
cssclass: secinterp-note
---

# `exporters/image_exporter.py`

> [!abstract] One-line summary
> Exports **`QgsMapSettings` to PNG/JPG** with `QImage` + `QgsMapRendererCustomPainterJob`.

**Path**: `exporters/image_exporter.py` (72 lines)
**Class**: `ImageExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path: Path, map_settings: QgsMapSettings) -> bool:
    image = QImage(QSize(width, height), QImage.Format_ARGB32)
    image.fill(background_color)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    job = QgsMapRendererCustomPainterJob(map_settings, painter)
    job.start()
    job.waitForFinished()
    image.save(str(output_path))
```

---

## 🔗 Related notes

- [[base_exporter]] — contract

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
