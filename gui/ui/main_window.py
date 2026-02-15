"""Main Window assembly."""

from __future__ import annotations

import contextlib

from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
)

from .pages.dem_page import DemPage
from .pages.drillhole_page import DrillholePage
from .pages.geology_page import GeologyPage
from .pages.interpretation_page import InterpretationPage
from .pages.preview_page import PreviewWidget
from .pages.section_page import SectionPage
from .pages.settings_page import SettingsPage
from .pages.structure_page import StructurePage
from .sidebar import Sidebar


class SecInterpMainWindow(QDialog):
    """Main Programmatic Interface for SecInterp."""

    def __init__(self, iface: Any | None = None, parent: QWidget | None = None) -> None:
        """Initialize the main dialog.

        Args:
            iface: QGIS interface.
            parent: Parent widget.

        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Sec Interp"))
        self.resize(1200, 700)

        # Initialize UI components
        self.sidebar = Sidebar()
        self.stacked_widget = QStackedWidget()
        self.preview_widget = PreviewWidget()
        self.output_widget = QgsFileWidget()
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel
            | QDialogButtonBox.Save
            | QDialogButtonBox.Help
        )

        # Initialize Pages
        self.page_dem = DemPage(iface)
        self.page_section = SectionPage()
        self.page_geology = GeologyPage()
        self.page_struct = StructurePage()
        self.page_drillhole = DrillholePage()
        self.page_interpretation = InterpretationPage()
        self.page_settings = SettingsPage()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Assemble the UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # -- Main Content Area: Splitter [Sidebar | Settings | Preview] --
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)  # Nominal width
        splitter.setChildrenCollapsible(True)

        # Style the splitter handle to be visible and indicate interaction
        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                margin: 1px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #d0d0d0;
                border-color: #a0a0a0;
            }
            QSplitter::handle:pressed {
                background-color: #b0b0b0;
                border-color: #808080;
            }
        """
        )

        # 1. Left: Sidebar
        splitter.addWidget(self.sidebar)

        # 2. Middle: Settings (Stacked Pages)
        self.stacked_widget.addWidget(self.page_dem)
        self.stacked_widget.addWidget(self.page_section)
        self.stacked_widget.addWidget(self.page_geology)
        self.stacked_widget.addWidget(self.page_struct)
        self.stacked_widget.addWidget(self.page_drillhole)
        self.stacked_widget.addWidget(self.page_interpretation)
        self.stacked_widget.addWidget(self.page_settings)

        splitter.addWidget(self.stacked_widget)

        # 3. Right: Preview Widget
        splitter.addWidget(self.preview_widget)

        # Set Splitter Stretches (Sidebar minimal, Settings medium, Preview expanding)
        # Sidebar (0): 0 stretch, fixed size interactions handled by widget ref
        # Settings (1): 1 stretch, can shrink
        # Preview (2): 4 stretch, takes most space
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 0)  # Settings doesn't need to hog space
        splitter.setStretchFactor(2, 1)  # Preview gets the rest

        # Make settings panel collapsible
        splitter.setCollapsible(1, True)

        main_layout.addWidget(splitter, stretch=10)

        # -- Bottom Area: Output & Buttons --
        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel(self.tr("Output Folder")))

        self.output_widget.setStorageMode(QgsFileWidget.GetDirectory)
        out_layout.addWidget(self.output_widget)

        main_layout.addLayout(out_layout)
        main_layout.addWidget(self.button_box)

        # Populate sidebar
        self.sidebar.add_item(self.tr("DEM / Raster"), "mIconRaster.svg")
        self.sidebar.add_item(self.tr("Section Line"), "mIconLineLayer.svg")
        self.sidebar.add_item(self.tr("Geology"), "mIconPolygonLayer.svg")
        self.sidebar.add_item(self.tr("Structural"), "mIconPointLayer.svg")
        self.sidebar.add_item(self.tr("Drillholes"), "mActionDataSourceManager.svg")
        self.sidebar.add_item(self.tr("Interpretation"), "mActionEdit.svg")
        self.sidebar.add_item(self.tr("Settings"), "mActionOptions.svg")

        self.sidebar.setCurrentRow(0)

    def _connect_signals(self) -> None:
        """Connect navigation signals."""
        self.sidebar.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.sidebar.currentRowChanged.disconnect(self.stacked_widget.setCurrentIndex)
        with contextlib.suppress(TypeError, RuntimeError):
            self.output_widget.fileChanged.disconnect(self.update_button_state)
