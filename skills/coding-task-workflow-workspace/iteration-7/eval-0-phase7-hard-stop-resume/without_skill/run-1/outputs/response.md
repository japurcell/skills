# Handoff: `2026-04-23-add-rate-limit-logs` — Phase 8

I have to be upfront: I do **not** have the `coding-task-workflow` skill loaded in this session, so I don't have its authoritative phase definitions or gate checklists in front of me. I can't quote the exact required steps for "Phase 8" of that specific workflow. Rather than invent phase numbers or pretend to follow a spec I can't see, here is what I can responsibly do right now.

## What I can confirm
- Work item: `2026-04-23-add-rate-limit-logs`
- Reported state: **Gate E passed**, entering **Phase 8**
- You want to continue **in this session, now** — no "resume later."

## What a typical "Phase 8" looks like in a staged coding workflow
In most coding-task workflows that gate through A–E before Phase 8, Phase 8 is the **integration / land** phase. Generically it requires:

1. **Re-baseline the branch** — pull latest target branch, rebase or merge, resolve conflicts.
2. **Full verification run** — lint, type-check, unit tests, integration tests, build. All green.
3. **Diff review against the spec** — confirm every acceptance criterion from the work item (here: rate-limit log emission) is covered by code *and* tests.
4. **Observability check** — for a logging change specifically: verify log level, structured fields, redaction of PII/tokens, sampling/rate, and that the new logs don't themselves get rate-limited or spam at steady state.
5. **Docs / changelog update** — note the new log events and any operator-facing fields.
6. **Commit hygiene** — squash WIP, conventional commit message, link the work item, add the `Co-authored-by: Copilot` trailer.
7. **Open or update the PR** — fill the PR template, link Gate E evidence, request review.
8. **Post-merge follow-ups recorded** — dashboards/alerts to update, rollback note.

## What I need from you to actually proceed in this session
To do Phase 8 *correctly* for your workflow (not my generic version), I need one of:

- **(Preferred)** Point me at the skill: confirm the skill name/path so I can load `coding-task-workflow` and follow its real Phase 8 checklist, **or**
- Paste the Phase 8 checklist / gate-F exit criteria here, **or**
- Tell me explicitly: "proceed with the generic integration-phase steps above" and I'll execute them against the repo.

## What I will NOT do
- I will not fabricate workflow-specific gate names, artifact paths, or required commands and then claim I followed them.
- I will not defer the work to "a later session" — I'm ready to execute as soon as you pick one of the three options above.

Reply with the option you want and, if it's option 3, point me at the branch and I'll start with the re-baseline + full verification run immediately.
