"""Main Window assembly."""
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, 
    QStackedWidget, QDialogButtonBox, QLabel
)
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsFileWidget

from .sidebar import Sidebar
from .pages.dem_page import DemPage
from .pages.section_page import SectionPage
from .pages.geology_page import GeologyPage
from .pages.structure_page import StructurePage
from .pages.preview_page import PreviewWidget
from .pages.drillhole_page import DrillholePage


class SecInterpMainWindow(QDialog):
    """Main Programmatic Interface for SecInterp."""

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sec Interp")
        self.resize(1200, 700)
        
        # Initialize UI components
        self.sidebar = Sidebar()
        self.stacked_widget = QStackedWidget()
        self.preview_widget = PreviewWidget()
        self.output_widget = QgsFileWidget()
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | 
            QDialogButtonBox.Save | QDialogButtonBox.Help
        )
        
        # Initialize Pages
        self.page_dem = DemPage(iface)
        self.page_section = SectionPage()
        self.page_geology = GeologyPage()
        self.page_geology = GeologyPage()
        self.page_struct = StructurePage()
        self.page_drillhole = DrillholePage()
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Assemble the UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # -- Main Content Area: Splitter [Sidebar | Settings | Preview] --
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)  # Nominal width
        splitter.setChildrenCollapsible(True)
        
        # Style the splitter handle to be visible and indicate interaction
        splitter.setStyleSheet("""
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
        """)

        # 1. Left: Sidebar
        splitter.addWidget(self.sidebar)

        # 2. Middle: Settings (Stacked Pages)
        self.stacked_widget.addWidget(self.page_dem)
        self.stacked_widget.addWidget(self.page_section)
        self.stacked_widget.addWidget(self.page_geology)
        self.stacked_widget.addWidget(self.page_struct)
        self.stacked_widget.addWidget(self.page_drillhole)
        
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
        out_layout.addWidget(QLabel("Output Folder"))
        
        self.output_widget.setStorageMode(QgsFileWidget.GetDirectory)
        out_layout.addWidget(self.output_widget)
        
        main_layout.addLayout(out_layout)
        main_layout.addWidget(self.button_box)

        # Populate sidebar
        self.sidebar.add_item("DEM / Raster", "mIconRaster.svg")
        self.sidebar.add_item("Section Line", "mIconLineLayer.svg")
        self.sidebar.add_item("Geology", "mIconPolygonLayer.svg")
        self.sidebar.add_item("Structural", "mIconPointLayer.svg")
        self.sidebar.add_item("Drillholes", "mActionDataSourceManager.svg")
        
        self.sidebar.setCurrentRow(0)

    def _connect_signals(self):
        """Connect navigation signals."""
        self.sidebar.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
