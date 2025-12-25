from qgis.core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sec_interp.logger_config import get_logger

from .base_page import BasePage


logger = get_logger(__name__)


class DrillholePage(BasePage):
    """Configuration page for Drillhole data (Collar, Survey, Intervals)."""

    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(QCoreApplication.translate("DrillholePage", "Drillhole Data"), parent)

    def _setup_ui(self):
        # Override BasePage layout slightly to allow for Tabs or multiple Groups
        # BasePage expects self.group_box in a main_layout.
        # We will hide the default group box and use our own layout in the main widget area if
        # possible,
        # OR we use the default group box as a container for a TabWidget.

        # Let's use the BasePage structure but put a TabWidget inside the main group box
        super()._setup_ui()

        # Clear any default layout in group_box if BasePage added any (it creates an empty
        # QVBoxLayout usually)
        if self.group_box.layout():
            QWidget().setLayout(
                self.group_box.layout()
            )  # Hack to delete layout? No, just use it.
            layout = self.group_box.layout()
        else:
            layout = QVBoxLayout(self.group_box)
            self.group_box.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # -- Tab 1: Collars --
        self.collar_tab = QWidget()
        self._setup_collar_tab(self.collar_tab)
        self.tab_widget.addTab(self.collar_tab, self.tr("Collars"))

        # -- Tab 2: Survey --
        self.survey_tab = QWidget()
        self._setup_survey_tab(self.survey_tab)
        self.tab_widget.addTab(self.survey_tab, self.tr("Survey"))

        # -- Tab 3: Intervals --
        self.interval_tab = QWidget()
        self._setup_interval_tab(self.interval_tab)
        self.tab_widget.addTab(self.interval_tab, self.tr("Intervals"))

        # Add spacer to bottom of page
        layout.addStretch()

    def _setup_collar_tab(self, parent_widget):
        layout = QGridLayout(parent_widget)
        layout.setSpacing(6)

        self._add_collar_layer_widgets(layout)
        self._add_collar_coordinate_widgets(layout)
        self._add_collar_depth_widgets(layout)
        self._connect_collar_signals()

    def _add_collar_layer_widgets(self, layout):
        """Add layer and ID selection widgets to collar tab."""
        # Layer
        layout.addWidget(QLabel(self.tr("Collar Layer:")), 0, 0)
        self.c_layer = QgsMapLayerComboBox()
        self.c_layer.setFilters(Qgis.LayerFilter.PointLayer)
        self.c_layer.setAllowEmptyLayer(True)
        self.c_layer.setCurrentIndex(0)
        layout.addWidget(self.c_layer, 0, 1)

        # ID Field
        layout.addWidget(QLabel(self.tr("Hole ID:")), 2, 0)
        self.c_id = QgsFieldComboBox()
        layout.addWidget(self.c_id, 2, 1)

    def _add_collar_coordinate_widgets(self, layout):
        """Add coordinate selection widgets to collar tab."""
        # Use Geometry Checkbox
        self.chk_use_geom = QCheckBox(self.tr("Use Layer Geometry for Coordinates"))
        self.chk_use_geom.setChecked(True)
        layout.addWidget(self.chk_use_geom, 1, 0, 1, 2)

        # X / Y Fields (Hidden if geometry used)
        self.lbl_x = QLabel(self.tr("East (X):"))
        layout.addWidget(self.lbl_x, 3, 0)
        self.c_x = QgsFieldComboBox()
        self.c_x.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_x, 3, 1)

        self.lbl_y = QLabel(self.tr("North (Y):"))
        layout.addWidget(self.lbl_y, 4, 0)
        self.c_y = QgsFieldComboBox()
        self.c_y.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_y, 4, 1)

        # Z Field (Optional)
        layout.addWidget(QLabel(self.tr("Elevation (Z):")), 5, 0)
        self.c_z = QgsFieldComboBox()
        self.c_z.setAllowEmptyFieldName(True)
        self.c_z.setToolTip(self.tr("Leave empty to use DEM elevation"))
        layout.addWidget(self.c_z, 5, 1)

    def _add_collar_depth_widgets(self, layout):
        """Add depth widget to collar tab."""
        # Depth Field (Optional but recommended)
        layout.addWidget(QLabel(self.tr("Total Depth:")), 6, 0)
        self.c_depth = QgsFieldComboBox()
        self.c_depth.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_depth, 6, 1)

        layout.setRowStretch(7, 1)

    def _connect_collar_signals(self):
        """Connect collar tab signals."""
        self.c_layer.layerChanged.connect(self.c_id.setLayer)
        self.c_layer.layerChanged.connect(self.c_x.setLayer)
        self.c_layer.layerChanged.connect(self.c_y.setLayer)
        self.c_layer.layerChanged.connect(self.c_z.setLayer)
        self.c_layer.layerChanged.connect(self.c_depth.setLayer)
        self.c_layer.layerChanged.connect(self.dataChanged.emit)

        self.chk_use_geom.toggled.connect(self._toggle_xy_fields)
        self._toggle_xy_fields(True)

        for widget in [
            self.c_id,
            self.c_x,
            self.c_y,
            self.c_z,
            self.c_depth,
            self.chk_use_geom,
        ]:
            if hasattr(widget, "fieldChanged"):
                widget.fieldChanged.connect(self.dataChanged.emit)
            elif hasattr(widget, "toggled"):
                widget.toggled.connect(self.dataChanged.emit)

    def _setup_survey_tab(self, parent_widget):
        layout = QGridLayout(parent_widget)
        row = 0

        layout.addWidget(QLabel(self.tr("Survey Layer:")), row, 0)
        self.s_layer = QgsMapLayerComboBox()

        # Use modern flags if available (QGIS 3.32+)
        try:
            self.s_layer.setFilters(
                Qgis.LayerFilters(
                    Qgis.LayerFilter.PointLayer | Qgis.LayerFilter.NoGeometry
                )
            )
        except (AttributeError, TypeError):
            self.s_layer.setFilters(
                QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.NoGeometry
            )

        self.s_layer.setAllowEmptyLayer(True)
        self.s_layer.setCurrentIndex(0)
        layout.addWidget(self.s_layer, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Hole ID:")), row, 0)
        self.s_id = QgsFieldComboBox()
        layout.addWidget(self.s_id, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Depth:")), row, 0)
        self.s_depth = QgsFieldComboBox()
        layout.addWidget(self.s_depth, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Azimuth:")), row, 0)
        self.s_azim = QgsFieldComboBox()
        layout.addWidget(self.s_azim, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Inclination:")), row, 0)
        self.s_incl = QgsFieldComboBox()
        layout.addWidget(self.s_incl, row, 1)
        row += 1

        layout.setRowStretch(row, 1)

        self.s_layer.layerChanged.connect(self.s_id.setLayer)
        self.s_layer.layerChanged.connect(self.s_depth.setLayer)
        self.s_layer.layerChanged.connect(self.s_azim.setLayer)
        self.s_layer.layerChanged.connect(self.s_incl.setLayer)
        self.s_layer.layerChanged.connect(self.dataChanged.emit)

        for w in [self.s_id, self.s_depth, self.s_azim, self.s_incl]:
            w.fieldChanged.connect(self.dataChanged.emit)

    def _setup_interval_tab(self, parent_widget):
        layout = QGridLayout(parent_widget)
        row = 0

        layout.addWidget(QLabel(self.tr("Interval Layer:")), row, 0)
        self.i_layer = QgsMapLayerComboBox()
        # Intervals can be tables or vector layers
        # Use modern flags if available (QGIS 3.32+)
        try:
            self.i_layer.setFilters(
                Qgis.LayerFilters(
                    Qgis.LayerFilter.PointLayer | Qgis.LayerFilter.NoGeometry
                )
            )
        except (AttributeError, TypeError):
            self.i_layer.setFilters(
                QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.NoGeometry
            )

        self.i_layer.setAllowEmptyLayer(True)
        self.i_layer.setCurrentIndex(0)
        layout.addWidget(self.i_layer, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Hole ID:")), row, 0)
        self.i_id = QgsFieldComboBox()
        layout.addWidget(self.i_id, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("From Depth:")), row, 0)
        self.i_from = QgsFieldComboBox()
        layout.addWidget(self.i_from, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("To Depth:")), row, 0)
        self.i_to = QgsFieldComboBox()
        layout.addWidget(self.i_to, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Lithology/Attribute:")), row, 0)
        self.i_lith = QgsFieldComboBox()
        layout.addWidget(self.i_lith, row, 1)
        row += 1

        layout.setRowStretch(row, 1)

        self.i_layer.layerChanged.connect(self.i_id.setLayer)
        self.i_layer.layerChanged.connect(self.i_from.setLayer)
        self.i_layer.layerChanged.connect(self.i_to.setLayer)
        self.i_layer.layerChanged.connect(self.i_lith.setLayer)
        self.i_layer.layerChanged.connect(self.dataChanged.emit)

        for w in [self.i_id, self.i_from, self.i_to, self.i_lith]:
            w.fieldChanged.connect(self.dataChanged.emit)

    def _toggle_xy_fields(self, checked):
        enabled = not checked
        self.lbl_x.setEnabled(enabled)
        self.c_x.setEnabled(enabled)
        self.lbl_y.setEnabled(enabled)
        self.c_y.setEnabled(enabled)

    def get_data(self) -> dict:
        """Get drillhole configuration."""
        return {
            # Collars
            "collar_layer": self.c_layer.currentLayer(),
            "use_geometry": self.chk_use_geom.isChecked(),
            "collar_id": self.c_id.currentField(),
            "collar_x": self.c_x.currentField(),
            "collar_y": self.c_y.currentField(),
            "collar_z": self.c_z.currentField(),
            "collar_depth": self.c_depth.currentField(),
            # Survey
            "survey_layer": self.s_layer.currentLayer(),
            "survey_id": self.s_id.currentField(),
            "survey_depth": self.s_depth.currentField(),
            "survey_azim": self.s_azim.currentField(),
            "survey_incl": self.s_incl.currentField(),
            # Interval
            "interval_layer": self.i_layer.currentLayer(),
            "interval_id": self.i_id.currentField(),
            "interval_from": self.i_from.currentField(),
            "interval_to": self.i_to.currentField(),
            "interval_lith": self.i_lith.currentField(),
        }

    def is_complete(self) -> bool:
        """Check if required fields are filled if layers are selected."""
        # Require Collar layer at minimum to be considered 'active'
        if not self.c_layer.currentLayer():
            # logger.debug("is_complete: No collar layer selected")
            return False

        # Check Collar fields
        if not self.c_id.currentField():
            logger.debug("is_complete: Collar ID missing")
            return False

        if not self.chk_use_geom.isChecked() and not (
            self.c_x.currentField() and self.c_y.currentField()
        ):
            logger.debug("is_complete: Collar X/Y missing")
            return False

        # If Survey Layer selected, check its fields
        if self.s_layer.currentLayer() and not all(
            [
                self.s_id.currentField(),
                self.s_depth.currentField(),
                self.s_azim.currentField(),
                self.s_incl.currentField(),
            ]
        ):
            logger.debug("is_complete: Survey fields incomplete")
            return False

        # If Interval Layer selected, check its fields
        if self.i_layer.currentLayer() and not all(
            [
                self.i_id.currentField(),
                self.i_from.currentField(),
                self.i_to.currentField(),
                self.i_lith.currentField(),
            ]
        ):
            logger.debug("is_complete: Interval fields incomplete")
            return False

        logger.debug("is_complete: True")
        return True
