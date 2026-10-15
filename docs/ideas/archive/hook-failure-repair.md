# Repair the secret-scanner size-limit deadlock during a merge

Archived on 2026-10-15 when the [Design B ExecPlan](../../hook-resilience-design-b/ExecPlan.md) was created. This report retains historical incident evidence; its repair proposals are superseded by that plan.

## Incident and current status

On 2026-10-15, the Codex secret-scanner hook prevented the agent from finishing a legitimate merge because the pending Git snapshots exceeded its 8 MiB scan budget. The scanner correctly refused to call an incomplete inspection clean. The operational failure was that ordinary investigation commands and session completion were blocked too, leaving the agent unable to resolve the merge through those commands.

The user reported disabling the hook outside the chat and instructed the agent to continue. The merge then completed locally as `c137b5111c8fd7f13d385a779c7bb70e2e906721`. No scanner repair was implemented. This report does not establish that the installed hook has since been re-enabled, or that the incident's pending content received a complete secret scan.

The hook owner should repair the supported workload and recovery experience, then restore and verify enforcement. Changing the conditional skill installer is not the repair target.

## Exact failure

The repeated session-end message was:

```text
scan-secrets blocked: session-end scan; scan incomplete; potential secrets could not be checked. total_bytes_limit/git_index: total candidate byte limit exceeded (measured 8403665 bytes, limit 8388608 bytes). Check pending scan size and unintended generated artifacts. security_outcome=incomplete; audit_outcome=written; enforcement=deny; build=471533ef86089e4b; profile=pending_snapshots_v1; route=pending_scan; cause=total_bytes_limit.
```

Tool calls produced the same diagnostic with `tool scan` instead of `session-end scan`. The observed cumulative reservation was 15,057 bytes above the limit. It is the count at the first failed reservation, not a completed inventory of every candidate.

| Field | Meaning in this incident |
| --- | --- |
| `total_bytes_limit` | Aggregate candidate content exceeded the scanner's byte allowance. |
| `git_index` | The failure occurred while reserving bytes for Git index snapshots. It was not a shell-command length limit. |
| `security_outcome=incomplete` | Inspection did not finish. This neither establishes a secret finding nor certifies clean content. |
| `audit_outcome=written` | The hook reported writing its failure audit record. This does not mean scanning succeeded. The record itself was not independently collected during recovery. |
| `enforcement=deny` | Block mode refused the tool or stop attempt. |
| `build=471533ef86089e4b` | Scanner build identity reported by the installed hook. The merged repository's generated Codex scanner contains the same identity; installed file hashes were not captured. |
| `profile=pending_snapshots_v1; route=pending_scan` | The ordinary pending-content scan ran, rather than the special diagnostics route. |

## What triggered it

The worktree was `/Users/adam/.codex/worktrees/d238/skills`, on `codex/plan-conditional-skill-installer`. The feature tip before merging was `e5c2be2095ba30626559adae7fb2c49ba691734e`. Incoming main was `5f3948c92e5037fb066321e9c9e5b03419410671`.

The agent ran `git merge --no-commit --no-ff origin/main`. Git left four content conflicts:

- `scripts/install.sh`
- `scripts/install.ps1`
- `scripts/test-install.sh`
- `scripts/test_test_all.py`

Main also brought substantial retained hook research, test evidence, compressed archives, generated hooks and source changes. The incoming comparison contained 211 changed files. That Git file count is not the scanner's snapshot count.

After the merge started, the hook denied attempted `git diff --cc`, `git ls-files -u`, ordinary source/instruction reads, and this attempted diagnostic command:

```text
rtk proxy python3 /Users/adam/.codex/hooks/hooks-diagnostics.py --help
```

Those denied commands did not execute. Repeating a final reply triggered the Stop hook again against the same pending state, producing repeated identical blocks without resolving anything. The agent eventually used a chat question to obtain help from the human owner.

Do not infer that a particular archive was unnecessary or caused the entire excess. No complete per-candidate byte inventory was retained before the user disabled the hook. Deleting or unstaging legitimate incoming evidence merely to pass this check would change the merge and conceal the workload problem.

## Source explanation

These facts were checked against the merged repository at `c137b511`:

- [Canonical scanner](../../../hooks/families/scan_secrets.py): `MAX_TOTAL_BYTES = 8388608`, `MAX_GIT_OUTPUT_BYTES = 8388608`, `MAX_FILES = 256`, and `MAX_SCAN_SECONDS = 8.0` are compiled constants. There is no existing environment setting for increasing the aggregate byte budget.
- `ScanBudget.charge()` rejects a reservation when `used_bytes + size` exceeds `MAX_TOTAL_BYTES`. `reserve_index()` labels this failure `git_index` and charges each candidate once within its index reservations.
- `SnapshotSource.__init__()` resolves index object IDs, obtains blob sizes with `git cat-file --batch-check`, and reserves those bytes before classification and matching. Binary content can consume acquisition budget even when it will not be scanned as ordinary UTF-8 text.
- An unresolved path can contribute base, ours, theirs and working-copy versions. Making the visible working file small does not remove the unresolved index versions. Resolving and staging a path changes that state, but the agent needs a working control path to do so.
- Git capture has a separate byte bound. `_next_batch()` already splits index captures into bounded batches. Smaller Git batches alone do not fix an aggregate scan-budget rejection. A single blob larger than the capture limit can encounter a separate limit even after an aggregate-budget change.
- The pending scan depends on repository state, not whether the requested command writes a file. A read-only command can therefore be refused for the same pending-index failure.
- The Codex scanner covers tool calls and Stop. Retrying Stop does not reduce candidate bytes or complete the interrupted scan.

The observed denial is consistent with the implemented resource policy. The evidence does not prove a byte-accounting defect, secret-detection failure, or audit-write failure. The repair must address the supported merge size and recovery path without turning incomplete inspection into permission to proceed silently.

## Recover access and collect evidence

Use an ordinary human Terminal outside Codex when its tool hook prevents investigation. Keep the existing merge intact while collecting evidence. The original merge has already finished; current clean Git status cannot reproduce or certify its earlier pending snapshots.

1. Record the failing message, event, build identity, branch, commit IDs and whether a merge is active. In a future occurrence, use `rtk proxy git status --short --branch` and `rtk proxy git ls-files -u` from the human Terminal. Review paths privately before sharing reports.
2. Use the standalone installed diagnostics CLI from that Terminal. Substitute the trusted absolute interpreter recorded in the installed registration and the actual installed script path:

   ```sh
   /absolute/path/to/trusted/python3 -I -S -B /Users/adam/.codex/hooks/hooks-diagnostics.py --doctor
   /absolute/path/to/trusted/python3 -I -S -B /Users/adam/.codex/hooks/hooks-diagnostics.py
   ```

   These are path templates, not commands to run unchanged. `--doctor` inspects fixed installation assets and registrations. No arguments also collect bounded current-directory metadata. Neither performs a content security scan. File-size metadata does not establish the size of all staged or conflicting versions.
3. Compare the loaded build, observed installed hashes, helper health and registered commands with the trusted repository. Matching build text alone does not prove that installed bytes match. A broken interpreter or common transport helper can require repair from the human Terminal before diagnostics work.
4. Retain a private copy of the existing hook configuration before any owner-directed installation or registration change. In this incident its path was `/Users/adam/.codex/hooks.json`. Preserve unrelated handlers and the owner's trust decisions.

There is also an existing agent diagnostics route. For a native Codex `exec_command` or `functions.exec_command` request, the exact tool arguments are:

```json
{"cmd":"hooks-diagnostics-v1","login":false}
```

Do not prefix that marker with RTK or Python, append arguments, add a working directory, or place it inside a shell script. The scanner matches the native tool envelope, rather than interpreting a command found inside arbitrary wrapper code. A client that exposes only a differently shaped wrapper may not reach this route. See [the exact matcher](../../../hooks/families/scan_secrets.py) in `_diagnostic_request()`.

Expected response: denial containing `scan-secrets diagnostics (request not executed):` and bounded JSON. It intentionally reports security as `not_scanned`; the marker is never executed. Tool Guardian still inspects the request independently. A denial is the expected diagnostics result, not another failed attempt to execute a helper.

The incident attempted the ordinary Python `--help` command, not this exact native marker request. Consequently, it does not establish that the special route was broken. That distinction matters when choosing the repair. [Recovery tests](../../../scripts/test-hook-diagnostic-recovery.py) already cover diagnostics after an overflow and strict rejection of extended marker requests. Source tests do not establish actual desktop dispatch.

## Reproduce before changing code

From the repository root, run these maintained public-entrypoint fixtures:

```sh
rtk proxy python3 scripts/test-scan-secrets-merge.py --provider codex -k conflict_snapshots
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py -k overflow_failure
```

The first command creates disposable unresolved merges. Three conflicts with three 900,000-byte index versions each remain below the aggregate limit; four exceed it. The small working-copy replacements do not remove those index versions. Under current policy both tests should pass: one verifies a complete scan, the other verifies an incomplete result and denial. Passing these tests demonstrates the existing limit, not a repair that accepts the incident workload.

The second command verifies that the exact diagnostics profile remains available after an overflow through source scanner entrypoints. It should pass even though ordinary scanning rejects the oversized state.

For an incident-specific regression, reconstruct the original merge in a separate disposable worktree starting at `e5c2be20`, merging `5f3948c9` with `--no-commit --no-ff`. Keep its conflicting index intact. Run the generated scanner with a native Codex tool envelope and then a Stop envelope, using a disposable home and explicit disposable audit/log paths. Reuse [scanner fixture support](../../../scripts/scanner_test_support.py) and [recovery fixture support](../../../scripts/test-hook-diagnostic-recovery.py), which isolate those paths and remove inherited skip/allowlist settings. Do not run the experiment in the user's active worktree or write fixture audits into the real home.

Record the actual candidate snapshot count, cumulative content sizes, first rejected reservation, decision, audit result and elapsed time. The precise measured count can depend on the reconstructed state; do not manufacture a match to 8,403,665. No frozen incident replay was run while authoring this report.

## Recommended repair work

First decide whether this legitimate merge must fit within the product's supported scan envelope. If it must, implement a bounded increase or a complete-scan design that covers it. For an initial bounded experiment, 16 MiB is a reasonable candidate aggregate budget; it is not an approved requirement, an existing setting, or a validated fix. Measure before choosing the final value. A higher byte allowance may expose the separate snapshot, Git capture, time or memory limits.

Preserve these requirements while evaluating a change:

1. Inspect every required pending version before declaring the scan clean. Do not allow a command because earlier batches passed while later versions remain unchecked.
2. Keep finite byte, snapshot, time, capture, finding and audit-output bounds. Keep incomplete scans denied in block mode and preserve existing secret findings if later work fails.
3. Keep total candidate content accounting separate from Git framing and snapshot replay. Verify that a proposed accounting correction removes only unintended duplicate work, not distinct conflict versions.
4. Keep diagnostics accessible without granting execution authority. Improve the ordinary denial's recovery text to explain the outside-chat Terminal and exact native diagnostics request. Never advertise an ordinary helper invocation as guaranteed to work through a blocked tool gate.
5. Check actual Codex dispatch and Stop retry behavior. If the client cannot deliver the strict diagnostics envelope, retain the human CLI and make that limitation explicit. Preventing repetitive chat retries must not produce a false clean result.

Do not use warn mode, a skip variable, an allowlist, or automatic exclusion of retained evidence as the permanent fix. Do not hand-edit the installed scanner to raise one constant: that creates untracked source/installation drift and leaves generated providers inconsistent.

## Files to change and verification

Edit [hooks/families/scan_secrets.py](../../../hooks/families/scan_secrets.py) for scanner policy and denial/recovery wording. Edit [hooks/families/diagnostics.py](../../../hooks/families/diagnostics.py) only if diagnostic collection needs a change. Generated outputs live in `.codex/hooks/`, `.copilot/hooks/scripts/` and `.gemini/hooks/scripts/`; regenerate them rather than editing them by hand.

Add the incident regression through the generated scanner's public JSON entrypoint. Keep the existing near-limit, over-limit and conflict-version controls. If policy changes a boundary, update the independent expected byte values and preserve an over-new-limit denial case. Pair any accepted larger workload with a fake credential near its end, including a conflict-only version, to prove that acceptance did not truncate inspection.

Run these commands from the repository root after the targeted failing reproduction and repair:

```sh
rtk proxy python3 scripts/generate-hooks.py --write
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-scan-secrets-merge.py
rtk proxy python3 scripts/test-scan-secrets-streaming.py
rtk proxy python3 scripts/test-scan-secrets-capture.py
rtk proxy python3 scripts/test-hook-diagnostics.py
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py
rtk proxy python3 scripts/test-generate-hooks.py
rtk proxy bash scripts/test-install.sh
rtk proxy pwsh -NoProfile -File scripts/test-install.ps1
rtk proxy python3 scripts/generate-hooks.py --check
```

Run generator and installer suites serially. Pause all checkout edits during `test-generate-hooks.py`, which compares whole-checkout snapshots. Follow [security validation guidance](../../../.agents/instructions/testing/hooks-security.md) for resource measurements and native Windows capture coverage; a macOS PowerShell pass is not Windows evidence. If a budget increase exceeds existing resource or deadline acceptance, revise the design rather than weakening the failing checks.

Acceptance requires the incident-equivalent legitimate merge to complete inspection, a late fake secret to remain detected, over-budget and capture failures to remain incomplete/denied, and diagnostics to remain bounded and deny-only. Exercise both PreToolUse and Stop. Read native denial JSON and audit status; a hook process exit code of zero alone is not an allow decision.

## Install, restore enforcement and close the incident

After source checks pass, the human owner should review and install the repaired source. The repository's `scripts/install.sh` or `scripts/install.ps1` refreshes skills, agents, provider hooks and configuration, so review that full scope before applying it to a real account. Installer fixtures are the first deployment check. Both installers pin security registrations to an absolute interpreter with `-I -S -B`; preserve that property and unrelated user handlers. Follow the repository's [Codex trust and deployment rules](../../../.agents/instructions/hooks-codex.md).

Restore the hook using the same owner-controlled configuration or application control that disabled it. The session did not capture which control was used, so this report cannot prescribe an exact toggle or JSON edit. Do not assume reinstalling alone reverses every possible disabling mechanism.

Collect installed diagnostics again, then verify actual tool and Stop delivery with the hook enabled. Use an isolated disposable repository for a legitimate large merge and an unmistakably fake secret control. Confirm that the fake secret is denied, the accepted large workload actually finishes scanning, and repeated completion attempts do not trap the user without usable recovery instructions. Preserve source SHA, installed hashes, build identity, platform, native responses and audit outcomes with the repair evidence.

Until those checks are recorded, the honest status is: original merge completed after a user-reported hook disablement; permanent scanner/recovery repair and restored installed enforcement remain unverified.
