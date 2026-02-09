"""Settings models using dataclasses for validation.

Provides a structured and validated way to handle plugin configurations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sec_interp.core.validation.validators import (
    validate_and_clamp,
)


@dataclass
class SectionSettings:
    """Settings for the Section page."""

    layer_id: str = ""
    layer_name: str = ""
    buffer_dist: float = 100.0

    def __post_init__(self):
        """Validate settings after initialization."""
        self.buffer_dist = validate_and_clamp(0.0, float("inf"))(self.buffer_dist)


@dataclass
class DemSettings:
    """Settings for the DEM page."""

    layer_id: str = ""
    layer_name: str = ""
    band: int = 1
    scale: float = 50000.0
    vert_exag: float = 1.0

    def __post_init__(self):
        """Validate settings after initialization."""
        self.band = int(validate_and_clamp(1, float("inf"))(self.band))
        self.scale = validate_and_clamp(1.0, float("inf"))(self.scale)
        self.vert_exag = validate_and_clamp(0.1, float("inf"))(self.vert_exag)


@dataclass
class GeologySettings:
    """Settings for the Geology page."""

    layer_id: str = ""
    layer_name: str = ""
    field: str = ""


@dataclass
class StructureSettings:
    """Settings for the Structure page."""

    layer_id: str = ""
    layer_name: str = ""
    dip_field: str = ""
    strike_field: str = ""
    dip_scale_factor: float = 1.0

    def __post_init__(self):
        """Validate settings after initialization."""
        self.dip_scale_factor = validate_and_clamp(0.1, float("inf"))(self.dip_scale_factor)


@dataclass
class DrillholeSettings:
    """Settings for the Drillhole page."""

    # Collar
    collar_layer_id: str = ""
    collar_layer_name: str = ""
    collar_id_field: str = ""
    use_geom: bool = True
    collar_x_field: str = ""
    collar_y_field: str = ""
    collar_z_field: str = ""
    collar_depth_field: str = ""

    # Survey
    survey_layer_id: str = ""
    survey_layer_name: str = ""
    survey_id_field: str = ""
    survey_depth_field: str = ""
    survey_azim_field: str = ""
    survey_incl_field: str = ""

    # Interval
    interval_layer_id: str = ""
    interval_layer_name: str = ""
    interval_id_field: str = ""
    interval_from_field: str = ""
    interval_to_field: str = ""
    interval_lith_field: str = ""

    # Export 3D options
    export_3d_traces: bool = True
    export_3d_intervals: bool = True
    export_3d_original: bool = True
    export_3d_projected: bool = False


@dataclass
class InterpretationSettings:
    """Settings for the Interpretation page."""

    inherit_geol: bool = True
    inherit_drill: bool = True
    custom_fields: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class PreviewSettings:
    """Settings for the preview widget."""

    show_topo: bool = True
    show_geol: bool = True
    show_struct: bool = True
    show_drillholes: bool = True
    show_interpretations: bool = True
    show_legend: bool = True
    auto_lod: bool = False
    adaptive_sampling: bool = True
    max_points: int = 10000

    def __post_init__(self):
        """Validate settings after initialization."""
        self.max_points = int(validate_and_clamp(100, float("inf"))(self.max_points))


@dataclass
class PluginSettings:
    """Main container for all plugin settings."""

    section: SectionSettings = field(default_factory=SectionSettings)
    dem: DemSettings = field(default_factory=DemSettings)
    geology: GeologySettings = field(default_factory=GeologySettings)
    structure: StructureSettings = field(default_factory=StructureSettings)
    drillhole: DrillholeSettings = field(default_factory=DrillholeSettings)
    interpretation: InterpretationSettings = field(default_factory=InterpretationSettings)
    preview: PreviewSettings = field(default_factory=PreviewSettings)
    last_output_dir: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginSettings:
        """Create a PluginSettings instance from a dictionary with validation."""
        # This will be used by ConfigService to load from QgsSettings
        return cls(
            section=SectionSettings(**data.get("section", {})),
            dem=DemSettings(**data.get("dem", {})),
            geology=GeologySettings(**data.get("geology", {})),
            structure=StructureSettings(**data.get("structure", {})),
            drillhole=DrillholeSettings(**data.get("drillhole", {})),
            interpretation=InterpretationSettings(**data.get("interpretation", {})),
            preview=PreviewSettings(**data.get("preview", {})),
            last_output_dir=data.get("last_output_dir", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to a nested dictionary for easier persistence/inspection."""
        import dataclasses

        return dataclasses.asdict(self)
