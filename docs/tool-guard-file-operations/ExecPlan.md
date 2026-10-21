# Make Tool Guardian file operations reliable and its policy easier to understand

This is the current ExecPlan for `docs/tool-guard-file-operations/`. Source implementation and acceptance measurements are complete on runtime commit `aa4a7976`. Final documentation verification and the coordinated knowledge pass are complete. The retained [validation summary](validation-summary.json) records report hashes, failed observations, exact repeats and all 76 candidate runtime fingerprints. Superseded task instructions and detailed experiments are preserved in [historical evidence](ExecPlan.history-2026-10-21.md); they do not control current work.

## Purpose / Big Picture

Ordinary edits, patches, searches and proven literal file writers now use content budgets without charging document text as executable commands. Dangerous executable actions and incomplete inspection still deny. The recorded legitimate writers pass through generated public hook entrypoints; paired executable variants deny. Native content has a usable1 MiB aggregate decoded UTF-8 capacity, and complete-hook performance satisfies the unchanged acceptance contract.

The policy is easier to inspect through ordinary Python source, unified readable rule records and explicit results and enforcement. Existing caches, representations and bounded survey exceptions remain where removal failed security or behavior checks. Optimizations were replaced only after security review and whole-hook measurements.

### Authorization boundary

The user authorized implementation and completion of T1-T9. They explicitly required installed hooks to remain disabled. No real-home installation, configuration change or re-enablement occurred. Installation and re-enablement require separate user approval. Source acceptance does not establish installed provider dispatch or native Windows behavior. No push or pull request was requested.

## Progress

- [x] (2026-10-20) [milestone-0] P0: Write the plan, address all four initial Astra findings, and obtain its second review before implementation.
- [x] (2026-10-20) [milestone-1] T1: Reproduce historical shell/Python writer failures through public hook processes and freeze sanitized fixtures and the original runtime.
- [x] (2026-10-20) [milestone-1] T2: Verify baseline selection, versioned expectations, audits, harness completeness and baseline measurements.
- [x] (2026-10-20) [milestone-2] T3: Accept the1 MiB boundary after writer-proof, adversarial, throughput and finite-resource experiments; reject4 MiB.
- [x] (2026-10-20) [milestone-3] T4: Deliver native capacity, bounded admission, independent diagnostics and the reviewed v2 harness.
- [x] (2026-10-20) [milestone-3] T5: Deliver quoted shell-heredoc proofs and content/executable accounting.
- [x] (2026-10-20) [milestone-3] T6: Deliver narrow Python writer proofs, wrapper handling, output-effect repairs and trusted action summaries; accept composed behavior.
- [x] (2026-10-20) [milestone-4] T7: Deliver explicit inspection results, enforcement and safe reporting.
- [x] (2026-10-20) [milestone-4] T8: Adopt readable rules and ordinary runtime source; retain pipeline representation/caches and bounded survey exceptions after failed alternatives.
- [x] (2026-10-21) [milestone-5] T9: Complete integrated correctness, security, generator, packaging, diagnostics and recovery verification; repair material review findings.
- [x] (2026-10-21) [milestone-5] T9: Resolve repeated performance failures through reviewed, separately benchmarked repairs and accept final timing against both frozen references.
- [x] (2026-10-21) [milestone-5] T9: Pass all 231 final finite-resource cases with native RSS collection and unchanged sources.
- [x] (2026-10-21) [milestone-5] T9: Finish documentation verification and the coordinated knowledge pass; close milestone 5 at source delivery.

## Surprises & Discoveries

Historical writer failures were not solely byte limits: sanitized shell and Python document writers were denied at 721 and 860 tokens against 256. Native edit contents containing dangerous-looking examples already belonged to data. Reclassifying whole arbitrary commands as data would have created bypasses; writer proofs must cover the complete supported syntax and execution context.

Prototype review found assigned-print effects and nested or sequential stdout consumers could erase executable context. Repairs track output effects independently of proof eligibility and propagate consumer context through recursive sinks and shared stdout. The narrow Python recognizer is not a general sandbox or a guarantee about a saved script's future execution.

Raw JSON bytes, decoded content, normalized executable bytes, structural markers, recursive work and reporting size are separate budgets. Escaping can expand content sixfold. Reader checks precede JSON decoding; policy budgets follow it. None is a universal process-memory bound.

Whole-hook measurements caught performance costs that isolated regex diagnostics missed. Single-quote character iteration, per-Unicode-escape reader work and per-escape dynamic searches needed separate repairs. A Unicode optimization passed a limited matrix but regressed high-line patches by26 ms; the final repair matrix therefore included every capacity fixture. All rejected attempts and failed observations remain retained.

## Decision Log

- Preserve exact native provider schemas and strict fallback for unknown aliases, extra fields, invalid types and unsupported syntax. Preserve patch delete/move-source checks and denial on incomplete inspection in block and warn modes.
- Separate inert body data only after a complete supported proof. A proof never exempts remaining executable arguments or removes executable output-consumer context.
- Use1,048,576 aggregate decoded UTF-8 content bytes and32,768 normalized executable bytes. Source admission is1,081,344bytes and recursive work2,162,688bytes. Guardian raw transport is6,889,472bytes with4,096 outside-string structural markers. Keep independent metadata, token, parser, syntax and deadline checks. The4 MiB alternative failed the existing finite-case ceiling.
- Retain AST/syntax preflight limits and whole-executable charging on unproved sources. Python proof limits include2,048 AST nodes/depth 32 and1,024 syntax nodes/depth 32. Exact current diagnostics and constants are owned by source and tests.
- Use trusted fixed action summaries and bounded redacted tool labels. Never copy arbitrary payload or matched credential values into diagnostics or audit records.
- Adopt unified six-field RULES and explicit InspectionResult/enforcement. Retain precomputed matchers, _ScanText caches and suffix summaries. Reject direct parsed-pipeline replacement because a nested producer-to-shell control became allowed. Retain bounded survey exceptions because removing them denied legitimate probes.
- Extract canonical policy to ordinary `hooks/runtime/tool_guard_policy.py`; generate provider-local copies through `hooks/families/tool_guard.py`. Preserve explicit imports, lazy unused dependencies, delivery closure and build identities.
- Preserve timing gates: two independent matched warm pairs with 25 samples/3 warmups, reversed order in pair2; warm median/p95 allowances+2/+5ms. Cold uses25 fresh-copy launches per case/condition, zero provider bytecode; median/p95 allowances+5/+10ms. OS and standard-library caches remain uncleared.
- Retain every failed observation. Permit exact isolated repeats only; recurring or systematic violations require repair. Neither pooling pairs nor changing thresholds is permitted. Full final comparisons use fixed T6 `65cd978` and original `effd0d7b` references. Original capacity observations never become relative-gate passes.
- On2026-10-21, accept final runtime `aa4a7976` against both references after the documented isolated repeats and all 231 resources. Keep installed hooks disabled. Native Windows remains separate outstanding platform proof.

## Outcomes & Retrospective

Milestones 0-4 are accepted. T9 source, security, packaging, final performance and documentation acceptance are met. All authorized ExecPlan tasks are complete. Native edits and supported literal writers now accept document bodies within1 MiB while strict executable and incomplete-inspection protections remain. Policy source and reporting are simpler without removing measured caches or necessary exceptions.

Repeated final performance failures required three bounded repairs: span-based single-quote scanning, Unicode escape batching, and escape-run batching across ordinary string spans. The final change improves high-line patch warm medians77-78ms against its immediate predecessor while preserving quoted and escaped fast paths. Prior failed candidates remain failures.

Both full timing comparisons validate279 cases, with 1116 warm and 13950 cold rows each. Fixed-T6 has 837 gates; original-relative has 657 gates and 180 capacity observations. Three isolated final p95 violations pass their exact full-method repeats, with original failures preserved. Final231-case resources all pass500 ms, worst launch133.413417ms and peak RSS48,660,480bytes on this host. These are finite fixture results, not a universal latency or memory guarantee.

Installed hooks remain disabled and untouched. Native Windows execution and real provider dispatch remain unverified. A Windows owner can run the native suites separately; live installation or re-enablement remains the user's decision.

## Context and Orientation

- `hooks/runtime/tool_guard_policy.py` owns provider-aware schemas, budgets, writer proofs, matching and inspection results. Its relative scan_allowlist/scan_reporting imports resolve in generated provider-local helper packages.
- `hooks/families/tool_guard.py` renders bootstrap, audit and provider envelopes and delivers the canonical policy helper. `hooks/families/common.py` owns bounded JSON transport; all owned outputs come from `scripts/generate-hooks.py`.
- `hooks/families/reporting.py` owns shared build identity and small safe diagnostic primitives. `hooks/families/diagnostics.py` reads canonical runtime Guardian constants so published limits/build identities stay correct.
- Generated adapters/helpers remain separated under `.codex/`, `.copilot/`, `.gemini/` and applicable `.github/` targets. Installers deliver existing reviewed helper closures; no cross-provider runtime import or new packaging asset is introduced.
- `scripts/fixtures/tool_guard_file_operations_expectations.json` owns versioned case-specific decision/audit contracts and original/equivalent case partitions. SHA256 is `59174284ca686cb27cf5a5e4c2f58afa8c964a5d5009b29e27d22b9e4a253c7a`.
- `scripts/verify-hook-release.py` owns complete warm/cold comparison and strict report validation. `scripts/benchmark-tool-guard-resources.py` owns finite resources and separate native macOS RSS launches.

A content proof recognizes a supported literal operation whose body cannot execute in the current tool action. Strict fallback inspects the whole unsupported source. Admission only permits bounded parsing; it is not permission to execute. Source acceptance exercises generated public processes in disposable homes; it does not install or enable a hook.

## Plan of Work

The following tasks are completed contracts and evidence, not instructions to repeat implementation.

### Milestone 0: Deliver the planning contract

Status: done
Acceptance: met

P0 produced the reviewed plan without implementation. Two Astra reviews resolved transport sizing, hardcoded historical resource expectations, audit-failure proof and pre-proof admission gaps. The user then authorized implementation. Detailed findings and replies are in the historical evidence.

### Milestone 1: Establish reproducible failures and a trustworthy baseline

Status: done
Acceptance: met

T1 had no implementation prerequisite beyond P0 and authorization. It supplied sanitized public-envelope reproducers and froze the original runtime. T2 required T1, then delivered explicit baseline selection, versioned fixtures/contracts, matched mechanics, strict gate/completeness validation and attributable baseline measurements. Original `effd0d7b` is fingerprint-identical to planned `260c578a`. Both tasks and their composed baseline proof are accepted.

### Milestone 2: Resolve budget and writer-recognition feasibility

Status: done
Acceptance: met

T3 required accepted T1/T2. It tested256 KiB,1 MiB and4 MiB candidates and whole supported shell/Python proofs above32 KiB. Independent adversarial review reproduced output-effect/context bypasses before repair and denied paired controls afterward.1 MiB passed unchanged correctness, security, timing and finite-resource checks;4 MiB failed500 ms and was rejected. Admission and post-proof charging remain distinct.

### Milestone 3: Make normal file operations pass while dangerous variants deny

Status: done
Acceptance: met

T4 required T3 and delivered native capacity, independent limits/diagnostics and the integrated v2 harness. T5 required T4 and delivered exact quoted-heredoc writer proof. T6 required T5 and delivered bounded Python AST proof, supported wrappers, all-constant accounting and output-context repairs. T6-R2 trusted summaries repaired reporting cost; accepted commit `65cd978` remains the fixed equivalent-work reference.

Public native/file/shell/limit/corpus/banner suites and independent adversarial checks prove combined native/shell/Python/strict-fallback behavior, including hostile nested/shared stdout and first failing budget attribution. Scope remains narrow; general Python sandboxing and new destination protection are not claimed.

### Milestone 4: Remove justified complexity without losing throughput

Status: done
Acceptance: met

T7 required accepted T4-T6 and made profile, route, findings, completeness, audit override and final enforcement explicit. T8 required T7. Its separately reviewed/measured candidates adopted readable unified rules and ordinary runtime extraction. Direct parsed-pipeline replacement allowed a dangerous nested pipeline and was rejected before timing. Survey-exception removal denied legitimate probes and was rejected. Existing caches and representations remain.

Extraction passed63 cases/189 gates and12 resource cases per condition. Diagnostics was repaired to read moved canonical limits; public mutation checks prove both limit and build updates. Generator, delivery and import-failure checks establish composed behavior.

### Milestone 5: Prove integrated behavior and finish source delivery

Status: done
Acceptance: met

T9 required accepted T7/T8. Integrated correctness, packaging, security/code-quality review and material repairs are complete. Final runtime `aa4a7976` exactly matches its reviewed/measured prototype across76 runtime fingerprints. Full source timing/resource acceptance is met as recorded below. Documentation lint/link/diff verification and the coordinated knowledge pass. The existing hooks-security guidance now points to ordinary canonical policy, distinguishes pre-decode reader bounds and uses trusted summaries while preserving the owner-disabled state. No new memory or index change is warranted. Installation and re-enablement are explicitly excluded.

### Task graph and shared invariants

P0 precedes T1; T2 requires T1; T3 requires T1/T2; T4 requires T3; T5 requires T4; T6 requires T5; T7 requires T4/T5/T6; T8 requires T7; T9 requires T7/T8. Later capacity fixtures use T2's delivered interface rather than creating a dependency cycle.

All accepted tasks preserve whole-input inspection, exact schemas, finite admission and post-proof budgets, executable context, incomplete-inspection denial, bounded safe diagnostics, declared audit outcomes and provider-local delivery. Generator mutations, fixture-mutating tests, reviewer probes and acceptance measurements were serialized where required.

## Concrete Steps

All authorized implementation and source-acceptance work is complete. Final `rtk proxy python3 scripts/lint-okf.py` exits 0, `rtk proxy python3 scripts/generate-hooks.py --check` reports 68 current files, local links resolve, and `rtk git diff --check` passes. All76 current runtime fingerprints still match accepted commit `aa4a7976` and the validation summary. Final documentation is included in the source-delivery record; no benchmark or reviewer remains active. Do not rerun passing suites without changed runtime or an unresolved concern. Do not install or enable anything.

After source delivery, no authorized implementation task remains. Native Windows proof and any installation/re-enablement are separate owner actions. A Windows owner can run `pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1` and `pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` on native Windows; macOS PowerShell tests do not substitute for them.

## Validation and Acceptance

### Integrated source and review proof

All checks below were run against the relevant integrated source or a fingerprint-identical candidate. Passing older source is not claimed as proof of later changes.

- Final reader candidate: live transport17, helpers17, file-operations18, native26, shell18, limits19, incident153, banners16, all three scanner suites, generator28 and freshness68 pass. Independent Astra compares155,955 actual-reader cases against both prior readers with identical outcomes, errors, limit metadata, unread chunks and transport requests. Its transport/time were mocked; live transport17 independently covers pipes/deadlines. All probes stopped before timing.
- Integrated policy: all three Guardian suites, scanner component12, security reporting, diagnostics10 with canonical mutation, recovery17 through disposable Bash/PowerShell installations, Codex configuration merge and disposable Bash installer pass. Recovery retains hostile startup/PATH, denial/audit and registration-tamper coverage without enabling the real hook.
- Maintained release harness34 passes with native RSS collection permitted. Its initial two sandbox kern.clockrate failures were retained environment failures, not weakened tests. Strict completeness, finite numeric values, exact gate types, source/harness hashes and cold-copy requirements received independent review.
- Integrated Astra review found and repaired moved-source diagnostics, then rechecked all 8 limits across 3 providers and canonical mutation. Its72 public probes produced 63 expected denies and 9 intended warning allows. No unresolved actionable P1/P2 remains.

Relevant commands are `python3 scripts/test-hook-input-bounds.py`, `scripts/test_helpers.py`, `scripts/test-tool-guard-file-operations.py`, `scripts/test-tool-guard-native-data.py`, `scripts/test-tool-guard-shell-data.py`, `scripts/test-tool-guard-limits.py`, `scripts/test-tool-guard-false-positives.py`, `scripts/test-security-banners.py`, `scripts/test-generate-hooks.py`, and the three `scripts/test-*-hooks-secrets-scanner.sh` suites through Bash. Use RTK and disposable logs/homes. Exact historical commands and counts remain in the archived plan; no unrun aggregate-suite or native Windows pass is claimed.

### Final performance evidence

All evidence roots below are under `/private/tmp/tool-guard-file-operations-fjhc6r2a`. Raw reports retain individual samples, outputs, audit attribution, fingerprints and failed observations. The tracked validation summary records hashes and acceptance resolution.

| Evidence | Observed result |
| --- | --- |
| `final-r3-t6-equivalent-timing.json` | All279 cases;837 gates;836 pass; one isolated small-edit warm p95 failure. No contract errors; sources unchanged. |
| `final-r3-t6-equivalent-timing-repeat.json` | Exact failed case, full method; all 3 gates pass. Affected p95 delta+5.315ms becomes-1.873ms; median remains improved. |
| `final-r3-original-timing.json` | All279 cases;657 gates and 180 capacity observations;655 gates pass. Two isolated p95 failures. No errors; sources unchanged. |
| `final-r3-original-timing-repeat.json` | Both exact failed cases, full method; all 6 gates pass. Affected p95 deltas+10.664/+11.139ms become-2.836/+1.004ms. |
| `final-r3-resources.json` | All231 cases pass500 ms;25 measured calls/3 warmups plus first call, native RSS and audits. Worst133.413417ms, RSS48,660,480bytes. No errors; sources unchanged. |

The three final timing failures had passing medians and other original phases. Exact repeats clear every affected gate without new failures. Individual tail calls appear in the full reports but do not recur in targeted repeats. This supports the existing isolated-repeat policy; original full reports still have gates_met=false and are never relabeled. Full coverage comes from full runs, not filtered repeats. Repeated failures in prior candidates required actual repairs.

Environment: arm64 macOS 26.7.1, Python 3.14.6 at `/Users/adam/.pyenv/versions/3.14.6/bin/python3`, Clang 21.0.0. Timings cover whole hook subprocesses, not actual provider dispatch. Native macOS time-l collection reports RSS bytes separately from latency. No universal memory, contention-p95 or deployed-platform claim is made.

For a justified future recheck, preserve roots and reports and use a new output filename. Commands, from repository root:

```sh
rtk proxy python3 scripts/verify-hook-release.py --baseline-root /private/tmp/tool-guard-file-operations-fjhc6r2a/t6-r2-candidate --baseline-ref 65cd978 --baseline-condition candidate --comparison-reference equivalent --candidate-root /private/tmp/tool-guard-file-operations-fjhc6r2a/final-r3-candidate --fixture-set file-operations-v2 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --output /private/tmp/tool-guard-file-operations-fjhc6r2a/NEW-equivalent-timing.json
rtk proxy python3 scripts/verify-hook-release.py --baseline-root /private/tmp/tool-guard-file-operations-fjhc6r2a/baseline --baseline-ref effd0d7b --baseline-condition baseline --comparison-reference original --candidate-root /private/tmp/tool-guard-file-operations-fjhc6r2a/final-r3-candidate --fixture-set file-operations-v2 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --output /private/tmp/tool-guard-file-operations-fjhc6r2a/NEW-original-timing.json
rtk proxy python3 scripts/benchmark-tool-guard-resources.py --script-root /private/tmp/tool-guard-file-operations-fjhc6r2a/final-r3-candidate --fixture-set file-operations-v2 --expectations scripts/fixtures/tool_guard_file_operations_expectations.json --condition candidate --samples 25 --warmups 3 --ceiling-ms 500 --output /private/tmp/tool-guard-file-operations-fjhc6r2a/NEW-resources.json
```

### Observable behavior

The sanitized shell/Python document reproducers now allow. Paired executable consumers, unsupported syntax, aggregate content/executable overflows and malformed/incomplete transport deny with safe causes and true units. Native data containing command examples remains data, including source-code files. Missing/corrupt helpers fail closed. Audit failures retain their declared enforcement. These outcomes are covered through generated public JSON entrypoints, never by executing dangerous fixture commands.

## Idempotence and Recovery

Generate owned outputs only with `scripts/generate-hooks.py --write`, then require `--check`; never edit generated files directly. Disposable tests can be repeated for a changed input or unresolved concern. Preserve failed reports and use unused paths; the harness rejects overwriting evidence. Recreate a missing frozen root from its exact Git revision and verify all runtime fingerprints before measuring. Never substitute a moving worktree or a different reference.

If a future source change fails security, correctness or repeated performance gates, keep acceptance unmet and repair or revert the bounded candidate. Do not relax tests, budgets, audit requirements or delta gates. Earlier passes cannot accept changed runtime. Task commits preserve rollback points; avoid destructive Git operations that discard unrelated work.

Retain the disposable evidence until any owner review is complete. If it becomes unavailable, the tracked summary preserves hashes and key acceptance facts; full sample-level reinspection then requires recovery of the reports or a justified fresh run. Installation/re-enablement remains unauthorized until the user explicitly approves it.

## Interfaces and Dependencies

The public seam remains provider JSON on stdin, provider decision JSON on stdout and safe audit records in isolated paths. No new runtime dependency is added. Exact native schemas select profiles; unsupported shapes remain strict. InspectionResult owns profile, route, cause, findings and completeness, followed by one normal-enforcement decision and an explicit audit-failure override.

The shared reader keeps raw-byte, depth, structural-marker and completion bounds. It uses the original outside-string marker expression and batches complete Unicode/escaped-pair runs plus intervening ordinary string spans. Literal-backslash entry preserves plain-data throughput; quotes/backslashes delimit deterministic runs. json.loads remains the syntax authority. The single-quote shell scan uses a bounded C-level find and one span append with unchanged quote failure semantics.

## Historical Records

[ExecPlan.history-2026-10-21.md](ExecPlan.history-2026-10-21.md) preserves the complete prior plan, original requirements, task packets, security findings, all candidate decisions, exact historical commands and unique performance evidence. Its old statuses are historical only. [T3-initial-prototype-history.md](T3-initial-prototype-history.md) retains the earlier budget experiments. Current owner limits and outstanding platform proof remain inline above.
