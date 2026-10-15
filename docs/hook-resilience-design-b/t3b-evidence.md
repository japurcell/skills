# T3b source checkpoint CLI evidence

This is source-process evidence from the private `codex/design-b-t3b` worktree, based on `72193e3b`, on 2026-10-15. The host is macOS 26.7.1 arm64, Python 3.14.6, and Git 2.54.0 (Apple Git-157). Native Windows execution, installed neutral bundles, saved status, Git gates, authenticated provider delivery and real-home deployment remain outside this node. The primary owns plan reconciliation, test-registry integration and the coordinated KB pass.

## Delivered interface

Use either the executable `scripts/scan-secrets.py` or `python3 -I -S -B scripts/scan-secrets.py`. The executable shebang starts Python with isolation, no site initialization and no bytecode writes. A convenience invocation through an already unisolated Python re-executes with these flags, but cannot undo Python startup code that ran before the script. Initial-startup isolation is proved only for the protected invocation.

`check --repo PATH --scope worktree|index` defaults to the current directory and worktree scope. Common `--json`, `--no-input`, `--quiet` and `--no-color` flags work before or after `check`. Checks never read stdin or prompt. No arguments, `-h`, `--help`, `help`, `help check`, `check -h`, `check --help` and `--version` do not resolve Git, load detector policy/budgets, read stdin or write audit/status files. Unknown commands/options, abbreviations and unsupported scopes fail with exit 3 without echoing supplied arguments.

Checks return 0 only for complete-clean, 1 for complete-findings, 2 for incomplete inspection or required infrastructure failure, 3 for invalid invocation/configuration, and 130 for interruption. JSON check mode emits one `scan_secrets_check_v1` object, with CLI version `1.0.0`, engine schema version 1, policy version `pending_snapshots_v1`, trusted build identity, budget identity/effective limits, scope/snapshot identity, coverage, safe counts, bounded redacted findings, audit/status outcomes, phase/reason/diagnostic and concrete recovery. Human result summaries use stdout; human errors use stderr. JSON retains its result under `--quiet`. Closed output pipes produce no traceback and cannot return successful permission.

The bootstrap loads only explicit modules into a package with no search path. Check captures each trusted module's source bytes once, hashes those same bytes, then compiles those bytes. Its closure is the entrypoint, `scan_cli.py`, the seven maintained engine modules, `scan_budget.py` and `scan_repository.py`. Missing/corrupt detector helpers fail check with exit 2 rather than hashing a smaller closure. Help/version continue to work when the parser remains available. No provider or renderer is imported by the standalone runtime.

The CLI calls the same `scan_engine.scan` as compatibility providers. Its optional explicit `ScanContext` carries the protected acquisition state and the inspection budget through discovery and matching. Existing providers retain their seven-helper closure, 256 snapshots, 8 MiB and 8 seconds. This node introduces no matcher or suppression fork and never uses a provider's protocol exit 0 as permission.

## Protected acquisition and scope

Discovery runs bounded, captured, noninteractive Git control queries with ambient Git redirects, config/global attributes, executable helper variables and scanner mode/skip/allowlist settings removed. Only discovery, HEAD verification and configuration queries see the source Git directory. The CLI copies raw index bytes, relevant split-index metadata and a pinned HEAD into private metadata with a minimal config. Object reads borrow the original object store with replacements and lazy fetch disabled and no remotes/filter drivers/hooks/fsmonitor in private config. Worktree-local text/alignment settings are captured after common local settings. No source Git configuration, refs, index or worktree bytes are changed.

Candidate enumeration disables text, filter, encoding and ident conversions at the highest private attribute layer. Mutable source driver names therefore cannot become an execution path during enumeration. Before diff matching, the CLI captures applicable `.gitattributes` ancestors through held no-follow descriptors, plus captured repository attribute declarations, and resolves policy in a private attribute view. Supported explicit text/autocrlf normalization is bound to this captured policy. Custom filter, encoding and ident conversions that require unsupported stable-diff conversion return incomplete rather than executing a helper. Private comparisons remain the engine's protected before/after captures.

Worktree scope retains pending staged/unstaged, required conflict versions and untracked content with ordinary repository ignore semantics. Global user ignore/attribute configuration is not imported. Index scope scans changed selected stage-0 versions in full; unresolved indexes fail with `index_unresolved`. Worktree indexes with assume-unchanged or skip-worktree flags cannot certify coverage and fail with `index_flags_unsupported`. The snapshot digest identifies captured candidate bytes, baselines and conversion decisions. Borrowed object availability and worktree enumeration/reads are not one globally atomic filesystem transaction. Concurrent edits after a captured read are not covered by that earlier read.

All Git captures retain the maintained regular-file capture, output/input ceilings, five-second per-command ceiling and bounded process cleanup. Inspection uses one non-extendable configured deadline beginning before runtime loading. Audit has its independent bounded lock/two-second caller deadline. These bounds describe maintained subprocess/read loops, not a guarantee against an unresponsive operating-system filesystem call.

## Configuration, storage and recovery

Only `--budget-file PATH` selects a resource file. There is no automatic repository budget file, `.env` loading or environment override of security scope, mode, skips, limits or allowlists. Without this option, fixed schema-1 defaults apply. The explicit file is captured once as bounded regular-file bytes, rejects leaf symlinks and changing identity, and is limited to 65,536 bytes. Its exact bytes contribute to `budget_identity`. Explicit owner-selected parent paths are resolved before opening the leaf.

The complete root object has exactly `schema_version: 1`, `checkpoint` and `publication`. Both profiles require all five fields below. Unknown/missing/duplicate fields, booleans, wrong types, nonfinite numbers and values outside the allowed range are invalid configuration, exit 3. Counts/bytes are integers; seconds may be an integer or finite fractional number. No incompatible-schema fallback occurs. Publication is validated now as part of the single file contract but is not executed by this node.

| Field | Checkpoint default; inclusive range | Publication default; inclusive range |
| --- | --- | --- |
| `max_objects` | 4096; 1-16384 snapshots | 20000; 1-100000 objects |
| `max_candidate_bytes` | 67108864; 1048576-536870912 bytes | 268435456; 1048576-1073741824 bytes |
| `max_seconds` | 30; 1-120 seconds | 120; 1-600 seconds |
| `max_capture_bytes` | 134217728; 1048576-1073741824 bytes | 536870912; 1048576-2147483648 bytes |
| `max_temp_bytes` | 268435456; 1048576-2147483648 bytes | 805306368; 1048576-3221225472 bytes |

For this checkpoint, `max_capture_bytes` binds both per-command and aggregate capture ceilings independently, while `max_temp_bytes` measures simultaneously retained private file bytes. Capture includes discovery, copied metadata/attributes and object captures; candidate charging retains normal per-snapshot semantics. A range is admission, not a promise every combination completes. Reports show the effective configured values and actual failing measurement/unit. Fractional timeout proof reports 1.25 seconds, not a truncated legacy 8-second limit. Recovery is to repair the reported resource/storage issue or edit the explicit file within its supported ranges, then rerun the explicit check.

Required audit data goes to `scan-secrets/audit.jsonl` under an absolute `XDG_DATA_HOME` when supplied on Unix/macOS; otherwise macOS uses `~/Library/Application Support`, other Unix uses `~/.local/share`, and Windows uses `LOCALAPPDATA` or `~/AppData/Local`. The application directory must be outside the scanned worktree and scanner bundle. The audit uses the maintained bounded redacted writer: 64 KiB maximum record, 1 MiB rotation size, three backups, private modes and bounded locking. Application-directory/leaf symlinks, unsafe file types and hard-linked audit/lock/rotation files are rejected; opened regular files are checked before chmod or append. An unusable audit prevents complete-clean. Content coverage remains independent of infrastructure outcome, and known findings remain in incomplete results.

This source node writes no historical status. `status_outcome` is `not_attempted`; T4 owns the real status store. All test audit roots, Git fixtures and temporary captures are disposable. No home hook installation, global configuration mutation, gate, watcher, background checkpoint, retry worker or remote operation was introduced.

## Public red/green observations

- The first public complete-clean test failed because `scripts/scan-secrets.py` did not exist. It passed after the isolated entrypoint, lazy parser and same-engine check were implemented.
- Explicit-budget proof first failed because the result lacked effective limits. Strict schema admission and real engine binding then passed. Separate finite snapshot, candidate, aggregate capture, temporary and fractional-time controls fail incomplete with their actual bounds.
- The hostile environment control initially returned incomplete through the supplied `GIT_DIR`. A local filter/fsmonitor control actually created its execution sentinel. Protected metadata and conversion-free enumeration now detect the credential under hostile redirects and return unsupported conversion without executing either helper. Source bytes/index remain unchanged.
- The help closed-pipe control initially emitted an interpreter flush exception. Flushing parser exits within the pipe handler repaired it. The final sweep extended the same control to no-argument help and `help check`; these also reproduced the exception and now flush within the protected route. All help and check pipe routes fail without tracebacks.
- A hard-linked audit control initially returned complete-clean while appending to tracked source and changing its mode. Descriptor validation and rotation preflight now reject links before writes/chmod; public audit/lock controls retain source bytes, source mode and raw index.
- A real temporary-resource cleanup fault after a detected credential initially dropped known findings into generic `internal_error`. The caller now retains the result/counts/findings with incomplete exit 2 and safe `cleanup_failed`; temporary accounting is released in `finally`.
- Linked-worktree `core.autocrlf=true` initially reported a historical unchanged credential after CRLF conversion. Capturing worktree configuration after common configuration restores historical-line suppression and still detects the new credential.

The capacity control scans 300 binary candidates totaling 9,830,400 bytes under defaults, then appends a runtime-constructed 40-byte fake credential to the final candidate and requires a finding. This exceeds both old limits with a meaningful final-path detection control. An explicit 1 MiB candidate limit fails finite incomplete. Independent 1 MiB aggregate-capture and temporary limits also fail incomplete. Display retention of 100 findings remains complete at 101 processed findings; the actual 1000 processed-finding limit is incomplete. These are functional capacity controls, not performance acceptance benchmarks.

Other public controls cover no-argument/help/version outside Git with open stdin and no side effects; argument redaction and abbreviations; clean/findings/incomplete exits; full staged versions versus worktree added lines; unresolved conflict versions; unborn repos; missing helpers; missing/malformed Git; required audit failure; direct isolated startup with decoy `sitecustomize` and helper environment; raw CRLF/index/config preservation; live index substitution after capture; replacement-object resistance; and missing promisor objects with zero remote-helper invocation. Cancellation observes the canonical Git-capture child in its own session/process group and asserts it is dead before fixture fallback cleanup. An inherited sleep child alone is not the cancellation proof.

## Observed validation

All commands run from the assigned private worktree. Prefix commands with `rtk proxy` below. Scoped escalation was required for managed-worktree chmod/generator writes, Git fixture/process observations and later commit metadata. The initial sandboxed generator write failed with EPERM at its lock and completed rollback; the approved run succeeded. No failed test was deleted, skipped or weakened.

| Command | Observed result |
| --- | --- |
| `python3 scripts/test-scan-secrets-cli.py` | 28 passed, 13.918 seconds against final CLI bytes; focused unsafe-root and expanded closed-pipe controls also pass |
| `python3 scripts/test-generate-hooks.py` | 26 passed, 19.818 seconds against final shared runtime/generated closure; later CLI-only help flush does not alter generator inputs |
| `python3 scripts/generate-hooks.py --check` | exact current parity, 59 files |
| `python3 scripts/test-scan-secrets-streaming.py` | 22 passed, 56.803 seconds |
| `python3 scripts/test-security-reporting.py` | 14 passed, 73.125 seconds |
| `python3 scripts/test-scan-secrets-merge.py` | 33 passed, 237.480 seconds |
| `python3 scripts/test-verify-security-fixture-patch.py` | 25 passed, 130.663 seconds |
| `python3 scripts/test-scan-secrets-capture.py codex` | passed, including capture faults and no-HEAD control |
| `python3 scripts/test-scan-secrets-capture.py copilot` | passed, including capture faults and no-HEAD control |
| `python3 scripts/test-scan-secrets-capture.py gemini` | passed, including capture faults and no-HEAD control |

Compatibility suites use isolated fixtures and were allowed to overlap; their durations are functional-suite observations, not benchmark comparisons. Installer, authenticated host and native Windows suites were not rerun because this node does not change their owned closure or installation behavior. No Guardian runtime or performance claim is made. I2 owns registering `scripts/test-scan-secrets-cli.py` in `scripts/test-all.py` during primary integration.

The three capture rows ran the unchanged `scripts/test-scan-secrets-capture.py` from base `72193e3b`, SHA-256 `0061d58147aa93fa74b87587caa1cda34b80bed22e14dea4a611223367a766c9`. They do not contain or establish the new explicit native-execution assertions from the separately integrated T9b commit `f250a87c`; primary owns that integrated evidence.

## Frozen trusted source SHA-256

| Source | SHA-256 |
| --- | --- |
| `scripts/scan-secrets.py` | `3b1483a7880cb65051b608b6f9ba245bb0d59471a4dc1d9b4aa0c5883d077d85` |
| `hooks/runtime/scan_cli.py` | `03f3fd9262b2fa8d8852db3c22fe84035de3d1b0e6658550fabc32b44d83e601` |
| `hooks/runtime/scan_budget.py` | `ebae4c807569d821ed326e412c7117f71004a7fc88ac4023bdf2a492240307b6` |
| `hooks/runtime/scan_repository.py` | `4e3de8bb1edb9f8e73bdd38ea9e6cf37a73835b6c002d1ffa2e715bb12b8983f` |
| `hooks/runtime/scan_types.py` | `4cfaa1d56f83db63147092b4764498ac13ffd701f2e1cf3bc5b0d5af6ede3506` |
| `hooks/runtime/scan_reporting.py` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` |
| `hooks/runtime/scan_allowlist.py` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` |
| `hooks/runtime/scan_stream.py` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` |
| `hooks/runtime/scan_git.py` | `6f83d827ffe75038d060945b0123cb59679d642d37b29623c810537d1a63e78f` |
| `hooks/runtime/scan_engine.py` | `8d46251fee28037cae38d236a97f0a7fe19f7e27a2cf01822eb4c41859ccc0f3` |
| `hooks/runtime/scan_audit.py` | `fbb71a47891862ea8549c7bee0fb0c1075610ea49aa536fc85afe0914ca708d8` |

The raw CLI sources read for B3 were `.agents/sources/clig-dev.md`, `.agents/sources/12-factor-cli-apps.md` and `.agents/sources/cli-design-guidelines.md`. Git's documented [environment controls](https://git-scm.com/docs/git/2.53.0), [attribute precedence](https://git-scm.com/docs/gitattributes) and [fsmonitor configuration](https://git-scm.com/docs/git-config) support the protected-context choices. These sources describe mechanics; the adversarial process controls above establish the observed implementation behavior.
