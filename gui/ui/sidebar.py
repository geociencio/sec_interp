"""Sidebar navigation widget."""
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem
from qgis.PyQt.QtCore import QSize, Qt
from qgis.core import QgsApplication


class Sidebar(QListWidget):
    """Sidebar navigation widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(32, 32))
        self.setFixedWidth(140)  # Slightly wider for better text fit
        
        # Style to look like QGIS options dialog sidebar
        self.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border-right: 1px solid #d0d0d0;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                color: #404040;
            }
            QListWidget::item:selected {
                background-color: #ffffff;
                color: #000000;
                border-left: 3px solid #0078d7;
            }
            QListWidget::item:hover {
                background-color: #e8e8e8;
            }
        """)

    def add_item(self, text, icon_name=None):
        """Add an item to the sidebar.
        
        Args:
            text (str): Item label.
            icon_name (str): QGIS theme icon name (e.g. 'mIconRaster.svg').
        """
        item = QListWidgetItem(text)
        if icon_name:
            icon = QgsApplication.getThemeIcon(icon_name)
            item.setIcon(icon)
        
        # Center text alignment
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.addItem(item)
