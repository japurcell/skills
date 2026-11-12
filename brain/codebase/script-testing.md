# Script validation and fixture contracts

## Narrow checks

- Restore and hash snapshot files from raw Git blob bytes. Use `rtk proxy git show` or `git show` through subprocess inside `rtk proxy python3`. Display-filtered `rtk git show` output can differ from the blob and must not establish file identity or restoration bytes.

- Use syntax check plus the smallest relevant maintained suite; discover commands with [test-all.py](../../scripts/test-all.py) `--list`/`--help` rather than discovering fixture/archive tests. Apply [validation evidence limits](testing.md).
- Generated-hook CLI: `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py` then `rtk proxy python3 scripts/generate-hooks.py --check`. Preserve deterministic rendering, freshness, ownership, modes, and transactional recovery; `--check` stays read-only.
- RTK configuration/installer preflight: `rtk proxy python3 scripts/tests/installers/test-rtk-stable.py`; native proof uses [the dedicated Windows RTK suite](powershell-installers.md#fixture-isolation-and-verification) with real stable RTK.
- Model router: `rtk proxy python3 skills/default/subagent-model-router/scripts/test_route.py` exercises the public JSON CLI and copied bundle. Use the direct registered command for focused runs; `test-all.py` has `--list` but no suite selector. Pair suite-registration changes with the aggregate-runner regression below.
- Aggregate runner: `rtk proxy python3 scripts/tests/runner/test_test_all.py` uses temporary checkouts and substituted suite/tool executables at the public process boundary, without the full suite toolchain or recursive real aggregate execution. Preserve registry completeness, file-based skill paths, preflight, stdin/stream separation, aggregate exits, broken pipes, and cancellation. Run full integration only with prerequisites available.
- Bash installers use [installer validation](installer-testing.md). Addy installer: `rtk proxy bash -n scripts/addy-install.sh` and `rtk proxy bash scripts/tests/installers/test-addy-install.sh`.
- Helper modules: `rtk proxy python3 scripts/tests/tooling/test_helpers.py`; for import/resource-cleanup changes use `rtk proxy python3 -W error scripts/tests/tooling/test_helpers.py`.
- Root helpers: `rtk proxy bash scripts/tests/tooling/test-repo-root.sh`; expected roots use physical fixture `pwd -P` on macOS (`/var` and `/private/var` may alias), retaining both Git-root and fallback cases.
- PowerShell helpers also use [PowerShell checks](powershell-installers.md); hook helpers use [hook tests](hook-testing.md); skill helpers use their owning skill's narrow checks after the script check.

## Fixtures that must remain meaningful

- Fake provider envelopes must carry results from real underlying tool operations when those operations are the behavior under test. Execute the public CLI/helper and capture actual argv, exit, state and file readback; invent only the provider transport envelope, not positive component outputs.
- Keep offline fixture coverage distinct from native/provider proof. Ground required execution and identity evidence in retained provider output; a passing fixture cannot establish host behavior.
- A benchmark root selector does not establish delegated child selectors. Bind claims to actual session/child context and keep state generations separated across resets. Preserve original automated outcomes separately from a versioned independent native-evidence assessment.

- Disposable Git commits set fixture identity and `-c commit.gpgsign=false`; never change user Git configuration.
- Cancellation descendants inherit output pipes. Assert bounded `communicate()` reaches EOF from descendants as well as the runner before cleanup. Cleanup-only kills occur after assertions and cannot make a leaked descendant pass. Cover graceful shutdown and forced termination after the suite leader exits in [test_test_all.py](../../scripts/tests/runner/test_test_all.py).
- Imported provider helpers need isolated registered package/module specs; Codex helpers without `__init__.py` need a namespace-package spec. Put logs/audit files and rotation companions under writable `TemporaryDirectory` fixtures; patch locations rather than writing protected source or installed trees. See [test_helpers.py](../../scripts/tests/tooling/test_helpers.py).
- Keep [test-common.sh](../../scripts/tests/support/test-common.sh) `mock_bin` on `printf "%b\n"` so escaped newlines produce executable mocks.
- Serialize generator and installer suites that mutate shared fixture files. Preserve failures and report missing prerequisites as errors.

Evidence: restored `.agents/instructions/testing/scripts.md` policy at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; linked test seams and [suite registry](../../scripts/test-all.py) checked 2026-10-21. Recheck when fixtures, public CLIs, registry ownership, or process cleanup changes. Source inspection does not replace running the selected suite or native/provider proof.

Router extraction targeted evidence, 2026-11-03: parent confirmed 33 CLI tests and 14 registry tests passed after final corrections, skill/source validation passed, and independent final review had no remaining findings. The optional full aggregate was cancelled with exit 130 and remains unverified; the parent confirmed no matching runner remained. These targeted checks do not establish full-suite success. Durable architecture and guardrails live in the router bundle and canonical exec-plans skill rather than duplicated brain prose.
