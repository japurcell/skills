# T5a-R changed staged-file policy evidence

Observed on 2026-10-16 in the isolated private worktree `codex/design-b-t5a-r`, based on primary `388c939`. Executable inputs match primary's D1 documentation commit `69c735b`. The user explicitly selected **changed staged files inspected in full**. This repairs the original T5a node; it does not change B5 outgoing-history coverage.

The original [T5a evidence](t5a-evidence.md) is retained unchanged as historical proof of `selected_index_v1` / `full_selected_index`. Its SHA-256 remains `266d47930fd45d340e0754b543abf8d637abdbec52698fb24ba6622fec5653be`; its old full-tree acceptance does not establish acceptance of this revised policy.

## Current behavior and proof

The public action remains `scan-secrets gate pre-commit --repo PATH --json`. Its policy is now `selected_staged_v1`, scope `index`, description `changed_staged_files`. The engine reuses canonical staged-path collection relative to the captured private HEAD and actual selected index, including explicit `GIT_INDEX_FILE`. It then inspects each selected stored version in full. The obsolete all-index collector was removed; there is no diff-line suppression, matcher change, fixture-literal rewrite or allowlist.

The first new real-commit reproducer failed before runtime edits: an existing committed fake credential fixture in `selected.txt` blocked an unrelated clean `unrelated.txt` commit with exit 1 and unchanged HEAD. The same public fixture now commits successfully and advances HEAD. Editing `selected.txt` only by appending a safe line leaves its old credential line unchanged; that staged file still produces findings and the actual commit leaves HEAD unchanged. Deleting that old fixture while changing the safe file contributes only the remaining safe stored version and allows the commit.

Additional public controls prove renamed and new credential-like paths reusing an old clean blob OID remain selected, run path policy and block actual commits. Unborn additions, unresolved stages anywhere alongside a clean staged file, alternate indexes, actual `git commit --only` temporary indexes, split indexes, held selected-index acquisition and narrow verified macOS aliases remain covered. Existing skip/warn, missing-helper, capacity, cancellation, closed-pipe, audit/display independence and malformed/missing/mismatched-result controls remain. The current caller boundary rejects the old full-index policy as a gate result. Status continues displaying old-policy records as historical information and admits the new policy only with index scope.

The neutral installer fixture installs from a disposable copied source, deletes that source, then runs the installed gate. An unrelated safe staged file with an unchanged fixture elsewhere passes; changing the old fixture with only an appended safe line produces findings. Both results come from the independent installed entrypoint/runtime. A separate real SHA-256 repository allows the unrelated commit, blocks the unchanged-secret-line commit and rejects substituted loose-blob bytes with `git_output_invalid` / exit 2. Existing SHA-1 corruption and late-known-findings controls still pass. No outgoing SHA-256 acceptance is inferred.

Two new fixture setup errors were corrected before final validation: the copied installer source needed its maintained `scan_install_windows.py` support asset, and intentionally deleting an already-staged changed fixture required Git's explicit force option. No assertion, failing security test or admission limit was removed or weakened.

## Frozen real-repository probe

Primary froze `/Users/adam/.codex/worktrees/a468/skills` at `69c735bf402bbd83615b2aaf310eefd6abb26b84` while this repaired source entrypoint ran against it. HOME, USERPROFILE, XDG configuration and audit/status data roots were disposable. The result was exit 0, `complete_clean`, coverage complete, required audit written, `selected_staged_v1` / `changed_staged_files`, zero candidates, zero inspected snapshots and zero candidate bytes. This certifies the empty changed-staged scope, not all repository content. Metadata acquisition still charged 639,100 capture bytes and a 637,209-byte temporary peak.

Before/after identities were identical:

| Input | Identity |
| --- | --- |
| `head` | `69c735bf402bbd83615b2aaf310eefd6abb26b84` |
| `index_sha256` | `7218225d25f61e4b18aaca81551b5cb0639b0b7e2aeae6973d0e00fb6edc51f6` |
| `head_file_sha256` | `589a792923e1da5e65d878dd29697bc22e3ec769a36034cc2c67958cd00d7731` |
| `config_sha256` | `282eddd5df54242dcf6e2a171df68a1c6e71ae71b3641be58eba943b9323d4df` |
| `refs_sha256` | `adb1d28cd747c32bd75f7d4d2d266359ac4f5f3fa463d6099a2ff3bb0a20d7a5` |

The probe did not change source/index/refs/config. Primary was notified when the read-only probe completed and then released its freeze. Existing fake fixture literals remain intact.

## Validation

Environment: macOS 26.7.1 arm64, Python 3.14.6, Apple Git 2.54.0 and RTK 0.51.0. Commands ran from this private worktree, prefixed with `rtk proxy`. Native `ps` cancellation proofs used scoped escalation. Generator and source-mutating installer suites were serialized; no edits occurred during generator whole-tree snapshots.

| Command after `rtk proxy` | Observed result |
| --- | --- |
| `python3 scripts/test-scan-secrets-git-gates.py` | 26 pass; actual commit and source-free installed positive/negative controls included |
| `python3 scripts/test-scan-secrets-cli.py` | 35 pass |
| `python3 scripts/test-scan-secrets-status.py` | 29 pass |
| `python3 scripts/test_test_all.py` | 14 pass |
| `python3 scripts/test-install-scan-secrets.py` | 21 pass; real disposable-home Bash and macOS PowerShell installer paths |
| `python3 scripts/test-generate-hooks.py` | 26 pass |
| `python3 scripts/generate-hooks.py --write` then `--check` | Canonical outputs refreshed; current, 62 generated assets |
| `python3 scripts/test-scan-secrets-streaming.py` | 22 pass |
| `python3 scripts/test-security-reporting.py` | 14 pass |
| `git diff --check` | Pass |

The source diff changes only four canonical runtime files, the precommit suite, canonical generated assets and this evidence. The neutral closure remains 14 files, provider runtime closure eight helpers, and generated ownership 62 assets. Matcher policy, streaming matcher, capture, repository protection, budget, audit and outgoing collector source were not edited. Targeted generated-provider streaming/reporting checks cover the shared engine's unchanged default behavior; unrelated broad suites were not rerun.

## Frozen canonical runtime fingerprints

| File | SHA-256 |
| --- | --- |
| `hooks/runtime/scan_cli.py` | `a7de2e91771585d7c5d3c639a4fdeb5243f15359d3610d65f1bc749d2d383a59` |
| `hooks/runtime/scan_engine.py` | `33bbfb091672a9ef5b03d04c291e9e91ec063945cbbfbc08a0007ab2c3ab2249` |
| `hooks/runtime/scan_gate.py` | `354611807bd5b4b04e8dc749036c5a8f558ff43c395b290d7231d6b4bd90f25f` |
| `hooks/runtime/scan_status.py` | `87f78b532381a7db82bb202054d78900b8cfa50e2ac6741af72b19d64a1ccce2` |

## Review and remaining boundaries

Primary's five-axis review found the frozen repair consistent with the approved scope. No test was skipped or deleted to obtain a passing result. The superseded full-tree expectation was replaced by positive actual-commit acceptance and full-changed-file rejection, as explicitly requested.

Native Windows execution remains unverified; macOS PowerShell is not native Windows proof. Pre-push/history collection, LFS and production repository dispatcher installation are outside this node. All repositories, indexes, homes, dispatchers and installs used for mutation controls were disposable; there was no external push, live-home deployment, hook trust/enablement change or background worker. Primary owns the final coordinated KB/ExecPlan/README pass and T5b integration.
