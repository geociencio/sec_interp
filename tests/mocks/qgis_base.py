"""Base QGIS and Qt mocks."""

from unittest.mock import MagicMock


class MockQgsBase:
    """Base class for non-mock QGIS objects to provide standard methods."""

    def isNull(self):
        """Check if the geometry is null."""
        return False

    def isValid(self):
        """Check if the object is valid."""
        return True

    def constGet(self):
        return self

    def get(self):
        return self


class MockQObject:
    """Mock implementation for QObject with basic transition support."""

    def __init__(self, *args, **kwargs):
        """Initialize the mock QObject."""
        pass

    def tr(self, text, disambiguation=None, n=-1):
        """Translate text (returns text as is)."""
        return text

    def setObjectName(self, name):
        """Set object name."""
        pass

    def setToolTip(self, tip):
        """Set tool tip."""
        pass

    def property(self, name):
        """Get property value."""
        return None

    def setProperty(self, name, value):
        """Set property value."""
        pass


class ModuleProxy:
    """A proxy module that captures all attribute accesses as MagicMocks."""

    def __init__(self, name):
        self._name = name

    def __getattr__(self, name):
        if name not in self.__dict__:
            mock = MagicMock(name=f"{self._name}.{name}")
            setattr(self, name, mock)
            return mock
        return self.__dict__[name]

    def reset_mock(self):
        for attr in list(self.__dict__.keys()):
            if not attr.startswith("_"):
                m = getattr(self, attr)
                # Only call reset_mock if it's an instance, not the class
                if hasattr(m, "reset_mock") and not isinstance(m, type):
                    try:
                        m.reset_mock()
                    except (TypeError, AttributeError):
                        pass
