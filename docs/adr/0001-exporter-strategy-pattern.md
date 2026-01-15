# 1. Exporter Strategy Pattern

Date: 2024-07 (v1.0)

## Status

Accepted

## Context

The plugin supports exporting geological data to multiple formats (CSV, DXF/Shapefile, Images, PDF, SVG).
Initially, export logic was embedded within the main dialog or monolithic "save" methods. This violated the Single Responsibility Principle and Open-Closed Principle (adding a format required modifying multiple core files).

## Decision

We have adopted the **Strategy Pattern** for all data exportation.

### 1. Abstract Base Class
`exporters.base_exporter.BaseExporter` defines the common interface (`export()`) and shared utilities.

### 2. Concrete Strategies
Each export format is a separate class in `exporters/`:
- `ImageExporter` (PNG/JPG)
- `PdfExporter` (PDF)
- `SvgExporter` (SVG)
- `ShapefileExporter` (SHP/DXF)
- `CsvExporter` (CSV)

### 3. Service Orchestration
The `core.services.export_service.ExportService` acts as the Context. It receives a request, instantiates the appropriate Exporter strategy based on the file extension/type, and delegates the execution.

## Consequences

### Positive
- **Extensibility**: Adding a new format (e.g., GeoPackage) only requires adding a new class in `exporters/` without touching the GUI.
- **Maintainability**: Format-specific quirks (e.g., PDF DPI handling vs SVG scaling) are isolated.
- **Testability**: Each exporter can be unit-tested independently of the UI.

### Negative
- **Class Explosion**: We have many small files in `exporters/`.

## Compliance
- New export formats MUST implement `BaseExporter`.
- The GUI MUST NOT contain export logic; it should only collect parameters and call `ExportService`.
