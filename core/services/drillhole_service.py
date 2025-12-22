"""Drillhole Data Processing Service.

Service for processing and projecting drillhole data (collars, surveys, intervals).
"""
from typing import List, Tuple, Dict, Any, Optional
from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsPointXY,
    QgsDistanceArea,
    QgsRasterLayer,
    QgsRaster
)

from sec_interp.core import utils as scu
from sec_interp.core.types import GeologySegment
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)



class DrillholeService:
    """Service for processing drillhole data."""

    def project_collars(
        self,
        collar_layer: QgsVectorLayer,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        dem_layer: Optional[QgsRasterLayer],
    ) -> List[Tuple[Any, float, float, float, float]]:
        """Project collar points onto section line.

        Projects drillhole collars within a specified buffer from the section line
        onto that line, calculating their distance along the section and elevation.

        Args:
            collar_layer: The QGIS vector layer containing drillhole collars.
            line_geom: The geometry of the cross-section line.
            line_start: The starting point of the cross-section line.
            distance_area: The QGS distance calculation object.
            buffer_width: Maximum perpendicular distance from the line to include collars.
            collar_id_field: The attribute field name for the drillhole ID.
            use_geometry: If True, use layer geometry; otherwise use coordinate fields.
            collar_x_field: The attribute field name for X coordinates.
            collar_y_field: The attribute field name for Y coordinates.
            collar_z_field: The attribute field name for elevation (Z).
            collar_depth_field: The attribute field name for total depth.
            dem_layer: Digital Elevation Model layer for elevation fallback if Z is missing.

        Returns:
            A list of tuples: (hole_id, dist_along, elevation, offset, depth)
                - hole_id (Any): The unique identifier for the drillhole.
                - dist_along (float): Distance from the start of the section line.
                - elevation (float): Elevation (Z) of the collar.
                - offset (float): Perpendicular distance from the section line.
                - depth (float): Total depth of the drillhole.
        """
        projected_collars = []

        logger.info(f"DrillholeService.project_collars START")
        logger.info(f"  - Buffer: {buffer_width}")
        logger.info(f"  - Use Geometry: {use_geometry}")
        logger.info(f"  - ID Field: {collar_id_field}")

        feature_count = collar_layer.featureCount()
        logger.info(f"  - Processing {feature_count} collar features...")

        for collar_feat in collar_layer.getFeatures():
            # Get Coordinates
            x, y = 0.0, 0.0
            hole_id = collar_feat[collar_id_field]

            if use_geometry:
                collar_geom = collar_feat.geometry()
                if not collar_geom:
                    continue
                point = collar_geom.asPoint()
                x, y = point.x(), point.y()
            else:
                try:
                    x = float(collar_feat[collar_x_field])
                    y = float(collar_feat[collar_y_field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid X/Y for collar {hole_id}")
                    continue

            if x == 0.0 and y == 0.0:
                logger.warning(f"Collar {hole_id} has null coordinates (0,0)")
                continue

            # Get Elevation (Z)
            z = 0.0
            if collar_z_field:
                try:
                    z = float(collar_feat[collar_z_field])
                except (ValueError, TypeError):
                    pass

            # If Z is missing/zero, sample from DEM
            if z == 0.0 and dem_layer:
                ident = dem_layer.dataProvider().identify(
                    QgsPointXY(x, y), QgsRaster.IdentifyFormatValue
                )
                if ident.isValid():
                    val = ident.results().get(1)  # Band 1
                    if val is not None:
                        z = val

            # Get Total Depth
            depth = 0.0
            if collar_depth_field:
                try:
                    depth = float(collar_feat[collar_depth_field])
                except (ValueError, TypeError):
                    pass

            # Project to section line
            collar_point = QgsPointXY(x, y)
            collar_geom_pt = QgsGeometry.fromPointXY(collar_point)

            # Find nearest point on section line
            nearest_point = line_geom.nearestPoint(collar_geom_pt)
            nearest_pt_xy = nearest_point.asPoint()

            # Calculate distance along section
            dist_along = distance_area.measureLine(line_start, nearest_pt_xy)

            # Calculate offset (perpendicular distance)
            offset = distance_area.measureLine(collar_point, nearest_pt_xy)

            # Check if within buffer
            if offset <= buffer_width:
                logger.debug(
                    f"Collar {hole_id}: dist={dist_along:.2f}, offset={offset:.2f} [IN]"
                )
                projected_collars.append((hole_id, dist_along, z, offset, depth))
            else:
                 logger.debug(
                    f"Collar {hole_id}: dist={dist_along:.2f}, offset={offset:.2f} [OUT]"
                )

        logger.info(f"DrillholeService.project_collars END: Found {len(projected_collars)} collars within buffer.")
        return projected_collars

    def process_intervals(
        self,
        collar_points: List[Tuple],
        collar_layer: QgsVectorLayer,
        survey_layer: QgsVectorLayer,
        interval_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: Dict[str, str],
        interval_fields: Dict[str, str],
    ) -> Tuple[List[GeologySegment], List[Tuple[Any, List[Tuple[float, float]], List[GeologySegment]]]]:
        """Process drillhole interval data and project onto the section.

        Calculates trajectories for all collars within the buffer and interpolates
        geological intervals along those trajectories.

        Args:
            collar_points: List of projected collars from `project_collars`.
            collar_layer: Original collar vector layer.
            survey_layer: Survey data vector layer (depth, azimuth, inclination).
            interval_layer: Geological interval data vector layer.
            collar_id_field: Attribute field name for drillhole ID.
            use_geometry: If True, use layer geometry for coordinates.
            collar_x_field: Attribute field name for X coordinates.
            collar_y_field: Attribute field name for Y coordinates.
            line_geom: Geometry of the cross-section line.
            line_start: Starting point of the cross-section line.
            distance_area: QGS distance calculation object.
            buffer_width: Maximum perpendicular distance to include intervals.
            section_azimuth: The azimuth of the cross-section line.
            survey_fields: Dictionary mapping standard survey fields to layer fields.
                Required keys: 'id', 'depth', 'azim', 'incl'.
            interval_fields: Dictionary mapping standard interval fields to layer fields.
                Required keys: 'id', 'from', 'to', 'lith'.

        Returns:
            A tuple containing (geology_segments, drillhole_traces):
                - geology_segments (List[GeologySegment]): Flat list of all projected intervals.
                - drillhole_traces (List): List of trajectories (hole_id, trace_points, hole_segments).
        """
        geol_data = []
        drillhole_data = []

        logger.info(f"DrillholeService.process_intervals START")
        logger.info(f"  - Input Collars: {len(collar_points)}")

        # Build collar coordinate map
        collar_coords = {}
        for collar_feat in collar_layer.getFeatures():
            hole_id = collar_feat[collar_id_field]
            if use_geometry:
                geom = collar_feat.geometry()
                if geom:
                    pt = geom.asPoint()
                    if pt.x() != 0 and pt.y() != 0:
                        collar_coords[hole_id] = pt
            else:
                try:
                    x = float(collar_feat[collar_x_field])
                    y = float(collar_feat[collar_y_field])
                    if x != 0 and y != 0:
                        collar_coords[hole_id] = QgsPointXY(x, y)
                except (ValueError, TypeError):
                    continue

        for hole_id, collar_dist, collar_z, collar_offset, _ in collar_points:
            if hole_id not in collar_coords:
                logger.warning(f"Coords not found for collar {hole_id}")
                continue

            collar_point = collar_coords[hole_id]

            # Get survey data
            survey_data = []
            s_id = survey_fields["id"]
            s_depth = survey_fields["depth"]
            s_azim = survey_fields["azim"]
            s_incl = survey_fields["incl"]

            for feat in survey_layer.getFeatures():
                if feat[s_id] == hole_id:
                    try:
                        d = float(feat[s_depth])
                        a = float(feat[s_azim])
                        i = float(feat[s_incl])
                        survey_data.append((d, a, i))
                    except (ValueError, TypeError):
                        continue

            if not survey_data:
                logger.info(f"  - No survey data for hole {hole_id}. Attempting vertical projection.")
            else:
                survey_data.sort(key=lambda x: x[0])

            # Get Intervals (Fetched early for depth calc)
            intervals = []
            i_id = interval_fields["id"]
            i_from = interval_fields["from"]
            i_to = interval_fields["to"]
            i_lith = interval_fields["lith"]

            for feat in interval_layer.getFeatures():
                if feat[i_id] == hole_id:
                    try:
                        fd = float(feat[i_from])
                        td = float(feat[i_to])
                        lith = str(feat[i_lith])
                        intervals.append((fd, td, lith))
                    except (ValueError, TypeError):
                        continue

            max_interval_depth = max([i[1] for i in intervals]) if intervals else 0.0

            # Determine Final Depth
            given_depth = next((cp[4] for cp in collar_points if cp[0] == hole_id), 0.0)

            final_depth = given_depth
            if final_depth <= 0:
                max_survey_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
                final_depth = max(max_survey_depth, max_interval_depth)

            # Calculate Trajectory
            # Now passing total_depth=final_depth for extrapolation support
            trajectory = scu.calculate_drillhole_trajectory(
                collar_point, collar_z, survey_data, section_azimuth, densify_step=1.0, total_depth=final_depth
            )

            # Project Trajectory to Section
            projected_traj = scu.project_trajectory_to_section(
                trajectory, line_geom, line_start, distance_area
            )

            # Interpolate Intervals on Trajectory
            hole_geol_tuples = []
            if intervals:
                # Pack attributes into a dictionary to preserve metadata through interpolation
                rich_intervals = []
                for fd, td, lith in intervals:
                    attrs = {"unit": lith, "from": fd, "to": td}
                    rich_intervals.append((fd, td, attrs))
                
                hole_geol_tuples = scu.interpolate_intervals_on_trajectory(
                    projected_traj, rich_intervals, buffer_width
                )
            else:
                 logger.warning(f"  - No intervals for hole {hole_id}")

            hole_geol_data = []
            for attr_data, points in hole_geol_tuples:
                # Unpack attributes
                # attr_data is the dictionary we packed above
                unit_name = str(attr_data.get("unit", "Unknown"))
                
                # Create domain object
                seg = GeologySegment(
                    unit_name=unit_name,
                    geometry=None,
                    attributes=attr_data,
                    points=points
                )
                hole_geol_data.append(seg)

            if hole_geol_data:
                geol_data.extend(hole_geol_data)

            # Store for export/rendering
            traj_points = [(p[4], p[3]) for p in projected_traj]
            drillhole_data.append((hole_id, traj_points, hole_geol_data))

        logger.info(f"DrillholeService.process_intervals END: Generated {len(drillhole_data)} drillhole traces.")
        return geol_data, drillhole_data
