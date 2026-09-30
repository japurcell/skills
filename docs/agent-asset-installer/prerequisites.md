# Installer Prerequisite Probe

Initial probe and refresh date: 2026-09-29 local time. The user supplies flock before the implementation resumes; this version is promoted after M3 integration. This is read-only environment and official-documentation evidence for milestones 4 and 6 of `ExecPlan.md`. It does not assert live client support or completion of either milestone. Existing architecture research is in `docs/agent-asset-distribution/local-inventory.md` and `recommendation.md`; the accepted recommendation is a selective Git-sourced installer with provider-specific native outputs, and those documents remain the baseline rather than being repeated here.

## Observed command availability

Commands were discovered with `command -v` and queried using `--version` only. Platform evidence from Bash identifies this as Apple Darwin on arm64; this probe did not run a client, authenticate, install software, or modify a home/config directory.

| Command | Observed |
| --- | --- |
| Python (`python3`) | 3.14.6; resolves through `/Users/adam/.pyenv/shims/python3`. |
| Additional Python | 3.13.14 is installed. The complete current 64-case public installer suite passes on this runtime in 64.547 seconds. This is macOS evidence only. |
| flock | 0.4.0 at `/Users/adam/homebrew/bin/flock`, installed by the user. |
| Git | 2.50.1 (Apple Git-155). |
| Bash | GNU bash 3.2.57(1)-release (arm64-apple-darwin25). |
| PowerShell (`pwsh`) | 7.6.6; present, but this is macOS PowerShell and does not satisfy native Windows acceptance. |
| RTK (`rtk`) | 0.50.0. `rtk proxy` successfully ran version queries. `rtk gain` could not initialize its tracking database because the probe worktree environment denied opening that database; the shim also prints a pyenv rehash permission warning. |
| Codex CLI (`codex`) | `codex-cli 0.159.0`; present. The version command warned PATH aliases could not be created due to operation permission, but returned the version. |
| Copilot CLI (`copilot`) | Not found on PATH. |
| VS Code CLI (`code`) | Not found on PATH. |
| Gemini CLI (`gemini`) | Not found on PATH. |
| Claude Code CLI (`claude`) | Not found on PATH. |
| Cursor CLI (`cursor`) | Not found on PATH. |
| OpenCode CLI (`opencode`) | Not found on PATH. |

**Prerequisite refresh:** flock is now available and the aggregate dependency preflight succeeds. The resumed baseline runs 37 suites, with 34 passing and three existing fixture failures; those failures and provider trace-state isolation are repaired and integrated. The aggregate after M3 and both repair nodes passes all 37 suites with zero failures in 378.4 seconds. Existing host-specific skips remain unverified native Windows evidence. Git and Python remain installer prerequisites; selected RTK hooks require RTK. Do not add flock as a skill-only installer prerequisite. No Windows or Linux host evidence is available, and Python 3.11 has not been observed locally.

## Official paths and trust constraints

The existing source inventory and recommendation remain authoritative for the native path matrix. These current first-party references clarify relevant constraints:

- **Codex:** [`AGENTS.md` project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [hooks and trust review](https://learn.chatgpt.com/docs/hooks), and [project config basics](https://learn.chatgpt.com/docs/config-file/config-basic). Codex project-local hooks load only when the project `.codex/` layer is trusted. Non-managed hook definitions require review/trust against the current definition hash; changed hooks require review again. The `hooks` docs identify `/hooks` for review. The existing inventory documents `.agents/skills`, `.codex/agents/*.toml`, and `.codex/hooks.json` for local Codex. Treat local CLI/desktop observations as separate from IDE and cloud surfaces.
- **Copilot:** [customization paths cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet), [hook reference](https://docs.github.com/en/copilot/reference/hooks-reference), [custom agent profiles](https://docs.github.com/en/copilot/reference/custom-agents-configuration), and [CLI customization](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/overview). Project hooks use `.github/hooks/*.json`; CLI user hooks combine with project hooks. Cloud hooks execute in a restricted ephemeral Linux job with no interactive trust prompt. The CLI and VS Code must be verified independently; a VS Code workspace override is not evidence for CLI or cloud behavior.
- **Gemini CLI:** [trusted folders](https://geminicli.com/docs/cli/trusted-folders/), [configuration](https://geminicli.com/docs/reference/configuration/), [Agent Skills](https://geminicli.com/docs/cli/using-agent-skills/), and [hook security](https://geminicli.com/docs/hooks/best-practices/). Project settings, skills, and hooks depend on native workspace trust. The trust docs describe isolated trust-state placement via `GEMINI_CLI_TRUSTED_FOLDERS_PATH`; the configuration docs describe `GEMINI_CLI_HOME` for user configuration/storage. The CLI was absent here, so no disposable profile or trust path was exercised.
- **Claude Code:** [project skills](https://code.claude.com/docs/en/skills), [hooks](https://code.claude.com/docs/en/hooks), and [settings](https://code.claude.com/docs/en/settings). Existing research identifies `.claude/skills`, `.claude/agents`, and project settings; any hook is executable and must be proven through the real client. CLI absent here.
- **Cursor:** [Agent Skills](https://cursor.com/docs/skills), [hooks](https://cursor.com/docs/hooks), and [plugins](https://cursor.com/docs/plugins). Official docs describe project `.agents/skills/` and `.cursor/skills/`. User-global skill syncing is a separate cloud-agent workflow, and unsynced local skills do not automatically transfer to cloud or remote workers. CLI absent here.
- **OpenCode:** [skills](https://opencode.ai/docs/skills), [agents](https://opencode.ai/docs/agents), and [plugins](https://opencode.ai/docs/plugins). Official skills docs explicitly accept project `.agents/skills/<name>/SKILL.md`; project agents/configuration and plugin runtime are distinct surfaces. CLI absent here.

The Codex project trust and Gemini folder-trust docs provide supported native trust procedures; do not manufacture trust by bypassing safeguards. Any later live probe should use a disposable clone and isolated profile/home where the client documents one, inspect the source it will load, then let the client request or record normal trust. Keep the fixture response distinct from any personal/global asset.

## Documented versus observed

Official documentation establishes that the listed formats and paths are supported by the named product surfaces. It does not establish that this repository's rendered settings, hook command lines, executable bits, runtime dependencies, or selected fixture load successfully. This probe observed versions only. It did not observe native skill discovery, agent selection, hook execution, trust dialogs, clone relocation, Windows/Linux behavior, or client compatibility at runtime. Existing prior research likewise records no live client installation.

## Remaining gates and safe next actions

1. Preserve the passing 37-suite aggregate result after integrated repairs and M3; rerun only when new source changes or unresolved concerns justify it. Preserve all assertions. The user supplies flock; the agent does not install dependencies or add flock as a blanket installer prerequisite.
2. Run the repository-owned provider subprocess suites on supported runtimes, then obtain native macOS, Linux, and Windows jobs. Python 3.14.6 is observed locally; the plan explicitly requires Python 3.11 and a supported newer version. A local 3.14 result cannot replace the planned matrix.
3. For milestone 4, prove that generated Codex, Copilot, and Gemini files survive relocation and run their harmless hook subprocesses with provider-valid envelopes. Record generated presence separately from client trust.
4. For milestone 6, use native Windows for PowerShell forwarding, reserved/case-colliding paths, reparse refusal, and replacement/recovery. `pwsh` on this Darwin host cannot meet that gate.
5. For each available client, use a disposable checkout and isolated profile, verify skill plus supporting-reference discovery on Codex CLI/desktop, Copilot CLI/VS Code, and Gemini CLI, and run the planned harmless hook. Verify skills/references only for Claude Code, Cursor, and OpenCode. Repeat from a clone without the source checkout. Missing binaries/credentials are unmet gates, never passing evidence.
6. Keep OS-level automated test evidence, clone/hash/line-ending evidence, discovery evidence, and hook-event evidence as separate entries in the eventual `client-validation.md` required by milestone 6.

The initial client probe uses discovery/version reporting only. Later installed Codex help and official trust inspection are recorded separately in [Codex CLI prerequisites](codex-cli-prerequisites.md); no live client runs. No credentials were read; no live model was invoked; no software, home directory, configuration, repository source, remote, or published artifact was changed.
