# Remove the remaining hook observability integration

## Purpose / Big Picture

Remove `hooks/families/observability.py` and the remaining Copilot/Gemini trace capture integration, generated helpers, dedicated metadata/settings, and tests. RTK forwarding and required-skill startup hooks must retain their public input/output behavior, validation, fallback handling, and ordinary diagnostic audit logging. No retained hook should create observability SQLite databases, transcript state, or NDJSON trace events after this change.

The user authorized this cleanup after learning that the renderer remained shared by RTK and startup hooks. This is a repository change on `codex/remove-hooks`, starting at `87f4f90ad680f0239fe2f2e9891e3cec42d19118`. Normal provider refresh should retire exact owned legacy observability helper files; modified files and existing logs/data remain user-owned. Do not modify a live user installation or erase historical data.

## Progress

- [x] (2026-11-11) [milestone-1] T1: Identify remaining capture consumers and agree removal/preservation boundaries.
- [ ] [milestone-1] T2: Remove capture implementation and exclusive dependencies, update existing fixtures and documentation, regenerate, and verify retained behavior in an isolated worktree. Depends on T1 and the committed plan.
- [ ] [milestone-2] T3: Integrate T2 and verify the integrated result with no concurrent repository writes during generator tests. Depends on T2.
- [ ] [milestone-2] T4: Run independent Standards and Spec review, resolve findings through one isolated implementer, and repeat at most three review iterations. Depends on T3.
- [ ] [milestone-2] T5: Reflect, archive the completed plan, and remove the merged implementer worktree/branch. Depends on clean T4 or a clearly reported iteration-limit outcome.

## Surprises & Discoveries

- `hooks/families/common.py` injects optional capture calls into JSON input/output; `hooks/families/rtk.py` imports and calls capture directly. Both integrations must disappear before removing generated helpers.
- `hooks/providers.py` has an observability-only environment-prefix field, while `runtime_home_name` remains used by ordinary audit logging.
- The existing helper and generator suites contain observability-only cases. Their removal is authorized feature deletion; assertions covering retained parsing, UTF-8, forwarding, and installer safety must remain.

## Decision Log

- 2026-11-11: Remove trace capture completely, preserving separate ordinary audit logging and all RTK/startup behavior. This follows the user's explicit approval of the proposed dependency cleanup.
- 2026-11-11: Preserve exact historical asset hashes in `hooks/registrations.py` for safe upgrades. Do not delete logs/databases/transcripts or modified installed helpers.
- 2026-11-11: Do not add regression tests for a deleted feature. Use existing retained suites and disposable one-off migration checks.
- 2026-11-11: Use one implementer in its own worktree and a persistent integration coordinator. The parent owns dispatch deadlines and independent biaxis review; the coordinator owns plan checkpoints and integration.

## Context and Orientation

`hooks/manifest.py` declares generated ownership. Canonical renderers live in `hooks/families/`; generated copies live under `.copilot/hooks/scripts/` and `.gemini/hooks/scripts/`. `scripts/generate-hooks.py` renders owned files and checks freshness. `hooks/registrations.py` holds exact retirement receipts used by provider installers. `hooks/providers.py` provides renderer metadata. `scripts/tests/hooks/test-generate-hooks.py`, `scripts/tests/tooling/test_helpers.py`, and `scripts/tests/support/test-common.sh` contain remaining trace-specific assertions and environment setup.

Current guidance appears in `brain/codebase/hook-observability.md`, related brain indexes/testing guidance, and the historical `docs/adr/0003-sqlite-backed-hook-observability.md`. Audit current references across the repository, distinguish unrelated uses of the word observability in published skills, and preserve clearly historical evidence while repairing links affected by retirement.

## Plan of Work

### Milestone 1: Remove capture while retaining hook behavior
Status: in progress
Acceptance: not met

T2 is one bounded implementation task because the renderer, imports, generated outputs, and fixture inventory form one coupled deletion. Remove the observability renderer and its two generated helper files, both manifest entries, capture-only fields/constants/calls, and now-unused trace-specific helper/test code. Simplify newly unused capture plumbing without changing input validation or forwarding bytes. Keep common/audit helpers and their independent settings. Record both pre-removal generated helper hashes for safe retirement through existing ownership checks. Update affected current documentation, mark the ADR historical, reconcile brain navigation, and preserve prior plan evidence. Do not edit unrelated skills.

The implementer creates a worktree outside the repository, starts from the integration branch, and merges the latest integration tip before finishing. It activates the TDD skill but follows the explicit no-deletion-regression-tests rule. It activates the commit skill and validates the message before any commit. Acceptance requires generated freshness and affected retained protocol/installer tests to pass, plus a disposable retirement check proving exact helpers are removed, modified helpers and logs preserved, and repeated refresh converges.

### Milestone 2: Integrate and independently review
Status: open
Acceptance: not met

T3 fast-forwards or merges the scoped implementer commit through the coordinator. Verify the integrated source and retain exact command/results, avoiding redundant full reruns when worker checks ran on the exact merged content. T4 pins the base and integrated target and runs separate Standards and Spec reviewers against the same source. Record all findings as frontier tasks, fix actionable findings through the isolated implementer, and review again for at most three iterations. Reconcile plan state before freezing each review candidate. T5 records final acceptance and reflection, archives the plan and reports, and removes only the clean merged worker worktree and branch.

## Concrete Steps

Next, the coordinator commits this plan and confirms the integration baseline. The parent dispatches T2 to a single isolated implementer; no source edits occur before the plan exists. Commands run from the selected worktree root and are prefixed with `rtk`. The integration branch stays `codex/remove-hooks`; use `codex/retire-observability-work` for the implementer and `/private/tmp/retire-observability/worktree` for its checkout.

## Validation and Acceptance

Run `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check`, then `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`. Expect 14 generated targets after removing the two observability helpers; record actual test counts. No concurrent writes during generator tests.

Run `rtk proxy python3 scripts/tests/tooling/test_helpers.py`, both `rtk proxy bash scripts/tests/hooks/test-hooks-rtk.sh` and `test-gemini-hooks-rtk.sh`, and both `rtk proxy bash scripts/tests/hooks/test-hooks-startup.sh` and `test-gemini-hooks-startup.sh`. Existing cases must establish preserved JSON envelopes, UTF-8, retained stdin/trailing-data handling, forwarding/fallback, and startup behavior. Run `rtk proxy bash scripts/tests/installers/test-install.sh` and `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1` for changed generated assets and retirement receipts. Run generator freshness after affected suites and `rtk proxy git diff --check`. Platform-specific skips do not establish native Windows verification.

In disposable provider destinations, seed the old helper bytes from the base commit and refresh through existing installer/merger paths. Observe that unchanged owned helpers disappear, changed helpers remain, unrelated files and runtime logs remain, and a repeated refresh is stable. Keep this one-off evidence outside source tests. Search active hook code, configuration, and maintained tests for capture imports/env keys: only exact migration ownership records should remain where needed. Check changed Markdown links. All results here are expectations until recorded as observed evidence.

## Idempotence and Recovery

Regeneration and provider refresh are repeatable. Never hand-edit generated outputs. If a retained suite fails, diagnose and fix the underlying retained behavior or stale deleted-feature expectation; never weaken retained assertions to obtain a pass. Recover only task-owned files from the recorded base if needed, preserving other work. Do not execute live-home installers or touch stored observability data.

## Outcomes & Retrospective

The dependency inventory and scope are complete. Implementation, integrated verification, and independent review remain pending. Existing common/audit helpers are retained; observability capture and exclusive assets are the authorized removal. No live installations have been changed.
