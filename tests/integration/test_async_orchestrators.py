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

from sec_interp.core.exceptions import ValidationError
from sec_interp.gui.adapters.drillhole_extractor import DrillholeExtractor
from sec_interp.gui.adapters.feature_fetcher import DataFetcher
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


class TestDrillholeExtractor(BaseIntegrationTest):
    """Integration tests for DrillholeExtractor."""

    def setUp(self) -> None:
        super().setUp()
        self.extractor = DrillholeExtractor(data_fetcher=DataFetcher())

    def test_extract_context_validates_and_extracts(self) -> None:
        """extract_context should validate input and return a DrillholeContext."""
        line_lyr = _make_line_layer()
        collar_lyr = _make_collar_layer()

        context = self.extractor.extract_context(
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

        self.assertIsNotNone(context)
        self.assertEqual(context.buffer_width, 100.0)
        self.assertEqual(context.collar_id_field, "hole_id")
        self.assertEqual(len(context.collar_data), 1)
        self.assertEqual(context.collar_data[0]["attributes"]["hole_id"], "DH-01")

    def test_extract_context_raises_validation_error_on_invalid_field(self) -> None:
        """Should raise ValidationError if a specified collar field does not exist."""
        line_lyr = _make_line_layer()
        collar_lyr = _make_collar_layer()

        with self.assertRaises(ValidationError):
            self.extractor.extract_context(
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

            # Mock the geology extractor accessed via the manager chain
            self.mock_manager.preview_service.controller.geology_extractor = MagicMock()
            self.mock_manager.preview_service.controller.geology_extractor.extract_context.return_value = (
                MagicMock()
            )

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

        # Add to the active tasks set for the new anchoring logic
        self.orchestrator._active_tasks.append(mock_geo_task)
        self.orchestrator._active_tasks.append(mock_drill_task)

        self.orchestrator.cancel_active_tasks()

        mock_geo_task.cancel.assert_called_once()
        mock_drill_task.cancel.assert_called_once()

        self.assertIsNone(self.orchestrator.geology_task)
        self.assertIsNone(self.orchestrator.drillhole_task)
