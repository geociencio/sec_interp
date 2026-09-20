"""Interpretation persistence mixin (project JSON and vector layers)."""

from __future__ import annotations

import json
from typing import Any

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class InterpretationPersistenceMixin:
    """Load/save interpretations from the project JSON or an external layer."""

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
        from qgis.core import QgsFeatureRequest, QgsWkbTypes

        self.interpretations = []
        # Filter by the layer extent so the request is served through the
        # spatial index instead of scanning every feature unfiltered.
        request = QgsFeatureRequest().setFilterRect(layer.extent())
        for feature in layer.getFeatures(request):
            geom = feature.geometry()
            if geom.isNull() or geom.type() != QgsWkbTypes.GeometryType.PolygonGeometry:
                continue

            vertices = []
            polygon = geom.asPolygon()
            if polygon:
                for pt in polygon[0]:
                    vertices.append((pt.x(), pt.y()))

            attrs = feature.attributes()
            fields = layer.fields()

            def get_field_val(name: str, default: Any = "", _attrs=attrs, _fields=fields) -> Any:
                """Get attribute value by field name."""
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

            def set_field(name: str, value: Any, _feat=feat, _fields=fields) -> None:
                """Set feature attribute by field name."""
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
