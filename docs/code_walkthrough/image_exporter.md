---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - image
aliases:
  - image_exporter.py
  - ImageExporter
cssclass: secinterp-note
---

# `exporters/image_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **`QgsMapSettings` a PNG/JPG** con `QImage` + `QgsMapRendererCustomPainterJob`.

**Ruta**: `exporters/image_exporter.py` (72 líneas)
**Clase**: `ImageExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #image

---

## 🧱 `export()` — flujo

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

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
