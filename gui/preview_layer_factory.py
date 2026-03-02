"""Factory for creating and styling QGIS memory layers for the preview."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.core.domain import (
    DrillholeProjection,
    GeologyData,
    ProfileData,
    StructureData,
)
from sec_interp.core.utils.geometry_utils.optimization import PreviewOptimizer
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from qgis.core import QgsVectorDataProvider

    from sec_interp.gui.renderers.color_manager import ColorManager
    from sec_interp.gui.renderers.drillhole_renderer import DrillholeRenderer
    from sec_interp.gui.renderers.geology_renderer import GeologyRenderer
    from sec_interp.gui.renderers.structure_renderer import StructureRenderer
    from sec_interp.gui.renderers.topo_renderer import TopoRenderer

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
        from sec_interp.gui.renderers.color_manager import ColorManager
        from sec_interp.gui.renderers.drillhole_renderer import DrillholeRenderer
        from sec_interp.gui.renderers.geology_renderer import GeologyRenderer
        from sec_interp.gui.renderers.structure_renderer import StructureRenderer
        from sec_interp.gui.renderers.topo_renderer import TopoRenderer

        self.color_manager: ColorManager = ColorManager()
        self.topo_renderer: TopoRenderer = TopoRenderer()
        self.geol_renderer: GeologyRenderer = GeologyRenderer(self.color_manager)
        self.struct_renderer: StructureRenderer = StructureRenderer()
        self.drill_renderer: DrillholeRenderer = DrillholeRenderer(self.color_manager)

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
        """Create a memory layer with project CRS.

        Args:
            geometry_type: Geometry type (e.g., "Point", "LineString").
            name: Display name for the layer.
            fields: Optional field definition URI string.

        Returns:
            Tuple of (Layer, DataProvider).

        """
        uri = geometry_type
        if fields:
            uri += f"?{fields}"

        layer = QgsVectorLayer(uri, name, "memory")

        if not layer.isValid():
            logger.error(f"Failed to create memory layer: {name}")
            return None, None

        # Ensure layer has a valid CRS (Project CRS) to allow rendering
        # independent of On-The-Fly transformation settings
        project_crs = QgsProject.instance().crs()
        if project_crs.isValid():
            layer.setCrs(project_crs)

        return layer, layer.dataProvider()

    def create_topo_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        use_adaptive_sampling: bool = False,
    ) -> QgsVectorLayer | None:
        """Create temporary layer for topographic profile with polychromatic elevation styling."""
        MIN_REQUIRED_POINTS = 2
        if not topo_data or len(topo_data) < MIN_REQUIRED_POINTS:
            return None

        # Apply LOD decimation
        if use_adaptive_sampling:
            render_data = PreviewOptimizer.adaptive_sample(topo_data, max_points=max_points)
        else:
            render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)

        # Create layer with elevation field for polychromy
        layer, provider = self.create_memory_layer("LineString", "Topography", "field=elev:double")
        if not layer:
            return None

        # Create segments for each pair of points to allow per-segment coloring
        features = []

        for i in range(len(render_data) - 1):
            p1 = render_data[i]
            p2 = render_data[i + 1]

            line_points = self._to_qgs_points(self._apply_exaggeration([p1, p2], vert_exag))
            line_geom = QgsGeometry.fromPolylineXY(line_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            # Use average elevation for the segment color
            avg_elev = (p1[1] + p2[1]) / 2.0
            feat.setAttribute("elev", avg_elev)
            features.append(feat)

        if not features:
            return None

        provider.addFeatures(features)
        self.topo_renderer.apply_style(layer)
        layer.updateExtents()
        return layer

    def create_topo_fill_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        base_elevation: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create a solid 'curtain' fill layer under the topography for depth."""
        MIN_REQUIRED_POINTS = 2
        if not topo_data or len(topo_data) < MIN_REQUIRED_POINTS:
            return None

        render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)

        layer, provider = self.create_memory_layer("Polygon", "Topography Fill")
        if not layer:
            return None

        # Calculate base line (bottom of the section)
        elevs = [p[1] for p in topo_data]
        if base_elevation is None:
            base_elevation = min(elevs) - (max(elevs) - min(elevs)) * 0.2

        base_y = base_elevation * vert_exag

        # Construct polygon points
        poly_points = []
        # Top edge (the profile)
        for d, e in render_data:
            poly_points.append(QgsPointXY(d, e * vert_exag))

        # Bottom edge (closing the curtain)
        poly_points.append(QgsPointXY(render_data[-1][0], base_y))
        poly_points.append(QgsPointXY(render_data[0][0], base_y))
        poly_points.append(QgsPointXY(render_data[0][0], render_data[0][1] * vert_exag))

        geom = QgsGeometry.fromPolygonXY([poly_points])
        feat = QgsFeature()
        feat.setGeometry(geom)
        provider.addFeatures(
            [feat]
        )  # Corrected from 'features' to '[feat]' as 'features' is not defined here.
        self.struct_renderer.apply_style(
            layer
        )  # Simple fill style could be here too, but for now reuse
        layer.updateExtents()
        return layer

    def create_geol_layer(
        self, geol_data: GeologyData, vert_exag: float = 1.0, max_points: int = 1000
    ) -> QgsVectorLayer | None:
        """Create temporary layer for geological profile."""
        if not geol_data:
            return None

        layer, provider = self.create_memory_layer("LineString", "Geology", "field=unit:string")
        if not layer:
            return None

        unique_units = {s.unit_name for s in geol_data}
        features = []
        MIN_REQUIRED_POINTS = 2
        for segment in geol_data:
            if not segment.points or len(segment.points) < MIN_REQUIRED_POINTS:
                continue

            render_points = PreviewOptimizer.decimate(segment.points, max_points=max_points)
            line_points = self._to_qgs_points(self._apply_exaggeration(render_points, vert_exag))
            line_geom = QgsGeometry.fromPolylineXY(line_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)

        provider.addFeatures(features)
        self.geol_renderer.apply_style(layer, unique_units=unique_units)
        layer.updateExtents()
        return layer

    def create_struct_layer(
        self,
        struct_data: StructureData,
        reference_data: ProfileData,
        vert_exag: float = 1.0,
        dip_line_length: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create temporary layer for structural dips."""
        if not struct_data:
            return None

        layer, provider = self.create_memory_layer("LineString", "Structures")
        if not layer:
            return None

        if dip_line_length is not None and dip_line_length > 0:
            line_length = dip_line_length
        else:
            if reference_data:
                elevs = [e for _, e in reference_data]
                e_range = max(elevs) - min(elevs)
            else:
                e_range = 100
            line_length = e_range * 0.1

        features = []
        for m in struct_data:
            elev = m.elevation
            dist = m.distance
            app_dip = m.apparent_dip

            rad_dip = math.radians(abs(app_dip))
            dx = line_length * math.cos(rad_dip)
            dy = line_length * math.sin(rad_dip)

            if app_dip < 0:
                dx = -dx

            points = [(dist, elev), (dist + dx, elev - dy)]
            line_points = self._to_qgs_points(self._apply_exaggeration(points, vert_exag))

            line_geom = QgsGeometry.fromPolylineXY(line_points)
            feat = QgsFeature()
            feat.setGeometry(line_geom)
            features.append(feat)

        provider.addFeatures(features)
        self.struct_renderer.apply_style(layer)
        layer.updateExtents()
        return layer

    def create_drillhole_trace_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> QgsVectorLayer | None:
        """Create temporary layer for drillhole traces."""
        logger.debug(
            f"create_drillhole_trace_layer called with {len(drillhole_data) if drillhole_data else 0} holes"
        )
        if not drillhole_data:
            logger.warning("No drillhole data provided for trace layer")
            return None

        layer, provider = self.create_memory_layer(
            "LineString", "Drillhole Traces", "field=hole_id:string"
        )
        if not layer:
            return None

        features = []
        for hole_data in drillhole_data:
            # hole_data can be DrillholeProjection object or (hole_id, spatial_points, segments) tuple
            if isinstance(hole_data, DrillholeProjection):
                hole_id = hole_data.hole_id
                trace_points = hole_data.points_3d
            else:
                hole_id, trace_points = hole_data[0], hole_data[1]

            MIN_TRACE_POINTS = 2
            if not trace_points or len(trace_points) < MIN_TRACE_POINTS:
                logger.debug(
                    f"Skipping hole {hole_id}: insufficient trace points ({len(trace_points) if trace_points else 0})"
                )
                continue

            render_points = []
            for p in trace_points:
                # Handle both SpatialMeta objects and legacy tuples
                dist = getattr(p, "dist_along", p[0] if isinstance(p, list | tuple) else 0.0)
                z = getattr(p, "z", p[1] if isinstance(p, list | tuple) else 0.0)
                render_points.append((dist, z))

            line_points = self._to_qgs_points(self._apply_exaggeration(render_points, vert_exag))
            line_geom = QgsGeometry.fromPolylineXY(line_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("hole_id", hole_id)
            features.append(feat)

        logger.info(f"Adding {len(features)} drillhole trace features to layer")

        provider.addFeatures(features)
        self.drill_renderer.apply_style(layer, role="trace")
        layer.updateExtents()
        return layer

    def create_drillhole_interval_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> QgsVectorLayer | None:
        """Create temporary layer for drillhole intervals."""
        if not drillhole_data:
            return None

        all_segments = []
        for hole_data in drillhole_data:
            # hole_data can be DrillholeProjection or legacy tuple
            if isinstance(hole_data, DrillholeProjection):
                segments = hole_data.segments
            else:
                # segments are usually the last element
                MIN_HOLE_DATA_FOR_SEGMENTS = 3
                segments = hole_data[-1] if len(hole_data) >= MIN_HOLE_DATA_FOR_SEGMENTS else []

            if segments and isinstance(segments, list):
                all_segments.extend(segments)

        if not all_segments:
            return None

        layer, provider = self.create_memory_layer(
            "LineString", "Drillhole Intervals", "field=unit:string"
        )
        if not layer:
            return None

        features = []
        unique_units = set()
        MIN_SEGMENT_POINTS = 2
        for segment in all_segments:
            if not segment.points or len(segment.points) < MIN_SEGMENT_POINTS:
                continue

            unique_units.add(segment.unit_name)
            line_points = self._to_qgs_points(self._apply_exaggeration(segment.points, vert_exag))
            line_geom = QgsGeometry.fromPolylineXY(line_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)

        provider.addFeatures(features)
        self.drill_renderer.apply_style(layer, role="interval", unique_units=unique_units)
        layer.updateExtents()
        return layer

    def interpolate_elevation(self, reference_data: ProfileData, target_dist: float) -> float:
        """Interpolate elevation at a given distance."""
        if not reference_data:
            return 0
        for i in range(len(reference_data) - 1):
            d1, e1 = reference_data[i]
            d2, e2 = reference_data[i + 1]
            if d1 <= target_dist <= d2:
                if d2 == d1:
                    return e1
                t = (target_dist - d1) / (d2 - d1)
                return e1 + t * (e2 - e1)
        if target_dist < reference_data[0][0]:
            return reference_data[0][1]
        return reference_data[-1][1]
