# -*- coding: utf-8 -*-
"""
Specific exporters for profile data (Shapefiles).
"""
import math
from pathlib import Path
from typing import List, Any, Dict

from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsWkbTypes,
    QgsRaster,
)
from qgis.PyQt.QtCore import QMetaType

from .base_exporter import BaseExporter
from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileLineShpExporter(BaseExporter):
    """Exports the topographic profile line to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """
        Args:
            data (dict): Must contain 'profile_data' (list of tuples) and 'crs'.
        """
        profile_data = data.get("profile_data")
        crs = data.get("crs")
        if not profile_data or not crs:
            return False

        try:
            points = [QgsPointXY(d, e) for d, e in profile_data]
            geom = QgsGeometry.fromPolylineXY(points)
            if not geom or geom.isNull():
                return False

            fields = QgsFields()
            fields.append(QgsField("id", QMetaType.Type.Int))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([1])
            writer.addFeature(feat)
            del writer
            return True
        except Exception as e:
            logger.error(f"Failed to export profile line to {output_path}: {e}")
            return False


class GeologyShpExporter(BaseExporter):
    """Exports the geological profile to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """
        Args:
            data (dict): Must contain 'line_lyr', 'raster_lyr', 'outcrop_lyr',
                         'band_number'.
        """
        line_lyr = data.get("line_lyr")
        raster_lyr = data.get("raster_lyr")
        outcrop_lyr = data.get("outcrop_lyr")
        band_number = data.get("band_number", 1)

        if not all([line_lyr, raster_lyr, outcrop_lyr]):
            return False

        try:
            line_geom, line_start, da = scu.prepare_profile_context(line_lyr)

            writer = scu.create_shapefile_writer(
                str(output_path), outcrop_lyr.crs(), outcrop_lyr.fields()
            )

            for feature in outcrop_lyr.getFeatures():
                outcrop_geom = feature.geometry()
                if not outcrop_geom or outcrop_geom.isNull():
                    continue
                if not outcrop_geom.intersects(line_geom):
                    continue

                intersection = outcrop_geom.intersection(line_geom)
                if not intersection or intersection.isNull():
                    continue

                geoms = (
                    intersection.asGeometryCollection()
                    if intersection.isMultipart()
                    else [intersection]
                )

                for geom in geoms:
                    if geom.wkbType() not in [
                        QgsWkbTypes.LineString,
                        QgsWkbTypes.LineString25D,
                    ]:
                        continue

                    points = scu.sample_elevation_along_line(
                        geom, raster_lyr, band_number, da, line_start
                    )

                    if len(points) > 1:
                        profile_geom = QgsGeometry.fromPolylineXY(points)
                        new_feat = QgsFeature(outcrop_lyr.fields())
                        new_feat.setAttributes(feature.attributes())
                        new_feat.setGeometry(profile_geom)
                        writer.addFeature(new_feat)

            del writer
            return True
        except Exception as e:
            logger.error(f"Failed to export geology profile to {output_path}: {e}")
            return False


class StructureShpExporter(BaseExporter):
    """Exports the structural profile to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """
        Args:
            data (dict): Must contain 'line_lyr', 'raster_lyr', 'struct_lyr',
                         'dip_field', 'strike_field', 'band_number',
                         'buffer_distance', 'dip_scale_factor'.
        """
        line_lyr = data.get("line_lyr")
        raster_lyr = data.get("raster_lyr")
        struct_lyr = data.get("struct_lyr")
        dip_field = data.get("dip_field")
        strike_field = data.get("strike_field")
        band_number = data.get("band_number", 1)
        buffer_distance = data.get("buffer_distance", 100)
        dip_scale_factor = data.get("dip_scale_factor", 4)

        if not all([line_lyr, raster_lyr, struct_lyr, dip_field, strike_field]):
            return False

        try:
            line_geom, line_start, da = scu.prepare_profile_context(line_lyr)
            line_az = scu.calculate_line_azimuth(line_geom)

            res = raster_lyr.rasterUnitsPerPixelX()
            L = res * dip_scale_factor
            buffer_geom = line_geom.buffer(buffer_distance, 25)

            writer = scu.create_shapefile_writer(
                str(output_path), line_lyr.crs(), struct_lyr.fields()
            )

            for f in struct_lyr.getFeatures():
                struct_geom = f.geometry()
                if not struct_geom or struct_geom.isNull():
                    continue

                if struct_geom.intersects(buffer_geom):
                    proj_dist = line_geom.lineLocatePoint(struct_geom)
                    if proj_dist < 0:
                        continue

                    proj_pt = line_geom.interpolate(proj_dist).asPoint()
                    dist = da.measureLine(line_start, proj_pt)

                    res_val = (
                        raster_lyr.dataProvider()
                        .identify(proj_pt, QgsRaster.IdentifyFormatValue)
                        .results()
                    )
                    elev = res_val.get(band_number, 0.0)

                    strike_raw = f[strike_field]
                    dip_raw = f[dip_field]

                    strike = scu.parse_strike(strike_raw)
                    dip, _ = scu.parse_dip(dip_raw)

                    if strike is not None and dip is not None:
                        app_dip = scu.calculate_apparent_dip(strike, dip, line_az)
                        rad_dip = math.radians(app_dip)

                        dy = -L * math.sin(abs(rad_dip))
                        dx = L * math.cos(abs(rad_dip))
                        if app_dip < 0:
                            dx = -dx

                        p1 = QgsPointXY(dist, elev)
                        p2 = QgsPointXY(dist + dx, elev + dy)
                        dip_line = QgsGeometry.fromPolylineXY([p1, p2])

                        new_feat = QgsFeature(struct_lyr.fields())
                        new_feat.setAttributes(f.attributes())
                        new_feat.setGeometry(dip_line)
                        writer.addFeature(new_feat)

            del writer
            return True
        except Exception as e:
            logger.error(f"Failed to export structural profile to {output_path}: {e}")
            return False


class AxesShpExporter(BaseExporter):
    """Exports the profile axes to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """
        Args:
            data (dict): Must contain 'profile_data' and 'crs'.
        """
        profile_data = data.get("profile_data")
        crs = data.get("crs")
        if not profile_data or not crs:
            return False

        try:
            dists = [p[0] for p in profile_data]
            elevs = [p[1] for p in profile_data]

            min_d, max_d = min(dists), max(dists)
            min_e, max_e = min(elevs), max(elevs)

            if max_d == min_d:
                max_d = min_d + 100
            if max_e == min_e:
                max_e = min_e + 10

            e_range = max_e - min_e
            min_e_padded = min_e - e_range * 0.05
            max_e_padded = max_e + e_range * 0.05

            lines = [
                [QgsPointXY(min_d, min_e_padded), QgsPointXY(min_d, max_e_padded)],
                [QgsPointXY(max_d, min_e_padded), QgsPointXY(max_d, max_e_padded)],
                [QgsPointXY(min_d, min_e_padded), QgsPointXY(max_d, min_e_padded)],
            ]

            fields = QgsFields()
            fields.append(QgsField("axis", QMetaType.Type.QString))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            axis_names = ["Left", "Right", "Bottom"]
            for i, points in enumerate(lines):
                feat = QgsFeature()
                geom = QgsGeometry.fromPolylineXY(points)
                feat.setGeometry(geom)
                feat.setAttributes([axis_names[i]])
                writer.addFeature(feat)

            del writer
            return True
        except Exception as e:
            logger.error(f"Failed to export axes to {output_path}: {e}")
            return False
