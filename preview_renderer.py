# -*- coding: utf-8 -*-
"""
Preview Renderer Module (PyQGIS Native)

Handles rendering of interactive previews using native QGIS resources:
- QgsMapCanvas for rendering
- Temporary memory layers for data
- Native QGIS symbology
"""

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsLineString,
    QgsProject,
    QgsSymbol,
    QgsSingleSymbolRenderer,
    QgsCategorizedSymbolRenderer,
    QgsRendererCategory,
    QgsMarkerSymbol,
    QgsLineSymbol,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsMapSettings,
    QgsMapRendererCustomPainterJob,
)
from qgis.PyQt.QtCore import QSize, QSizeF
from qgis.PyQt.QtGui import QColor, QImage, QPainter

from .logger_config import get_logger

logger = get_logger(__name__)


class PreviewRenderer:
    """Renders interactive preview using native PyQGIS resources."""
    
    # Color palette for geological units
    GEOLOGY_COLORS = [
        QColor(231, 76, 60),    # Red
        QColor(52, 152, 219),   # Blue
        QColor(46, 204, 113),   # Green
        QColor(155, 89, 182),   # Purple
        QColor(241, 196, 15),   # Yellow
        QColor(230, 126, 34),   # Orange
        QColor(26, 188, 156),   # Turquoise
        QColor(52, 73, 94),     # Dark Blue/Grey
        QColor(149, 165, 166),  # Grey
        QColor(211, 84, 0),     # Pumpkin
        QColor(192, 57, 43),    # Dark Red
        QColor(127, 140, 141),  # Dark Grey
        QColor(142, 68, 173),   # Wisteria
        QColor(41, 128, 185),   # Belize Hole
        QColor(39, 174, 96),    # Nephritis
        QColor(22, 160, 133),   # Green Sea
    ]
    
    def __init__(self, canvas=None):
        """Initialize preview renderer.
        
        Args:
            canvas: QgsMapCanvas instance (optional, will be created if not provided)
        """
        self.canvas = canvas
        self.layers = []  # Track created layers for cleanup
    
    def _get_color_for_unit(self, name):
        """Get a consistent color for a geological unit based on its name."""
        if not name:
            return QColor(100, 100, 100)  # Default grey
        
        # Simple hash to map name to index
        hash_val = sum(ord(c) for c in str(name))
        index = hash_val % len(self.GEOLOGY_COLORS)
        return self.GEOLOGY_COLORS[index]
    
    def _create_topo_layer(self, topo_data):
        """Create temporary layer for topographic profile.
        
        Args:
            topo_data: List of (distance, elevation) tuples
            
        Returns:
            QgsVectorLayer with topographic profile
        """
        if not topo_data or len(topo_data) < 2:
            return None
        
        # Create memory layer
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Topography", "memory")
        provider = layer.dataProvider()
        
        # Create line geometry from points
        points = [QgsPointXY(dist, elev) for dist, elev in topo_data]
        line = QgsLineString(points)
        
        # Add feature
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry(line))
        provider.addFeatures([feat])
        
        # Apply symbology - blue line, 2px width
        symbol = QgsLineSymbol.createSimple({
            'color': '0,102,204',
            'width': '0.5',
            'capstyle': 'round',
            'joinstyle': 'round'
        })
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        layer.updateExtents()
        logger.debug(f"Created topography layer with {len(topo_data)} points")
        return layer
    
    def _create_geol_layer(self, geol_data):
        """Create temporary layer for geological profile.
        
        Args:
            geol_data: List of (distance, elevation, unit_name) tuples
            
        Returns:
            QgsVectorLayer with geological profile
        """
        if not geol_data or len(geol_data) < 2:
            return None
        
        # Create memory layer with attributes
        layer = QgsVectorLayer(
            "LineString?crs=EPSG:4326&field=unit:string",
            "Geology",
            "memory"
        )
        provider = layer.dataProvider()
        
        # Group by geological unit
        geol_groups = {}
        for dist, elev, name in geol_data:
            if name not in geol_groups:
                geol_groups[name] = []
            geol_groups[name].append((dist, elev))
        
        # Create features for each unit
        features = []
        for unit_name, points in geol_groups.items():
            if len(points) < 2:
                continue
            
            # Create line geometry
            line_points = [QgsPointXY(dist, elev) for dist, elev in points]
            line = QgsLineString(line_points)
            
            # Create feature with attributes
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry(line))
            feat.setAttribute('unit', str(unit_name))
            features.append(feat)
        
        provider.addFeatures(features)
        
        # Apply categorized symbology
        categories = []
        for unit_name in geol_groups.keys():
            color = self._get_color_for_unit(unit_name)
            symbol = QgsLineSymbol.createSimple({
                'color': f'{color.red()},{color.green()},{color.blue()}',
                'width': '0.7',
                'capstyle': 'round',
                'joinstyle': 'round'
            })
            category = QgsRendererCategory(str(unit_name), symbol, str(unit_name))
            categories.append(category)
        
        renderer = QgsCategorizedSymbolRenderer('unit', categories)
        layer.setRenderer(renderer)
        
        layer.updateExtents()
        logger.debug(f"Created geology layer with {len(geol_groups)} units")
        return layer
    
    def _create_struct_layer(self, struct_data, reference_data):
        """Create temporary layer for structural dips.
        
        Args:
            struct_data: List of (distance, apparent_dip) tuples
            reference_data: List of (distance, elevation) tuples for elevation lookup
            
        Returns:
            QgsVectorLayer with structural dip lines
        """
        if not struct_data or len(struct_data) < 1:
            return None
        
        # Create memory layer
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Structures", "memory")
        provider = layer.dataProvider()
        
        # Calculate extent for line length
        if reference_data:
            elevs = [e for _, e in reference_data]
            e_range = max(elevs) - min(elevs)
        else:
            e_range = 100  # Default range
        
        line_length = e_range * 0.1  # 10% of elevation range
        
        # Create dip lines
        features = []
        for dist, app_dip in struct_data:
            # Interpolate elevation from reference data
            if reference_data:
                elev = self._interpolate_elevation(reference_data, dist)
            else:
                elev = 0
            
            # Calculate dip line endpoints
            import math
            rad_dip = math.radians(abs(app_dip))
            dx = line_length * math.cos(rad_dip)
            dy = -line_length * math.sin(rad_dip)
            
            if app_dip < 0:
                dx = -dx
            
            # Create line geometry
            p1 = QgsPointXY(dist, elev)
            p2 = QgsPointXY(dist + dx, elev + dy)
            line = QgsLineString([p1, p2])
            
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry(line))
            features.append(feat)
        
        provider.addFeatures(features)
        
        # Apply symbology - red line, 2px width
        symbol = QgsLineSymbol.createSimple({
            'color': '204,0,0',
            'width': '0.5',
            'capstyle': 'round'
        })
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        layer.updateExtents()
        logger.debug(f"Created structures layer with {len(struct_data)} dips")
        return layer
    
    def _interpolate_elevation(self, reference_data, target_dist):
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
    
    def render(self, topo_data, geol_data=None, struct_data=None, vert_exag=1.0):
        """Render preview with all data layers.
        
        Args:
            topo_data: List of (dist, elev) tuples for topographic profile
            geol_data: Optional list of (dist, elev, geology_name) tuples
            struct_data: Optional list of (dist, app_dip) tuples
            vert_exag: Vertical exaggeration factor (default 1.0)
            
        Returns:
            Tuple of (QgsMapCanvas, list of layers) or (None, None) if no data
        """
        # Clean up previous layers
        for layer in self.layers:
            if layer:
                QgsProject.instance().removeMapLayer(layer.id())
        self.layers = []
        
        # Create layers
        topo_layer = self._create_topo_layer(topo_data) if topo_data else None
        geol_layer = self._create_geol_layer(geol_data) if geol_data else None
        
        # For structural layer, use topo or geol as reference
        reference_data = topo_data if topo_data else (
            [(d, e) for d, e, _ in geol_data] if geol_data else None
        )
        struct_layer = self._create_struct_layer(struct_data, reference_data) if struct_data else None
        
        # Collect valid layers
        layers = [l for l in [struct_layer, geol_layer, topo_layer] if l is not None]
        
        if not layers:
            logger.warning("No valid layers to render")
            return None, None
        
        self.layers = layers
        
        # Calculate combined extent with vertical exaggeration
        extent = None
        for layer in layers:
            layer_extent = layer.extent()
            if extent is None:
                extent = layer_extent
            else:
                extent.combineExtentWith(layer_extent)
        
        # Apply vertical exaggeration to extent
        if extent and vert_exag != 1.0:
            center_y = (extent.yMinimum() + extent.yMaximum()) / 2
            height = extent.height()
            new_height = height * vert_exag
            extent.setYMinimum(center_y - new_height / 2)
            extent.setYMaximum(center_y + new_height / 2)
        
        # Add 10% padding
        if extent:
            extent.scale(1.1)
        
        # Configure canvas if provided
        if self.canvas:
            self.canvas.setLayers(layers)
            self.canvas.setExtent(extent)
            self.canvas.refresh()
            logger.debug(f"Canvas configured with {len(layers)} layers")
        
        return self.canvas, layers
    
    def export_to_image(self, layers, extent, width, height, output_path, dpi=300):
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
            
            painter.end()
            
            # Save
            success = image.save(output_path)
            if success:
                logger.info(f"Exported preview to {output_path}")
            else:
                logger.error(f"Failed to save image to {output_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error exporting preview: {e}")
            return False
