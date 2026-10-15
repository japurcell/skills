# T3b-R ordinary linked-worktree repair

The bounded repair ran on 2026-10-15 in `/Users/adam/.codex/worktrees/design-b-t3b-repair/skills`, branch `codex/design-b-t3b-repair`, starting from `087676ae63d9d3d8b4fd39a0dceb2251ad67575b`. The host was macOS 26.7.1 arm64, Python 3.14.6 and Git 2.54.0 (Apple Git-157). Source ownership is `hooks/runtime/scan_repository.py`, `scripts/test-scan-secrets-cli.py` and this evidence document. After the observed freshness failure, the primary expanded ownership to regenerate the six affected provider scanner/diagnostic build-metadata assets through the existing generator. The primary owns plan/KB/registry reconciliation; T4 owns status/CLI integration and its composed proof after this repair integrates.

## Public failure and repair

The new `test_ordinary_linked_worktree_checks_without_worktree_config_extension` first reproduced the failure against unchanged implementation bytes. Its disposable repository contains an ordinary commit and a linked worktree without `extensions.worktreeConfig`. The common config sets `core.autocrlf=true`; the linked worktree adds a clean line while retaining a historical runtime-constructed fake credential. The public source CLI should return complete-clean, then detect a newly appended credential. Before repair its first invocation returned exit 2 with `git_failed`, phase `git_command` and child exit status 128. The failing command was the unconditional `git config --worktree --includes --null --list` identified by T4.

Protected configuration capture now runs one bounded `git config --includes --null --show-scope --list`. Git loads enabled worktree settings itself. The helper validates the scope/NUL pairs, rejects missing terminators, incomplete pairs, empty records and unknown scope names, then retains only `local` and `worktree` records in their original precedence. System/global/command records are excluded from selected repository settings. This preserves repository `core.attributesFile` rather than accidentally replacing it with the command-layer `/dev/null` isolation setting.

There is no error fallback or independent extension-boolean parser. An enabled worktree setting is not discarded. Existing configuration, helper isolation, conversion policy, capture/deadline and raw index behavior remain in place. The ordinary-worktree control verifies unchanged common config, linked index and HEAD bytes, plus preserved pending source content. The missing-settings control verifies that an enabled extension with no `config.worktree` still uses common settings without creating a file. A malformed enabled file returns incomplete `git_failed` and preserves its bytes/index/common config. A valid opposite worktree override wins over common normalization; the earlier enabled-override test also remains intact.

The new attributes-file control requires `conversion_unsupported` without executing its configured clean helper. Four public subprocess-boundary capture faults require `git_output_invalid`: missing trailing NUL, unknown scope, a scope without a record, and an empty record. No failing test was deleted, disabled, skipped or weakened.

Git's official [config documentation for 2.54.0](https://git-scm.com/docs/git-config/2.54.0) documents scope labels, NUL-delimited values/newline-separated keys and include handling. A separate disposable real-Git probe confirmed alternating `scope\0key\nvalue\0` framing before implementation. This source check is synchronous and uses the existing maintained engine. No status, installer, gate, background work or live-home changes were made. Provider inspection behavior and helper closure are unchanged; the six generated provider entrypoints carry updated build identities as recorded below.

## Observed commands

All commands below ran from the assigned repair worktree. The standalone CLI remains protected by its existing isolated entrypoint; the test runner also used `-I -S -B`. Scoped escalation was used only for the existing suite's disposable process-state observation.

| Command | Observation |
| --- | --- |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k ordinary_linked` before repair | failed as expected: CLI exit 2, `git_failed`, child exit 128; 0.170 seconds |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k linked_worktree` after repair | 2 passed, 1.622 seconds |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k worktree_config` | 2 passed, 1.421 seconds |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k configuration_capture` | 1 passed with four fault subcases, 0.291 seconds |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py -k attribute_setting` | 1 passed, 0.342 seconds |
| `rtk proxy python3 -I -S -B scripts/test-scan-secrets-cli.py` | 32 passed, 15.709 seconds, including existing hostile environment/local helpers, raw index/config, audit and cancellation controls |
| `rtk proxy python3 scripts/generate-hooks.py --check` before regeneration | exit 1; six scanner/diagnostic outputs require updated build identities |
| `rtk proxy python3 scripts/generate-hooks.py --write` | regenerated exactly six scanner/diagnostic entrypoints |
| `rtk proxy python3 scripts/generate-hooks.py --check` afterward | exit 0, exact current parity for 59 files |
| `rtk proxy python3 scripts/test-generate-hooks.py` | 26 passed, 18.318 seconds |

The read-only freshness check exposed that `hooks/families/reporting.py:19-23` hashes every canonical runtime Python file for scanner build identity, including this CLI-only support file. `hooks/families/scan_secrets.py:446` inserts that identity in generated scanner entrypoints, and diagnostics carries the related build identity. The primary authorized regeneration of exactly the three scanner and three diagnostic entrypoints. An exact before/after comparison, after removing only `DIAG_BUILD` and `REPORT_BUILD` assignment lines, confirmed that all six files are otherwise byte-identical to the base. Canonical generator/manifest, normal provider helper bodies and T4-owned CLI/status files remain untouched. T4 owns any later build-only regeneration after composing its source changes with this repair. No broad provider/installer rerun was requested for this support-only repair. This is macOS source evidence; native Windows, installed neutral bundles and T4 persistence composition remain separate. The primary integrates the clean repair before T4's final linked-worktree status proof.

The regenerated scanner `REPORT_BUILD` is `d8851f60abee1341` for all three providers. Their scanner and diagnostics `DIAG_BUILD` identities are:

| Provider | `DIAG_BUILD` |
| --- | --- |
| Codex | `13428b44f08b68dea88ed9988b162ba9f532af85b0405bb0e39913bbc8666412` |
| Copilot | `d1bbef3d31ad7341baab4edcc58c7ea389ec8267ccd33ab7082104b0d7d1acc2` |
| Gemini | `5b72a15d877c7b952bc566dab5921666c8ec42a4fbd63464787387c7f891a35a` |

## Frozen source SHA-256

| File | SHA-256 |
| --- | --- |
| `hooks/runtime/scan_repository.py` | `bbbeea58f3aaab5bc064030c2c85063774725437d3765e14f83451000e0c10be` |
| `scripts/test-scan-secrets-cli.py` | `de8cb5115a97d724e94618c8c14cdcf3c2dce90b0bcd5e757434c3d76038cc0c` |
| `hooks/runtime/scan_cli.py` (unchanged) | `03f3fd9262b2fa8d8852db3c22fe84035de3d1b0e6658550fabc32b44d83e601` |
| `scripts/scan-secrets.py` (unchanged) | `3b1483a7880cb65051b608b6f9ba245bb0d59471a4dc1d9b4aa0c5883d077d85` |
