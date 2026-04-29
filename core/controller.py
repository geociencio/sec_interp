"""Controller for SecInterp profile data generation.

This module handles the orchestration of various data generation services
(topography, geology, structures, drillholes) and manages result caching.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from typing import Any

from qgis.core import QgsDistanceArea, QgsProject

from sec_interp.core import utils as scu
from sec_interp.core.config import ConfigService
from sec_interp.core.data_cache import DataCache
from sec_interp.core.domain import (
    DrillholeProjection,
    GeologySegment,
    PreviewParams,
    StructureMeasurement,
)
from sec_interp.core.exceptions import ProcessingError
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.core.utils.qgis import LayerResolver
from sec_interp.core.utils.safe_loader import SafeLoader
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileController(TranslatableMixin):
    """Orchestrates data generation services for SecInterp profile creation."""

    def __init__(self) -> None:
        """Initialize services and the data cache using Dependency Injection."""
        self.config_service = ConfigService()
        self.data_cache = DataCache()
        self.settings = self.config_service.get_all_settings()

        # 1. Component Factories (Loaded safely)
        # Processors
        self.collar_processor = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.collar_processor", "CollarProcessor"
        )
        self.survey_processor = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.survey_processor", "SurveyProcessor"
        )
        self.interval_processor = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.interval_processor", "IntervalProcessor"
        )
        self.trajectory_engine = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.trajectory_engine", "TrajectoryEngine"
        )
        self.profile_sampler = SafeLoader.lazy_load(
            "sec_interp.core.services.geology.profile_sampler", "ProfileSampler"
        )
        self.outcrop_processor = SafeLoader.lazy_load(
            "sec_interp.core.services.geology.outcrop_processor", "OutcropProcessor"
        )
        self.data_fetcher = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.data_fetcher", "DataFetcher"
        )

        # 3. Services (Safely instantiated)
        self.profile_service = SafeLoader.lazy_load(
            "sec_interp.core.services.profile_service", "ProfileService"
        )

        # Geology Service (Using the new lazy_load with DI)
        self.geology_service = SafeLoader.lazy_load(
            "sec_interp.core.services.geology_service",
            "GeologyService",
            profile_sampler=self.profile_sampler,
            outcrop_processor=self.outcrop_processor,
        )

        self.structure_service = SafeLoader.lazy_load(
            "sec_interp.core.services.structure_service", "StructureService"
        )

        # Drillhole Service (Using the new lazy_load with DI)
        self.drillhole_service = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole_service",
            "DrillholeService",
            collar_processor=self.collar_processor,
            survey_processor=self.survey_processor,
            interval_processor=self.interval_processor,
            data_fetcher=self.data_fetcher,
            trajectory_engine=self.trajectory_engine,
        )

        # Orchestrator
        self.drillhole_orchestrator = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole.drillhole_orchestrator",
            "DrillholeTaskOrchestrator",
            service=self.drillhole_service,
        )

        self._connected_layers: list[Any] = []
        logger.debug("ProfileController initialized with DI")
        self.reload_settings()

    def reload_settings(self) -> None:
        """Force reload of settings from ConfigService."""
        self.settings = self.config_service.get_all_settings(reload=True)
        logger.debug("ProfileController settings reloaded")

    def connect_layer_notifications(self, layers: dict[str, Any]) -> None:
        """Connect to layer signals for automatic cache invalidation on data changes.

        Args:
            layers: Dictionary mapping bucket names to QgsMapLayer objects.

        """
        self.disconnect_layer_notifications()
        for bucket, layer in layers.items():
            if not layer:
                continue

            # Map specific internal layer buckets to cache buckets
            cache_bucket = bucket
            if bucket in ["drill_collar", "drill_survey", "drill_interval"]:
                cache_bucket = "drill"

            # Special case for 'section': invalidates ALL buckets as it's the base geometry
            if bucket == "section":

                def callback() -> None:
                    """Invalidate all cache buckets."""
                    return self.data_cache.invalidate()

            else:
                # Use a closure to capture the bucket name
                callback = self._create_invalidation_callback(cache_bucket)

            layer.dataChanged.connect(callback)
            self._connected_layers.append((layer, callback))
            logger.debug(
                f"Connected cache invalidation to layer: {layer.name()} -> bucket: {cache_bucket}"
            )

    def _create_invalidation_callback(self, bucket: str) -> Callable[[], None]:
        """Create a callback for specific bucket invalidation."""

        def callback() -> None:
            """Invalidate specific cache bucket."""
            return self.data_cache.invalidate(bucket)

        return callback

    def disconnect_layer_notifications(self) -> None:
        """Disconnect from all previously connected layer signals."""
        for layer, callback in self._connected_layers:
            try:
                layer.dataChanged.disconnect(callback)
            except (TypeError, RuntimeError, Exception) as e:
                logger.debug(f"Layer disconnection failed (expected on close): {e}")
        self._connected_layers.clear()
        logger.debug("Layer signals disconnected")

    def get_cached_data(self, inputs: dict[str, Any]) -> dict[str, Any] | None:
        """Retrieve data from cache if available for the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.

        Returns:
            Cached data dictionary if found, else None.

        """
        cache_key = self.data_cache.get_cache_key(inputs)
        return self.data_cache.get("main", cache_key)

    def cache_data(self, inputs: dict[str, Any], data: dict[str, Any]) -> None:
        """Cache the generated data resulting from the given inputs.

        Args:
            inputs: Dictionary of input parameters to generate cache key.
            data: Data dictionary to cache.

        """
        cache_key = self.data_cache.get_cache_key(inputs)
        self.data_cache.set("main", cache_key, data)

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
        messages: list[str] = []
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
        """Generate a sub-key for caching specific components.

        Args:
            param_values: List of values to include in the cache key.

        Returns:
            MD5 hash string of the parameter values.

        """
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

    def _process_topography(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[tuple[float, float]]:
        """Process topographic profile data.

        Args:
            params: Preview parameters containing layer IDs and settings.
            cache_meta: Metadata to store with the cached result.
            messages: List to append processing status messages.

        Returns:
            List of (distance, elevation) tuples.

        Raises:
            ProcessingError: If required layers are missing or service fails.

        """
        topo_key = self._get_cache_sub_key([params.band_num, params.max_points])
        profile_data = self.data_cache.get("topo", topo_key)
        if profile_data:
            logger.debug("Cache hit: Topography")
        else:
            line_lyr = LayerResolver.resolve(params.line_layer)
            raster_lyr = LayerResolver.resolve(params.raster_layer)

            if not line_lyr or not raster_lyr:
                raise ProcessingError(self.tr("Required layers for topography are missing."))

            if not self.profile_service:
                raise ProcessingError(self.tr("Topography service failed to load."))

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
        return profile_data  # type: ignore[no-any-return]

    def _process_geology(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[GeologySegment] | None:
        """Process geological profile data.

        Args:
            params: Preview parameters containing layer IDs and settings.
            cache_meta: Metadata to store with the cached result.
            messages: List to append processing status messages.

        Returns:
            List of geological segments if successful, None otherwise.

        """
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
            line_lyr = LayerResolver.resolve(params.line_layer)
            raster_lyr = LayerResolver.resolve(params.raster_layer)
            outcrop_lyr = LayerResolver.resolve(params.outcrop_layer)

            if not all([line_lyr, raster_lyr, outcrop_lyr]):
                return None

            if not self.geology_service:
                messages.append(self.tr("Geology: Service failed to load"))
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
        return geol_data  # type: ignore[no-any-return]

    def _process_structures(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[StructureMeasurement] | None:
        """Process structural profile data.

        Args:
            params: Preview parameters containing layer IDs and settings.
            cache_meta: Metadata to store with the cached result.
            messages: List to append processing status messages.

        Returns:
            List of projected structural measurements if successful, None otherwise.

        """
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
            line_lyr = LayerResolver.resolve(params.line_layer)
            if not line_lyr:
                return None

            line_feat = next(line_lyr.getFeatures(), None)
            if line_feat:
                line_geom = line_feat.geometry()
                if line_geom and not line_geom.isNull():
                    line_start = scu.get_line_start_point(line_geom)
                    line_azimuth = scu.calculate_line_azimuth(line_geom)

                    struct_lyr = LayerResolver.resolve(params.struct_layer)
                    raster_lyr = LayerResolver.resolve(params.raster_layer)

                    if not struct_lyr:
                        return None

                    if not self.structure_service:
                        messages.append(self.tr("Structures: Service failed to load"))
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
        return struct_data  # type: ignore[no-any-return]

    def _process_drillholes(
        self, params: PreviewParams, cache_meta: dict, messages: list[str]
    ) -> list[DrillholeProjection] | None:
        """Process drillhole profile data.

        Args:
            params: Preview parameters containing layer IDs and settings.
            cache_meta: Metadata to store with the cached result.
            messages: List to append processing status messages.

        Returns:
            List of projected drillholes if successful, None otherwise.

        """
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
            return drillhole_data  # type: ignore[no-any-return]

        collar_lyr = LayerResolver.resolve(params.collar_layer)
        if not collar_lyr:
            return None

        if not self.drillhole_orchestrator:
            messages.append(self.tr("Drillholes: Orchestrator failed to load"))
            return None

        drillhole_data = self.drillhole_orchestrator.run_preview(params)

        if drillhole_data:
            self.data_cache.set("drill", drill_key, drillhole_data, cache_meta)

        return drillhole_data  # type: ignore[no-any-return]
