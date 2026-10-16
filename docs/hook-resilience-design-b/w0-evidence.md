# W0 native installer repair evidence

W0 is in progress. Native acceptance is not met. Primary owns native snapshot publication, collected run identities, final integration, and the coordinated knowledge pass.

## Public E2E red

[Windows run 38978729929](https://github.com/japurcell/skills/actions/runs/38978729929), job `117234305423`, ran source `d8d58e0814f7c3e1ef4fe766db555eef1bd3aa79` on Windows Server 2025 (10.0.26100), Git 2.56.0.windows.2 and Python 3.13.16. RTK setup, native prerequisites, generated freshness (65), and security banners (14) passed. The actual command `pwsh -NoProfile -File scripts/test-install.ps1` failed at `Expected helper diagnostic and recovery preserved.` between 22:57:54 and 22:58:01 UTC on 2026-10-16.

Read-only `gh run view 38978729929 --repo japurcell/skills --log-failed` confirmed that assertion and exit 1. It did not identify which helper iteration failed or the child's captured stderr. The cause remains unknown.

## First diagnostic candidate

Only `scripts/test-install.ps1` changes behavior: failed helper-process assertions now include the helper basename, installer exit code, and the first 2000 characters of each captured stream. Disposable fixture paths become `<fixture>`. Assertions, expected diagnostics, exit codes, no-stdout requirement, real installer invocation, and preflight home fingerprints remain unchanged. No implementation fix is included.

PowerShell parser-only syntax validation and `git diff --check` passed. These checks run no installer or fixture. Local functional suites, generators and installers are paused for T8b's exclusive test window. No local runtime or native pass is claimed. Primary should publish this frozen candidate's exact tree and return the actual native failure before dependent repair. The branch stays private and unpushed.
