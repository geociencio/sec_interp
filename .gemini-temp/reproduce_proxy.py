import types
from unittest.mock import MagicMock


class ModuleProxy(types.ModuleType):
    def __init__(self, name):
        super().__init__(name)
        self._mock = MagicMock(name=name)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self._mock, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def reset_mock(self):
        self._mock.reset_mock()


class MockClass:
    def __init__(self):
        print("MockClass init")

    def value(self):
        return "RealValue"


proxy = ModuleProxy("test_module")
proxy.MockClass = MockClass

print(f"Proxy MockClass: {proxy.MockClass}")
instance = proxy.MockClass()
print(f"Instance value: {instance.value()}")

proxy.reset_mock()
print(f"After reset, Proxy MockClass: {proxy.MockClass}")
instance = proxy.MockClass()
print(f"After reset, Instance value: {instance.value()}")
