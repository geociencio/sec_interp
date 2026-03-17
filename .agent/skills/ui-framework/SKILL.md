---
name: ui-framework
description: Standards for the custom SecInterp interface, focused on programmatic creation and premium aesthetics.
trigger: when modifying or creating GUI widgets, layouts, or CSS styles.
---

# UI and UX Framework

Defines the rules for creating elegant, responsive, and efficient user interfaces within QGIS, prioritizing full control through code.

## When to use this skill
- When designing new dialogs or tool panels.
- When applying visual styles or subtle animations.
- When improving the usability of existing widgets.

## Degree of Freedom
- **Guided**: Visual design creativity is encouraged as long as programmatic creation and responsiveness are respected.

## Workflow
1. **Design**: Sketch the layout structure (HBox, VBox, Grid).
2. **Implementation**: Create widgets programmatically (avoid `.ui` files).
3. **Style**: Apply custom CSS for a "premium" appearance.
4. **Validation**: Ensure thread safety and visual feedback to the user.

## Instructions and Rules

### Design Principles
- **Programmatic**: Do not use Qt Designer. The entire design lives in Python code.
- **Responsiveness**: The dialog must adapt to different window sizes.
- **Feedback**: Clear visual indicators for validation or loading states.
- **Deterministic Cleanup**: Explicitly disconnect signals and cleanup managers/tools in `closeEvent` to prevent orphaned GraphicsItems (rubber bands) and signal leaks.

### Component Standards
- **Tooltips**: Mandatory for every interactive element.
- **Iconography**: Use standardized project resources.
- **Asynchrony**: UI updates via signals/slots from secondary threads.

## Quality Checklist
- [ ] Has the use of `.ui` files been avoided?
- [ ] Is the interface responsive to resize changes?
- [ ] Are there tooltips for all interaction elements?
- [ ] Are updates thread-safe?
