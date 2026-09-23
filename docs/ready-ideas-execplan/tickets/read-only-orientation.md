# Read Only Orientation

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

Which read-only tasks should bypass mandatory memory and conventions pre-reading, and what minimum orientation remains necessary for accurate reviews and reports? Decide wording and placement in `AGENTS.md` without weakening guidance for edits.

---

## Resolution

The user accepted all four recommended decisions:

1. Read-only audits, diff reviews, and reports that make no repository changes qualify for lighter orientation, including nontrivial tasks. A report written into the repository is an edit and does not qualify.
2. No memory file is mandatory at the start of a qualifying read-only task. Start with the requested artifact or diff, then read only repository guidance needed for accurate findings. Consult `.agents/memory/INDEX.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, and area instructions when the task calls for them. Broad reviews still need relevant architecture or conventions when those facts affect the conclusion.
3. If the task changes from read-only analysis to an edit, complete the existing full orientation before the first edit, including the affected area instructions and matching known-issues and testing files. The exception never waives edit-time guidance or the end-of-session documentation pass when that pass applies.
4. Put the exception next to the loading rules in `AGENTS.md` `## Agent Orientation` and align items 1–2 of `## Validation Checklist`; leave the edit-time rule intact. The user's Ready item explicitly requests this protected-section change. Align `.agents/memory/INDEX.md` guidance that currently says to read the index for every task, so no contradictory mandatory pre-read remains.

Suggested wording for the implementation plan: “For read-only audits, diff reviews, and reports that do not change repository files, start with the requested material and load only guidance needed for accurate findings. These tasks are exempt from mandatory pre-reading of INDEX.md, ARCHITECTURE.md, and CONVENTIONS.md. If the task becomes an edit, complete the normal orientation before the first edit.” Match the Validation Checklist and knowledge index to this rule.

Acceptance: a narrow diff review can proceed without loading all three memory files; a broad review loads relevant guidance when necessary; a review that turns into a fix completes full orientation before editing. The AGENTS.md orientation and validation sections, plus the knowledge index, state the same rule.
