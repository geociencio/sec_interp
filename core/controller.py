"""Controller for SecInterp profile data generation.

This module handles the orchestration of various data generation services
(topography, geology, structures, drillholes) and manages result caching.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

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
from sec_interp.core.utils.safe_loader import SafeLoader
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class ProfileController(TranslatableMixin):
    """Orchestrates data generation services for SecInterp profile creation."""

    def __init__(
        self,
        data_fetcher: Any | None = None,
        structure_extractor: Any | None = None,
        geology_extractor: Any | None = None,
        profile_extractor: Any | None = None,
    ) -> None:
        """Initialize services and the data cache using Dependency Injection.

        Args:
            data_fetcher: Optional feature fetcher (Extract adapter), provided
                by the GUI composition root.
            structure_extractor: Optional structure extractor (Extract adapter),
                provided by the GUI composition root.
            geology_extractor: Optional geology extractor (Extract adapter),
                provided by the GUI composition root.
            profile_extractor: Optional profile extractor (Extract adapter),
                provided by the GUI composition root.

        """
        self.config_service = ConfigService()
        self.data_cache = DataCache()
        self.settings = self.config_service.get_all_settings()
        self.data_fetcher = data_fetcher
        self.structure_extractor = structure_extractor
        self.geology_extractor = geology_extractor
        self.profile_extractor = profile_extractor

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

        # 3. Services (Safely instantiated)
        # Geology Service (QGIS-agnostic; extraction is delegated to the adapter)
        self.geology_service = SafeLoader.lazy_load(
            "sec_interp.core.services.geology_service", "GeologyService"
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

        logger.debug("ProfileController initialized with DI")
        self.reload_settings()

    def reload_settings(self) -> None:
        """Force reload of settings from ConfigService."""
        self.settings = self.config_service.get_all_settings(reload=True)
        logger.debug("ProfileController settings reloaded")

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
            # If it's a layer object, use its ID. Otherwise use the plain value.
            if hasattr(val, "id"):
                val = val.id()
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
            line_lyr = params.line_layer
            raster_lyr = params.raster_layer

            if not line_lyr or not raster_lyr:
                raise ProcessingError(self.tr("Required layers for topography are missing."))

            if not self.profile_extractor:
                raise ProcessingError(self.tr("Topography service failed to load."))

            profile_data = self.profile_extractor.extract_profile(
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
            line_lyr = params.line_layer
            raster_lyr = params.raster_layer
            outcrop_lyr = params.outcrop_layer

            if not all([line_lyr, raster_lyr, outcrop_lyr]):
                return None

            if not self.geology_service or not self.geology_extractor:
                messages.append(self.tr("Geology: Service failed to load"))
                return None

            context = self.geology_extractor.extract_context(
                line_lyr,
                raster_lyr,
                outcrop_lyr,
                params.outcrop_name_field,
                params.band_num,
            )
            geol_data = self.geology_service.build_segments(context)

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
            line_lyr = params.line_layer
            struct_lyr = params.struct_layer
            raster_lyr = params.raster_layer

            if not line_lyr or not struct_lyr:
                return None

            if not self.structure_service or not self.structure_extractor:
                messages.append(self.tr("Structures: Service failed to load"))
                return None

            ctx = self.structure_extractor.extract_section_and_structures(
                line_lyr, struct_lyr, params.buffer_dist
            )
            if ctx is None:
                return None

            def elevation_sampler(x: float, y: float) -> float:
                return self.structure_extractor.sample_elevation(raster_lyr, x, y, params.band_num)

            # 1+2. Detach and project structures
            struct_data = self.structure_service.project_structures(
                line_points=ctx.line_points,
                struct_data=ctx.structures,
                elevation_sampler=elevation_sampler,
                line_az=ctx.line_azimuth,
                dip_field=params.dip_field,
                strike_field=params.strike_field,
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

        collar_lyr = params.collar_layer
        if not collar_lyr:
            return None

        if not self.drillhole_orchestrator:
            messages.append(self.tr("Drillholes: Orchestrator failed to load"))
            return None

        drillhole_data = self.drillhole_orchestrator.run_preview(params)

        if drillhole_data:
            self.data_cache.set("drill", drill_key, drillhole_data, cache_meta)

        return drillhole_data  # type: ignore[no-any-return]
