"""Preview reporting and message formatting for SecInterp.

This module provides the PreviewReporter class to handle the formatting of
preview generation results and performance metrics into human-readable messages.
"""

from __future__ import annotations

from typing import Optional

from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.performance_metrics import MetricsCollector, format_duration
from sec_interp.core.types import (
    GeologyData,
    PreviewResult,
    StructureData,
)
from .main_dialog_config import DialogConfig


class PreviewReporter:
    """Formatter for preview generation results and status messages."""

    @staticmethod
    def format_results_message(result: PreviewResult, metrics: MetricsCollector) -> str:
        """Format results message for display using core result objects.

        Args:
            result: The preview result object containing data and metadata.
            metrics: Performance metrics collector.

        Returns:
            A formatted string ready for display in the UI.
        """
        lines = [
            QCoreApplication.translate("PreviewReporter", "✓ Preview generated!"),
            "",
            QCoreApplication.translate(
                "PreviewReporter", "Topography: {} points"
            ).format(len(result.topo) if result.topo else 0),
        ]

        # Add components
        lines.append(PreviewReporter.format_geology_summary(result.geol))
        lines.append(
            PreviewReporter.format_structure_summary(result.struct, result.buffer_dist)
        )
        lines.append(PreviewReporter.format_drillhole_summary(result.drillhole))

        # Add ranges
        lines.extend(PreviewReporter.format_result_metrics(result))

        # Add performance metrics if enabled
        if (
            DialogConfig.ENABLE_PERFORMANCE_METRICS
            and DialogConfig.SHOW_METRICS_IN_RESULTS
        ):
            lines.extend(PreviewReporter.format_performance_metrics(metrics, result))

        lines.extend(
            [
                "",
                QCoreApplication.translate(
                    "PreviewReporter",
                    "Adjust 'Vert. Exag.' and click Preview to update.",
                ),
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def format_geology_summary(geol_data: Optional[GeologyData]) -> str:
        """Format a summary line for geology data."""
        if not geol_data:
            return QCoreApplication.translate("PreviewReporter", "Geology: No data")
        return QCoreApplication.translate(
            "PreviewReporter", "Geology: {} segments"
        ).format(len(geol_data))

    @staticmethod
    def format_structure_summary(
        struct_data: Optional[StructureData], buffer_dist: float
    ) -> str:
        """Format a summary line for structural data."""
        if not struct_data:
            return QCoreApplication.translate("PreviewReporter", "Structures: No data")
        return QCoreApplication.translate(
            "PreviewReporter", "Structures: {} measurements (buffer: {}m)"
        ).format(len(struct_data), buffer_dist)

    @staticmethod
    def format_drillhole_summary(drillhole_data: Optional[Any]) -> str:
        """Format a summary line for drillhole data."""
        if not drillhole_data:
            return QCoreApplication.translate("PreviewReporter", "Drillholes: No data")
        return QCoreApplication.translate(
            "PreviewReporter", "Drillholes: {} holes found"
        ).format(len(drillhole_data))

    @staticmethod
    def format_result_metrics(result: PreviewResult) -> list[str]:
        """Format elevation metrics for the results message."""
        min_elev, max_elev = result.get_elevation_range()
        min_dist, max_dist = result.get_distance_range()

        return [
            "",
            QCoreApplication.translate("PreviewReporter", "Geometry Range:"),
            QCoreApplication.translate(
                "PreviewReporter", "  Elevation: {} to {} m"
            ).format(round(min_elev, 1), round(max_elev, 1)),
            QCoreApplication.translate(
                "PreviewReporter", "  Distance: {} to {} m"
            ).format(round(min_dist, 1), round(max_dist, 1)),
        ]

    @staticmethod
    def format_performance_metrics(
        metrics: MetricsCollector, result: PreviewResult
    ) -> list[str]:
        """Format performance metrics into a list of strings."""
        timings = metrics.timings
        if not timings:
            return []

        lines = ["", QCoreApplication.translate("PreviewReporter", "Performance:")]

        mapping = {
            "Topography Generation": "  Topo: {}",
            "Geology Generation": "  Geol: {}",
            "Structure Generation": "  Struct: {}",
            "Rendering": "  Render: {}",
            "Total Preview Generation": "  Total: {}",
        }

        for key, template in mapping.items():
            if key in timings:
                # Special skip for geol if result says no geol (though usually timing exists if it ran)
                if key == "Geology Generation" and not result.geol:
                    continue
                if key == "Structure Generation" and not result.struct:
                    continue

                lines.append(
                    QCoreApplication.translate("PreviewReporter", template).format(
                        format_duration(timings[key])
                    )
                )

        return lines
