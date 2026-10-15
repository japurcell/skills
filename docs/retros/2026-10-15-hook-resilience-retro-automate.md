# Hook resilience automation retrospective

Saved on 2026-10-15 from the independent `retro-automate` retrospective. [Companion report](2026-10-15-hook-resilience-retro.md). Original findings are retained below. The implementation guide adds concrete steps without claiming the proposals are built. Transcript links are machine-local historical evidence and may be unavailable on another computer. Repository links are relative, and historical line numbers may drift.

## Session

Security-hook resilience, Copilot capture recovery, review and duplication cleanup, ending with the mode-helper correction. Most avoidable intervention came from scanner-blocked fixture edits and review requirements that did not fit the available agents.

The primary transcript covers 2026-10-14 16:21 UTC through 2026-10-15 02:49 UTC for this scope. It records nine compactions. This report uses original role-tagged messages and tool results where retained, plus current source inspection; inherited summaries are not independent proof. Earlier work represented only in replacement histories is outside the verified scope. No tests or builds were run for this retrospective, and no repository files were changed.

Transcript references below are JSONL line numbers, not inferred turn counts. All timestamps are UTC. The source is [the primary transcript](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl).

## Interventions

| # | Turn | What happened | Type | Root cause |
| --- | --- | --- | --- | --- |
| 1 | User, [T304](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:304), 16:40:05 | Requested a plan and implementation after diagnosis. | Workflow steer | The human selected the next authorized phase. This was an ordinary scope decision; proposal 3 can preserve phase state, but should not assume authorization for later work. |
| 2 | User, [T5206](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:5206), 20:21:18 | Asked what performance was being tuned; the reply explained per-call latency and existing limits. | Context clarification | Not know: the active performance gate and work item were not visible in the update. Proposal 3 can expose the current gate and reason. |
| 3 | User, [T6945](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:6945), 23:09:20; [T6965](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:6965), 23:09:50 | Requested review, then approved an available agent type as a substitute for unavailable `generalist`. | Capability mismatch | Not reach: the workflow named a runtime agent type rather than an executable capability mapping. Addressed by proposal 3. |
| 4 | User, [T7147](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:7147), 23:20:19 | Requested duplication cleanup and explicitly widened the default finding limit. | Workflow steer | The user chose additional scope. Proposal 3 should retain that authorization, not turn every review into automatic cleanup. |
| 5 | User reply, [T7853](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:7853), 23:34:30 | Approved a narrow Terminal fixture repair after scanner blocks prevented ordinary reads and patches. Terminal still proved unavailable. | Plumbing | Not reach: the proposed recovery channel was forbidden by the computer-use runtime. The approval did not create the missing capability. Proposal 1 prevents reaching this state. |
| 6 | User reply, [T7880](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:7880), 23:35:36 | Ran three restore commands so the agent could resume. | Plumbing / rework | Not check: credential-shaped synthetic fixture text reached the guarded worktree before validation. Addressed by proposal 1. |
| 7 | User reply, [T8056](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:8056), 23:39:02 | Repeated the same restore after the next attempt was blocked. | Recurring steer / rework | Not check: preflight examined a Python-computed diff; Git classified retained fixture content differently. The actual scanner and candidate contents were the missing oracle. Addressed by proposal 1. |
| 8 | User, [T8592](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:8592), 23:59:10 | Reopened the unexplained Copilot capture failure and required investigation of intermittent faults. | Blind sensor / correction | Not know: the original capture error discarded its OS operation and errno. Safe capture metadata and bounded launch recovery have since been implemented; preserve those mechanisms. |
| 9 | User, [T9106](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:9106), 00:23:05; [T9147](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:9147), 00:25:41 | Requested final review, then approved three reviewers followed by the fourth. | Capability mismatch | Not reach: four required reviewers were coupled to simultaneous execution despite three child slots. Addressed by proposal 3. |
| 10 | User, [T9410](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:9410), 02:46:07; [T9420](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl:9420), 02:48:23 | Asked whether work remained, then selected the mode-helper correction from optional follow-ups. | Closure check / correction | Not check: recovery assertions matched an error message without proving the helper's requested enforcement mode. Proposal 2 makes that contract executable; proposal 3 keeps remaining work visible. |
| 11 | System records, T252, T1404, T2492, T3329, T5005, T6536, T6928, T8577, T9124 | Nine compactions repeatedly replaced working history. | Context pressure | Not know: detailed evidence was expensive to retain and recover. Proposal 3 persists bounded, attributable phase evidence. Compaction alone does not prove lost work or degraded correctness. |

The hook prompts at T7817, T7827 and T7839 are injected messages with the user role. They are repeated sensor output, not human approvals or three additional human interventions. The approval rejection at T7792 and runtime refusal at T7862 directly support the unavailable recovery path. The agent explicitly identified the inadequate diff preflight at T8021.

Existing mechanisms that paid off: the active scanner caught synthetic credential exposure; approval controls refused a bypass route; the later actual-scanner preflight restored progress; fault injection and native `EAGAIN` reproduction exposed a real launch defect; review filtering prevented a weak candidate becoming a required finding. The source now retains bounded `capture_step`, `os_errno` and attempt metadata, and retries only transient launches within the original deadline in [the scanner family](../../hooks/families/scan_secrets.py). T8853 records transient recovery and retained-deadline checks; T9049 records 1,200 passing controls. These results establish the reproduced defect and its tested recovery, not the historical incident's exact cause.

## Proposals

### 1. Validate security-fixture patches before applying them

**Quadrant:** Computational feedforward and feedback. **Cost:** Temporary Git snapshots and scanner launches for edits to security fixtures only; no cost on ordinary tool calls. Benchmark before choosing a timeout rather than inventing a latency target.

Build a narrowly scoped patch application command that evaluates the exact Git view and complete changed fixture files before they enter the live worktree. Prefer the existing runtime-assembled synthetic credential vectors over new credential-shaped source literals.

**Build:** Add `scripts/apply-verified-security-fixture-patch.py` and focused transaction tests. Accept a patch outside the checkout and an explicit fixture-path list. Preserve the existing index, staged changes and unstaged content in a disposable repository, apply the candidate there, and invoke the reviewed active scanner build and candidate source build with real provider envelopes. Check the actual pending diff and each changed file as a complete candidate. A zero process exit is insufficient: require a complete clean scan and allowed enforcement. On failure, print redacted path/line, scanner build, outcome and cause, then exit without touching the worktree. On success, recheck original file/index hashes before applying; refuse concurrent drift. Verify fixture runtime bytes against existing behavioral vectors rather than altering scanner expectations.

**Wiring:** Route security-fixture changes through this command in the repository's existing hook-testing instructions. Register its transaction tests in `scripts/test-all.py`; add candidate-check cases for a moved retained fixture, a Git/Python diff disagreement, dirty index preservation, and rejected candidates leaving no changes. No bypass flag, scanner exemption, or automatic human-terminal fallback is part of this proposal.

**Evidence:** Interventions 5-7. Existing fragment-built values in [secret scanner vectors](../../scripts/fixtures/secret_scanner_vectors.py) demonstrate a safe representation. The existing generator already has transaction semantics, but [its implementation](../../scripts/generate-hooks.py) owns generated hook outputs, not arbitrary fixture refactors. This proposal fills that narrower missing path.

**Guard against gaming:** Validate with the actual scanner builds and independent expected runtime fixture bytes. Do not declare success merely because source strings were split or the patch command completed.

### 2. Keep the helper's mode contract in the maintained recovery suite

**Quadrant:** Computational feedback. **Cost:** Six short public-entrypoint subprocess cases in the existing recovery suite; no live-hook overhead.

The one-line fix is present, but its successful before/after matrix remains transcript evidence rather than a permanent case exercising this helper's contract. Keep that matrix next to the helper.

**Build:** Add a parameterized case to `scripts/test-hook-diagnostic-recovery.py`. For each provider and requested block/warn mode, deliberately supply conflicting inherited `SCAN_MODE` and `GUARD_MODE`, invoke the existing `launch` helper against the public Guardian entrypoint using an already-established risky-operation fixture, and assert the native decision plus audit `enforcement`. Warn mode must permit with its warning; block mode must deny. Keep the separate missing-policy behavior denied. Reverting the one-line fix must fail this new case.

**Wiring:** The recovery suite is already registered in [the aggregate runner](../../scripts/test-all.py); extend it rather than adding a parallel harness or another registry entry. Reuse the provider envelope adapters and the established enforcement assertions from [security reporting tests](../../scripts/test-security-reporting.py).

**Evidence:** Intervention 10. [The corrected helper](../../scripts/test-hook-diagnostic-recovery.py) now sets both mode variables. The old missing-helper check at line 246 asserts only the error text. Tool output T9445 shows the first new probe falsely equated a nonempty warn response with denial; T9453 shows `enforcement=allow`; T9465 records six before failures and six after passes.

**Guard against gaming:** Assert observable decisions and audit outcomes, not the environment dictionary or response emptiness. Existing reporting tests already cover broad block/warn behavior, so keep the addition limited to this helper and hostile inheritance.

### 3. Schedule required reviews by capacity and retain their evidence

**Quadrant:** Computational feedforward and feedback. **Cost:** One small manifest per review phase and one lightweight validation pass. With three available slots, four independent reviews require two waves; do not hide that extra wall time.

Separate required review coverage from the runtime agent names and number of simultaneous launches. Make the existing approval to use available generic capability and bounded waves durable in the reviewed workflow, then record completion against one fixed target.

**Build:** Add a portable `scripts/plan-review-waves.py` with explicit inputs for required review roles, available agent types, current child capacity, authorized mappings, scope, base/head hashes and spec hash. Emit deterministic waves and a bounded JSON evidence ledger under the review's output directory. Record phase, active gate/reason, authorized follow-up scope, reviewer role, submitted configuration, result path, finding disposition, test evidence and remaining validation categories. Never claim the executed model when the runtime reports only the submitted configuration. Reject missing roles, duplicate coverage, stale target hashes and unauthorized fallback mappings with the exact missing input in the error.

**Wiring:** Invoke it at review intake and validate the ledger before declaring review complete. Use the same ledger as the small resume input after compaction, and render the active phase and unresolved categories into progress/closure updates. Update the review workflow's existing simultaneous-launch requirement only as part of this explicit workflow change. Preserve four independent reviews, existing finding thresholds, and the prohibition on unrequested test execution.

**Evidence:** Interventions 1-4, 9-11. The unavailable role was surfaced at T6958; the concurrency conflict at T9140; T9147 authorized the workable schedule. Final review at T9400 reported all four passes while keeping native Windows and authenticated provider delivery unverified. A machine ledger can retain this distinction without the user having to ask what remains.

**Guard against gaming:** Validate coverage and evidence identity, not a review-quality score or a tally of findings. An empty findings report is a valid result; a missing role is not. A ledger records authorization but never grants it.

## Considered and rejected

- Add another capture retry or generic retry wrapper: the scoped fix already retries transient launch failures and retains deadline/cleanup boundaries. Broad retries could mask persistent failures.
- Add the capture test directly to the aggregate registry: it is already reached through all three provider scanner shell suites, at lines 54, 76 and 315 respectively. A second registration would duplicate runtime.
- Replace the recovery diagnostics route: the exact deny-only route and standalone CLI already exist. [README](../../README.md) explains their limits. They diagnose the block; they do not authorize arbitrary repairs.
- Automatically restore files after any scanner finding: this could discard unrelated user work and conceal a real secret. Prevention with candidate validation is safer than broad rollback privileges.
- Treat a warning body as a failed allow decision: T9453 and existing enforcement tests directly disprove that proxy.
- Add mandatory native Windows or authenticated provider execution to this local retrospective: those are distinct evidence gaps, not demonstrated defects. The checked-in Windows workflow already runs generation and native envelope/capture checks; source tests and that workflow's configuration do not prove a particular remote run succeeded.
- Automatically run cleanup or install live hooks after review: those are separate scope and installation decisions. The transcript establishes specific requests, not a general standing authorization.
- Add a large instruction document: the recurring failures have executable seams. Keep only short routing lines after the mechanisms exist.

## Open questions

- The original intermittent Copilot capture errno is unrecoverable from the retained incident evidence. The reproduced native/transient failure and its fix are verified separately. Future safe metadata can resolve the next incident; no current proposal depends on claiming this historical cause.
- The transcript and checked-in files do not establish authenticated provider dispatch, a successful native Windows CI run for the exact head, or installation of the latest source into live hooks. Keep these evidence categories unresolved until separately validated.

Build proposal 1 first, then proposal 2, then proposal 3; this report proposes them only and implements none.


## Implementation guide for a new contributor

### Status, prerequisites, and repository map

These are proposals, not completed features or authorization to deploy hooks. On 2026-10-15, the helper correction was committed as `f3cbb80a`; capture recovery was already present in `82136483`. Recheck current source before implementation. These revisions identify evidence, not instructions to reset the checkout. This guide supplements the original report and is sufficient to start without access to its machine-local transcript.

Run commands from the repository root. Start with `rtk git status --short` and preserve staged, unstaged, and untracked work. Read [instruction routes](../../.agents/instructions/INDEX.md), [script rules](../../.agents/instructions/scripts.md), and [security testing guidance](../../.agents/instructions/testing/hooks-security.md). Implement one proposal at a time, starting with its failing behavioral check. Follow repository planning requirements before changes spanning multiple scripts or workflow layers.

The canonical runtime lives in `hooks/families/`. Generated adapters live under `.codex/hooks/`, `.copilot/hooks/scripts/`, and `.gemini/hooks/scripts/`. Do not edit generated adapters directly. If runtime source changes, run `rtk proxy python3 scripts/generate-hooks.py --write` and then `rtk proxy python3 scripts/generate-hooks.py --check`. Test tooling and workflow proposals should normally leave runtime code alone.

For a reproducible initial environment, use Python 3.13, Git, Bash, and stable RTK with the repository-required hook processors. Full recovery/installer validation also needs PowerShell (`pwsh`). Verify the repository's current supported versions before implementing; do not silently raise hook interpreter requirements. Keep all homes, logs, and Git fixtures disposable. A skipped platform case is not proof of that platform. Do not install hooks into a real home as a test shortcut.

Existing components to reuse:

- [Scanner fixture support](../../scripts/scanner_test_support.py): disposable repositories, provider envelopes, logs, and outcome assertions.
- [Recovery tests](../../scripts/test-hook-diagnostic-recovery.py): copied adapters, isolated homes, `setup_fixture`, `envelope`, and the corrected `launch` helper.
- [Reporting tests](../../scripts/test-security-reporting.py): provider decisions and audit enforcement assertions.
- [Capture tests](../../scripts/test-scan-secrets-capture.py): injected launch errors and macOS native process-exhaustion checks.
- [Suite registry](../../scripts/test-all.py): maintained commands. Capture tests already run through provider shell suites; do not register them twice.

### Fixture preflight: implementation sequence

Proposed files: `scripts/apply-verified-security-fixture-patch.py` and `scripts/test-apply-verified-security-fixture-patch.py`. They are not available commands yet. Define a CLI accepting `--patch PATH`, repeated `--path RELATIVE_PATH`, an explicit `--active-hook-root PATH`, and mutually exclusive `--check` and `--apply`. Require `--check` to be read-only. Explain the active-root directory layout in `--help` and verify the selected scanner build rather than assuming installed and source builds match.

Initially support only explicitly named regular fixture files. Reject path traversal, absolute target paths, symlinks, special files, unmerged indexes, and unsupported binary/rename patch forms. Each rejection must name the unsupported condition without changing the checkout.

1. Snapshot the baseline, index, worktree, and relevant untracked state needed to reproduce the pending scan. Preserve staged-versus-unstaged differences. A clean clone of HEAD is insufficient. Do not copy or execute live Git hooks/configuration. Stop if the state cannot be reproduced faithfully.
2. Record target file bytes/modes and index fingerprints. Build the exact candidate in a private disposable repository outside the live checkout. Apply the patch there and let Git classify its changes. Do not substitute a Python textual diff.
3. Run both the reviewed active scanner and candidate source adapters with real provider envelopes in block mode. Isolate HOME, logs, temporary paths, and Git configuration. Reject inherited skip/allowlist settings. Exercise the pending-change view and complete changed-file contents using the existing supported scanner scope. Require structured clean status, allowed enforcement, expected build identity, and successful expected audit output. Exit zero alone is insufficient because native denials can also exit zero.
4. Construct synthetic credential controls only inside disposable fixtures using existing vector constructors. Require findings for those controls and verify that source representation changes preserve runtime bytes. Never write assembled credential-shaped strings into the new tooling or report output.
5. Before `--apply`, recheck fingerprints and reject concurrent drift. Preserve the live index. Prepare replacement files and retain their modes. Multi-file replacement is not inherently atomic: keep a bounded recovery journal, and restore only files still matching this transaction's written bytes after a partial failure. Never overwrite concurrent user edits during rollback.
6. Report stage, safe cause, scanner build, and redacted relative paths. Findings, incomplete scans, missing logs, crashes, timeouts, malformed output, and build mismatches must prevent application. Do not print patch contents or raw exceptions.

Acceptance cases: clean patch, moved unsafe fixture, dirty staged/unstaged state, conflicting untracked content, Git/textual-diff disagreement, scanner failure, timeout, concurrent drift, symlink target, and failure halfway through application. Rejected cases must preserve original bytes, modes, and index. Verify cleanup without disabling the live scanner. Register the new suite in `scripts/test-all.py`, run it, and run affected provider scanner suites sequentially. Measure actual preflight cost before selecting a production timeout.

### Mode contract: retain behavioral coverage

Add `test_launch_honors_guard_mode` to `RecoveryTests`. Reuse `setup_fixture`, `envelope`, and `launch`; do not mock the subprocess environment. For each provider and requested block/warn mode, set inherited mode variables to the opposite value. Invoke the copied Guardian entrypoint with an established protected-operation fixture. The hook only inspects the request; the test must never execute the described operation.

Assert native denial in block mode and absence of denial in warn mode. Assert the matching written audit record's mode, rule identifier, and enforcement. A warning can have a nonempty `systemMessage`; response emptiness is not the contract. Put provider-specific audit paths under the temporary fixture root. Preserve separate missing/corrupt policy checks, which must deny in both modes.

After adding the proposed method, run:

```bash
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_guard_mode
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_helper_failures_preserve_report_and_common_needs_human_cli
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py
```

Expected: all affected cases pass. In a disposable source copy, remove only the `GUARD_MODE` assignment and confirm the focused case fails. Do not remove the fix from the live checkout. These six Guardian cases protect `GUARD_MODE`. To claim equivalent protection for `SCAN_MODE`, add a separate scanner control through the same helper and prove that removing that assignment also fails its case. The suite is already registered; no new registry entry is needed.

### Review scheduling: choose the smallest sufficient implementation

The canonical published source is `skills/code-review/SKILL.md`, not the installed user-global copy. Inspect its current requirements and evaluations before changing it. Preserve every required independent review role while permitting capacity-limited waves. Keep one fixed scope, spec, and finding threshold. Unavailable agent types still need an authorized capability mapping; capacity handling does not grant fallback authorization.

Acceptance scenarios: four roles with three slots, four roles with one slot, sufficient capacity, no slot, an unavailable role without a mapping, and a reviewer failure after other roles finish. Missing or failed reviews must remain incomplete. Evaluate coverage and evidence identity, not finding count. Follow the repository skill-authoring workflow for edits and evaluations.

The automation report proposes an additional `scripts/plan-review-waves.py`. Treat that as a larger option, not a prerequisite for the scheduling correction. If built, keep it offline and unable to execute commands or grant permission. Its JSON output should contain required roles, authorized mappings, deterministic waves, fixed target identifiers, result references, and unresolved states. Reject stale identities and duplicate/missing roles. Keep transcripts and credentials out of the ledger. Add `scripts/test-plan-review-waves.py` to the suite registry only if this new tool is implemented.

### Completion and recovery

Record exact revisions, commands, observed outcomes, and limitations. Run `rtk git diff --check`. Run affected suites sequentially when they share generated fixtures or installers. Do not run benchmarks alongside functional tests. New Python suites need registry entries; extensions of existing suites do not.

Rollback only the reviewed changes belonging to the proposal, preserving unrelated work. A blocked preflight or missing prerequisite is a stop condition, not permission to weaken scanners or tests. Complete one end-of-session documentation pass after implementation. Source tests do not prove live installation, authenticated provider delivery, or native Windows success.
