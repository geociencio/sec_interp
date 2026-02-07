from __future__ import annotations

"""SecInterp Core Domain Package.

This package contains the domain entities, DTOs, and enums that define
the core business logic of the plugin, decoupled from QGIS-specific
implementation details where possible.
"""

from .dtos import (
    PreviewParams,
    PreviewResult,
)
from .entities import (
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
from .enums import FieldType
from .spatial_meta import SpatialMeta
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
    "SpatialMeta",
    "StructureData",
    "StructureMeasurement",
    "StructurePoints",
    "ValidationResult",
]
