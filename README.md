# Skills

This repository publishes custom GitHub Copilot assets:

- **Skills** in `skills/` for reusable task workflows such as `tdd`, `frontend-design`, `create-skill`, `prd`, `code-review`, and `commit`
- **Custom agents** in `agents/` such as `code-architect`, `code-explorer`, `code-reviewer`, and `grader`
- **Copilot global configs** in `.copilot`
- **Gemini global configs** in `.gemini`

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
- `agents/` files into both `~/.gemini/agents` and `~/.copilot/agents`
- `.copilot/hooks/` entries are copied to `~/.copilot/hooks` when that directory exists
- `.gemini/` contents into `~/.gemini`, then `.gemini/global-settings.json` into `~/.gemini/settings.json`
- `.copilot/copilot-instructions.md` into `~/.copilot/copilot-instructions.md`

Workspace directories whose names end with `-workspace` are skipped during installation.

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

1. Edit source files in `skills/`, `agents/`, `.copilot/`, or `.gemini/`
2. Rerun `./scripts/install.sh` to refresh the installed local copies.
3. Use targeted checks from `.agents/memory/TESTING_STRATEGY.md`; there is no single repo-wide test runner.

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

Run the narrowest command that covers your change. Canonical agent-facing validation routing lives in `.agents/memory/TESTING_STRATEGY.md`.

For hook changes, run `./scripts/install.sh` first and then the targeted regressions listed in `.agents/memory/testing/hooks.md`; the current hook validation set starts with auto-ingest/startup, observability, secrets, tool-guard, and RTK checks.

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
