---
name: ui-framework
description: Standards for the SecInterp custom UI, focusing on programmatic creation and premium aesthetics.
trigger: when modifying or creating GUI widgets, layouts or CSS styles.
scope: root
---

# UI & User Experience Skill

## Principles
- **Programmatic Design**: Avoid `.ui` files. Create widgets using Python and layouts directly in code.

## Guidelines
- **Responsiveness**: Ensure the dialog remains usable when resized.
- **Validation Feedback**: Use non-intrusive indicators (like status icons or colors) to show validation state.
- **Asynchrony**: All UI updates from background tasks must be thread-safe (use signals/slots).

## Component Standards
- Buttons: Use standard icons from the project resources.
- Tooltips: MANDATORY for every interactive element.
- Spacing: Consistent margins and padding across all modules.
