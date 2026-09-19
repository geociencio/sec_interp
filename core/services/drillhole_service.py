"""Drillhole Data Processing Service (pure computation).

This module provides the pure computation for projecting and processing
drillhole data — collar projection, trajectory calculation, and interval
interpolation — operating on a detached :class:`DrillholeContext`.
"""

from __future__ import annotations

from typing import Any

from sec_interp.core.domain import DrillholeProjection, GeologySegment
from sec_interp.core.domain.task_inputs import DrillholeContext
from sec_interp.core.exceptions import SecInterpError
from sec_interp.core.interfaces.drillhole_interface import IDrillholeService
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DrillholeService(IDrillholeService, TranslatableMixin):
    """Service for processing and orchestrating drillhole data (QGIS-agnostic)."""

    def __init__(
        self,
        collar_processor: CollarProcessor | None = None,
        survey_processor: SurveyProcessor | None = None,
        interval_processor: IntervalProcessor | None = None,
        data_fetcher: Any | None = None,
        trajectory_engine: TrajectoryEngine | None = None,
    ) -> None:
        """Initialize the service with specialized processors.

        Args:
            collar_processor: Optional collar processor.
            survey_processor: Optional survey processor.
            interval_processor: Optional interval processor.
            data_fetcher: Kept for backward-compatible construction (unused).
            trajectory_engine: Optional trajectory engine.

        """
        self.collar_processor = collar_processor or CollarProcessor()
        self.survey_processor = survey_processor or SurveyProcessor()
        self.interval_processor = interval_processor or IntervalProcessor()
        self.data_fetcher = data_fetcher
        self.trajectory_engine = trajectory_engine or TrajectoryEngine()

    def process_context(
        self, context: DrillholeContext, feedback: Any | None = None
    ) -> tuple[list[GeologySegment], list[DrillholeProjection]] | None:
        """Process drillholes from a detached context (pure computation).

        Args:
            context: Fully-detached drillhole data from ``DrillholeExtractor``.
            feedback: Optional feedback object for progress/cancellation.

        Returns:
            A tuple ``(geol_data, drillhole_data)``, or None if cancelled.

        """
        geol_data_all: list[GeologySegment] = []
        drillhole_data_all: list[DrillholeProjection] = []
        total = len(context.collar_data)

        for i, collar in enumerate(context.collar_data):
            if feedback and feedback.isCanceled():
                return None

            proj = self.collar_processor.extract_and_project_detached(
                collar,
                context.line_points,
                context.buffer_width,
                context.collar_id_field,
                context.collar_z_field,
                context.collar_depth_field,
                context.pre_sampled_z,
            )
            if proj:
                hole_id = proj.hole_id
                point = collar.get("point")
                surveys = context.survey_data.get(hole_id, [])
                intervals = context.interval_data.get(hole_id, [])

                try:
                    hole_geol, hole_tuple = self.trajectory_engine.process_single_hole(
                        hole_id,
                        point,
                        proj.elevation,
                        proj.total_depth,
                        surveys,
                        intervals,
                        context.line_points,
                        context.buffer_width,
                        context.section_azimuth,
                    )
                    geol_data_all.extend(hole_geol)
                    drillhole_data_all.append(hole_tuple)
                except (ValueError, TypeError, KeyError) as e:
                    logger.exception(self.tr("Data error in hole {0}: {1}").format(hole_id, e))
                except SecInterpError as e:
                    logger.exception(
                        self.tr("Processing error in hole {0}: {1}").format(hole_id, e)
                    )

            if feedback:
                feedback.setProgress((i / total) * 100)

        return geol_data_all, drillhole_data_all
