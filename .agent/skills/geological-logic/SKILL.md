---
name: geological-logic
description: Standards for handling drillhole data, section interpolation and 3-level validation.
trigger: when implementing geological algorithms, data validation or drillhole processing logic.
scope: root
---

# Geological & Domain Logic Skill

## Data Domain
- **Drillholes**: Handling of collar, survey, and geology (intervals) tables.
- **Sections**: Calculation of intersection points between 3D objects and 2D planes.
- **Interpolation**: Ensuring geometric consistency during manual interpretation.

## 3-Level Validation
Every model and service must implement:
1. **Level 1 (Type)**: Dataclass types and basic range clamps.
2. **Level 2 (Schema)**: Cross-field consistency (e.g., `StartDepth < EndDepth`).
3. **Level 3 (Business)**: External consistency (e.g., "Layer exists in project", "No overlaps in geology").

## Geometry Rules
- **Core Decoupling**: Core services (`GeologyService`, `DrillholeService`) MUST NOT depend on `QgsGeometry`. Use DTOs with WKT strings or point tuples.
- **WKT Standards**: Use WKT-agnostic logic in the core; convert to/from `QgsGeometry` only at the GUI/Exporter boundary.
- **Mocks**: Use `MockQgsGeometry` standards (supports `pointN`, `is3D`) for local unit tests.
- All spatial logic must be unit-tested with varying CRS contexts.
- Handle edge cases like vertical drillholes or parallel section lines.
