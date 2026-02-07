from __future__ import annotations

"""Processing logic for Outcrop intersections."""

from typing import Any

from qgis.core import QgsFeatureRequest, QgsGeometry, QgsVectorLayer


class OutcropProcessor:
    """Handles extraction and intersection of outcrop features."""

    def extract_outcrop_data(
        self,
        line_geom: QgsGeometry,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
    ) -> list[dict[str, Any]]:
        """Extract outcrop features intersecting the line bounding box (detached).

        Args:
            line_geom: Section line geometry.
            outcrop_lyr: Outcrop vector layer.
            outcrop_name_field: Field for geological unit names.

        Returns:
            List of detached outcrop dictionaries.

        """
        outcrop_data = []
        line_bbox = line_geom.boundingBox()
        request = QgsFeatureRequest().setFilterRect(line_bbox)

        for feature in outcrop_lyr.getFeatures(request):
            if not feature.hasGeometry():
                continue

            attrs = dict(zip(feature.fields().names(), feature.attributes(), strict=False))
            try:
                unit_name = str(feature[outcrop_name_field])
            except KeyError:
                unit_name = "Unknown"

            outcrop_data.append(
                {
                    "wkt": feature.geometry().asWkt(),
                    "attrs": attrs,
                    "unit_name": unit_name,
                }
            )
        return outcrop_data
