# Secret-scanner size-limit incident

Archived on 2026-10-15 when the [Design B ExecPlan](../../hook-resilience-design-b/ExecPlan.md) was created. This report retains historical incident evidence; its repair proposals are superseded by that plan.

Date: 2026-10-15. Status: investigation report, not a repair. Audience: the hook's maintainer, including someone unfamiliar with this scanner.

## What happened

After screenshots were added for the software-factory design review, the secret scanner refused a read-only tool call. It also refused session completion repeatedly. The assistant could neither inspect the screenshots nor finish normally. Repeated Stop messages carried the same hook-run ID and failure; they were not independent detections of new secrets.

The user subsequently reported disabling the hook. Ordinary file reads then worked. The assistant did not disable, modify, reinstall, or re-enable it. That workaround restores access but does not repair the scanner or establish a clean scan. Re-enable the protection after a verified repair.

Observed diagnostic:

```text
scan-secrets blocked: session-end scan; scan incomplete; potential secrets could not be checked.
total_bytes_limit/candidate_read: total candidate byte limit exceeded
(measured 9264664 bytes, limit 8388608 bytes).
security_outcome=incomplete; audit_outcome=written; enforcement=deny;
build=471533ef86089e4b; profile=pending_snapshots_v1;
route=pending_scan; cause=total_bytes_limit.
```

The tool-time failure had the same size, limit, build, profile, and route. It blocked `rtk read /Users/adam/.agents/skills/handoff/SKILL.md`, before the command executed. The failure concerned pending repository content, not the size of that skill file.

## Plain-language explanation

The scanner gathers changed and untracked files that might be committed. It has a shared byte allowance for inspecting them. In this incident, that allowance was 8,388,608 bytes, or 8 MiB. Its attempted next acquisition brought the measured amount to 9,264,664 bytes, exceeding the allowance by 876,056 bytes.

This is an **incomplete inspection**, not evidence that a secret was found. Failing closed on an incomplete security scan is intentional. The usability problem is that ordinary image assets exceed the supported workload, and the same unresolved condition blocks both investigation commands and ending the turn.

The measured value is not necessarily the total size of all pending files. The installed source reports the charged bytes plus the next candidate size when acquisition would exceed the limit. It can fail before visiting every candidate.

## Evidence gathered after access was restored

The six supplied PNGs under `prototypes/screenshots/` in the incident repository total **20,026,474 bytes**:

| File | Bytes |
| --- | ---: |
| phase-details.png | 3,611,602 |
| session-details-live-updates.png | 3,131,324 |
| session-details.png | 2,495,842 |
| session-index-live-updates.png | 3,340,075 |
| session-index.png | 3,319,151 |
| tui-workflow-picker.png | 4,128,480 |

These assets alone exceed the installed aggregate allowance. They are intentional design inputs, not unwanted generated output. Their presence is consistent with the failure, but the exact candidate ordering and first offending file were not recovered from an audit log. Do not claim that a particular screenshot caused the reported 9,264,664-byte measurement.

Source inspection found an important version distinction:

- Installed scanner: `/Users/adam/.codex/hooks/scan-secrets.py`. It contains `MAX_TOTAL_BYTES = 8388608`, a `ScanBudget` class, `Snapshot`, and `SnapshotSource.acquire`. Worktree acquisition checks remaining capacity against file size, then charges bytes while capturing the file, before classification. Binary content also has a scanning path; PNGs are not automatically outside the budget.
- This checkout's canonical renderer: [hooks/families/scan_secrets.py](../../../hooks/families/scan_secrets.py). It also sets an 8 MiB aggregate limit, but has `MAX_FILE_BYTES = 1048576` and different implementation structure.
- This checkout's generated Codex entrypoint: [.codex/hooks/scan-secrets.py](../../../.codex/hooks/scan-secrets.py). It likewise has the older per-file limit. The installed scanner's diagnostic policy says that constant is not defined.

Therefore **this checkout does not contain the same scanner implementation as the installed incident version**. Locate the source checkout that produced build `471533ef86089e4b` before patching or installing. Reinstalling this checkout blindly could replace the newer installed implementation with a different one.

## Repair path for the owner

1. **Identify the deployed source.** Locate the generating checkout/build manifest for the installed scanner and confirm the active hook registration in `/Users/adam/.codex/hooks.json`. Preserve unrelated hooks. Record the deployed version before changing anything.
2. **Reproduce in a disposable repository.** Add several benign PNGs whose total exceeds 8 MiB, along with a small changed text file. Exercise the real PreToolUse and Stop provider envelopes. Confirm that an ordinary read command and Stop reach the reported incomplete-scan condition. Use obviously synthetic secrets only for detection fixtures.
3. **Choose an explicit supported workload.** A bounded configurable aggregate limit could accommodate image-heavy documentation, but increasing it also affects scan latency, timeout, disk capture, and resource use. This screenshot set alone needs over 20 MB, before other pending files and any distinct index/worktree snapshots. A small increase just above the first reported 9.3 MB would not be sufficient for this set. Check all relevant budgets together.
4. **Preserve coverage.** Do not fix this by silently skipping PNG extensions, treating truncated content as clean, ignoring the failure, or disabling scanning. Binary files may contain textual credential material or sensitive metadata. If changing binary handling, document its coverage and limits and test the new contract. This scanner is not shown to perform OCR on screenshot pixels.
5. **Make recovery actionable.** Report safe counts, actual limit, phase, and the supported remediation path. Avoid dumping file contents or secrets. If the owner introduces a configurable limit, document its exact setting and accepted range. No supported configuration knob was verified in this investigation; the earlier chat advice to adjust a “configured limit” was too imprecise.
6. **Resolve the repeated Stop behavior deliberately.** Test the same unchanged incomplete result across repeated Stop callbacks. Keep the result explicitly incomplete and retain enforcement for sensitive actions; do not call it clean or add a blanket fail-open. Design a bounded, provider-supported way to ask the human for recovery without an endless series of identical assistant replies. The provider's exact lifecycle contract needs verification before choosing that mechanism.
7. **Regenerate and validate before installation.** This repository generates provider files from `hooks/families/`; edit the owning canonical source, regenerate its adapters, and check generated parity. Use the source checkout matching the deployed version. Then validate installation/trust and exercise the installed hook, not only source tests.

## Acceptance checks

- The supported image-heavy fixture completes a full scan; a deliberately oversized fixture remains an explicit incomplete result.
- A synthetic text credential in the pending text file is still detected, including when large binary assets precede it.
- Supported binary-string detection, staged/worktree/untracked coverage, chunk boundaries, and concurrent-change guarantees are not weakened.
- Limits, deadlines, unreadable files, and corrupt capture remain fail-closed with sanitized messages.
- Ordinary PreToolUse and Stop delivery are exercised end to end, including repeated Stop events and a human recovery route.
- Generated adapters agree with canonical source, installed build identity is verified, and the hook is re-enabled and tested.

Existing test entry points to investigate in the correct source revision include [capture tests](../../../scripts/test-scan-secrets-capture.py), [Codex scanner tests](../../../scripts/test-codex-hooks-secrets-scanner.sh), and [Windows scanner tests](../../../scripts/test-scan-secrets-windows.ps1). This report did not run them, reproduce the incident in a scratch repository, or change any scanner code. No repair or clean scan is claimed.
