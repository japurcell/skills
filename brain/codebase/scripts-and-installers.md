# Scripts and installers

Read when reviewing, designing, updating, or creating scripts anywhere in this repository, including hooks and skill-bundled scripts.

## Authoring and execution

- All entrypoint scripts throughout the repository must follow CLI design best practices for agents, including but not limited to the requirements below.
- Keep repository-level shell/Python helpers in root `scripts/`, with `#!/usr/bin/env bash` or `#!/usr/bin/env python3`, directly executable and simple. Use [common.sh](../../scripts/common.sh) for shared repo-root helpers requiring `REPO_ROOT`.
- Prefer the standard library unless an existing script already implies dependencies.
- Provide `--help` with usage, options, input/output formats, and exit statuses, without executing normal work. Reserve `-h`/`--help`; prefer descriptive long flags over mixed positional types.
- Handle I/O correctly: read stdin only according to the documented interface; send primary/machine results to stdout and diagnostics, status, progress, warnings, and errors to stderr. Preserve machine-readable output and host protocol contracts.
- Use predictable, documented exit statuses and actionable errors. Support noninteractive execution without unexpected prompts; keep interactive prompts optional.
- Handle malformed input, EOF, broken pipes, and cancellation predictably, with appropriate cleanup.
- Register cleanup functions by name, for example `trap cleanup EXIT`; quote the exact `mktemp` path and use `--` for recursive cleanup.
- Gate decorative color/spinners on TTY detection and respect `TERM=dumb`, `NO_COLOR`, and a direct opt-out flag.
- Never execute human-only `import-skill-repos.sh` or `pull-skill-repos.sh`. Agents use targeted verification and test scripts.
- Use [PowerShell conventions](powershell-installers.md) for `scripts/*.ps1`. For hook changes also read [hook ownership](hooks.md) and matching [hook validation](hook-testing.md); skill helpers also use the owning skill's narrow validation.

## Registry and installation invariants

- [test-all.py](../../scripts/test-all.py) owns the explicit maintained-suite registry. Update it when suites are added/moved/removed; exclude helpers such as `test-common.sh`, archived tests, generated workspaces, and fixture trees. Keep `test_test_all.py` registered without recursively running the real aggregate suite.
- [generate-hooks.py](../../scripts/generate-hooks.py) owns only [manifest targets](../../hooks/manifest.py). Refresh with `--write`; use read-only `--check` for freshness. Installers check before destination mutation and never generate repository sources; never hand-edit owned outputs. Check content/ownership everywhere and executable modes only on hosts where POSIX modes are meaningful.
- Both installers preflight [configure-rtk.py](../../scripts/configure-rtk.py) `--check` before installed-file writes. After hook freshness passes, configure stable RTK 0.50.0 or newer; change only `hooks.suppress_hook_warning`, back up changed existing TOML, and leave ambiguous or modified legacy files for manual review. Verify with `--home` in disposable paths, never the actual home.
- Run [install-codex-agents.py](../../scripts/install-codex-agents.py) `--source-dir PATH --destination-dir PATH` before provider copies. Remove only manifest-owned Codex TOML outputs.
- Preflight [install-provider-hooks.py](../../scripts/install-provider-hooks.py) `--check` for both Copilot and Gemini before any destination mutation. Exclude hook configs from bulk and mode copying; merge maintained entries with user settings and unowned handlers, including retired registrations left for manual cleanup.
- Malformed/ambiguous JSON and linked configuration parents stop the entire installation before copying assets. Never chmod existing configuration through a hard link: atomically replace with owner-only independent bytes when link count or mode requires repair. Preserve unrelated configuration, unmanaged agents, and runtime logs; repeated installs must converge.
- Author/test changes use [script validation](script-testing.md) and [installer acceptance fixtures](installer-testing.md).

## Timing probes

- [benchmark-high-rate-hooks.py](../../scripts/benchmark-high-rate-hooks.py) uses disposable Git/home/log/RTK paths and direct provider JSON entrypoints, without installing hooks or invoking provider CLIs. Whole-subprocess timing does not measure provider delivery.
- Run timing probes sequentially on frozen source, with no concurrent tests, generators, or benchmarks. Serialize generator/installer suites that mutate shared fixtures. Retain failed observations; optional ablations are separate from [security acceptance evidence](security-testing.md).

Evidence: restored shell policy from `.agents/instructions/scripts.md` at `092038394a2e3bb0cc21fffdec2eb60a12cece29`, checked against linked sources plus [Bash](../../scripts/install.sh)/[PowerShell](../../scripts/install.ps1) preflight order on 2026-10-21. Recheck when CLIs, ownership, preflights, or benchmark methodology change. Inspection does not prove successful installed/native delivery or performance.
