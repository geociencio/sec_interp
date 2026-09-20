"""Main Plugin Module.

Orchestrates the lifecycle of the SecInterp QGIS plugin. Lifecycle actions,
input validation and the render pipeline live in :mod:`sec_interp.plugin`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QSettings,
    QTranslator,
)

from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.core.utils.safe_loader import SafeLoader
from sec_interp.logger_config import get_logger, setup_logging
from sec_interp.plugin import (
    InputValidationMixin,
    PluginLifecycleMixin,
    RenderPipelineMixin,
)

logger = get_logger(__name__)


class SecInterp(TranslatableMixin, PluginLifecycleMixin, InputValidationMixin, RenderPipelineMixin):
    """QGIS Plugin Implementation for Geological Data Extraction.

    This class implements the main logic of the SecInterp plugin, handling
    initialization, UI integration, and orchestration of data processing tasks.
    It connects the QGIS interface with the plugin's dialog and processing algorithms.
    """

    def __init__(self, iface: Any) -> None:
        """Initialize the plugin.

        Args:
            iface (QgsInterface): An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.

        """
        setup_logging()

        self.iface = iface
        self.plugin_dir = Path(__file__).resolve().parent
        self._load_translator()

        # Prepare core services BEFORE the dialog (required by PreviewManager)
        self.preview_renderer = SafeLoader.lazy_load(
            "sec_interp.gui.preview_renderer", "PreviewRenderer"
        )
        data_fetcher = SafeLoader.lazy_load(
            "sec_interp.gui.adapters.feature_fetcher", "DataFetcher"
        )
        structure_extractor = SafeLoader.lazy_load(
            "sec_interp.gui.adapters.structure_extractor", "StructureExtractor"
        )
        geology_extractor = SafeLoader.lazy_load(
            "sec_interp.gui.adapters.geology_extractor", "GeologyExtractor"
        )
        profile_extractor = SafeLoader.lazy_load(
            "sec_interp.gui.adapters.profile_extractor", "ProfileExtractor"
        )
        drillhole_extractor = SafeLoader.lazy_load(
            "sec_interp.gui.adapters.drillhole_extractor",
            "DrillholeExtractor",
            data_fetcher=data_fetcher,
        )
        self.controller = SafeLoader.lazy_load(
            "sec_interp.core.controller",
            "ProfileController",
            data_fetcher=data_fetcher,
            structure_extractor=structure_extractor,
            geology_extractor=geology_extractor,
            profile_extractor=profile_extractor,
            drillhole_extractor=drillhole_extractor,
        )

        self.layer_notification_manager = SafeLoader.lazy_load(
            "sec_interp.gui.layer_notification_manager",
            "LayerNotificationManager",
            data_cache=self.controller.data_cache,
        )

        export_mod = SafeLoader.safe_import("sec_interp.core.services.export_service")
        export_klass = SafeLoader.get_class(export_mod, "ExportService")
        self.export_service = export_klass(self.controller) if export_klass else None

        dialog_mod = SafeLoader.safe_import("sec_interp.gui.main_dialog")
        dialog_klass = SafeLoader.get_class(dialog_mod, "SecInterpDialog")
        self.dlg = dialog_klass(self.iface, self) if dialog_klass else None

        if self.dlg:
            self.dlg.plugin_instance = self
        else:
            logger.error("Failed to initialize main dialog. Plugin functionality will be limited.")

        self.first_start = True

        self.actions = []
        self.menu = self.tr("&Sec Interp")
        self.toolbar = self.iface.addToolBar(self.tr("Sec Interp"))
        self.toolbar.setObjectName("SecInterp")
        self.toolbar.setVisible(True)

    def _load_translator(self) -> None:
        """Install the best matching translation file for the user locale."""
        user_locale = QSettings().value("locale/userLocale", "en")
        locale_path = self.plugin_dir / f"i18n/SecInterp_{user_locale}.qm"

        MIN_LOCALE_LENGTH = 2
        if not locale_path.exists() and user_locale and len(user_locale) > MIN_LOCALE_LENGTH:
            locale_short = user_locale[0:2]
            locale_path = self.plugin_dir / f"i18n/SecInterp_{locale_short}.qm"

        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path))
            QCoreApplication.installTranslator(self.translator)

    def save_profile_line(self) -> None:
        """Save profile data by delegating to the dialog's export manager."""
        if hasattr(self, "dlg") and self.dlg:
            self.dlg.export_manager.export_data()
