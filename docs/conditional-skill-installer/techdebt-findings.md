# Conditional installer duplication cleanup

## Scope and acceptance

The user requested all meaningful duplication findings in `main...HEAD`, with no result cap, and authorized fixing every safe candidate. Discovery used fixed merge base `4f2b2f4efb8823683ceb046b51248f0dc0f27f37` through `6ff95ef643506332e6ff9f68ae30cf0c11cd089b`; local `main` was `7182b156`. The starting worktree was clean.

Three discovery lanes inspected substantively changed production units, Bash tests, PowerShell tests, and maintained consumers. Nearby existing helpers were considered for reuse. Pure unchanged file moves, historical evidence, immutable sources, and unrelated unchanged bodies were excluded. Safe preexisting repetition inside substantively changed units was eligible. Discovery found 23 safe candidates; there is no top-three cutoff.

All changes must preserve the [ExecPlan](ExecPlan.md) D1-D4 contract, public CLI seams, fixture inputs, independent assertions, diagnostics, environment isolation, source bytes, permission restoration, and external link/inode safety. Private helpers and literal loops are implementation details. Distinct platform and failure semantics remain explicit. All 23 safe candidates are fixed and independently validated locally against the frozen source/test files. Native Windows verification subsequently passed at published `b1e3704a` in [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419).

## Candidate ledger

Locations below identify source files; the fixed-range discovery IDs remain stable after line movement.

| ID | Classification | Duplication and chosen extraction | State |
| --- | --- | --- | --- |
| PROD-01 | Near | `scripts/rebase-skill-references.py`: share original-mode calculation and read-only hard-link refusal; keep chmod and each caller's exception/restoration boundaries local. | Fixed; local validation passed |
| PROD-02 | Exact | Same module: share lazy `os.walk` directory-link filtering, preserving in-place pruning and traversal order. | Fixed; local validation passed |
| PROD-03 | Near | `scripts/install.ps1`: share successful source-mode application versus failed-copy original-mode restoration. | Fixed; local validation passed |
| PROD-04 | Exact | Rebase CLI: one rebase call inside either temporary write access or `nullcontext`, preserving optional pruning. | Fixed; local validation passed |
| PROD-05 | Exact | Both installers: merge consecutive file-preflight loops while retaining all 13 paths in original order and the same first-error diagnostic. | Fixed; local validation passed |
| PROD-06 | Exact | PowerShell copier: combine identical SymbolicLink/Junction preservation branches; keep hard links and unsupported reparse behavior separate. | Fixed; local validation passed |
| BT-01 | Near | `scripts/test-install.sh`: share reference-subshell HOME/profile environment setup without applying it to selection cases. | Fixed; local validation passed |
| BT-02 | Near | Same suite: share script-only CLI fixtures and exact destination sentinels while preserving missing-source/dependency cases. | Fixed; local validation passed |
| BT-03 | Reimplementation | Same suite: share fingerprint equality composition while retaining every snapshot and distinct diagnostic. | Fixed; local validation passed |
| BT-04 | Reimplementation | Same suite: reuse existing `cleanup_test_workdir`; keep trap registration/lifetime in callers and read-only cleanup separate. | Fixed; local validation passed |
| BT-05 | Exact | Same suite: share the three excluded-document fixture writes with exact bytes. | Fixed; local validation passed |
| BT-06 | Near | Same suite: share the paired hard-link refusal status/diagnostic/fingerprint assertion group; retain both public calls and inode oracle. | Fixed; local validation passed |
| BT-07 | Near | Same suite: share six reference-fixture constructors without moving caller-owned EXIT traps. | Fixed; local validation passed |
| BT-08 | Near | `scripts/test-addy-install.sh`: share local-source fixture directories, leaving destinations and remote fixtures explicit. | Fixed; local validation passed |
| BT-09 | Near | Same suite: share local-source process environment; leave case-specific destinations, overrides, argv and redirection in callers. | Fixed; local validation passed |
| BT-10 | Near | Bash installer suite: share regular LF SKILL fixture writing and identical candidate payload loops; exclude CRLF, link and missing-file cases. | Fixed; local validation passed |
| BT-11 | Exact | Same suite: replace repeated hook chmod/executable guards with the same literal ordered matrix and per-file diagnostics. | Fixed; local validation passed |
| BT-12 | Near | Same suite: group matching provider fixture writes into literal loops, preserving exact contents and paths. | Fixed; local validation passed |
| BT-13 | Exact | Same suite: use two script-copy inventory loops, preserving order and the intervening RTK stub/PATH setup. | Fixed; local validation passed |
| PSC-001 | Near | `scripts/test-install.ps1`: share common child-profile mapping and process-environment save/restore primitives while retaining launch-specific overrides and try/finally. | Fixed; local validation passed |
| PSC-002 | Exact | Same suite: share the three permission-repair cleanup snippets; keep each finally block and deletion order. | Fixed; local validation passed |
| PSC-003 | Near | Same suite: share external read-only hard-link fixture construction with explicit bytes/paths and distinct caller oracles. | Fixed; local validation passed |
| PSC-004 | Reimplementation | Same suite: reuse `Get-PythonForFixture` for Codex assertions, preserving interpreter precedence and contextual missing-dependency errors. | Fixed; local validation passed |

## Retained and rejected extraction candidates

These entries explain all considered repetitions that were not selected. Retention is based on behavior or lack of meaningful shared implementation, not a result cap.

| IDs | Retained repetition | Reason |
| --- | --- | --- |
| PROD-07 | Addy importer versus installed-reference rewriting | Different path resolution, source text, byte/newline, link and copy contracts. A shared cross-script algorithm would introduce coupling and an architectural decision. |
| PROD-08 | Reparse classification across generator, provider validation and rebaser | Helpers have incompatible reject/raise/false-on-error and fallback semantics. Preserve their trust boundaries. |
| BT-I01, BT-I02, PSC-007 | Independent byte/mode/inode/reference oracles | Different obligations, CRLF handling, actual eight-reference coverage and failure checks must not become self-validation through production code. |
| BT-I03 | Pruning with absent references, read-only files, hard links and preexisting content | Fixture writing is shared by BT-05; distinct assertions and repeat behavior stay explicit. |
| BT-I04, BT-I05 | CLI result groups and option/environment matrices | Help, success, argument failures and source failures have different streams, exits, stage sentinels and mutation allowances. Preserve literal inputs and Unicode cases. |
| BT-I06 | Root-linked versus nested-linked external targets | Link identity, raw targets and traversal rules differ. BT-03 shares only fingerprint comparison. |
| BT-I07 | One-line file/presence/absence predicates | Different `-f`, `-e`, `-d` and symlink semantics; a new assertion API would obscure simple case-specific checks. |
| BT-I08, BT-I14 | Copy inventory and hook-mode repetition reconsidered under changed-unit scope | Safe portions promoted to BT-13 and BT-11. Ordered main dispatch and unrelated commented tests remain explicit. |
| BT-I09 | Stale generated output versus generator failure | Shared fixture/cleanup mechanics are covered by BT-02/03/04; recovery advice must remain required in one case and forbidden in the other. |
| BT-I10 | Addy default/explicit reference depth and remote clone/pull | Local fixture/process mechanics use BT-08/09; reference-depth expectations differ, and remote invocation bodies only received path assertion edits. |
| BT-I11, BT-I12 | Unicode test data and stage/failure stubs | Different code points and failure contracts are test inputs rather than competing algorithms. |
| BT-I13 | Import declaration/Git fixture versus Addy remote fixtures | Different setup policy and public behavior; a cross-suite fixture dependency adds coupling without meaningful shared policy. |
| PSC-005 | Three direct rebaser argument lists | Success/no-op and captured refusal calls differ. An argument-only wrapper offers little reuse and risks hiding the exercised CLI boundary. |
| PSC-006 | PowerShell fixture lifecycle and fingerprint pairs | Existing helpers own substantial mechanics. Snapshot timing and allowed mutation differ; a callback framework would add scope/control-flow risk. |
| PSC-008 | Independent profile-isolation oracle, cp1252 constraint and bytecode suppression | Keep oracle setup independent from the mapping under test and retain distinct lifetimes. Low-level mechanics may be shared only where equivalent. |
| PSC-009 | PowerShell file inventories, mode literals and stream primitives | Data-level repetition with explicit identity/order; no substantial competing policy or algorithm. |
| Consumer/rename-only units | Registry expected paths, relocated grader utilities, eval manifests, README and guidance | Changed paths preserve independent expectations and self-contained skill bundles. No new shared runtime, prose abstraction or unrelated body cleanup is justified by relocation alone. |

## Verification

All checks below passed on 2026-10-14 against the same frozen six-file input. Environment: macOS 26.7.1 arm64, Bash 3.2.57, Python 3.14.6, PowerShell 7.6.6, RTK 0.51.0. Independent validators inspected every selected candidate; none required a corrective edit or reversion.

| Command or check | Result |
| --- | --- |
| `rtk proxy bash scripts/test-install.sh` | Exit 0; all 34 enabled installer tests, including the real local-Git import-to-install case, passed. |
| `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` | Exit 0; `test-install.ps1: all tests passed.` Sole skip: junction creation unsupported on this macOS host. |
| `bash scripts/test-addy-install.sh`, invoked by an RTK-prefixed capture wrapper | Exit 0; all 10 enabled cases passed. The two preexisting commented cases remain unchanged and have static-only equivalence evidence. |
| `rtk proxy python3 -B /private/tmp/conditional-techdebt-production-helper-checks.py` | Exit 0; all 15 baseline/current public-process cases matched independently asserted outcomes. The harness and logs are disposable verification artifacts. |
| Bash syntax for production and both test scripts, including `/bin/bash` 3.2 | Exit 0. |
| PowerShell Parser.ParseFile for installer and fixture suite; Python and embedded-Python syntax | Exit 0. |
| Independent assertion, case-data, diagnostic, environment, trap and dispatch comparisons | Passed: all 33 Bash heredocs and 235 PowerShell assertion lines preserved. All test definitions and ordered dispatches remained intact. |
| `rtk proxy git diff --check` and `rtk proxy python3 scripts/lint-okf.py` | Exit 0 after final documentation reconciliation. |

The full suites ran serially, followed by focused helper checks and then Addy. The 15 helper cases covered help, missing/unknown arguments, nonzero copy exit, copy launch failure, successful mode-preserving copy, pruning enabled/disabled, absent optional references, nested links, all three source/destination root-link combinations, and read-only/writable hard links. They verified CRLF/UTF-8 bytes, source-mode adoption, failure-mode restoration, external fingerprints and expected streams/exits. Exception comparisons preserved the final diagnostic; traceback frames necessarily changed with extracted helpers.

The following SHA-256 values were captured before the suite runs and remained identical after all validation:

| File | SHA-256 |
| --- | --- |
| `scripts/install.sh` | `a7f4fb4e674a2a846d433755d60425a0381977d4cf34e5b1b582c52b9e1204d6` |
| `scripts/install.ps1` | `dc478ba61dae9d0ea5d15b9ed3d78bfc45dc299a886e088260657bc7eb35123f` |
| `scripts/rebase-skill-references.py` | `ef6832075062d3fc6d4bd98fbd53522274d0eb8c3718cde2764dd1e4ff41a23f` |
| `scripts/test-install.sh` | `0e45fa5f7fef0a1a56e99a3177eeda03db5a8bda7b560010bd2b8ec1e4227a6d` |
| `scripts/test-install.ps1` | `b4b868c1343e2f548a1ec4adc7dab9697731f8cbcc3cc8fb508fa875b04c7240` |
| `scripts/test-addy-install.sh` | `b2cb1c5351819254fbec19bdd4b9dc9f943daa67e067cac2db930c6224829050` |

All 23 candidates meet local acceptance, and [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) established native Windows fixture acceptance at published `b1e3704a`. PROD-06 junction preservation, external-target safety, Windows ReadOnly hard-link refusal and profile/Unicode cases passed without native capability skips. All downstream workflow checks succeeded. The three skips concern inapplicable POSIX mode/executable/unreadable000 assertions and retain local proof; general NTFS ACL behavior is not established. [Current native evidence](techdebt-native-windows-verification.json) retains actual host, versions, step times and exact input. Prior native evidence at `44a47e5b` remains historical.

## Agent-doc admission and disposition

The single coordinated `update-agent-docs` pass followed all workers and validators. Existing script, PowerShell and testing rules already cover private helper placement, profile restoration, interpreter selection, source/installed boundaries and native proof limits. The new helper names and session narrative are readily discoverable source facts, so no canonical KB changes are warranted.

Added: None. Changed: None. Split or moved: None. Deduplicated: None. Index updates: None. Remaining doc quality TODOs: None. No skill improvements identified.

No additional safe in-scope dedupe target remains from discovery. All selected candidates were fixed; none was reverted or blocked. The retained groups above are intentional, incompatible, ambiguous in value, or outside the substantive scope. Cleanup is committed and published as `b1e3704a` after explicit user approval on 2026-10-15. [Windows run 38737045419](https://github.com/japurcell/skills/actions/runs/38737045419) passed on that exact revision; [native evidence](techdebt-native-windows-verification.json) and ExecPlan Milestone 6 record its actual outcome. The previous publication rejection is resolved history. Only result-documentation edits remain uncommitted.
