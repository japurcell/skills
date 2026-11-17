# Skill category selection

## Sub-features

- Opt in with `--forest-service`, `--fs`, or `INSTALL_FOREST_SERVICE_SKILLS=true`.
- Override environment selection with `--no-forest-service`.
- Reject conflicting flags and invalid environment values.

## How to get to it (user POV)

Pass selection flags to either installer, or set `INSTALL_FOREST_SERVICE_SKILLS` for that invocation.

## Driving it with Bash

Use the installation command and readback recipe from `install.md`, replacing its selection arguments. Run each entrypoint with a fresh home and separate logs. Opt-in must install the union of eligible directory names from `skills/default` and `skills/forest-service`, flat under `.agents/skills`. `INSTALL_FOREST_SERVICE_SKILLS=true ... --no-forest-service` must install only defaults into a fresh home. Repeat default-only into an opt-in home and prove previously installed Forest Service skills remain.

Run `bash scripts/install.sh --fs --no-forest-service` and, separately, selection value `banana` with no flag. Both must exit 2, explain the invalid selection on stderr, and leave the empty home unchanged. Run the corresponding PowerShell commands to cover that entrypoint. Record exact arguments, category name sets, and exit codes.

## Gotchas

- Default-only refresh is not an uninstall operation.
- Empty categories are valid; excluded `archive` and `*-workspace` directories are not installable skills.
- Override inherited environment values explicitly; otherwise the same command can select different categories across sessions.
