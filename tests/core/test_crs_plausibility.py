"""Tests for the mislabelled-CRS plausibility heuristic."""

from tests.base_test import BaseTestCase

from sec_interp.core.validation.crs_plausibility import implausible_crs_reason
from sec_interp.core.validation.layer_metadata import KIND_RASTER, LayerMetadata


def _meta(**kwargs) -> LayerMetadata:
    base = {"name": "Layer", "is_valid": True, "kind": KIND_RASTER}
    base.update(kwargs)
    return LayerMetadata(**base)


class TestImplausibleCrsReason(BaseTestCase):
    """Conservative extent-vs-CRS plausibility rules."""

    def test_projected_declared_with_degree_extent_is_flagged(self):
        """Declared projected but a sub-metre degree-sized extent is suspect."""
        reason = implausible_crs_reason(
            _meta(
                name="DEM",
                crs_is_geographic=False,
                extent_xmin=-99.0,
                extent_ymin=22.7,
                extent_xmax=-98.99,
                extent_ymax=23.0,
            )
        )
        self.assertIn("DEM", reason)
        self.assertIn("degrees", reason)

    def test_projected_declared_with_tiny_pixel_is_flagged(self):
        """A sub-millimetre pixel in a projected CRS is not believable."""
        reason = implausible_crs_reason(
            _meta(
                crs_is_geographic=False,
                pixel_size_x=1e-4,
                extent_xmin=0.0,
                extent_ymin=0.0,
                extent_xmax=2.0,
                extent_ymax=2.0,
            )
        )
        self.assertNotEqual(reason, "")

    def test_projected_declared_with_large_extent_is_plausible(self):
        """A normal projected extent (metres) is accepted."""
        reason = implausible_crs_reason(
            _meta(
                crs_is_geographic=False,
                extent_xmin=500000.0,
                extent_ymin=4000000.0,
                extent_xmax=510000.0,
                extent_ymax=4010000.0,
            )
        )
        self.assertEqual(reason, "")

    def test_projected_extent_outside_lonlat_bounds_is_plausible(self):
        """A large extent outside lon/lat bounds is accepted as projected."""
        reason = implausible_crs_reason(
            _meta(
                crs_is_geographic=False,
                extent_xmin=0.0,
                extent_ymin=0.0,
                extent_xmax=200.0,
                extent_ymax=200.0,
            )
        )
        self.assertEqual(reason, "")

    def test_geographic_declared_with_lonlat_extent_is_plausible(self):
        """A correctly declared geographic extent is accepted."""
        reason = implausible_crs_reason(
            _meta(
                crs_is_geographic=True,
                extent_xmin=-99.0,
                extent_ymin=22.7,
                extent_xmax=-98.99,
                extent_ymax=23.0,
            )
        )
        self.assertEqual(reason, "")

    def test_geographic_declared_with_projected_extent_is_flagged(self):
        """Declared geographic but coordinates exceed lon/lat bounds."""
        reason = implausible_crs_reason(
            _meta(
                name="Line",
                crs_is_geographic=True,
                extent_xmin=500000.0,
                extent_ymin=4000000.0,
                extent_xmax=510000.0,
                extent_ymax=4010000.0,
            )
        )
        self.assertIn("geographic", reason)
        self.assertIn("projected", reason)

    def test_missing_extent_or_crs_is_not_judged(self):
        """Without extent or CRS kind the heuristic stays silent."""
        self.assertEqual(
            implausible_crs_reason(_meta(crs_is_geographic=False)),
            "",
        )
        self.assertEqual(
            implausible_crs_reason(
                _meta(
                    crs_is_geographic=None,
                    extent_xmin=0.0,
                    extent_ymin=0.0,
                    extent_xmax=0.5,
                    extent_ymax=0.5,
                )
            ),
            "",
        )
        self.assertEqual(implausible_crs_reason(None), "")

    def test_degenerate_extent_is_ignored(self):
        """A zero-size extent is not used as evidence."""
        reason = implausible_crs_reason(
            _meta(
                crs_is_geographic=False,
                extent_xmin=0.0,
                extent_ymin=0.0,
                extent_xmax=0.0,
                extent_ymax=0.0,
            )
        )
        self.assertEqual(reason, "")
