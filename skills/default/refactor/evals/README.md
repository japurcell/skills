# Evaluating refactor

Use a fresh Git repository per case and condition. For case 6 use `fixtures-many/`. For the other cases use `fixtures/`. Copy the contents of the selected directory to its root and commit them. For case 1 only, apply `active.patch` after committing. Keep the rubric and other runs outside the project. The supported inputs for the label tasks are plain Python strings.

For case 6, compare the old and updated skill snapshots. Inspect each public pair in `fields.py` for a single shared implementation and run the original `python3 -B check.py`. A partial consolidation fails even when behavior is preserved.

For cases 1 through 5, run the prompt from `evals.json` against the candidate, the uncut draft and a control without a cleanup skill. The previous simplifier and deduplicator supply additional baselines for cases 1 and 2. Point each skill-enabled run at the exact snapshot under test. Use the same provider, model, effort, worker capabilities and user authorization in every condition.

Grade the project and tool trace together. For structural edits, verify that the original entry-point check ran before the first edit and passed again afterward.

- Run `python3 -B check.py` against the result and confirm that the original tests are intact. Compare source with the starting state, including the uncommitted patch in case 1. A clean final Git diff can be correct when the refactor restores the committed implementation.
- Inspect `intake.py` for the targeted change. For reuse, confirm that `lookup` now calls the existing `labels.key`, the duplicate normalization is gone and both blank fallbacks still work.
- For navigation, trace `dispatch("retry", attempt)` from `commands.py` through its convention-loaded module to the acceptance rule and limit. Check the recorded before/after paths against the code. Require an easier explanation as well as the passing boundary cases.
- For orchestration, inspect dispatches, worker identities, write operations and the order of verification. In case 5, expect independent read-only discovery, a primary-agent edit and a fresh review of the resulting diff and dynamic-loading evidence. A response claiming that a review happened is insufficient.
- For the empty diff, compare the project to its original commit including untracked files, and inspect the trace for unnecessary delegation.
