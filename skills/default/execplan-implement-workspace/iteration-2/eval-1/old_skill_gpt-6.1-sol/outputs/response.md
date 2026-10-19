**The milestone cannot be accepted.** Task tests and conflict-free merges do not prove combined install/prune recovery.

The next task is a **named integration-verification task**, not speculative implementation. Exercise interrupted install followed by prune and recovery against the integrated base tree. Retain results tied to that tree. The coordinator may execute this proof or delegate the named integration task to a fresh worker.

If verification fails, record the reproduced failure and required repair with prerequisites. Delegate the repair through step 5, then repeat affected checks and composed-behavior proof. If verification remains unrun, record the blocker and next owner action.

Keep milestone `Status` and `Acceptance` synchronized with affected `Progress` entries. Reconcile task prerequisites and evidence, `Concrete Steps`, `Validation and Acceptance`, and `Outcomes & Retrospective`. Update `Surprises & Discoveries`, `Decision Log`, and recovery guidance where findings change them. Preserve completed implementation evidence while keeping integration acceptance unmet.
