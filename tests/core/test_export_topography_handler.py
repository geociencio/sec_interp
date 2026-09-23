"""Tests for the topography export handler (smoothed outputs)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sec_interp.core.services.export.handlers.topography import export_topography
from tests.base_test import BaseTestCase


class TestExportTopographySmoothed(BaseTestCase):
    """The smoothed profile is exported only when enabled."""

    def _run(self, options: dict) -> tuple[int, int]:
        csv_exporter = MagicMock()
        csv_exporter.export.return_value = True

        with patch("sec_interp.exporters.ProfileLineVectorExporter") as vector_cls:
            vector_cls.return_value.export.return_value = True
            export_topography(
                self.output_dir,
                [(0.0, 0.0), (10.0, 5.0), (20.0, 3.0)],
                crs=MagicMock(),
                csv_exporter=csv_exporter,
                msg=[],
                controller=None,
                settings=None,
                ext=".shp",
                options=options,
            )
            return csv_exporter.export.call_count, vector_cls.return_value.export.call_count

    def test_smoothed_written_when_enabled(self) -> None:
        """Raw + smoothed CSV/vector are written when smoothing is on."""
        csv_calls, vector_calls = self._run({"smooth": True, "smooth_window": 10})

        self.assertEqual(csv_calls, 2)
        self.assertEqual(vector_calls, 2)

    def test_no_smoothed_when_disabled(self) -> None:
        """Only the raw outputs are written when smoothing is off."""
        csv_calls, vector_calls = self._run({"smooth": False, "smooth_window": 10})

        self.assertEqual(csv_calls, 1)
        self.assertEqual(vector_calls, 1)
