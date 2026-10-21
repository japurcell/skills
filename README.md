# Skills

This repository publishes reusable agent assets for Codex, GitHub Copilot, and Gemini:

- **Skills** in category folders under `skills/`, with the default bundles in `skills/default/`, for reusable task workflows such as `tdd`, `frontend-design`, `create-skill`, `prd`, `code-review`, and `commit`
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

Both commands install default skills by default. Add `--forest-service` (or
its alias `--fs`) to include Forest Service skills. To force a default-only
install even when the environment opts in, use `--no-forest-service`:

```bash
./scripts/install.sh --forest-service
./scripts/install.sh --no-forest-service
INSTALL_FOREST_SERVICE_SKILLS=true ./scripts/install.sh
```

```powershell
pwsh -NoProfile -File scripts/install.ps1 --forest-service
pwsh -NoProfile -File scripts/install.ps1 --no-forest-service
$env:INSTALL_FOREST_SERVICE_SKILLS = 'true'; pwsh -NoProfile -File scripts/install.ps1
```

Without a selection flag, set `INSTALL_FOREST_SERVICE_SKILLS` to `1` or
`true` to include Forest Service skills, or `0` or `false` to install only
default skills. Values must match these strings exactly, ignoring case; unset
or empty means default only. An explicit selection flag takes precedence over
this variable. The Forest Service category currently has no skills, so
opting in makes no additional skill copies today. Both `skills/default/` and
`skills/forest-service/` source directories must exist; each skill directory
must contain `SKILL.md`. The installer places selected skills directly in
`~/.agents/skills/<name>/`. A later default-only install leaves previously
installed Forest Service skills in place.

Use `-h` or `--help` to print usage to stdout and exit 0 without installing.
Successful installation exits 0. Invalid or conflicting
arguments, or an invalid nonempty environment value when no selection flag is
given, print a diagnostic to stderr and exit 2. Missing category directories,
skill directories without `SKILL.md`, and duplicate skill directory names
across categories print a diagnostic to stderr and exit 1. Restore the missing
category, add the reported `SKILL.md`, or rename one of the conflicting
directories, then rerun the installer. Other installation failures also exit
1 with a diagnostic. Successful install status goes to stderr; help goes to
stdout.

The installer copies:

- `skills/default/` entries into `~/.agents/skills`
- top-level `references/` entries into `~/.agents/references` when that directory exists
- top-level `agents/*.md` files are the canonical custom-agent source for all three providers: Markdown copies go to `~/.gemini/agents` and `~/.copilot/agents`, while generated personal TOML goes to `~/.codex/agents` (or `$CODEX_HOME/agents` when `CODEX_HOME` is set)
- `.copilot/hooks/` entries are copied to `~/.copilot/hooks` when that directory exists
- `.gemini/` contents into `~/.gemini`, then `.gemini/global-settings.json` into `~/.gemini/settings.json`
- `.copilot/copilot-instructions.md` into `~/.copilot/copilot-instructions.md`
- maintained `.codex/hooks/` scripts for startup and security into `~/.codex/hooks`, then safely merges their `SessionStart`, `PreToolUse`, and `Stop` registrations from `.codex/global-hooks.json` into `~/.codex/hooks.json`

Both installers require stable Rust Token Killer (RTK) 0.50.0 or newer on `PATH` before changing installed files. They set only `[hooks] suppress_hook_warning = true` in the user's RTK config (`~/Library/Application Support/rtk/config.toml` on macOS, `~/.config/rtk/config.toml` on Linux, or `%APPDATA%\rtk\config.toml` on Windows). An existing config is backed up as `config.toml.bak` before a change; a correct config stays byte-identical. An existing backup or ambiguous TOML stops the install for manual review. This account-wide setting suppresses the false missing-hook advisory for explicit commands while leaving other RTK diagnostics visible. The installers do not download RTK. They remove old prerelease files only when ownership and content or receipt hashes match, and report modified files for manual review. Copilot and Gemini still use automatic RTK forwarding.

The Codex merge preserves unrelated hooks. A real configuration change keeps the previous valid file as owner-only `~/.codex/hooks.json.bak`; malformed existing JSON is left unchanged and stops installation. After installing or changing the non-managed hook, open `/hooks` in Codex CLI to review and trust its exact definition.

### Explicit secret checks and Git gates

Tool Guardian checks dangerous tool actions when enabled. Its registration is
currently disabled; source validation does not re-enable an installed hook. Native
file contents and complete patches have a 1 MiB aggregate decoded UTF-8 budget.
Recognized quoted shell heredocs and narrow literal Python file writers use that
content budget after proving the body is inert in its execution context. Unknown
shapes and unproved executable input retain strict inspection and a 32 KiB
normalized executable budget. Limits remain finite; incomplete inspection denies
in both block and warn modes. Limit messages identify the measured quantity,
threshold and unit.

Secret scanning runs only when explicitly requested or when an explicitly installed
Git gate runs. Reads, repairs and ending a turn do not trigger a secret scan.

End Turn displays the last saved scan result, its time and scope. Missing, stale,
corrupt or unavailable status does not block completion. Status never scans,
retries, starts background work or authorizes a later commit or push.

Both provider installers install the standalone CLI without adding it to PATH or
activating repository Git gates. On macOS/POSIX, use the installed command directly:

```sh
"$HOME/.local/lib/scan-secrets/scan-secrets" check --repo .
"$HOME/.local/lib/scan-secrets/scan-secrets" check --repo . --scope index --json
"$HOME/.local/lib/scan-secrets/scan-secrets" status --repo .
"$HOME/.local/lib/scan-secrets/scan-secrets" help hooks
```

`check` inspects pending worktree changes by default; `--scope index` inspects
staged versions. It saves historical status outside the repository and installed
executable bundle. Checks return `0` for complete clean, `1` for findings, `2` for
incomplete inspection, `3` for invalid invocation and `130` for cancellation.
Findings and incomplete inspection include recovery advice. Repair the reported
problem, then rerun the explicit command. Editing remains available.

To activate gates for one repository, first preview the change, then install it.
Select a trusted direct Git executable; on macOS the Command Line Tools path is
usually the following:

```sh
"$HOME/.local/lib/scan-secrets/scan-secrets" hooks install --repo . --git /Library/Developer/CommandLineTools/usr/bin/git --dry-run --json
"$HOME/.local/lib/scan-secrets/scan-secrets" hooks install --repo . --git /Library/Developer/CommandLineTools/usr/bin/git
```

Pre-commit checks each changed staged file in full using Git's selected index.
Pre-push independently checks outgoing history and messages, including credentials
removed by a later commit. A saved clean checkpoint never replaces either check.
A failed gate blocks that Git operation; fix the content or infrastructure and
retry. Existing hooks run in the preserved order after required checks. Supported
LFS delivery inspects verified local payloads before upload and requires an
explicit pinned Git LFS 3.8.0 tool and supported endpoint binding; use
`hooks install --help` for those options and unsupported configurations.

To restore the original repository hook binding:

```sh
"$HOME/.local/lib/scan-secrets/scan-secrets" hooks uninstall --repo . --git /Library/Developer/CommandLineTools/usr/bin/git --dry-run --json
"$HOME/.local/lib/scan-secrets/scan-secrets" hooks uninstall --repo . --git /Library/Developer/CommandLineTools/usr/bin/git
```

Repository gates require trusted interpreter, runtime, Git and data paths.
Group/other-writable ancestry is refused, except supported root-owned sticky
temporary directories. Use a reviewed private installation if a system package
fails these checks.

Installation preserves owned backups, uses locks for cooperating writers and
refuses ownership drift. It does not protect against arbitrary simultaneous edits
by another program. Review an ambiguous backup or orphan lock before retrying;
do not delete unrelated hooks. Provider migration retires only exactly owned old
scanner registrations and preserves unrelated handlers and existing disable/trust
choices. Review and trust changed definitions through the provider's normal flow.

The complete checkpoint/commit/push workflow is validated on macOS. Existing
Windows provider hooks have separate native tests. Windows repository-gate
activation is unsupported and refuses before mutation. Do not infer Linux or
native Windows gate support from portable source alone. Windows standalone
launchers live under `%LOCALAPPDATA%\Programs\scan-secrets`; invoke the
PowerShell launcher with `pwsh -NoProfile -File`.

Checkpoint defaults are 4096 objects, 64 MiB candidate content and 30 seconds.
Publication defaults are 20000 objects, 256 MiB candidate content and 120 seconds.
Explicit budget files retain finite capture and temporary-storage limits. Limit,
Git, audit and cancellation failures remain incomplete, never clean. Reports
sanitize labels and omit arbitrary file bodies. No scan downloads missing content.

### Security fixture patches

For a proposed text-fixture repair, verify the patch before applying it with your
normal patch tool. Run from the repository root, name each existing fixture with
`--path`, and select the reviewed active hook root explicitly:

```sh
python3 -I -S -B scripts/verify-security-fixture-patch.py --patch repair.patch --path scripts/fixture.py --active-hook-root "$HOME" --check --json
```

Replace the example patch and fixture paths with your actual files. The verifier
checks disposable copies against active and candidate scanners and independent
credential controls. It never applies the patch or changes the live index. Native
Windows verification is unsupported and refuses before launching children.

### Hook diagnostics

The installed standalone diagnostics command collects bounded metadata without
scanning content. The legacy `hooks-diagnostics-v1` marker applies only to old
scanner registrations; use the standalone command for current installations.

Each provider also installs a standalone `hooks-diagnostics.py` beside its scanner.
Both installers pin scanner and Tool Guardian registrations to the absolute Python
executable selected during installation, with `-I -S -B` and absolute installed
script paths. These commands ignore Python startup configuration and later PATH
changes. Reinstall after moving or removing that interpreter. The installing user
must trust the selected interpreter and installed files; replacing them remains
outside this protection. Windows paths containing shell expansion characters
`%` or `!` are refused instead of registering an ambiguous command.
From an ordinary human terminal, choose a trusted absolute Python executable and
use isolated startup with the absolute installed script path, for example:

```sh
/usr/bin/python3 -I -S -B /Users/your-name/.codex/hooks/hooks-diagnostics.py
/usr/bin/python3 -I -S -B /Users/your-name/.codex/hooks/hooks-diagnostics.py --doctor
```

Replace both absolute paths with your reviewed installation paths. Copilot's CLI
is `~/.copilot/hooks/scripts/hooks-diagnostics.py`; Gemini's is
`~/.gemini/hooks/scripts/hooks-diagnostics.py`. Only no arguments, `--doctor`, and
`--help` are accepted. No arguments collect current-directory file metadata and
fixed installation checks; `--doctor` checks only fixed assets and registrations.
The collector runs no Git or subprocesses and reads no candidate contents.
Its bounded largest-file inventory leaves pending/index status unknown. Inspect
the index separately if worktree sizes do not explain an incomplete scan.

Reports separate the loaded canonical build from observed disk hashes, helper
drift, registration counts, repository metadata, audit status, and content
security. Entrypoint disk hashes remain unverified observations. Diagnostics do
not establish a clean scan, authenticate installed execution, or grant an agent
command an exemption. Tool Guardian may still deny an unsafe tool action. The human
owns interpreter and installation trust; reinstall from trusted source if the
CLI itself is damaged. Platforms without descriptor-relative no-follow access
report limited checks instead of claiming equivalent filesystem guarantees.

The repository-state guard is retired from maintained source and fresh installs. An older installation may still have `~/.copilot/hooks/scripts/repository-state.py`, `~/.gemini/hooks/scripts/repository-state.py`, or `~/.codex/hooks/repository-state.py`. Review `~/.copilot/hooks/hooks.json`, `~/.gemini/settings.json`, and `~/.codex/hooks.json` for matching `repository-state.py` commands before manually removing those entries and files. On Windows, use the equivalent paths under `%USERPROFILE%`; Gemini's settings path is `%USERPROFILE%\.gemini\settings.json`. Back up modified configuration first, preserve unrelated hooks, and use each provider's hook review or trust flow afterward. The installers retire only exactly owned scanner registrations; unrelated retired scripts and registrations still require manual review.

### Old Markdown Health installations

The former user-global Markdown Health checker is no longer maintained or included in fresh installs. An older installation may still run it. If you want to retire an installed copy, inspect your user hook configuration and remove only the `markdown-health.py` handlers from `~/.copilot/hooks/hooks.json`, `~/.gemini/settings.json`, and `~/.codex/hooks.json` where present. Then remove the old script at `~/.copilot/hooks/scripts/markdown-health.py`, `~/.gemini/hooks/scripts/markdown-health.py`, or `~/.codex/hooks/markdown-health.py` after confirming no registration still needs it. Keep shared `audit.log` history and the dedicated `markdown-health-state` directories unless you separately decide to archive or remove that data.

Published benchmark workspaces sit beside their owners under `skills/<category>/`; their `-workspace` suffix keeps them out of installations.

Codex TOML files and `.skills-repo-agents.json` in the selected Codex agents directory are installer-managed. Do not edit them manually: update the canonical top-level Markdown source and rerun an installer. Each source file must be a regular UTF-8 Markdown file with YAML frontmatter containing non-empty `name` and `description`; its body becomes the exact `developer_instructions` value. The Codex converter removes only stale TOML files recorded in its manifest and leaves every unrecorded personal agent untouched.

## CLI dependencies

- Core tooling: `bash`, `python3`, and `git`
- Hook runtime: `python3`, `jq`, and `flock`
- Hook formatting: `npx` (with `oxfmt`) for JS/TS files, `dotnet` SDK for C# files
- Agent shell workflows: stable `rtk` 0.50.0 or newer (required by the installers)

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

1. Edit published skill sources in `skills/<category>/`, custom agents in `agents/`, and hook/config sources in `hooks/`, `.codex/`, `.copilot/`, or `.gemini/`.
2. Rerun `./scripts/install.sh` to refresh the installed local copies.
3. Run `./scripts/test-all.py` for all maintained test suites, or use targeted checks from [testing guidance](.agents/instructions/testing.md).

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
generated files; they never generate repository sources. The manifest lists all
maintained executable outputs.

Ignore `skills/*/*-workspace/**/outputs/` and `.agents/skills/*-workspace/**/outputs/` during normal edits and reviews. Those files are benchmark fixtures, not maintained source.

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

Run the narrowest command that covers your change. Canonical agent-facing validation routing lives in [testing guidance](.agents/instructions/testing.md).

For hook changes, use the targeted [source checks](.agents/instructions/testing/hooks.md). Before authorized live validation, refresh installed copies and follow [live-hook testing](.agents/instructions/testing/hooks-live.md); honor task-specific installation ownership.

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

- [Instruction routes](.agents/instructions/INDEX.md) - select guidance by task.
- [Knowledge admission](.agents/instructions/knowledge-base.md) - what earns a place in instructions or memory.
- [Testing guidance](.agents/instructions/testing.md) - focused validation routes.
- [Memory index](.agents/memory/INDEX.md) - optional limitations and source references.
