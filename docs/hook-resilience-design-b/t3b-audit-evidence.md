# T3b-A required-audit ancestor repair evidence

This scoped repair starts at `50c12113563b2c1f519514bdb2bcd73b32339334` in the isolated `codex/design-b-t3b-audit` worktree. It repairs the maintained audit writer used by the source CLI and three provider scanners. The parent owns the ExecPlan, registry and coordinated knowledge-base update. T4 owns status, source CLI loading and final composed source/status proof; none of those files were edited here.

## Reproduction and repair

The primary's first macOS fixture used an unresolved `/var` alias and did not activate its pathname equality injection. That inactive observation was not evidence of safety. This worktree's public regression resolves both fixture and repository roots first, asserts that substitution actually activates, and runs `python3 -I -S -B scripts/scan-secrets.py check --repo ... --json` through a `runpy` filesystem-fault wrapper.

Before the repair, `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k ancestor_swap` failed in 0.227 seconds. At the real `os.mkdir` boundary, the wrapper renamed the external data root and replaced its name with a symlink into the committed worktree. The old audit writer followed that substituted ancestor, appended audit JSON to a tracked mode-644 source file, and returned exit 0 with complete-clean/audit-written semantics. The raw Git index stayed unchanged. The activated reproducer exposed source mutation despite that clean result.

The repaired POSIX writer holds verified directory descriptors from the filesystem root through the audit parent. Directory creation, no-follow leaf acquisition, lock opening, owner/type/link validation, chmod, rotation, unlink and append stay relative to those descriptors. Root-owned aliases under a root-owned parent without group/other write permission accommodate system aliases such as macOS `/var`; user-owned symlink ancestors are rejected. Final directory and opened file ownership checks remain in place, and a regular file must have exactly one link before chmod or writing. All descriptors remain held until lock release and append/flush/fsync finish. No process CWD changes or `/dev/fd` path aliases are used.

The strengthened regression asserts substitution while a verified parent descriptor is held, then requires unchanged tracked source bytes, mode 644 and raw index. Either an anchored audit write or honest required-audit failure satisfies the safety contract. An additional public rotation control swaps the ancestor during the actual relative `os.replace`; it requires successful anchored rotation/append, unchanged three tracked source files and raw index, and the expected rotated records under the held original directory. A public cancellation control holds the real audit lock, asserts a real nonblocking acquisition attempt, sends SIGINT, requires exit 130 with a redacted cancellation result and no log, then proves a subsequent explicit check succeeds.

Audit policy remains caller-owned: default rotation size 1,048,576 bytes, three backups, maximum record 65,536 bytes, lock wait at most one second with 50-millisecond polling and the existing overall deadline. Audit redaction, finding retention, provider mode semantics and required-audit failure handling are preserved. No background work was added.

## Windows primitive and limitations

The initial sharing-only full-path Windows draft was rejected during review: no-delete/no-write sharing alone does not establish that mutable reparse attributes cannot redirect subsequent pathname traversal. The final `scan_native_file.py` contains only dependency-neutral standard-library/native filesystem operations. Audit and status callers retain their own errors, deadlines and ACL policy. It has no scanner, matcher, audit or `scan_types` imports.

Only the drive/share root is acquired through `CreateFileW`. Each descendant is one validated component opened by documented user-mode `NtCreateFile` with `OBJECT_ATTRIBUTES.RootDirectory`, `OBJ_DONT_REPARSE`, `FILE_OPEN_REPARSE_POINT` and an explicit directory/non-directory constraint. Handle metadata rejects reparse objects and multiply linked regular leaves. Rename uses `SetFileInformationByHandle(FileRenameInfo)` with the held destination directory handle; delete uses `FileDispositionInfo` on the opened leaf. Both rename names are validated against separators, alternate streams and special components. Unicode string storage and rename buffers count UTF-16 code units, including non-BMP ancestor names.

The shared API exposes the held `.parent` handle, selective extra access masks, readonly descent that never creates, actual exclusive creation through `FILE_CREATE`, a directory-created result from `IO_STATUS_BLOCK.Information`, CRT file descriptors and optional delete sharing for readonly leaf readers. Audit enables only its pre-existing readonly-attribute normalization through `FileBasicInfo`; the primitive never changes DACLs. Status can request its own READ_CONTROL/WRITE_DAC policy at specific owned boundaries without requesting WRITE_DAC on volume ancestors.

The API basis is Microsoft's [user-mode NtCreateFile contract](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile), [OBJECT_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes), [FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info) and [SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle). These documents support the chosen operations; they do not prove execution on this host.

Native Windows kernel execution is unverified. POSIX fixtures, PowerShell running on macOS and static ABI review do not prove native Windows junction substitution, handle behavior, ACL enforcement or non-BMP execution. Unsupported native operations must produce an honest required-audit failure rather than an unsafe pathname fallback. This change does not claim a global atomic filesystem snapshot or protection from arbitrary privileged kernel/filesystem behavior.

## Helper closure and compatibility

The maintained scanner closure grows from seven helpers to eight by adding `scan_native_file.py`. Canonical manifest/rendering, all three provider helper copies, both installers' exact Codex lists and public recovery inventories are synchronized. The generated scanner bootstrap explicitly requires the neutral helper, preserving fail-closed ordinary scans when it is missing or corrupt while diagnostics recovery remains available. T4 owns adding the new helper to the standalone loader/build closure when composing status; no T4 source was edited here.

Fixture preflight permits only its reviewed two-helper legacy, seven-helper normal and eight-helper native closures. It does not copy arbitrary diagnostic inventory entries. The immutable seven-helper archive contains exactly 30 regular files copied from base `50c12113563b2c1f519514bdb2bcd73b32339334`, with deterministic ZIP ordering/timestamps, fixed allowed names, bounded sizes and SHA-256 values in its manifest. The original two-helper historical archive is unchanged. A public test verifies the real old-seven active bundle independently against the current-eight candidate, including six detection controls, coverage schema 1 and unchanged repository state.

The build route is `hooks/families/reporting.py:build_identity`: scanner identity includes all canonical runtime Python files, `scan_runtime.py`, provider/manifest inputs and trusted launch source. Consequently neutral helper changes affect scanner/diagnostic metadata. The final scanner REPORT_BUILD is `eaa6329716a3a96c`. Scanner DIAG_BUILD values are Codex `77ff65980a41a678e7d5267d914c1d0a3686137228450a8d89a915fea086e57e`, Copilot `581c1b6b407fd08f8763f3605e361b133f32fc423369d3291315079b9d919af3` and Gemini `0d4b8c80226ae15319ded8f2a362373b92c2805c467e25c9e24e962d6886cd41`. The manifest also changes the three generated Guardian REPORT_BUILD constants to `6367ccf607c6810a`; their executable bodies and canonical Guardian policy are unchanged. No Guardian performance change is claimed or required by this metadata-only difference.

## Public red/green and verification

All commands below ran in `/Users/adam/.codex/worktrees/design-b-t3b-audit/skills` on macOS 26.7.1 arm64 with Python 3.14.6. Exact subprocess checks use `rtk proxy`. Real test installers use disposable homes, never the live home. No test was deleted, weakened or disabled to obtain a pass. The three added POSIX race/cancellation cases explicitly retain native Windows as a separate platform obligation.

- Initial activated ancestor reproduction: failed before repair in 0.227 seconds, as described above.
- Focused held-parent ancestor control: passed in 0.239 seconds after repair.
- Focused anchored rotation control: passed in 0.238 seconds.
- Focused real audit-lock cancellation control: passed in 0.460 seconds.
- The public recovery helper list initially failed because the new generated native helper was absent. Canonical eight-helper generation repaired that actual closure failure.
- After eight-helper generation, focused public fixture preflight initially failed with exit 2 / `invalid_scanner_result` because the copied candidate still omitted the required helper. The minimal exact-closure compatibility repair corrected this; the old-seven/current-eight control passed in 7.427 seconds.
- Generator inventory verification initially failed on the three new native targets. Its exact target inventory and expected count were extended to all 62 generated assets; the original equality assertion remains intact.
- A concurrent generator transaction/recovery run failed the repeated Bash installer because the transaction intentionally made `send-event.py` temporarily stale. This was an orchestration failure, not a waived test. Final transaction tests run alone before any installer or source-copying consumer. The temporary transaction file returned byte-identical to its base after the suite.
- An initial command used the nonexistent filename `scripts/test-scan-secrets-security-reporting.py` and exited 2 without executing tests; the maintained suite is `scripts/test-security-reporting.py` and is reported separately below.

| Final command | Outcome |
| --- | --- |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py` | 35 tests passed, 19.348 seconds. Includes normal clean/findings/incomplete behavior, hardlink rejection, activated ancestor/rotation preservation and real audit-lock cancellation. |
| `rtk proxy python3 scripts/generate-hooks.py --write` | Canonical generation succeeded; no outputs were hand-edited. |
| `rtk proxy python3 scripts/generate-hooks.py --check` | All 62 generated assets current, including a final check after the consumer suites. |
| `rtk proxy python3 scripts/test-generate-hooks.py` | 26 tests passed, 18.018 seconds; final transaction run executed alone after whitespace repair. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | 16 tests passed, 79.966 seconds after serialization. Includes real Bash and PowerShell installers in disposable homes, exact byte/executable checks for all eight helpers across all three providers, mode controls, missing/corrupt helper rejection and diagnostics recovery. |
| `rtk proxy python3 scripts/test-verify-security-fixture-patch.py` | 26 tests passed, 139.848 seconds on final stable generated outputs. Legacy-two, historical-seven and current-eight bundles remain independently exercised. |
| `rtk proxy python3 scripts/test-security-reporting.py` | 14 tests passed, 75.789 seconds on final generated outputs; redaction, bounds, known findings and lock contention preserved. |
| `rtk proxy python3 scripts/test-scan-secrets-capture.py codex` | Passed capture failures and no-HEAD success. |
| `rtk proxy python3 scripts/test-scan-secrets-capture.py copilot` | Passed capture failures and no-HEAD success. |
| `rtk proxy python3 scripts/test-scan-secrets-capture.py gemini` | Passed capture failures and no-HEAD success. |
| `rtk proxy git diff --check` | Passed before staging and after the final staged whitespace repair. |

The first staged `git diff --cached --check` caught a new blank line at EOF in the untracked native source and its three generated copies. The commit stopped before writing history. Only that trailing blank line was removed from canonical source, followed by canonical regeneration, refreshed hashes/build identities, another isolated 26-test generator pass and final staged diff-check. The functional suite rows above precede this whitespace-only source adjustment and resulting build metadata changes; executable statements and API semantics are identical. No broad functional rerun is claimed for that adjustment.

Each final capture run emitted four native Darwin observations: real errno 35, clamped hard limit, retained lowered hard limit and restored soft limit for clean/findings in block/warn modes. These observations come from the unchanged capture source hashed below, which includes T9b. They establish this macOS behavior only. The earlier pre-extraction capture and reporting passes are supplementary; final rows above refer to the stable expanded closure.

The maintained full Bash and PowerShell installer suites were not rerun. Their exact closure lists were updated, and the focused recovery suite executes both real installers and checks the same eight-helper bytes and executable properties in disposable homes. Native Windows, authenticated provider delivery, live-home deployment and Guardian benchmarks were not performed. Existing Guardian executable bodies remain byte-identical apart from their build constants.

The final review covers correctness, readability, architecture, security and performance. The activated public regressions establish the repaired POSIX boundary; native ABI/RootDirectory/UTF-16/closure review found no remaining blocker, with native execution explicitly outstanding. The source CLI/status composition remains T4's responsibility. Primary retains the coordinated KB/registry/integration pass; no skill, KB or registry files changed in this node.

## Frozen source identities

| Path | SHA-256 |
| --- | --- |
| `hooks/runtime/scan_audit.py` | `50973ffa051b6750173a0afe22262ffef4f34250a700839e6be5b6b132d9a0e2` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/families/scan_runtime.py` | `7be406dd53c1dd261b4b2a56b84e8e3735ef72f98be5b3800f4cbf26aeae69a3` |
| `hooks/families/scan_secrets.py` | `2166370a9979006fbd5451cee833b633f3f9532dcc4f5a053c6ac2e5fcaa2a12` |
| `hooks/manifest.py` | `3d223eadb301a8d45baf821b8d567c219263f85e501a79217e8e9fe70b618fb6` |
| `scripts/install.sh` | `59dd640e6e8bbbe6c214edb65fef7cfc5080d15890294b4691375bf71f341932` |
| `scripts/install.ps1` | `663b6919ec219d6190732ac74918c27959b68d4e2102927c79ec6ead72bb59fb` |
| `scripts/test-scan-secrets-cli.py` | `6a685e4dbc0a48fa43cf705c6325da028cf52b7a1ad0c39067e8f6470f6321e4` |
| `scripts/test-hook-diagnostic-recovery.py` | `bc5412fbd682ddb9aee05de20058b2988b99f4d12875d043cb2128874202a756` |
| `scripts/test-generate-hooks.py` | `10fbbf93abce9b4ade825fcf782016c633bbb0c166d9760485774ac58d665530` |
| `scripts/verify-security-fixture-patch.py` | `68bf29cdb965bd7b0295007e252434d29ec6a08620e966eed30c680314376053` |
| `scripts/test-verify-security-fixture-patch.py` | `e5c32ed114ec5b6988e3d5c8c1cd64fa9f6b968ba6b2f720fa921d44decdb62a` |
| `scripts/test-scan-secrets-capture.py` | `fdf9314ea62508d405871a2870dda8c7da46b2ecca435378e11aaf2a7026d7d3` |
| `scripts/test-security-reporting.py` | `ac7e7eb3034e669116b03edc0fa1880ea00dd54089ee16d7a7211c014fd88f22` |
| `scripts/fixtures/hook-resilience/seven-helper-active-scanners.zip` | `638820d6385a060618f1bd07ec2f9a44738d7d68bcba366c19ba7038f1838d7c` |
| `scripts/fixtures/hook-resilience/seven-helper-active-scanners.json` | `543c3bf5fc92783165d0b8cdd8e8fba233110894510442bad585a37030ab1638` |
| `scripts/test-install.sh` | `0e6fdfa7653680192dfd9b23ae3bce4e795001fbc7d555e37eb35f9429bb4b08` |
| `scripts/test-install.ps1` | `c46dd6b1247a2458072ab5483080c05012a8102cca5c3b2a134fb4e9bd1cbcf0` |

## Generated helper identities

All three generated `helpers/scan_audit.py` copies have the same hash, and all three generated `helpers/scan_native_file.py` copies have the same hash. Canonical freshness checks establish all 62 outputs against their renderers, not only these two assets.

| Generated relative path | SHA-256 |
| --- | --- |
| `.codex/hooks/helpers/scan_audit.py` | `ad2d7e4bc045940bf521267a21ec36c5e01eb2d1d5ee1a25ff539f200d359e0f` |
| `.codex/hooks/helpers/scan_native_file.py` | `52dd7df2f11c151b65a22f2a52cb5f248f38eae552523cbbc01c4b8defd8d0e3` |
| `.copilot/hooks/scripts/helpers/scan_audit.py` | `ad2d7e4bc045940bf521267a21ec36c5e01eb2d1d5ee1a25ff539f200d359e0f` |
| `.copilot/hooks/scripts/helpers/scan_native_file.py` | `52dd7df2f11c151b65a22f2a52cb5f248f38eae552523cbbc01c4b8defd8d0e3` |
| `.gemini/hooks/scripts/helpers/scan_audit.py` | `ad2d7e4bc045940bf521267a21ec36c5e01eb2d1d5ee1a25ff539f200d359e0f` |
| `.gemini/hooks/scripts/helpers/scan_native_file.py` | `52dd7df2f11c151b65a22f2a52cb5f248f38eae552523cbbc01c4b8defd8d0e3` |
