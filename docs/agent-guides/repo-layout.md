# Repo layout

## Structure

- `skills/`: one directory per skill; each skill is centered on `SKILL.md` and may include `scripts/`, `references/`, `assets/`, and `evals/`
- `agents/`: standalone custom agent prompt files such as `code-architect.md` and `code-reviewer.md`
- `skills/*-workspace/`: generated evaluation runs, snapshots, and review artifacts

## Key files

- `copilot-install.sh`: installs `skills/` → `~/.agents/skills`, `agents/` → `~/.copilot/agents`, and `.copilot/copilot-instructions.md` → `~/.copilot/copilot-instructions.md`
- `.nvmrc`: Node version hint (`lts/*`)
- `skills/skill-creator/scripts/quick_validate.py`: validates `SKILL.md` frontmatter and structure
- `skills/skill-creator/scripts/package_skill.py`: packages a skill directory into a distributable `.skill` archive
- `skills/agent-sop-author/validate-sop.sh`: validates `.sop.md` files against the expected SOP structure
