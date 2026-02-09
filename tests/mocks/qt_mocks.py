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


class MockQWidget(MockQObject):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__()
        self._layout = None
        self._checked = False
        self._text = ""
        self._value = 0
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

    def addWidget(self, widget):
        pass

    def addLayout(self, layout):
        pass

    def addStretch(self, s=0):
        pass

    def setContentsMargins(self, l, t, r, b):
        pass

    def setSpacing(self, s):
        pass
