# T9a: initial macOS security CI wiring

Observed on 2026-10-15 in `/Users/adam/.codex/worktrees/design-b-t9a/skills`, private branch `codex/design-b-t9a`, based on `8d6e27d0524e52531c6774ad1bbee83752048b25`. This task changes only `.github/workflows/hooks-posix.yml` and this evidence. The primary owns plan reconciliation, integration and the coordinated knowledge-maintenance pass. T9b owns later coverage and explicit native capture evidence.

## Job contract

The new `Hook security macOS` workflow uses `macos-latest`, a 30-minute limit, read-only `contents` permissions and checkout without persisted credentials. Push and pull-request filters both include `hooks/**`, all three generated provider roots (`.codex/**`, `.copilot/**`, `.gemini/**`), `scripts/**` and this workflow path; manual dispatch is available. The job has no privileged event, arbitrary external script execution, test skip fallback or continue-on-error step.

It follows the existing Windows workflow's `actions/checkout@v7` and `actions/setup-python@v7` convention. Homebrew installs Git, Bash, jq, PowerShell, Git LFS and stable RTK. Only those formula bin directories enter `GITHUB_PATH`; setup-python runs afterward, ensuring its selected Python 3.13 takes precedence. Python 3.13 is this CI job's target, with no runtime floor change. The preflight requires executable tools, prints their versions, requires PowerShell 7+, requires a stable numeric RTK version >=0.50.0, checks `rtk gain` and requires both Copilot and Gemini hook processors. Git LFS is prepared for later publication tests; no LFS publication suite is claimed here.

After installation, the job writes test homes, XDG directories, temporary files and logs below `$RUNNER_TEMP/hook security`. The space in that path exercises quoting. Disposable Git fixtures created through `TMPDIR` inherit no system/global Git configuration or interactive credential prompting. No real-home deployment or trust/enablement change is performed.

The job runs these exact commands serially, with Bash's failure propagation and RTK proxy preserving each command's output and exit:

```sh
rtk proxy python3 scripts/generate-hooks.py --check
rtk proxy python3 scripts/test-verify-security-fixture-patch.py
rtk proxy python3 scripts/test-hook-diagnostic-recovery.py
rtk proxy python3 scripts/test-security-reporting.py
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh
```

Each scanner shell already runs its provider's capture suite. This workflow adds no duplicate capture invocation and does not refer to unimplemented CLI, status, Git gate, LFS or migration suites. The native Windows workflow, registry and capture test source are unchanged.

## Local validation

Local platform: macOS 26.7.1 arm64; Python 3.14.6 for the full new reporting run and fault controls; Python 3.13.14 for the targeted compatibility checks below; Git 2.54.0 (Apple Git-157); Bash 3.2.57; jq 1.7.1; PowerShell 7.6.7; RTK 0.51.0 with both required processors. Git LFS and actionlint are absent locally. No global dependency was installed for validation.

The repository's vendored PyYAML 6.0.3, loaded explicitly from `scripts/vendor`, parsed the workflow with `BaseLoader` so `on` remains a string. Executed structural assertions required the exact three triggers and filters, read-only permissions, macOS runner, both action versions, checkout credential setting, exact seven serial commands, and absence of continue-on-error. Every `run` block was passed individually to `bash -n`; all ten passed, including the embedded Python heredoc. Final checks repeated Bash parsing after the PATH/order correction. These are local structural/shell checks, not a full GitHub Actions service or actionlint validation.

A disposable tool-resolution check executed the actual bootstrap run block against a private mock Homebrew that only implemented installation success and six formula-prefix responses. A conflicting `python3` in the mocked general Homebrew bin directory would exit 98. After reproducing runner PATH prepends and setup-python's final prepend with the real local 3.13.14 installation, the exact workflow Python version assertion selected `/Users/adam/.pyenv/versions/3.13.14/bin/python3` and passed. The structural check also required bootstrap before setup-python. This proves local ordering/resolution mechanics; it does not execute the hosted setup action or Homebrew downloads. The workflow's unchanged stable-RTK Python block separately passed with real RTK 0.51.0.

The actual prerequisite block was also invoked locally with Python 3.13.14 and the workflow's disposable environment. It exited 1 at missing `git-lfs`; a separate `git lfs version` invocation confirmed the missing executable. This is the intended failing prerequisite behavior, not a passing skip. The Homebrew installation and complete prerequisite success remain hosted-run obligations.

| Executed check | Observed result |
| --- | --- |
| `rtk proxy python3 scripts/test-security-reporting.py` with the exact workflow disposable environment | Exit 0; all 14 tests pass in 71.885 seconds on Python 3.14.6. |
| `rtk proxy python3 scripts/generate-hooks.py --check` after both faults were removed, using Python 3.13.14 | Exit 0; generated hooks current, 38 files. |
| `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py RecoveryTests.test_launch_honors_scan_mode RecoveryTests.test_launch_honors_guard_mode` using Python 3.13.14 | Exit 0; 2 methods pass in 1.342 seconds, covering all 12 provider/mode subcases. |
| `rtk proxy python3 scripts/test-security-reporting.py SecurityReportingTests.test_guardian_invalid_transport_and_nonobject_have_safe_attribution` using Python 3.13.14 | Exit 0; 1 method passes in 0.212 seconds. |

The worktree starts at the exact executable revision validated by [I1](i1-evidence.md). `rtk proxy git diff --exit-code HEAD -- hooks scripts .codex .copilot .gemini` exits 0. Therefore the unchanged complete preflight/recovery and all three scanner shell successes are reused from I1: 22 preflight tests in 89.872 seconds, 15 recovery methods in 63.968 seconds, generated parity of 38 assets, and all three serial provider scanner/capture shells. T9a does not relabel those older Python 3.14.6 results as Python 3.13 or new CI results.

## Deliberate failure controls

Both faults were made only in separate archive extractions from `git archive HEAD`, under writable temporary paths containing spaces. The actual selected job commands ran with the same isolated environment used by the reporting run. No live tracked assertion or generated asset was edited, disabled or weakened.

1. Recovery assertion control: in the disposable copy of `scripts/test-hook-diagnostic-recovery.py`, replace only the first occurrence of `self.assertEqual(rows[0]["mode"], mode)` with `self.assertEqual(rows[0]["mode"], "deliberate_t9a_fault")`. This changes the requested scanner-mode expectation, while retaining the Guardian expectation. Invoke the full exact job command `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py`. It exited 1; all 15 methods ran in 77.302 seconds (77.347 seconds for the command wrapper), with exactly six failures in `test_launch_honors_scan_mode`, one for each provider/block-or-warn pair. Each reports actual `block` or `warn` unequal to the deliberate marker. The isolated source copy was then removed.
2. Generated drift control: in a separate disposable copy, append `\n# deliberate T9a generated drift control\n` to `.codex/hooks/scan-secrets.py`. Invoke the full exact job command `rtk proxy python3 scripts/generate-hooks.py --check`. It exited 1 in 0.269 seconds and printed `.codex/hooks/scan-secrets.py`. The first local harness additionally expected an undocumented `--write` hint and therefore failed its own extra assertion after observing the required command failure. That extra assumption was removed; re-execution of the exact drift command again exited 1 and named the drifted file. The isolated copy was removed. No product change was needed.

Temporary full logs were retained outside Git at `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/t9a local d6zr45k_/` as `security-reporting.log`, `recovery-fault.log`, `drift-fault.log` and `local-prerequisite-failure.log`. Both fault-bearing source copies are gone. The exact mutations, commands and decisive outputs are retained above so acceptance does not depend on temporary log retention.

## Primary sources and limits

The implementation follows GitHub's [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) for path filters, dispatch, read-only permissions and serial steps, the official [checkout documentation](https://github.com/actions/checkout) for `persist-credentials: false`, and the [variables reference](https://docs.github.com/en/actions/reference/workflows-and-actions/variables) for runner-temporary storage. Homebrew's [manual](https://docs.brew.sh/Manpage) documents installation and formula-specific prefixes. Its current [PowerShell formula](https://formulae.brew.sh/formula/powershell), [RTK formula](https://formulae.brew.sh/formula/rtk) and [Git LFS formula](https://formulae.brew.sh/formula/git-lfs) support the selected package commands. Current PowerShell is a formula (`brew install powershell`); the former cask page returned 404. RTK's [official repository](https://github.com/rtk-ai/rtk) also documents Homebrew installation, `rtk --version` and `rtk gain`. The processor requirement is enforced against the installed executable, matching the repository's Windows convention. These pages were checked on 2026-10-15; future package incompatibility fails preflight.

No hosted workflow run, push, PR, branch-protection update, real-home installation, provider-host delivery or native Windows execution occurred. A macOS job plus generic capture PASS output does not independently establish that Darwin's `native_once` process-exhaustion branch executed. T9b must add that explicit marker and later suites after I4; V1 must retain real CI URLs and branch-protection evidence. T9a establishes initial wiring and locally observed failure propagation only.
