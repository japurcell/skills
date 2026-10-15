# T3a extraction evidence

This records the private `codex/design-b-t3a` implementation of ExecPlan node T3a on macOS, 2026-10-15. Source and disposable installed-provider evidence do not establish native Windows or authenticated provider delivery. No home installation, enablement, push, standalone CLI, status store, Git gate or lifecycle activation occurred.

## Delivered interface and ownership

`hooks/runtime/scan_engine.py` exposes `scan(work_dir, ScanPolicy, ScanLimits, started=...) -> ScanResult`. Each invocation owns coverage, outcome, findings, counts, elapsed time, safe reason, scope digest and independent audit/status outcomes. No runtime module imports a provider or renderer. `scan_git.py` owns protected Git capture, index OID resolution, borrowed stable snapshots, baseline acquisition and bounded descendant cleanup. `scan_stream.py`, `scan_reporting.py`, `scan_allowlist.py` and `scan_audit.py` are the one maintained normal implementations. Build-time wrappers preserve shared Guardian composition.

Legacy provider adapters retain 256 snapshots, 8 MiB candidate/per-command capture, and 8 seconds. They preserve mode/scope/allowlist/skip inputs, native JSON and exit 0. Normal acquisition additionally accepts explicit aggregate capture and concurrent temporary limits; later T3b must bind B4 configuration to these fields. They remain unbound for compatibility adapters. Audit metadata carries `scanResult`; native stdout receives no new host fields. Required audit failure changes overall outcome to incomplete while retaining independent content coverage and security outcome.

The manifest owns 21 new provider-local helper copies, 59 generated outputs total. Both installer Codex helper lists and exact installed-file checks include the closure. Diagnostics inventory and build identity include all moved inputs. Guardian policy outputs are byte-identical to the base; Guardian entrypoints differ only in `REPORT_BUILD`.

## Public red/green evidence and corrections

- The new coverage test first failed with `KeyError: scanResult`. It now distinguishes 101 findings with complete coverage and 100 retained from the actual 1,000 processed-finding stop, which is incomplete with known findings. Exact retained finding/order assertions remain in the existing cap tests.
- Missing/corrupt runtime-helper process checks exposed Codex emitting the Stop response shape before initializing its tool event. Initializing the already-captured event before the optional-import check repaired native PreToolUse denial. All 84 provider/helper/state/mode combinations, plus exact deny-only diagnostics recovery, passed.
- A Git wrapper rewrote the original candidate immediately before text diff. Before repair it returned complete-clean/allow despite captured credential bytes. Git now compares private copies of the protected snapshot and immutable baseline using `--no-index`; all 3 providers detect the captured token. Existing diff-only suppression remains covered.
- Further public controls substituted the index at worktree EOF and HEAD at index batch-check. Both first returned clean. Baseline OIDs now pin before candidate acquisition, and baseline identity contributes to the scope digest. Both controls pass for all 3 providers.
- Initial per-candidate baseline acquisition hit the unchanged 8 second limit on 250/256-candidate workloads (18 assertions failed in the full merge run, 280.648 seconds). Baseline metadata now resolves in bounded argument batches, and repeated baseline bodies share a protected batch capture. The 250-candidate clean/final-secret controls passed in 21.158 seconds combined; the 256-candidate long-path control passed in 81.923 seconds across its provider/mode/scope calls. Limits and detection assertions were preserved.
- An added drift check initially rejected immutable descriptor snapshots after pathname replacement or completed EOF replay. Checks now run during nonempty reads and preserve completed captured bytes. Six focused replacement/replay process controls pass. The pre-existing failed-diff fixture now stages its synthetic tracked candidate so it still reaches and asserts the intended exit 9 Git diff failure.
- Reporting initially lost the known count 120 of environment paths after the now-honest finding-cap failure. Incomplete records retain omission counts without exposing those path labels. The exact bounded-record test passes.

## Observed checks

All commands run from the private worktree root with `rtk proxy` unless they are Git commands. Intermediate passes are listed honestly; final integrated reruns are recorded below when complete.

| Command | Observed result |
| --- | --- |
| `python3 scripts/test-generate-hooks.py` | 26 passed, 19.048 seconds after final batching |
| `python3 scripts/test-scan-secrets-stream-component.py` | 12 passed, 0.152 seconds |
| `python3 scripts/test-scan-secrets-streaming.py` | 17 passed, 45.135 seconds |
| `python3 scripts/test-security-reporting.py` | 14 passed, 72.786 seconds |
| `python3 scripts/test-hook-diagnostics.py` | 10 passed, 2.448 seconds |
| `python3 scripts/test-hook-diagnostic-recovery.py` | 16 passed, 88.905 seconds after batching |
| `python3 scripts/test-scan-secrets-merge.py` | 33 passed, 238.941 seconds after batching |
| `bash scripts/test-codex-hooks-secrets-scanner.sh` | passed including capture faults before final batching |
| `bash scripts/test-hooks-secrets-scanner.sh` | passed including capture faults before final batching |
| `bash scripts/test-gemini-hooks-secrets-scanner.sh` | passed including capture faults before final batching |
| `python3 scripts/test-install-codex-hooks.py` | passed maintained-hook merge |
| `bash scripts/test-install.sh` | passed disposable installer suite; helper closure unchanged by later matching work |
| `pwsh -NoProfile -File scripts/test-install.ps1` | passed; junction creation unavailable on macOS |
| `python3 scripts/generate-hooks.py --check` | 59 current assets |
| `git diff --check` | passed |

The first full generator invocation encountered sandbox-denied fixture mutations. Scoped worktree escalation permitted the maintained transaction tests. Exact 38-file expectations were updated to 59; all policy/fault assertions were retained and adapted to normal helper contexts.

## Delivery state and limits

The extraction and R1 repair are committed and rebased onto the integrated base. The original reviewed extraction tree `802bfdb` equals amended snapshot `ec40a77`; the private R1 repair snapshot was `d86193e`. After rebasing, extraction is `794c2127` and the frozen engine is `7444fa3d`. R1 conversion/isolation correction and final affected engine checks are complete. The handed-off T1 helper closure and strict coverage contract are complete; its full 25-test acceptance suite passed in 129.195 seconds. The primary owns plan, registry, CI and the coordinated knowledge-maintenance pass.

No production publication/LFS capacity, remote service, Linux, native Windows, real provider trust or host event-delivery claim is made. Worktree collection remains non-atomic across the repository; decisions bind the protected captured inputs. Ambient Git hardening and new worktree/index CLI semantics remain dependent-node work. No experimental D0 implementation was reused.

## R1 declared text-conversion correction

The global `core.autocrlf=true` paired control passed both old and extracted entrypoints. The path-specific `converted.txt text eol=crlf` control with `core.autocrlf=false` passed the old entrypoint and failed the extracted entrypoint by reporting an unchanged historical token. Both paired controls now pass for all providers, including detection of a newly added token on line 2. Worktree attributes/configuration are captured before content acquisition. Explicit text normalization converts only captured CRLF sequences to LF; staged blobs remain literal. Auto conversion delegates binary heuristics to Git on the private inputs and respects whether the pinned index baseline already contains CRLF. Scope identity includes the selected conversion. Raw candidate identity remains unchanged.

This follows the [official text/eol and auto-normalization contract](https://git-scm.com/docs/gitattributes). No whitespace-ignore option is used. Named filters, working-tree encodings and ident conversion are explicit unsupported incomplete cases in this stable-diff path; no new external clean helper is invoked. The legacy candidate enumeration still uses its existing ambient Git behavior. Protecting new standalone CLI acquisition against ambient helpers remains dependent-node work, not a deployment claim here.

R1 focused observed results after correction: global/path-specific CRLF controls: 2 passed in 2.770 seconds; CRLF-indexed baseline control passed in 2.066 seconds; unsupported conversion with known findings passed in 1.865 seconds; existing unchanged-secret suppression passed in 2.810 seconds; 250-candidate controls: 2 passed in 19.938 seconds; scanner generator subset: 9 passed in 4.827 seconds. Full streaming before the final two focused controls passed 19 tests in 48.944 seconds. The normal-source EOF formatting correction now passes `git diff --check`; Guardian policy output remains byte-identical.

The private-name global filter sentinel first executed its helper despite the original-path `-filter` override. The repaired comparison uses one private bare repository per invocation, an explicit empty template, isolated Git configuration/attributes, disabled hooks/fsmonitor, and no inherited `GIT_*` redirection. Only captured original-path conversion and alignment settings enter comparison. Init capture shares the deadline/capture budget; private metadata traversal is capped at 64 entries/depth 4 and charged to temporary accounting. The paired clean/new-secret sentinel now proves no unrelated helper execution while preserving detection. Full streaming after this repair passed 22 tests in 56.509 seconds; Codex capture fault controls passed.

Final R1 engine checks after private comparison isolation: full merge 33 tests passed in 226.066 seconds; full generator 26 tests passed in 18.146 seconds; Codex, Copilot and Gemini protected-capture fault suites passed. Generator fixtures ran serially with all other suites stopped. Guardian policy files still match the pre-extraction source exactly; Guardian entrypoints change only their build fingerprints. Subsequent source changes were confined to the handed-off T1 candidate closure and explicit-result validation.

## T1 verification compatibility

The pre-existing public repaired-representation check first returned `invalid_scanner_result` because the candidate copied only the three old assets. Bundle acquisition now recognizes only the historical scanner/common/audit closure or that closure plus the exact seven declared normal helpers, verifies every helper digest, and includes the complete chosen closure in its bundle identity. Guardian, diagnostic and arbitrary inventory entries do not authorize copied code.

A public 101-finding case first returned incomplete despite complete inspection. Modern audit metadata now requires schema 1, matching build/policy/scope, a SHA-256 scope identity, complete coverage/outcome, finite elapsed time, nonnegative counts, correct retention accounting and written audit. The paired test now returns findings (1) for display-only retention and incomplete (2) for the actual 1,000-finding inspection stop. Ten public metadata fault controls reject missing or inconsistent schema, coverage, build, policy, scope, identity, outcome, counts and audit while retaining known findings and live state.

The immutable historical fixture at `scripts/fixtures/hook-resilience/legacy-active-scanners.zip` contains exactly nine reviewed assets from source revision `6c3c2d8c8033525792fb1c5effd04e3e32cd7682`. Its companion manifest records every byte count and SHA-256 digest. Tests enforce the fixed names, regular-file types, archive/member bounds and digests before explicit extraction; no Git history is needed. The old-active/new-candidate public check passes all six runtime controls with distinct identities. Historical truncation still rejects as incomplete.

The maintained source-filter test exposed named attributes in the raw private reproduction as an unsupported conversion under the new engine. Highest-priority `.git/info/attributes` in verifier-owned copies now disables filter/encoding/ident transforms without changing captured tracked attributes or original HEAD/index/worktree bytes. Its safe and new-secret controls pass without executing the source helper or modifying the live state. This is verification-only raw-byte policy, with no live provider policy or engine change.


Final T1 acceptance: `rtk proxy python3 scripts/test-verify-security-fixture-patch.py` passed all 25 tests in 129.195 seconds. All original cancellation, bounded real Git-session descendant cleanup, source-state/index preservation, raw attributed HEAD/index, audit/native fault and resource-error assertions remain enabled. `python3 scripts/generate-hooks.py --check` reports 59 current assets and `git diff --check` passes. No shared registry, CI, plan, knowledge-base or live installation file was edited by this delegated node. Installer closure checks were already green before matching-only corrections and were not redundantly rerun after unchanged installer assets.
