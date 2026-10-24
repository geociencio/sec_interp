"""Controller for SecInterp profile data generation.

This module handles the orchestration of various data generation services
(topography, geology, structures, drillholes) and manages result caching.
"""

from __future__ import annotations

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
from sec_interp.core.services.profile.drillholes import process_drillholes
from sec_interp.core.services.profile.errors import (
    ProfileDataError,
    ProfileInputError,
    ProfileServiceError,
)
from sec_interp.core.services.profile.geology import process_geology
from sec_interp.core.services.profile.pipeline import build_profile_data
from sec_interp.core.services.profile.structures import process_structures
from sec_interp.core.services.profile.topography import process_topography
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
        drillhole_extractor: Any | None = None,
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
            drillhole_extractor: Optional drillhole extractor (Extract adapter),
                provided by the GUI composition root.

        """
        self.config_service = ConfigService()
        self.data_cache = DataCache()
        self.settings = self.config_service.get_all_settings()
        self.data_fetcher = data_fetcher
        self.structure_extractor = structure_extractor
        self.geology_extractor = geology_extractor
        self.profile_extractor = profile_extractor
        self.drillhole_extractor = drillhole_extractor

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

        # Drillhole Service (QGIS-agnostic; extraction is delegated to the adapter)
        self.drillhole_service = SafeLoader.lazy_load(
            "sec_interp.core.services.drillhole_service",
            "DrillholeService",
            collar_processor=self.collar_processor,
            survey_processor=self.survey_processor,
            interval_processor=self.interval_processor,
            data_fetcher=self.data_fetcher,
            trajectory_engine=self.trajectory_engine,
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
        return build_profile_data(
            params,
            self._process_topography,
            self._process_geology,
            self._process_structures,
            self._process_drillholes,
        )

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
        try:
            profile_data = process_topography(
                params,
                self.profile_extractor,
                self.data_cache,
                cache_meta,
            )
        except ProfileInputError:
            raise ProcessingError(self.tr("Required layers for topography are missing.")) from None
        except ProfileServiceError:
            raise ProcessingError(self.tr("Topography service failed to load.")) from None
        except ProfileDataError:
            raise ProcessingError(self.tr("No topographic profile data was generated.")) from None

        messages.append(
            self.tr("✓ Data processed successfully!\n\nTopography: {0} points").format(
                len(profile_data)
            )
        )
        return profile_data

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

        try:
            geol_data = process_geology(
                params,
                self.geology_extractor,
                self.geology_service,
                self.data_cache,
                cache_meta,
            )
        except ProfileInputError:
            return None
        except ProfileServiceError:
            messages.append(self.tr("Geology: Service failed to load"))
            return None

        if geol_data:
            messages.append(self.tr("Geology: {0} segments").format(len(geol_data)))
        else:
            messages.append(self.tr("Geology: No intersections"))
        return geol_data

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

        try:
            struct_data = process_structures(
                params,
                self.structure_extractor,
                self.structure_service,
                self.data_cache,
                cache_meta,
            )
        except ProfileServiceError:
            messages.append(self.tr("Structures: Service failed to load"))
            return None

        if struct_data:
            messages.append(self.tr("Structures: {0} points").format(len(struct_data)))
        elif struct_data is not None:
            messages.append(self.tr("Structures: None in {0}m buffer").format(params.buffer_dist))
        return struct_data

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

        try:
            return process_drillholes(
                params,
                self.drillhole_extractor,
                self.drillhole_service,
                self.data_cache,
                cache_meta,
            )
        except ProfileServiceError:
            messages.append(self.tr("Drillholes: Service failed to load"))
            return None
