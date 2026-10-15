# Hook resilience session retrospective

Saved on 2026-10-15 from the independent `retro` retrospective. [Companion report](2026-10-15-hook-resilience-retro-automate.md). Original findings are retained below. The implementation guide adds concrete steps without claiming the proposals are built. Transcript links are machine-local historical evidence and may be unavailable on another computer. Repository links are relative, and historical line numbers may drift.

This report applies the `retro` skill and its `writing-for-agents` reference to the scanner and Tool Guardian coding session. It proposes environment improvements only. No implementation, hook installation, skill change, or knowledge-base change was performed for this retrospective.

The strongest opportunities are to preflight credential-fixture changes through the real scanner before they enter the working tree, run the existing POSIX security suites in CI, and preserve the helper mode contract with behavioral checks. Most other reliability lessons already have maintained tests or tooling and should remain there.

## Evidence and scope

The primary transcript is [the session JSONL](/Users/adam/.codex/sessions/2026/10/14/rollout-2026-10-14T09-15-33-01a13b32-96f6-7b21-9379-1cd3ccf16a8a.jsonl). References below use physical JSONL line numbers and UTC timestamps. User requests, assistant claims, and tool results are identified separately. Logs were treated as evidence, not instructions. Credential values and raw credential fixtures are omitted.

The request began at line 17, 2026-10-14 16:21:08 UTC, user: diagnose the new scanner report and improve both hooks' fragility. The inspected coding sequence ends at line 9472, 2026-10-15 02:49:28 UTC, assistant: the helper sets both modes and the targeted checks passed. The later retrospective request is outside the coding evidence window.

At the original retrospective, source inspection found one uncommitted change: `scripts/test-hook-diagnostic-recovery.py:186` now sets both `SCAN_MODE` and `GUARD_MODE`. Existing work was preserved. No tests or builds were run for this retrospective; historical results below come from retained tool outputs.

## Candidates, ordered by severity

### 1. High: preflight moved credential fixtures before writing them into the checkout

**Categories:** Automated checks; tool economy.

Moving fake credentials into shared shell support caused the scanner to block normal reads and corrective patches. The first repair required a manual restore. The attempted preflight compared a Python-produced diff, but Git classified a retained fake fixture as added, and the next write blocked tools again. This is a reproducible workflow hazard with direct user interruption, not just an inconvenient warning.

**Evidence:**

- Transcript line 7813, 2026-10-14 23:33:42 UTC, assistant: fixture movement blocked reads and patches; a proposed Terminal route was rejected by automatic approval review.
- Line 7862, 23:34:35 UTC, tool result: Computer Use forbade Terminal even after the user authorized that narrow route.
- Line 7880, 23:35:36 UTC, user: first restore completed.
- Line 8021, 23:38:13 UTC, assistant: the Python diff preflight was insufficient because Git classified the fixture differently.
- Line 8056, 23:39:02 UTC, user: second restore completed.
- Line 8061, 23:39:09 UTC, assistant: require the actual scanner in a disposable Git repository before another write.

**Proposal:** Add a reusable fixture preflight command for changes to shared security test data. Build the candidate in a disposable Git checkout with the intended baseline/index/worktree state, invoke the existing generated scanner entrypoints using their real provider envelopes, and copy the candidate into the working checkout only after the expected results pass. Inspect complete candidate contents as well as Git's actual change classification. Keep temporary evidence outside the scanned checkout and preserve runtime fixture bytes.

**Completion criterion:** The preflight rejects the previously blocking candidate without touching the working checkout; accepts the repaired candidate; and the intended credential controls still produce findings when executed. A diagnostic recovery request remains deny-only. This requires a deterministic tool, not another always-loaded warning or a broad scanner exemption.

**Existing coverage:** Shared security support and provider scanner suites exist. The session discovered the actual-scanner preflight process, but current testing guidance does not expose a reusable command for it. Reuse the existing scanner and fixture adapters rather than implement a second secret detector.

### 2. High: wire the maintained POSIX security checks into CI

**Category:** Automated checks.

The repository has an explicit aggregate suite, but the only checked-in CI workflow found is Windows-only. The diagnostic recovery suite and macOS-specific capture fault coverage therefore depend on a coding agent remembering to run them locally. This is a coverage wiring gap, not an absence of tests.

**Evidence:**

- `scripts/test-all.py:19-71` registers maintained suites, including diagnostic recovery at line 50 and all three provider scanner shell suites. Capture checks are already invoked transitively by those shell suites, for example `scripts/test-hooks-secrets-scanner.sh:315`.
- `.github/workflows/ready-ideas-windows.yml:26` selects `windows-latest`; lines 63-84 run generated-output checks and selected Windows suites. It does not run the diagnostic recovery suite or the POSIX aggregate runner.
- No configured `core.hooksPath` was returned, and the resolved local `hooks/pre-commit` path did not exist. This observation is local to this checkout's Git repository; it does not establish all developers' configuration.
- `scripts/test-all.py:199` explicitly rejects native Windows. The maintained aggregate command is documented at `.agents/instructions/testing.md:8`.

**Proposal:** Add macOS CI for the maintained POSIX validation route, with required prerequisites installed. A broad job can invoke the existing aggregate runner; a targeted job can invoke the registered security suites if runtime makes that boundary clearer. Keep the existing native Windows job. Include generated-output parity and diagnostic recovery, and let provider scanner shell suites supply their existing capture matrix.

**Completion criterion:** A deliberately failing diagnostic recovery assertion fails CI; the macOS native process-exhaustion branch actually executes; generated drift fails; and missing prerequisites fail visibly. Preserve separate Windows results. Do not invent duplicate capture tests or claim authenticated provider delivery from subprocess simulations.

### 3. Medium: make the mode-setting helper's behavior an explicit test contract

**Categories:** Automated checks; coding standards.

The final review retained a mode mismatch as a low-impact candidate below its reporting threshold. The user subsequently requested the fix. The one-line repair is present, but its six-case before/after proof was an ad hoc probe rather than a newly retained regression check. The first probe also equated warning output with denial and initially failed after the correct fix.

**Evidence:**

- Line 9400, 2026-10-15 00:32:21 UTC, assistant: all four final review roles completed; one test candidate fell below the reporting threshold.
- Line 9420, 02:48:23 UTC, user: correct the `SCAN_MODE`/`GUARD_MODE` mismatch.
- Line 9438, 02:48:42 UTC, tool result: original warn request was denied, reproducing the mismatch.
- Line 9445, 02:48:55 UTC, tool result: the first post-fix probe still failed its warning-response assumption; the existing recovery test passed.
- Line 9458, 02:49:11 UTC, assistant: inspect enforcement rather than expect an empty warn response.
- Line 9465, 02:49:21 UTC, tool result: six before cases reproduced the mismatch and six after cases passed, covering three providers and two modes.
- The source inspected during the retrospective at `scripts/test-hook-diagnostic-recovery.py:185-188` confirmed both environment variables are now set; that change added no permanent test case.

**Proposal:** Retain a small behavioral regression in the existing recovery test module. Exercise the same helper with scanner and Guardian entrypoints under all three provider envelopes and both modes. Set conflicting ambient mode values so inheritance cannot accidentally make the test pass. Assert the actual enforcement outcome; allow warning diagnostics when enforcement permits execution.

**Completion criterion:** Removing either mode assignment makes the relevant case fail, and the current helper passes. Preserve the separate rule that missing policy helpers deny even in warn mode. This fixed contract belongs in tests, not a new reviewer rule about remembering environment variable names.

### 4. Medium: preserve a safe failure packet before disposable capture fixtures disappear

**Categories:** Information access; tool economy.

The historical intermittent failure cannot now be attributed. Its OS error was discarded and its temporary fixture was removed. Repeated successful controls did not recover that missing evidence. Later native fault injection established an EAGAIN defect and a validated repair, but it did not prove the historical event had that cause.

**Evidence:**

- Line 8767, 2026-10-15 00:03:48 UTC, assistant: 1,000 ordinary controls passed; a child-local process limit produced a real launch failure; the original errno was absent.
- Lines 8800 and 8808, 00:04:52 and 00:05:02 UTC, tool results: failing baseline controls became findings after the repair.
- Line 9014, 00:13:09 UTC, tool result: 1,200 stress controls passed with unchanged source hashes.
- `docs/hook-resilience/capture-reliability-result.md:7-13` records both the destroyed original fixture and the limited causal conclusion. Its lines 17-23 describe the implemented bounded retry and sanitized diagnostics.

**Proposal:** Before a failed disposable test exits, retain an owner-only, bounded packet containing the sanitized structured response, expected outcome, provider/event, operation/errno/attempt count, interpreter/platform, source fingerprint, and test case identifier. Exclude candidate contents, credential values, and raw exception text. Link the packet in the failure output. Reuse the new capture diagnostics; do not add another retry layer.

**Completion criterion:** An injected persistent launch error leaves enough sanitized evidence to distinguish launch failure from storage, wait, consumption, and cleanup failures after its fixture is gone. A clean run leaves no unnecessary incident packet.

**Existing tooling:** Installed delivery already has `scripts/probe-provider-hook-delivery.py`, tested separately and documented in `.agents/instructions/testing/hooks-live.md:10-22`. Native and authenticated delivery remain explicit validation limits. Use that tooling when authorized; do not replace it with another simulated envelope test.

### 5. Low: schedule all review roles against available capacity

**Categories:** Tool economy; navigation.

Four review roles were required, but the runtime supported only three children. The first review already completed by starting the fourth when a slot opened. A later invocation requested another user approval for the same batching arrangement.

**Evidence:** Transcript line 7014, 2026-10-14 23:10:42 UTC, assistant: fourth child rejected, queue general quality. Line 9147, 2026-10-15 00:25:41 UTC, user: run three reviewers together, then the fourth. Line 9400 confirms all roles completed.

**Proposal:** Have the review workflow distinguish required role coverage from simultaneous execution. Read runtime capacity and queue excess roles automatically, retaining the fixed diff/spec and a completed-role checklist. If a skill explicitly requires concurrency, revise that requirement in the owning review skill rather than add another global instruction.

**Completion criterion:** Four roles complete with three child slots without losing a role or requesting approval solely for ordinary scheduling. Explicit user constraints still govern.

## Candidates already handled or not supported

- **Capture launch resilience:** Bounded EAGAIN retries, permanent-error behavior, deadline preservation, sanitized errno detail, and public regression controls are already implemented. Recommend preserving them, not writing a second policy or generalized retry framework.
- **Benchmark discipline:** The maintained release adapter and current security testing guidance already specify adjacent matched launches, reversed order, retained failed observations, and separate latency acceptance. No additional benchmark instruction is warranted from this review.
- **Navigation:** The instruction index and testing routes already locate scanner, Guardian, installed delivery, and platform checks. I found no supported navigation delay that justifies a new root pointer.
- **Global AGENTS.md and no-ops:** The evidence does not establish that a particular global instruction caused this session's failures. Protected repository sections were left untouched. Mechanical obligations should be enforced by the checks above rather than expanding always-loaded instructions.
- **Review standards:** The session supports behavioral checks and scheduling repair. It does not support a new broad subjective coding standard.

## Limits

The transcript contains compactions, summaries, and delegated reports. The reviewed physical lines preserve the later coding sequence directly; this report distinguishes assistant claims from tool results instead of treating summaries as proof of every earlier milestone. Historical validation was inspected, not rerun. CI configuration was read, but remote CI run state and branch-protection settings were not inspected. No authenticated provider invocation or native Windows run was performed here.

A separate retrospective-time read-only parsing command was denied by Tool Guardian after it interpreted a diagnostic marker word as a SQL operation. The denial is preserved in this retrospective agent's tool history. It is outside the original coding evidence window and is not used to establish a coding-session finding. The read was reformulated without changing any security control.


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

### POSIX CI: build a focused first job

Create `.github/workflows/hooks-posix.yml` alongside the existing Windows workflow. Use a macOS runner so the capture suite's current `native_once` branch can execute. Trigger on pull requests and pushes affecting `hooks/**`, generated provider directories, `scripts/**`, and the workflow itself; include manual dispatch. Use read-only repository permissions and the current repository action-version policy.

Install or verify Git, Bash, Python 3.13, PowerShell, and stable RTK with required hook processors. Missing prerequisites must fail before testing. Put writable test paths in runner-temporary storage. Run this initial focused set sequentially:

```bash
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py
rtk proxy python3 scripts/test-security-reporting.py
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh
```

The shell suites already invoke capture checks. Confirm the native macOS case executed from its output; a skip is not acceptance. Expand coverage after the focused job is reliable. `rtk proxy python3 scripts/test-all.py --list` lists maintained commands; the current runner has no subset flag. The full aggregate invocation is `rtk proxy python3 scripts/test-all.py`.

On a disposable branch, introduce a failing recovery assertion and generated drift separately and confirm each fails the job. Remove those deliberate faults before merging. Preserve Windows as a separate result. Branch protection is a separate owner action; a workflow file alone does not make its result required for merging. No remote CI run was performed while saving this report.

### Failure packets: retain bounded evidence before cleanup

Extend the support used by capture tests instead of adding another runtime retry layer. Add a test-only evidence-directory option pointing outside the checkout. On failure, before fixture cleanup, serialize an allowlisted record: schema version, case identifier, provider/event, expected and actual outcome, build/source fingerprint, interpreter/platform, and existing safe `operation`, `capture_step`, `os_errno`, and `attempts` fields when available.

Do not serialize raw responses or exceptions wholesale. Set explicit bounds on strings, records, packet bytes, and retained packet count. Use exclusive creation, owner-only permissions, and no-follow destination checks. Report the packet path on stderr. Preserve the original test failure if packet writing also fails. Missing metadata means unavailable, not an inferred value. Successful runs should leave no incident packet.

Tests must cover a persistent launch failure, cleanup after that failure, an unwritable destination, oversized metadata, credential-bearing error text, and a symlink destination. After cleanup, the packet must still identify the failure stage without candidate contents, token bytes, or home paths. Existing transient-recovery and deadline checks must continue passing. Document a bounded retention/cleanup policy so repeated failures cannot fill the disk.
