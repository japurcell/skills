Understanding
- Track: Standard (medium-sized feature, three files, then review).

Workflow-Enforced Execution
1. Discovery and exploration (Phases 1-2)
- Identify affected three files and verify existing patterns before coding.
2. Clarification/design (Phases 3-4)
- Resolve only material ambiguities, then pick one recommended approach.
3. Implementation (Phase 5)
- Required: implement using the tdd skill with explicit red-green-refactor loop.
- This is mandatory on every track and not optional.
4. Quality review (Phase 6)
- Required separate subagent role 1: code-simplifier
- Purpose: identify post-implementation refactoring/simplification opportunities.
- Required separate subagent role 2: independent code-reviewer
- Purpose: evaluate correctness, risk, conventions, and maintainability.
- For Standard track, run multiple independent code-reviewer passes with different focuses when useful.

How requirements are enforced across tracks
- Light track: still requires TDD + code-simplifier + at least one independent code-reviewer.
- Standard track: same mandatory gates, often with deeper exploration and potentially multiple reviewer focuses.
- Deep track: same mandatory gates plus broader exploration/design depth.
- Track changes depth, not the required implementation/review safeguards.

Concrete quality-review sequence
1. Finish implementation with tests green (TDD complete).
2. Launch code-simplifier subagent and apply high-value simplifications.
3. Launch independent code-reviewer subagent(s):
- Reviewer A focus: correctness and edge cases.
- Reviewer B focus: conventions, readability, and maintainability.
4. Fix high-severity findings, rerun tests, summarize residual risks.
