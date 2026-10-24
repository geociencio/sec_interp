"""Feature selector with optional label field for the section line."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsExpression, QgsExpressionContextUtils
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget

from sec_interp.gui.adapters.geometry import get_line_vertices
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_TWO_VERTICES = 2


def _string_attr(obj: Any, name: str) -> str | None:
    """Return a non-empty string attribute, or None."""
    try:
        value = getattr(obj, name)()
    except (AttributeError, TypeError, RuntimeError):
        return None
    return value if isinstance(value, str) and value.strip() else None


def _attribute_text(feature: Any, field: str) -> str:
    """Return a feature attribute as text, or an empty string."""
    try:
        value = feature.attribute(field)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return ""
    return "" if value is None else str(value)


def _automatic_label(layer: Any, feature: Any) -> str:
    """Resolve the layer's display expression/field for a feature."""
    expression_text = _string_attr(layer, "displayExpression")
    if expression_text:
        try:
            expression = QgsExpression(expression_text)
            if expression.isValid():
                context = QgsExpressionContextUtils.createFeatureBasedContext(
                    feature, layer.fields()
                )
                value = expression.evaluate(context)
                if value is not None and str(value).strip():
                    return str(value)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            pass

    display_field = _string_attr(layer, "displayField")
    return _attribute_text(feature, display_field) if display_field else ""


def _label_for(layer: Any, feature: Any, field: str | None) -> str:
    """Resolve the label for one feature (selected field or automatic)."""
    if field:
        return _attribute_text(feature, field)
    return _automatic_label(layer, feature)


def _feature_label(layer: Any, fid: int, feature: Any, field: str | None) -> str:
    """Format a feature as ``fid`` or ``fid — label``."""
    label = _label_for(layer, feature, field)
    return f"{fid} — {label}" if label and label != str(fid) else str(fid)


def _is_two_point(feature: Any) -> bool:
    """Return True only for a single-part line with exactly two vertices."""
    try:
        geometry = feature.geometry()
        if geometry is None or geometry.isNull():
            return False
        if geometry.isMultipart() and len(geometry.asMultiPolyline()) != 1:
            return False
        vertices = get_line_vertices(geometry)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return False
    return len(vertices) == _TWO_VERTICES


def _section_features(layer: Any, limit: int) -> list[tuple[int, Any]]:
    """Collect valid 2-vertex features, capped at ``limit``."""
    features: list[tuple[int, Any]] = []
    try:
        iterator = layer.getFeatures()
    except (AttributeError, RuntimeError):
        return features
    for feature in iterator:
        if len(features) >= limit:
            logger.warning("Section feature list truncated at %s features", limit)
            break
        if not _is_two_point(feature):
            continue
        try:
            fid = int(feature.id())
        except (AttributeError, TypeError, ValueError):
            continue
        features.append((fid, feature))
    return features


def _add_label_fields(combo: QComboBox, layer: Any, auto_label: str) -> None:
    """Fill the label-field combo with Auto plus the layer fields."""
    combo.addItem(auto_label, None)
    try:
        fields = layer.fields()
    except (AttributeError, RuntimeError):
        return
    for field in fields:
        try:
            name = field.name()
        except (AttributeError, TypeError):
            continue
        if name:
            combo.addItem(name, name)


def _refresh_labels(
    combo: QComboBox,
    features: list[tuple[int, Any]],
    layer: Any,
    field: str | None,
) -> None:
    """Rewrite feature labels after the label field changes."""
    for index, (fid, feature) in enumerate(features):
        combo.setItemText(index, _feature_label(layer, fid, feature, field))


class SectionFeatureSelector(QWidget):
    """Select a 2-vertex section feature and the field used for its label.

    The feature combo only lists valid section lines (exactly two vertices,
    single part). The label field combo offers ``Auto`` plus every attribute
    field of the current layer. The selected field only affects the displayed
    text; it does not change the feature id or any preview/cache input.
    """

    featureChanged = pyqtSignal()
    MAX_FEATURES = 500

    def __init__(self, parent: Any = None) -> None:
        """Build the feature and label-field combos."""
        super().__init__(parent)
        self._layer: Any = None
        self._features: list[tuple[int, Any]] = []
        self._populating = False

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(self.tr("Feature")), 0, 0)
        self.feature_combo = QComboBox(self)
        self.feature_combo.setToolTip(self.tr("Select the section line feature"))
        layout.addWidget(self.feature_combo, 0, 1)

        layout.addWidget(QLabel(self.tr("Label field")), 1, 0)
        self.label_field_combo = QComboBox(self)
        self.label_field_combo.setToolTip(self.tr("Field used to label each section feature"))
        layout.addWidget(self.label_field_combo, 1, 1)

        self.feature_combo.currentIndexChanged.connect(self._on_feature_changed)
        self.label_field_combo.currentIndexChanged.connect(self._on_label_field_changed)

    def set_layer(self, layer: Any) -> None:
        """Repopulate both combos from ``layer``."""
        self._layer = layer
        self._features = []
        self._populating = True
        try:
            self.feature_combo.clear()
            self.label_field_combo.clear()
            if layer is None or not getattr(layer, "isValid", lambda: True)():
                self.feature_combo.setEnabled(False)
                self.label_field_combo.setEnabled(False)
                return

            _add_label_fields(self.label_field_combo, layer, self.tr("Auto"))
            self._features = _section_features(layer, self.MAX_FEATURES)
            for fid, feature in self._features:
                self.feature_combo.addItem(
                    _feature_label(layer, fid, feature, self.label_field()), fid
                )
            if self._features:
                self.feature_combo.setCurrentIndex(0)
            self.feature_combo.setEnabled(len(self._features) > 1)
            self.label_field_combo.setEnabled(bool(self._features))
        finally:
            self._populating = False

    def selected_feature_id(self) -> int | None:
        """Return the selected feature id, or None when nothing is selected."""
        if not self._features or self.feature_combo.count() == 0:
            return None
        data = self.feature_combo.currentData()
        return int(data) if isinstance(data, int) else None

    def select_feature(self, feature_id: int | None) -> bool:
        """Select ``feature_id``; return False when it is not a valid feature."""
        if feature_id is None:
            if self._features:
                self.feature_combo.setCurrentIndex(0)
                return True
            return False
        index = self.feature_combo.findData(int(feature_id))
        if index < 0:
            return False
        self.feature_combo.setCurrentIndex(index)
        return True

    def label_field(self) -> str | None:
        """Return the selected label field, or None for automatic labels."""
        data = self.label_field_combo.currentData()
        return str(data) if isinstance(data, str) and data else None

    def set_label_field(self, field_name: str | None) -> bool:
        """Select a label field by name; fall back to Auto when missing."""
        if field_name is None:
            if self.label_field_combo.count():
                self.label_field_combo.setCurrentIndex(0)
            return True
        index = self.label_field_combo.findData(field_name)
        if index < 0:
            if self.label_field_combo.count():
                self.label_field_combo.setCurrentIndex(0)
            return False
        self.label_field_combo.setCurrentIndex(index)
        return True

    def _on_feature_changed(self, _index: int = 0) -> None:
        if self._populating:
            return
        self.featureChanged.emit()

    def _on_label_field_changed(self, _index: int = 0) -> None:
        if self._populating:
            return
        _refresh_labels(
            self.feature_combo,
            self._features,
            self._layer,
            self.label_field(),
        )
