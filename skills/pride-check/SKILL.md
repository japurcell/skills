---
name: pride-check
description: Enforces craft review after non-trivial code changes. Use whenever you finish implementing or revising code and need to decide whether the result is maintainable, self-explaining, edge-case-aware, simple at the right level, and leaves the codebase better than before. Also use whenever a hook, reviewer, or teammate asks for a `Pride Check` section or questions code quality beyond correctness. Not for read-only research, planning-only work, or turns with no code change.
---

# Pride Check

## Overview

Turn five craft questions into concrete code improvements and a final response block that proves the change is worth signing. Pride Check is about craftsmanship, not correctness alone.

## When to Use

- After non-trivial code changes: features, bug fixes, refactors, behavior-linked test updates
- When a hook or reviewer asks for a `Pride Check:` section
- When code is technically correct but you still need to judge readability, maintainability, and cleanup quality
- Not for read-only research, planning-only answers, or trivial no-change turns

## Workflow

1. **Confirm this applies.** If no code changed, say the skill does not apply yet and stop. Do not fabricate a Pride Check for read-only work.
2. **Re-read touched files, related tests, and your final diff or summary.** Do not answer from memory.
3. **Ask five questions.** If any answer is weak, fix code, tests, or nearby cleanup before finalizing.
   1. **Senior respect** — would a senior engineer respect the structure, naming, and tradeoffs?
   2. **Self-explaining** — can another engineer understand the changed code without author narration?
   3. **Edge cases** — did you cover the relevant boundary, failure, empty-state, or recovery paths?
   4. **Simplicity** — is this the least complexity that solves the actual problem without clever hacks or speculative abstraction?
   5. **Codebase better** — did you leave the touched area better than you found it, not merely different?
4. **Fix before you narrate.** Pride Check is not permission to explain away weak code. If `Codebase better` is vague, do one adjacent improvement now in the touched area: regression test, dead-code removal, naming cleanup, import cleanup, misleading comment fix, or helper extraction.
5. **End with this exact section.** Hooks and deterministic reviewers depend on these labels.

```text
Pride Check:
- Senior respect: ...
- Self-explaining: ...
- Edge cases: ...
- Simplicity: ...
- Codebase better: ...
```

6. **Ground every line in concrete evidence.** Name specific files, functions, tests, or failure modes. Avoid generic claims like `looks good`, `cleaner now`, or `handled edge cases`.

## Specific Techniques

### What strong answers sound like

- **Senior respect:** mention repo-pattern alignment, stable invariants, or why the abstraction earned its cost.
- **Self-explaining:** mention a renamed helper, straighter control flow, clearer data shape, or deleted misleading comment.
- **Edge cases:** name exact cases and where they are covered, such as `tests/test_auth_session.py`, `None`, empty input, boundary timestamps, retry exhaustion, or missing config.
- **Simplicity:** justify why you stopped at this abstraction level and what extra machinery you deliberately avoided.
- **Codebase better:** name a concrete improvement beyond task minimum: a regression test, import cleanup, dead code removal, or duplicate helper extraction.

### What to do when a line is weak

1. Reopen the touched files.
2. Make the smallest concrete improvement that fixes the weak answer.
3. Update tests if behavior or edge handling changed.
4. Rewrite the line with code-grounded evidence.

### Non-example

Bad:

```text
Pride Check:
- Senior respect: Yes.
- Self-explaining: Cleaner now.
- Edge cases: Covered.
- Simplicity: Simple enough.
- Codebase better: Done.
```

Good:

```text
Pride Check:
- Senior respect: `src/report_builder.py` now follows the repo's existing formatter split instead of keeping CSV normalization inline.
- Self-explaining: Extracting `format_row` into `src/report_formatter.py` makes the builder flow obvious without extra comments.
- Edge cases: `tests/test_report_builder.py` now covers blank rows and missing-owner cells so report generation fails less silently.
- Simplicity: One extracted helper removed duplication without introducing a generic reporting framework.
- Codebase better: Removed duplicated row-formatting logic and added the missing regression test in the touched area.
```

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "Hook only needs the section headings." | Empty headings fail the goal of the skill. Fix weak craft issues before writing the block. |
| "Correctness is already covered, so craftsmanship can slide." | Pride Check exists because correct code can still be painful to maintain. |
| "Task completion means the codebase is better." | Completion alone is not improvement. Name the adjacent quality gain or go make one. |
| "This edit was small, so I can skip rereading touched files." | Small edits still introduce naming, control-flow, and edge-case regressions. |
| "I'll mention edge cases even if I did not actually handle them." | Unsupported claims guarantee noisy follow-up and break trust in the report. |

## Red Flags

- Final response gives generic yes/no claims instead of file-grounded judgments
- `Codebase better` is only "finished the task"
- `Simplicity` praises cleverness or unused abstraction
- `Edge cases` ignores failure or boundary behavior relevant to the change
- Skill is used for read-only analysis or before code changed

## Verification

- [ ] Skill was used only after a real code change or explicitly marked not applicable
- [ ] Touched files and related tests were reread before writing the section
- [ ] Weak answers were fixed in code before the final response
- [ ] Final response includes the exact `Pride Check:` section with all five labels
- [ ] Each line names concrete files, functions, tests, or failure modes
- [ ] `Codebase better` names a real adjacent improvement, not task completion
