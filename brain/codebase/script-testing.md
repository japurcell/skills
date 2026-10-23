# Script validation and fixture contracts

## Narrow checks

- Use syntax check plus the smallest relevant maintained suite; discover commands with [test-all.py](../../scripts/test-all.py) `--list`/`--help` rather than discovering fixture/archive tests. Apply [validation evidence limits](testing.md).
- Generated-hook CLI: `rtk proxy python3 scripts/test-generate-hooks.py` then `rtk proxy python3 scripts/generate-hooks.py --check`. Preserve deterministic rendering, freshness, ownership, modes, and transactional recovery; `--check` stays read-only.
- The generator suite's `snapshot(ROOT)` includes the entire checkout, including untracked files. Freeze source and evaluation artifacts during that suite, or run it in an isolated frozen copy. Concurrent edits invalidate its read-only assertions and can make formatting a large dictionary diff consume gigabytes of memory. After an interrupted mutation fixture, restore outputs with `scripts/generate-hooks.py --write` and rerun affected installer checks. Observed through the aggregate runner on 2026-10-22; isolated generator (27 cases) and RTK installer (12 cases) reruns passed.
- A frozen checkout used for release verification must retain historical Git objects required by the suite. A fresh fixture commit with copied files cannot satisfy fixed `--baseline-ref` checks; preserve the object history or run that suite in the original checkout.
- RTK configuration/installer preflight: `rtk proxy python3 scripts/test-rtk-stable.py`; native proof uses [the dedicated Windows RTK suite](powershell-installers.md#fixture-isolation-and-verification) with real stable RTK.
- Aggregate runner: `rtk proxy python3 scripts/test_test_all.py` uses temporary checkouts and substituted suite/tool executables at the public process boundary, without the full suite toolchain or recursive real aggregate execution. Preserve registry completeness, file-based skill paths, preflight, stdin/stream separation, aggregate exits, broken pipes, and cancellation. Run full integration only with prerequisites available.
- Bash installers use [installer validation](installer-testing.md). Addy installer: `rtk proxy bash -n scripts/addy-install.sh` and `rtk proxy bash scripts/test-addy-install.sh`.
- Helper modules: `rtk proxy python3 scripts/test_helpers.py`; for import/resource-cleanup changes use `rtk proxy python3 -W error scripts/test_helpers.py`.
- Root helpers: `rtk proxy bash scripts/test-repo-root.sh`; expected roots use physical fixture `pwd -P` on macOS (`/var` and `/private/var` may alias), retaining both Git-root and fallback cases.
- PowerShell helpers also use [PowerShell checks](powershell-installers.md); hook helpers use [hook tests](hook-testing.md); skill helpers use their owning skill's narrow checks after the script check.

## Fixtures that must remain meaningful

- Disposable Git commits set fixture identity and `-c commit.gpgsign=false`; never change user Git configuration.
- Cancellation descendants inherit output pipes. Assert bounded `communicate()` reaches EOF from descendants as well as the runner before cleanup. Cleanup-only kills occur after assertions and cannot make a leaked descendant pass. Cover graceful shutdown and forced termination after the suite leader exits in [test_test_all.py](../../scripts/test_test_all.py).
- Imported provider helpers need isolated registered package/module specs; Codex helpers without `__init__.py` need a namespace-package spec. Put logs/audit files and rotation companions under writable `TemporaryDirectory` fixtures; patch locations rather than writing protected source or installed trees. See [test_helpers.py](../../scripts/test_helpers.py).
- Keep [test-common.sh](../../scripts/test-common.sh) `mock_bin` on `printf "%b\n"` so escaped newlines produce executable mocks.
- Serialize generator and installer suites that mutate shared fixture files. Run deadline-sensitive scanner and benchmark checks without competing heavyweight suites; fake-provider tests can still consume the same CPU and process budget. Preserve failures and report missing prerequisites as errors.

Evidence: restored `.agents/instructions/testing/scripts.md` policy at `092038394a2e3bb0cc21fffdec2eb60a12cece29`; linked test seams and [suite registry](../../scripts/test-all.py) checked 2026-10-21. Recheck when fixtures, public CLIs, registry ownership, or process cleanup changes. Source inspection does not replace running the selected suite or native/provider proof.
