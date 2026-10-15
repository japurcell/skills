# I1: preparation integration evidence

Observed on 2026-10-15 in `/Users/adam/.codex/worktrees/design-b-i1/skills`, private branch `codex/design-b-i1`, starting at `68a3661c126f8982c615beb9f111c03c7af96bd0`. The integrated base contains the final verification-only T1 repair and T2 mode-helper tests. I1 owns only this evidence, `scripts/test-all.py`, and `scripts/test_test_all.py`; the primary owns plan reconciliation and the coordinated knowledge-maintenance pass.

Platform: macOS 26.7.1, arm64; Python 3.14.6; Git 2.54.0 (Apple Git-157); RTK 0.51.0. Public CLI processes, provider JSON entrypoints, real installers in disposable homes, and disposable Git repositories are the confirmed seams. Process-observing T1 checks ran with scoped permission for numeric `/bin/ps` metadata and disposable fixture operations.

## Registry red and green

The existing `TestTestAll.test_list_covers_maintained_suites_without_running_them` first gained the expected `scripts/test-verify-security-fixture-patch.py` suite. This test invokes the actual runner's `--list` from an unrelated temporary directory with an empty tool PATH. Before the registry edit, the focused command exited 1 and reported that exact path missing from the listed set. After adding the explicit Python command beside the recovery suite, the same focused command exited 0 (one test, 0.032 seconds):

```sh
rtk proxy python3 scripts/test_test_all.py TestTestAll.test_list_covers_maintained_suites_without_running_them
```

`rtk proxy python3 scripts/test-all.py --list` then exited 0 and listed 53 maintained commands. A separate public-process check parsed that listing with `shlex.split` and required the exact command `['python3', 'scripts/test-verify-security-fixture-patch.py']` exactly once. No real aggregate run was invoked. The full runner CLI suite uses disposable executable substitutions and also passed below.

## Integrated verification

All seven requested checks ran serially against the same source tree. The scanner shell suites transitively ran their provider's capture checks; no separate duplicate capture run was added.

| Command from the worktree root | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-verify-security-fixture-patch.py` | Exit 0; all 22 tests pass in 89.872 seconds. This is a complete final-source 22-case run. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | Exit 0; all 15 methods pass in 63.968 seconds, including the 12 scanner/Guardian mode subcases and real disposable installation/launcher cases. |
| `rtk proxy python3 scripts/generate-hooks.py --check` | Exit 0; `Generated hooks are current (38 files).` |
| `rtk proxy python3 scripts/test_test_all.py` | Exit 0; all 14 tests pass in 11.094 seconds. |
| `rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh` | Exit 0; public envelopes and nested capture failures/no-HEAD success report PASS. |
| `rtk proxy bash scripts/test-hooks-secrets-scanner.sh` | Exit 0; Copilot shell assertions and nested capture failures/no-HEAD success pass. |
| `rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh` | Exit 0; Gemini shell assertions and nested capture failures/no-HEAD success pass. |

The Copilot and Gemini shell checks intentionally emit timeout, Git-failure, audit-failure, and invalid-input diagnostics while asserting native block/warn behavior. These are expected fixture outcomes, not failed checks. No test was deleted, skipped, weakened, or repaired during I1. AST parsing of both modified Python files and `rtk git diff --check` also pass.

## Fidelity and ambient configuration

The full T1 run retains `test_repaired_representation_preserves_runtime_and_dirty_state`. It verifies a split fake-credential representation through the actual public preflight, requires six detector controls, then executes only that reviewed representation in a separate disposable Python file and compares its stdout to the exact intended runtime token bytes. Target bytes/mode, raw index bytes and status remain unchanged; staged/worktree differences and unrelated untracked content survive, and hostile copied hooks/filters do not execute.

The same full run includes `test_open_stdin_is_bounded_and_help_does_not_read_it`. Its open-pipe cases require bounded help completion and the incomplete `stdin_timeout` outcome. Its successful EOF-patch invocation inherits `SKIP_SECRETS_SCAN=true`, `SCAN_MODE=warn`, `SECRETS_ALLOWLIST=.*`, `NO_COLOR=1`, and `TERM=dumb`, yet still requires six real credential controls, empty stderr, and unchanged live fingerprints. This existing public composition establishes that preflight does not depend on ambient warning, skip, or allowlist settings. No extra test or runtime change was needed.

T2's mode-helper coverage still supplies the requested mode while both inherited mode variables are opposite, through the real generated provider process. The original assignment-removal mutation controls remain documented in [T2 evidence](t2-evidence.md); I1 reran the complete public recovery suite rather than claiming a new mutation run. The T1 cancellation, consistency, resource, raw-byte and practical-workload history remains in [T1 evidence](t1-evidence.md).

## Frozen identities and D0 prerequisite

The checked source identities were SHA-256:

| File | SHA-256 |
| --- | --- |
| `scripts/verify-security-fixture-patch.py` | `07da7b8a321104f4e2b525bade6e62a21fb5f577074915a798aa418517abbc06` |
| `scripts/test-verify-security-fixture-patch.py` | `06a48f6da41c86948e1b68ee0665f8e8644a47128afb9a3ffa830057381b53e5` |
| `scripts/test-hook-diagnostic-recovery.py` | `5075c47ceb3998cce32322cc36973d085eb52f6f04954427687edf531361409b` |
| `scripts/test-all.py` | `a3986e85fd2f49f65114a9def0ae8939865900b9d69f48bdc3afe7efadcb572f` |
| `scripts/test_test_all.py` | `0fa4213de8a4e3b2ec052baa687850ea71c1cd1bbecaf23be29503f37a0aad6f` |
| `docs/hook-resilience-design-b/publication-contract.md` | `9f62af55735ceccb7a0297a78e647ac3d9986ec008084463b6cf2ae482186592` |

The [D0 publication contract](publication-contract.md) exists and retains its bounded macOS/SHA-1/basic-HTTP laboratory proof and production/platform obligations. I1 did not repeat capacity experiments or implement production gates.

## Review, ownership and limits

The two source-line additions were reviewed for correctness, readability, architecture, security, and performance. They preserve explicit registry ownership and existing public-CLI coverage, add no dependency or discovery behavior, and introduce no blocking finding. The evidence links resolve to retained artifacts.

All requested I1 preparation checks pass. These results establish source behavior and the suites' disposable installation/process evidence on the stated macOS platform. They do not establish authenticated provider-host delivery, native Windows execution, real-home deployment, production Git/LFS gate behavior, or broad performance acceptance. No installed home, trust/enablement setting, provider runtime, generated asset, installer, or user pending work was changed by I1. The primary retains milestone acceptance, plan/KB updates, integration, and worktree archival. This branch remains private and unpushed.
