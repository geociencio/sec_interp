"""Preview Renderer Module (PyQGIS Native).

Handles rendering of interactive previews using native QGIS resources:
- QgsMapCanvas for rendering
- Temporary memory layers for data
- Native QGIS symbology
"""

from collections import defaultdict
import math
from typing import Optional

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsFeature,
    QgsGeometry,
    QgsLineString,
    QgsLineSymbol,
    QgsMapRendererCustomPainterJob,
    QgsMapSettings,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsProject,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtCore import QRectF, QSize, Qt
from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter, QPen

from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class PreviewRenderer:
    """Renders interactive preview using native PyQGIS resources."""

    # Color palette for geological units
    GEOLOGY_COLORS = [
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

    def __init__(self, canvas=None) -> None:
        """Initialize preview renderer.

        Args:
            canvas: QgsMapCanvas instance (optional, will be created if not provided)
        """
        self.canvas = canvas
        self.layers = []  # Track created layers for cleanup
        self.active_units = {}  # Track active geological units for legend {name: color}
        self.has_topography = False  # Track if topography layer exists
        self.has_structures = False  # Track if structures layer exists

    def _decimate_line_data(
        self,
        data: list[tuple[float, float]],
        tolerance: float | None = None,
        max_points: int = 1000,
    ) -> list[tuple[float, float]]:
        """Decimate line data using Douglas-Peucker algorithm.

        Args:
            data: List of (x, y) tuples
            tolerance: Simplification tolerance (if provided, overrides max_points heuristic)
            max_points: Maximum points to keep (approximate target if tolerance is None)

        Returns:
            Decimated list of (x, y) tuples
        """
        if not data or len(data) <= max_points: # Check for max_points even if tolerance is given
            return data

        try:
            # Create QgsGeometry from points
            points = [QgsPointXY(x, y) for x, y in data]
            line = QgsGeometry.fromPolylineXY(points)

            # Determine tolerance
            if tolerance is None:
                # Auto-calculate tolerance based on max_points heuristic
                extent = line.boundingBox()
                diag = math.sqrt(extent.width() ** 2 + extent.height() ** 2)
                calculated_tolerance = diag / max_points
            else:
                calculated_tolerance = tolerance

            # Simplify
            simplified = line.simplify(calculated_tolerance)

            # Extract points
            if simplified.isMultipart():
                result_points = simplified.asMultiPolyline()[0]
            else:
                result_points = simplified.asPolyline()

            result = [(p.x(), p.y()) for p in result_points]

            logger.debug(
                f"LOD Decimation: {len(data)} -> {len(result)} points (tol={calculated_tolerance:.2f})"
            )
            return result

        except Exception as e:
            logger.warning(f"LOD decimation failed: {e}")
            return data

    def _calculate_curvature(self, data: list[tuple[float, float]]) -> list[float]:
        """Calculate a simple curvature metric for each point in a line.

        This approximates curvature by the angle deviation between successive segments.
        High values indicate sharper turns.

        Args:
            data: List of (x, y) tuples.

        Returns:
            List of curvature values (angles in degrees), same length as data.
        """
        if len(data) < 3:
            return [0.0] * len(data)

        curvatures = [0.0]  # First point has no preceding segment
        for i in range(1, len(data) - 1):
            p_prev = data[i - 1]
            p_curr = data[i]
            p_next = data[i + 1]

            # Vectors for segments
            v1_x = p_curr[0] - p_prev[0]
            v1_y = p_curr[1] - p_prev[1]
            v2_x = p_next[0] - p_curr[0]
            v2_y = p_next[1] - p_curr[1]

            # Dot product and magnitudes
            dot_product = v1_x * v2_x + v1_y * v2_y
            mag_v1 = math.sqrt(v1_x**2 + v1_y**2)
            mag_v2 = math.sqrt(v2_x**2 + v2_y**2)

            if mag_v1 == 0 or mag_v2 == 0:
                angle = 0.0
            else:
                # Angle between vectors
                cosine_angle = dot_product / (mag_v1 * mag_v2)
                # Clamp to avoid NaN from floating point inaccuracies
                cosine_angle = max(-1.0, min(1.0, cosine_angle))
                angle = math.degrees(math.acos(cosine_angle))

            # Angle deviation from 180 (straight line)
            curvatures.append(abs(180 - angle))

        curvatures.append(0.0)  # Last point has no succeeding segment
        return curvatures

    def _adaptive_sample(
        self,
        data: list[tuple[float, float]],
        min_tolerance: float = 0.1,
        max_tolerance: float = 10.0,
        max_points: int = 1000,
    ) -> list[tuple[float, float]]:
        """Adaptively sample data based on local curvature.

        Args:
            data: List of (x, y) tuples
            min_tolerance: Minimum tolerance for high-detail areas
            max_tolerance: Maximum tolerance for low-detail areas
            max_points: Maximum points to keep (approximate target)

        Returns:
            Adaptively sampled data
        """
        if len(data) <= max_points:
            return data

        # Calculate local curvature
        curvatures = self._calculate_curvature(data)

        # Use average curvature to set a general tolerance for the entire line
        # This is a simplification; a true adaptive algorithm would vary tolerance per segment
        avg_curvature = sum(curvatures) / len(curvatures)

        # Scale tolerance based on average curvature:
        # High curvature -> lower tolerance (more detail)
        # Low curvature -> higher tolerance (less detail)
        # Interpolate between min_tolerance and max_tolerance
        # Normalize avg_curvature (assuming max possible is 180, though usually much less)
        normalized_curvature = avg_curvature / 180.0
        # Invert for tolerance: higher curvature means lower tolerance
        tolerance_factor = 1.0 - normalized_curvature

        # Linearly interpolate tolerance
        tolerance = min_tolerance + (max_tolerance - min_tolerance) * tolerance_factor
        tolerance = max(
            min_tolerance, min(max_tolerance, tolerance)
        )  # Clamp to ensure range

        logger.debug(
            f"Adaptive sampling: Avg curvature={avg_curvature:.2f}, calculated tolerance={tolerance:.2f}"
        )

        # Now use the calculated tolerance for decimation
        return self._decimate_line_data(data, tolerance=tolerance, max_points=max_points)

    def _get_color_for_unit(self, name: str) -> QColor:
        """Get a consistent color for a geological unit based on its name."""
        if not name:
            return QColor(100, 100, 100)  # Default grey

        # Simple hash to map name to index
        hash_val = sum(ord(c) for c in str(name))
        index = hash_val % len(self.GEOLOGY_COLORS)
        return self.GEOLOGY_COLORS[index]

    def _create_memory_layer(
        self,
        geometry_type: str,
        name: str,
        fields: str | None = None,
        crs: str = "EPSG:4326",
    ) -> tuple[QgsVectorLayer | None, object | None]:
        """Create a memory layer with standard configuration.

        Args:
            geometry_type: "Point", "LineString", "Polygon"
            name: Layer display name
            fields: Optional field definition string (e.g., "field=id:integer")
            crs: CRS identifier (default: EPSG:4326)

        Returns:
            Tuple of (QgsVectorLayer, QgsDataProvider) or (None, None) if failed
        """
        field_def = f"&{fields}" if fields else ""
        uri = f"{geometry_type}?crs={crs}{field_def}"
        layer = QgsVectorLayer(uri, name, "memory")

        if not layer.isValid():
            logger.error(f"Failed to create memory layer: {name}")
            return None, None

        return layer, layer.dataProvider()

    def _create_topo_layer(
        self,
        topo_data: ProfileData,
        vert_exag: float = 1.0,
        max_points: int = 1000,
        use_adaptive_sampling: bool = False,
    ) -> QgsVectorLayer | None:
        """Create temporary layer for topographic profile.

        Args:
            topo_data: List of (distance, elevation) tuples
            vert_exag: Vertical exaggeration factor
            max_points: Max points for LOD optimization (default: 1000)
            use_adaptive_sampling: Whether to use adaptive sampling for decimation.

        Returns:
            QgsVectorLayer with topographic profile
        """
        logger.debug(f"_create_topo_layer called")
        logger.debug(f"  topo_data type: {type(topo_data)}, value: {topo_data}")
        logger.debug(
            f"  bool(topo_data): {bool(topo_data)}, len check: {len(topo_data) if topo_data else 'N/A'}"
        )

        if not topo_data or len(topo_data) < 2:
            logger.debug(f"  Returning None: topo_data is None or has < 2 points")
            return None

        # Apply LOD decimation
        logger.debug(f"  Creating render data from {len(topo_data)} points")
        if use_adaptive_sampling:
            render_data = self._adaptive_sample(topo_data, max_points=max_points)
        else:
            render_data = self._decimate_line_data(topo_data, max_points=max_points)
        logger.debug(f"  After decimation: {len(render_data)} points")

        # Create memory layer using factory
        logger.debug(f"  Creating memory layer...")
        layer, provider = self._create_memory_layer("LineString", "Topography")
        if not layer:
            logger.error("Failed to create memory layer 'Topography'")
            return None

        logger.debug(f"  Memory layer created successfully, adding features...")
        # Create line geometry from points
        points = [QgsPointXY(dist, elev * vert_exag) for dist, elev in render_data]
        line = QgsLineString(points)

        # Add feature
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry(line))
        provider.addFeatures([feat])

        # Apply symbology - blue line, 0.5px width
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
        logger.debug("Created topography layer with %d points", len(render_data))
        return layer

    def _create_geol_layer(
        self, geol_data: GeologyData, vert_exag: float = 1.0, max_points: int = 1000
    ) -> QgsVectorLayer | None:
        """Create temporary layer for geological profile.

        Args:
            geol_data: List of GeologySegment objects
            vert_exag: Vertical exaggeration factor
            max_points: Max points for LOD optimization (default: 1000)

        Returns:
            QgsVectorLayer with geological lines
        """
        if not geol_data:
            return None

        # Create memory layer using factory
        layer, provider = self._create_memory_layer(
            "LineString", "Geology", "field=unit:string"
        )
        if not layer:
            logger.error("Failed to create memory layer 'Geology'")
            return None

        # Collect features from segments
        # Note: Segments are already logically grouped pieces of geometry.
        # However, for coloring/symbology, we might still want to group by unit to assign colors?
        # The existing logic grouped POINTS then made lines.
        # Now we have SEGMENTS which are inherently lines.
        # We can just iterate segments and add them.
        
        # We still need to group to assign colors per unit name though.
        # Let's collect unit names first
        unique_units = set(s.unit_name for s in geol_data)
        
        features = []
        for segment in geol_data:
            if not segment.points or len(segment.points) < 2:
                continue

            # Apply LOD decimation per segment?
            # Or just use the points directly since they are likely already sampled correctly?
            # Existing logic decimated points.
            render_points = self._decimate_line_data(segment.points, max_points=max_points)
            
            # Create geometry
            line_points = [
                QgsPointXY(dist, elev * vert_exag) for dist, elev in render_points
            ]
            line = QgsLineString(line_points)
            
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry(line))
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)

        provider.addFeatures(features)

        # Apply categorized symbology
        categories = []
        for unit_name in unique_units:
            color = self._get_color_for_unit(unit_name)
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

            # Track for legend
            self.active_units[unit_name] = color

        renderer = QgsCategorizedSymbolRenderer("unit", categories)
        layer.setRenderer(renderer)
        layer.updateExtents()
        logger.debug("Created geology layer with %d segments", len(geol_data))
        return layer

    def _create_struct_layer(
        self,
        struct_data: StructureData,
        reference_data: ProfileData,
        vert_exag: float = 1.0,
        dip_line_length: float | None = None,
    ) -> QgsVectorLayer | None:
        """Create temporary layer for structural dips.

        Args:
            struct_data: List of StructureMeasurement objects
            reference_data: List of (distance, elevation) tuples for elevation lookup
            vert_exag: Vertical exaggeration factor
            dip_line_length: Length of dip line in map units (if None, calculates default)

        Returns:
            QgsVectorLayer with structural dip lines
        """
        if not struct_data:
            return None

        # Create memory layer using factory
        layer, provider = self._create_memory_layer("LineString", "Structures")
        if not layer:
            logger.error("Failed to create memory layer 'Structures'")
            return None

        # Calculate line length default if needed
        if dip_line_length is not None and dip_line_length > 0:
            line_length = dip_line_length
        else:
            if reference_data:
                elevs = [e for _, e in reference_data]
                e_range = max(elevs) - min(elevs)
            else:
                e_range = 100  # Default range
            line_length = e_range * 0.1

        # Create dip lines
        features = []
        for m in struct_data:
            # m is StructureMeasurement(distance, elevation, apparent_dip, ...)
            
            # Use pre-calculated elevation if available (which it acts like it is now)
            # But the logic previously interpolated from reference data (topo).
            # StructureService now extracts elevation itself from raster.
            # We should prefer the measurement's elevation if it exists (which it does).
            elev = m.elevation
            dist = m.distance
            app_dip = m.apparent_dip

            # Calculate dip line endpoints
            rad_dip = math.radians(abs(app_dip))
            dx = line_length * math.cos(rad_dip)
            dy = line_length * math.sin(rad_dip)

            # Apply vertical exaggeration to dy
            # dy is vertical component
            
            # Direction
            if app_dip < 0:
                dx = -dx

            # Create line from point downward
            p1 = QgsPointXY(dist, elev * vert_exag)
            p2 = QgsPointXY(dist + dx, (elev - dy) * vert_exag)

            line = QgsLineString([p1, p2])
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry(line))
            features.append(feat)

        provider.addFeatures(features)

        # Apply symbology - red line, 2px width
        symbol = QgsLineSymbol.createSimple(
            {"color": "204,0,0", "width": "0.5", "capstyle": "round"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        layer.updateExtents()
        logger.debug("Created structures layer with %d dips", len(struct_data))
        return layer

    def _interpolate_elevation(
        self, reference_data: ProfileData, target_dist: float
    ) -> float:
        """Interpolate elevation at a given distance."""
        if not reference_data:
            return 0

        # Find bracketing points
        for i in range(len(reference_data) - 1):
            d1, e1 = reference_data[i]
            d2, e2 = reference_data[i + 1]

            if d1 <= target_dist <= d2:
                # Linear interpolation
                if d2 == d1:
                    return e1
                t = (target_dist - d1) / (d2 - d1)
                return e1 + t * (e2 - e1)

        # If outside range, use nearest
        if target_dist < reference_data[0][0]:
            return reference_data[0][1]
        return reference_data[-1][1]

    def _get_nice_interval(self, target_step):
        """Calculate a nice interval for grid lines (1-2-5 sequence).

        Args:
            target_step: The desired step size (e.g. range / 5)

        Returns:
            A 'nice' number close to target_step
        """
        if target_step <= 0:
            return 100.0

        exponent = math.floor(math.log10(target_step))
        fraction = target_step / (10**exponent)

        if fraction < 1.5:
            nice_fraction = 1.0
        elif fraction < 3.5:
            nice_fraction = 2.0
        elif fraction < 7.5:
            nice_fraction = 5.0
        else:
            nice_fraction = 10.0

        return nice_fraction * (10**exponent)

    def _create_axes_layer(self, extent, vert_exag=1.0):
        """Create temporary layer for axes and grid.

        Args:
            extent: QgsRectangle defining the data extent
            vert_exag: Vertical exaggeration factor

        Returns:
            QgsVectorLayer with grid lines and annotations
        """
        if not extent:
            return None

        # Create memory layer
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Axes", "memory")
        provider = layer.dataProvider()

        # Calculate grid intervals
        width = extent.width()
        height = extent.height()

        x_interval = self._get_nice_interval(width / 5)  # Aim for ~5 ticks
        y_interval = self._get_nice_interval((height / vert_exag) / 5)

        # Adjust start points to be multiples of interval
        x_start = math.floor(extent.xMinimum() / x_interval) * x_interval

        y_min_orig = extent.yMinimum() / vert_exag
        y_max_orig = extent.yMaximum() / vert_exag
        y_start = math.floor(y_min_orig / y_interval) * y_interval

        features = []

        # Create vertical grid lines
        x = x_start
        while x <= extent.xMaximum():
            if x >= extent.xMinimum():
                p1 = QgsPointXY(x, extent.yMinimum())
                p2 = QgsPointXY(x, extent.yMaximum())
                line = QgsLineString([p1, p2])
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry(line))
                features.append(feat)
            x += x_interval

        # Create horizontal grid lines
        y = y_start
        while y <= y_max_orig:
            y_draw = y * vert_exag
            if y_draw >= extent.yMinimum():
                p1 = QgsPointXY(extent.xMinimum(), y_draw)
                p2 = QgsPointXY(extent.xMaximum(), y_draw)
                line = QgsLineString([p1, p2])
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry(line))
                features.append(feat)
            y += y_interval

        provider.addFeatures(features)

        # Apply symbology - light grey dashed line
        symbol = QgsLineSymbol.createSimple(
            {"color": "200,200,200", "width": "0.3", "line_style": "dash"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        # Add annotations for labels if canvas is available
        # Note: We are using a separate vector layer for labels (_create_axes_labels_layer)
        # which is more robust than QgsTextAnnotation across QGIS versions.
        # The QgsTextAnnotation code has been removed to avoid compatibility issues.

        return layer

    def _create_axes_labels_layer(self, extent, vert_exag=1.0):
        """Create a point layer for axes labels."""
        if not extent:
            return None

        # Add quadrant field for data-defined placement
        layer = QgsVectorLayer(
            "Point?crs=EPSG:4326&field=label:string&field=quadrant:integer",
            "Axes Labels",
            "memory",
        )
        provider = layer.dataProvider()

        # Calculate grid intervals
        width = extent.width()
        height = extent.height()

        x_interval = self._get_nice_interval(width / 5)
        y_interval = self._get_nice_interval((height / vert_exag) / 5)

        x_start = math.floor(extent.xMinimum() / x_interval) * x_interval

        y_min_orig = extent.yMinimum() / vert_exag
        y_max_orig = extent.yMaximum() / vert_exag
        y_start = math.floor(y_min_orig / y_interval) * y_interval

        features = []

        # X Axis Labels (bottom)
        x = x_start
        while x <= extent.xMaximum():
            if x >= extent.xMinimum():
                feat = QgsFeature(layer.fields())
                feat.setGeometry(
                    QgsGeometry.fromPointXY(QgsPointXY(x, extent.yMinimum()))
                )
                feat.setAttribute("label", f"{x:.0f}")
                feat.setAttribute("quadrant", 7)  # Below
                features.append(feat)
            x += x_interval

        # Y Axis Labels (left)
        y = y_start
        while y <= y_max_orig:
            y_draw = y * vert_exag
            if y_draw >= extent.yMinimum():
                feat = QgsFeature(layer.fields())
                feat.setGeometry(
                    QgsGeometry.fromPointXY(QgsPointXY(extent.xMinimum(), y_draw))
                )
                feat.setAttribute("label", f"{y:.0f}")
                feat.setAttribute("quadrant", 3)  # Left
                features.append(feat)
            y += y_interval

        provider.addFeatures(features)

        # Configure labeling
        settings = QgsPalLayerSettings()
        settings.fieldName = "label"
        settings.placement = (
            QgsPalLayerSettings.Placement.OverPoint
        )  # Allows quadrant usage

        format = QgsTextFormat()
        format.setColor(QColor(0, 0, 0))
        format.setSize(8)
        settings.setFormat(format)

        # Data defined properties for quadrant
        from qgis.core import QgsProperty, QgsPropertyCollection

        props = QgsPropertyCollection()
        props.setProperty(
            QgsPalLayerSettings.Property.OffsetQuad, QgsProperty.fromField("quadrant")
        )
        settings.setDataDefinedProperties(props)

        # Add a small distance offset so they aren't right on top of the line
        settings.dist = 1.0  # mm

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)

        # Invisible symbol for points
        symbol = QgsMarkerSymbol.createSimple({"size": "0", "color": "0,0,0,0"})
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        return layer

    def _create_drillhole_trace_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> QgsVectorLayer | None:
        """Create temporary layer for drillhole traces.
        
        Args:
            drillhole_data: List of (hole_id, traces, segments)
            vert_exag: Vertical exaggeration factor
            
        Returns:
            QgsVectorLayer
        """
        if not drillhole_data:
            return None
            
        layer, provider = self._create_memory_layer("LineString", "Drillhole Traces", "field=hole_id:string")
        if not layer:
            return None
            
        features = []
        for hole_id, trace_points, _ in drillhole_data:
            if not trace_points or len(trace_points) < 2:
                continue
                
            # Create line geometry
            # Apply vertical exaggeration
            render_points = [QgsPointXY(x, y * vert_exag) for x, y in trace_points]
            line = QgsLineString(render_points)
            
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry(line))
            feat.setAttribute("hole_id", hole_id)
            features.append(feat)
            
        provider.addFeatures(features)
        
        # Symbology: Thin grey/black line
        symbol = QgsLineSymbol.createSimple(
            {
                "color": "50,50,50",
                "width": "0.3",
                "capstyle": "round"
            }
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        # Labelling for Hole IDs (at the top/start of the trace)
        settings = QgsPalLayerSettings()
        settings.fieldName = "hole_id"
        settings.placement = QgsPalLayerSettings.Placement.Line
        
        format = QgsTextFormat()
        format.setColor(QColor(0, 0, 0))
        format.setSize(8)
        settings.setFormat(format)
        
        # Offset slightly above/left
        # settings.dist = 1.0
        
        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)
        
        layer.updateExtents()
        return layer

    def _create_drillhole_interval_layer(
        self, drillhole_data: list, vert_exag: float = 1.0
    ) -> QgsVectorLayer | None:
        """Create temporary layer for drillhole intervals.
        
        Args:
            drillhole_data: List of (hole_id, traces, segments)
            vert_exag: Vertical exaggeration factor
            
        Returns:
            QgsVectorLayer
        """
        if not drillhole_data:
            return None
            
        # Collect all segments from all holes
        all_segments = []
        for _, _, segments in drillhole_data:
             if segments:
                 all_segments.extend(segments)
                 
        if not all_segments:
            return None
            
        # Create memory layer
        layer, provider = self._create_memory_layer("LineString", "Drillhole Intervals", "field=unit:string")
        if not layer:
            return None
            
        features = []
        unique_units = set()
        
        for segment in all_segments:
            if not segment.points or len(segment.points) < 2:
                continue
                
            unique_units.add(segment.unit_name)
            
            # Create geometry
            render_points = [QgsPointXY(x, y * vert_exag) for x, y in segment.points]
            line = QgsLineString(render_points)
            
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry(line))
            feat.setAttribute("unit", segment.unit_name)
            features.append(feat)
            
        provider.addFeatures(features)
        
        # Categorized symbology - reuse colors from geology if available
        categories = []
        for unit_name in unique_units:
            # Check if we already assigned a color for this unit in geology service
            # If so, reuse it. If not, generate one.
            if unit_name in self.active_units:
                color = self.active_units[unit_name]
            else:
                color = self._get_color_for_unit(unit_name)
                self.active_units[unit_name] = color # cache it
            
            # Thicker line for intervals
            symbol = QgsLineSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()}",
                    "width": "2.0", # Thicker than traces
                    "capstyle": "flat", # Flat caps for intervals to look like bars
                    "joinstyle": "bevel"
                }
            )
            category = QgsRendererCategory(unit_name, symbol, unit_name)
            categories.append(category)
            
        renderer = QgsCategorizedSymbolRenderer("unit", categories)
        layer.setRenderer(renderer)
        layer.updateExtents()
        return layer

    def render(
        self,
        topo_data: ProfileData,
        geol_data: GeologyData | None = None,
        struct_data: StructureData | None = None,
        vert_exag: float = 1.0,
        dip_line_length: float | None = None,
        max_points: int = 1000,
        preserve_extent: bool = False,
        use_adaptive_sampling: bool = False,
        drillhole_data: list | None = None,
        **kwargs
    ) -> tuple[object | None, list[QgsVectorLayer]]:
        """Render preview with all data layers.

        Args:
            topo_data: List of (dist, elev) tuples for topographic profile
            geol_data: Optional list of (dist, elev, geology_name) tuples
            struct_data: Optional list of (dist, app_dip) tuples
            vert_exag: Vertical exaggeration factor (default 1.0)
            dip_line_length: Optional explicit length for dip lines
            max_points: Max points for LOD optimization (default: 1000)
            preserve_extent: If True, do not reset canvas extent (default: False)
            drillhole_data: Optional list of (hole_id, traces, segments) tuples

        Returns:
            Tuple of (QgsMapCanvas, list of layers) or (None, None) if no data
        """
        # Debug: log input data
        logger.debug(f"render() called with:")
        logger.debug(f"  topo_data: {len(topo_data) if topo_data else 0} points")
        logger.debug(f"  geol_data: {len(geol_data) if geol_data else 0} points")
        logger.debug(f"  struct_data: {len(struct_data) if struct_data else 0} points")
        logger.debug(
            f"  topo_data is None: {topo_data is None}, bool(topo_data): {bool(topo_data)}"
        )

        # Clean up previous layers
        for layer in self.layers:
            if layer:
                try:
                    QgsProject.instance().removeMapLayer(layer.id())
                except Exception as e:
                    logger.debug(f"Could not remove layer {layer.name()}: {e}")
        self.layers = []
        self.active_units = {}  # Reset active units
        self.has_topography = False
        self.has_structures = False

        # Create layers
        logger.debug(
            f"About to create topo_layer, topo_data is None={topo_data is None}"
        )
        topo_layer = (
            self._create_topo_layer(topo_data, vert_exag, max_points, use_adaptive_sampling)
            if topo_data
            else None
        )
        logger.debug(f"topo_layer created: {topo_layer is not None}")
        if topo_layer:
            self.has_topography = True

        geol_layer = (
            self._create_geol_layer(geol_data, vert_exag, max_points)
            if geol_data
            else None
        )

        # For structural layer, use topo or geol as reference
        reference_data = (
            topo_data
            if topo_data
            else ([(d, e) for d, e, _ in geol_data] if geol_data else None)
        )
        struct_layer = (
            self._create_struct_layer(
                struct_data, reference_data, vert_exag, dip_line_length
            )
            if struct_data
            else None
        )
        if struct_layer:
            self.has_structures = True

        # Render Drillholes
        # drillhole_data is passed as argument now
        drillhole_layers = []
        if drillhole_data:
            # 1. Traces
            trace_layer = self._create_drillhole_trace_layer(drillhole_data, vert_exag)
            if trace_layer:
                drillhole_layers.append(trace_layer)
            
            # 2. Intervals
            interval_layer = self._create_drillhole_interval_layer(drillhole_data, vert_exag)
            if interval_layer:
                drillhole_layers.append(interval_layer)
        
        # Collect valid layers
        data_layers = [
            layer
            for layer in [struct_layer, geol_layer, topo_layer] + drillhole_layers
            if layer is not None
        ]

        logger.debug(
            f"Layers created: topo={topo_layer is not None}, geol={geol_layer is not None}, struct={struct_layer is not None}, dh={len(drillhole_layers)}"
        )
        logger.debug(f"Valid data_layers count: {len(data_layers)}")

        if not data_layers:
            logger.warning("No valid layers to render")
            return None, None

        # Calculate extent from data layers
        extent = None
        for layer in data_layers:
            layer_extent = layer.extent()
            if extent is None:
                extent = layer_extent
            else:
                extent.combineExtentWith(layer_extent)

        # Create axes layers based on data extent
        axes_layer = self._create_axes_layer(extent, vert_exag)
        labels_layer = self._create_axes_labels_layer(extent, vert_exag)

        # Combine all layers (labels on top, then data, then grid)
        layers = [labels_layer, *data_layers, axes_layer]
        layers = [layer for layer in layers if layer is not None]

        self.layers = layers

        # Vertical exaggeration is now applied to geometries, so we don't need to modify extent
        # except for padding

        # Add 10% padding
        if extent:
            extent.scale(1.1)

        # Configure canvas if provided
        if self.canvas:
            self.canvas.setLayers(layers)
            # Canvas will automatically use CRS from the layers
            if not preserve_extent:
                self.canvas.setExtent(extent)
            self.canvas.refresh()
            logger.debug("Canvas configured with %d layers", len(layers))

        return self.canvas, layers

    def export_to_image(
        self,
        layers: list[QgsVectorLayer],
        extent,
        width: int,
        height: int,
        output_path,
        dpi: int = 300,
    ) -> bool:
        """Export preview to image file using QgsMapRendererCustomPainterJob.

        Args:
            layers: List of QgsVectorLayer to render
            extent: QgsRectangle defining the area to render
            width: Output width in pixels
            height: Output height in pixels
            output_path: Path to save the image
            dpi: DPI for output (default 300)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create map settings
            settings = QgsMapSettings()
            settings.setLayers(layers)
            # CRS is automatically derived from the layers
            settings.setExtent(extent)
            settings.setOutputSize(QSize(width, height))
            settings.setOutputDpi(dpi)

            # Create image
            image = QImage(QSize(width, height), QImage.Format_ARGB32)
            image.fill(QColor(255, 255, 255))  # White background

            # Render
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)

            job = QgsMapRendererCustomPainterJob(settings, painter)
            job.start()
            job.waitForFinished()

            # Draw legend
            self.draw_legend(painter, QRectF(0, 0, width, height))

            painter.end()

            # Save
            success = image.save(output_path)
            if success:
                logger.info("Exported preview to %s", output_path)
            else:
                logger.error("Failed to save image to %s", output_path)

            return success

        except Exception as e:
            logger.exception("Error exporting preview: %s", e)
            return False

    def draw_legend(self, painter, rect):
        """Draw legend on the given painter within the rect.

        Args:
            painter: QPainter instance
            rect: QRectF defining the drawing area
        """
        # Check if we have anything to show
        if (
            not self.active_units
            and not self.has_topography
            and not self.has_structures
        ):
            return

        # Legend configuration - compact size
        padding = 6
        item_height = 16
        symbol_size = 10
        line_width = 2
        font_size = 8

        # Setup painter
        painter.save()
        font = QFont("Arial", font_size)
        painter.setFont(font)

        # Calculate legend size
        fm = painter.fontMetrics()
        max_width = 0

        # Check all items for width
        if self.has_topography:
            max_width = max(max_width, fm.boundingRect("Topography").width())
        if self.has_structures:
            max_width = max(max_width, fm.boundingRect("Structures").width())
        for name in self.active_units:
            width = fm.boundingRect(name).width()
            max_width = max(max_width, width)

        # Count total items
        total_items = len(self.active_units)
        if self.has_topography:
            total_items += 1
        if self.has_structures:
            total_items += 1

        legend_width = max_width + symbol_size + padding * 3
        legend_height = total_items * item_height + padding * 2

        # Position: Top Right with margin
        margin = 20
        x = rect.width() - legend_width - margin
        y = margin

        # Draw background
        bg_color = QColor(255, 255, 255, 200)  # Semi-transparent white
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(x, y, legend_width, legend_height))

        # Draw border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(QRectF(x, y, legend_width, legend_height))

        # Draw items
        current_y = y + padding

        # Draw topography if present
        if self.has_topography:
            painter.setPen(QPen(QColor(0, 102, 204), line_width))  # Blue
            painter.drawLine(
                int(x + padding),
                int(current_y + item_height / 2),
                int(x + padding + symbol_size),
                int(current_y + item_height / 2),
            )
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(
                x + padding * 2 + symbol_size, current_y, max_width, item_height
            )
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "Topography")
            current_y += item_height

        # Draw structures if present
        if self.has_structures:
            painter.setPen(QPen(QColor(204, 0, 0), line_width))  # Red
            painter.drawLine(
                int(x + padding),
                int(current_y + item_height / 2),
                int(x + padding + symbol_size),
                int(current_y + item_height / 2),
            )
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(
                x + padding * 2 + symbol_size, current_y, max_width, item_height
            )
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "Structures")
            current_y += item_height

        # Draw geological units
        for name, color in self.active_units.items():
            # Draw symbol (rectangle)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            symbol_rect = QRectF(
                x + padding,
                current_y + (item_height - symbol_size) / 2,
                symbol_size,
                symbol_size,
            )
            painter.drawRect(symbol_rect)

            # Draw text
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(
                x + padding * 2 + symbol_size, current_y, max_width, item_height
            )
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, name)

            current_y += item_height

        painter.restore()
