# ExecPlan: Windows Hook Fixes

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

## Purpose / Big Picture

This plan aims to resolve several critical hook execution issues on Windows. Specifically, it will:
1. Eliminate the PowerShell `ParserError` at Gemini CLI startup caused by `$GEMINI_PROJECT_DIR` interpolation immediately followed by a forward slash `/` (interpreted as division).
2. Fix Copilot hook execution on Windows by adding the `"powershell"` key with explicit `python \"...\"` invocation, allowing hooks like `load-required-skills.py` to run.
3. Clean up the installed `$HOME/.gemini/` layout by ensuring `global-settings.json` and local `settings.json` are not left over or incorrectly copied to the user's home directory.

After implementation, a Windows user will have a fully functioning, warning-free Gemini CLI startup and operational Copilot/VS Code hooks that populate `scan.log`, `guard.log`, and `audit.log` correctly without manual setup.

## Progress

- [x] (2026-09-02 08:15Z) [milestone-1] Fix PowerShell Parser Error in `.gemini/settings.json`.
- [x] (2026-09-02 08:20Z) [milestone-2] Fix Copilot Windows execution by adding `"powershell"` key to `.copilot/hooks/hooks.json`.
- [x] (2026-09-02 08:25Z) [milestone-3] Exclude/clean `global-settings.json` and local `settings.json` in `install.ps1` and `install.sh`.
- [x] (2026-09-02 08:35Z) [milestone-4] Verify installation cleanliness and live hook execution.
- [x] (2026-09-02 08:45Z) [milestone-5] Add explicit Python unit test coverage for helper changes.

## Surprises & Discoveries

- Discovery: Running the python hook scripts manually from the command line blocks on reading `sys.stdin` (waiting for input payload), which is the expected behavior when stdin is not closed.
- Discovery: Git Bash (`bash`) is fully available and can execute `.sh` test scripts directly on the Windows host.
- Discovery: Python's `json.dumps` with `ensure_ascii=False` crashes with a `'charmap' codec can't encode character '\u2192'` error on Windows because Windows command streams default to CP1252 (charmap) encoding instead of UTF-8, and `→` exists in the loaded skill files. Resolved by programmatically reconfiguring `sys.stdout` to use `utf-8` encoding inside `emit_json`.
- Discovery: The Gemini CLI automatically wraps `$GEMINI_PROJECT_DIR` in single quotes when interpolating it on Windows. When combined with sub-paths (e.g. `'D:\Projects\personal\skills'/.gemini/...`), PowerShell splits the string into two separate tokens or Python fails to locate the script due to the literal single quotes. Resolved by switching `.gemini/settings.json` to use clean relative paths starting with `python .gemini/hooks/scripts/...py` which execute correctly relative to the workspace root.
- Discovery: When Copilot / VS Code runs hooks on Windows using a POSIX runtime (like WSL2), the `cwd` (current working directory) is passed as a Windows-style path (e.g., `D:\Projects\personal\skills`). Since the Python process is POSIX-based, it treats this Windows path as a relative path, creating a folder literally named `D:\Projects\personal\skills` (using Unicode-translated characters like `` and `` under MSYS2/GitBash or normal slashes in WSL) under the process's working directory. Resolved by implementing a path conversion helper `convert_windows_path_to_posix` in `helpers/common.py` that translates Windows drives and paths (e.g., `D:\...` to `/mnt/d/...` or `/d/...`) when running under POSIX runtimes on Windows.

## Decision Log

- Decision: Wrap paths in escaped double quotes `\"...\"` and prefix with `python`.
  Rationale: Follows the established best practice documented in `.agents/memory/known-issues/hooks.md` under "PowerShell Parser Error on $HOME in Command Hooks (Windows)" to avoid PowerShell parsing `/` as a division operator and to bypass Windows registry file association limitations.
  Date/Author: 2026-09-02 / Gemini CLI
- Decision: Use relative paths `python .gemini/hooks/scripts/...py` in `.gemini/settings.json` instead of `$GEMINI_PROJECT_DIR`.
  Rationale: Completely sidesteps automatic quoting, backslash/forward-slash conversion, and path-splitting bugs in Windows shells without losing location robustness, since hooks always run relative to the workspace root.
  Date/Author: 2026-09-02 / Gemini CLI
- Decision: Add `sys.stdout.reconfigure(encoding="utf-8")` inside `emit_json` in helper modules.
  Rationale: Forces Python standard output streams to utilize UTF-8 on Windows, preventing charmap (CP1252) encoding crashes when serializing non-ASCII Unicode characters (like `→` or arrows) to JSON stdout.
  Date/Author: 2026-09-02 / Gemini CLI
- Decision: Convert Windows drive paths to POSIX style in Python scripts if running on POSIX runtimes under Windows.
  Rationale: Ensures absolute Windows workspace paths (like `cwd`) passed by the IDE to Linux/WSL/GitBash hook subprocesses are correctly mapped to `/mnt/...` or `/` mount paths, preventing them from being treated as relative folders containing literal backslashes and colons.
  Date/Author: 2026-09-02 / Gemini CLI
- Decision: Add explicit Python unit tests (`scripts/test_helpers.py`) for all changes.
  Rationale: Fully tests path conversion (`convert_windows_path_to_posix`) and `emit_json` Unicode serialization safety across both native Windows and POSIX/WSL platforms to guarantee absolute robustness.
  Date/Author: 2026-09-02 / Gemini CLI

## Outcomes & Retrospective

All milestones were successfully implemented, installed, and validated on Windows.
1. The PowerShell `ParserError` and Python module/path splitting errors at Gemini CLI startup were completely resolved by updating `.gemini/settings.json` to use clean relative paths.
2. Copilot hook execution was enabled on Windows by adding the `"powershell"` key with identical explicit `python` wrapping to `.copilot/hooks/hooks.json` and `.copilot/hooks/rtk-rewrite.json`.
3. Charmap encoding crashes on non-ASCII characters (like `→` arrows in `GEMINI.md`) were permanently resolved by forcing UTF-8 stdout streams in `helpers/common.py`.
4. Windows absolute workspace paths passed as `cwd` to POSIX-based shells (such as WSL or GitBash) are gracefully translated to proper absolute POSIX paths, eliminating virtual translation folder pollution.
5. Clean, explicit unit test coverage was added in `scripts/test_helpers.py` and validated on both Windows and POSIX shells.
6. Installation scripts (`install.ps1` and `install.sh`) were cleaned up to prevent leaving unneeded config files (`global-settings.json` and local project `settings.json`) in `$HOME/.gemini/`.
7. Verification confirmed that the environment is fully clean, and all hook tests pass correctly.

## Context and Orientation

On Windows, the default execution environment for shell-based commands is PowerShell (`powershell.exe`). 

1. **The Division Parser Error**: When Gemini CLI replaces `$GEMINI_PROJECT_DIR` in a string like `$GEMINI_PROJECT_DIR/.gemini/hooks/scripts/auto-ingest.py`, it interpolates it with single quotes (e.g. `'D:\Projects\personal\skills'`). In PowerShell, a string followed immediately by `/` (e.g., `'path'/foo`) is interpreted as dividing the string, triggering a `ParserError`. Wrapping the entire command in double quotes and prefixing with `python` (e.g., `python \"$GEMINI_PROJECT_DIR/...\"`) forces PowerShell to treat the path as an argument, bypassing the division parser.
2. **Copilot Platform Suffixes**: In `.copilot/hooks/hooks.json`, hook objects only contain a `"bash"` key. On Windows, Copilot CLI/VS Code requires a `"powershell"` key to execute. Without it, the hooks do not fire, resulting in empty or missing logs.
3. **Installer Pollution**: Both `scripts/install.ps1` and `scripts/install.sh` copy the whole `.gemini` folder recursively, which includes both `global-settings.json` and the local `settings.json`. They then overwrite `settings.json` with `global-settings.json`. This leaves `global-settings.json` behind in `$HOME/.gemini/`.

## Plan of Work

### Milestone 1: Fix PowerShell Parser Error in `.gemini/settings.json`
Status: done
Acceptance: met

Modify `D:\Projects\personal\skills\.gemini\settings.json` to prefix commands with `python` and wrap the interpolated paths in escaped double quotes.

### Milestone 2: Fix Copilot Windows execution by adding `"powershell"` key to `.copilot/hooks/hooks.json`
Status: done
Acceptance: met

Modify `D:\Projects\personal\skills\.copilot\hooks\hooks.json` to add `"powershell"` keys mimicking the `"bash"` keys but using the `python \"...\"` format.

### Milestone 3: Exclude/clean `global-settings.json` and local `settings.json` in `install.ps1` and `install.sh`
Status: done
Acceptance: met

Modify `scripts/install.ps1` and `scripts/install.sh` to remove `global-settings.json` and the copied local `settings.json` from the destination `.gemini` directory before copying the correct global configuration.

### Milestone 4: Verify installation cleanliness and live hook execution
Status: done
Acceptance: met

Run the PS1 installer, verify `$HOME/.gemini/` has no `global-settings.json`, and run dry tests to confirm both runtime environments load hooks correctly.

## Concrete Steps

1. Edit `.gemini/settings.json` with the `replace` tool.
2. Edit `.copilot/hooks/hooks.json` with the `replace` or `write_file` tool.
3. Edit `scripts/install.ps1` with the `replace` tool.
4. Edit `scripts/install.sh` with the `replace` tool.
5. Execute `powershell.exe -NoProfile -Command ".\scripts\install.ps1"`.
6. Inspect `$HOME/.gemini/` contents.

## Validation and Acceptance

- Clean installation: running `.\scripts\install.ps1` completes successfully, and `$HOME/.gemini/` contains only `settings.json` (no `global-settings.json`).
- Startup: Launching Gemini CLI in YOLO mode has no startup parser warning for `auto-ingest-sources`.
- Copilot logs: Running Copilot hooks creates `scan.log` and `guard.log` correctly inside the `.copilot` directory structure.

## Idempotence and Recovery

All edits are fully idempotent and can be re-run safely. If a hook breaks, we can restore from Git.
