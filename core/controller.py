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
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor
from sec_interp.core.services.drillhole.data_fetcher import DataFetcher
from sec_interp.core.services.drillhole.drillhole_orchestrator import (
    DrillholeTaskOrchestrator,
)
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine
from sec_interp.core.services.geology.outcrop_processor import OutcropProcessor
from sec_interp.core.services.geology.profile_sampler import ProfileSampler
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileController:
    """Orchestrates data generation services for SecInterp profile creation."""

    def __init__(self) -> None:
        """Initialize services and the data cache using Dependency Injection."""
        self.config_service = ConfigService()
        self.data_cache = DataCache()

        # 1. Shared Infrastructure
        self.data_fetcher = DataFetcher()

        # 2. Domain Processors
        self.collar_processor = CollarProcessor()
        self.survey_processor = SurveyProcessor()
        self.interval_processor = IntervalProcessor()
        self.trajectory_engine = TrajectoryEngine()
        self.profile_sampler = ProfileSampler()
        self.outcrop_processor = OutcropProcessor()

        # 3. Services (with Dependency Injection)
        self.profile_service = ProfileService()
        self.geology_service = GeologyService(
            profile_sampler=self.profile_sampler,
            outcrop_processor=self.outcrop_processor,
        )
        self.structure_service = StructureService()
        self.drillhole_service = DrillholeService(
            collar_processor=self.collar_processor,
            survey_processor=self.survey_processor,
            interval_processor=self.interval_processor,
            data_fetcher=self.data_fetcher,
            trajectory_engine=self.trajectory_engine,
        )
        self.drillhole_orchestrator = DrillholeTaskOrchestrator(self.drillhole_service)

        self._connected_layers: list[Any] = []
        logger.debug("ProfileController initialized with DI")

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

    def _resolve_layer(self, layer_ref: Any) -> Any:
        """Resolve a layer reference (ID or object) to a QgsMapLayer."""
        from qgis.core import QgsProject

        if not isinstance(layer_ref, str) or not layer_ref:
            return layer_ref

        return QgsProject.instance().mapLayer(str(layer_ref))

    def _get_cache_sub_key(self, param_values: list[Any]) -> str:
        """Generate a sub-key for caching specific components."""
        import hashlib

        hasher = hashlib.md5()  # nosec B324
        for val in param_values:
            from qgis.core import QgsMapLayer

            if isinstance(val, QgsMapLayer | str):
                # If it's a layer object, use its ID. If it's already an ID, use it directly.
                layer_id = val.id() if hasattr(val, "id") else str(val)
                hasher.update(layer_id.encode("utf-8"))
            else:
                hasher.update(str(val).encode("utf-8"))
        return hasher.hexdigest()

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("ProfileController", message)

    def _process_topography(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[tuple[float, float]]:
        """Process topographic profile data."""
        topo_key = self._get_cache_sub_key([params.band_num, params.max_points])
        profile_data = self.data_cache.get("topo", topo_key)
        if profile_data:
            logger.debug("Cache hit: Topography")
        else:
            line_lyr = self._resolve_layer(params.line_layer)
            raster_lyr = self._resolve_layer(params.raster_layer)

            if not line_lyr or not raster_lyr:
                raise ProcessingError(self.tr("Required layers for topography are missing."))

            profile_data = self.profile_service.generate_topographic_profile(
                line_lyr, raster_lyr, params.band_num
            )
            if not profile_data:
                raise ProcessingError(self.tr("No topographic profile data was generated."))
            self.data_cache.set("topo", topo_key, profile_data, cache_meta)
        messages.append(
            self.tr("✓ Data processed successfully!\n\nTopography: {0} points").format(
                len(profile_data)
            )
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
            messages.append(self.tr("Geology: {0} segments").format(len(geol_data)))
        else:
            line_lyr = self._resolve_layer(params.line_layer)
            raster_lyr = self._resolve_layer(params.raster_layer)
            outcrop_lyr = self._resolve_layer(params.outcrop_layer)

            if not all([line_lyr, raster_lyr, outcrop_lyr]):
                return None

            geol_data = self.geology_service.generate_geological_profile(
                line_lyr,
                raster_lyr,
                outcrop_lyr,
                params.outcrop_name_field,
                params.band_num,
            )
            if geol_data:
                self.data_cache.set("geol", geol_key, geol_data, cache_meta)
                messages.append(self.tr("Geology: {0} segments").format(len(geol_data)))
            else:
                messages.append(self.tr("Geology: No intersections"))
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
            messages.append(self.tr("Structures: {0} points").format(len(struct_data)))
        else:
            line_lyr = self._resolve_layer(params.line_layer)
            if not line_lyr:
                return None

            line_feat = next(line_lyr.getFeatures(), None)
            if line_feat:
                line_geom = line_feat.geometry()
                if line_geom and not line_geom.isNull():
                    line_start = scu.get_line_start_point(line_geom)
                    line_azimuth = scu.calculate_line_azimuth(line_geom)

                    struct_lyr = self._resolve_layer(params.struct_layer)
                    raster_lyr = self._resolve_layer(params.raster_layer)

                    if not struct_lyr:
                        return None

                    da = QgsDistanceArea()
                    da.setSourceCrs(
                        line_lyr.crs(),
                        QgsProject.instance().transformContext(),
                    )
                    da.setEllipsoid(QgsProject.instance().ellipsoid())

                    # 1. Detach structures
                    detached_structs = self.structure_service.detach_structures(
                        struct_lyr, line_geom, params.buffer_dist
                    )

                    # 2. Project structures
                    struct_data = self.structure_service.project_structures(
                        line_geom=line_geom,
                        line_start=line_start,
                        da=da,
                        raster_lyr=raster_lyr,
                        struct_data=detached_structs,
                        buffer_m=params.buffer_dist,
                        line_az=line_azimuth,
                        dip_field=params.dip_field,
                        strike_field=params.strike_field,
                        band_number=params.band_num,
                    )
                    if struct_data:
                        self.data_cache.set("struct", struct_key, struct_data, cache_meta)
                        messages.append(self.tr("Structures: {0} points").format(len(struct_data)))
                    else:
                        messages.append(
                            self.tr("Structures: None in {0}m buffer").format(params.buffer_dist)
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

        collar_lyr = self._resolve_layer(params.collar_layer)
        if not collar_lyr:
            return None

        drillhole_data = self.drillhole_orchestrator.run_preview(params)

        if drillhole_data:
            self.data_cache.set("drill", drill_key, drillhole_data, cache_meta)

        return drillhole_data
