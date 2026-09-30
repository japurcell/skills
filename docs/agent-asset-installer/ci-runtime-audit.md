# Existing CI and runtime test conventions for agent-assets M6

Historical read-only audit of the M5 baseline. The inventory below describes that checkpoint; the M6 changes and remaining gates are recorded first.

## M6 changes and version evidence

`.github/workflows/agent-assets.yml` adds full public-suite jobs on macOS/Linux with Python 3.11 and 3.14. A POSIX producer exports a real installed commit as a Git bundle. Six OS/Python clone jobs download that immutable payload and audit clones with autocrlf true/false before any repair, assert literal text/binary bytes and hashes, run relocated installed shell commands, and require intentionally committed damage to fail audit. The native Windows boundary group checks fail-closed behavior. A separate, explicitly unmet Windows mutation job runs the existing full suite without continue-on-error or filtering; it cannot pass while Windows writes remain unsupported. These jobs are wired, not executed evidence. Existing Windows PowerShell suites remain intact.

Official release pages were fetched on 2026-09-30: [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1), [setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0), [upload-artifact v7.0.1](https://github.com/actions/upload-artifact/releases/tag/v7.0.1), and [download-artifact v8.0.1](https://github.com/actions/download-artifact/releases/tag/v8.0.1). Exact release tags are used in the new workflow. The existing workflow's major-tag pattern is left untouched.

`--group clone` needs no clients or credentials. `--export-clone-bundle PATH` creates its committed payload on a supported POSIX writer; `AGENT_ASSETS_CLONE_BUNDLE` points a consumer at that bundle. Native Windows consumers only clone/audit/execute committed scripts. The no-group command retains all previous public groups and includes clone coverage; Windows native mutation acceptance still requires its real implementation and concurrency/recovery cases.

## Workflows and entry points

- `.github/workflows/ready-ideas-windows.yml:1-32` is the only workflow file in this checkout. It runs on push/PR path filters for `.codex/**`, `.copilot/**`, `.gemini/**`, `hooks/**`, `scripts/**`, and itself, plus manual dispatch. It uses `windows-latest`, `actions/checkout@v7`, and `actions/setup-python@v7` with Python `3.13`. There is no OS/Python matrix and no explicit `autocrlf` checkout setting.
- Windows CI prerequisites are `python`, `git`, `pwsh`, and `rtk` (`ready-ideas-windows.yml:56-62`). RTK is installed by winget and checked for >=0.50.0 and Copilot/Gemini processors (`:33-55`). Steps run generator check, `scripts/test-security-banners.py`, `scripts/test-install.ps1`, and native PowerShell hook suites (`:63-84`). This is focused Windows CI, not the full repository suite.
- The explicit aggregate is `python3 scripts/test-all.py` (`scripts/test-all.py:19-52,155-175`). It includes `python3 scripts/test-agent-assets.py` (`:42`) with Bash, Python, and PowerShell suites. It explicitly rejects Windows (`:184-187`); requires bash, python3, git, jq, flock, sqlite3, and PowerShell 7+ (`:188-199,213-224`); continues after child failures and returns a failing summary if any suite failed (`:228-255`). `--list` lists exact registered commands (`:178-183`).
- Direct entry points: `python3 scripts/test-agent-assets.py` for the Python acceptance suite; `pwsh -NoProfile -File scripts/test-install.ps1` for the separate installer fixture; `python3 scripts/test-all.py --list` to inspect the aggregate registry. Current Windows CI does not run `test-agent-assets.py`.

## Agent-assets Python fixture and coverage

- `scripts/test-agent-assets.py:23-69` uses standard-library unittest, subprocesses the actual CLI, and creates disposable source/target Git repos under temporary paths with spaces. It initializes main, commits a minimal skill and JSON catalog, and checks output bytes, Git metadata, JSON reports, and untouched target files.
- Existing cases cover line-ending attributes, repeat-install no-write behavior, nonportable Windows path strings (CON, colon/stream, trailing dot, traversal), case-folded collisions, and a disposable clone acquisition (`:91-104,208-237,297-306`). These are input coverage, not native-Windows execution. Three race cases are explicitly POSIX-only skips (`:816,879,981`); one Unix file-mode assertion is skipped on Windows (`:202-203`).
- The mutex-holder test selects msvcrt on Windows and fcntl elsewhere (`:1168-1189`), but the aggregate runner is unsupported on Windows and no agent-assets native PowerShell wrapper or Windows workflow step exists here.
- No checked-in workflow or fixture verifies a fresh Windows checkout with `core.autocrlf=true` or a clone configured with autocrlf. Workflow checkout uses defaults; the Python disposable clone test does not assert checkout configuration (`:297-306`). This is a coverage gap relative to the supplied M6 plan.

## Existing PowerShell fixture conventions and limits

- `scripts/test-install.ps1:1-55` is a self-contained PowerShell 7+ fixture: temporary workdir/repo/home, invokes the real installer in a child process, captures stdout/stderr separately, asserts resulting layout/content, and cleans up. Command: `pwsh -NoProfile -File scripts/test-install.ps1`.
- It deliberately prints skips when symlink, hard-link, or junction creation is unsupported (`:632-640,669-689,711-735`). Junction type/target and an unchanged external sentinel are asserted after successful fixture creation (`:737-746`). Unix mode assertions are guarded off on Windows (`:701-704`). macOS PowerShell results are PowerShell-on-macOS evidence only, not native-Windows proof.
- Other Windows-named PowerShell suites are in the aggregate and Windows workflow. Their documented non-Windows runs skip and are syntax-only evidence; see `.agents/memory/testing/powershell.md`. Attribute platform evidence only to actual Windows runner execution.

## M6 reuse and coverage notes

- Keep `test-agent-assets.py` as the cross-platform Python behavior suite and keep explicit registry discipline in `test-all.py`. Native Windows coverage needs an explicit Windows workflow step/wrapper because the aggregate rejects Windows. Do not count macOS PowerShell or skip output as native-Windows evidence.
- Preserve failure visibility: do not turn required platform coverage into a successful skip or filter failing cases; wrappers should propagate child failures. Existing aggregate continues through all suites and fails if any child fails. Optional fixture setup skips are printed by individual tests.
- Reuse fixture patterns: disposable source/target repos, temp paths with spaces, actual CLI subprocess, byte/content and metadata assertions, no-write checks, Git index/source-state comparisons, distinct stdout/stderr, and cleanup. The planned fresh checkout/autocrlf verification should be an explicit fixture/CI operation before repair; current tests do not do this.
- Existing version evidence: Windows workflow requests Python 3.13 and checks PowerShell 7+; aggregate only says Python 3 and checks PowerShell 7+. No Python-minor floor is enforced by the aggregate. Do not infer a new version pin from this audit.
