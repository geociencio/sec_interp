"""Orchestrator for drillhole processing tasks.

This module provides the DrillholeTaskOrchestrator, which coordinates the
high-level flow of drillhole data processing, including synchronous previews
and asynchronous task preparation and execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.domain import (
    DrillholeProjection,
    DrillholeTaskInput,
    GeologySegment,
    PreviewParams,
)
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.utils.qgis import LayerResolver

if TYPE_CHECKING:
    from sec_interp.core.services.drillhole_service import DrillholeService


class DrillholeTaskOrchestrator:
    """Orchestrates high-level drillhole processing workflows.

    This class separates the orchestration (the "how" and "when") from
    the business logic (the "what") contained in DrillholeService.
    """

    def __init__(self, service: DrillholeService) -> None:
        """Initialize with a drillhole service.

        Args:
            service: The service containing the core processing logic.

        """
        self.service = service

    def run_preview(self, params: PreviewParams) -> list[DrillholeProjection] | None:
        """Execute a synchronous drillhole preview.

        This mimics the legacy generate_drillhole_data but is now managed
        by the orchestrator.
        """
        line_lyr = LayerResolver.resolve(params.line_layer)
        collar_lyr = LayerResolver.resolve(params.collar_layer)
        raster_lyr = LayerResolver.resolve(params.raster_layer)
        survey_lyr = LayerResolver.resolve(params.survey_layer)
        interval_lyr = LayerResolver.resolve(params.interval_layer)

        if not line_lyr or not collar_lyr:
            return None

        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            return None

        section_geom = line_feat.geometry()
        vertices = scu.get_line_vertices(section_geom)
        if not vertices:
            return None
        section_start = vertices[0]
        distance_area = scu.create_distance_area(line_lyr.crs())

        # 1. Detach Collar Data
        collar_ids, collar_data, pre_sampled_z = (
            self.service.collar_processor.detach_features(
                collar_lyr,
                section_geom,
                params.buffer_dist,
                params.collar_id_field or "",
                params.collar_use_geometry,
                params.collar_x_field or "",
                params.collar_y_field or "",
                params.collar_z_field or "",
                raster_lyr,
                target_crs=line_lyr.crs(),
            )
        )

        if not collar_data:
            return None

        # 2. Project Collars (Detached)
        collars_projected = self.service.project_collars(
            collar_data=collar_data,
            line_data=section_geom,
            distance_area=distance_area,
            buffer_width=params.buffer_dist,
            collar_id_field=params.collar_id_field or "",
            use_geometry=params.collar_use_geometry,
            collar_x_field=params.collar_x_field or "",
            collar_y_field=params.collar_y_field or "",
            collar_z_field=params.collar_z_field or "",
            collar_depth_field=params.collar_depth_field or "",
            pre_sampled_z=pre_sampled_z,
        )

        if not (collars_projected and survey_lyr and interval_lyr):
            return None

        # 3. Extract Detached Data for Child Layers
        survey_map = self.service.data_fetcher.fetch_bulk_data(
            survey_lyr,
            collar_ids,
            {
                "id": params.survey_id_field or "",
                "depth": params.survey_depth_field or "",
                "azim": params.survey_azim_field or "",
                "incl": params.survey_incl_field or "",
            },
        )
        interval_map = self.service.data_fetcher.fetch_bulk_data(
            interval_lyr,
            collar_ids,
            {
                "id": params.interval_id_field or "",
                "from": params.interval_from_field or "",
                "to": params.interval_to_field or "",
                "lith": params.interval_lith_field or "",
            },
        )

        section_azimuth = scu.calculate_line_azimuth(section_geom)

        # 4. Process Intervals (Detached)
        _, drillhole_data = self.service.process_intervals(
            collar_points=collars_projected,
            collar_data=collar_data,
            survey_data=survey_map,
            interval_data=interval_map,
            collar_id_field=params.collar_id_field or "",
            use_geometry=params.collar_use_geometry,
            collar_x_field=params.collar_x_field or "",
            collar_y_field=params.collar_y_field or "",
            line_geom=section_geom,
            line_start=section_start,
            distance_area=distance_area,
            buffer_width=params.buffer_dist,
            section_azimuth=section_azimuth,
            survey_fields={},
            interval_fields={},
        )
        return drillhole_data

    def _validate_prepare_task_params(
        self,
        buffer_width: float,
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
    ) -> None:
        """Validate input parameters for task preparation."""
        from sec_interp.core.exceptions import ValidationError

        if buffer_width <= 0:
            raise ValidationError("Buffer width must be positive")

        if collar_layer:
            self._validate_collar_params(
                collar_layer,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
            )

        if survey_layer:
            self._validate_survey_params(survey_layer, survey_fields)

        if interval_layer:
            self._validate_interval_params(interval_layer, interval_fields)

    def _validate_collar_params(
        self,
        layer: QgsVectorLayer,
        id_field: str,
        use_geom: bool,
        x_f: str,
        y_f: str,
        z_f: str,
        dept_f: str,
    ) -> None:
        """Validate collar layer fields."""
        from sec_interp.core.exceptions import ValidationError

        fields = [f.name() for f in layer.fields()]
        if id_field not in fields:
            raise ValidationError(f"Collar ID field '{id_field}' not found")
        if not use_geom:
            if x_f not in fields:
                raise ValidationError(f"Collar X field '{x_f}' not found")
            if y_f not in fields:
                raise ValidationError(f"Collar Y field '{y_f}' not found")
        if z_f and z_f not in fields:
            raise ValidationError(f"Collar Z field '{z_f}' not found")
        if dept_f and dept_f not in fields:
            raise ValidationError(f"Collar Depth field '{dept_f}' not found")

    def _validate_survey_params(
        self, layer: QgsVectorLayer, fields: dict[str, str]
    ) -> None:
        """Validate survey layer fields."""
        from sec_interp.core.exceptions import ValidationError

        layer_fields = [f.name() for f in layer.fields()]
        for fname in fields.values():
            if fname and fname not in layer_fields:
                raise ValidationError(f"Survey field '{fname}' not found")

    def _validate_interval_params(
        self, layer: QgsVectorLayer, fields: dict[str, str]
    ) -> None:
        """Validate interval layer fields."""
        from sec_interp.core.exceptions import ValidationError

        layer_fields = [f.name() for f in layer.fields()]
        for fname in fields.values():
            if fname and fname not in layer_fields:
                raise ValidationError(f"Interval field '{fname}' not found")

    def prepare_task_input(
        self,
        line_layer: QgsVectorLayer,
        buffer_width: float,
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
        dem_layer: QgsRasterLayer | None = None,
        band_num: int = 1,
    ) -> DrillholeTaskInput:
        """Prepare detached domain data for asynchronous processing."""
        # 0. Level 3 Domain Validation
        self._validate_prepare_task_params(
            buffer_width,
            collar_layer,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
            collar_z_field,
            collar_depth_field,
            survey_layer,
            survey_fields,
            interval_layer,
            interval_fields,
        )
        line_feat = next(line_layer.getFeatures(), None)
        if not line_feat:
            raise DataMissingError("Line layer has no features")

        line_geom = line_feat.geometry()
        line_crs = line_layer.crs()

        # Calculate line orientation
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
        section_azimuth = azimuth

        # 1. Filter and Detach Collars
        collar_ids: set[str] = set()
        collar_data: list[dict[str, Any]] = []
        pre_sampled_z: dict[str, float] = {}
        if collar_layer:
            (
                collar_ids,
                collar_data,
                pre_sampled_z,
            ) = self.service.collar_processor.detach_features(
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
        survey_map = {}
        interval_map = {}
        if collar_ids:
            if survey_layer:
                survey_map = self.service.data_fetcher.fetch_bulk_data(
                    survey_layer, collar_ids, survey_fields
                )
            if interval_layer:
                interval_map = self.service.data_fetcher.fetch_bulk_data(
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

    def process_task_data(
        self, task_input: DrillholeTaskInput, feedback: Any | None = None
    ) -> tuple[list[GeologySegment], list[DrillholeProjection]] | None:
        """Process drillholes using detached domain data (Thread-Safe)."""
        # Reconstruct Objects
        line_crs = QgsCoordinateReferenceSystem(task_input.line_crs_authid)
        da = scu.create_distance_area(line_crs)
        line_geom = QgsGeometry.fromWkt(task_input.line_geometry_wkt)
        line_start = QgsPointXY(task_input.line_start_x, task_input.line_start_y)

        geol_data_all = []
        drillhole_data_all = []

        total = len(task_input.collar_data)

        for i, c_item in enumerate(task_input.collar_data):
            if feedback and feedback.isCanceled():
                return None

            # Logic moved from DrillholeService._process_detached_collar_item
            result = self.service.collar_processor.extract_and_project_detached(
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

            if result:
                hole_id = result.hole_id
                z = result.elevation
                depth = result.total_depth
                pt = self.service.collar_processor.extract_point_agnostic(
                    c_item,
                    True,
                    task_input.use_geometry,
                    task_input.collar_x_field,
                    task_input.collar_y_field,
                )

                if pt:
                    surveys = task_input.survey_data.get(hole_id, [])
                    intervals = task_input.interval_data.get(hole_id, [])

                    res = self.service.trajectory_engine.process_single_hole(
                        hole_id,
                        pt,
                        z,
                        depth,
                        surveys,
                        intervals,
                        line_geom,
                        line_start,
                        da,
                        task_input.buffer_width,
                        task_input.section_azimuth,
                    )
                    if res:
                        hole_geol, hole_tuple = res
                        geol_data_all.extend(hole_geol)
                        drillhole_data_all.append(hole_tuple)

            if feedback:
                feedback.setProgress((i / total) * 100)

        return geol_data_all, drillhole_data_all
