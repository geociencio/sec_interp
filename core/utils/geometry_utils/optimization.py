"""Geometry optimization utilities for SecInterp preview.

Handles simplification and sampling of geometric data to improve rendering performance.
"""

from __future__ import annotations

import math
from typing import Optional

from qgis.core import QgsGeometry, QgsPointXY

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class PreviewOptimizer:
    """Provides geometric optimization and sampling logic for preview rendering."""

    @staticmethod
    def decimate(
        data: list[tuple[float, float]],
        tolerance: Optional[float] = None,
        max_points: int = 1000,
    ) -> list[tuple[float, float]]:
        """Decimate line data using Douglas-Peucker algorithm.

        Args:
            data: List of (x, y) tuples
            tolerance: Simplification tolerance (if provided, overrides max_points heuristic)
            max_points: Maximum points to keep (approximate target if tolerance is None)

        Returns:
            Decimated list of (x, y) tuples
        """
        if not data or len(data) <= max_points:
            return data

        try:
            # Create QgsGeometry from points
            points = [QgsPointXY(x, y) for x, y in data]
            line = QgsGeometry.fromPolylineXY(points)

            # Determine tolerance
            if tolerance is None:
                # Auto-calculate tolerance based on max_points heuristic
                extent = line.boundingBox()
                diag = math.sqrt(extent.width() ** 2 + extent.height() ** 2)
                calculated_tolerance = diag / max_points
            else:
                calculated_tolerance = tolerance

            # Simplify
            simplified = line.simplify(calculated_tolerance)

            # Extract points
            if simplified.isMultipart():
                result_points = simplified.asMultiPolyline()[0]
            else:
                result_points = simplified.asPolyline()

            result = [(p.x(), p.y()) for p in result_points]

            logger.debug(
                f"LOD Decimation: {len(data)} -> {len(result)} points "
                f"(tol={calculated_tolerance:.2f})"
            )
        except Exception as e:
            logger.warning(f"LOD decimation failed: {e}")
            return data
        else:
            return result

    @staticmethod
    def calculate_curvature(data: list[tuple[float, float]]) -> list[float]:
        """Calculate a simple curvature metric for each point in a line.

        This approximates curvature by the angle deviation between successive segments.
        High values indicate sharper turns.

        Args:
            data: List of (x, y) tuples.

        Returns:
            List of curvature values (angles in degrees), same length as data.
        """
        if len(data) < 3:
            return [0.0] * len(data)

        curvatures = [0.0]  # First point has no preceding segment
        for i in range(1, len(data) - 1):
            p_prev = data[i - 1]
            p_curr = data[i]
            p_next = data[i + 1]

            # Vectors for segments
            v1_x = p_curr[0] - p_prev[0]
            v1_y = p_curr[1] - p_prev[1]
            v2_x = p_next[0] - p_curr[0]
            v2_y = p_next[1] - p_curr[1]

            # Dot product and magnitudes
            dot_product = v1_x * v2_x + v1_y * v2_y
            mag_v1 = math.sqrt(v1_x**2 + v1_y**2)
            mag_v2 = math.sqrt(v2_x**2 + v2_y**2)

            if mag_v1 == 0 or mag_v2 == 0:
                angle = 0.0
            else:
                # Angle between vectors
                cosine_angle = dot_product / (mag_v1 * mag_v2)
                # Clamp to avoid NaN from floating point inaccuracies
                cosine_angle = max(-1.0, min(1.0, cosine_angle))
                angle = math.degrees(math.acos(cosine_angle))

            # Angle deviation from 180 (straight line)
            curvatures.append(abs(180 - angle))

        curvatures.append(0.0)  # Last point has no succeeding segment
        return curvatures

    @classmethod
    def adaptive_sample(
        cls,
        data: list[tuple[float, float]],
        min_tolerance: float = 0.1,
        max_tolerance: float = 10.0,
        max_points: int = 1000,
    ) -> list[tuple[float, float]]:
        """Adaptively sample data based on local curvature.

        Args:
            data: List of (x, y) tuples
            min_tolerance: Minimum tolerance for high-detail areas
            max_tolerance: Maximum tolerance for low-detail areas
            max_points: Maximum points to keep (approximate target)

        Returns:
            Adaptively sampled data
        """
        if len(data) <= max_points:
            return data

        # Calculate local curvature
        curvatures = cls.calculate_curvature(data)

        # Use average curvature to set a general tolerance for the entire line
        avg_curvature = sum(curvatures) / len(curvatures)

        # Scale tolerance based on average curvature:
        # Normalize avg_curvature (assuming max possible is 180)
        normalized_curvature = avg_curvature / 180.0
        # Invert for tolerance: higher curvature means lower tolerance
        tolerance_factor = 1.0 - normalized_curvature

        # Linearly interpolate tolerance
        tolerance = min_tolerance + (max_tolerance - min_tolerance) * tolerance_factor
        tolerance = max(min_tolerance, min(max_tolerance, tolerance))

        logger.debug(
            f"Adaptive sampling: Avg curvature={avg_curvature:.2f}, "
            f"calculated tolerance={tolerance:.2f}"
        )

        # Now use the calculated tolerance for decimation
        return cls.decimate(data, tolerance=tolerance, max_points=max_points)
