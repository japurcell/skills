# T8: Align reporting-contract tests with bounded scanner reports

Date: 2026-10-14. Source base: `e5370cb9`. Private branch: `codex/hook-resilience-t8`.

## Scope and public seam

This task changes only `scripts/test-scan-secrets-merge.py`, `scripts/test-codex-hooks-windows.ps1`, and this evidence file. Both suites invoke the generated scanner JSON entrypoints as subprocesses. No scanner, generated hook, installer, live hook configuration, or product limit changed. The coordinator owns the plan, aggregate validation, and coordinated knowledge-maintenance pass.

The accepted report contract replaces newline/tab label characters with ASCII spaces and clips long labels to 160 ASCII characters, including the final three dots. Test expectations use explicit known labels and fixture dimensions; they neither import nor invoke the production sanitizer. PowerShell warnings require the complete action message and an anchored suffix with exact outcomes, route, cause, profile, and a 16-character lowercase hexadecimal build identity.

## Original failures retained

The coordinator supplied the V1 aggregate observation on `ec736044`: merge suite ran 33 tests in 201.123 seconds and failed 36 provider/mode/scope subtests across the older-Git, delimiter-path, and long-path tests. Detection succeeded, but path expectations still required raw or unclipped names.

Before editing, from this isolated checkout:

```text
rtk proxy python3 scripts/test-scan-secrets-merge.py --provider copilot MergeScannerTests.test_batch_paths_preserve_newlines_tabs_and_colons -v
Ran 1 test in 0.806s
FAILED (failures=4)
```

All four failures were the exact path assertion. The public report retained `github_classic_pat`, severity `high`, line `1`, and redacted match `ghp_...FAKE`, with path `line break name.txt`; the test expected `line\nbreak\tname.txt`. Block mode denied and warn mode allowed with the required warning. Full disposable transcript: `/tmp/hook-resilience-t8-red.log`.

Before the PowerShell edit:

```text
rtk proxy pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1
Exception: scripts/test-codex-hooks-windows.ps1:36
Warning was absent or lacked action
```

The old exact string omitted the newly required attributable suffix. Full disposable transcript: `/tmp/hook-resilience-t8-pwsh-red.log`.

## Acquisition and negative-control proof

The delimiter and older-Git fixtures now include credential-free files named like the safe display label and its delimiter fragments. Their only fake credential remains in the original path's stage-zero index blob after replacing its working file with safe content. Thus detection cannot be explained by acquiring the displayed name, splitting its delimiters into another path, or falling back to the working file. The delimiter test separately moves the sole staged credential to `:0:notes.txt`, then replaces that working file with safe content, proving that the leading colon is an ordinary path character.

The long-path fixture retains all 256 paths and the existing 8,192-byte command-argument wrapper. Only the last indexed path contains the fake credential. Its explicit expected label is `entry-255-` followed by 147 `x` characters and three dots. The distinct prefix survives clipping, and staged-scope findings prove late index acquisition. Both clean and secret phases still exercise all three providers, block/warn modes, and diff/staged scopes.

Finding checks now also require exact severity, line 1, and redacted-match metadata, plus exact provider, mode, and scope. All existing tests and negative controls remain. PowerShell still checks PreToolUse denial, Stop blocking, and an empty clean response, and now checks all three non-clean responses for credential leakage. Both fixtures keep homes, config, logs, and repositories disposable; PowerShell restores inherited environment values in `finally`.

An attempted strengthening replaced the long-path working file after staging. That legitimately added a 257th candidate in diff scope and failed six subtests with `snapshot_count_limit/git_candidates`, measured 257, limit 256. The observation is retained in `/tmp/hook-resilience-t8-focused-green.log` (`Ran 3 tests in 58.646s; FAILED (failures=6)`). The final fixture preserves the original 256-candidate topology and uses staged-scope evidence for index acquisition. This was a fixture-design error, not a product defect or a reason to change the product bound.

## Final validation

Observed final focused check, covering all three providers and both modes/scopes:

```text
rtk proxy python3 scripts/test-scan-secrets-merge.py MergeScannerTests.test_pre_238_git_allows_clean_index_and_detects_staged_secret MergeScannerTests.test_batch_paths_preserve_newlines_tabs_and_colons MergeScannerTests.test_batch_long_paths_fit_bounded_git_command_lines -v
Ran 3 tests in 91.948s
OK
```

Transcript: `/tmp/hook-resilience-t8-focused-final.log`.

The final isolated PowerShell suite passed with `PASS: Codex scanner Windows envelopes`; transcript: `/tmp/hook-resilience-t8-pwsh-final.log`. Python `ast.parse`, PowerShell `System.Management.Automation.Language.Parser.ParseFile`, and `rtk proxy git diff --check` passed.

The complete unchanged 33-test inventory passed, including all providers, both enforcement modes, both scan scopes where applicable, malformed capture/index responses, unsafe paths, merge stages, late index secrets, resolved 250-file merges, and byte/snapshot bounds:

```text
rtk proxy python3 scripts/test-scan-secrets-merge.py -v
Ran 33 tests in 202.541s
OK
```

Transcript: `/tmp/hook-resilience-t8-merge-full.log`. No skips or weakened controls were introduced. Full aggregate checks and performance benchmarks belong to the coordinator. These are macOS source-entrypoint checks; they do not establish native Windows execution or authenticated provider delivery. No skill improvements identified.
