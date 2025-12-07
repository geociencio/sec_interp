# -*- coding: utf-8 -*-
"""
Exporters package for Sec Interp plugin.

Provides specialized exporters for different file formats.
"""

from .base_exporter import BaseExporter
from .image_exporter import ImageExporter
from .svg_exporter import SVGExporter
from .pdf_exporter import PDFExporter
from .csv_exporter import CSVExporter
from .shp_exporter import ShapefileExporter
from .profile_exporters import (
    ProfileLineShpExporter,
    GeologyShpExporter,
    StructureShpExporter,
    AxesShpExporter,
)

__all__ = [
    "BaseExporter",
    "ImageExporter",
    "SVGExporter",
    "PDFExporter",
    "CSVExporter",
    "ShapefileExporter",
    "ProfileLineShpExporter",
    "GeologyShpExporter",
    "StructureShpExporter",
    "AxesShpExporter",
    "get_exporter",
]


def get_exporter(extension: str, settings: dict):
    """
    Factory function to get appropriate exporter for file extension.

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
