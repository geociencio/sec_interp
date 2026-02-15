"""Controller for SecInterp profile data generation.

This module handles the orchestration of various data generation services
(topography, geology, structures, drillholes) and manages result caching.
"""

from __future__ import annotations

import time
from typing import Any

from qgis.core import QgsDistanceArea, QgsProject
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core import utils as scu
from sec_interp.core.config import ConfigService
from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import PreviewParams
from sec_interp.core.exceptions import ProcessingError
from sec_interp.core.services import (
    DrillholeService,
    GeologyService,
    ProfileService,
    StructureService,
)
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileController:
    """Orchestrates data generation services for SecInterp profile creation."""

    def __init__(self) -> None:
        """Initialize services and the data cache."""
        self.config_service = ConfigService()
        self.data_cache = DataCache()
        self.profile_service = ProfileService()
        self.geology_service = GeologyService()
        self.structure_service = StructureService()
        self.drillhole_service = DrillholeService()
        self._connected_layers: list[Any] = []
        logger.debug("ProfileController initialized")

    def connect_layer_notifications(self, layers: list[Any]) -> None:
        """Connect to layer signals for automatic cache invalidation on data changes.

        Args:
            layers: List of QgsMapLayer objects to monitor.

        """
        self.disconnect_layer_notifications()
        for layer in layers:
            if not layer:
                continue
            # When layer data changes, clear cache for its bucket or altogether
            layer.dataChanged.connect(self.data_cache.clear)
            self._connected_layers.append(layer)
            logger.debug(f"Connected cache invalidation to layer: {layer.name()}")

    def disconnect_layer_notifications(self) -> None:
        """Disconnect from all previously connected layer signals."""
        for layer in self._connected_layers:
            try:
                # Disconnect specific slot to avoid breaking other connections
                layer.dataChanged.disconnect(self.data_cache.clear)
                logger.debug(f"Disconnected cache invalidation from layer: {layer.name()}")
            except (TypeError, RuntimeError):
                # Signal might not be connected or layer might be deleted
                pass
        self._connected_layers.clear()

    def get_cached_data(self, inputs: dict[str, Any]) -> dict[str, Any] | None:
        """Retrieve data from cache if available for the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.

        Returns:
            Cached data dictionary if found, else None.

        """
        cache_key = self.data_cache.get_cache_key(inputs)
        return self.data_cache.get(cache_key)

    def cache_data(self, inputs: dict[str, Any], data: dict[str, Any]) -> None:
        """Cache the generated data resulting from the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.
            data: Data dictionary to cache.

        """
        cache_key = self.data_cache.get_cache_key(inputs)
        self.data_cache.set(cache_key, data)

    def generate_profile_data(
        self, params: PreviewParams
    ) -> tuple[
        list[tuple[float, float]],
        list[Any] | None,
        list[Any] | None,
        Any | None,
        list[str],
    ]:
        """Unified method to generate all profile data components with granular caching."""
        params.validate()
        messages = []
        cache_meta = {
            "max_points": params.max_points,
            "canvas_width": params.canvas_width,
            "timestamp": time.time(),
        }

        # 1. Topography
        profile_data = self._process_topography(params, cache_meta, messages)

        # 2. Geology
        geol_data = self._process_geology(params, cache_meta, messages)

        # 3. Structure
        struct_data = self._process_structures(params, cache_meta, messages)

        # 4. Drillholes
        drillhole_data = self._process_drillholes(params, cache_meta, messages)

        return profile_data, geol_data, struct_data, drillhole_data, messages

    def _get_cache_sub_key(self, param_values: list[Any]) -> str:
        """Generate a sub-key for caching specific components."""
        import hashlib

        hasher = hashlib.md5()  # nosec B324
        for val in param_values:
            from qgis.core import QgsMapLayer

            if isinstance(val, QgsMapLayer):
                hasher.update(val.id().encode("utf-8"))
            else:
                hasher.update(str(val).encode("utf-8"))
        return hasher.hexdigest()

    def _process_topography(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[tuple[float, float]]:
        """Process topographic profile data."""
        topo_key = self._get_cache_sub_key([params.band_num, params.max_points])
        profile_data = self.data_cache.get("topo", topo_key)
        if profile_data:
            logger.debug("Cache hit: Topography")
        else:
            profile_data = self.profile_service.generate_topographic_profile(
                params.line_layer, params.raster_layer, params.band_num
            )
            if not profile_data:
                raise ProcessingError(
                    QCoreApplication.translate(
                        "ProfileController",
                        "No topographic profile data was generated.",
                    )
                )
            self.data_cache.set("topo", topo_key, profile_data, cache_meta)
        messages.append(
            QCoreApplication.translate(
                "ProfileController",
                "✓ Data processed successfully!\n\nTopography: {0} points",
            ).format(len(profile_data))
        )
        return profile_data

    def _process_geology(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[Any] | None:
        """Process geological profile data."""
        if not params.outcrop_layer:
            return None

        geol_key = self._get_cache_sub_key(
            [params.outcrop_layer, params.outcrop_name_field, params.band_num]
        )
        geol_data = self.data_cache.get("geol", geol_key)
        if geol_data:
            logger.debug("Cache hit: Geology")
            messages.append(
                QCoreApplication.translate("ProfileController", "Geology: {0} segments").format(
                    len(geol_data)
                )
            )
        else:
            geol_data = self.geology_service.generate_geological_profile(
                params.line_layer,
                params.raster_layer,
                params.outcrop_layer,
                params.outcrop_name_field,
                params.band_num,
            )
            if geol_data:
                self.data_cache.set("geol", geol_key, geol_data, cache_meta)
                messages.append(
                    QCoreApplication.translate("ProfileController", "Geology: {0} segments").format(
                        len(geol_data)
                    )
                )
            else:
                messages.append(
                    QCoreApplication.translate("ProfileController", "Geology: No intersections")
                )
        return geol_data

    def _process_structures(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[Any] | None:
        """Process structural profile data."""
        if not params.struct_layer:
            return None

        struct_key = self._get_cache_sub_key(
            [
                params.struct_layer,
                params.buffer_dist,
                params.dip_field,
                params.strike_field,
                params.band_num,
            ]
        )
        struct_data = self.data_cache.get("struct", struct_key)
        if struct_data:
            logger.debug("Cache hit: Structure")
            messages.append(
                QCoreApplication.translate("ProfileController", "Structures: {0} points").format(
                    len(struct_data)
                )
            )
        else:
            line_feat = next(params.line_layer.getFeatures(), None)
            if line_feat:
                line_geom = line_feat.geometry()
                if line_geom and not line_geom.isNull():
                    line_start = scu.get_line_start_point(line_geom)
                    line_azimuth = scu.calculate_line_azimuth(line_geom)

                    da = QgsDistanceArea()
                    da.setSourceCrs(
                        params.line_layer.crs(),
                        QgsProject.instance().transformContext(),
                    )
                    da.setEllipsoid(QgsProject.instance().ellipsoid())

                    # 1. Detach structures
                    detached_structs = self.structure_service.detach_structures(
                        params.struct_layer, line_geom, params.buffer_dist
                    )

                    # 2. Project structures
                    struct_data = self.structure_service.project_structures(
                        line_geom=line_geom,
                        line_start=line_start,
                        da=da,
                        raster_lyr=params.raster_layer,
                        struct_data=detached_structs,
                        buffer_m=params.buffer_dist,
                        line_az=line_azimuth,
                        dip_field=params.dip_field,
                        strike_field=params.strike_field,
                        band_number=params.band_num,
                    )
                    if struct_data:
                        self.data_cache.set("struct", struct_key, struct_data, cache_meta)
                        messages.append(
                            QCoreApplication.translate(
                                "ProfileController", "Structures: {0} points"
                            ).format(len(struct_data))
                        )
                    else:
                        messages.append(
                            QCoreApplication.translate(
                                "ProfileController", "Structures: None in {0}m buffer"
                            ).format(params.buffer_dist)
                        )
        return struct_data

    def _process_drillholes(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> Any | None:
        """Process drillhole profile data."""
        if not params.collar_layer:
            return None

        drill_key = self._get_cache_sub_key(
            [
                params.collar_layer,
                params.survey_layer,
                params.interval_layer,
                params.buffer_dist,
            ]
        )
        drillhole_data = self.data_cache.get("drill", drill_key)

        if drillhole_data:
            logger.debug("Cache hit: Drillholes")
            return drillhole_data

        drillhole_data = self.drillhole_service.generate_drillhole_data(params)

        if drillhole_data:
            self.data_cache.set("drill", drill_key, drillhole_data, cache_meta)

        return drillhole_data
