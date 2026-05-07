I’ll answer from the exact local build-review skill file and avoid changing or validating the repo.

**Review scope:** `review_scope_files` should be the deduped, filtered list:

1. `skills/build-review/SKILL.md`
2. `skills/build-review/implementer-prompt.md`
3. `notes.txt`

Exclude `dist/generated-report.json` because it is gitignored, `scratch.tmp` because it is deleted, and `.gitignore` because the workflow explicitly excludes `.gitignore` itself.

**Code-reviewers:** run **one** code-reviewer, because the filtered scope has 3 files (`<=5 files` means one reviewer over the full list).

**Context to reviewer:** give the reviewer the exact manager-authored scope above, using the same partition as the completed code-simplifier wave; say all wave tasks are already done and the code-simplifier wave is complete; instruct them not to recompute, expand, narrow, or include ignored/deleted/`.gitignore` paths. The final tracking sync only happens after that reviewer returns `DONE`; if they return findings that require fixes, say `the final reviewed sync does not happen yet`.
