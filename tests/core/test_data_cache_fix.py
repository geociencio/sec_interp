
import sys
import os
import unittest
from pathlib import Path

# Add qgispluginsdev to sys.path to allow importing sec_interp as a package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sec_interp.core.data_cache import DataCache

class TestDataCache(unittest.TestCase):
    def setUp(self):
        self.cache = DataCache()
        
    def test_get_cache_key(self):
        params1 = {'a': 1, 'b': 'test'}
        params2 = {'b': 'test', 'a': 1}
        params3 = {'a': 2, 'b': 'test'}
        
        # Order shouldn't matter
        key1 = self.cache.get_cache_key(params1)
        key2 = self.cache.get_cache_key(params2)
        key3 = self.cache.get_cache_key(params3)
        
        self.assertEqual(key1, key2, "Keys should be identical for same params regardless of order")
        self.assertNotEqual(key1, key3, "Keys should differ for different params")
        
    def test_set_and_get(self):
        key = "test_key"
        data = {
            'profile_data': [(0, 100), (10, 110)],
            'geol_data': [(5, 105, 'Granite')],
            'struct_data': [(2, 45)]
        }
        
        self.cache.set(key, data)
        
        # Test unified get
        retrieved = self.cache.get(key)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['profile_data'], data['profile_data'])
        self.assertEqual(retrieved['geol_data'], data['geol_data'])
        self.assertEqual(retrieved['struct_data'], data['struct_data'])
        
        # Test individual gets (checking compatibility)
        self.assertEqual(self.cache.get_topographic_profile(key), data['profile_data'])
        self.assertEqual(self.cache.get_geological_profile(key), data['geol_data'])
        self.assertEqual(self.cache.get_structural_data(key), data['struct_data'])
        
    def test_get_missing(self):
        self.assertIsNone(self.cache.get("nonexistent_key"))

if __name__ == '__main__':
    unittest.main()
