# -*- coding: utf-8 -*-
"""
Preview Renderer Module

Handles rendering of interactive previews with topography, geology, and structural data.
Includes coordinate axes, grid, and multi-layer visualization.
"""

import math
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QPen, QColor, QBrush
from qgis.PyQt.QtWidgets import QGraphicsScene

from . import si_core_utils as scu
from .logger_config import get_logger

logger = get_logger(__name__)


class PreviewRenderer:
    """Renders interactive preview with multiple data layers."""
    
    # Color palette for geological units
    # Color palette for geological units (expanded and refined)
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
    
    def _get_color_for_unit(self, name):
        """Get a consistent color for a geological unit based on its name.
        
        Uses a hash of the name to select a color from the palette, ensuring
        that the same unit always gets the same color.
        """
        if not name:
            return QColor(100, 100, 100)  # Default grey for unnamed
            
        # Simple hash to map name to index
        hash_val = sum(ord(c) for c in name)
        index = hash_val % len(self.GEOLOGY_COLORS)
        return self.GEOLOGY_COLORS[index]
    
    def __init__(self, view_width=600, view_height=400, margin=60):
        """Initialize preview renderer.
        
        Args:
            view_width: Width of the preview canvas in pixels
            view_height: Height of the preview canvas in pixels
            margin: Margin for axes and labels in pixels
        """
        self.view_w = view_width
        self.view_h = view_height
        self.margin = margin
    
    def render(self, topo_data, geol_data=None, struct_data=None, vert_exag=1.0):
        """Render preview with all data layers.
        
        Args:
            topo_data: List of (dist, elev) tuples for topographic profile
            geol_data: Optional list of (dist, elev, geology_name) tuples
            struct_data: Optional list of (dist, app_dip) tuples
            vert_exag: Vertical exaggeration factor (default 1.0 = no exaggeration)
            
        Returns:
            QGraphicsScene with rendered preview
        """
        scene = QGraphicsScene()

        # Check if we have any data to display
        has_any_data = False
        if topo_data and len(topo_data) >= 2:
            has_any_data = True
        if geol_data and len(geol_data) >= 2:
            has_any_data = True
        if struct_data and len(struct_data) >= 1:
            has_any_data = True
        
        if not has_any_data:
            scene.addText("No data to preview.\nPlease ensure at least one data type is selected and has valid data.")
            return scene

        # Determine which data to use for bounds calculation
        primary_data = None
        
        # Try geological data first
        if geol_data and len(geol_data) >= 2:
            # Convert geological data to (dist, elev) tuples for bounds calculation
            primary_data = [(d, e) for d, e, _ in geol_data]
        # Then try topographic data
        elif topo_data and len(topo_data) >= 2:
            primary_data = topo_data
        # If only structural data, create synthetic bounds
        elif struct_data and len(struct_data) >= 1:
            # Get distance range from structural data
            dists = [d for d, _ in struct_data]
            min_d, max_d = min(dists), max(dists)
            # Create synthetic elevation range (arbitrary but reasonable)
            # Use a range that will show the dip lines nicely
            mid_elev = 1000  # Arbitrary middle elevation
            elev_range = (max_d - min_d) * 0.3  # 30% of distance range
            # Create two synthetic points to define bounds
            primary_data = [
                (min_d, mid_elev - elev_range/2),
                (max_d, mid_elev + elev_range/2)
            ]
        
        if not primary_data:
            scene.addText("Insufficient data for preview.")
            return scene

        # Calculate bounds from all available data
        bounds = scu.calculate_bounds(primary_data, geol_data if geol_data else None)
        
        # Create coordinate transformation with vertical exaggeration
        transform = scu.create_coordinate_transform(bounds, self.view_w, self.view_h, self.margin, vert_exag)
        
        # Draw grid and axes first (background)
        self._draw_grid(scene, bounds, transform)
        self._draw_axes(scene, bounds, transform)
        
        # Track what data is being displayed
        has_topo = False
        has_geol = False
        has_struct = False
        
        # Draw topographic layer if available
        if topo_data and len(topo_data) >= 2:
            self._draw_topo_layer(scene, topo_data, transform)
            has_topo = True
        
        if geol_data and len(geol_data) > 0:
            logger.debug("Drawing %d geological points", len(geol_data))
            self._draw_geol_layer(scene, geol_data, transform)
            has_geol = True
        else:
            logger.debug("No geological data to draw")
        
        if struct_data and len(struct_data) > 0:
            logger.debug("Drawing %d structural points", len(struct_data))
            # For structural data, we need reference data for elevation
            # Use topographic or geological data if available, otherwise use synthetic data
            if topo_data and len(topo_data) >= 2:
                reference_data = topo_data
            elif geol_data and len(geol_data) >= 2:
                reference_data = [(d, e) for d, e, _ in geol_data]
            else:
                # Use synthetic data (flat line at middle elevation)
                dists = [d for d, _ in struct_data]
                min_d, max_d = min(dists), max(dists)
                mid_elev = (bounds['min_e'] + bounds['max_e']) / 2
                reference_data = [(min_d, mid_elev), (max_d, mid_elev)]
            
            self._draw_struct_layer(scene, struct_data, reference_data, transform, bounds)
            has_struct = True
        else:
            logger.debug("No structural data to draw")
        
        # Draw legend
        if has_geol or has_struct:
            logger.debug("Drawing legend (geol=%s, struct=%s)", has_geol, has_struct)
            self._draw_legend(scene, geol_data, struct_data, bounds, transform)
        
        # Add informative message if only topography is shown
        if has_topo and not has_geol and not has_struct:
            info_text = scene.addText("Only topographic profile is displayed.\n"
                                     "Geological and structural data may be missing or\n"
                                     "not intersecting with the cross-section line.")
            info_text.setPos(10, self.view_h - 80)
            info_text.setScale(0.7)
            info_text.setDefaultTextColor(QColor(200, 100, 0))  # Orange color
        
        # Add note if only structural data is shown
        if has_struct and not has_topo and not has_geol:
            info_text = scene.addText("Only structural data is displayed.\n"
                                     "Elevations are synthetic (not from topography/geology).")
            info_text.setPos(10, self.view_h - 60)
            info_text.setScale(0.7)
            info_text.setDefaultTextColor(QColor(100, 100, 200))  # Blue color
        
        # Set explicit scene rect to ensure proper bounds for export
        # This is especially important when only topography is displayed
        items_rect = scene.itemsBoundingRect()
        logger.debug("Scene has %d items", len(scene.items()))
        logger.debug("Items bounding rect: x=%f, y=%f, w=%f, h=%f", 
                    items_rect.x(), items_rect.y(), items_rect.width(), items_rect.height())
        scene.setSceneRect(items_rect)
        logger.debug("Scene rect set to items bounding rect")
        
        return scene
    

    

    
    def _draw_grid(self, scene, bounds, transform):
        """Draw background grid."""
        pen = QPen(QColor(220, 220, 220))
        pen.setStyle(Qt.DotLine)
        
        # Vertical grid lines
        d_range = bounds['max_d'] - bounds['min_d']
        d_interval = scu.calculate_interval(d_range)
        
        d = math.ceil(bounds['min_d'] / d_interval) * d_interval
        while d <= bounds['max_d']:
            x1, y1 = transform(d, bounds['min_e'])
            x2, y2 = transform(d, bounds['max_e'])
            scene.addLine(x1, y1, x1, y2, pen)
            d += d_interval
        
        # Horizontal grid lines
        e_range = bounds['max_e'] - bounds['min_e']
        e_interval = scu.calculate_interval(e_range)
        
        e = math.ceil(bounds['min_e'] / e_interval) * e_interval
        while e <= bounds['max_e']:
            x1, y1 = transform(bounds['min_d'], e)
            x2, y2 = transform(bounds['max_d'], e)
            scene.addLine(x1, y1, x2, y1, pen)
            e += e_interval
    
    def _draw_axes(self, scene, bounds, transform):
        """Draw coordinate axes with labels."""
        pen = QPen(Qt.black)
        pen.setWidth(2)
        
        # X axis
        x1, y1 = transform(bounds['min_d'], bounds['min_e'])
        x2, y2 = transform(bounds['max_d'], bounds['min_e'])
        scene.addLine(x1, y1, x2, y1, pen)
        
        # Y axis (Left)
        x1, y1 = transform(bounds['min_d'], bounds['min_e'])
        x2, y2 = transform(bounds['min_d'], bounds['max_e'])
        scene.addLine(x1, y1, x1, y2, pen)
        
        # X axis (Top)
        x1, y1 = transform(bounds['min_d'], bounds['max_e'])
        x2, y2 = transform(bounds['max_d'], bounds['max_e'])
        scene.addLine(x1, y1, x2, y1, pen)
        
        # Y axis (Right)
        x1, y1 = transform(bounds['max_d'], bounds['min_e'])
        x2, y2 = transform(bounds['max_d'], bounds['max_e'])
        scene.addLine(x1, y1, x1, y2, pen)
        
        # X axis labels
        d_range = bounds['max_d'] - bounds['min_d']
        d_interval = scu.calculate_interval(d_range)
        
        d = math.ceil(bounds['min_d'] / d_interval) * d_interval
        while d <= bounds['max_d']:
            x, y = transform(d, bounds['min_e'])
            text = scene.addText(f"{int(d)} m")
            text.setPos(x - 15, y + 5)
            text.setScale(0.7)
            d += d_interval
        
        # Y axis labels
        e_range = bounds['max_e'] - bounds['min_e']
        e_interval = scu.calculate_interval(e_range)
        
        e = math.ceil(bounds['min_e'] / e_interval) * e_interval
        while e <= bounds['max_e']:
            x, y = transform(bounds['min_d'], e)
            text = scene.addText(f"{int(e)} m")
            text.setPos(x - 50, y - 10)
            text.setScale(0.7)
            e += e_interval
        
        # Axis titles - position dynamically based on actual content
        # X axis title at bottom center of the actual data area
        center_x, bottom_y = transform((bounds['min_d'] + bounds['max_d']) / 2, bounds['min_e'])
        title_x = scene.addText("Distance (m)")
        title_x.setPos(center_x - 40, bottom_y + 10)
        title_x.setScale(0.8)
        
        # Y axis title at top left of the actual data area
        left_x, top_y = transform(bounds['min_d'], bounds['max_e'])
        title_y = scene.addText("Elevation (m)")
        title_y.setPos(left_x - 55, top_y - 25)
        title_y.setScale(0.8)
    
    def _draw_topo_layer(self, scene, points, transform):
        """Draw topographic profile."""
        logger.debug("Drawing topography with %d points", len(points))
        pen = QPen(QColor(0, 102, 204))  # Blue
        pen.setWidth(2)
        
        lines_added = 0
        for i in range(len(points) - 1):
            x1, y1 = transform(points[i][0], points[i][1])
            x2, y2 = transform(points[i + 1][0], points[i + 1][1])
            line_item = scene.addLine(x1, y1, x2, y2, pen)
            lines_added += 1
            if i == 0:
                logger.debug("First topo line: (%f, %f) -> (%f, %f)", x1, y1, x2, y2)
        
        logger.debug("Added %d topography lines to scene", lines_added)
    
    def _draw_geol_layer(self, scene, geol_data, transform):
        """Draw geological profile with different colors per unit."""
        # Group by geology name
        geol_groups = {}
        for dist, elev, name in geol_data:
            if name not in geol_groups:
                geol_groups[name] = []
            geol_groups[name].append((dist, elev))
        
        for name, points in geol_groups.items():
            color = self._get_color_for_unit(name)
            pen = QPen(color)
            pen.setWidth(3)
            
            for i in range(len(points) - 1):
                x1, y1 = transform(points[i][0], points[i][1])
                x2, y2 = transform(points[i + 1][0], points[i + 1][1])
                scene.addLine(x1, y1, x2, y2, pen)
    
    def _draw_struct_layer(self, scene, struct_data, topo_data, transform, bounds):
        """Draw structural dip lines."""
        pen = QPen(QColor(204, 0, 0))  # Red
        pen.setWidth(2)
        
        # Calculate line length based on view scale
        e_range = bounds['max_e'] - bounds['min_e']
        line_length = e_range * 0.1  # 10% of elevation range
        
        for dist, app_dip in struct_data:
            # Assume elevation at ground level (would need actual elevation)
            # For now, use middle of elevation range
            elev = scu.interpolate_elevation(topo_data, dist)
            
            rad_dip = math.radians(app_dip)
            dx = line_length * math.cos(abs(rad_dip))
            dy = -line_length * math.sin(abs(rad_dip))
            
            if app_dip < 0:
                dx = -dx
            
            x1, y1 = transform(dist, elev)
            x2, y2 = transform(dist + dx, elev + dy)
            scene.addLine(x1, y1, x2, y2, pen)
    
    def _draw_legend(self, scene, geol_data, struct_data, bounds, transform):
        """Draw legend for geological units and structures.
        
        Args:
            scene: QGraphicsScene to draw on
            geol_data: Geological data
            struct_data: Structural data
            bounds: Data bounds
            transform: Coordinate transform function
        """
        legend_x = self.view_w - 150
        legend_y = 20
        
        # Background
        scene.addRect(legend_x - 10, legend_y - 10, 140, 200, 
                     QPen(Qt.black), QBrush(QColor(255, 255, 255, 200)))
        
        current_y = legend_y
        
        # Title
        title = scene.addText("Legend")
        title.setPos(legend_x, current_y)
        title.setDefaultTextColor(Qt.black)
        current_y += 25
        
        # Topography
        scene.addLine(legend_x, current_y + 10, legend_x + 20, current_y + 10, 
                     QPen(QColor(0, 102, 204), 2))
        text = scene.addText("Topography")
        text.setPos(legend_x + 25, current_y)
        text.setScale(0.8)
        current_y += 20
        
        # Geology
        if geol_data:
            geol_names = sorted(list(set(d[2] for d in geol_data)))
            for name in geol_names:
                color = self._get_color_for_unit(name)
                scene.addLine(legend_x, current_y + 10, legend_x + 20, current_y + 10, 
                             QPen(color, 3))
                text = scene.addText(str(name))
                text.setPos(legend_x + 25, current_y)
                text.setScale(0.8)
                current_y += 20
                
        # Structure
        if struct_data:
            scene.addLine(legend_x, current_y + 10, legend_x + 20, current_y + 10, 
                         QPen(QColor(204, 0, 0), 2))
            text = scene.addText("Structure")
            text.setPos(legend_x + 25, current_y)
            text.setScale(0.8)
            current_y += 20
