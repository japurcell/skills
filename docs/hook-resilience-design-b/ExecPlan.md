# Finish the core Design B hooks

This is the active ExecPlan at `docs/hook-resilience-design-b/ExecPlan.md`. Follow the repository's exec-plans instructions. On 2026-10-16 the user directed us to finish the core design, prefer removing optional complexity, and make routine decisions without asking. This contract supersedes the larger implementation frontier. The preceding plan and its complete task/evidence ledger are preserved in [history](ExecPlan.history-2026-10-16-before-scope-reduction.md); that history does not authorize more work.

## Purpose / Big Picture

An agent must be able to read, repair and finish its turn without a secret scanner starting automatically or asking for another turn. Tool Guardian still checks dangerous tool actions. Secret scanning happens only at an explicitly requested checkpoint or an installed Git commit/push gate. A failed gate blocks that Git operation, not editing or ending the agent turn.

End Turn reads the last saved scan status and its age/scope. It does not scan, wait for a scan, retry, repair state or request continuation. There are no background checkpoints, queues, watchers, workers or daemons. Saved status is historical information, never permission to publish.

Finish the existing implementation. Do not build new Windows repository-installer/ACL backends, native gate support, diagnostic frameworks, benchmark systems, review rounds or automation. Existing Windows provider hooks must pass their existing GitHub Actions tests; native repository gate activation remains explicitly unsupported and must refuse before mutation. The complete checkpoint/commit/push workflow is validated on macOS through the existing POSIX implementation. Other POSIX hosts have no new platform acceptance from this task. Do not silently advertise broader support.

## Core requirements

1. Preserve Guardian tool protection and move secret scanning out of tool and turn-end callbacks. Retire only exactly owned old registrations; preserve unrelated handlers, user disable/trust state, backups and drift checks.
2. Keep the standalone checkpoint/status/gate CLI. `check` and gates return 0 for complete clean, 1 for findings, 2 for incomplete, 3 for invalid invocation and 130 for cancellation. A timeout or failed required audit never counts as clean. Status performs no Git, content scan, network work or repair.
3. Pre-commit inspects changed staged files in full using the selected index. Pre-push independently checks the exact outgoing transaction, reachable history, repeated paths and captured object identity. No checkpoint result authorizes a later commit or push.
4. Preserve LFS ordering and coverage: inspect the actual local payload before an upload-capable hook, deny before upload on findings/incomplete, and preserve exact checked/uploaded bytes. Keep the existing explicit support boundary; do not add native LFS support.
5. Keep ordinary repository installation with cooperating-writer locks, exact ownership, drift refusal, backups and recovery. Do not claim atomic protection against arbitrary simultaneous direct edits. Installing provider hooks must not silently activate repository gates.
6. Deliver retrospective candidates 1-3: verification-only fixture preflight (no apply), macOS security CI, and tests that set both SCAN_MODE and GUARD_MODE. Keep the five accepted adversarial fixes in requirements 1-5 and the CLI exit contract.
7. All CLI help, diagnostics and installation documentation follow the saved [CLI Guidelines](../../.agents/sources/clig-dev.md), [12 Factor CLI Apps](../../.agents/sources/12-factor-cli-apps.md) and [CLI Design Guidelines](../../.agents/sources/cli-design-guidelines.md): predictable subcommands/help, explicit options, stable machine-readable output, useful stderr, correct exits, bounded noninteractive operation and no surprise mutation or PATH changes.

The existing schema-1 resource budgets stay unchanged. Checkpoint defaults are 4096 objects, 64 MiB candidate bytes, 30 seconds, 128 MiB capture and 256 MiB temporary storage. Publication defaults are 20000 objects, 256 MiB candidate bytes, 120 seconds, 512 MiB capture and 768 MiB temporary storage. Preserve current validation/ranges and caller input limits. Status adapter work stays within one second. The fixture verifier keeps its existing finite invocation/child/input/cleanup limits. Do not increase product limits or weaken assertions to hide a failure.

## Progress

- [x] Core source checkpoint/status, selected-index commit gates, outgoing-history/LFS gates and POSIX installation/recovery are implemented with retained source/source-free proof.
- [x] Provider registration migration and installed repair/End Turn workflows pass. All three maintained scanner suites and 12 Darwin cases pass in actual macOS run 38986235261; the 130-input scanner closure is preserved on accepted source.
- [x] Windows main installer passes actual native tests. Existing Windows capture tests exposed real child-containment defects; their bounded repair passed the complete standard native workflow.
- [x] (2026-10-16) [milestone-1] T1: integrated the observer repair and direct 28-test core suite at `1a1c3b8c`. One Python 3.13 run passed in 112.568 seconds; optional diagnostic machinery is removed. All 68 tested input hashes/modes survive integration.
- [x] (2026-10-16) [milestone-1] W2: actual Windows run 38989319821 passed every step, including native containment. Removed 203 optional diagnostic lines while retaining all controls.
- [x] (2026-10-16) [milestone-1] Primary: reviewed and integrated repairs serially through `37aeaa20`, preserving tested inputs and the unresolved historical observation.
- [x] (2026-10-16) [milestone-2] T9c-P: integrated CI coverage, verified prerequisites and the targeted alias-fixture repair at `d61250aa`. Early hosted results and the exact fixture red/green are retained in [evidence](t9c-p-evidence.md).
- [ ] [milestone-2] Primary: Windows run 38992020163 is complete and green. macOS run 38995142743 passed every behavioral/installer suite, then exposed a fragile generator fixture startup allowance. Its scaled timeline preserves cumulative-budget sensitivity; 27 generator and 14 runner tests pass locally. Push the fixture/check-order correction and await complete macOS CI. Product/runtime limits and native Windows inputs are unchanged.
- [x] (2026-10-16) [milestone-3] Primary: aligned README/CLI-help/support guidance, repaired historical links and completed one coordinated knowledge pass. Updated existing security instructions and scanner-consistency memory; no new memory/index/skill/source files. OKF lint, affected links, generated freshness (68 files) and whitespace checks pass.
- [ ] [milestone-3] Primary: retain final integrated CI results and completion status.

## Context and Orientation

Canonical hook code lives under `hooks/`; `scripts/generate-hooks.py` owns generated provider files under `.codex/`, `.copilot/` and `.gemini/`. Never hand-edit generated output. The standalone runtime and Git gates live under `hooks/runtime/`. `scripts/install-scan-secrets.py` installs the standalone CLI; `scripts/install.sh` and `scripts/install.ps1` install provider assets. The existing repository CLI installs POSIX Git dispatchers only when explicitly requested.

Current accepted implementation branch is `codex/hook-resilience-design-b`. The primary owns shared documentation, workflow transport and integration. Existing private owners retain their original responsibility: T1 for fixture preflight, W2 for existing native capture cleanup, and T9c-P for macOS workflow wiring. Do not create more implementation or review tasks. Keep private branches unpushed; primary may push the implementation/CI branch to run Actions. Real-home deployment, trust/enablement changes, PR creation, merge and release are not part of this task.

### Existing evidence and current limits

The retained [POSIX production proof](i3-p-evidence.md), [installed repair/turn-end proof](i4-evidence.md), [provider migration proof](t8b-evidence.md), [registration-test repair](t8b-r-evidence.md), and [native installer proof](w0-evidence.md) establish their documented scopes. Reuse unchanged relevant proof rather than rerunning everything.

A historical fixture-preflight source-filter check returned incomplete in hosted run 38985093967, but its underlying scanner audit was not retained. It cannot be retrospectively diagnosed. Later full suites and one bounded diagnostic observation pass; do not call that historical event fixed or keep adding telemetry/retries to chase it. Keep the original direct source-filter clean/credential-negative test enabled. Any new reproducible failure blocks final completion and receives a bounded repair.

The observer repair has mechanism-specific local and actual hosted proof, including delayed observation, stalled observation and resistant separate-session cleanup. Independent review found no new high-confidence correctness blocker. It can be integrated as that scoped improvement while the historical cause stays unknown.

## Plan of Work

### Milestone 1: Finish the existing repairs
Status: done
Acceptance: met

T1 keeps the small verifier process-observation repair and removes the optional generated audit/inner-Git diagnostic wrappers from its tests. The source-filter case returns to the actual CLI directly. Preserve all original positive, negative, timeout, cancellation, nonmutation and no-filter-execution assertions, including the added ordinary 0.65-second observation case. Remove only the diagnostic feature and its diagnostic-only test; do not add deletion regression tests. Run the resulting core suite once on Python 3.13 and preserve its output and source identity.

W2 finishes the already-written shared Windows child boundary. Actual native tests established an orphaned-grandchild defect, a strict single-link refusal of the two-link OS command interpreter, and a suspended-child survival gap between creation and job assignment. The implementation uses one shared native file layer, a fixed read-only image pin only for the OS-selected command interpreter, and creation-time Job Object membership. Existing single-link data/Git/batch checks remain strict. Do not build another trust layer or broaden this into native repository activation. Remove opt-in tracing and failure-only metadata collectors after the actual native outcome; retain every behavioral/watchdog/audit/redaction assertion and meaningful new containment/sharing control.

Primary reviews each final diff, reuses unchanged proof, checks the exact relevant inputs and integrates clean private branches serially. Archive only clean integrated worktrees, confirm archival, then remove their integrated local branches. Preserve unresolved observations without presenting hypotheses as causes.

### Milestone 2: Run complete CI on the integrated core
Status: in progress
Acceptance: not met

T9c-P's existing workflow adds the already-registered CLI/status/gate/LFS/installation/lifecycle suites, preserves all existing required commands and the 12-case native Darwin validator, provisions actual Python 3.11 plus Python 3.13, and selects hash-verified Git LFS 3.8.0 through an absolute path. Its disposable global Git config is a private writable empty file so checkout cleanup works. All these prerequisites pass locally and on the early hosted run; full headroom and final integrated proof remain to be observed. The early full job exposed a gate-test fixture assumption about its temporary directory; its explicit-alias fixture repair is now integrated, preserving actual gate assertions.

Use `.github/workflows/hooks-posix.yml` and `.github/workflows/ready-ideas-windows.yml` for actual final proof. Remove temporary supplemental diagnostic jobs from the final source. Existing scanner shells already include capture tests, so do not add duplicate aggregate capture runs. Preserve all current tests; fix actual failures without more frameworks. A CI job timeout may be set from observed complete workload needs, but product deadlines and test assertions do not change.

One actual complete final workflow per platform is the main integration check. Run additional targeted local tests only for changed code or a concrete failure. Do not replay the entire hosted command list locally after matching host proof. Record the tested commit, run link, result and material support limits.

### Milestone 3: Document and finish
Status: in progress
Acceptance: not met

Update README and verify existing CLI help to describe the actual installed command, explicit check/gates, historical status, migration/recovery and supported platforms. The default command is under `$HOME/.local/lib/scan-secrets/scan-secrets`; do not imply PATH is modified. Explain how a user explicitly installs/uninstalls repository gates and how failures leave editing available. Document Windows repository-gate refusal plainly without promising unfinished native features.

After all code work finishes, complete one `update-agent-docs` pass using the knowledge-admission rules. Add no memory unless evidence warrants it. Preserve protected AGENTS.md sections and immutable `.agents/sources/`. Repair links affected by the plan reduction, run applicable documentation validation and inspect the final diff. Retain concise outcomes; no new review/audit system.

## Concrete Steps

Work from `/Users/adam/.codex/worktrees/a468/skills`. All code owners have completed and their clean branches are integrated through `37aeaa20`. The single coordinated documentation pass is complete. Source `f1ae45de` is pushed; primary awaits the remaining macOS workflow in Progress; native Windows acceptance is complete. Inspect actual failures and repair only their demonstrated cause. No full local replay or new workstream is needed.

Useful validation commands, selected according to the changed files, are:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-verify-security-fixture-patch.py
    rtk proxy pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1
    rtk proxy git diff --check

Native PowerShell tests must run on actual Windows in GitHub Actions; macOS PowerShell does not establish native proof. The full macOS workflow covers the core checkpoint/status/gates/LFS/installer/lifecycle composition. Existing installed E2E proof already demonstrates guarded merge/binary repair, explicit late-secret rejection, repair/retry, and status-only End Turn callbacks.

## Validation and Acceptance

The final supported POSIX workflow must allow reads and repairs and finish turns with absent/stale/incomplete/corrupt/unavailable saved status. Guardian still denies its established dangerous-operation controls. Explicit checkpoints detect fake credentials. Actual installed commit/push gates deny findings/incomplete; after a repair, retry succeeds. LFS denial happens before upload. CLI results and audits preserve scope and object identity. Existing source-free installed proof and unchanged relevant inputs can be reused.

Actual final macOS CI and existing Windows provider-hook CI must pass on the integrated source. A Windows repository gate must remain a clear unsupported refusal before mutation. Do not count an unsupported path as successful platform delivery. No background checkpoint, automatic scan retry, disabled protection or newly skipped failing test is acceptable.

## Idempotence and Recovery

Use disposable homes/repositories for tests. Keep exactly owned backups and drift refusal in existing installers. Reinstall and uninstall through the existing CLI, never by deleting unrelated hooks. A failed scan is incomplete, not clean. A failed gate blocks only commit/push. Preserve current owner disable/trust state. Do not install into the user's real home or enable hooks automatically.

## Decision Log

- 2026-10-16, user: Finish the core design, prefer removing optional complexity, make routine choices without asking, and add nothing beyond the core. This removes the unfinished native repository-installer/ACL/gate expansion and experimental diagnostic machinery from the active frontier. It does not weaken existing security or test contracts.
- User-confirmed existing choices remain: fixture preflight is verification-only; pre-commit inspects changed staged files in full; D2 protects cooperating writers through locks/ownership/drift/backups, not arbitrary direct edits; no background checkpoints.
- Existing observed repairs are retained where needed for the core: safe process cleanup, explicit UTF-8 generation, read-only OS-image pinning and creation-time job membership. Reuse these implementations instead of designing another abstraction.

## Surprises & Discoveries

Actual Windows tests exposed real process-lifetime and OS-image compatibility defects; source inspection alone had missed them. Those bounded fixes are justified. The expanded platform/backend/diagnostic effort was not needed to finish the selected core and has been removed from the active work.

Integrated recovery exposed a concrete helper-admission gap: `scan_native_process` was declared in the installed closure but loaded lazily only on Windows. Missing/corrupt copies therefore escaped the existing POSIX bootstrap-denial assertion. Actual macOS run 38990328070/job 117271086073 and a targeted local public-entrypoint run reproduced all 12 provider/mode/state failures. One canonical import restores the required-helper contract. The unchanged targeted closure test passes in 9.477 seconds; existing mode and repair/retry tests pass together in 2.775 seconds. No assertion, platform boundary or retry policy changed. The hosted log is `/private/tmp/design-b-final-macos-117271086073.log`, SHA-256 `e11a51b5e45332865d81960ab01c2ebf95ddc9ccc2aca7667d1d6ba8abc3094f`.

The next macOS run 38990998653/job 117273162031 exposed the paired packaging omission: preflight still copied only the reviewed seven/eight-helper closures. Its current scanner correctly denied the missing ninth helper, so 27 assertions and one dependent report access failed. A direct source-filter CLI test reproduced `invalid_scanner_result`. The verifier now explicitly admits and hashes the reviewed nine-helper closure alongside its historical closures, and its existing active-copy fixture includes that helper. All 28 unchanged behavioral tests pass in 112.299 seconds on Python 3.14.6. The hosted log is `/private/tmp/design-b-final-macos-117273162031.log`, SHA-256 `56476da07060c659f0372a7ee504fde2702381d51c2aa99f467ab634036a7fdc`. This is a demonstrated packaging failure, distinct from the older unexplained incomplete result.

Windows run 38991408700/job 117274394515 stopped at `copilot block oversized exceeded outer watchdog`; the underlying blocked frame was not retained, so no runtime cause is claimed. Log: `/private/tmp/design-b-final-windows-117274394515.log`, SHA-256 `6d703ec53c7efd8ac2d58018277b1ba6432f3a2e448a18ca20c4b0325bd2e223`. The oversized fixture previously started legacy Windows PowerShell solely to write 8,388,609 zero bytes, then held output open. Its replacement uses the existing Python interpreter for exactly those bytes and an 11-second hold. The eight-second watchdog, cleanup controls and original assertions remain; a new cause assertion requires `git_output_limit`, preventing a generic timeout from satisfying the oversized case. This is a bounded fixture simplification, not a diagnosed fix for all historical watchdog events. The complete native run 38992020163 passed the simplified fixture and all unchanged controls; no historical watchdog root cause is claimed.

macOS run 38991408659/job 117274394505 completed all 62 gate cases; only the two installed-bundle counts failed (`23 != 22`). The alias case and all runtime gate cases passed. A narrow search found the same obsolete exact count in one installed LFS and one installed preview case. Their original public-process tests reproduce the count failure; changing only those four literals to 23 makes all four cases pass (gate pair 0.851 seconds, actual LFS delivery 1.614 seconds, repository preview 0.529 seconds). No enforcement, identity, delivery or no-mutation assertion changes. Log: `/private/tmp/design-b-final-macos-117274394505.log`, SHA-256 `7b58f561e6716e7ddfe538c78809eaa087252f3c95e6d395592f904c4b2beb5b`.

macOS run 38992431493/job 117277526063 passed preflight (28/186.922 seconds), recovery (17/85.311), reporting (14/107.378), all scanners/native cases, checkpoint/status and all 62 gate cases (56.466). LFS completed 43 tests in 121.161 seconds with one fixture error: its `/var` case allocated beneath the inherited external TMPDIR, then attempted a `/private/var` relative path. The fixture now allocates under the verified alias target (`/private/tmp` or `/private/var/tmp`). A targeted external-TMPDIR red reproduces the exact error; both unchanged alias dispatch/cleanup assertions pass after the one-line repair (2.010 seconds). A bounded search confirms the other system-alias fixtures already allocate explicit physical parents. Log: `/private/tmp/design-b-final-macos-117277526063.log`, SHA-256 `8d84cd8fdaa36848a921a477e9cd2c09e72b7083a68cd30b29ada5bbdd1c27c0`.

macOS run 38993713099/job 117281442992 passed LFS, then 45 of 60 installer cases refused `installation_location_untrusted` during discovery. The same full installer suite passes locally. Product checks remain unchanged; an early read-only CI ancestry check will identify the hosted source/interpreter/temp component before another long test run. This is a temporary scoped prerequisite diagnosis, not another runtime trust backend or relaxed policy. Log: `/private/tmp/design-b-final-macos-117281442992.log`, SHA-256 `1f0b74ac9838d832bddfcdc65c61341824a2b1b7a4c34d9073edf02bd5e31aca`.

The bounded early check in macOS run 38994977378/job 117285434853 identifies exactly four root-owned mode-0775 paths: `/Library/Frameworks/Python.framework/Versions`, its `3.13` directory, `3.13/bin`, and `3.13/bin/python3.13`. CI now removes group/other write from only those four hosted-package locations before installer tests. Product trust checks stay strict. The temporary metadata probe is removed. Probe log: `/private/tmp/design-b-ci-ancestry-117285434853.log`, SHA-256 `21248735c0f4f93dedaebbf1530e16fa12a9946e95fee86fcc6716f9d7c7276c`. No local system interpreter permissions were changed.

macOS run 38995142743/job 117285944887 passed all source, gate, LFS, repository/standalone installation, migration, status cleanup, merger and both complete installers. Generator coverage then hit one fixture timing assumption: a 0.15-second fake command had to start and finish within a 0.25-second shared budget. The first Gemini call correctly timed out, leaving only 100 ms for startup. The fixture now scales both values together to 1.2 and 2.0 seconds: each call fits, their combined work does not. Product limits and the separate output-cap latency assertion are unchanged. All 27 generator tests pass locally (21.428 seconds). An in-memory control that resets the deadline between calls fails both provider assertions, proving cumulative-budget sensitivity remains. All 14 runner tests pass (12.656 seconds). Existing generator/runner commands move earlier in CI; a command multiset comparison proves no command is added, removed or duplicated. Log: `/private/tmp/design-b-final-macos-117285944887.log`, SHA-256 `0b5fb1056df2eede29a7c2f8446c1236c580d6fe63432e56b378cdef05994a5e`.

The historical unexplained preflight incomplete result is retained honestly. Later greens are scoped proof, not a reconstructed cause. The direct existing test remains the check for recurrence.

## Outcomes & Retrospective

The core implementation already exists, including explicit scans/gates, status-only turn end, migration and POSIX installation. Minimal repairs and CI coverage are integrated. Remaining work is final integrated CI, documentation validation and exact results/support limits. No live deployment has happened. This plan is not complete until those remaining acceptance checks are met.
