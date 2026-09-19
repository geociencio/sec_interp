import unittest
from unittest.mock import MagicMock

from sec_interp.gui.adapters.geology_extractor import GeologyExtractor
from sec_interp.core.exceptions import DataMissingError


class TestGeologyExtractorOptionalLayer(unittest.TestCase):
    """Test that the GeologyExtractor tolerates an optional outcrop layer."""

    def setUp(self):
        self.extractor = GeologyExtractor()

    def test_validate_inputs_without_outcrop_layer(self):
        """extract_context validation should allow None for outcrop_layer."""
        mock_line = MagicMock()
        mock_line.isValid.return_value = True

        mock_raster = MagicMock()
        mock_raster.isValid.return_value = True
        mock_raster.bandCount.return_value = 1

        try:
            self.extractor._validate_inputs(mock_line, mock_raster, None, "Unit", 1)
        except DataMissingError as e:
            self.fail(f"GeologyExtractor raised DataMissingError for optional layer: {e}")


if __name__ == "__main__":
    unittest.main()
