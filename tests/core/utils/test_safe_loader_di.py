"""Tests for SafeLoader DI and DataCache granular invalidation."""

import unittest
from unittest.mock import MagicMock

# Import tests to activate QGIS mocks via tests.__init__ -> tests.base_test
from sec_interp import tests  # noqa: F401

from sec_interp.core.utils.safe_loader import SafeLoader
from sec_interp.core.data_cache import DataCache


class TestComponent:
    """Mock component for testing SafeLoader DI."""
    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class TestSafeLoaderDI(unittest.TestCase):
    """Test SafeLoader dynamic argument support."""

    def test_lazy_load_with_args(self):
        """Verify that lazy_load correctly passes arguments to the constructor."""
        # Use a local class for testing
        instance = SafeLoader.lazy_load(
            "tests.core.utils.test_safe_loader_di",
            "TestComponent",
            arg1="hello",
            arg2=123
        )

        self.assertIsNotNone(instance)
        self.assertEqual(instance.arg1, "hello")
        self.assertEqual(instance.arg2, 123)

    def test_lazy_load_failure_returns_none(self):
        """Verify that lazy_load returns None on failure instead of crashing."""
        instance = SafeLoader.lazy_load("non_existent_module", "NonExistentClass")
        self.assertIsNone(instance)


class TestDataCacheGranular(unittest.TestCase):
    """Test DataCache granular invalidation buckets."""

    def setUp(self):
        self.cache = DataCache()
        self.cache._buckets = {
            "topo": {"key1": "data1"},
            "geol": {"key2": "data2"},
            "drill": {"key3": "data3"}
        }

    def test_invalidate_specific_bucket(self):
        """Verify that invalidating a bucket only affects that bucket."""
        self.cache.invalidate("topo")
        self.assertEqual(len(self.cache._buckets["topo"]), 0)
        self.assertEqual(len(self.cache._buckets["geol"]), 1)
        self.assertEqual(len(self.cache._buckets["drill"]), 1)

    def test_invalidate_all_on_section_change(self):
        """Verify that invalidating without arguments clears everything."""
        self.cache.invalidate()
        for bucket in self.cache._buckets.values():
            self.assertEqual(len(bucket), 0)

    def test_invalidate_specific_key(self):
        """Verify that invalidating a specific key works."""
        self.cache.invalidate("geol", "key2")
        self.assertEqual(len(self.cache._buckets["geol"]), 0)
        self.assertEqual(len(self.cache._buckets["drill"]), 1)


if __name__ == "__main__":
    unittest.main()
