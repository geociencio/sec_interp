"""QGIS Feature and Field mocks."""

from unittest.mock import MagicMock
from .qgis_base import MockQgsBase
from .qgis_geometry import MockQgsGeometry


class MockQgsField(MockQgsBase):
    def __init__(self, name="field", type=None, *args, **kwargs):
        super().__init__()
        self._name = name
        self._type = type

    def name(self):
        return self._name

    def type(self):
        return self._type


class MockQgsFields(MockQgsBase):
    def __init__(self):
        super().__init__()
        self._fields = []

    def count(self):
        return len(self._fields)

    def append(self, field):
        self._fields.append(field)

    def __getitem__(self, index):
        return self._fields[index]

    def __len__(self):
        return len(self._fields)

    def __iter__(self):
        return iter(self._fields)

    def indexFromName(self, name):
        for i, f in enumerate(self._fields):
            if f.name() == name:
                return i
        return -1

    def indexOf(self, name):
        return self.indexFromName(name)

    def names(self):
        return [f.name() for f in self._fields]

    def field(self, name):
        idx = self.indexFromName(name)
        return self._fields[idx] if idx != -1 else None

    def at(self, index):
        return self._fields[index]


class MockQgsFeature(MockQgsBase):
    def __init__(self, fields=None):
        super().__init__()
        self._fields = fields or MockQgsFields()
        self._attributes = [None] * len(self._fields)
        self._geometry = MockQgsGeometry()
        self._valid = True

    def setGeometry(self, geom):
        self._geometry = geom

    def geometry(self):
        return self._geometry

    def hasGeometry(self):
        return not self._geometry.isEmpty()

    def setFields(self, fields, initAttributes=True):
        self._fields = fields
        if initAttributes:
            self._attributes = [None] * len(self._fields)

    def setAttribute(self, name, value):
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
        if isinstance(name, int):
            return self._attributes[name]
        idx = self._fields.indexFromName(name)
        return self._attributes[idx] if idx != -1 else None

    def attributes(self):
        return self._attributes

    def setAttributes(self, attrs):
        self._attributes = attrs

    def isValid(self):
        return self._valid

    def id(self):
        return 1

    def fields(self):
        return self._fields

    def __getitem__(self, name):
        return self.attribute(name)

    def __setitem__(self, name, value):
        self.setAttribute(name, value)
