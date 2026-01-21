from __future__ import annotations

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class CacheHandler:
    """Handles cache operations for the dialog."""

    def __init__(self, dialog: sec_interp.gui.main_dialog.SecInterpDialog):
        """Initialize cache handler.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance

        """
        self.dialog = dialog

    def clear_cache(self) -> None:
        """Clear cached data and notify user."""
        if hasattr(self.dialog, "plugin_instance") and self.dialog.plugin_instance:
            self.dialog.plugin_instance.controller.data_cache.clear()
            self.dialog.preview_widget.results_text.append(
                self.dialog.tr("✓ Cache cleared - next preview will re-process data")
            )
            logger.info("Cache cleared by user")
        else:
            self.dialog.preview_widget.results_text.append(self.dialog.tr("⚠ Cache not available"))
