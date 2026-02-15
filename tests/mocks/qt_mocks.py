"""Qt utility mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQObject


class MockSignal:
    """Mock implementation for PyQt signals."""

    def __init__(self, *args, **kwargs):
        """Initialize the mock signal."""
        self._slots = []
        self.emit = MagicMock(side_effect=self._emit_to_slots)
        self.connect = MagicMock(side_effect=self._connect_slot)
        self.disconnect = MagicMock()

    def _connect_slot(self, slot):
        """Connect a slot to the signal."""
        self._slots.append(slot)

    def _emit_to_slots(self, *args, **kwargs):
        """Emit signal to connected slots."""
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except Exception:
                pass


def mock_signal(*args, **kwargs):
    return MockSignal(*args, **kwargs)


class MockQApplication(MagicMock):
    """Mock implementation for QApplication."""

    _instance = None

    @classmethod
    def instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = MagicMock(name="QApplicationInstance")
        return cls._instance

    @staticmethod
    def translate(context, text, disambiguation=None, n=-1):
        """Translate text."""
        return text

    @staticmethod
    def installTranslator(translator):
        """Install translator."""
        return True


class MockQThread(MagicMock):
    """Mock implementation for QThread."""

    @staticmethod
    def sleep(seconds):
        """Sleep for given seconds."""
        pass

    @staticmethod
    def currentThread():
        """Get the current thread."""
        return MagicMock(name="CurrentThread")


class MockQPainter(MagicMock):
    """Mock implementation for QPainter."""

    Antialiasing = 1

    def __init__(self, *args, **kwargs):
        """Initialize the mock painter."""
        super().__init__(**kwargs)


class MockQImage(MagicMock):
    """Mock implementation for QImage."""

    Format_ARGB32 = 0

    def __init__(self, *args, **kwargs):
        """Initialize the mock image."""
        super().__init__(**kwargs)


class MockQColor(MagicMock):
    """Mock implementation for QColor."""

    def isValid(self):
        """Check if color is valid."""
        return True

    def darker(self, f=150):
        """Get darker version of color."""
        return self

    def setAlpha(self, a):
        """Set alpha channel."""
        pass

    def red(self):
        """Get red channel."""
        return 0

    def green(self):
        """Get green channel."""
        return 0

    def blue(self):
        """Get blue channel."""
        return 0

    @staticmethod
    def fromHsv(h, s, v, a=255):
        """Create color from HSV values."""
        return MockQColor()


class MockQPoint:
    """Mock implementation for QPoint."""

    def __init__(self, x, y):
        """Initialize the mock point."""
        self._x, self._y = x, y

    def x(self):
        """Get X coordinate."""
        return self._x

    def y(self):
        """Get Y coordinate."""
        return self._y


class MockQRectF(MagicMock):
    """Mock implementation for QRectF."""

    def __init__(self, x=0, y=0, w=0, h=0):
        """Initialize the mock rectangle."""
        super().__init__()


class MockQFrame:
    """Mock for QFrame with frame shape constants."""

    # Frame Shape Constants
    StyledPanel = 0x0001
    Panel = 0x0002
    Box = 0x0003
    NoFrame = 0x0000

    def __init__(self, parent=None):
        self._frame_shape = 0
        self._parent = parent

    def setFrameShape(self, shape):
        self._frame_shape = shape

    def setLayout(self, layout):
        pass

    def layout(self):
        return None


class MockQWidget(MockQObject):
    """Mock implementation for QWidget."""

    def __init__(self, parent=None, *args, **kwargs):
        """Initialize the mock widget."""
        super().__init__()
        self._layout = None
        self._checked = False
        self._text = ""
        self.clicked = mock_signal()
        self.toggled = mock_signal()
        self.valueChanged = mock_signal()
        self.textChanged = mock_signal()
        self.stateChanged = mock_signal()
        self.currentIndexChanged = mock_signal()

    def setVisible(self, visible):
        """Set widget visibility."""
        pass

    def setLayout(self, layout):
        """Set widget layout."""
        self._layout = layout

    def layout(self):
        """Get widget layout."""
        return self._layout

    def setWindowTitle(self, title):
        """Set window title."""
        pass

    def setMinimumSize(self, w, h):
        """Set minimum size."""
        pass

    def setMaximumSize(self, w, h):
        """Set maximum size."""
        pass

    def setEnabled(self, enabled):
        """Set enabled status."""
        pass

    def setChecked(self, checked):
        """Set checked status."""
        self._checked = checked
        self.toggled.emit(checked)

    def isChecked(self):
        """Check if widget is checked."""
        return self._checked

    def setText(self, text):
        """Set widget text."""
        self._text = text
        self.textChanged.emit(text)

    def text(self):
        """Get widget text."""
        return self._text

    def setValue(self, val):
        """Set widget value."""
        self._value = val
        self.valueChanged.emit(val)

    def value(self):
        """Get widget value."""
        return self._value

    def show(self):
        """Show widget."""
        pass

    def hide(self):
        """Hide widget."""
        pass

    def update(self):
        """Update widget."""
        pass

    def resize(self, w, h=None):
        """Resize widget."""
        pass

    def setFrameShape(self, shape):
        """Set frame shape."""
        pass

    def setStyleSheet(self, style):
        """Set style sheet."""
        pass

    def setFixedSize(self, w, h=None):
        """Set fixed size."""
        pass

    def setIcon(self, icon):
        """Set widget icon."""
        pass

    def setToolTip(self, tip):
        """Set tool tip."""
        pass

    def setCheckable(self, checkable):
        """Set checkable status."""
        pass

    def setOpenExternalLinks(self, open):
        """Set open external links."""
        pass

    # ComboBox/List methods
    def addItem(self, text, data=None):
        """Add item to list/combo."""
        pass

    def addItems(self, items):
        """Add multiple items."""
        pass

    def clear(self):
        """Clear all items."""
        pass

    def currentIndex(self):
        """Get current index."""
        return 0

    def setCurrentIndex(self, index):
        """Set current index."""
        self.currentIndexChanged.emit(index)

    def currentText(self):
        """Get current text."""
        return self._text

    def setReadOnly(self, local_ro):
        """Set read only status."""
        pass

    def setMaximumWidth(self, width):
        """Set maximum width."""
        pass


class MockQLayout(MockQObject):
    """Mock implementation for QLayout."""

    def __init__(self, parent=None):
        """Initialize the mock layout."""
        super().__init__()

    def addWidget(self, widget, stretch=0):
        """Add widget to layout."""
        pass

    def addLayout(self, layout):
        """Add nested layout."""
        pass

    def addStretch(self, s=0):
        """Add stretch to layout."""
        pass

    def setContentsMargins(self, l, t, r, b):
        """Set contents margins."""
        pass

    def setSpacing(self, spacing):
        """Set layout spacing."""
        pass

    def count(self):
        """Get number of items."""
        return 0

    def insertWidget(self, index, widget):
        """Insert widget at index."""
        pass


class MockQListWidget(MockQWidget):
    """Mock implementation for QListWidget."""

    def __init__(self, parent=None):
        """Initialize the mock list widget."""
        super().__init__(parent)
        self._items = []
        self._current_row = -1
        self.currentRowChanged = mock_signal()
        self.itemClicked = mock_signal()

    def addItem(self, item):
        """Add item to list."""
        self._items.append(item)

    def setCurrentRow(self, row):
        """Set current row."""
        self._current_row = row
        self.currentRowChanged.emit(row)

    def currentRow(self):
        """Get current row."""
        return self._current_row

    def setIconSize(self, size):
        """Set icon size."""
        pass

    def setFixedWidth(self, width):
        """Set fixed width."""
        pass

    def setStyleSheet(self, style):
        """Set style sheet."""
        pass


class MockQListWidgetItem:
    """Mock implementation for QListWidgetItem."""

    def __init__(self, text=""):
        """Initialize the mock item."""
        self._text = text
        self._icon = None
        self._alignment = 0

    def setText(self, text):
        """Set item text."""
        self._text = text

    def text(self):
        """Get item text."""
        return self._text

    def setIcon(self, icon):
        """Set item icon."""
        self._icon = icon

    def setTextAlignment(self, alignment):
        """Set text alignment."""
        self._alignment = alignment
