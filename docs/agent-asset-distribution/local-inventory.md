# Current Repository Distribution Inventory

Inspected on 2026-09-29. This inventory describes current source behavior; it does not propose approved installer changes.

## Existing installation boundary

The repository currently contains 51 maintained skill directories with `SKILL.md` entry points, excluding `archive` and directories ending in `-workspace`, and 19 top-level canonical agent Markdown files. No root `package.json`, root `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, or `gemini-extension.json` exists. The existing distribution entry points are the [Bash installer](../../scripts/install.sh) and [PowerShell installer](../../scripts/install.ps1), documented in [README](../../README.md).

The Bash installer has no command-line scope or selection interface. It copies skill entries to `~/.agents/skills`, references to `~/.agents/references`, agent Markdown to `~/.copilot/agents` and `~/.gemini/agents`, and generated agent TOML to `${CODEX_HOME:-$HOME/.codex}/agents`. Its skill copier excludes benchmark workspaces and archives, then prunes evaluation and selected documentation files from installed copies. The PowerShell installer describes the same installed layout. These are existing personal installation semantics, not a repository packaging contract. [Sources: Bash installer](../../scripts/install.sh), [PowerShell installer](../../scripts/install.ps1).

## Asset families have different portability

| Family | Existing source boundary | Distribution implication |
| --- | --- | --- |
| Skills | `skills/<name>/SKILL.md` and optional supporting files | Preserve the complete runtime dependency tree for each selected workflow. Discovery paths still depend on the client. |
| Custom agents | Canonical `agents/*.md`; Codex receives generated TOML | Keep canonical instructions, with client-specific serialization and capability metadata. |
| Hooks | Canonical build-time `hooks/` families generate provider-local Python | Package generated runtime files with provider-specific registrations; do not assume one hook event schema. |
| Instructions | `.codex/AGENTS.md`, `.copilot/copilot-instructions.md`, `.gemini/` context | Distinguish personal preferences from repository policy and avoid replacing unrelated project instructions. |
| Settings | Provider templates include both behavior and personal settings | Extract only selected repository behavior rather than publishing an entire personal settings file. |
| References and state | Shared references plus logs under user hook directories | Make read-only assets portable and define writable state separately from installed package code. |

The [Codex agent converter](../../scripts/install-codex-agents.py) requires exactly `name` and `description` in source frontmatter and emits `name`, `description`, and `developer_instructions` TOML. Future agent packaging must preserve this contract until an explicit migration is chosen. The [generated ownership manifest](../../hooks/manifest.py) lists separate Copilot, Gemini, Codex, and repository GitHub hook outputs. This repository already shares hook source at build time rather than importing shared code across installed provider runtimes.

## Home-directory assumptions to address

The [Codex registration template](../../.codex/global-hooks.json), [Copilot registration template](../../.copilot/hooks/hooks.json), and [Gemini global settings](../../.gemini/global-settings.json) invoke scripts under home-directory paths. Relocating the scripts without regenerating registration commands will still invoke personal installed copies.

The [Codex required-skill loader](../../.codex/hooks/load-required-skills.py) directly loads `Path.home() / ".agents" / "skills"`. The [Copilot loader](../../.copilot/hooks/scripts/load-required-skills.py) and [Gemini injector](../../.gemini/hooks/scripts/skill-context-injector.py) already support `AGENTS_SKILLS_DIR` and `COPILOT_SKILLS_DIR` overrides, with different precedence. A repository install must define its own discovery contract rather than relying on user-global copies.

Several hook families and generated audit helpers default writable logs to provider directories beneath the user's home. A package root can be immutable or replaced during updates, so writable state location is a separate design decision. [Sources: hook families](../../hooks/families/), [Codex audit helper](../../.codex/hooks/helpers/audit.py).

Gemini's global settings combine hooks with UI preferences, authentication selection, model definitions, custom-agent overrides, and account-specific MCP configuration. The current global install is intentional, but publishing that entire file as repository configuration would distribute unrelated personal choices. [Source: global settings](../../.gemini/global-settings.json).

## Selective installation includes workflow dependencies

Skill workflows invoke other skills. For example, [wayfinder](../../skills/wayfinder/SKILL.md) activates research and grilling, and [delegate-to-subagents](../../skills/delegate-to-subagents/SKILL.md) activates the model router. Installing only a named top-level workflow can therefore leave required workflows missing even when its `SKILL.md` is valid. The absent `domain-modeling` skill referenced by wayfinder was encountered during this session. Model discovery, workflow dependency resolution, and hook execution dependencies are distinct requirements.

## Implications for the pending decision

The recommendation should preserve current user-global installation, add explicitly selected repository behavior, retain provider-local hook generation, and treat configuration merging and owned-file removal as public installation behavior. These are implications inferred from current source, not an approved design. Both committed team setup and local untracked setup are required, with committed team setup as the user-confirmed default.
