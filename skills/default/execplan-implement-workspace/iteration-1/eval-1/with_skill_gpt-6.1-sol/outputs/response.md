**The milestone cannot be accepted.** Passing task tests and conflict-free merges do not prove combined recovery behavior.

The next task is a named **integration-verification task**: exercise interrupted install followed by prune and recovery on the integrated base tree, using the plan’s acceptance check. Retain actual results. Do not invent implementation changes merely to perform verification.

If the check reproduces an in-scope failure, record an unfinished repair with prerequisites and return it to the execution loop. If blocked or unrun, retain the blocker and keep acceptance unmet.

Reconcile milestone status and acceptance with all affected Progress entries. Keep Concrete Steps, Validation and Acceptance, task prerequisites/evidence, and Outcomes & Retrospective consistent. Update Surprises & Discoveries and Decision Log when findings or decisions change.

Report implementation as integrated, but combined recovery as unverified. Name the next task’s owner and any blocking owner action.
