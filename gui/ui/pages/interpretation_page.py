"""Interpretation configuration page."""

from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QComboBox,
    QHeaderView,
)

from .base_page import BasePage


class InterpretationPage(BasePage):
    """Page for managing interpretation attributes and custom fields."""

    def __init__(self, parent=None):
        """Initialize the interpretation page."""
        super().__init__(
            QCoreApplication.translate("InterpretationPage", "Interpretation Settings"), parent
        )

    def _setup_ui(self):
        """Set up the UI for interpretation settings."""
        super()._setup_ui()

        self.group_layout = QVBoxLayout()
        self.group_box.setLayout(self.group_layout)

        # 1. Custom Fields Section
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
        self.btn_add_field.clicked.connect(self._add_field_row)
        self.btn_remove_field.clicked.connect(self._remove_field_row)
        btn_layout.addWidget(self.btn_add_field)
        btn_layout.addWidget(self.btn_remove_field)
        self.group_layout.addLayout(btn_layout)

        self.group_layout.addSpacing(15)

        # 2. Inheritance Options
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

    def _add_field_row(self):
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)

        # Type combo
        type_combo = QComboBox()
        type_combo.addItems(["String", "Integer", "Double"])
        self.fields_table.setCellWidget(row, 1, type_combo)

        # Default name
        self.fields_table.setItem(row, 0, QTableWidgetItem(f"field_{row + 1}"))
        self.fields_table.setItem(row, 2, QTableWidgetItem(""))

    def _remove_field_row(self):
        current_row = self.fields_table.currentRow()
        if current_row >= 0:
            self.fields_table.removeRow(current_row)

    def get_data(self) -> dict:
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
