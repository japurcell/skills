# Skills

This repository publishes custom GitHub Copilot assets:

- **Skills** in `skills/` for reusable task workflows such as `tdd`, `security-review`, `frontend-design`, and `create-plan`
- **Custom agents** in `agents/` such as `code-architect`, `code-explorer`, `code-reviewer`, and `grader`
- **Local Copilot instructions** in `.copilot/copilot-instructions.md`

## Installation

Install or refresh the locally loaded copies with:

```bash
./scripts/copilot-install.sh
```

The installer copies:

- `skills/` entries into `~/.agents/skills`
- top-level `references/` entries into `~/.agents/references` when that directory exists
- `agents/` files into `~/.copilot/agents`
- `.copilot/copilot-instructions.md` into `~/.copilot/copilot-instructions.md`

Workspace directories whose names end with `-workspace` are skipped during installation.

## Repository layout

- `skills/`: one directory per skill, centered on `SKILL.md`
- `agents/`: standalone custom agent prompt files
- `references/`: optional shared reference material installed to `~/.agents/references`
- `scripts/`: repo helper and installation scripts
- `docs/agent-guides/`: repo-specific guidance for layout, authoring, and validation
- `skills/*-workspace/`: generated eval runs, snapshots, and review artifacts
- `scripts/copilot-install.sh`: installs `skills/` → `~/.agents/skills`, optional top-level `references/` → `~/.agents/references`, `agents/` → `~/.copilot/agents`, and `.copilot/copilot-instructions.md` → `~/.copilot/copilot-instructions.md`
- `scripts/addy-install.sh`: imports addy agents, skills, and top-level references into this repository, prefixing imported addy agent and skill names with `addy-`; pass `--skills foo,bar` to copy specific source skill names and their referenced skills

## Working in this repo

1. Edit source files in `skills/`, `agents/`, or `.copilot/`.
2. Rerun `./scripts/copilot-install.sh` to refresh the installed local copies.
3. Use targeted checks for the area you changed; there is no single repo-wide test runner.

Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews. Those files are benchmark fixtures, not maintained source.

## Authoring notes

### Skills

- Use `SKILL.md` as the entry point.
- Start each `SKILL.md` with YAML frontmatter.
- Keep `name` lowercase kebab-case.
- Keep descriptions concrete and trigger-oriented.

### Agents

- Store each custom agent as a single Markdown file in `agents/`.
- Use YAML frontmatter with `name` and `description`.
- Keep the body focused on execution guidance, output shape, and decision criteria.

## Validation

Run the narrowest command that covers your change:

```bash
# Installer changes
bash -n scripts/copilot-install.sh
bash -n scripts/addy-install.sh
bash scripts/test-addy-install.sh

# Skill validation
python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>

# Skill packaging
PYTHONPATH=skills/skill-creator python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name> /tmp/skill-dist

# Agent SOP validation
bash skills/agent-sop-author/validate-sop.sh path/to/file.sop.md
```

## Additional docs

- `docs/agent-guides/repo-layout.md`
- `docs/agent-guides/authoring.md`
- `docs/agent-guides/validation.md`
