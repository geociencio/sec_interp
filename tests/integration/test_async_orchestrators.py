"""Integration tests for asynchronous task orchestrators.

Covers DrillholeTaskOrchestrator and PreviewTaskOrchestrator, testing
signal connections, task preparation, and synchronous processing flows.
"""

from __future__ import annotations

import os

os.environ["FORCE_MOCKS"] = "0"

from unittest.mock import MagicMock, patch

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
)

from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import ValidationError
from sec_interp.core.services.drillhole.drillhole_orchestrator import (
    DrillholeTaskOrchestrator,
)
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.gui.preview_task_orchestrator import PreviewTaskOrchestrator
from tests.integration.base_integration import BaseIntegrationTest


def _make_line_layer() -> QgsVectorLayer:
    layer = QgsVectorLayer("LineString?crs=EPSG:32719", "section_line", "memory")
    feat = QgsFeature()
    feat.setGeometry(
        QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 6_000_000), QgsPointXY(1000, 6_000_000)]
        )
    )
    layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


def _make_collar_layer() -> QgsVectorLayer:
    uri = "Point?crs=EPSG:32719&field=hole_id:string(50)&field=depth:double"
    layer = QgsVectorLayer(uri, "collars", "memory")
    feat = QgsFeature(layer.fields())
    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(500, 6_000_000)))
    feat.setAttribute("hole_id", "DH-01")
    feat.setAttribute("depth", 100.0)
    layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


class TestDrillholeTaskOrchestrator(BaseIntegrationTest):
    """Integration tests for DrillholeTaskOrchestrator."""

    def setUp(self) -> None:
        super().setUp()
        self.service = DrillholeService()
        self.orchestrator = DrillholeTaskOrchestrator(self.service)

    def test_run_preview_returns_none_if_missing_layers(self) -> None:
        """run_preview should return None if essential layers are missing."""
        params = PreviewParams(
            line_layer="invalid_layer",
            collar_layer="",
            raster_layer="",
            survey_layer="",
            interval_layer="",
            buffer_dist=100.0,
            collar_id_field="hole_id",
            collar_use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="",
            collar_depth_field="depth",
            survey_id_field="",
            survey_depth_field="",
            survey_azim_field="",
            survey_incl_field="",
            interval_id_field="",
            interval_from_field="",
            interval_to_field="",
            interval_lith_field="",
            band_num=1,
        )
        result = self.orchestrator.run_preview(params)
        self.assertIsNone(result)

    def test_prepare_task_input_validates_and_extracts(self) -> None:
        """prepare_task_input should validate input and return a DrillholeTaskInput."""
        line_lyr = _make_line_layer()
        collar_lyr = _make_collar_layer()

        task_input = self.orchestrator.prepare_task_input(
            line_layer=line_lyr,
            buffer_width=100.0,
            collar_layer=collar_lyr,
            collar_id_field="hole_id",
            use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="",
            collar_depth_field="depth",
            survey_layer=None,
            survey_fields={},
            interval_layer=None,
            interval_fields={},
            dem_layer=None,
            band_num=1,
        )

        self.assertIsNotNone(task_input)
        self.assertEqual(task_input.buffer_width, 100.0)
        self.assertEqual(task_input.collar_id_field, "hole_id")
        self.assertEqual(len(task_input.collar_data), 1)
        self.assertEqual(task_input.collar_data[0]["attributes"]["hole_id"], "DH-01")

    def test_prepare_task_input_raises_validation_error_on_invalid_field(self) -> None:
        """Should raise ValidationError if a specified collar field does not exist."""
        line_lyr = _make_line_layer()
        collar_lyr = _make_collar_layer()

        with self.assertRaises(ValidationError):
            self.orchestrator.prepare_task_input(
                line_layer=line_lyr,
                buffer_width=100.0,
                collar_layer=collar_lyr,
                collar_id_field="invalid_id_field",  # Does not exist
                use_geometry=True,
                collar_x_field="",
                collar_y_field="",
                collar_z_field="",
                collar_depth_field="depth",
                survey_layer=None,
                survey_fields={},
                interval_layer=None,
                interval_fields={},
            )


class TestPreviewTaskOrchestrator(BaseIntegrationTest):
    """Integration tests for PreviewTaskOrchestrator."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_manager = MagicMock()
        self.orchestrator = PreviewTaskOrchestrator(self.mock_manager)

    @patch(
        "sec_interp.gui.preview_task_orchestrator.QgsApplication.taskManager",
        create=True,
    )
    def test_start_geology_task_creates_and_adds_task(self, mock_task_manager) -> None:
        """start_geology_task should setup GeologyGenerationTask and add it to TaskManager."""
        mock_task_manager_instance = MagicMock()
        mock_task_manager.return_value = mock_task_manager_instance

        # Params object mimicking the expected structure
        class DummyParams:
            line_layer = "dummy_line"
            raster_layer = "dummy_raster"
            outcrop_layer = "dummy_outcrop"
            outcrop_name_field = "unit"
            band_num = 1

        params = DummyParams()

        # Mock resolve_layer to avoid needing real QgsProject IDs
        with patch(
            "sec_interp.gui.preview_task_orchestrator.resolve_layer"
        ) as mock_resolve:
            mock_lyr = MagicMock()
            mock_resolve.return_value = mock_lyr

            mock_service = MagicMock()
            mock_service.prepare_task_input.return_value = MagicMock()

            self.orchestrator.start_geology_task(params, mock_service)

            # Verification
            self.assertIsNotNone(self.orchestrator.geology_task)
            self.assertEqual(
                self.orchestrator.geology_task.description(), "Geology Preview (Async)"
            )
            mock_task_manager_instance.addTask.assert_called_once_with(
                self.orchestrator.geology_task
            )

            # Check signals are connected to manager
            # In PyQt/QGIS signals might not be easily assertable if they are real signals,
            # but we can verify the mock manager methods were passed as slots.
            # Since GeologyGenerationTask is created, we just ensure it exists.

    def test_cancel_active_tasks_cleans_up(self) -> None:
        """cancel_active_tasks should cancel and disconnect any active tasks."""
        # Setup dummy tasks
        mock_geo_task = MagicMock()
        mock_drill_task = MagicMock()

        self.orchestrator.geology_task = mock_geo_task
        self.orchestrator.drillhole_task = mock_drill_task

        self.orchestrator.cancel_active_tasks()

        mock_geo_task.cancel.assert_called_once()
        mock_drill_task.cancel.assert_called_once()

        self.assertIsNone(self.orchestrator.geology_task)
        self.assertIsNone(self.orchestrator.drillhole_task)
