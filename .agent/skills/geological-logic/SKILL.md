---
name: geological-logic
description: Standards for handling drillhole data, section interpolation, and 3-level validation.
trigger: when implementing geological algorithms, data validation, or drillhole processing logic.
---

# Geological and Domain Logic

Defines the business rules for processing mining/geological data, ensuring geometric consistency and the integrity of drillhole data.

## When to use this skill
- When modifying drillhole processing services (`DrillholeService`).
- When designing interpolation algorithms or section intersections.
- When implementing new geological data validation rules.

## Degree of Freedom
- **Strict**: 3-level validation rules and PyQGIS decoupling are mandatory.

## Workflow
1. **Modeling**: Define entities using Dataclasses and strict types.
2. **Validation**: Implement the 3 levels (Type, Schema, Business).
3. **Abstraction**: Ensure core logic uses WKT or DTOs, not `QgsGeometry`.
4. **Testing**: Create unit tests with varied CRS contexts.

## Instructions and Rules

### 3-Level Validation
1. **Level 1 (Type)**: Basic data types and allowed ranges.
2. **Level 2 (Schema)**: Consistency between fields (e.g., `StartDepth < EndDepth`).
3. **Level 3 (Business)**: External consistency (e.g., "Layer exists", "No overlaps in geology").

### Geometry Rules
- **Decoupling**: Core services MUST NEVER depend on `QgsGeometry`.
- **WKT Standard**: Operate with WKT strings; convert to PyQGIS only at the UI boundary.
- **Endpoint Interpolation**: Mandate interpolation at exact interval depths in `TrajectoryEngine` to guarantee valid segment geometry generation for short intervals.
- **Mocks**: Use `MockQgsGeometry` for local unit tests.

## Quality Checklist
- [ ] Is core logic independent of PyQGIS?
- [ ] Are all 3 validation levels implemented?
- [ ] Do tests exist for edge cases (vertical, parallel drillholes)?
- [ ] Are units and CRS handled correctly?
