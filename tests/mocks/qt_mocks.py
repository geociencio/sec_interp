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
        """Emit signal to connected slots with flexible signature support."""
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except TypeError:
                # If slot doesn't accept all arguments, try calling it without them
                # This emulates PyQt behavior where slots can ignore extra arguments
                try:
                    slot()
                except Exception:
                    pass
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

    @staticmethod
    def getThemeIcon(name):
        """Get theme icon."""
        return MockQIcon()

    @staticmethod
    def initQgis():
        """Initialize QGIS."""
        pass

    @staticmethod
    def exitQgis():
        """Exit QGIS."""
        pass

    @staticmethod
    def taskManager():
        """Get the task manager."""
        return MagicMock(name="QgsTaskManager")


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
    SmoothPixmapTransform = 2

    def __init__(self, *args, **kwargs):
        """Initialize the mock painter."""
        super().__init__(**kwargs)


class MockQImage(MagicMock):
    """Mock implementation for QImage."""

    Format_ARGB32 = 0

    def __init__(self, *args, **kwargs):
        """Initialize the mock image."""
        super().__init__(**kwargs)

    def save(self, path):
        """Mock image saving."""
        return True


class MockQColor(MagicMock):
    """Mock implementation for QColor."""

    def __init__(self, *args, **kwargs):
        """Initialize the mock color."""
        super().__init__()
        self._args = args

    def __eq__(self, other):
        """Compare colors by their initialization arguments."""
        if isinstance(other, MockQColor):
            return self._args == other._args
        return False

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


class MockQSize:
    """Mock implementation for QSize."""

    def __init__(self, w=0, h=0):
        self._w, self._h = w, h

    def width(self):
        return self._w

    def height(self):
        return self._h


class MockQPixmap(MagicMock):
    """Mock implementation for QPixmap."""

    def __init__(self, *args, **kwargs):
        super().__init__()

    def size(self):
        return MockQSize(16, 16)


class MockQIcon(MagicMock):
    """Mock implementation for QIcon."""

    def __init__(self, *args, **kwargs):
        super().__init__()

    def pixmap(self, w, h=None):
        return MockQPixmap()


class MockQRectF(MagicMock):
    """Mock implementation for QRectF."""

    def __init__(self, x=0, y=0, w=0, h=0, *args, **kwargs):
        """Initialize the mock rectangle."""
        super().__init__(*args, **kwargs)
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def width(self):
        return self._w

    def height(self):
        return self._h

    def x(self):
        return self._x

    def y(self):
        return self._y


class MockQSizeF(MagicMock):
    """Mock implementation for QSizeF."""

    def __init__(self, w=0, h=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._w, self._h = w, h

    def width(self):
        return self._w

    def height(self):
        return self._h


class MockQPageSize(MagicMock):
    """Mock implementation for QPageSize."""

    class Unit:
        Point = 0

    def __init__(self, *args, **kwargs):
        super().__init__()


class MockQPdfWriter(MagicMock):
    """Mock implementation for QPdfWriter."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._resolution = 300

    def setResolution(self, res):
        self._resolution = res

    def resolution(self):
        return self._resolution

    def setPageSize(self, size):
        pass

    def setPageMargins(self, margins):
        pass


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

    Accepted = 1
    Rejected = 0

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

    def setAttribute(self, attr, on=True):
        """Set widget attribute."""
        pass

    def accept(self):
        """Accept dialog logic."""
        pass

    def reject(self):
        """Reject dialog logic."""
        pass

    def exec_(self):
        """Mock exec_."""
        return self.Accepted

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
        return getattr(self, "_current_index", 0)

    def setCurrentIndex(self, index):
        """Set current index."""
        self._current_index = index
        self.currentIndexChanged.emit(index)

    def findText(self, text, flags=None):
        """Find text in items."""
        if hasattr(self, "_items") and text in self._items:
            return self._items.index(text)
        elif hasattr(self, "_items"):
            return -1
        return 0

    def addItems(self, items):
        """Add multiple items."""
        if not hasattr(self, "_items"):
            self._items = []
        self._items.extend(items)

    def currentText(self):
        """Get current text."""
        return self._text

    def setPixmap(self, pixmap):
        """Set widget pixmap (for QLabel)."""
        self._pixmap = pixmap

    def pixmap(self):
        """Get widget pixmap."""
        return getattr(self, "_pixmap", None)

    def windowTitle(self):
        """Get window title."""
        return getattr(self, "_window_title", "")

    def setWindowTitle(self, title):
        """Set window title."""
        self._window_title = title

    def setReadOnly(self, local_ro):
        """Set read only status."""
        pass

    def setAutoFillBackground(self, enabled):
        """Set auto fill background."""
        pass

    def setMaximumWidth(self, width):
        """Set maximum width."""
        pass

    def setPlaceholderText(self, text):
        """Set placeholder text."""
        pass

    def setAlignment(self, alignment):
        """Set text alignment."""
        pass

    def setValidator(self, validator):
        """Set input validator."""
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

    def addSpacing(self, spacing):
        """Add spacing to layout."""
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
