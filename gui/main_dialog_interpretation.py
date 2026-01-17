"""Interpretation management module for SecInterp main dialog.

This module handles interpretation polygons, their persistence, and attribute inheritance,
decoupling this logic from the main dialog class.
"""

import json
from typing import TYPE_CHECKING, Any

from qgis.core import QgsGeometry, QgsPointXY

from sec_interp.core.types import InterpretationPolygon
from sec_interp.logger_config import get_logger, log_critical_operation

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class DialogInterpretationManager:
    """Manages interpretation polygons and their business logic."""

    def __init__(self, dialog: "SecInterpDialog"):
        """Initialize interpretation manager.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog
        self.interpretations: list[InterpretationPolygon] = []

    def load_interpretations(self) -> None:
        """Load interpretations from the QGIS project."""
        if not self.dialog.project:
            return

        json_data, ok = self.dialog.project.readEntry("SecInterp", "interpretations", "[]")
        if not ok or not json_data:
            return

        try:
            data = json.loads(json_data)
            self.interpretations = []
            for item in data:
                interp = InterpretationPolygon(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    type=item.get("type", "lithology"),
                    vertices_2d=[tuple(v) for v in item.get("vertices_2d", [])],
                    attributes=item.get("attributes", {}),
                    color=item.get("color", "#FF0000"),
                    created_at=item.get("created_at", ""),
                )
                self.interpretations.append(interp)
            logger.info(f"Loaded {len(self.interpretations)} interpretations from project")
        except Exception:
            logger.exception("Failed to load interpretations")

    def save_interpretations(self) -> None:
        """Save interpretations to the QGIS project."""
        if not self.dialog.project:
            return

        data = []
        for interp in self.interpretations:
            data.append(
                {
                    "id": interp.id,
                    "name": interp.name,
                    "type": interp.type,
                    "vertices_2d": interp.vertices_2d,
                    "attributes": interp.attributes,
                    "color": interp.color,
                    "created_at": interp.created_at,
                }
            )

        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code."""
            if hasattr(obj, "isNull"):  # Handle QVariant (PyQt5/PyQGIS)
                if obj.isNull():
                    return None
                return obj.value()
            return str(obj)

        json_data = json.dumps(data, default=json_serial)
        self.dialog.project.writeEntry("SecInterp", "interpretations", json_data)
        logger.debug(f"Saved {len(data)} interpretations to project")

    def handle_interpretation_finished(self, interpretation: InterpretationPolygon) -> None:
        """Process a finished interpretation polygon.

        Args:
            interpretation: The finished interpretation polygon.

        """
        from qgis.PyQt.QtWidgets import QDialog

        from .dialogs.interpretation_properties_dialog import (
            InterpretationPropertiesDialog,
        )

        log_critical_operation(
            logger,
            "handle_interpretation_finished",
            polygon_id=interpretation.id,
            vertices=len(interpretation.vertices_2d),
        )

        # 1. Prepare for inheritance
        interp_config = self.dialog.page_interpretation.get_data()

        # Try to inherit attributes if enabled
        if interp_config.get("inherit_geology") or interp_config.get("inherit_drillholes"):
            self.apply_attribute_inheritance(interpretation, interp_config)

        # 2. Show properties dialog
        dlg = InterpretationPropertiesDialog(
            interpretation, interp_config.get("custom_fields"), self.dialog
        )

        if dlg.exec_() != QDialog.Accepted:
            logger.info(f"Interpretation canceled by user: {interpretation.id}")
            # Deactivate interpretation tool anyway
            self.dialog.preview_widget.btn_interpret.setChecked(False)
            return

        # Store interpretation
        self.interpretations.append(interpretation)
        self.save_interpretations()
        logger.info(
            f"Interpretation polygon added: {interpretation.id} "
            f"({len(interpretation.vertices_2d)} vertices)"
        )

        # Display feedback in results area
        msg = (
            f"<b>{self.dialog.tr('Interpretation Finished')}</b><br>"
            f"<b>{self.dialog.tr('Name')}:</b> {interpretation.name}<br>"
            f"<b>{self.dialog.tr('Vertices')}:</b> {len(interpretation.vertices_2d)}<br>"
            f"<b>ID:</b> {interpretation.id[:8]}..."
        )
        self.dialog.preview_widget.results_text.setHtml(msg)
        self.dialog.preview_widget.results_group.setCollapsed(False)

        # Deactivate interpretation tool
        self.dialog.preview_widget.btn_interpret.setChecked(False)

        # Update preview to show the new polygon
        self.dialog.update_preview_from_checkboxes()

    def apply_attribute_inheritance(
        self, interpretation: InterpretationPolygon, config: dict[str, Any]
    ) -> None:
        """Inherit attributes from nearest geology or drillhole data."""
        # Use centroid or first vertex as reference point
        poly_geom = QgsGeometry.fromPolygonXY(
            [[QgsPointXY(x, y) for x, y in interpretation.vertices_2d]]
        )
        ref_point = poly_geom.centroid().asPoint()

        best_match = None
        min_dist = float("inf")

        # 1. Check Geology Data
        if config.get("inherit_geology") and self.dialog.preview_manager.cached_data.get("geol"):
            for segment in self.dialog.preview_manager.cached_data["geol"]:
                if not segment.points:
                    continue

                seg_min_dist = float("inf")
                for p_dist, p_elev in segment.points:
                    d = ref_point.distance(QgsPointXY(p_dist, p_elev))
                    seg_min_dist = min(d, seg_min_dist)

                if seg_min_dist < min_dist:
                    min_dist = seg_min_dist
                    best_match = {
                        "name": segment.unit_name,
                        "type": "geology",
                        "attrs": segment.attributes,
                    }

        # 2. Check Drillhole Data (Intervals)
        if config.get("inherit_drillholes") and self.dialog.preview_manager.cached_data.get(
            "drillhole"
        ):
            for dh in self.dialog.preview_manager.cached_data["drillhole"]:
                extracted_intervals = []
                if isinstance(dh, tuple) and len(dh) >= 3:
                    extracted_intervals = dh[2]
                elif hasattr(dh, "intervals"):
                    extracted_intervals = dh.intervals

                if not extracted_intervals:
                    continue

                for interval in extracted_intervals:
                    if not interval.points:
                        continue

                    int_min_dist = float("inf")
                    for p_dist, p_elev in interval.points:
                        d = ref_point.distance(QgsPointXY(p_dist, p_elev))
                        int_min_dist = min(d, int_min_dist)

                    if int_min_dist < min_dist:
                        min_dist = int_min_dist
                        unit_name = getattr(
                            interval,
                            "rock_unit",
                            getattr(interval, "unit_name", "Unknown"),
                        )

                        best_match = {
                            "name": unit_name,
                            "type": "drillhole",
                            "attrs": interval.attributes,
                        }

        if best_match:
            logger.info(f"Inherited attributes from {best_match['type']}: {best_match['name']}")
            interpretation.name = best_match["name"]
            interpretation.type = best_match["type"]
            if best_match["attrs"]:
                interpretation.attributes.update(best_match["attrs"])
            interpretation.color = self.dialog.layer_factory.get_color_for_unit(
                best_match["name"]
            ).name()
