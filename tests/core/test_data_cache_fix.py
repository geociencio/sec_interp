import sys
import os
from tests.base_test import BaseTestCase
from sec_interp.core.data_cache import DataCache


class TestDataCache(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.cache = DataCache()

    def test_get_cache_key(self):
        params1 = {"a": 1, "b": "test"}
        params2 = {"b": "test", "a": 1}
        params3 = {"a": 2, "b": "test"}

        # Order shouldn't matter
        key1 = self.cache.get_cache_key(params1)
        key2 = self.cache.get_cache_key(params2)
        key3 = self.cache.get_cache_key(params3)

        self.assertEqual(
            key1, key2, "Keys should be identical for same params regardless of order"
        )
        self.assertNotEqual(key1, key3, "Keys should differ for different params")

    def test_set_and_get(self):
        key = "test_key"
        data = {
            "profile_data": [(0, 100), (10, 110)],
            "geol_data": [(5, 105, "Granite")],
            "struct_data": [(2, 45)],
        }

        self.cache.set("topo", key, data)

        # Test unified get
        retrieved = self.cache.get("topo", key)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["profile_data"], data["profile_data"])
        self.assertEqual(retrieved["geol_data"], data["geol_data"])
        self.assertEqual(retrieved["struct_data"], data["struct_data"])

        # Test individual gets (checking compatibility)
        # In the new API, we use the generic get method
        self.assertEqual(self.cache.get("topo", key), data)
        self.assertEqual(
            self.cache.get("geol", key), None
        )  # Different bucket
        self.cache.set("geol", key, data["geol_data"])
        self.assertEqual(self.cache.get("geol", key), data["geol_data"])
        self.cache.set("struct", key, data["struct_data"])
        self.assertEqual(self.cache.get("struct", key), data["struct_data"])

    def test_get_missing(self):
        self.assertIsNone(self.cache.get("topo", "nonexistent_key"))


if __name__ == "__main__":
    unittest.main()
