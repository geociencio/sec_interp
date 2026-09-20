"""Interpretation management module for SecInterp main dialog.

This module handles interpretation polygons, their persistence, and attribute
inheritance, decoupling this logic from the main dialog class. Persistence and
inheritance live in dedicated mixins.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sec_interp.core.domain import InterpretationPolygon
from sec_interp.gui.interpretation_inheritance_mixin import InterpretationInheritanceMixin
from sec_interp.gui.interpretation_persistence_mixin import InterpretationPersistenceMixin
from sec_interp.logger_config import get_logger, log_critical_operation

from .preview_state import PreviewCache

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class InterpretationManager(InterpretationPersistenceMixin, InterpretationInheritanceMixin):
    """Manages interpretation polygons and their business logic."""

    def __init__(self, dialog: SecInterpDialog, cache: PreviewCache | None = None) -> None:
        """Initialize interpretation manager.

        Args:
            dialog: The main dialog instance.
            cache: Shared preview data cache (owned by the dialog).

        """
        self.dialog = dialog
        self.interpretations: list[InterpretationPolygon] = []
        self._preview_cache = cache if cache is not None else PreviewCache()
        self._on_preview_update: Callable[[], None] | None = None

    def set_preview_update_handler(self, handler: Callable[[], None]) -> None:
        """Register the callback invoked after an interpretation is added.

        Args:
            handler: Callable that re-renders the preview.

        """
        self._on_preview_update = handler

    def clear_interpretations(self) -> None:
        """Clear all interpretations and persist the change."""
        self.interpretations = []
        self.save_interpretations()

    def handle_interpretation_finished(self, interpretation: InterpretationPolygon) -> None:
        """Process a finished interpretation polygon.

        Args:
            interpretation: The finished interpretation polygon.

        """
        from .dialogs.interpretation_properties_dialog import (
            InterpretationPropertiesDialog,
        )

        log_critical_operation(
            logger,
            "handle_interpretation_finished",
            polygon_id=interpretation.id,
            vertices=len(interpretation.vertices_2d),
        )

        interp_config = self.dialog.page_interpretation.get_data()

        if interp_config.get("inherit_geology") or interp_config.get("inherit_drillholes"):
            self.apply_attribute_inheritance(interpretation, interp_config)

        dlg = InterpretationPropertiesDialog(
            interpretation, interp_config.get("custom_fields"), self.dialog
        )

        if dlg.exec() != 1:
            logger.info(f"Interpretation canceled by user: {interpretation.id}")
            self.dialog.preview_widget.btn_interpret.setChecked(False)
            return

        self.interpretations.append(interpretation)
        self.save_interpretations()
        logger.info(
            f"Interpretation polygon added: {interpretation.id} "
            f"({len(interpretation.vertices_2d)} vertices)"
        )

        msg = (
            f"<b>{self.dialog.tr('Interpretation Finished')}</b><br>"
            f"<b>{self.dialog.tr('Name')}:</b> {interpretation.name}<br>"
            f"<b>{self.dialog.tr('Vertices')}:</b> {len(interpretation.vertices_2d)}<br>"
            f"<b>{self.dialog.tr('ID')}:</b> {interpretation.id[:8]}..."
        )
        self.dialog.preview_widget.results_text.setHtml(msg)
        self.dialog.preview_widget.results_group.setCollapsed(False)

        self.dialog.preview_widget.btn_interpret.setChecked(False)

        if self._on_preview_update:
            self._on_preview_update()
