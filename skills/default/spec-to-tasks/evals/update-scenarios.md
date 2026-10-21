# Completion reconciliation scenarios

These supplemental scenarios exercise updates to completed work. They require semantic review and are separate from the fresh-manifest grader in `grade_benchmark.py`. Run each from the same original state, using an explicit pre-edit skill snapshot for the baseline and the edited skill for comparison. Keep generated manifests and responses outside the maintained skill bundle.

## Starting state

Use complete schema records for these three tasks, with ascending priorities, applicable verification and inline source/context. All three start with `passes: true` and the following supplied historical evidence in `notes`:

| Task | Outcome and prerequisites | Existing evidence |
| --- | --- | --- |
| T001 | Record a decision requiring conflicting destinations to refuse before writes and preserve metadata. No prerequisites. | A decision review matched both guarantees to the supplied requirements. |
| T002 | Verify the supplied inspection record against T001's decision. Depends on T001. | The reviewed record reports `REFUSED_CONFLICT`, `destinationWriteEvents=[]`, and equal metadata before/after. |
| T003 | Record that owner deployment remains excluded. No prerequisites. | The recorded boundary matches the supplied owner policy. |

The evidence proves only these stated outcomes. No record covers repeated attempts, interrupted execution or additional checks. The producer may update task definitions and completion state, but it may not execute tasks or fabricate new evidence.

## Case 1: Unchanged meaning

Request: clarify T001's title and relocate its reference without changing the source meaning, guarantees or checks. Preserve all task IDs and historical notes.

Expected: T001, T002 and T003 remain passed. The producer confirms that the existing evidence still covers the contract instead of reopening tasks solely because text changed.

## Case 2: Changed guarantee

Request: add a requirement that refusal also holds on repeated attempts. Update T001's decision and T002's verification to cover that guarantee; no decision or inspection evidence covers it yet. Preserve IDs and historical evidence.

Expected: T001 and T002 become unfinished. T003 remains passed. Existing notes remain present, with reasons for reopening appended. The producer reports both reopened tasks and does not claim that old evidence proves the new requirement.

## Case 3: Additional required check

Request: add a required manual check to T002 comparing an independently supplied metadata inventory, which is not yet available. T001's decision and T003's boundary are unchanged. Preserve IDs and historical evidence.

Expected: T002 becomes unfinished, its missing evidence stays explicit, and T001/T003 remain passed. Authoring the additional check does not establish execution or completion. Ralph intake presented with a deliberately stale all-true copy must block without rewriting it.

## Review

Compare before/after IDs, flags and notes, and inspect the explanation for each retained or reopened pass. Reject lost historical evidence, blanket resets, invented proof, silently retained stale completion or promotion of an unfinished task during authoring. A matching flag map alone does not prove sufficient source/context or appropriate verification.
