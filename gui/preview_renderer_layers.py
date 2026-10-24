"""Layer collection and extent helpers for PreviewRenderer."""

from __future__ import annotations

from typing import Any

from sec_interp.core.domain import ProfileData


def collect_data_layers(  # noqa: PLR0913, PLR0917
    renderer: Any,
    topo_data,
    geol_data,
    struct_data,
    vert_exag,
    max_points,
    use_adaptive,
    dip_len,
    drill_data,
    interp_data,
    topo_color_mode: str = "gradient",
    topo_ramp_name: str | None = None,
    topo_single_color: str | None = None,
    topo_smooth_data: ProfileData | None = None,
    layer_styles: dict | None = None,
    hidden_interp_ids: set[str] | None = None,
) -> list:
    """Collect all data layers in Z-order."""
    style = layer_styles or {}
    topo_layer = renderer.layer_factory.create_topo_layer(
        topo_data,
        vert_exag,
        max_points,
        use_adaptive,
        topo_color_mode,
        topo_ramp_name,
        topo_single_color,
        line_width=style.get("topo_line_width"),
    )
    if topo_layer:
        renderer.has_topography = True

    topo_smooth = renderer.layer_factory.create_smoothed_topo_layer(
        topo_smooth_data, vert_exag, max_points
    )
    topo_fill = renderer.layer_factory.create_topo_fill_layer(topo_data, vert_exag, max_points)
    geol_layer = renderer.layer_factory.create_geol_layer(geol_data, vert_exag, max_points)
    struct_layer = add_struct_layer(
        renderer, struct_data, topo_data, geol_data, vert_exag, dip_len, style
    )
    drill_layers = add_drillhole_layers(renderer, drill_data, vert_exag, style)
    interp_layer = renderer.layer_factory.create_interp_layer(
        interp_data,
        vert_exag,
        default_color=style.get("interp_color"),
        hidden_ids=hidden_interp_ids,
    )

    candidates = [
        struct_layer,
        geol_layer,
        topo_smooth,
        topo_layer,
        topo_fill,
        *drill_layers,
        interp_layer,
    ]
    return [layer for layer in candidates if layer is not None]


def add_struct_layer(renderer: Any, data, topo, geol, exag, dip_len, style=None) -> Any | None:
    """Create a structural layer if data exists."""
    ref = topo if topo else ([p for segment in geol for p in segment.points] if geol else None)
    style = style or {}
    layer = renderer.layer_factory.create_struct_layer(
        data,
        ref,
        exag,
        dip_len,
        color=style.get("struct_color"),
        width=style.get("struct_width"),
    )
    if layer:
        renderer.has_structures = True
    return layer


def add_drillhole_layers(renderer: Any, data, exag, style=None) -> list:
    """Create drillhole layers if data exists."""
    layers = []
    if not data:
        return layers

    style = style or {}
    trace_layer = renderer.layer_factory.create_drillhole_trace_layer(
        data,
        exag,
        color=style.get("drill_trace_color"),
        width=style.get("drill_trace_width"),
        labels=style.get("drill_labels", True),
    )
    if trace_layer:
        layers.append(trace_layer)

    interval_layer = renderer.layer_factory.create_drillhole_interval_layer(data, exag)
    if interval_layer:
        layers.append(interval_layer)

    if layers:
        renderer.has_drillholes = True
    return layers


def calculate_extent(layers: list) -> Any | None:
    """Combine extents of all given layers."""
    extent = None
    for layer in layers:
        layer_extent = layer.extent()
        if extent is None:
            extent = layer_extent
        else:
            extent.combineExtentWith(layer_extent)
    return extent
