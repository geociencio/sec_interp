from __future__ import annotations

"""Facade for SecInterp core types re-exporting to maintain compatibility."""

from .domain_types import (
    DomainGeometry,
    ExportSettings,
    GeologyData,
    GeologyPoints,
    GeologySegment,
    InterpretationPolygon,
    InterpretationPolygon25D,
    LayerDict,
    Point2D,
    Point3D,
    PointList,
    ProfileData,
    ProfilePoints,
    SettingsDict,
    StructureData,
    StructureMeasurement,
    StructurePoints,
    ValidationResult,
)
from .dtos import (
    PreviewParams,
    PreviewResult,
)
from .enums import FieldType
from .task_inputs import (
    DrillholeTaskInput,
    GeologyTaskInput,
)

__all__ = [
    "DomainGeometry",
    "DrillholeTaskInput",
    "ExportSettings",
    "FieldType",
    "GeologyData",
    "GeologyPoints",
    "GeologySegment",
    "GeologyTaskInput",
    "InterpretationPolygon",
    "InterpretationPolygon25D",
    "LayerDict",
    "Point2D",
    "Point3D",
    "PointList",
    "PreviewParams",
    "PreviewResult",
    "ProfileData",
    "ProfilePoints",
    "SettingsDict",
    "StructureData",
    "StructureMeasurement",
    "StructurePoints",
    "ValidationResult",
]
