---
name: pride-check
description: Use after non-trivial code changes to review maintainability, readability, edge cases, simplicity, and whether the touched code is better. Outputs a required `Pride Check:` block. Do not use for read-only or planning-only work.
---

# Pride Check

Use only after code was implemented or revised. Do not use for read-only research, planning-only work, or turns with no code change.

## Steps

1. Confirm code changed.
   - If no code changed, respond: `Pride Check not applicable: no code changed.`

2. Inspect evidence before answering.
   - Review touched files, related tests, and the final diff or summary.
   - If you cannot inspect them, say so. Do not invent file, test, or failure-mode evidence.

3. Evaluate five craft checks:
   - Senior respect: structure, naming, patterns, tradeoffs.
   - Self-explaining: understandable without author narration.
   - Edge cases: relevant empty, missing, invalid, boundary, failure, or recovery paths.
   - Simplicity: solves the actual problem without cleverness or speculative abstraction.
   - Codebase better: leaves the touched area better, not merely changed.

4. Fix weak answers before finalizing.
   - If a check is weak, make the smallest safe improvement in the touched area.
   - Examples: add/regression test, remove dead code, clean imports, rename unclear helper, fix misleading comment, simplify control flow.
   - Do not broaden scope or make unrelated churn.

5. Final response must include this exact section and labels:

```text
Pride Check:
- Senior respect: ...
- Self-explaining: ...
- Edge cases: ...
- Simplicity: ...
- Codebase better: ...
```

## Output rules

- Each line must cite concrete evidence: files, functions, tests, changed behavior, or specific failure modes.
- Avoid generic claims such as `looks good`, `covered`, `cleaner`, `simple`, or `done`.
- Do not claim edge cases, tests, or cleanup that were not actually handled.

## Example

```text
Pride Check:
- Senior respect: `src/report_builder.py` now follows the existing formatter split instead of keeping CSV normalization inline.
- Self-explaining: `format_row` makes the builder flow clear without an explanatory comment.
- Edge cases: `tests/test_report_builder.py` covers blank rows and missing-owner cells.
- Simplicity: One helper removed duplication without introducing a generic reporting framework.
- Codebase better: Removed duplicate row-formatting logic and added a regression test in the touched area.
```
