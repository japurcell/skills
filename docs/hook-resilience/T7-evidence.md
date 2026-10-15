# T7: trusted installed scanner and Guardian launches

Observed on macOS, 2026-10-14, starting from `e3103d74`. This is isolated
installation evidence, not authenticated provider dispatch or native Windows
execution. No live user home was installed or modified.

## Public red reproduction

The maintained public test is
`scripts/test-hook-diagnostic-recovery.py`, methods
`test_bash_installed_commands_resist_startup_and_path_injection` and
`test_powershell_installed_commands_resist_startup_and_path_injection`.
They run the real installer into a disposable HOME and CODEX_HOME, read installed
provider JSON, and execute the registered command bytes without adding Python
flags. The Python executable path contains spaces, an ampersand and an apostrophe;
the install home contains spaces and an apostrophe.

Before implementation, the Bash installed-command test failed on startup code.
A subsequent independent replay extracted `git archive e3103d74` to a disposable
directory, loaded the current test with `runpy.run_path`, set its `ROOT` to that
archive, and ran the Bash installed-command case. Every command reset the sentinel
before execution. All six scanner/Guardian commands across Codex, Copilot and
Gemini independently wrote the sentinel for both hostile PYTHONPATH/sitecustomize
and post-install Python PATH replacement. The baseline runner reported 12 attack
subtest failures plus the expected missing ordinary audit evidence.

## Repair and scope

Both installers resolve the selected Python's actual absolute `sys.executable`
once using isolated startup. Registration mergers render that executable with
exact `-I -S -B` and absolute installed hook paths for scanner and Guardian,
including scanner stop registrations. Runtime launches do not consult PATH.
Source registration templates remain portable; installation materializes trusted
paths. Owned old registrations are upgraded, including exact pairs naming a
previous interpreter that no longer exists. Unowned handlers and user settings
remain governed by the existing merge rules.

POSIX commands use shell quoting, Copilot PowerShell commands use the invocation
operator and escaped single quotes, and Windows commands quote both absolute
paths even when no spaces occur. Ambiguous Windows expansion characters `%` and
`!`, quotes and line breaks are refused. Codex merge validation now runs before
any installer destination mutation. Doctor recognizes exact installed command
and handler shapes, including when the human diagnostic CLI uses another trusted
Python. Extra operands remain unowned and leave a missing registration. It never
executes these settings or grants diagnostic execution authority.

Generated scanner and standalone diagnostic outputs were refreshed only through
`scripts/generate-hooks.py --write`. Scanner/Guardian policy, candidate inspection,
deny-only diagnostic requests and their authority were not broadened.

## Observed green checks

- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests passed, run alone.
- `rtk proxy python3 scripts/test-hook-diagnostics.py -v`: 8 tests passed.
- `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py -v`: all 12 tests
  passed in 36.543 seconds, including both real installer/registry cases.
- `rtk proxy python3 scripts/test-install-codex-hooks.py`: maintained merge passed,
  including old-interpreter upgrade, exact command pairs, preservation,
  idempotence, malformed-template refusal and write-failure cleanup.
- `rtk proxy python3 scripts/generate-hooks.py --check`: all 38 files current.
- `rtk proxy bash -n scripts/install.sh`: passed.
- `rtk proxy bash scripts/test-install.sh`: passed.
- `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`: all tests passed;
  junction creation was unavailable on this host and explicitly reported.
- `rtk proxy python3 scripts/test-rtk-stable.py -v`: all 12 tests passed.
- `rtk proxy git diff --check`: passed.

The installed-command cases passed for Bash and macOS PowerShell, including
Copilot's actual PowerShell registration command. No hostile sentinel was written.
Actual scanner commands allowed a clean repository and denied an unmistakably
fake credential; Guardian denied a protected force-push. Completed scanner and
Guardian audit records were read from isolated logs. Doctor counted installed
registrations as observed, then counted a registration with an appended operand
as unowned/missing. A repeated install preserved settings exactly. Unsupported
Windows shell characters caused failure with the entire disposable install-home
fingerprint unchanged; PowerShell's own startup caches were isolated outside that
home before taking the fingerprint.

The two new tests extend an existing registered recovery suite; no new test suite
or aggregate registry entry was introduced.

## Limits

Native Windows execution, ACLs, junction behavior and authenticated provider hook
dispatch were unavailable. macOS PowerShell command execution and textual Windows
command rendering do not establish those results. No performance benchmark or
full aggregate run is claimed here. The coordinator owns integration validation,
living-plan reconciliation and the single end-of-session KB maintenance pass.
The installing user still owns trust in the interpreter and installed files;
same-user replacement of those bytes is outside this protection.
