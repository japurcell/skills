# Repo layout

## Structure

- `skills/`: one directory per skill; each skill is centered on `SKILL.md` and may include `scripts/`, `references/`, `assets/`, and `evals/`
- `agents/`: standalone custom agent prompt files such as `code-architect.md` and `code-reviewer.md`
- `references/`: optional top-level shared reference material copied into `~/.agents/references`
- `scripts/`: repository-level helper scripts such as installers and importers
- `skills/*-workspace/`: generated evaluation runs, snapshots, and review artifacts

## Key files

- `scripts/copilot-install.sh`: installs `skills/` → `~/.agents/skills`, optional top-level `references/` → `~/.agents/references`, `agents/` → `~/.copilot/agents`, optional top-level `hooks/` → `~/.copilot/hooks`, and `.copilot/copilot-instructions.md` → `~/.copilot/copilot-instructions.md`
- `scripts/addy-install.sh`: syncs `../addy-agent-skills` from `https://github.com/addyosmani/agent-skills` by cloning or fast-forward pulling, then imports agents, skills, top-level references, and top-level hooks into this repository; imported addy agent and skill names get `addy-` prefixes, optional `--skills foo,bar` or `--skills-file path` filtering also pulls in referenced skills, and successful runs refresh `.addy-skills` with the installed source skill names
- `.nvmrc`: Node version hint (`lts/*`)
- `skills/skill-creator/scripts/quick_validate.py`: validates `SKILL.md` frontmatter and structure
- `skills/skill-creator/scripts/package_skill.py`: packages a skill directory into a distributable `.skill` archive
- `skills/agent-sop-author/validate-sop.sh`: validates `.sop.md` files against the expected SOP structure
