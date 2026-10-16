# T7a read-only repository installation preview

Observed on 2026-10-16 in private branch `codex/design-b-t7a`, based on `b36fcd438267ccd8f3f647b2f484ecada895638c`. This evidence covers T7a only. The coordinator owns plan reconciliation, serial integration and the final coordinated knowledge pass. T7b activation, composition, rollback, D2 concurrency scope, native Windows and milestone acceptance remain open.

## Delivered behavior

The authoritative [CLI](../../hooks/runtime/scan_cli.py) exposes `hooks install/uninstall --repo PATH --dry-run`, explicit `--git PATH`, `--budget-file PATH` and the existing common flags. The [source helper](../../scripts/install-repo-gates.py) forwards into that parser without owning another parser or scanner policy. No-argument/help/version paths remain read-only and do not discover Git. A non-dry-run action returns exit 3 with `installation_activation_unavailable` before discovery or mutation. Successful preview JSON uses `scan_secrets_repo_install_v1`, `dry_run=true`, `activated=false`, `changes_applied=false`, and `authorizes_publication=false`. Quiet suppresses human success only; requested JSON and errors remain visible. Preview never reads stdin.

[Discovery](../../hooks/runtime/scan_repo_install.py) identifies canonical root, worktree Git directory, common Git directory, object format, linked-worktree inventory and existing worktree-configuration enablement. It preserves origin-aware system/global/include/local/worktree configuration precedence and standard owner-selected `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM` locations. Inherited command-config injection and repository/object/index redirects are removed. Metadata queries neutralize fsmonitor, pager, maintenance and related execution settings. Git is pinned to a trusted absolute executable outside repository ownership. On macOS an Apple launcher, including an alias resolving to it, requires an explicit direct `--git PATH`; the resolved selection is computed once and reused. The preview reports its exact executable and selection source. It does not invoke `xcrun` to guess active developer selection.

The snapshot reports supported original hook paths, held-read identities, digests and executable state for all 28 hooks in the consulted Git hook manual. Relative hooksPath is resolved separately against the appropriate hook cwd, including receive-side Git-directory execution. Duplicate values from the same scope/origin, empty or unsupported path values, linked/unsafe originals and untrusted metadata are refused. Original hook bytes are never executed. Ordinary linked worktrees with shared configuration explicitly report `shared_config_requires_scope_decision`; already enabled worktree configuration can report `selected_worktree`. Preview never enables extensions or broadens repository coverage.

It reports absolute intended runtime, interpreter, data, budget and repository dispatcher locations, plus proposed operations. Only verified root-owned macOS `/tmp` and `/var` aliases are canonicalized when pinning trusted locations; arbitrary linked ancestors remain refused. An explicit budget is ordinary, owner-only, stable and admitted through the existing complete schema-1 validator. Both profile-read digests must match each other and the protected snapshot digest. Built-in finite defaults remain available. The exact running interpreter is probed for Python >=3.12 and a working in-memory sqlite3 connection with `autocommit` and `SQLITE_DBCONFIG_DEFENSIVE/setconfig`.

There is no accepted repository activation manifest schema yet. An absent manifest is reported explicitly; a present malformed or unknown manifest produces a safe refusal with its exact identity/digest, without interpreting neutral bundle `installation.json` as repository ownership. Native Windows preview explicitly refuses until native ownership behavior is verified. Non-dry-run activation is not implemented.

Discovery has a 10-second operation deadline, 2 seconds per Git subprocess, 64 KiB per metadata file/capture, 1 MiB aggregate capture, 2,048 configuration entries and 128 worktrees. Existing held-ancestry/native-read and bounded capture/child cleanup mechanisms are reused. These bound loops, subprocess waits and captured bytes; they do not claim to interrupt every possible kernel filesystem stall. Dry-run creates no persistent configuration, hook, report, backup, manifest, lock or destination directory. Bounded private Git captures are cleaned.

## Public E2E proof and observed repairs

All tests use disposable repositories, homes, configuration, temporary captures and optional installed bundles. Fixtures compare complete byte/mode/inventory fingerprints, including symlink targets. Success and error cases leave original hooks unchanged and dormant. A real FIFO configuration include holds the actual Git metadata process for timeout and cancellation controls; it is not a mocked Git implementation.

The final [25-method public suite](../../scripts/test-install-repo-gates.py) covers default/inherited/global/custom/relative hooksPath; conditional includes and precedence; owner-selected global origin equivalence with actual Git; absent/duplicate/empty/URL settings; ordinary and enabled linked worktrees; paths with spaces; linked and malformed metadata; original-hook/config links; budget trust, canonical aliases and digests; unsupported real Python; non-dry-run refusal; noargs/help/version/common options and the thin helper; open stdin; redacted JSON/text errors and size limits; repository PATH Git sentinels and dormant fsmonitor/credential/SSH helpers; timeout/cancellation cleanup; Apple launcher aliases; and source-free real neutral-installed install/uninstall previews.

Observed reds and repairs are distinct:

- The initial public preview exited 3 as an unknown command. The shared parser/preview slice then passed.
- The new neutral closure initially imported optional status eagerly, making the existing 35-case CLI suite fail with `runtime_unavailable`. Making only discovery's status import lazy restored the existing contract. A subsequent CLI run had 34 passes and one sandbox `ps` EPERM; the authorized isolated suite rerun with process observation passed all 35. The sandbox failure was not counted as a pass.
- A public 0644 budget was initially admitted. Private-file and trusted-ancestry checks then made the public trust control pass.
- Malformed repository ownership initially produced the generic unsupported-schema reason. Protected identity capture plus strict duplicate-aware JSON classification now distinguishes invalid from unknown ownership safely.
- Raw linked Git metadata targets and a repository PATH Git shim were initially accepted. Raw target ancestry validation and repository executable refusal made both public controls pass without execution.
- The first strict disposable TMPDIR proof observed Apple's `/usr/bin/git` launcher creating `xcrun_db`. Direct executable selection removed that side effect; ambiguity now refuses with explicit `--git` recovery. A real alias to the launcher also initially exited 0; the final single resolved selection rejects it before execution. No final preview infers active Xcode selection from the existence of CommandLineTools.
- The first full 62-case gate run passed 60 cases and failed two exact installed closure assertions expecting 19 rather than 20 assets. Updating only those counts made all 62 pass. Neutral maximum inventory remains exactly 64 entries with 58 assets; added synthetic closure members were reduced by one rather than weakening the boundary.
- A review suspicion that valid `/tmp` budgets were refused was **not reproduced** on this host: both physical and alias previews succeeded. The comparison instead exposed differing reported budget locations. Canonical pinning is an interface normalization, not a repaired observed refusal; physical/alias profiles and digests now match the same reported location.
- A review suspicion of terminal-control leakage from a real repository path was **not reproduced**: the existing origin-path validation already refused it. Direct text `--no-color` and JSON controls now prove exit 3, no raw ANSI/credential text and unchanged state. No runtime repair was made for that suspicion.

## Verification results

Working directory for all relative commands: `/Users/adam/.codex/worktrees/design-b-t7a/skills`. Every shell invocation used RTK and `login:false`. The pinned preview Git was `/Library/Developer/CommandLineTools/usr/bin/git`, version `2.54.0 (Apple Git-157)`. Current process proof is macOS only. The real unsupported-interpreter fixture used the installed CommandLineTools Python 3.9; other hosts must provide a real pre-3.12 interpreter through `TEST_UNSUPPORTED_PYTHON` if no candidate exists. Missing prerequisites are errors, not passing skips. Linux and native Windows were not executed.

| Check | Observed result and scope |
| --- | --- |
| `rtk proxy python3 scripts/test-install-repo-gates.py` | Final complete 25/25 on Python 3.14.6, 6.203 seconds |
| `rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 -B scripts/test-install-repo-gates.py` | Final complete 25/25 on Python 3.13.14, 5.882 seconds |
| `rtk proxy python3 scripts/generate-hooks.py --write`, then `--check` | After final runtime edits, canonically refreshed exactly six scanner/diagnostic outputs; final freshness 62/62 |
| `rtk proxy python3 scripts/test-scan-secrets-cli.py` | Final frozen runtime 35/35, 18.071 seconds |
| `rtk proxy python3 scripts/test-scan-secrets-status.py` | Compatibility snapshot 29/29, 15.432 seconds |
| `rtk proxy python3 scripts/test-scan-secrets-git-gates.py` | Compatibility snapshot 62/62, 48.457 seconds after exact closure assertion repair |
| `rtk proxy python3 scripts/test-install-scan-secrets.py` | Compatibility snapshot 21/21, 39.849 seconds, real installers/disposable homes |
| `rtk proxy python3 scripts/test-generate-hooks.py` | Compatibility snapshot 26/26, 17.861 seconds |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py` | Compatibility snapshot 16/16, 65.981 seconds |
| `rtk proxy python3 scripts/test_test_all.py` | Registry 14/14; exact maintained suite set grows 58 to 59 |
| `rtk proxy python3 scripts/test-scan-secrets-git-gates.py GateTests.test_neutral_installed_bundle_selects_changed_files_without_source_checkout GateTests.test_publication_neutral_installed_bundle_uses_exact_closure` | Final build source-free installed gates 2/2, 0.806 seconds |
| `rtk proxy env TEST_GIT_LFS=/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs python3 scripts/test-scan-secrets-lfs.py LFSTests.test_source_free_real_installed_launcher_delivers_verified_payload` | Final build source-free installed verified delivery 1/1, 1.740 seconds |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_scanner_runtime_helper_closure_fails_closed_and_preserves_recovery` | Final canonical metadata focused recovery 1/1, 7.509 seconds |
| `rtk git diff --check` | Pass before evidence/staging; repeated before commit |

The compatibility snapshots precede later changes confined to discovery: resolving Git selection once, canonicalizing established system aliases, and test-only additions. No gate, publication, LFS, private handoff, status, neutral packaging or generator implementation changed in those repairs. Final focused installed checks and complete preview/CLI runs exercise the new build; earlier broad results are retained as source-equivalence evidence, not mislabeled as complete final-build reruns. The original T6 evidence is byte-identical. Provider helper behavior/closure remains distinct from refreshed provider metadata. Generator checks and installer suites were serialized; no timing acceptance claim is made.

## Final identities

Neutral scanner build: `7fde2f03ce5c3fa1e06235b83b87061b92a0ca5022578947f512ca0f7f2122b9`, 20 ordered build inputs / exact neutral installed files, 17 literal `MODULES` members. Provider helper closure remains 8. Canonical provider `REPORT_BUILD` is `6f24e9ff65a33255`. Generated targets remain 62. Registry has 59 maintained suites.

| Artifact | SHA-256 |
| --- | --- |
| `hooks/runtime/scan_cli.py` | `fd4bf28daefc1e6e719be0197f3838e1a82413f22cda71211c3f8c77dbd1bb8e` |
| `hooks/runtime/scan_repo_install.py` | `f7b5671dec95eae1050936930073b869a60153a6bc2080b4d514046ee3f13567` |
| `scripts/install-repo-gates.py` | `2121090429c63197fc671adb5b0eac094f6181b90663b131520b301ab6a4cfb3` |
| `scripts/test-install-repo-gates.py` | `dd25334020600e91ad50b05556fa0c1e2310e3848606516a7342e9719509f6a8` |
| `scripts/test-scan-secrets-git-gates.py` | `92c3bee5c98a1a16f8638f5d3e174c9dda60170298d152dcb5edc8cbac1b20bf` |
| `scripts/test-scan-secrets-lfs.py` | `9fc89ff01fe7395847fee717623e60c53628893cac4e710928cda17360cfc8b8` |
| Unchanged `hooks/runtime/scan_dispatch.py` | `f23165bec799972b3211fcdf68d48aeab9932563a1eb6f91f7be6cc445eb68f9` |
| Unchanged `hooks/runtime/scan_private.py` | `e5562785406b2f06727f520dd2755182ab8d49922a456d4204abd23c1a220a59` |
| Unchanged `docs/hook-resilience-design-b/t6-evidence.md` | `c17fe12719d6338c758fc4169478fcdba78ddf486bb949f210797f7707205983` |
| `.codex/hooks/scan-secrets.py` | `c9b063c5c4be7c1b8c17cf13b0f89b14dcc979b241bf14f954b2bfc578f20bd6` |
| `.codex/hooks/hooks-diagnostics.py` | `b040bb5df505bb73a6633b1bac7ef81779f31983df971ac64eb62de7832f0f82` |
| `.copilot/hooks/scripts/scan-secrets.py` | `9de8b42a54c281a457fe3c12b7b11e2ad94a23e9a088a40f3573e96e8806e8d0` |
| `.gemini/hooks/scripts/scan-secrets.py` | `0cabdddac7fe169c02336e122663b42f0170552e0290dd970623dd3eaf5d3fb4` |

New source/helper/suite modes are 0755. The neutral maximum-inventory assertion still requires exactly 64 entries and 58 assets, with 38 synthetic extra modules admitted and 39 refused. The only gate/LFS suite changes are their exact 19-to-20 closure assertions. Scanner policy and provider lifecycle placement are unchanged.

## Authority and remaining limits

Nontrivial configuration, hook cwd/framing and SQLite capability choices were checked against the official [Git 2.54 configuration manual](https://git-scm.com/docs/git-config/2.54.0), [Git 2.54 hook manual](https://git-scm.com/docs/githooks/2.54.0) and [Python 3.14 sqlite3 manual](https://docs.python.org/3.14/library/sqlite3.html), together with the immutable local CLI design sources. Those references do not select a new minimum supported Git version or establish native Windows behavior.

T7a makes no repository changes. T7b must still define/validate activation ownership, composition and linked-worktree mutation scope, implement conditional restoration/recovery under the eventual D2 decision, preserve every relevant original hook and complete native dispatch/ownership proof. Preview is a bounded read-only discovery snapshot, not global atomicity, a passing security scan, a saved authorization receipt or permission to publish. No background process, watcher, checkpoint, retry, provider deployment, home settings update, real hook mutation, global Git change or external remote publication was performed. The sole installed transfer proof uses the already accepted isolated local fixture and pinned Git LFS 3.8.0 boundary; it does not broaden T6 transport/platform support.
