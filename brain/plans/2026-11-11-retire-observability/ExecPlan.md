# Remove the remaining hook observability integration

## Purpose / Big Picture

Remove `hooks/families/observability.py` and the remaining Copilot/Gemini trace capture integration, generated helpers, dedicated metadata/settings, and tests. RTK forwarding and required-skill startup hooks must retain their public input/output behavior, validation, fallback handling, and ordinary diagnostic audit logging. No retained hook should create observability SQLite databases, transcript state, or NDJSON trace events after this change.

The user authorized this cleanup after learning that the renderer remained shared by RTK and startup hooks. This is a repository change on `codex/remove-hooks`, starting at `87f4f90ad680f0239fe2f2e9891e3cec42d19118`. Normal provider refresh should retire exact owned legacy observability helper files; modified files and existing logs/data remain user-owned. Do not modify a live user installation or erase historical data.

## Progress

- [x] (2026-11-11) [milestone-1] T1: Identify remaining capture consumers and agree removal/preservation boundaries.
- [x] (2026-11-12) [milestone-1] T2: Remove capture implementation and exclusive dependencies, update existing fixtures and documentation, regenerate, and verify retained behavior in an isolated worktree. Depends on T1 and the committed plan.
- [x] (2026-11-12) [milestone-2] T3: Integrate T2 and verify the integrated result with no concurrent repository writes during generator tests. Depends on T2.
- [ ] [milestone-2] T4: Run independent Standards and Spec review of the integrated source, resolve findings through one isolated implementer, and repeat at most three review iterations. Depends on T3.
- [ ] [milestone-2] T5: Reflect, archive the completed plan, and remove the merged implementer worktree/branch. Depends on clean T4 or a clearly reported iteration-limit outcome.

## Surprises & Discoveries

- `hooks/families/common.py` injects optional capture calls into JSON input/output; `hooks/families/rtk.py` imports and calls capture directly. Both integrations must disappear before removing generated helpers.
- `hooks/providers.py` has an observability-only environment-prefix field, while `runtime_home_name` remains used by ordinary audit logging.
- Before T2, helper and generator suites contained capture-only cases. T2 removed those deletion-specific cases while retaining assertions for input parsing, UTF-8, forwarding, startup behavior, and installer safety.

## Decision Log

- 2026-11-11: Remove trace capture completely, preserving separate ordinary audit logging and all RTK/startup behavior. This follows the user's explicit approval of the proposed dependency cleanup.
- 2026-11-11: Preserve exact historical asset hashes in `hooks/registrations.py` for safe upgrades. Do not delete logs/databases/transcripts or modified installed helpers.
- 2026-11-11: Do not add regression tests for a deleted feature. Use existing retained suites and disposable one-off migration checks.
- 2026-11-11: Use one implementer in its own worktree and a persistent integration coordinator. The parent owns dispatch deadlines and independent biaxis review; the coordinator owns plan checkpoints and integration.

## Context and Orientation

`hooks/manifest.py` declares generated ownership. Canonical renderers live in `hooks/families/`; generated copies live under `.copilot/hooks/scripts/` and `.gemini/hooks/scripts/`. `scripts/generate-hooks.py` renders owned files and checks freshness. `hooks/registrations.py` holds exact retirement receipts used by provider installers. `hooks/providers.py` provides renderer metadata. `scripts/tests/hooks/test-generate-hooks.py`, `scripts/tests/tooling/test_helpers.py`, and `scripts/tests/support/test-common.sh` contain remaining trace-specific assertions and environment setup.

Before T2, current guidance appeared in `brain/codebase/hook-observability.md`, related brain indexes/testing guidance, and `docs/adr/0003-sqlite-backed-hook-observability.md`. T2 removed obsolete active guidance and marked the ADR historical. T4 should review the integrated references while distinguishing unrelated uses of “observability” in published skills and preserving historical evidence.

## Plan of Work

### Milestone 1: Remove capture while retaining hook behavior
Status: done
Acceptance: met

T2 is complete in worker commit `6876a6559487bbbf41caebd47ef1093de64087a1`. The worker removed the canonical renderer, both generated helper files and manifest targets, capture calls/metadata, exclusive environment settings, capture-only tests, and obsolete active brain guidance. It retained common/audit helpers, ordinary audit logging, RTK forwarding and validation, and required-skill startup behavior. Exact Copilot/Gemini generated-helper hashes were added to retirement receipts. No unrelated skills or live installations were changed. The worker used an isolated worktree and added no regression tests for the deleted feature.

Observed T2 checks: generation produced 14 targets and was current on a second check; the generator suite passed 12 tests; helper suite passed 8 tests; both RTK suites, both startup suites, Bash installer suite, and PowerShell installer suite exited 0. The PowerShell junction case was skipped because the macOS host cannot create that junction; this is not native Windows evidence. Disposable legacy asset retirement removed unchanged owned helpers, preserved modified helpers, historical NDJSON logs, and unrelated files, and was stable on repeat. The worker made no live-home changes.

### Milestone 2: Integrate and independently review
Status: in progress
Acceptance: not met

T3 is complete. The integration branch fast-forwarded to worker commit `6876a6559487bbbf41caebd47ef1093de64087a1`, whose parent is the plan baseline `9291b24a2b98b9cd14c77f874a0146ee51f56f81`; integrated `HEAD` equals the exact tested worker commit. Integrated generation freshness reports 14 current files and `rtk git diff --check` passes. No retained suites were rerun because the integrated source exactly matches the tested worker commit.

T4 is next: freeze the integrated source against base `9291b24a2b98b9cd14c77f874a0146ee51f56f81`, run separate independent Standards and Spec reviews against the same target, and record findings as frontier tasks. Resolve actionable findings through one isolated implementer and repeat at most three review iterations. Reconcile plan status before freezing each candidate. T5 records final acceptance and reflection, archives the plan and reports, and removes only the clean merged worker worktree and branch.

## Concrete Steps

T2 and T3 are complete. The integrated target is `6876a6559487bbbf41caebd47ef1093de64087a1` on `codex/remove-hooks`. Next, the parent freezes this target and dispatches independent Standards and Spec reviews (T4). Record review findings, if any, as bounded frontier tasks for a single isolated implementer. Commands run from the selected worktree root and are prefixed with `rtk`. The completed worker checkout is `/private/tmp/retire-observability/worktree`; do not remove it until T5.

## Validation and Acceptance

### T2 worker verification

All commands below ran from `/private/tmp/retire-observability/worktree` before the worker commit; integrated `HEAD` is exactly that commit, so the results apply to the integrated source. No implementation suites were redundantly rerun during integration.

- `rtk proxy python3 scripts/generate-hooks.py --write`: generated 14 targets.
- `rtk proxy python3 scripts/generate-hooks.py --check`: current, 14 files; repeated after suites with the same result.
- `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`: 12 tests passed.
- `rtk proxy python3 scripts/tests/tooling/test_helpers.py`: 8 tests passed.
- `rtk proxy bash scripts/tests/hooks/test-hooks-rtk.sh`, `test-gemini-hooks-rtk.sh`, `test-hooks-startup.sh`, and `test-gemini-hooks-startup.sh`: all exited 0. The expected missing-required-skill fixture emitted its hard-stop diagnostic.
- `rtk proxy bash scripts/tests/installers/test-install.sh`: exited 0.
- `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1`: passed; the junction case was skipped because the macOS host cannot create junctions. No native Windows claim is made.
- Disposable legacy asset retirement: unchanged owned helpers were removed; modified helpers, historical NDJSON logs, and unrelated files were preserved; repeat refresh was stable. This was a disposable retirement check, not a claim that a live installation was refreshed.
- `rtk proxy git diff --check`: passed.

### T3 integration verification

- Confirmed integration `HEAD` equals tested worker commit `6876a6559487bbbf41caebd47ef1093de64087a1`, with parent `9291b24a2b98b9cd14c77f874a0146ee51f56f81`.
- `rtk proxy python3 scripts/generate-hooks.py --check`: current, 14 files.
- `rtk proxy git diff --check`: passed.

### T4 acceptance

T4 acceptance requires separate independent Standards and Spec reviews of the same frozen source target, with evidence and frontier tasks recorded in this plan. Any fixes must preserve the user-authorized behavior: remove trace capture, generated helpers, metadata/settings and dedicated tests, while retaining RTK forwarding, startup behavior, input validation/fallbacks, and ordinary audit logging. If issues require changes, use one isolated implementer; allow at most three review iterations. Historical reviewer reports must state clearly that reviewers did not execute tests.

## Idempotence and Recovery

Regeneration and provider refresh are repeatable. Never hand-edit generated outputs. If a retained suite fails, diagnose and fix the underlying retained behavior or stale deleted-feature expectation; never weaken retained assertions to obtain a pass. Recover only task-owned files from the recorded base if needed, preserving other work. Do not execute live-home installers or touch stored observability data.

## Outcomes & Retrospective

The capture removal is implemented and integrated. Canonical and generated trace helpers, capture metadata and settings, capture-only test cases, and obsolete current guidance were removed. RTK forwarding and required-skill startup checks passed; common/audit helpers, ordinary audit logging, validation and fallback behavior remain. Generated freshness and the retained suites passed on the exact integrated commit. The macOS PowerShell junction case was skipped, so no native Windows claim is made. A disposable retirement check confirmed unchanged helper removal, preservation of modified helpers/logs/unrelated files, and stable repeat refresh. No live installations were changed. Independent T4 Standards and Spec review remains pending; milestone 2 acceptance is not yet met.
