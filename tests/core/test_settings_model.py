import unittest
from sec_interp.core.models.settings_model import (
    PluginSettings,
    SectionSettings,
    DemSettings,
    StructureSettings,
    PreviewSettings,
)


class TestSettingsModel(unittest.TestCase):
    """Test suite for settings models and validation logic."""

    def test_section_validation(self):
        """Test validation of section settings."""
        # Valid
        s = SectionSettings(buffer_dist=50.0)
        self.assertEqual(s.buffer_dist, 50.0)

        # Invalid (negative) -> capped at 0
        s = SectionSettings(buffer_dist=-10.0)
        self.assertEqual(s.buffer_dist, 0.0)

        # Type conversion
        s = SectionSettings(buffer_dist="123.4")
        self.assertEqual(s.buffer_dist, 123.4)

    def test_dem_validation(self):
        """Test validation of DEM settings."""
        # Scale < 1 -> capped at 1
        d = DemSettings(scale=0.5)
        self.assertEqual(d.scale, 1.0)

        # Vert exag < 0.1 -> capped at 0.1
        d = DemSettings(vert_exag=0.0)
        self.assertEqual(d.vert_exag, 0.1)

        # Band < 1 -> capped at 1
        d = DemSettings(band=0)
        self.assertEqual(d.band, 1)

    def test_structure_validation(self):
        """Test validation of structure settings."""
        s = StructureSettings(dip_scale_factor=0.0)
        self.assertEqual(s.dip_scale_factor, 0.1)

    def test_preview_validation(self):
        """Test validation of preview settings."""
        p = PreviewSettings(max_points=50)
        self.assertEqual(p.max_points, 100)

    def test_plugin_settings_from_dict(self):
        """Test creation of full settings from nested dictionary."""
        data = {
            "section": {"buffer_dist": -50.0},
            "dem": {"scale": "10000", "vert_exag": 2.5},
            "preview": {"max_points": 50000},
        }

        settings = PluginSettings.from_dict(data)

        self.assertEqual(settings.section.buffer_dist, 0.0)  # Validated
        self.assertEqual(settings.dem.scale, 10000.0)  # Type converted
        self.assertEqual(settings.preview.max_points, 50000)
        self.assertEqual(settings.geology.layer_id, "")  # Default

    def test_to_dict(self):
        """Test serialization to dictionary."""
        settings = PluginSettings()
        data = settings.to_dict()

        self.assertIn("section", data)
        self.assertIn("dem", data)
        self.assertEqual(data["section"]["buffer_dist"], 100.0)


if __name__ == "__main__":
    unittest.main()
