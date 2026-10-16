# T5a staged gate evidence

Observed on 2026-10-15 in the private managed worktree on `codex/design-b-t5a`, based on `a7c6b814`. Platform: macOS 26.7.1 arm64, Python 3.14.6, Apple Git 2.54.0, RTK 0.51.0. All fixture repositories, homes, data roots, temporary dispatchers and installed bundles were disposable. No real-home installation, trust/enablement change, external push, background scan or production repository dispatcher was performed.

## Delivered behavior

`python3 -I -S -B scripts/scan-secrets.py gate pre-commit --repo PATH --json` inspects every stage-zero path in the captured selected index tree, including unchanged HEAD paths. Every selected blob is inspected in full with the canonical matcher; no pending-diff suppression or ambient allowlist/skip/warn setting grants permission. Worktree bytes are outside this staged feedback. Check defaults and existing pending index-check semantics remain unchanged.

The gate explicitly captures `GIT_INDEX_FILE` when present, interpreting a relative path from the invocation directory as Git does. Other inherited Git redirects are excluded. Default, alternate and split-index metadata reads use held-directory operations; the Windows composition uses the existing `WindowsDirectoryHandles` API. Only verified root-owned macOS `/tmp` and `/var` aliases are normalized. Arbitrary linked ancestors, missing explicit indexes, special files and unresolved indexes deny. An absent default index in an unborn repository is an honest empty staged state. Selected Git blobs are checked against format-specific Git object hashes before their captured bytes become coverage evidence.

Results use `scan_secrets_gate_v1`, action `pre-commit`, policy `selected_index_v1`, scope `index`, description `full_selected_index`, checkpoint profile and explicit accounting units. Defaults remain 4,096 snapshots, 67,108,864 candidate bytes, 30 seconds, 134,217,728 capture bytes and 268,435,456 temporary bytes; explicit schema-1 overrides retain B4 bounds. Required audit records carry the actual action/policy/scope and `git_gate` route. Informational status remains historical, detector-free on read, and independent of audit/security enforcement.

The new `hooks/runtime/scan_gate.py:validate_result` boundary consumes bounded raw process output and exit status plus independently expected action/build/repository/index/budget identities, with an optional independently expected scope digest. It rejects missing, empty, malformed, duplicate/unknown-field, mismatched or internally inconsistent results. A caller must both validate successfully and require process exit zero. Exit one is findings; two is incomplete or required infrastructure failure; three is invalid invocation/configuration; 130 is cancellation. Early failures lacking initialized evidence cannot validate as an authorizing gate result. The scanner does not self-authorize by validating its own output.

A disposable fixture dispatcher invokes this shared boundary before actual Git commits. Clean staged states advance HEAD; unsafe staged states, alternate/partial unsafe states, missing/malformed/mismatched results, help output, invalid invocation and required-audit failures leave HEAD unchanged. This establishes the reusable caller boundary and fixture composition. T7 still owns production dispatcher installation and mandatory caller binding; T5-I owns combined current source/installed gate acceptance. A pre-commit result describes captured staged state and does not certify mutations by later hooks.

## Public red and green observations

- Initial new suite: the absent gate command returned exit 3 / `invalid_arguments` where a staged fake credential required exit 1. The same staged-secret/worktree-clean and staged-clean/worktree-secret test now passes.
- Apple Git returned substituted loose-object bytes successfully. Original `clean original\n` selects OID `080b3a9143782213ce0f34cca8986365bcccf542`; substituted `clean impostor\n` hashes to `6ac394ad6ddab9538b48408aa8cef36f22737831`. Before captured-object verification the public gate falsely returned complete clean / exit 0. It now returns incomplete / `git_output_invalid` / exit 2. Original and substituted body SHA-256 values are `e054f47cd0e9a4ca0ec4bfcdd21df3f8ecb2df7176838997fabd43463beb2db0` and `daa95371471e675c03c46fbaf0f81aba4f7c7ead96647e2808093cd3137f3507`. A separate late-corruption case retains previously detected findings alongside incomplete coverage.
- Multiple common flags before a gate initially produced a check failure schema. Its focused public test now passes with the gate schema and exit 3.
- Primary review reproduced an explicit `/tmp` index alias returning `candidate_unsafe` while identical physical bytes passed. The local `/var` alias control also reproduced exit 2 before repair, then passed; arbitrary-link negative controls remain.
- Primary review reproduced a repository argument named `status` being mistaken for a status command on the error path. One shared command recognition result repairs it; the retained public outside-repository fixture passes. An initial local fixture inside a Git repository correctly returned clean instead of the intended outside-repository error; its location was corrected.
- The neutral installer suite initially failed its maximum-inventory fixture because the maintained closure grew from 13 to 14 assets. Synthetic extras were adjusted from 45 to 44 at the same 64-item inventory limit, and the over-limit control from 46 to 45. The final 21-test installer suite passes; no admission bound or failure control was weakened.

## Verification

Commands were run from the private worktree with `rtk proxy` (except the RTK version probe). Native `ps` cancellation proofs used scoped sandbox escalation. Installer and generator suites were serialized, and source edits paused during generator snapshots.

| Command after `rtk proxy` | Observed result |
| --- | --- |
| `python3 scripts/test-scan-secrets-git-gates.py` | 23 tests pass; source CLI, actual commits, one neutral installed gate, capacity, audit/display, result controls, open stdin/closed output and cancellation |
| `python3 scripts/test_test_all.py` | 14 tests pass; explicit registry includes the new gate suite |
| `python3 scripts/test-scan-secrets-cli.py` | 35 tests pass |
| `python3 scripts/test-scan-secrets-status.py` | 29 tests pass |
| `python3 scripts/test-install-scan-secrets.py` | 21 tests pass, including real main Bash and macOS PowerShell installers in disposable homes |
| `python3 scripts/test-generate-hooks.py` | 26 tests pass before the final command-recognition-only metadata refresh |
| `python3 scripts/generate-hooks.py --write` then `--check` | Canonical generated outputs refreshed; final check current, 62 assets |
| `python3 scripts/test-scan-secrets-merge.py` | 33 tests pass through all providers |
| `python3 scripts/test-scan-secrets-streaming.py` | 22 tests pass |
| `python3 scripts/test-security-reporting.py` | 14 tests pass |
| `python3 scripts/test-scan-secrets-capture.py codex` | Pass; block/warn and native macOS errno-35 recovery controls |
| `python3 scripts/test-scan-secrets-capture.py copilot` | Pass; same boundary |
| `python3 scripts/test-scan-secrets-capture.py gemini` | Pass; same boundary |
| `python3 scripts/test-verify-security-fixture-patch.py` | 26 tests pass, with retained archived/current exact closure controls |
| `git diff --check` | Pass |

The source CLI closure is exactly 14 files (entrypoint, CLI, status, eleven listed runtime modules). Provider runtime closure remains eight normal helpers and total generated ownership remains 62 assets. Installed gate execution uses the copied neutral entrypoint/runtime and emits findings with required audit success. Existing installed round-trip tests separately prove independent operation after removing their copied source/provider trees.

## Runtime fingerprints

SHA-256 of changed/owned canonical runtime files at the frozen passing source:

| File | SHA-256 |
| --- | --- |
| `hooks/runtime/scan_audit.py` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` |
| `hooks/runtime/scan_cli.py` | `638735aeb2efe87eab5b807d73271d8f625bd0c6c0c7030507f41a6f23cadba0` |
| `hooks/runtime/scan_engine.py` | `8702f6856a0f6e5a497630d95758af4f9ab6a3450dc2356436d81df4755b5764` |
| `hooks/runtime/scan_gate.py` | `747a2751a42da2d49b76db442921b8e277e82a56bafea8b6c4d2a248407c97fb` |
| `hooks/runtime/scan_git.py` | `d43158cefff8d48526e03798e00a3d818abadb0d92b502313f8506ee8c96e2e2` |
| `hooks/runtime/scan_repository.py` | `001c9daa360840f7a6bce17ec7b31b510b6e628d8141e13718f60bd51ffc1634` |
| `hooks/runtime/scan_status.py` | `8076607c2f3399581b6f115d0df7d7a3906f393c4ccaa06bc1abce25a9df8488` |

## Limits and ownership

Native Windows execution is unverified. macOS PowerShell checks are not native Windows proof. The selected-index Windows branch composes existing held-handle operations without changing their native ABI. No outgoing-history traversal, pre-push action, LFS support or repository-hook installer is delivered here. Source provider tests do not establish installed provider delivery or hosted CI acceptance.

Primary review checked correctness, simplicity, architecture, security and performance and supplied the alias, held-handle and error-schema repairs. The primary owns ExecPlan reconciliation and the single coordinated knowledge-maintenance pass after all work completes. No additional canonical KB or skill edits were made by this node; no durable in-scope skill improvement was identified.
