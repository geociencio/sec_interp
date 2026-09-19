"""Narrow dependency containers injected into dialog managers.

These containers break the managers' dependency on the full dialog surface, so
each manager receives only the collaborators it needs (composition-root
pattern).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pages:
    """Configuration pages consumed by the input manager."""

    dem: Any = None
    section: Any = None
    geology: Any = None
    structure: Any = None
    drillhole: Any = None
    settings: Any = None
