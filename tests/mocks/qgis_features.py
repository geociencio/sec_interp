"""QGIS Feature and Field mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQgsBase
from .qgis_geometry import MockQgsGeometry


class MockQgsField(MockQgsBase):
    """Mock implementation for QgsField."""

    def __init__(self, name="field", type=None, *args, **kwargs):
        """Initialize the mock field."""
        super().__init__()
        self._name = name
        self._type = type

    def name(self):
        """Get field name."""
        return self._name

    def type(self):
        """Get field type."""
        return self._type


class MockQgsFields(MockQgsBase):
    """Mock implementation for QgsFields."""

    def __init__(self):
        """Initialize the mock fields collection."""
        super().__init__()
        self._fields = []

    def count(self):
        """Get number of fields."""
        return len(self._fields)

    def append(self, field):
        """Append a field to the collection."""
        self._fields.append(field)

    def __getitem__(self, index):
        """Get field by index."""
        return self._fields[index]

    def __len__(self):
        """Get collection length."""
        return len(self._fields)

    def __iter__(self):
        """Iterate over fields."""
        return iter(self._fields)

    def indexFromName(self, name):
        """Get field index by name."""
        for i, f in enumerate(self._fields):
            if f.name() == name:
                return i
        return -1

    def indexOf(self, name):
        """Get field index by name (alias)."""
        return self.indexFromName(name)

    def names(self):
        """Get all field names."""
        return [f.name() for f in self._fields]

    def field(self, name):
        """Get field by name."""
        idx = self.indexFromName(name)
        return self._fields[idx] if idx != -1 else None

    def at(self, index):
        """Get field at index."""
        return self._fields[index]


class MockQgsFeature(MockQgsBase):
    """Mock implementation for QgsFeature."""

    def __init__(self, fields=None):
        """Initialize the mock feature."""
        super().__init__()
        self._id = fields if isinstance(fields, int) else 1
        self._fields = (
            fields if not isinstance(fields, int) and fields else MockQgsFields()
        )
        self._attributes = [None] * len(self._fields)
        self._geometry = MockQgsGeometry()
        self._valid = True

    def setGeometry(self, geom):
        """Set feature geometry."""
        self._geometry = geom

    def geometry(self):
        """Get feature geometry."""
        return self._geometry

    def hasGeometry(self):
        """Check if feature has geometry."""
        return not self._geometry.isEmpty()

    def setFields(self, fields, initAttributes=True):
        """Set feature fields."""
        old_attributes = self._attributes
        self._fields = fields
        if initAttributes:
            self._attributes = [None] * len(self._fields)
            # Try to preserve attributes by index if they fit
            for i in range(min(len(old_attributes), len(self._attributes))):
                self._attributes[i] = old_attributes[i]

    def setAttribute(self, name, value):
        """Set attribute value by name or index."""
        if isinstance(name, int):
            idx = name
        else:
            idx = self._fields.indexFromName(name)

        if idx != -1:
            # Grow attributes list if needed
            if idx >= len(self._attributes):
                self._attributes.extend([None] * (idx - len(self._attributes) + 1))
            self._attributes[idx] = value

    def attribute(self, name):
        """Get attribute value by name or index."""
        if isinstance(name, int):
            return self._attributes[name]
        idx = self._fields.indexFromName(name)
        return self._attributes[idx] if idx != -1 else None

    def attributes(self):
        """Get all attributes."""
        return self._attributes

    def setAttributes(self, attrs):
        """Set all attributes."""
        self._attributes = attrs

    def isValid(self):
        """Check if feature is valid."""
        return self._valid

    def id(self):
        """Get feature ID."""
        return self._id

    def fields(self):
        """Get feature fields."""
        return self._fields

    def __getitem__(self, name):
        return self.attribute(name)

    def __setitem__(self, name, value):
        self.setAttribute(name, value)
