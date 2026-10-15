# T3a extraction evidence

This records the private `codex/design-b-t3a` implementation of ExecPlan node T3a on macOS, 2026-10-15. Source and disposable installed-provider evidence do not establish native Windows or authenticated provider delivery. No home installation, enablement, push, standalone CLI, status store, Git gate or lifecycle activation occurred.

## Delivered interface and ownership

`hooks/runtime/scan_engine.py` exposes `scan(work_dir, ScanPolicy, ScanLimits, started=...) -> ScanResult`. Each invocation owns coverage, outcome, findings, counts, elapsed time, safe reason, scope digest and independent audit/status outcomes. No runtime module imports a provider or renderer. `scan_git.py` owns protected Git capture, index OID resolution, borrowed stable snapshots, baseline acquisition and bounded descendant cleanup. `scan_stream.py`, `scan_reporting.py`, `scan_allowlist.py` and `scan_audit.py` are the one maintained normal implementations. Build-time wrappers preserve shared Guardian composition.

Legacy provider adapters retain256 snapshots,8MiB candidate/per-command capture,8seconds, mode/scope/allowlist/skip inputs, native JSON and exit0. Normal acquisition additionally accepts explicit aggregate capture and concurrent temporary limits; later T3b must bind B4 configuration to these fields. They remain unbound for compatibility adapters. Audit metadata carries `scanResult`; native stdout receives no new host fields. Required audit failure changes overall outcome to incomplete while retaining independent content coverage and security outcome.

The manifest owns21 new provider-local helper copies,59 generated outputs total. Both installer Codex helper lists and exact installed-file checks include the closure. Diagnostics inventory and build identity include all moved inputs. Guardian policy outputs are byte-identical to the base; Guardian entrypoints differ only in `REPORT_BUILD`.

## Public red/green evidence and corrections

- The new coverage test first failed with `KeyError: scanResult`. It now distinguishes101 findings with complete coverage and100 retained from the actual1,000 processed-finding stop, which is incomplete with known findings. Exact retained finding/order assertions remain in the existing cap tests.
- Missing/corrupt runtime-helper process checks exposed Codex emitting the Stop response shape before initializing its tool event. Initializing the already-captured event before the optional-import check repaired native PreToolUse denial. All84 provider/helper/state/mode combinations, plus exact deny-only diagnostics recovery, passed.
- A Git wrapper rewrote the original candidate immediately before text diff. Before repair it returned complete-clean/allow despite captured credential bytes. Git now compares private copies of the protected snapshot and immutable baseline using `--no-index`; all3 providers detect the captured token. Existing diff-only suppression remains covered.
- Further public controls substituted the index at worktree EOF and HEAD at index batch-check. Both first returned clean. Baseline OIDs now pin before candidate acquisition, and baseline identity contributes to the scope digest. Both controls pass for all3 providers.
- Initial per-candidate baseline acquisition hit the unchanged8second limit on250/256-candidate workloads (18 assertions failed in the full merge run,280.648s). Baseline metadata now resolves in bounded argument batches, and repeated baseline bodies share a protected batch capture. The250-candidate clean/final-secret controls passed in21.158s combined; the256-candidate long-path control passed in81.923s across its provider/mode/scope calls. Limits and detection assertions were preserved.
- An added drift check initially rejected immutable descriptor snapshots after pathname replacement or completed EOF replay. Checks now run during nonempty reads and preserve completed captured bytes. Six focused replacement/replay process controls pass. The pre-existing failed-diff fixture now stages its synthetic tracked candidate so it still reaches and asserts the intended exit9 Git diff failure.
- Reporting initially lost the known count120 of environment paths after the now-honest finding-cap failure. Incomplete records retain omission counts without exposing those path labels. The exact bounded-record test passes.

## Observed checks

All commands run from the private worktree root with `rtk proxy` unless they are Git commands. Intermediate passes are listed honestly; final integrated reruns are recorded below when complete.

| Command | Observed result |
| --- | --- |
| `python3 scripts/test-generate-hooks.py` |26 passed,19.048s after final batching |
| `python3 scripts/test-scan-secrets-stream-component.py` |12 passed,0.152s |
| `python3 scripts/test-scan-secrets-streaming.py` |17 passed,45.135s |
| `python3 scripts/test-security-reporting.py` |14 passed,72.786s |
| `python3 scripts/test-hook-diagnostics.py` |10 passed,2.448s |
| `python3 scripts/test-hook-diagnostic-recovery.py` |16 passed,88.905s after batching |
| `python3 scripts/test-scan-secrets-merge.py` |33 passed,238.941s after batching |
| `bash scripts/test-codex-hooks-secrets-scanner.sh` |passed including capture faults before final batching |
| `bash scripts/test-hooks-secrets-scanner.sh` |passed including capture faults before final batching |
| `bash scripts/test-gemini-hooks-secrets-scanner.sh` |passed including capture faults before final batching |
| `python3 scripts/test-install-codex-hooks.py` |passed maintained-hook merge |
| `bash scripts/test-install.sh` |passed disposable installer suite; helper closure unchanged by later matching work |
| `pwsh -NoProfile -File scripts/test-install.ps1` |passed; junction creation unavailable on macOS |
| `python3 scripts/generate-hooks.py --check` |59 current assets |
| `git diff --check` |passed |

The first full generator invocation encountered sandbox-denied fixture mutations. Scoped worktree escalation permitted the maintained transaction tests. Exact38-file expectations were updated to59; all policy/fault assertions were retained and adapted to normal helper contexts.

## Remaining work and limits

Extraction snapshot `ec40a77` is committed (identical tree to reviewed `802bfdb`; commit-message spacing corrected). All listed final batching suites completed. Reviewer R1 confirmed path-specific CRLF suppression differs from old source; conversion correction and final relevant checks precede rebasing onto integrated T1. Then adapt the verification-only fixture utility's candidate dependency closure. Preserve support for its reviewed older active bundles and strict audit behavior. The primary owns plan, registry and the coordinated knowledge-maintenance pass.

No production publication/LFS capacity, remote service, Linux, native Windows, real provider trust or host event-delivery claim is made. Worktree collection remains non-atomic across the repository; decisions bind the protected captured inputs. Ambient Git hardening and new worktree/index CLI semantics remain dependent-node work. No experimental D0 implementation was reused.


## R1 declared text-conversion correction

The global `core.autocrlf=true` paired control passed both old and extracted entrypoints. The path-specific `converted.txt text eol=crlf` control with `core.autocrlf=false` passed the old entrypoint and failed the extracted entrypoint by reporting an unchanged historical token. Both paired controls now pass for all providers, including detection of a newly added token on line2. Worktree attributes/configuration are captured before content acquisition. Explicit text normalization converts only captured CRLF sequences to LF; staged blobs remain literal. Auto conversion delegates binary heuristics to Git on the private inputs and respects whether the pinned index baseline already contains CRLF. Scope identity includes the selected conversion. Raw candidate identity remains unchanged.

This follows the [official text/eol and auto-normalization contract](https://git-scm.com/docs/gitattributes). No whitespace-ignore option is used. Named filters, working-tree encodings and ident conversion are explicit unsupported incomplete cases in this stable-diff path; no new external clean helper is invoked. The legacy candidate enumeration still uses its existing ambient Git behavior. Protecting new standalone CLI acquisition against ambient helpers remains dependent-node work, not a deployment claim here.


R1 focused observed results after correction: global/path-specific CRLF controls2 passed2.770s; CRLF-indexed baseline control passed2.066s; unsupported conversion with known findings passed1.865s; existing unchanged-secret suppression passed2.810s;250-candidate controls2 passed19.938s; scanner generator subset9 passed4.827s. Full streaming before the final two focused controls passed19 tests48.944s. The normal-source EOF formatting correction now passes `git diff --check`; Guardian policy output remains byte-identical.


The private-name global filter sentinel first executed its helper despite the original-path `-filter` override. The repaired comparison uses one private bare repository per invocation, an explicit empty template, isolated Git configuration/attributes, disabled hooks/fsmonitor, and no inherited `GIT_*` redirection. Only captured original-path conversion and alignment settings enter comparison. Init capture shares the deadline/capture budget; private metadata traversal is capped at 64 entries/depth 4 and charged to temporary accounting. The paired clean/new-secret sentinel now proves no unrelated helper execution while preserving detection. Full streaming after this repair passed 22 tests in 56.509 seconds; Codex capture fault controls passed.


Final R1 engine checks after private comparison isolation: full merge 33 tests passed in 226.066 seconds; full generator 26 tests passed in 18.146 seconds; Codex, Copilot and Gemini protected-capture fault suites passed. Generator fixtures ran serially with all other suites stopped. Guardian policy files still match the pre-extraction source exactly; Guardian entrypoints change only their build fingerprints. The next source changes are confined to the handed-off T1 candidate closure and explicit-result validation.
