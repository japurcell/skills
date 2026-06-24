# Skills

This repository publishes custom GitHub Copilot assets:

- **Skills** in `skills/` for reusable task workflows such as `tdd`, `frontend-design`, `create-skill`, `prd`, `code-review`, and `commit`
- **Custom agents** in `agents/` such as `code-architect`, `code-explorer`, `code-reviewer`, and `grader`
- **Copilot global configs** in `.copilot`
- **Gemini global configs** in `.gemini`

Detailed layout, validation, authoring, and hook guidance live in `docs/agent-guides/`.

## Installation

Install or refresh the locally loaded copies with:

```bash
./scripts/install.sh
```

The installer copies:

- `skills/` entries into `~/.agents/skills`
- top-level `references/` entries into `~/.agents/references` when that directory exists
- `agents/` files into both `~/.gemini/agents` and `~/.copilot/agents`
- `.copilot/hooks/` entries are copied to `~/.copilot/hooks` when that directory exists
- `.gemini/` contents into `~/.gemini`
- `.copilot/copilot-instructions.md` into `~/.copilot/copilot-instructions.md`

Workspace directories whose names end with `-workspace` are skipped during installation.

## CLI dependencies

- Core tooling: `bash`, `python3`, and `git`
- Hook runtime: `jq` and `flock`
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

## Repository layout

- `skills/`: one directory per skill, centered on `SKILL.md`
- `skills/archive/`: skills that are no longer maintained but kept for historical reference
- `agents/`: standalone custom agent prompt files
- `references/`: optional shared reference material installed to `~/.agents/references`
- `scripts/`: repo helper and installation scripts
- `.copilot/`: local Copilot instructions copied by the installer
- `.copilot/hooks/`: hook scripts and configs installed to `~/.copilot/hooks`
- `docs/agent-guides/`: repo-specific guidance for layout, authoring, and validation
- `skills/*-workspace/`: generated eval runs, snapshots, and review artifacts; ignore their `outputs/` subdirectories during normal work
- `scripts/install.sh`: installs `skills/` → `~/.agents/skills`, optional top-level `references/` → `~/.agents/references`, `agents/` → both `~/.gemini/agents` and `~/.copilot/agents`, optional `.copilot/hooks/` → `~/.copilot/hooks`, `.gemini/` contents → `~/.gemini`, and `.copilot/copilot-instructions.md` → `~/.copilot/copilot-instructions.md`
- `scripts/addy-install.sh`: syncs `../addy-agent-skills` from `https://github.com/addyosmani/agent-skills` by cloning or fast-forward pulling, then imports addy agents, skills, and top-level references into this repository, prefixing imported addy agent and skill names with `addy-`; pass `--skills foo,bar` or `--skills-file path` to copy specific source skill names and their referenced skills, and each successful run refreshes `.addy-skills` with the installed source skill names

## Working in this repo

1. Edit source files in `skills/`, `agents/`, `.copilot/`, or `.gemini/`
2. Rerun `./scripts/install.sh` to refresh the installed local copies.
3. Use targeted checks for the area you changed; there is no single repo-wide test runner.

Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews. Those files are benchmark fixtures, not maintained source.

## Authoring notes

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

Run the narrowest command that covers your change. Use the canonical validation guide for targeted commands and live-validation workflow:

- [`docs/agent-guides/validation.md`](docs/agent-guides/validation.md)

## Additional docs

- `docs/agent-guides/repo-layout.md`
- `docs/agent-guides/hooks.md`
- `docs/agent-guides/authoring.md`
- `docs/agent-guides/validation.md`
