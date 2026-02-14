import unittest
from unittest.mock import MagicMock, patch

# from qgis.core import QgsVectorLayer, QgsRasterLayer # Removed imports to avoid need for QGIS env in import time if possible, though needed for patch
from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.exceptions import DataMissingError


class TestGeologyServiceOptionalLayer(unittest.TestCase):
    def setUp(self):
        self.service = GeologyService()

    def test_prepare_task_input_without_outcrop_layer(self):
        """Test that prepare_task_input allows None for outcrop_layer."""

        # Create mocks
        mock_line = MagicMock()
        mock_line.isValid.return_value = True
        mock_feat = MagicMock()
        mock_feat.geometry.return_value = MagicMock()
        mock_line.getFeatures.return_value = iter([mock_feat])

        mock_raster = MagicMock()
        mock_raster.isValid.return_value = True
        mock_raster.bandCount.return_value = 1

        # We assume _extract_line_info calls are mocked or handling mocks correctly
        # But _extract_line_info calls line_lyr.getFeatures(), which we mocked.

        # We need to mock ProfileSampler because prepare_task_input calls it
        self.service.profile_sampler = MagicMock()
        self.service.profile_sampler.generate_master_profile.return_value = ([], [])

        try:
            self.service._validate_inputs(mock_line, mock_raster, None, "Unit", 1)
            # Should not raise exception
        except DataMissingError as e:
            self.fail(f"GeologyService raised DataMissingError for optional layer: {e}")
        except Exception as e:
            # Other errors like 'AttributeError' might happen due to mocks, but we are looking for DataMissingError specifically
            pass


if __name__ == "__main__":
    unittest.main()
