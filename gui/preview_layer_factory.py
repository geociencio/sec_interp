"""Layer factory for SecInterp preview.

Handles creation of temporary memory layers and configuration of native QGIS symbology.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsFeature,
    QgsGeometry,
    QgsLineString,
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsProject,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.logger_config import get_logger

from .preview_optimizer import PreviewOptimizer


logger = get_logger(__name__)


class PreviewLayerFactory:
    """Factory for creating and styling QGIS memory layers for the preview."""

    # Color palette for geological units
    GEOLOGY_COLORS: ClassVar[list[QColor]] = [
        QColor(231, 76, 60),  # Red
        QColor(52, 152, 219),  # Blue
        QColor(46, 204, 113),  # Green
        QColor(155, 89, 182),  # Purple
        QColor(241, 196, 15),  # Yellow
        QColor(230, 126, 34),  # Orange
        QColor(26, 188, 156),  # Turquoise
        QColor(52, 73, 94),  # Dark Blue/Grey
        QColor(149, 165, 166),  # Grey
        QColor(211, 84, 0),  # Pumpkin
        QColor(192, 57, 43),  # Dark Red
        QColor(127, 140, 141),  # Dark Grey
        QColor(142, 68, 173),  # Wisteria
        QColor(41, 128, 185),  # Belize Hole
        QColor(39, 174, 96),  # Nephritis
        QColor(22, 160, 133),  # Green Sea
    ]

    def __init__(self):
        """Initialize the layer factory."""
        self.active_units: dict[str, QColor] = {}

    def get_color_for_unit(self, name: str) -> QColor:
        """Get a consistent color for a geological unit based on its name."""
        if not name:
            return QColor(100, 100, 100)  # Default grey

        if name in self.active_units:
            return self.active_units[name]

        # Simple hash to map name to index
        hash_val = sum(ord(c) for c in str(name))
        index = hash_val % len(self.GEOLOGY_COLORS)
        color = self.GEOLOGY_COLORS[index]
        self.active_units[name] = color
        return color

    def create_memory_layer(
        self,
        geometry_type: str,
        name: str,
        fields: Optional[str] = None,
    ) -> tuple[Optional[QgsVectorLayer], Any]:
        """Create a memory layer with an unknown CRS.

        Args:
            geometry_type: "Point", "LineString", "Polygon"
            name: Layer display name
            fields: Optional field definition string (e.g., "field=id:integer")

        Returns:
            Tuple of (QgsVectorLayer, QgsDataProvider) or (None, None) if failed
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
    ) -> Optional[QgsVectorLayer]:
        """Create temporary layer for topographic profile."""
        if not topo_data or len(topo_data) < 2:
            return None

        # Apply LOD decimation
        if use_adaptive_sampling:
            render_data = PreviewOptimizer.adaptive_sample(
                topo_data, max_points=max_points
            )
        else:
            render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)

        layer, provider = self.create_memory_layer("LineString", "Topography")
        if not layer:
            return None

        line_points = [QgsPointXY(dist, elev * vert_exag) for dist, elev in render_data]
        line_geom = QgsGeometry.fromPolylineXY(line_points)

        feat = QgsFeature()
        feat.setGeometry(line_geom)
        provider.addFeatures([feat])

        symbol = QgsLineSymbol.createSimple(
            {
                "color": "0,102,204",
                "width": "0.5",
                "capstyle": "round",
                "joinstyle": "round",
            }
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.updateExtents()
        return layer

    def create_geol_layer(
        self, geol_data: GeologyData, vert_exag: float = 1.0, max_points: int = 1000
    ) -> Optional[QgsVectorLayer]:
        """Create temporary layer for geological profile."""
        if not geol_data:
            return None

        layer, provider = self.create_memory_layer(
            "LineString", "Geology", "field=unit:string"
        )
        if not layer:
            return None

        unique_units = {s.unit_name for s in geol_data}
        features = []
        for segment in geol_data:
            if not segment.points or len(segment.points) < 2:
                continue

            render_points = PreviewOptimizer.decimate(
                segment.points, max_points=max_points
            )
            line_points = [
                QgsPointXY(dist, elev * vert_exag) for dist, elev in render_points
            ]
            line_geom = QgsGeometry.fromPolylineXY(line_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)

        provider.addFeatures(features)

        categories = []
        for unit_name in unique_units:
            color = self.get_color_for_unit(unit_name)
            symbol = QgsLineSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()}",
                    "width": "0.7",
                    "capstyle": "round",
                    "joinstyle": "round",
                }
            )
            category = QgsRendererCategory(unit_name, symbol, unit_name)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("unit", categories)
        layer.setRenderer(renderer)
        layer.updateExtents()
        return layer

    def create_struct_layer(
        self,
        struct_data: StructureData,
        reference_data: ProfileData,
        vert_exag: float = 1.0,
        dip_line_length: Optional[float] = None,
    ) -> Optional[QgsVectorLayer]:
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

            p1 = QgsPointXY(dist, elev * vert_exag)
            p2 = QgsPointXY(dist + dx, (elev - dy) * vert_exag)

            line_geom = QgsGeometry.fromPolylineXY([p1, p2])
            feat = QgsFeature()
            feat.setGeometry(line_geom)
            features.append(feat)

        provider.addFeatures(features)

        symbol = QgsLineSymbol.createSimple(
            {"color": "204,0,0", "width": "0.5", "capstyle": "round"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.updateExtents()
        return layer

    def create_drillhole_trace_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> Optional[QgsVectorLayer]:
        """Create temporary layer for drillhole traces."""
        logger.debug(f"create_drillhole_trace_layer called with {len(drillhole_data) if drillhole_data else 0} holes")
        if not drillhole_data:
            logger.warning("No drillhole data provided for trace layer")
            return None

        layer, provider = self.create_memory_layer(
            "LineString", "Drillhole Traces", "field=hole_id:string"
        )
        if not layer:
            return None

        features = []
        for hole_id, trace_points, _ in drillhole_data:
            if not trace_points or len(trace_points) < 2:
                logger.debug(f"Skipping hole {hole_id}: insufficient trace points ({len(trace_points) if trace_points else 0})")
                continue

            render_points = [QgsPointXY(x, y * vert_exag) for x, y in trace_points]
            line_geom = QgsGeometry.fromPolylineXY(render_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("hole_id", hole_id)
            features.append(feat)

        logger.info(f"Adding {len(features)} drillhole trace features to layer")

        provider.addFeatures(features)

        symbol = QgsLineSymbol.createSimple(
            {"color": "50,50,50", "width": "0.3", "capstyle": "round"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        settings = QgsPalLayerSettings()
        settings.fieldName = "hole_id"
        settings.placement = QgsPalLayerSettings.Placement.Line

        txt_format = QgsTextFormat()
        txt_format.setColor(QColor(0, 0, 0))
        txt_format.setSize(8)
        settings.setFormat(txt_format)

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)
        layer.updateExtents()
        return layer

    def create_drillhole_interval_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> Optional[QgsVectorLayer]:
        """Create temporary layer for drillhole intervals."""
        if not drillhole_data:
            return None

        all_segments = []
        for _, _, segments in drillhole_data:
            if segments:
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
        for segment in all_segments:
            if not segment.points or len(segment.points) < 2:
                continue

            unique_units.add(segment.unit_name)
            render_points = [QgsPointXY(x, y * vert_exag) for x, y in segment.points]
            line_geom = QgsGeometry.fromPolylineXY(render_points)

            feat = QgsFeature(layer.fields())
            feat.setGeometry(line_geom)
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)

        provider.addFeatures(features)

        categories = []
        for unit_name in unique_units:
            color = self.get_color_for_unit(unit_name)
            symbol = QgsLineSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()}",
                    "width": "2.0",
                    "capstyle": "flat",
                    "joinstyle": "bevel",
                }
            )
            category = QgsRendererCategory(unit_name, symbol, unit_name)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer("unit", categories)
        layer.setRenderer(renderer)
        layer.updateExtents()
        return layer

    def interpolate_elevation(
        self, reference_data: ProfileData, target_dist: float
    ) -> float:
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
