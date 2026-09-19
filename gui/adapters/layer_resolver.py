"""Layer resolution adapter (GUI seam).

Re-exports the layer resolver so GUI consumers depend on the adapter seam
rather than the core's internal ``utils.qgis`` module. The implementation will
migrate here once core services stop resolving layers directly.
"""

from __future__ import annotations

from sec_interp.core.utils.qgis import LayerResolver, resolve_layer

__all__ = ["LayerResolver", "resolve_layer"]
