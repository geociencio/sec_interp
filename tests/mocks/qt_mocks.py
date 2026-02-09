"""Qt utility mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQObject


class MockSignal:
    def __init__(self, *args, **kwargs):
        self._slots = []
        self.emit = MagicMock(side_effect=self._emit_to_slots)
        self.connect = MagicMock(side_effect=self._connect_slot)
        self.disconnect = MagicMock()

    def _connect_slot(self, slot):
        self._slots.append(slot)

    def _emit_to_slots(self, *args, **kwargs):
        for slot in self._slots:
            try:
                slot(*args, **kwargs)
            except Exception:
                pass


def mock_signal(*args, **kwargs):
    return MockSignal(*args, **kwargs)


class MockQApplication(MagicMock):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = MagicMock(name="QApplicationInstance")
        return cls._instance

    @staticmethod
    def translate(context, text, disambiguation=None, n=-1):
        return text


class MockQThread(MagicMock):
    @staticmethod
    def sleep(seconds):
        pass

    @staticmethod
    def currentThread():
        return MagicMock(name="CurrentThread")


class MockQPainter(MagicMock):
    Antialiasing = 1

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class MockQImage(MagicMock):
    Format_ARGB32 = 0

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class MockQColor(MagicMock):
    def isValid(self):
        return True

    def darker(self, f=150):
        return self

    def setAlpha(self, a):
        pass

    def red(self):
        return 0

    def green(self):
        return 0

    def blue(self):
        return 0

    @staticmethod
    def fromHsv(h, s, v, a=255):
        return MockQColor()


class MockQPoint:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def x(self):
        return self._x

    def y(self):
        return self._y


class MockQRectF(MagicMock):
    def __init__(self, x=0, y=0, w=0, h=0):
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
    def __init__(self, parent=None, *args, **kwargs):
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

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def setWindowTitle(self, title):
        pass

    def setMinimumSize(self, w, h):
        pass

    def setMaximumSize(self, w, h):
        pass

    def setEnabled(self, enabled):
        pass

    def setChecked(self, checked):
        self._checked = checked
        self.toggled.emit(checked)

    def isChecked(self):
        return self._checked

    def setText(self, text):
        self._text = text
        self.textChanged.emit(text)

    def text(self):
        return self._text

    def setValue(self, val):
        self._value = val
        self.valueChanged.emit(val)

    def value(self):
        return self._value

    def show(self):
        pass

    def hide(self):
        pass

    def update(self):
        pass

    def resize(self, w, h=None):
        pass

    def setFrameShape(self, shape):
        pass

    def setStyleSheet(self, style):
        pass

    def setFixedSize(self, w, h=None):
        pass

    def setIcon(self, icon):
        pass

    def setToolTip(self, tip):
        pass

    def setCheckable(self, checkable):
        pass

    def setOpenExternalLinks(self, open):
        pass

    # ComboBox/List methods
    def addItem(self, text, data=None):
        pass

    def addItems(self, items):
        pass

    def clear(self):
        pass

    def currentIndex(self):
        return 0

    def setCurrentIndex(self, index):
        self.currentIndexChanged.emit(index)

    def currentText(self):
        return self._text


class MockQLayout(MockQObject):
    def __init__(self, parent=None):
        super().__init__()

    def addWidget(self, widget, stretch=0):
        pass

    def addLayout(self, layout):
        pass

    def addStretch(self, s=0):
        pass

    def setContentsMargins(self, l, t, r, b):
        pass

    def setSpacing(self, spacing):
        pass


class MockQListWidget(MockQWidget):
    """Mock for QListWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_row = -1
        self.currentRowChanged = mock_signal()
        self.itemClicked = mock_signal()

    def addItem(self, item):
        self._items.append(item)

    def setCurrentRow(self, row):
        self._current_row = row
        self.currentRowChanged.emit(row)

    def currentRow(self):
        return self._current_row

    def setIconSize(self, size):
        pass

    def setFixedWidth(self, width):
        pass

    def setStyleSheet(self, style):
        pass


class MockQListWidgetItem:
    """Mock for QListWidgetItem."""

    def __init__(self, text=""):
        self._text = text
        self._icon = None
        self._alignment = 0

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text

    def setIcon(self, icon):
        self._icon = icon

    def setTextAlignment(self, alignment):
        self._alignment = alignment
