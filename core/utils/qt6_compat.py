"""Qt6 Compatibility Layer for SecInterp.

Provides monkeypatching for common Qt5 enums that were moved in Qt6,
ensuring the plugin runs on both QGIS 3 (Qt5) and QGIS 4 (Qt6).
"""

from qgis.PyQt.QtCore import QEvent, Qt
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHeaderView,
    QMenu,
    QMessageBox,
    QSizePolicy,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def apply_qt6_patches() -> None:
    """Apply patches to Qt classes to restore Qt5-style enum access."""
    _patch_qt_core()
    _patch_qevent()
    _patch_qframe()
    _patch_qdialogbuttonbox()
    _patch_qmessagebox()
    _patch_qslider()
    _patch_qsizepolicy()
    _patch_qabstractitemview()
    _patch_qheaderview()
    _patch_qpainter()
    _patch_methods()


def _safe_patch(target: type, source_enum: type, names: list[str]) -> None:
    """Safely copy attributes from source_enum to target if they are missing."""
    for name in names:
        if not hasattr(target, name) and hasattr(source_enum, name):
            setattr(target, name, getattr(source_enum, name))


def _patch_methods() -> None:
    """Patch methods that changed names in Qt6 (e.g., exec_ -> exec)."""
    # QDialog.exec_
    if not hasattr(QDialog, "exec_") and hasattr(QDialog, "exec"):
        QDialog.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)

    # QMenu.exec_
    if not hasattr(QMenu, "exec_") and hasattr(QMenu, "exec"):
        QMenu.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)

    # QMessageBox.exec_
    if not hasattr(QMessageBox, "exec_") and hasattr(QMessageBox, "exec"):
        QMessageBox.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)


def _patch_qevent() -> None:
    """Patch QEvent (Type)."""
    if hasattr(QEvent, "Type"):
        _safe_patch(
            QEvent,
            QEvent.Type,
            [
                "Resize",
                "MouseButtonPress",
                "MouseButtonRelease",
                "MouseMove",
                "KeyPress",
                "KeyRelease",
            ],
        )


def _patch_qabstractitemview() -> None:
    """Patch QAbstractItemView (SelectionBehavior, etc.)."""
    if hasattr(QAbstractItemView, "SelectionBehavior"):
        _safe_patch(
            QAbstractItemView,
            QAbstractItemView.SelectionBehavior,
            ["SelectRows", "SelectColumns", "SelectItems"],
        )

    if hasattr(QAbstractItemView, "SelectionMode"):
        _safe_patch(
            QAbstractItemView,
            QAbstractItemView.SelectionMode,
            ["SingleSelection", "MultiSelection", "ExtendedSelection"],
        )


def _patch_qheaderview() -> None:
    """Patch QHeaderView (ResizeMode)."""
    if hasattr(QHeaderView, "ResizeMode"):
        _safe_patch(
            QHeaderView,
            QHeaderView.ResizeMode,
            ["Stretch", "Fixed", "Interactive", "ResizeToContents"],
        )


def _patch_qt_core() -> None:
    """Patch Qt namespace (Alignment, Orientation, etc.)."""
    _patch_alignment()
    _patch_flags()
    _patch_input_types()
    _patch_pen_and_brush()
    _patch_global_color()


def _patch_alignment() -> None:
    """Patch Alignment and Orientation."""
    if hasattr(Qt, "AlignmentFlag"):
        _safe_patch(
            Qt,
            Qt.AlignmentFlag,
            [
                "AlignLeft",
                "AlignRight",
                "AlignHCenter",
                "AlignJustify",
                "AlignTop",
                "AlignBottom",
                "AlignVCenter",
                "AlignCenter",
            ],
        )

    if hasattr(Qt, "Orientation"):
        _safe_patch(Qt, Qt.Orientation, ["Horizontal", "Vertical"])


def _patch_flags() -> None:
    """Patch WindowFlags and WidgetAttributes."""
    if hasattr(Qt, "WindowType"):
        _safe_patch(Qt, Qt.WindowType, ["WindowStaysOnTopHint", "FramelessWindowHint"])

    if hasattr(Qt, "WidgetAttribute"):
        _safe_patch(
            Qt,
            Qt.WidgetAttribute,
            [
                "WA_TranslucentBackground",
                "WA_TransparentForMouseEvents",
                "WA_NoSystemBackground",
                "WA_DeleteOnClose",
            ],
        )

    if hasattr(Qt, "ApplicationAttribute"):
        _safe_patch(
            Qt,
            Qt.ApplicationAttribute,
            ["AA_EnableHighDpiScaling", "AA_UseHighDpiPixmaps"],
        )


def _patch_input_types() -> None:
    """Patch Keyboard, Mouse and Cursor types."""
    if hasattr(Qt, "KeyboardModifier"):
        _safe_patch(
            Qt,
            Qt.KeyboardModifier,
            ["NoModifier", "ControlModifier", "ShiftModifier", "AltModifier"],
        )

    if hasattr(Qt, "MouseButton"):
        _safe_patch(
            Qt,
            Qt.MouseButton,
            ["NoButton", "LeftButton", "RightButton", "MiddleButton"],
        )

    if hasattr(Qt, "CursorShape"):
        _safe_patch(
            Qt,
            Qt.CursorShape,
            [
                "ArrowCursor",
                "UpArrowCursor",
                "CrossCursor",
                "WaitCursor",
                "IBeamCursor",
                "SizeVerCursor",
                "SizeHorCursor",
                "SizeBDiagCursor",
                "SizeFDiagCursor",
                "SizeAllCursor",
                "BlankCursor",
                "SplitVCursor",
                "SplitHCursor",
                "PointingHandCursor",
                "ForbiddenCursor",
                "WhatsThisCursor",
                "BusyCursor",
            ],
        )

    # Keyboard keys (In Qt6 they are under Qt.Key)
    if hasattr(Qt, "Key"):
        _safe_patch(
            Qt,
            Qt.Key,
            [
                "Key_Return",
                "Key_Enter",
                "Key_Escape",
                "Key_Left",
                "Key_Right",
                "Key_Up",
                "Key_Down",
                "Key_Delete",
                "Key_Backspace",
            ],
        )

    # QgsRaster and QgsWkbTypes (QGIS Core)
    try:
        # Patch QgsRaster identify formats if needed
        from qgis.core import Qgis, QgsRaster

        if hasattr(Qgis, "RasterIdentifyFormat"):
            _safe_patch(QgsRaster, Qgis.RasterIdentifyFormat, ["Value", "Feature"])

        # Patch QgsWkbTypes if needed
        from qgis.core import QgsWkbTypes

        if hasattr(Qgis, "WkbType"):
            _safe_patch(
                QgsWkbTypes,
                Qgis.WkbType,
                [
                    "Point",
                    "LineString",
                    "Polygon",
                    "MultiPoint",
                    "MultiLineString",
                    "MultiPolygon",
                ],
            )
    except ImportError:
        pass


def _patch_pen_and_brush() -> None:
    """Patch PenStyle and BrushStyle."""
    if hasattr(Qt, "PenStyle"):
        _safe_patch(
            Qt,
            Qt.PenStyle,
            [
                "NoPen",
                "SolidLine",
                "DashLine",
                "DotLine",
                "DashDotLine",
                "DashDotDotLine",
                "CustomDashLine",
            ],
        )

    if hasattr(Qt, "BrushStyle"):
        _safe_patch(
            Qt,
            Qt.BrushStyle,
            [
                "NoBrush",
                "SolidPattern",
                "Dense1Pattern",
                "Dense2Pattern",
                "Dense3Pattern",
                "Dense4Pattern",
                "Dense5Pattern",
                "Dense6Pattern",
                "Dense7Pattern",
                "HorPattern",
                "VerPattern",
                "CrossPattern",
                "BDiagPattern",
                "FDiagPattern",
                "DiagCrossPattern",
                "LinearGradientPattern",
                "RadialGradientPattern",
                "ConicalGradientPattern",
                "TexturePattern",
            ],
        )


def _patch_global_color() -> None:
    """Patch GlobalColor."""
    if hasattr(Qt, "GlobalColor"):
        _safe_patch(
            Qt,
            Qt.GlobalColor,
            [
                "white",
                "black",
                "red",
                "darkRed",
                "green",
                "darkGreen",
                "blue",
                "darkBlue",
                "cyan",
                "darkCyan",
                "magenta",
                "darkMagenta",
                "yellow",
                "darkYellow",
                "gray",
                "darkGray",
                "lightGray",
                "transparent",
                "color0",
                "color1",
            ],
        )


def _patch_qframe() -> None:
    """Patch QFrame (Shapes and Shadows)."""
    if hasattr(QFrame, "Shape"):
        _safe_patch(
            QFrame,
            QFrame.Shape,
            ["NoFrame", "Box", "Panel", "WinPanel", "HLine", "VLine", "StyledPanel"],
        )

    if hasattr(QFrame, "Shadow"):
        _safe_patch(QFrame, QFrame.Shadow, ["Plain", "Raised", "Sunken"])


def _patch_qdialogbuttonbox() -> None:
    """Patch QDialogButtonBox (StandardButtons and Roles)."""
    if hasattr(QDialogButtonBox, "StandardButton"):
        _safe_patch(
            QDialogButtonBox,
            QDialogButtonBox.StandardButton,
            ["Ok", "Cancel", "Save", "Help", "Open", "Close", "Apply", "Reset"],
        )

    if hasattr(QDialogButtonBox, "ButtonRole"):
        _safe_patch(
            QDialogButtonBox,
            QDialogButtonBox.ButtonRole,
            ["ActionRole", "AcceptRole", "RejectRole"],
        )


def _patch_qmessagebox() -> None:
    """Patch QMessageBox (StandardButtons and Icons)."""
    if hasattr(QMessageBox, "StandardButton"):
        _safe_patch(QMessageBox, QMessageBox.StandardButton, ["Ok", "Cancel"])

    if hasattr(QMessageBox, "Icon"):
        _safe_patch(
            QMessageBox,
            QMessageBox.Icon,
            ["Information", "Warning", "Critical", "Question"],
        )


def _patch_qslider() -> None:
    """Patch QSlider (Orientation)."""
    from qgis.PyQt.QtWidgets import QAbstractSlider

    if hasattr(Qt, "Orientation"):
        _safe_patch(QAbstractSlider, Qt.Orientation, ["Horizontal", "Vertical"])


def _patch_qsizepolicy() -> None:
    """Patch QSizePolicy (Policy)."""
    if hasattr(QSizePolicy, "Policy"):
        _safe_patch(
            QSizePolicy,
            QSizePolicy.Policy,
            [
                "Fixed",
                "Minimum",
                "Maximum",
                "Preferred",
                "Expanding",
                "MinimumExpanding",
                "Ignored",
            ],
        )


def _patch_qpainter() -> None:
    """Patch QPainter (RenderHints, etc.)."""
    from qgis.PyQt.QtGui import QPainter

    if hasattr(QPainter, "RenderHint"):
        _safe_patch(
            QPainter,
            QPainter.RenderHint,
            [
                "Antialiasing",
                "TextAntialiasing",
                "SmoothPixmapTransform",
                "LosslessImageRendering",
            ],
        )
