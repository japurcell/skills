# Native Windows provider assertion repair

This record covers W5 in `ExecPlan.md`. It retains the local reproduction and repair evidence for Windows run [38763664559](https://github.com/japurcell/skills/actions/runs/38763664559), which failed at `e8742b79ad8e0e55ac0543f315a4222640dfc19c` in `Test-ProviderRefreshPreservesRetiredAndUserEntries` with zero maintained Copilot handlers counted.

## Reproduction

At base `af323806e36e56e1fef785b96c36c77c721e23ae`, only the disposable home in `Test-ProviderRefreshPreservesRetiredAndUserEntries` was changed from `home` to `home with spaces`. The original assertion and all production files were unchanged for this run.

Command from the repository root:

```text
rtk proxy pwsh -NoProfile -File scripts/test-install.ps1
```

Observed result: exit 1, with the same assertion as native Windows:

```text
Expected one maintained Copilot handler.
Expected: 1
Actual:   0
```

The failure is in the assertion. `scripts/trusted_hook_launch.py` serializes the Bash launch with `shlex.join`; a script path containing spaces is quoted, so the previous `-clike '*tool-guard.py'` suffix pattern did not match the closing quote. The native run and local reproduction both stop at the handler-count assertion.

## Repair and green evidence

The fixture permanently uses a space-containing disposable home. It locates maintained handlers by the exact installed `tool-guard.py` path, then still requires exactly one. It parses that handler with Python's standard `shlex` parser and asserts five launch operands, an absolute interpreter, the isolated flags `-I -S -B`, and the expected installed script. It also verifies the target exists. The existing retired-registration, user-setting, custom-handler, and repeat-install fingerprint assertions remain in the same test.

On macOS 26.7.1 (build 25G241), Darwin arm64, PowerShell 7.6.7, Python 3.14.6, and RTK 0.51.0, these checks passed from the repository root:

```text
rtk proxy pwsh -NoProfile -Command '$tokens = $null; $errors = $null; [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/test-install.ps1"), [ref]$tokens, [ref]$errors) | Out-Null; if ($errors.Count -gt 0) { $errors; exit 1 }'
```

Exit 0. The PowerShell parser reported no syntax errors.

```text
rtk proxy python3 scripts/generate-hooks.py --check
```

Exit 0: `Generated hooks are current (38 files).`

```text
rtk proxy pwsh -NoProfile -File scripts/test-install.ps1
```

Exit 0: `test-install.ps1: all tests passed.` The suite reported `Skipping: junction creation is not supported on this host.` The new command assertion passed, establishing that the installed quoted command parses to the absolute interpreter, isolated flags, and expected script path. Native Windows junction behavior and the complete Windows workflow remain for W6.

## Input hashes and limits

SHA-256 hashes at the local green result:

- Red-state `scripts/test-install.ps1` (space-containing home with original assertion): `b8cf808e0550171ae0679c42ee2d38c3c43d2bbf5375e1ca28429df657fdc2d6`.
- Green `scripts/test-install.ps1`: `7e173a09befb689de12fda1d1a5e10ca93b745be0be9952c8e06ce6969ba31f8`.
- Unchanged `scripts/trusted_hook_launch.py`: `74d224f7498a5191c23d351f11f03cb72301387daf631555c487616db2392079`.
- Unchanged `scripts/install-provider-hooks.py`: `c872999e10ace2033ea91248c83cd18b292c75a4e8dd64d893c06402c2feb3ae`.

The red-state test hash is reconstructed from the green file by replacing only the new assertion block with the original assertion; the red command was run before any assertion change. No production source was modified. Local macOS success does not establish native Windows acceptance, and junction coverage skipped on this host. W6 must rerun the complete Windows workflow on the integrated revision.
