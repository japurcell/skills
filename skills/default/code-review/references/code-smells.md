# Code Smells

Use these as maintainability/readability heuristics, not standards. Report only high-confidence smells introduced or worsened by the reviewed change.

Rules:

- Repo standards override this file.
- Do not report smells enforced by tooling.
- Label findings as possible smells, not hard rule violations.
- Keep only smells that survive `references/false-positive-rubric.md`.

Smells:

- **Mysterious Name**: a name hides purpose or meaning. Fix by renaming or simplifying.
- **Duplicated Code**: the same logic appears in multiple changed places. Fix with shared code or structure.
- **Feature Envy**: code depends more on another object’s data than its own. Move behavior closer to the data.
- **Data Clumps**: the same fields or parameters travel together repeatedly. Introduce a shared type.
- **Primitive Obsession**: a primitive/string represents a domain concept. Use an explicit type.
- **Repeated Switches**: repeated `switch`/`if` cascades on the same value type. Use one shared map, dispatch table, or polymorphism.
- **Shotgun Surgery**: one logical change requires scattered edits. Group related behavior.
- **Divergent Change**: one module changes for unrelated reasons. Split responsibilities.
- **Speculative Generality**: abstractions, hooks, or options serve no current need. Delete or inline them.
- **Message Chains**: callers navigate long object chains. Expose one method at the right boundary.
- **Middle Man**: code mostly delegates without adding value. Remove the wrapper.
- **Refused Bequest**: a subtype ignores much of its parent contract. Use composition or a narrower interface.
