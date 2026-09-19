"""Services package for geological data processing.

This package contains service classes that handle specific data processing tasks:
- GeologyService: Geological profile generation
- StructureService: Structural data projection
- DrillholeService: Drillhole projection
"""

from __future__ import annotations

from .drillhole_service import DrillholeService
from .geology_service import GeologyService
from .structure_service import StructureService

__all__ = [
    "DrillholeService",
    "GeologyService",
    "StructureService",
]
