"""Exporters for drillhole data (Shapefiles)."""

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter


logger = get_logger(__name__)


class DrillholeTraceShpExporter(BaseExporter):
    """Exports drillhole traces to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export drillhole traces to a Shapefile.
        
        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = QgsFields()
            fields.append(QgsField("hole_id", QMetaType.Type.QString))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            for hole_id, traces, _ in drillhole_data:
                if not traces or len(traces) < 2:
                    continue

                # traces is list of (dist, elev)
                points = [QgsPointXY(d, e) for d, e in traces]
                geom = QgsGeometry.fromPolylineXY(points)
                
                if not geom or geom.isNull():
                    continue

                feat = QgsFeature(fields)
                feat.setGeometry(geom)
                feat.setAttribute("hole_id", hole_id)
                writer.addFeature(feat)

            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export drillhole traces to {output_path}")
            return False


class DrillholeIntervalShpExporter(BaseExporter):
    """Exports drillhole intervals to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export drillhole intervals to a Shapefile.
        
        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = QgsFields()
            fields.append(QgsField("hole_id", QMetaType.Type.QString))
            fields.append(QgsField("from_depth", QMetaType.Type.Double))
            fields.append(QgsField("to_depth", QMetaType.Type.Double))
            fields.append(QgsField("unit", QMetaType.Type.QString))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            for hole_id, _, segments in drillhole_data:
                if not segments:
                    continue
                
                for segment in segments:
                    # segment is GeologySegment
                    if not segment.points or len(segment.points) < 2:
                        continue
                        
                    points = [QgsPointXY(d, e) for d, e in segment.points]
                    geom = QgsGeometry.fromPolylineXY(points)
                    
                    if not geom or geom.isNull():
                        continue

                    feat = QgsFeature(fields)
                    feat.setGeometry(geom)
                    feat.setAttribute("hole_id", hole_id)
                    
                    # Get attributes from segment
                    # We packed them as {"unit": lith, "from": fd, "to": td}
                    attrs = segment.attributes
                    feat.setAttribute("from_depth", attrs.get("from", 0.0))
                    feat.setAttribute("to_depth", attrs.get("to", 0.0))
                    feat.setAttribute("unit", segment.unit_name)
                    
                    writer.addFeature(feat)

            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export drillhole intervals to {output_path}")
            return False
