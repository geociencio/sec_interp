"""Export service shim — maintains backward compatibility.

New implementation lives in :mod:`sec_interp.core.services.export`.
This shim re-exports :class:`ExportService` so existing imports
``from sec_interp.core.services.export_service import ExportService``
and ``sec_interp_plugin.py`` continue to work.
"""

from __future__ import annotations

from sec_interp.core.services.export.orchestrator import ExportService

__all__ = ["ExportService"]
