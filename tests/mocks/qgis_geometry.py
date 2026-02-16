"""QGIS Geometry mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQgsBase


class MockQgsGeometry(MockQgsBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._polyline = []
        self._polygons = []
        self._point = MockQgsPointXY()
        self._wkb_type = 2  # Default LineString
        self._wkt = None

        if args:
            arg = args[0]
            if isinstance(arg, MockQgsGeometry):
                self._polyline = list(arg._polyline)
                self._wkb_type = arg._wkb_type
                self._point = MockQgsPointXY(arg._point.x(), arg._point.y())
                self._polygons = [list(r) for r in arg._polygons]
                self._wkt = arg._wkt
            elif "MockQgsPolygon" in str(type(arg)) or "Polygon" in str(type(arg)):
                self._polygons = arg._rings if hasattr(arg, "_rings") else []
                self._wkb_type = 3  # Default Polygon
                if self._polygons and self._polygons[0]:
                    first_pt = self._polygons[0][0]
                    # Check for z method OR _z attribute
                    if hasattr(first_pt, "z") or hasattr(first_pt, "_z"):
                        self._wkb_type = 1003  # PolygonZ
            elif "MockQgsLineString" in str(type(arg)) or "LineString" in str(
                type(arg)
            ):
                self._polyline = arg._points if hasattr(arg, "_points") else []
                self._wkb_type = 2  # LineString
                if self._polyline:
                    first_pt = self._polyline[0]
                    if hasattr(first_pt, "z") or hasattr(first_pt, "_z"):
                        self._wkb_type = 1002  # LineStringZ
            elif "MockQgsPoint" in str(type(arg)) or "Point" in str(type(arg)):
                self._point = MockQgsPointXY(arg.x(), arg.y())
                self._wkb_type = 1  # Point
                if hasattr(arg, "z") or hasattr(arg, "_z"):
                    self._wkb_type = 1001  # PointZ
            else:
                # Default fallback
                self._point = MockQgsPointXY(0, 0)

    @staticmethod
    def fromPolygonXY(rings):
        geom = MockQgsGeometry()
        geom._polygons = rings
        geom._wkb_type = 3  # Polygon
        return geom

    @staticmethod
    def fromPolylineXY(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 2  # LineString
        return geom

    @staticmethod
    def fromPolylineZ(points):
        geom = MockQgsGeometry()
        geom._polyline = points
        geom._wkb_type = 1002  # LineStringZ
        return geom

    @staticmethod
    def fromPolygonZ(rings):
        geom = MockQgsGeometry()
        geom._polygons = rings
        geom._wkb_type = 1003  # PolygonZ
        return geom

    @staticmethod
    def fromPolyline(points):
        if points and (hasattr(points[0], "z") or hasattr(points[0], "_z")):
            return MockQgsGeometry.fromPolylineZ(points)
        return MockQgsGeometry.fromPolylineXY(points)

    @staticmethod
    def fromPointXY(point):
        geom = MockQgsGeometry()
        geom._point = point
        geom._wkb_type = 1
        return geom

    @staticmethod
    def fromWkt(wkt):
        geom = MockQgsGeometry()
        geom._wkt = wkt
        if not wkt:
            return geom

        upper_wkt = wkt.upper()
        import re

        if "POINT" in upper_wkt:
            geom._wkb_type = 1
            m = re.search(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)", upper_wkt)
            if m:
                geom._point = MockQgsPointXY(float(m.group(1)), float(m.group(2)))
        elif "LINESTRING" in upper_wkt:
            geom._wkb_type = 2
            m = re.search(r"LINESTRING\s*\((.*)\)", upper_wkt)
            if m:
                content = m.group(1)
                pts = []
                for p_str in content.split(","):
                    xy = p_str.strip().split()
                    if len(xy) >= 2:
                        pts.append(MockQgsPointXY(float(xy[0]), float(xy[1])))
                geom._polyline = pts
        elif "POLYGON" in upper_wkt:
            geom._wkb_type = 3

        return geom

    def asWkt(self):
        if self._wkt:
            return self._wkt
        if self._wkb_type in [1, 1001]:
            return f"POINT({self._point.x()} {self._point.y()})"
        if self._polyline:
            pts = ", ".join([f"{p.x()} {p.y()}" for p in self._polyline])
            return f"LINESTRING ({pts})"
        return "GEOMETRYCOLLECTION EMPTY"

    def vertices(self):
        if self._polyline:
            return self._polyline
        if self._wkt and "LINESTRING" in self._wkt.upper():
            try:
                content = self._wkt.upper().split("(")[1].split(")")[0]
                pts = []
                for pair in content.split(","):
                    coords = pair.strip().split()
                    pts.append(MockQgsPointXY(float(coords[0]), float(coords[1])))
                return pts
            except Exception:
                return []
        if self._wkb_type in [1, 1001]:
            return [self._point]
        return []

    def asPolyline(self):
        return self.vertices()

    def asPolygon(self):
        return self._polygons

    def is3D(self):
        return self._wkb_type >= 1000

    def wkbType(self):
        return self._wkb_type

    def pointN(self, n):
        pts = self._polyline if self._polyline else self.vertices()
        if 0 <= n < len(pts):
            return pts[n]
        return None

    def asMultiPolygon(self):
        return [self._polygons]

    def asMultiPolyline(self):
        return [self._polyline]

    def intersection(self, other):
        return self.clone()

    def intersects(self, other):
        return True

    def isEmpty(self):
        if self._wkb_type in [1, 1001]:
            return False
        return not (self._polyline or self._polygons or self._wkt)

    def isNull(self):
        return False

    def isMultipart(self):
        return False

    def isGeosValid(self):
        return True

    def clone(self):
        new_geom = MockQgsGeometry()
        new_geom._polyline = list(self._polyline)
        new_geom._polygons = [list(r) for r in self._polygons]
        if self._point:
            new_geom._point = MockQgsPointXY(self._point.x(), self._point.y())
        else:
            new_geom._point = MockQgsPointXY(0, 0)
        new_geom._wkb_type = self._wkb_type
        new_geom._wkt = self._wkt
        return new_geom

    def centroid(self):
        p = self._point
        if self._polyline:
            p = self._polyline[0]
        elif self._polygons and self._polygons[0]:
            p = self._polygons[0][0]
        if p is None:
            p = MockQgsPointXY(0, 0)
        return MockQgsGeometry.fromPointXY(p)

    def makeValid(self):
        return self

    def asPoint(self):
        return self._point

    def type(self):
        if self._wkb_type in [1, 1001]:
            return 0
        if self._wkb_type in [2, 1002, 4, 1004]:
            return 1
        if self._wkb_type in [3, 1003, 6, 1006]:
            return 2
        return 4

    def length(self):
        verts = self.vertices()
        if len(verts) < 2:
            return 0.0
        total = 0.0
        for i in range(len(verts) - 1):
            p1, p2 = verts[i], verts[i + 1]
            total += ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5
        return total

    def interpolate(self, distance):
        return MockQgsGeometry.fromPointXY(MockQgsPointXY(distance, 0.0))

    def lineLocatePoint(self, point_geom):
        if isinstance(point_geom, MockQgsGeometry):
            return point_geom.asPoint().x()
        return 0.0

    def nearestPoint(self, other):
        if self.type() == 1 and self.vertices():
            verts = self.vertices()
            if all(pt.y() == 0 for pt in verts):
                try:
                    other_pt = other.asPoint()
                    return MockQgsGeometry.fromPointXY(
                        MockQgsPointXY(other_pt.x(), 0.0)
                    )
                except AttributeError:
                    pass
        return other

    def simplify(self, tolerance):
        return self

    def buffer(self, distance, segments):
        geom = MockQgsGeometry()
        geom._wkb_type = 3  # Polygon
        geom._polygons = [
            [
                MockQgsPointXY(0, 0),
                MockQgsPointXY(1, 1),
                MockQgsPointXY(0, 1),
                MockQgsPointXY(0, 0),
            ]
        ]
        return geom

    def densifyByDistance(self, distance):
        return self

    def boundingBox(self):
        verts = self.vertices()
        if not verts:
            return MagicMock()
        min_x = min(p.x() for p in verts)
        max_x = max(p.x() for p in verts)
        min_y = min(p.y() for p in verts)
        max_y = max(p.y() for p in verts)
        box = MagicMock()
        box.width.return_value = max_x - min_x
        box.height.return_value = max_y - min_y
        box.xMinimum.return_value = min_x
        box.xMaximum.return_value = max_x
        box.yMinimum.return_value = min_y
        box.yMaximum.return_value = max_y
        return box

    def transform(self, transform):
        pass

    def vertexAt(self, index):
        if self._wkb_type == 1 or self._wkb_type == 1001:
            return self._point
        all_pts = []
        if self._polyline:
            all_pts = self._polyline
        elif self._polygons and self._polygons[0]:
            ring = self._polygons[0]
            all_pts = ring.points() if hasattr(ring, "points") else ring
        if 0 <= index < len(all_pts):
            return all_pts[index]
        return MockQgsPoint(0, 0, 0)


class MockQgsLineString(MockQgsBase):
    def __init__(self, points):
        super().__init__()
        self._points = points

    def points(self):
        return self._points


class MockQgsPolygon(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._rings = []

    def setExteriorRing(self, ring):
        self._rings = [ring.points() if hasattr(ring, "points") else ring]

    def addInteriorRing(self, ring):
        self._rings.append(ring.points() if hasattr(ring, "points") else ring)


class MockQgsPoint(MockQgsBase):
    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        if isinstance(x, (MockQgsPoint, MockQgsPointXY)):
            self._x, self._y, self._z = x.x(), x.y(), getattr(x, "z", lambda: 0)()
        elif isinstance(x, (tuple, list)):
            self._x, self._y = float(x[0]), float(x[1])
            self._z = float(x[2]) if len(x) > 2 else 0.0
        else:
            self._x, self._y, self._z = float(x), float(y), float(z)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def setX(self, x):
        self._x = float(x)

    def setY(self, y):
        self._y = float(y)

    def setZ(self, z):
        self._z = float(z)

    def __iter__(self):
        yield self._x
        yield self._y


class MockQgsPointXY(MockQgsPoint):
    def __init__(self, x=0, y=0):
        if isinstance(x, (MockQgsPoint, MockQgsPointXY)):
            super().__init__(x.x(), x.y(), 0)
        else:
            super().__init__(x, y, 0)

    def distance(self, other):
        return ((self._x - other.x()) ** 2 + (self._y - other.y()) ** 2) ** 0.5

    def azimuth(self, other):
        import math

        dx, dy = other.x() - self._x, other.y() - self._y
        angle = math.degrees(math.atan2(dx, dy))
        if angle < 0:
            angle += 360
        return angle

    def compare(self, other, epsilon=1e-6):
        return self.distance(other) < epsilon
