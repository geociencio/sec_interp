"""Drillhole Data Processing Service.

This module provides services for processing and projecting drillhole data,
including collar projection, trajectory calculation, and interval interpolation.
"""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeTaskInput, GeologySegment
from sec_interp.core.exceptions import (
    SecInterpError,
    ValidationError,
)
from sec_interp.core.interfaces.drillhole_interface import IDrillholeService
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor
from sec_interp.core.services.drillhole.data_fetcher import DataFetcher
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DrillholeService(IDrillholeService):
    """Service for processing and orchestrating drillhole data.

    This service handles the projection of collars onto a 2D section line,
    the calculation of 3D trajectories from survey data, and the interpolation
    of geological intervals along those trajectories. It leverages specialized
    processors to maintain a clean separation of concerns.
    """

    def __init__(self) -> None:
        """Initialize the service with specialized processors."""
        self.collar_processor = CollarProcessor()
        self.survey_processor = SurveyProcessor()
        self.interval_processor = IntervalProcessor()
        self.data_fetcher = DataFetcher()
        self.trajectory_engine = TrajectoryEngine()

    def project_collars(
        self,
        collar_data: list[dict[str, Any]],
        line_data: Any,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
    ) -> list[tuple]:
        """Project collar points onto section line using detached domain data.

        Args:
            collar_data: List of detached collar dictionaries.
            line_data: Section line geometry or feature.
            distance_area: QgsDistanceArea for measurements.
            buffer_width: Maximum distance from section for projection.
            collar_id_field: Name of the ID field.
            use_geometry: Whether to use geometric data for projection.
            collar_x_field: Field name for X coordinate (if not using geometry).
            collar_y_field: Field name for Y coordinate (if not using geometry).
            collar_z_field: Field name for Z coordinate.
            collar_depth_field: Field name for total depth.
            pre_sampled_z: Optional dict of pre-sampled elevations.

        Returns:
            List of projection tuples: (hole_id, dist_along, z, offset, total_depth).

        Raises:
            ValidationError: If parameters are invalid.

        """
        # Simple parameter validation
        if buffer_width <= 0:
            raise ValidationError(f"Buffer width must be positive, got {buffer_width}")

        da = distance_area
        line_geom = line_data.geometry() if hasattr(line_data, "geometry") else line_data
        try:
            line_start = scu.get_line_start_point(line_geom)
        except (AttributeError, TypeError, ValueError, SecInterpError):
            line_start = QgsPointXY(0, 0)  # Fallback

        results = []
        for c_item in collar_data:
            # Delegate to CollarProcessor
            res = self.collar_processor.extract_and_project_detached(
                c_item,
                line_geom,
                line_start,
                da,
                buffer_width,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
                pre_sampled_z,
            )
            if res:
                results.append(res)

        return results

    def prepare_task_input(
        self,
        line_layer: QgsVectorLayer,
        buffer_width: float,
        # Collar Params
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        # Child Data params
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
        # Optional
        dem_layer: QgsRasterLayer | None = None,
        band_num: int = 1,
    ) -> DrillholeTaskInput:
        """Prepare detached domain data for asynchronous processing.

        This method extracts and detaches all necessary data from QGIS layers
        to create a serializable task input.

        Args:
            line_layer: The section line vector layer.
            buffer_width: Projection buffer distance.
            collar_layer: The drillhole collars vector layer.
            collar_id_field: Name of the identifier field.
            use_geometry: Whether to extract coordinates from geometry.
            collar_x_field: Field name for X coordinate.
            collar_y_field: Field name for Y coordinate.
            collar_z_field: Field name for Z coordinate.
            collar_depth_field: Field name for hole depth.
            survey_layer: Vector layer containing survey data.
            survey_fields: Mapping of logical fields to layer field names.
            interval_layer: Vector layer containing interval/geology data.
            interval_fields: Mapping of logical fields to layer field names.
            dem_layer: Optional raster layer for elevation sampling.
            band_num: Raster band number to sample.

        Returns:
            A DrillholeTaskInput object containing serialized data.

        """
        line_geom, line_crs = self._extract_line_data(line_layer)
        line_start, section_azimuth = self._calculate_line_orientation(line_geom)

        self._validate_prepare_task_params(
            buffer_width,
            section_azimuth,
            collar_layer,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
        )

        # 1. Filter and Detach Collars
        collar_ids, collar_data, pre_sampled_z = self.collar_processor.detach_features(
            collar_layer,
            line_geom,
            buffer_width,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
            collar_z_field,
            dem_layer,
            target_crs=line_crs,
        )

        # 2. Bulk Fetch Child Data (Sync)
        survey_map = self.data_fetcher.fetch_bulk_data(survey_layer, collar_ids, survey_fields)
        interval_map = self.data_fetcher.fetch_bulk_data(
            interval_layer, collar_ids, interval_fields
        )

        return DrillholeTaskInput(
            line_geometry_wkt=line_geom.asWkt(),
            line_start_x=line_start.x(),
            line_start_y=line_start.y(),
            line_crs_authid=line_crs.authid(),
            section_azimuth=section_azimuth,
            buffer_width=buffer_width,
            collar_id_field=collar_id_field,
            use_geometry=use_geometry,
            collar_x_field=collar_x_field,
            collar_y_field=collar_y_field,
            collar_z_field=collar_z_field,
            collar_depth_field=collar_depth_field,
            collar_data=collar_data,
            survey_data=survey_map,
            interval_data=interval_map,
            pre_sampled_z=pre_sampled_z,
        )

    def _extract_line_data(
        self, line_layer: QgsVectorLayer
    ) -> tuple[QgsGeometry, QgsCoordinateReferenceSystem]:
        """Extract line geometry and CRS from the layer.

        Args:
            line_layer: The vector layer to extract data from.

        Returns:
            Tuple containing the line geometry and its CRS.

        Raises:
            DataMissingError: If the layer has no features.

        """
        line_feat = next(line_layer.getFeatures(), None)
        if not line_feat:
            from sec_interp.core.exceptions import DataMissingError

            raise DataMissingError("Line layer has no features")
        return line_feat.geometry(), line_layer.crs()

    def _calculate_line_orientation(self, line_geom: QgsGeometry) -> tuple[QgsPointXY, float]:
        """Calculate line start point and section azimuth.

        Args:
            line_geom: The section line geometry.

        Returns:
            Tuple with (start_point, azimuth_in_degrees).

        """
        line_start = (
            line_geom.asPolyline()[0]
            if not line_geom.isMultipart()
            else line_geom.asMultiPolyline()[0][0]
        )
        p2_vertex = line_geom.vertexAt(1)
        p2 = QgsPointXY(p2_vertex.x(), p2_vertex.y())
        azimuth = line_start.azimuth(p2)
        if azimuth < 0:
            azimuth += 360
        return line_start, azimuth

    def _validate_prepare_task_params(
        self,
        buffer_width: float,
        section_azimuth: float,
        collar_layer: QgsVectorLayer,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> None:
        """Validate parameters for prepare_task_input.

        Args:
            buffer_width: Buffer distance.
            section_azimuth: Section orientation.
            collar_layer: Layer to check.
            id_field: ID field name.
            use_geom: Whether geometric extraction is active.
            x_field: X field for fallback.
            y_field: Y field for fallback.

        Raises:
            ValidationError: If any constraint fails.

        """
        from sec_interp.core.validation.validators import (
            validate_positive,
            validate_range,
        )

        validate_positive("Buffer width")(buffer_width)
        validate_range(0, 360, "Section azimuth")(section_azimuth)

        fields = collar_layer.fields()
        if id_field and fields.indexFromName(id_field) == -1:
            raise ValidationError(f"Collar ID field '{id_field}' not found.")

        if not use_geom:
            for f in [x_field, y_field]:
                if f and fields.indexFromName(f) == -1:
                    raise ValidationError(f"Field '{f}' not found for coordinate extraction.")
            if y_field and collar_layer.fields().indexFromName(y_field) == -1:
                raise ValidationError(f"Field '{y_field}' not found in collar layer.")

    def process_task_data(self, task_input: DrillholeTaskInput, feedback: Any | None = None) -> Any:
        """Process drillholes using detached domain data (Thread-Safe).

        Args:
            task_input: The serialized data for processing.
            feedback: Optional QgsFeedback for progress and cancellation.

        Returns:
            Tuple (geol_data_all, drillhole_data_all) or None if canceled.

        """
        # Reconstruct Objects
        line_crs = QgsCoordinateReferenceSystem(task_input.line_crs_authid)
        da = scu.create_distance_area(line_crs)
        line_geom = QgsGeometry.fromWkt(task_input.line_geometry_wkt)
        line_start = QgsPointXY(task_input.line_start_x, task_input.line_start_y)

        geol_data_all = []
        drillhole_data_all = []  # (hid, trace2d, trace3d, proj3d, geologic_segments)

        total = len(task_input.collar_data)

        for i, c_item in enumerate(task_input.collar_data):
            if feedback and feedback.isCanceled():
                return None

            # Process each collar and its associated data
            result = self._process_detached_collar_item(
                c_item, task_input, da, line_geom, line_start
            )
            if result:
                hole_geol, hole_tuple = result
                geol_data_all.extend(hole_geol)
                drillhole_data_all.append(hole_tuple)

            if feedback:
                feedback.setProgress((i / total) * 100)

        return geol_data_all, drillhole_data_all

    def _process_detached_collar_item(
        self,
        c_item: dict[str, Any],
        task_input: DrillholeTaskInput,
        da: QgsDistanceArea,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
    ) -> tuple[list[GeologySegment], tuple] | None:
        """Process a single detached collar item."""
        # 1. Project collar using CollarProcessor
        result = self.collar_processor.extract_and_project_detached(
            c_item,
            line_geom,
            line_start,
            da,
            task_input.buffer_width,
            task_input.collar_id_field,
            task_input.use_geometry,
            task_input.collar_x_field,
            task_input.collar_y_field,
            task_input.collar_z_field,
            task_input.collar_depth_field,
            task_input.pre_sampled_z,
        )

        if not result:
            return None

        hole_id, _dist, z, _offset, depth = result

        # 2. Extract point for single hole processing
        pt = self.collar_processor.extract_point_agnostic(
            c_item,
            True,  # it's a dict
            task_input.use_geometry,
            task_input.collar_x_field,
            task_input.collar_y_field,
        )

        if not pt:
            return None

        # 3. Full Processing
        surveys = task_input.survey_data.get(hole_id, [])
        intervals = task_input.interval_data.get(hole_id, [])

        return self._process_single_hole(
            hole_id=hole_id,
            collar_point=pt,
            collar_z=z,
            given_depth=depth,
            survey_data=surveys,
            intervals=intervals,
            line_geom=line_geom,
            line_start=line_start,
            distance_area=da,
            buffer_width=task_input.buffer_width,
            section_azimuth=task_input.section_azimuth,
        )

    def process_intervals(
        self,
        collar_points: list[tuple],
        collar_data: list[dict[str, Any]],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[list[GeologySegment], list[tuple]]:
        """Process drillhole interval data using detached structures.

        Args:
            collar_points: Projected collar results.
            collar_data: Original detached collar data.
            survey_data: Map of hole IDs to survey tuples.
            interval_data: Map of hole IDs to interval tuples.
            collar_id_field: ID field name.
            use_geometry: Whether geometry was used.
            collar_x_field: X field name.
            collar_y_field: Y field name.
            line_geom: Section geometry.
            line_start: Section start point.
            distance_area: Distance measurer.
            buffer_width: Buffer width.
            section_azimuth: Section orientation.
            survey_fields: Survey field mapping.
            interval_fields: Interval field mapping.

        Returns:
            Tuple of (geology_segments, drillhole_results).

        """
        geol_data: list[GeologySegment] = []
        drillhole_data: list[tuple] = []

        # 1. Build collar coordinate map from detached data
        collar_coords = self._build_collar_coordinate_map(
            collar_data, use_geometry, collar_x_field, collar_y_field
        )

        self._process_hole_batch(
            collar_points,
            collar_coords,
            survey_data,
            interval_data,
            line_geom,
            line_start,
            distance_area,
            buffer_width,
            section_azimuth,
            geol_data,
            drillhole_data,
        )

        return geol_data, drillhole_data

    def _build_collar_coordinate_map(
        self,
        collar_data: list[dict[str, Any]],
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
    ) -> dict[Any, QgsPointXY]:
        """Build a mapping of hole IDs to collar coordinates."""
        return self.collar_processor.build_coordinate_map(
            collar_data, use_geometry, collar_x_field, collar_y_field
        )

    def _extract_point_from_attrs(
        self, attrs: dict[str, Any], x_field: str, y_field: str
    ) -> QgsPointXY | None:
        """Safely extract a point from attribute dictionary."""
        return self.collar_processor.extract_point_agnostic(
            {"attributes": attrs}, True, False, x_field, y_field
        )

    def _process_hole_batch(
        self,
        collar_points: list[tuple],
        collar_coords: dict[Any, QgsPointXY],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        geol_data: list[GeologySegment],
        drillhole_data: list[tuple],
    ) -> None:
        """Process a batch of holes sequentially."""
        for hole_id, _dist, collar_z, _off, given_depth in collar_points:
            collar_point = collar_coords.get(hole_id)
            if not collar_point:
                continue

            self._safe_process_single_hole(
                hole_id,
                collar_point,
                collar_z,
                given_depth,
                survey_data,
                interval_data,
                line_geom,
                line_start,
                distance_area,
                buffer_width,
                section_azimuth,
                geol_data,
                drillhole_data,
            )

    def _fetch_bulk_data_detached(
        self, layer: QgsVectorLayer, hole_ids: set[Any], fields: dict[str, str]
    ) -> dict[Any, list[tuple]]:
        """Fetch data into pure python structures (no QgsFeature dependency)."""
        return self.data_fetcher.fetch_bulk_data(layer, hole_ids, fields)

    def _process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        survey_data: list[tuple[float, float, float]],
        intervals: list[tuple[float, float, str]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
    ) -> tuple[list[GeologySegment], tuple]:
        """Process a single drillhole's trajectory and intervals."""
        return self.trajectory_engine.process_single_hole(
            hole_id,
            collar_point,
            collar_z,
            given_depth,
            survey_data,
            intervals,
            line_geom,
            line_start,
            distance_area,
            buffer_width,
            section_azimuth,
        )

    def _create_drillhole_result_tuple(
        self,
        hole_id: Any,
        projected_traj: list[tuple],
        hole_geol_data: list[GeologySegment],
    ) -> tuple:
        """Create the final result tuple for a drillhole using SpatialMeta."""
        return self.trajectory_engine.create_drillhole_result_tuple(
            hole_id, projected_traj, hole_geol_data
        )

    def _safe_process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        surveys_map: dict[Any, list[tuple[float, float, float]]],
        intervals_map: dict[Any, list[tuple[float, float, str]]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        geol_data: list[GeologySegment],
        drillhole_data: list[tuple[Any, list[tuple[float, float]], list[GeologySegment]]],
    ) -> None:
        """Safely process a single hole with error logging."""
        try:
            hole_geol, hole_drill = self._process_single_hole(
                hole_id=hole_id,
                collar_point=collar_point,
                collar_z=collar_z,
                given_depth=given_depth,
                survey_data=surveys_map.get(hole_id, []),
                intervals=intervals_map.get(hole_id, []),
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=buffer_width,
                section_azimuth=section_azimuth,
            )

            if hole_geol:
                geol_data.extend(hole_geol)
            drillhole_data.append(hole_drill)
        except (ValueError, TypeError, KeyError) as e:
            logger.exception(f"Data error in hole {hole_id}: {e}")
        except SecInterpError as e:
            logger.exception(f"Processing error in hole {hole_id}: {e}")
        except (AttributeError, RuntimeError) as e:
            logger.exception(f"Runtime or attribute error processing hole {hole_id}")
            raise SecInterpError(f"Unexpected processing error: {e}") from e
        except Exception:
            logger.exception(f"Critical unexpected error processing hole {hole_id}")
            raise

    def generate_drillhole_data(self, params: Any) -> Any | None:
        """Orchestrate the generation of drillhole traces and intervals.

        Args:
            params: Configuration object (PreviewParams).

        Returns:
            List of drillhole data tuples or None if failed.

        """
        line_feat = next(params.line_layer.getFeatures(), None)
        if not line_feat:
            return None

        section_geom = line_feat.geometry()
        from sec_interp.core import utils as scu

        vertices = scu.get_line_vertices(section_geom)
        if not vertices:
            return None
        section_start = vertices[0]
        distance_area = scu.create_distance_area(params.line_layer.crs())

        # 1. Detach Collar Data
        collar_ids, collar_data, pre_sampled_z = self.collar_processor.detach_features(
            params.collar_layer,
            section_geom,
            params.buffer_dist,
            params.collar_id_field,
            params.collar_use_geometry,
            params.collar_x_field,
            params.collar_y_field,
            params.collar_z_field,
            params.raster_layer,
            target_crs=params.line_layer.crs(),
        )

        if not collar_data:
            return None

        # 2. Project Collars (Detached)
        collars_projected = self.project_collars(
            collar_data=collar_data,
            line_data=section_geom,
            distance_area=distance_area,
            buffer_width=params.buffer_dist,
            collar_id_field=params.collar_id_field,
            use_geometry=params.collar_use_geometry,
            collar_x_field=params.collar_x_field,
            collar_y_field=params.collar_y_field,
            collar_z_field=params.collar_z_field,
            collar_depth_field=params.collar_depth_field,
            pre_sampled_z=pre_sampled_z,
        )

        if not (collars_projected and params.survey_layer and params.interval_layer):
            return None

        # 3. Extract Detached Data for Child Layers
        survey_map = self.data_fetcher.fetch_bulk_data(
            params.survey_layer,
            collar_ids,
            {
                "id": params.survey_id_field,
                "depth": params.survey_depth_field,
                "azim": params.survey_azim_field,
                "incl": params.survey_incl_field,
            },
        )
        interval_map = self.data_fetcher.fetch_bulk_data(
            params.interval_layer,
            collar_ids,
            {
                "id": params.interval_id_field,
                "from": params.interval_from_field,
                "to": params.interval_to_field,
                "lith": params.interval_lith_field,
            },
        )

        section_azimuth = scu.calculate_line_azimuth(section_geom)

        # 4. Process Intervals (Detached)
        _, drillhole_data = self.process_intervals(
            collar_points=collars_projected,
            collar_data=collar_data,
            survey_data=survey_map,
            interval_data=interval_map,
            collar_id_field=params.collar_id_field,
            use_geometry=params.collar_use_geometry,
            collar_x_field=params.collar_x_field,
            collar_y_field=params.collar_y_field,
            line_geom=section_geom,
            line_start=section_start,
            distance_area=distance_area,
            buffer_width=params.buffer_dist,
            section_azimuth=section_azimuth,
            survey_fields={},
            interval_fields={},
        )
        return drillhole_data
