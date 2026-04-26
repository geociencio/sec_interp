"""Interpretation configuration page."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .base_page import BasePage


class InterpretationPage(BasePage):
    """Page for managing interpretation attributes and custom fields."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the interpretation page."""
        super().__init__(
            QCoreApplication.translate("InterpretationPage", "Interpretation Settings"),
            parent,
        )

    def _setup_ui(self) -> None:
        """Set up the UI for interpretation settings."""
        super()._setup_ui()

        self.group_layout = QVBoxLayout()
        self.group_box.setLayout(self.group_layout)

        # 1. Source Selection
        self.group_layout.addWidget(QLabel("<b>" + self.tr("Interpretation Storage") + "</b>"))
        source_layout = QHBoxLayout()
        self.cb_source = QComboBox()
        self.cb_source.addItems(
            [self.tr("Project (Internal JSON)"), self.tr("Vector Layer (External)")]
        )
        source_layout.addWidget(QLabel(self.tr("Source:")))
        source_layout.addWidget(self.cb_source)
        self.group_layout.addLayout(source_layout)

        from qgis.core import QgsMapLayerProxyModel
        from qgis.gui import QgsMapLayerComboBox

        layer_layout = QHBoxLayout()
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layer_combo.setEnabled(False)
        layer_layout.addWidget(self.layer_combo)
        self.group_layout.addLayout(layer_layout)

        self.chk_auto_sync = QCheckBox(self.tr("Auto-Sync on layer edits"))
        self.chk_auto_sync.setEnabled(False)
        self.chk_auto_sync.setToolTip(
            self.tr("Listen for changes in the target layer and update the preview.")
        )
        self.group_layout.addWidget(self.chk_auto_sync)
        self.group_layout.addSpacing(15)

        self.cb_source.currentIndexChanged.connect(self._on_source_changed)

        # 2. Custom Fields Section
        self.group_layout.addWidget(QLabel("<b>" + self.tr("Custom Attributes") + "</b>"))

        self.fields_table = QTableWidget(0, 3)
        self.fields_table.setHorizontalHeaderLabels(
            [self.tr("Field Name"), self.tr("Type"), self.tr("Default Value")]
        )
        self.fields_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fields_table.setMinimumHeight(150)
        self.group_layout.addWidget(self.fields_table)

        btn_layout = QHBoxLayout()
        self.btn_add_field = QPushButton(self.tr("Add Field"))
        self.btn_remove_field = QPushButton(self.tr("Remove Field"))
        btn_layout.addWidget(self.btn_add_field)
        btn_layout.addWidget(self.btn_remove_field)
        self.group_layout.addLayout(btn_layout)

        self.group_layout.addSpacing(15)

        # 3. Inheritance Options
        self.group_layout.addWidget(QLabel("<b>" + self.tr("Attribute Inheritance") + "</b>"))

        self.chk_inherit_geol = QCheckBox(self.tr("Auto-inherit from Geology layers"))
        self.chk_inherit_geol.setChecked(True)
        self.chk_inherit_geol.setToolTip(
            self.tr("Automatically copy unit name and attributes from the nearest geology segment.")
        )

        self.chk_inherit_drill = QCheckBox(self.tr("Auto-inherit from Drillhole intervals"))
        self.chk_inherit_drill.setChecked(True)
        self.chk_inherit_drill.setToolTip(
            self.tr(
                "Automatically copy rock code and attributes from the nearest drillhole interval."
            )
        )

        self.group_layout.addWidget(self.chk_inherit_geol)
        self.group_layout.addWidget(self.chk_inherit_drill)

    def _on_source_changed(self, index: int) -> None:
        is_layer = index == 1
        self.layer_combo.setEnabled(is_layer)
        self.chk_auto_sync.setEnabled(is_layer)

    def _add_field_row(self) -> None:
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)

        # Type combo
        type_combo = QComboBox()
        type_combo.addItems(["String", "Integer", "Double"])
        self.fields_table.setCellWidget(row, 1, type_combo)

        # Default name
        self.fields_table.setItem(row, 0, QTableWidgetItem(f"field_{row + 1}"))
        self.fields_table.setItem(row, 2, QTableWidgetItem(""))

    def _remove_field_row(self) -> None:
        current_row = self.fields_table.currentRow()
        if current_row >= 0:
            self.fields_table.removeRow(current_row)

    def get_data(self) -> dict[str, Any]:
        """Get the current configuration.

        Returns:
            dict: Custom fields and inheritance settings.

        """
        fields = []
        for i in range(self.fields_table.rowCount()):
            name_item = self.fields_table.item(i, 0)
            type_widget = self.fields_table.cellWidget(i, 1)
            default_item = self.fields_table.item(i, 2)

            if name_item and name_item.text():
                fields.append(
                    {
                        "name": name_item.text(),
                        "type": type_widget.currentText() if type_widget else "String",
                        "default": default_item.text() if default_item else "",
                    }
                )

        return {
            "source_type": "layer" if self.cb_source.currentIndex() == 1 else "json",
            "target_layer_id": (
                self.layer_combo.currentLayer().id() if self.layer_combo.currentLayer() else None
            ),
            "auto_sync": self.chk_auto_sync.isChecked(),
            "custom_fields": fields,
            "inherit_geology": self.chk_inherit_geol.isChecked(),
            "inherit_drillholes": self.chk_inherit_drill.isChecked(),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate fields."""
        # Check for duplicate names
        names = []
        for i in range(self.fields_table.rowCount()):
            item = self.fields_table.item(i, 0)
            if item:
                name = item.text().strip()
                if not name:
                    return False, self.tr("Field name cannot be empty")
                if name in names:
                    return False, self.tr("Duplicate field name: {}").format(name)
                names.append(name)
        return True, ""

    def connect_signals(self) -> None:
        """Connect internal signals for the interpretation page."""
        self.btn_add_field.clicked.connect(self._add_field_row)
        self.btn_remove_field.clicked.connect(self._remove_field_row)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.btn_add_field.clicked.disconnect()
        with contextlib.suppress(TypeError, RuntimeError):
            self.btn_remove_field.clicked.disconnect()
