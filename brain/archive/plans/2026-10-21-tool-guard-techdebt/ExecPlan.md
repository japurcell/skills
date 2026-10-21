# Remove branch-introduced Tool Guardian duplication

## Purpose / Big Picture

Remove all safe, meaningful duplication introduced by `469a5b3b...8f920e7f` on `codex/refactor-tool-guard-hook`. Preserve observable behavior, security policy, benchmark gates, fixture identities and measured runtime optimizations. The user requested no candidate-count limit and no commits. Installed hooks remain disabled; real-home installation and configuration changes are excluded.

## Progress

- [x] (2026-10-21) [milestone-1] Resolve branch scope and dispatch runtime, harness and test discovery.
- [x] (2026-10-21) [milestone-1] Reconcile runtime, harness and test inventories; overlapping patch-builder findings merged.
- [x] (2026-10-21) [milestone-2] Refactor all14 candidate groups, retaining only distinct/unsafe-to-unify subcontracts.
- [x] (2026-10-21) [milestone-3] Independently validate all14 groups and pass120 integrated tests,54 timing gates and26 resource rows.
- [x] (2026-10-21) [milestone-3] Complete reflection and archive evidence with navigation; leave all changes uncommitted.

## Surprises & Discoveries

Generated copies intentionally duplicate standalone provider code. Historical snapshots, independent expectations and report validation are evidence boundaries rather than automatic cleanup targets. The previous review prohibition on running tests applies only to that completed review, not this authorized refactoring task.

## Decision Log

- Preserve generated ownership: edit canonical sources only and regenerate when necessary.
- Preserve independent expected values, reviewed hashes, report revalidation and timing methodology.
- Runtime changes require appropriate public security checks and before/after performance gates. Prefer a smaller safe refactor or retain a candidate when behavior or performance equivalence cannot be established.

## Outcomes & Retrospective

All14 safe candidate groups are implemented and independently accepted. All120 integrated tests pass. Scoped runtime performance passes54 timing gates across18 affected cases and26 finite-resource rows across13 cases. No repeat or repair was required. No commit, installation or re-enablement occurred. Distinct report formats, filesystem phases, traversal semantics and intentional generated/evidence duplication remain separate.

## Context and Orientation

The accepted implementation spec is [the archived source-delivery plan](../2026-10-21-tool-guard-file-operations/ExecPlan.md). Canonical policy lives in `hooks/runtime/tool_guard_policy.py`, adapters in `hooks/families/tool_guard.py`, and transport in `hooks/families/common.py`. Benchmark infrastructure is `scripts/verify-hook-release.py`, `scripts/benchmark-tool-guard-resources.py` and `scripts/hook_benchmark_support.py`. Fixtures and focused public suites live under `scripts/fixtures/` and `scripts/test-tool-guard-*.py`.

Fixed scope and grouped diffs are retained in `/private/tmp/tool-guard-branch-review-20261021`. That intake's old read-only review instructions are superseded by this plan and the current user request. Only the fixed range and source evidence are reused.

## Plan of Work

### Milestone 1: Classify complete duplication inventory
Status: done
Acceptance: met

D1 inventories scope. D2, D3 and D4 independently inspect runtime, benchmark infrastructure and tests; they require D1. The coordinator deduplicates overlapping findings and records each as actionable or retained with a specific reason. No arbitrary candidate limit applies.

### Milestone 2: Remove safe duplication
Status: done
Acceptance: met

R tasks require the completed discovery inventory. Each worker owns named files, preserves others' edits and makes the smallest behavior-preserving change. Shared-file tasks run sequentially. New source/test design activates TDD. No public API or architecture changes are presumed authorized by cleanup.

### Milestone 3: Verify the integrated result
Status: done
Acceptance: met

Each V task depends on its corresponding R task and uses an independent validator. Run the narrow maintained suites and retain failures. On failure, repair or revert that candidate without weakening checks. Generator mutations and installer tests are serialized. Integrated acceptance requires all selected candidates accounted for, relevant checks passing, no installed-hook changes and no commits. Reflection follows completion of all workers.

## Concrete Steps

No authorized implementation task remains. This plan and its [validation summary](validation-summary.json) are completed evidence. Changes remain uncommitted for user review. Installation, re-enablement, native Windows and full release acceptance are separate actions and are not claimed. Work from `/Users/adam/.codex/worktrees/05ea/skills`, prefix shell commands with `rtk`, and keep disposable evidence under `/private/tmp`.

## Validation and Acceptance

Run the maintained test suite owning each changed invariant. Candidate-specific independent results and integrated commands are recorded below. Preserve fixture payload hashes and counts when factoring construction; preserve separate expected assertions. Do not execute dangerous fixture strings. Any runtime optimization replacement needs whole-hook measurements under unchanged gates; older acceptance cannot prove changed runtime. Native Windows and installed provider dispatch remain separate unverified proof unless actually exercised.

## Idempotence and Recovery

No commit is authorized. Preserve pre-edit file copies or exact Git source before edits; revert only this task's candidate when verification fails. Never discard unrelated changes. Preserve failed test and benchmark reports. Do not rerun unchanged passing checks without a new concern.

## Interfaces and Dependencies

Use existing local helpers where possible; no new runtime dependencies. Public provider JSON, diagnostics, audits, enforcement, release report schemas and versioned expectation manifests remain unchanged.

## Candidate ledger and assignments

- R1: Native data/body-field provenance construction. Runtime worker owns canonical policy only; generate after source edits. Public checks and matched whole-hook timing required.
- F1: Native patch capacity builder. Fixtures worker owns vectors and native-data suite. Preserve historical defaults and hashes.
- F2: Python writer source/wrappers. Fixtures worker owns resource cases and file-operation suite; depends on F1 to serialize fixture ownership.
- F3: Interior JSON padding. Same fixture ownership; depends on F2.
- T1: Local file-operation denial workflow. Test worker follows F2/F3.
- T2: Forced-reader shell fixtures. Test worker owns security-test-support and two public shell suites.
- T3: Synthetic helper-package loaders. Test worker owns generator suite; independent checks run after all writes stop.
- T4: Isolated Guardian test environment. Test worker owns banner suite and tool_guard_test_support; benchmark environment remains separate.
- H1: Shared resource case model/binding. Harness worker owns benchmark resource/release/support/fixture infrastructure.
- H2: Benchmark environment overlays. Same harness ownership after H1; preserve differing precedence.
- H3: Contract-aware response checks. Same ownership after H2; retain independent report revalidation.
- H4: Audit evidence reading. Same ownership after H3; retain independent acceptance policies.
- H5: Failure setup versus fresh failure inspection. Same ownership after H4; never reuse prelaunch proof.
- H6: Reader-limit shape validator. Same ownership after H5; retain independent marker counts and overflow proof.
- Retain H7 sample-retention similarity: report structures and time-field names differ; a parameterized helper would add machinery for two short branches without one shared invariant.
- Retain envelope-versus-content traversal: ordering, width/root counting and first-failure contracts differ. Sharing requires architectural policy parameterization beyond safe deduplication.
- Retain generated copies, old preexisting debt, distinct exceptions/budgets, historical snapshots, expected inventories and independent hash/report verification.

Every R/F/T/H refactor gets an independent validation assignment before acceptance. Pre-refactor runtime is frozen at `/private/tmp/tool-guard-techdebt-20261021/baseline`. Detailed discovery reports remain available in the three exploration agents; no arbitrary candidate limit was applied.

## Verification checkpoint

- F1 accepted independently: all 12 HEAD/current fixture bytes and before/after hashes match; capacity/key/UTF-8/high-line/overflow assertions preserved. Evidence `/private/tmp/tool-guard-f1/`. Native suite passed 26 cases before/after and independently under R1 validation.
- H1 accepted independently: all 12 ordered universe tuples match HEAD, including payloads, metadata, decisions, paths and environments; malformed and unselected stale manifest entries reject before filtering. Seven targeted release tests pass. Evidence `/private/tmp/h1-case-characterization.json`. Distinct case dataclasses retained.
- T2 accepted independently: Copilot 13 and Gemini 15 public scenarios exit 0 with unchanged provider assertions. Evidence `/private/tmp/t2-provider-validation-5unyx5vg/`.
- R1 public correctness: native26/file18/shell18/limits19 and Codex16 pass. Matched warm/cold timing and finite-resource acceptance subsequently passed after the integrated write pause. Evidence `/private/tmp/tool-guard-techdebt-20261021/r1-validation-20261021/`.
- F2/F3 accepted independently: all60 resource inputs, six writer commands and12 boundary payloads match HEAD byte-for-byte; independent budgets/assertions unchanged; file-operations18 pass. Evidence `/private/tmp/tool-guard-f2/`, `/private/tmp/tool-guard-f3/`.
- T1 accepted independently: expanding all seven denial-helper calls yields equivalent complete test-module AST (accounting for F2/F3); dynamic invalid-JSON/nonzero-exit check confirms return-code assertion first. File-operations18 pass.
- T4 accepted independently: 180 exact environment/subprocess comparisons; banner16/native26/shell18/limits19 pass. Evidence `/private/tmp/t4-independent-validation-35uv1nqf/`.
- H2 accepted independently: 48 full environment comparisons against HEAD, precedence/cold/failure semantics retained; narrow test passes.
- T3 direct-import validation accepted independently: six provider/loader combinations and24 executions preserve registration/cache/identities, scanner108 exports including54 aggregated; all26 test methods unchanged. The full26-test generator suite subsequently passed under the integrated write pause.
- H3 accepted independently: 738 HEAD/current response/error/evidence comparisons; six focused tests pass; clock boundary and persisted-report validator independence preserved.
- H4 accepted independently: 522 result/error/read-order comparisons and exact file evidence; three focused tests pass. Lazy parsing preserves first-error precedence.
- H5 accepted independently: 912 exact proof/error comparisons, four targeted tests, fresh proof on each pre/post invocation. Filesystem phase checks retained because combining them requires new phase options or extra reads. H6 accepted independently: 562 shape/caller/error comparisons; strict type/key/range and independent counts preserved.

## Integrated verification

All writers stopped before sequential checks. Generator26, release-verifier37, high-rate-harness3, input-bounds17, helpers13, diagnostics10 and registry14 pass:120 tests, no skips. Generator freshness passed before and after; diff whitespace check passed. Scoped escalation permitted owned generator fixtures and native macOS RSS tests. Logs: `/private/tmp/tool-guard-techdebt-20261021/integrated/`. No repair required.

Final runtime is frozen at `/private/tmp/tool-guard-techdebt-20261021/candidate`; pre-refactor is `baseline` beside it. Matched timing and finite resources completed sequentially without concurrent tests, generators or writes, using candidate-condition contracts for both snapshots.

## Performance acceptance and reflection

The18 affected-case timing comparison passes all54 gates without repeats: two independent25-sample/3-warmup pairs under +2ms median/+5ms p95, and25 fresh-copy cold launches per case/condition under +5/+10ms. Largest positive deltas: warm1 median0.469/p950.139ms, warm2 median1.473/p950.324ms, cold median0.294/p954.172ms. No pooled gate or changed threshold.

All13 finite-resource cases,26 condition rows pass500ms. Maximum measured launch62.99025ms and peak native macOS RSS28,639,232bytes. Strict verifier replay and independent arithmetic, adjacent schedule,2,988 timing/780 resource audit records,71 runtime files per condition and9 harness files per report pass. Sources remain unchanged; baseline matches pre-refactor HEAD and candidate matches current source. Reports are exact-case refactor evidence and explicitly not full-release eligible.

Raw reports: `/private/tmp/tool-guard-techdebt-20261021/r1-timing-01.json`, `r1-resources-01.json`, and `r1-independent-audit-01.json` in that directory. The validation summary retains their hashes, methods, fingerprints and audit conclusions. No benchmark failure or repair occurred.

Reflection: existing brain guidance already captures independent security evidence, measured optimization preservation, generated ownership and isolated tests. No new memory or skill change is warranted. A transient summary-inspection assumption about JSON container type was corrected without source changes; no durable lesson was admitted.

### Recorded integrated commands

From repository root, run sequentially with `rtk proxy python3`: `scripts/test-generate-hooks.py` (26), `scripts/generate-hooks.py --check` (60 files current), `scripts/test-verify-hook-release.py` (37), `scripts/test-benchmark-high-rate-hooks.py` (3), `scripts/test-hook-input-bounds.py` (17), `scripts/test_helpers.py` (13), `scripts/test-hook-diagnostics.py` (10), and `scripts/test_test_all.py` (14), followed by another generator check and `rtk git diff --check`. These checks passed. Generator mutation fixtures and native macOS RSS required scoped sandbox escalation; no real-home installation was used.

Focused public checks also passed: `rtk proxy python3 scripts/test-tool-guard-native-data.py` (26), `scripts/test-tool-guard-file-operations.py` (18), `scripts/test-tool-guard-shell-data.py` (18), `scripts/test-tool-guard-limits.py` (19), and `scripts/test-security-banners.py` (16), plus Bash invocations of all three public Guardian suites. Each uses disposable state. Independent validators retain exact command logs under the evidence directories above.
