"""Legend Widget Module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QEvent, QObject, QRectF, Qt
from qgis.PyQt.QtGui import QPainter
from qgis.PyQt.QtWidgets import QWidget


if TYPE_CHECKING:
    from sec_interp.gui.main_dialog import SecInterpDialog

    from .preview_legend_renderer import PreviewLegendRenderer as Renderer


class LegendWidget(QWidget):
    """Widget to display the geological legend over the map canvas."""

    def __init__(self, dialog: SecInterpDialog) -> None:
        super().__init__(dialog)  # Use dialog as the parent
        self.dialog = dialog  # Store reference to the dialog
        self.renderer: Renderer | None = None  # Apply UP037
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Let clicks pass through
        self.setAutoFillBackground(False)  # Don't fill background
        self.hide()

        # Install event filter on parent to track resize
        self.dialog.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle parent resize events."""
        if obj == self.dialog and event.type() == QtCore.QEvent.Resize:
            self.resize(event.size())
        return super().eventFilter(obj, event)

    def update_legend(self, renderer: Renderer) -> None:
        """Update legend with data from renderer."""
        self.renderer = renderer
        self.update()
        self.show()

    def paintEvent(self, event: QEvent) -> None:
        """Handle paint event to draw the legend."""
        if not self.renderer or not self.renderer.active_units:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw legend using the shared method
        self.renderer.draw_legend(painter, QRectF(self.rect()))
