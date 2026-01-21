"""Dialog for editing interpretation properties.

This module provides a dialog to edit the attributes and visual properties
of geological interpretations drawn on the profile.
"""

from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from sec_interp.core.types import InterpretationPolygon


class InterpretationPropertiesDialog(QDialog):
    """Dialog to edit attributes and properties of a newly created interpretation."""

    def __init__(
        self,
        interpretation: InterpretationPolygon,
        custom_fields_config: list[dict[str, Any]],
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the property editor dialog.

        Args:
            interpretation: The interpretation object to edit.
            custom_fields_config: Configuration for extra custom fields.
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self.interpretation = interpretation
        self.custom_fields_config = custom_fields_config
        self.setWindowTitle(self.tr("Interpretation Properties"))
        self.resize(400, 300)

        self.field_widgets: dict[str, QLineEdit] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the user interface components."""
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # 1. Standard Fields
        self.name_edit = QLineEdit(self.interpretation.name)
        form_layout.addRow(self.tr("Name:"), self.name_edit)

        self.type_edit = QLineEdit(self.interpretation.type)
        form_layout.addRow(self.tr("Type:"), self.type_edit)

        # Color picker
        color_layout = QHBoxLayout()
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 20)
        self._set_preview_color(self.interpretation.color)

        self.btn_change_color = QPushButton(self.tr("Change..."))
        self.btn_change_color.clicked.connect(self._pick_color)

        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.btn_change_color)
        color_layout.addStretch()
        form_layout.addRow(self.tr("Color:"), color_layout)

        form_layout.addRow(QLabel("<hr>"))

        # 2. Custom Fields
        if self.custom_fields_config:
            form_layout.addRow(QLabel("<b>" + self.tr("Custom Attributes") + "</b>"))
            for field in self.custom_fields_config:
                name = field["name"]
                default = field["default"]

                edit = QLineEdit(str(default))
                self.field_widgets[name] = edit
                form_layout.addRow(f"{name}:", edit)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _set_preview_color(self, hex_color: str) -> None:
        """Update the color preview label background.

        Args:
            hex_color: Color in hex format (e.g., '#RRGGBB').

        """
        self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")

    def _pick_color(self) -> None:
        """Open a color dialog to change the interpretation color."""
        color = QColor(self.interpretation.color)
        new_color = QColorDialog.getColor(color, self, self.tr("Select Color"))
        if new_color.isValid():
            self.interpretation.color = new_color.name()
            self._set_preview_color(self.interpretation.color)

    def accept(self) -> None:
        """Update interpretation object and close."""
        self.interpretation.name = self.name_edit.text()
        self.interpretation.type = self.type_edit.text()

        # Collect custom attributes
        for name, widget in self.field_widgets.items():
            self.interpretation.attributes[name] = widget.text()

        super().accept()

    def reject(self) -> None:
        """Close dialog without saving."""
        super().reject()
