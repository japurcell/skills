# Skills

This repository publishes reusable agent assets for Codex, GitHub Copilot, and Gemini:

- **Skills** in `skills/` for reusable task workflows such as `tdd`, `frontend-design`, `create-skill`, `prd`, `code-review`, and `commit`
- **Custom agents** in `agents/` such as `code-architect`, `code-explorer`, `code-reviewer`, and `grader`
- **Copilot global configs** in `.copilot`
- **Gemini global configs** in `.gemini`
- **Codex global hook sources** in `.codex`; generated Codex custom agents are installed outside the repository

Canonical agent-facing guidance lives in `.agents/`.

## Installation

Install or refresh the locally loaded copies with:

```bash
./scripts/install.sh
```

On Windows (or anywhere with PowerShell 7+), use the equivalent PowerShell installer:

```powershell
pwsh scripts/install.ps1
```

It produces the same installed layout as `install.sh`.

The installer copies:

- `skills/` entries into `~/.agents/skills`
- top-level `references/` entries into `~/.agents/references` when that directory exists
- top-level `agents/*.md` files are the canonical custom-agent source for all three providers: Markdown copies go to `~/.gemini/agents` and `~/.copilot/agents`, while generated personal TOML goes to `~/.codex/agents` (or `$CODEX_HOME/agents` when `CODEX_HOME` is set)
- `.copilot/hooks/` entries are copied to `~/.copilot/hooks` when that directory exists
- `.gemini/` contents into `~/.gemini`, then `.gemini/global-settings.json` into `~/.gemini/settings.json`
- `.copilot/copilot-instructions.md` into `~/.copilot/copilot-instructions.md`
- `.codex/hooks/load-required-skills.py` into `~/.codex/hooks`, then safely merges `.codex/global-hooks.json` into `~/.codex/hooks.json`

The Codex merge preserves unrelated hooks. A real configuration change keeps the previous valid file as owner-only `~/.codex/hooks.json.bak`; malformed existing JSON is left unchanged and stops installation. After installing or changing the non-managed hook, open `/hooks` in Codex CLI to review and trust its exact definition.

Workspace directories whose names end with `-workspace` are skipped during installation.

Codex TOML files and `.skills-repo-agents.json` in the selected Codex agents directory are installer-managed. Do not edit them manually: update the canonical top-level Markdown source and rerun an installer. Each source file must be a regular UTF-8 Markdown file with YAML frontmatter containing non-empty `name` and `description`; its body becomes the exact `developer_instructions` value. The Codex converter removes only stale TOML files recorded in its manifest and leaves every unrecorded personal agent untouched.

## CLI dependencies

- Core tooling: `bash`, `python3`, and `git`
- Hook runtime: `python3`, `jq`, and `flock`
- Hook formatting: `npx` (with `oxfmt`) for JS/TS files, `dotnet` SDK for C# files
- Agent shell workflows: `rtk` (recommended wrapper for compact terminal output)

### [Session End Hook](./.copilot/hooks/hooks.json)

For the session-end hook to work, add these lines to your vscode settings.json file:

```json
{
  "terminal.integrated.enableVisualBell": true,
  "terminal.integrated.bellDuration": 500,
  "accessibility.signalOptions.volume": 100,
  "accessibility.signals.terminalBell": {
    "sound": "on"
  }
}
```

## Working in this repo

1. Edit source files in `skills/`, `agents/`, `hooks/`, `.codex/`, `.copilot/`, or `.gemini/`.
2. Rerun `./scripts/install.sh` to refresh the installed local copies.
3. Run `./scripts/test-all.py` for all maintained test suites, or use targeted checks from `.agents/memory/TESTING_STRATEGY.md`.

### Generated provider hooks

The checked-in Python hooks marked `Generated from hooks/families/...` are
runtime-local outputs; do not edit them directly. Change their canonical source
under `hooks/`, regenerate all owned outputs, and verify freshness before
committing:

```bash
python3 scripts/generate-hooks.py --write
python3 scripts/generate-hooks.py --check
python3 scripts/test-generate-hooks.py
```

`--write` is the only generator action that changes files. `--check` is
read-only and exits `1` when an owned output is stale or missing. Both installers
run that check before changing an installation destination; on stale output they
stop and print the `--write` recovery command. Installers copy the checked-in
generated files; they never generate repository sources. The manifest currently
owns 22 executable outputs.

Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews. Those files are benchmark fixtures, not maintained source.

## Authoring notes

Canonical agent-facing authoring rules live in `.agents/instructions/`.

### Skill format

- Use `SKILL.md` as the entry point.
- Start each `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep descriptions concrete and trigger-oriented.

### Agents

- Store each custom agent as a single Markdown file in `agents/`.
- Use YAML frontmatter with `name` and `description`.
- Keep the body focused on execution guidance, output shape, and decision criteria.

## Validation

Run all maintained automated test suites on macOS or Linux with:

```bash
./scripts/test-all.py
./scripts/test-all.py --list
./scripts/test-all.py --help
```

The runner needs Python 3, `bash`, `git`, `jq`, `flock`, `sqlite3`, and PowerShell
7+ (`pwsh`) on `PATH`, plus the usual Unix shell utilities. Install missing tools
with your system package manager before running tests; the runner never installs
dependencies. `--help` and `--list` need only Python. Invoke the script by its path
from any directory; suites run from its containing checkout, which must be writable.

Suites run sequentially and continue after failures. Child stdout and stderr stay
separate and stream live; runner progress, individual failure codes, and the final
suite summary go to stderr. The runner emits plain text without terminal escape
sequences. Suites receive EOF on stdin; the runner never reads your input or prompts.
Host-specific skips remain visible in suite output, so a successful suite run does
not imply that platform-specific tests ran on every host.

Exit codes are `0` for successful suites, `1` for suite failures, `2` for usage,
dependency, or runner errors, `130` for Ctrl-C, `143` for SIGTERM, and `141` if the
runner encounters a broken pipe. Child broken-pipe failures do not stop later suites.
Cancellation signals the active suite and descendants in its process group, allows
five seconds for cleanup, then forces termination. A second Ctrl-C forces termination
immediately. Suites have no default timeout; CI may impose an overall job timeout.

The explicit suite registry includes installer, hook, helper, linter regression,
runner, and model-router grader tests. It excludes lint-only checks, formatting,
live model evaluations, archived tests, and generated fixtures. Native Windows is
not supported by this aggregate command; individual PowerShell tests remain usable.

Run the narrowest command that covers your change. Canonical agent-facing validation routing lives in `.agents/memory/TESTING_STRATEGY.md`.

For hook changes, run `./scripts/install.sh` first and then the targeted regressions listed in `.agents/memory/testing/hooks.md`; the current hook validation set starts with auto-ingest/startup, observability, secrets, tool-guard, and RTK checks.

For the Codex required-skills hook and installer, run:

```bash
bash scripts/test-codex-hooks-startup.sh
bash scripts/test-install.sh
```

When PowerShell 7 is available, also run `pwsh -NoProfile -File scripts/test-install.ps1`.

For the generated Codex custom-agent path, run:

```bash
python3 scripts/test-codex-agents.py
bash -n scripts/install.sh
bash scripts/test-install.sh
pwsh -NoProfile -File scripts/test-install.ps1
./scripts/install.sh
codex --version
```

The installer output identifies the resolved Codex agent destination. Parse an installed TOML file with `python3` and compare `developer_instructions` with the source body when validating a local client.

## Additional docs

- `.agents/memory/ARCHITECTURE.md`
- `.agents/memory/FILE_MAP.md`
- `.agents/memory/TESTING_STRATEGY.md`
- `.agents/instructions/repo.md`
- `.agents/instructions/hooks.md`
- `.agents/instructions/skills.md`
- `.agents/instructions/agents.md`
- `.agents/instructions/scripts.md`
- `.agents/instructions/powershell.md`
