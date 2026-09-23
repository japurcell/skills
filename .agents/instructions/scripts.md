---
type: Agent Instruction
description: Rules and conventions for repository helper scripts under `scripts/` that run in the shell
---

# Shell Scripts Conventions

- Follow existing shebang style for shell helper scripts: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
- Keep scripts directly executable and simple.
- `scripts/test-all.py` owns the explicit registry of maintained test-suite commands. Update it when adding, moving, or removing a suite; exclude `scripts/test-common.sh`, archived tests, generated workspaces, and fixture trees. Keep the runner's CLI regression suite in `scripts/test_test_all.py` registered without recursively invoking the real aggregate run.
- `scripts/generate-hooks.py` owns only the explicit targets in `hooks/manifest.py`. Use `--write` to refresh generated provider-local outputs and `--check` as its no-write freshness gate; both installers run `--check` before destination mutation, but never make installers generate repository sources or edit owned outputs by hand. Freshness always compares content and generated ownership; it checks executable mode only on non-Windows hosts, where POSIX modes are meaningful.
- `scripts/install-rtk-prerelease.py` pins the RTK `dev-0.50.0-rc.451` archive digest for each supported OS/architecture, extracts only the executable after verification, and writes a receipt beside the tag-qualified binary under `~/.agents/rtk/`. Use `--home` and `--archive` for disposable-home proof before touching a real home. Unsupported platforms and checksum mismatches fail without switching stable RTK.
- Shell-focused helper scripts should stay in the repo-root `scripts/` tree and use `scripts/common.sh` for shared repo-root helpers that require `REPO_ROOT`.
- Use stdout for primary or machine-readable output and stderr for status, warnings, progress, and errors so piping and redirection stay predictable.
- Prefer standard-library solutions unless an existing script already implies dependency use.
- `scripts/lint-okf.py` must load PyYAML 6.0.3 from `scripts/vendor/yaml/`, verify both the version and resolved import path, and fail with `OKF900` instead of falling back to a site package. Keep the linter read-only and offline at runtime.
- Register cleanup functions by name (for example, `trap cleanup EXIT`) instead of interpolating temporary paths into trap command strings. Quote the exact `mktemp`-created path and pass `--` to recursive cleanup commands.
- Treat user-facing helper scripts as CLIs: reserve `-h`/`--help` for help, prefer descriptive long flags over multiple positional argument types, and keep interactive prompts optional rather than mandatory.
- `scripts/install-codex-agents.py --source-dir PATH --destination-dir PATH` is the strict public converter for top-level canonical agent Markdown. It must run before provider copy operations in both installers and may remove only manifest-owned Codex TOML outputs.
- Gate decorative terminal behavior on TTY detection; if a script introduces color or spinners, it should also respect `TERM=dumb`, `NO_COLOR`, and a direct opt-out flag.
- **Agent-restricted scripts:** Never run human-only orchestration scripts (such as `import-skill-repos.sh` or `pull-skill-repos.sh`). Agents must strictly run only targeted verification and test scripts (such as `test-*.sh`).
- PowerShell-specific guidance lives in `.agents/instructions/powershell.md`; shell-focused validation lives in `.agents/memory/testing/scripts.md`.
- If the change also affects repo-local hook behavior, read `.agents/instructions/hooks.md` and the matching hook validation docs instead of treating hooks as generic shell scripts.
