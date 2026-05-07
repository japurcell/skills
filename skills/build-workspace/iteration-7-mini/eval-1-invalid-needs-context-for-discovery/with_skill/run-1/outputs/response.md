Brief: Routine repo exploration belongs to the implementer. NEEDS_CONTEXT must mean missing requirements/constraints or conflicting signals — not "please read the repo and tell me the solution." Respond by pushing discovery back to the implementer and asking for precise missing items if any.

Suggested manager reply to implementer:
- Routine repo exploration is your responsibility; please explore patterns and propose an approach.
- If you still claim NEEDS_CONTEXT, list exactly what's missing (requirements, constraints, conflicting signals).
- Re-dispatch when clarified.

Lean handoff to dispatch (use implementer-prompt.md):
- Task: <task text>
- Success criteria: <explicit checks>
- Known constraints & validation commands: <commands to run>
- File hints: <only already-known files>

Verification: run the narrow stack checks (e.g., pytest/npm test or specified shell checks).
