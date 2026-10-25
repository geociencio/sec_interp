"""Factory for creating and styling QGIS memory layers for the preview."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsPointXY, QgsVectorLayer
from qgis.PyQt.QtGui import QColor

from sec_interp.core.domain import GeologyData, ProfileData, StructureData
from sec_interp.core.domain.entities import InterpretationPolygon
from sec_interp.gui.preview_layers.drillholes import (
    create_drillhole_interval_layer,
    create_drillhole_trace_layer,
)
from sec_interp.gui.preview_layers.geology import create_geol_layer
from sec_interp.gui.preview_layers.interpretations import create_interp_layer
from sec_interp.gui.preview_layers.structures import create_struct_layer
from sec_interp.gui.preview_layers.topography import (
    create_smoothed_topo_layer,
    create_topo_fill_layer,
    create_topo_layer,
)
from sec_interp.gui.renderers.color_manager import ColorManager
from sec_interp.gui.renderers.drillhole_renderer import DrillholeRenderer
from sec_interp.gui.renderers.geology_renderer import GeologyRenderer
from sec_interp.gui.renderers.interpretation_renderer import InterpretationRenderer
from sec_interp.gui.renderers.structure_renderer import StructureRenderer
from sec_interp.gui.renderers.topo_renderer import TopoRenderer
from sec_interp.gui.utils import create_memory_layer as make_memory_layer
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from qgis.core import QgsVectorDataProvider

logger = get_logger(__name__)


class PreviewLayerFactory:
    """Factory for creating and styling QGIS memory layers for the preview."""

    @property
    def active_units(self) -> dict[str, Any]:
        """Compatibility property for active geological units."""
        return self.color_manager._active_units

    @active_units.setter
    def active_units(self, value: dict[str, Any]) -> None:
        """Allow resetting active units for cleanup."""
        if not value:
            self.color_manager._active_units = {}

    def __init__(self) -> None:
        """Initialize the layer factory with specialized renderers."""
        self.color_manager: ColorManager = ColorManager()
        self.topo_renderer: TopoRenderer = TopoRenderer()
        self.geol_renderer: GeologyRenderer = GeologyRenderer(self.color_manager)
        self.struct_renderer: StructureRenderer = StructureRenderer()
        self.drill_renderer: DrillholeRenderer = DrillholeRenderer(self.color_manager)
        self.interp_renderer: InterpretationRenderer = InterpretationRenderer()

    def get_color_for_unit(self, name: str) -> QColor:
        """Get a consistent color for a geological unit based on its name."""
        return self.color_manager.get_color(name)

    def _apply_exaggeration(
        self, points: list[tuple[float, float]], vert_exag: float
    ) -> list[tuple[float, float]]:
        """Apply vertical exaggeration to a list of (dist, elev) points."""
        return [(d, e * vert_exag) for d, e in points]

    def _to_qgs_points(self, points: list[tuple[float, float]]) -> list[QgsPointXY]:
        """Convert a list of (x, y) tuples to QgsPointXY objects."""
        return [QgsPointXY(x, y) for x, y in points]

    def create_memory_layer(
        self,
        geometry_type: str,
        name: str,
        fields: str | None = None,
    ) -> tuple[QgsVectorLayer | None, QgsVectorDataProvider | None]:
        """Create a memory layer with project CRS."""
        uri = geometry_type
        if fields:
            uri += f"?{fields}"

        layer = make_memory_layer(uri, name)
        if layer is None:
            return None, None

        return layer, layer.dataProvider()

    def create_topo_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        use_adaptive_sampling: bool = False,
        color_mode: str = "gradient",
        ramp_name: str | None = None,
        single_color: str | None = None,
        line_width: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create a temporary layer for the topographic profile."""
        return create_topo_layer(
            self,
            topo_data,
            vert_exag,
            max_points,
            use_adaptive_sampling,
            color_mode,
            ramp_name,
            single_color,
            line_width,
        )

    def create_smoothed_topo_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        color: str = "#e57373",
    ) -> QgsVectorLayer | None:
        """Create a smoothed topography overlay line."""
        return create_smoothed_topo_layer(self, topo_data, vert_exag, max_points, color)

    def create_topo_fill_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        base_elevation: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create a solid curtain fill under the topography."""
        return create_topo_fill_layer(self, topo_data, vert_exag, max_points, base_elevation)

    def create_geol_layer(
        self,
        geol_data: GeologyData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
    ) -> QgsVectorLayer | None:
        """Create a temporary layer for the geological profile."""
        return create_geol_layer(self, geol_data, vert_exag, max_points)

    def create_struct_layer(
        self,
        struct_data: StructureData,
        reference_data: ProfileData,
        vert_exag: float = 1.0,
        dip_line_length: float | None = None,
        color: str | None = None,
        width: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create a temporary layer for structural dips."""
        return create_struct_layer(
            self,
            struct_data,
            reference_data,
            vert_exag,
            dip_line_length,
            color,
            width,
        )

    def create_drillhole_trace_layer(
        self,
        drillhole_data: list,
        vert_exag: float = 1.0,
        color: str | None = None,
        width: float | None = None,
        labels: bool = True,
    ) -> QgsVectorLayer | None:
        """Create a temporary layer for drillhole traces."""
        return create_drillhole_trace_layer(self, drillhole_data, vert_exag, color, width, labels)

    def create_drillhole_interval_layer(
        self,
        drillhole_data: list,
        vert_exag: float = 1.0,
    ) -> QgsVectorLayer | None:
        """Create a temporary layer for drillhole intervals."""
        return create_drillhole_interval_layer(self, drillhole_data, vert_exag)

    def create_interp_layer(
        self,
        interp_data: list[InterpretationPolygon],
        vert_exag: float = 1.0,
        default_color: str | None = None,
        hidden_ids: set[str] | None = None,
    ) -> QgsVectorLayer | None:
        """Create a memory layer for interpretation polygons."""
        return create_interp_layer(self, interp_data, vert_exag, default_color, hidden_ids)
