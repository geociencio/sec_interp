"""Interpretation management module for SecInterp main dialog.

This module handles interpretation polygons, their persistence, and attribute inheritance,
decoupling this logic from the main dialog class.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from qgis.core import QgsGeometry, QgsPointXY

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.logger_config import get_logger, log_critical_operation

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class InterpretationManager:
    """Manages interpretation polygons and their business logic."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize interpretation manager.

        Args:
            dialog: The main dialog instance.

        """
        self.dialog = dialog
        self.interpretations: list[InterpretationPolygon] = []

    def load_interpretations(self) -> None:
        """Load interpretations from the elected source (Project JSON or Vector Layer)."""
        interp_config = self.dialog.page_interpretation.get_data()

        if interp_config.get("source_type") == "layer":
            target_layer_id = interp_config.get("target_layer_id")
            if target_layer_id:
                from qgis.core import QgsProject

                target_layer = QgsProject.instance().mapLayer(target_layer_id)
                if target_layer and target_layer.isValid():
                    self.sync_from_layer(target_layer)
                    return

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
        """Save interpretations to the elected source (Project JSON or Vector Layer)."""
        interp_config = self.dialog.page_interpretation.get_data()

        if interp_config.get("source_type") == "layer":
            target_layer_id = interp_config.get("target_layer_id")
            if target_layer_id:
                from qgis.core import QgsProject

                target_layer = QgsProject.instance().mapLayer(target_layer_id)
                if target_layer and target_layer.isValid():
                    self.save_to_layer(target_layer)
                    return

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

        def json_serial(obj: Any) -> Any:
            """JSON serializer for objects not serializable by default json code."""
            if hasattr(obj, "isNull"):  # Handle QVariant (qgis.PyQt/PyQGIS)
                if obj.isNull():
                    return None
                return obj.value()
            return str(obj)

        json_data = json.dumps(data, default=json_serial)
        self.dialog.project.writeEntry("SecInterp", "interpretations", json_data)
        logger.debug(f"Saved {len(data)} interpretations to project json")

    def sync_from_layer(self, layer: Any) -> None:
        """Synchronize interpretation polygons from an external vector layer."""
        from qgis.core import QgsWkbTypes

        self.interpretations = []
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom.isNull() or geom.type() != QgsWkbTypes.PolygonGeometry:
                continue

            vertices = []
            polygon = geom.asPolygon()
            if polygon:
                for pt in polygon[0]:
                    vertices.append((pt.x(), pt.y()))

            attrs = feature.attributes()
            fields = layer.fields()

            def get_field_val(name: str, default: Any = "", _attrs=attrs, _fields=fields) -> Any:
                idx = _fields.indexOf(name)
                return (
                    _attrs[idx]
                    if idx != -1 and not isinstance(_attrs[idx], type(None))
                    else default
                )

            interp = InterpretationPolygon(
                id=str(get_field_val("id", feature.id())),
                name=str(get_field_val("name", f"Interp_{feature.id()}")),
                type=str(get_field_val("type", "lithology")),
                vertices_2d=vertices,
                attributes={},  # Add custom attribute sync here if wanted
                color=str(get_field_val("color", "#FF0000")),
                created_at=str(get_field_val("created_at", "")),
            )
            self.interpretations.append(interp)
        logger.info(
            f"Synchronized {len(self.interpretations)} interpretations from layer {layer.name()}"
        )

    def save_to_layer(self, layer: Any) -> None:
        """Save interpretation polygons to an external vector layer."""
        from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

        if not layer.isEditable():
            layer.startEditing()

        layer.deleteFeatures([f.id() for f in layer.getFeatures()])

        features_to_add = []
        fields = layer.fields()

        for interp in self.interpretations:
            feat = QgsFeature(fields)
            qgs_pts = [QgsPointXY(x, y) for x, y in interp.vertices_2d]
            feat.setGeometry(QgsGeometry.fromPolygonXY([qgs_pts]))

            def set_field(name: str, value: Any, _feat=feat, _fields=fields):
                idx = _fields.indexOf(name)
                if idx != -1:
                    _feat.setAttribute(idx, value)

            set_field("id", interp.id)
            set_field("name", interp.name)
            set_field("type", interp.type)
            set_field("color", interp.color)
            set_field("created_at", interp.created_at)

            features_to_add.append(feat)

        layer.addFeatures(features_to_add)
        layer.commitChanges()
        logger.info(f"Saved {len(features_to_add)} interpretations to layer {layer.name()}")

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
        if config.get("inherit_geology"):
            best_match, min_dist = self._check_geology_inheritance(ref_point, min_dist, best_match)

        # 2. Check Drillhole Data (Intervals)
        if config.get("inherit_drillholes"):
            best_match, min_dist = self._check_drillhole_inheritance(
                ref_point, min_dist, best_match
            )

        if best_match:
            logger.info(f"Inherited attributes from {best_match['type']}: {best_match['name']}")
            interpretation.name = best_match["name"]
            interpretation.type = best_match["type"]
            if best_match["attrs"]:
                interpretation.attributes.update(best_match["attrs"])
            interpretation.color = self.dialog.layer_factory.get_color_for_unit(
                best_match["name"]
            ).name()

    def _check_geology_inheritance(
        self, ref_point: QgsPointXY, min_dist: float, best_match: dict[str, Any] | None
    ) -> tuple[dict[str, Any] | None, float]:
        """Search for nearest geological segment."""
        geol_data = self.dialog.preview_manager.cached_data.get("geol")
        if not geol_data:
            return best_match, min_dist

        for segment in geol_data:
            if not segment.points:
                continue

            seg_min = float("inf")
            for p_dist, p_elev in segment.points:
                d = ref_point.distance(QgsPointXY(p_dist, p_elev))
                seg_min = min(d, seg_min)

            if seg_min < min_dist:
                min_dist = seg_min
                best_match = {
                    "name": segment.unit_name,
                    "type": "geology",
                    "attrs": segment.attributes,
                }
        return best_match, min_dist

    def _check_drillhole_inheritance(
        self, ref_point: QgsPointXY, min_dist: float, best_match: dict[str, Any] | None
    ) -> tuple[dict[str, Any] | None, float]:
        """Search for nearest drillhole interval."""
        dh_data = self.dialog.preview_manager.cached_data.get("drillhole")
        if not dh_data:
            return best_match, min_dist

        for dh in dh_data:
            intervals = self._extract_intervals_from_dh_data(dh)
            if not intervals:
                continue

            for interval in intervals:
                int_dist = self._calculate_min_dist_to_interval(ref_point, interval)
                if int_dist < min_dist:
                    min_dist = int_dist
                    best_match = {
                        "name": getattr(
                            interval,
                            "rock_unit",
                            getattr(interval, "unit_name", "Unknown"),
                        ),
                        "type": "drillhole",
                        "attrs": interval.attributes,
                    }
        return best_match, min_dist

    def _extract_intervals_from_dh_data(self, dh: Any) -> list[Any]:
        """Safely extract intervals from various drillhole data formats."""
        if isinstance(dh, tuple):
            LEGACY_HOLE_SIZE = 5
            INTERVALS_INDEX_LEGACY = 4
            if len(dh) == LEGACY_HOLE_SIZE:
                return dh[INTERVALS_INDEX_LEGACY]
            MIN_COMPONENTS = 3
            if len(dh) >= MIN_COMPONENTS:
                return dh[2]
        return getattr(dh, "intervals", [])

    def _calculate_min_dist_to_interval(self, ref_point: QgsPointXY, interval: Any) -> float:
        """Calculate minimum distance from reference point to interval points."""
        points = getattr(interval, "points", None)
        if not points:
            return float("inf")

        min_d = float("inf")
        for p_dist, p_elev in points:
            d = ref_point.distance(QgsPointXY(p_dist, p_elev))
            min_d = min(d, min_d)
        return min_d
