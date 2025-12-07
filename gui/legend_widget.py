# -*- coding: utf-8 -*-
"""
Legend Widget Module
"""
from typing import Optional
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import Qt, QRectF, QObject, QEvent
from qgis.PyQt.QtGui import QPainter
from qgis.PyQt.QtWidgets import QWidget


class LegendWidget(QWidget):
    """Widget to display the geological legend over the map canvas."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:

        super().__init__(parent)
        self.renderer = None
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Let clicks pass through
        self.setAutoFillBackground(False)  # Don't fill background
        self.hide()

        # Install event filter on parent to track resize
        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle parent resize events."""
        if obj == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.resize(event.size())
        return super().eventFilter(obj, event)

    def update_legend(self, renderer: "Renderer") -> None:
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
