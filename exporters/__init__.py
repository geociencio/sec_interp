from __future__ import annotations

"""Exporters package for Sec Interp plugin.

Provides specialized exporters for different file formats.
"""

from .base_exporter import BaseExporter
from .csv_exporter import CSVExporter
from .drillhole_3d_exporter import (
    DrillholeInterval3DExporter,
    DrillholeTrace3DExporter,
)
from .drillhole_exporters import (
    DrillholeIntervalShpExporter,
    DrillholeTraceShpExporter,
)
from .dxf_exporter import DXFExporter
from .image_exporter import ImageExporter
from .interpretation_3d_exporter import Interpretation3DExporter
from .interpretation_exporters import Interpretation2DExporter
from .pdf_exporter import PDFExporter
from .profile_exporters import (
    AxesShpExporter,
    GeologyShpExporter,
    ProfileLineShpExporter,
    StructureShpExporter,
)
from .shp_exporter import ShapefileExporter
from .svg_exporter import SVGExporter

__all__ = [
    "AxesShpExporter",
    "BaseExporter",
    "CSVExporter",
    "DrillholeInterval3DExporter",
    "DrillholeIntervalShpExporter",
    "DrillholeTrace3DExporter",
    "DrillholeTraceShpExporter",
    "GeologyShpExporter",
    "ImageExporter",
    "Interpretation2DExporter",
    "Interpretation3DExporter",
    "PDFExporter",
    "ProfileLineShpExporter",
    "SVGExporter",
    "ShapefileExporter",
    "StructureShpExporter",
    "get_exporter",
]


def get_exporter(extension: str, settings: dict) -> BaseExporter:
    """Get the appropriate exporter instance for the file extension.

    Args:
        extension: File extension (e.g., '.png', '.svg')
        settings: Export settings dictionary

    Returns:
        Appropriate exporter instance

    Raises:
        ValueError: If extension is not supported

    """
    extension = extension.lower()

    if extension in [".png", ".jpg", ".jpeg"]:
        return ImageExporter(settings)
    if extension == ".svg":
        return SVGExporter(settings)
    if extension == ".pdf":
        return PDFExporter(settings)
    if extension == ".csv":
        return CSVExporter(settings)
    if extension in [".shp", ".gpkg"]:
        return ShapefileExporter(settings)

    raise ValueError(f"Unsupported file extension: {extension}")
