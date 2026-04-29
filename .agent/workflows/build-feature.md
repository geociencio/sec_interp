---
description: Start the Autonomous AI Developer Pipeline sequence for a new feature.
agent: Architect
skills: [qgis-core, qa-docker]
stop_conditions:
  - "Tests fail after 3 consecutive fix attempts → escalate to user"
  - "Architectural conflict detected between Core and GUI layers → stop and request review"
  - "Implementation plan diverges >30% from approved Technical_Specification.md → re-plan"
---
# Build Feature Autonomous Pipeline

When the user types `/build-feature <requirement>`, orchestrate the development process strictly using `.agent/AGENTS.md` and the modular `.agent/skills/`.

### Execution Sequence:

1. **Strategic Planning Mode**
   Act as the **@architect**. Deeply analyze the `<requirement>`. Use the `geological-logic` and `qgis-core` skills to draft a robust implementation plan.
   - **Important**: Save this plan as `docs/plans/Technical_Specification.md`.
   - **Approval Gate**: You MUST pause execution and eagerly ask the user: "Do you approve of this architecture? You can add comments directly to `Technical_Specification.md` if you want me to rethink any part."
   *(Wait for the user to explicitly type "Approved" or apply their requested feedback before moving to step 2).*

1.5. **Technical Critique (Architect vs. Auditor) 🤖**
   - **Agent Reflection**: Activate the **@auditor** role.
   - **Challenge the Plan**: Identify 3 potential failure points or edge cases in the proposed strategy.
   - **Mitigation**: The @architect must address these points before presenting the plan to the user.
   - **Hallucination Hunt**: Verify that all proposed tool calls and file paths are valid.

2. **Autonomous Execution Phase**
   Shift context. Act as the **@architect** again (now acting as the developer), but strictly follow the approved `Technical_Specification.md`.
   - Write the backend logic and the frontend GUI components according to the Extract-then-Compute standard.
   - Ensure the code adheres perfectly to PyQGIS `v3x` practices while preparing for `v4x`.

3. **Autonomous QA & Bug-Hunting Phase**
   Shift context. Act as the **@qa_engineer**.
   - Write the corresponding isolated unit tests or integration tests.
   - You MUST run `make docker-test` to guarantee native integration within the QGIS environment.
   - Find and fix any dependency mismatches, unhandled errors, or edge cases. Do not stop until all tests pass.

4. **Integration & Handover**
   Shift context to the **@auditor**.
   - Review that the code maintains the `.agent/AGENTS.md` metrics (such as the separation of Core and GUI).
   - **Gen 6 Quality Check**: Run `uv run python scripts/check_cc.py` to ensure no new feature method exceeds CC=10.
   - Once successfully checked, generate an output confirming the feature is ready to be committed!

---

## ⛔ Stop Conditions (Human Escalation Required)

| Condition | Action |
|---|---|
| Tests fail after **3+ fix attempts** on the same root cause | Stop. Report exact error. Ask user for direction. |
| A Core module needs to import from `qgis.gui` | Stop immediately. This violates Extract-then-Compute. Request architectural review. |
| The approved `Technical_Specification.md` no longer matches what was built | Stop. Present delta. Ask user to re-approve or adjust scope. |
| A background thread needs a live QGIS object | Stop. Propose WKT/DTO alternative. Wait for approval. |
