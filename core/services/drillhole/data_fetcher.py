from __future__ import annotations

"""Data Fetching logic for Drillhole child layers."""

from typing import Any

from qgis.core import QgsFeature, QgsFeatureRequest, QgsVectorLayer


class DataFetcher:
    """Handles bulk fetching of survey and interval data from QGIS layers."""

    def fetch_bulk_data(
        self, layer: QgsVectorLayer, hole_ids: set[Any], fields: dict[str, str]
    ) -> dict[Any, list[tuple[Any, ...]]]:
        """Fetch data for multiple holes in a single pass."""
        if not self._validate_fields(layer, fields):
            return {}

        result_map: dict[Any, list[tuple]] = {}
        if not hole_ids:
            return {}

        id_f = fields["id"]
        is_survey = "depth" in fields

        ids_str = ", ".join([f"'{hid!s}'" for hid in hole_ids])
        request = QgsFeatureRequest().setFilterExpression(f'"{id_f}" IN ({ids_str})')

        for feat in layer.getFeatures(request):
            hole_id = feat[id_f]
            data = self._extract_data_tuple(feat, fields, is_survey)
            if data:
                result_map.setdefault(hole_id, []).append(data)

        # Sort surveys by depth
        if is_survey:
            for h_id in result_map:
                result_map[h_id].sort(key=lambda x: x[0])

        return result_map

    def _validate_fields(self, layer: QgsVectorLayer, fields: dict[str, str]) -> bool:
        """Validate fields for bulk fetching."""
        if not layer or not layer.isValid():
            return False

        id_f = fields.get("id")
        if not id_f or layer.fields().indexFromName(id_f) == -1:
            return False

        is_survey = "depth" in fields
        required = ["depth", "azim", "incl"] if is_survey else ["from", "to", "lith"]

        for field_key in required:
            f_name = fields.get(field_key)
            if not f_name or layer.fields().indexFromName(f_name) == -1:
                return False

        return True

    def _extract_data_tuple(
        self, feat: QgsFeature, fields: dict[str, str], is_survey: bool
    ) -> tuple[float, float, Any] | None:
        """Extract a data tuple from a feature based on its role."""
        try:
            if is_survey:
                return (
                    float(feat[fields["depth"]]),
                    float(feat[fields["azim"]]),
                    float(feat[fields["incl"]]),
                )
            else:
                return (
                    float(feat[fields["from"]]),
                    float(feat[fields["to"]]),
                    str(feat[fields["lith"]]),
                )
        except (ValueError, TypeError, KeyError):
            return None
