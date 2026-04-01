Understanding
- Track: Standard.
- Request: Decide go/no-go on coding immediately in an unfamiliar repo for a medium-sized feature.

Recommendation
- No-go on starting implementation immediately.
- In feature-dev, medium-sized work in an unfamiliar codebase requires Phase 2 exploration first; skipping it materially increases rework and convention drift risk.

Minimum Pre-Implementation Checklist (must complete first)
1. Similar-feature trace (Phase 2)
- Find at least one analogous feature and trace end-to-end flow (entry point -> business logic -> persistence/API -> tests).
- Output: concrete reference path list and reuse decisions.
2. Architecture touchpoint map (Phase 2)
- Identify exact integration seams and affected modules/files for the new feature.
- Output: file-level impact map with ownership boundaries.
3. Conventions + quality baseline (Phase 2)
- Confirm coding patterns, error-handling style, logging approach, and naming conventions by reading representative files.
- Output: short convention checklist to apply during implementation.
4. Test and CI contract mapping (Phase 2)
- Identify test frameworks, fixture style, required test layers, and CI/lint gates.
- Output: minimal test plan aligned to repo norms.
5. Scope/ambiguity checkpoint (Phase 3)
- Resolve only high-impact unknowns that could change behavior or interfaces.
- Output: bounded assumption list and explicit non-goals.

Why skipping exploration is risky (mapped to workflow)
- Skip Phase 2 -> wrong integration points and duplicated abstractions.
- Skip Phase 3 -> hidden requirement mismatches and scope churn.
- Weak Phase 4 decisioning -> avoidable architecture debt.

Prioritized Clarifying Questions (bounded)
1. What is the exact user-visible behavior and acceptance criteria? (Can change scope and tests.)
2. Are there backward-compatibility constraints or API contracts we cannot break? (Can change design path.)
3. Are there performance/SLA targets for this feature? (Can change implementation strategy.)

Execution Gates Still Required After Checklist
1. Implementation must use TDD with explicit red-green-refactor (Phase 5 requirement on every track).
2. Run a separate code-simplifier pass (Phase 6).
3. Run independent code-reviewer review (Phase 6; one for Light, multiple for Standard/Deep).
