# Repository provider runtime audit

Audited for milestone 4 on 2026-09-30. This promotes the earlier read-only runtime inventory into the implemented repository contract. It describes generated files and installed subprocess proof, not normal client delivery or native Windows/Linux acceptance.

## Native paths and registration

| Provider | Skills and agents | Native configuration | Independent hook package |
| --- | --- | --- | --- |
| Codex | `.agents/skills`, `.codex/agents/*.toml` | `.codex/hooks.json` | `.codex/hooks/agent-assets/` |
| Copilot CLI and VS Code | `.agents/skills`, `.github/agents/*.agent.md` | `.github/hooks/agent-assets.json` | `.github/hooks/agent-assets/` |
| Gemini CLI | `.agents/skills`, `.gemini/agents/*.md` | `.gemini/settings.json` | `.gemini/hooks/agent-assets/` |

Canonical agent parsing and Codex serialization live in `scripts/canonical_agents.py`. Both the legacy personal converter and selected installer reuse these side-effect-free functions. Neither invokes the other installer's mutations. Selected installation also preflights malformed unmanaged Codex TOML and case-folded name/path collisions. The parser preserves the established strict two-field frontmatter, nonempty body, reserved-name checks, collision checks, and validated TOML serialization.

The selected registrations retain native events: Codex `SessionStart`, `PreToolUse`, and scanner `Stop`; Copilot `sessionStart`, `preToolUse`, and scanner `agentStop`; Gemini `SessionStart`, `BeforeTool`, and scanner `SessionEnd`. Copilot receives both Bash and PowerShell command fields. Codex receives `commandWindows`. Gemini's single command field uses a fixed Python bootstrap that obtains the Git root and passes the launcher path as a subprocess argument. It does not interpolate a repository path into shell source. POSIX commands and the bootstrap support nested working directories and quoted repository names. Windows strings remain unverified until milestone 6.

Codex hook timeouts use seconds, Gemini uses milliseconds, and Copilot uses `timeoutSec`. Gemini lifecycle groups omit matchers because the native field filters lifecycle events by exact string; its maintained tool groups retain their tool matcher. Existing provider envelopes and bounded JSON readers remain unchanged. Source references checked against the existing repository templates and current first-party documentation: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Copilot hook reference](https://docs.github.com/en/copilot/reference/hooks-reference), [Gemini hook reference](https://geminicli.com/docs/hooks/reference/). The earlier audit also consulted [VS Code hook compatibility](https://code.visualstudio.com/docs/copilot/customization/hooks); a fresh fetch during implementation was unavailable, so live VS Code proof remains open.

## Runtime configuration and state

Each hook package includes its launcher, selected handlers, `helpers/common.py`, `helpers/audit.py`, and `helpers/runtime_config.py`. Copilot and Gemini additionally include `helpers/observability.py` because the common helper may enable capture from the environment. There are no cross-provider imports. Generated source ownership lives in `hooks/manifest.py`; the three loaders now come from `hooks/families/required_skills.py`, and package launch/configuration helpers come from `hooks/families/repository_runtime.py`.

The launcher sets `AGENT_ASSETS_RUNTIME_CONFIG` to its adjacent `runtime.json`. This file records schema version, provider, installation ID, package-relative skill/reference roots, and required skill files. The helper rejects duplicate keys, wrong package/provider placement, invalid roots, traversal, and linked asset paths. Loaders prefer this explicit configuration; absent it, their existing personal defaults remain. Hook input cannot select a skill root.

The launcher uses `AGENT_ASSETS_STATE_DIR` when explicitly set. Otherwise state uses `XDG_STATE_HOME/agent-assets` or `~/.local/state/agent-assets` on Linux, `~/Library/Application Support/agent-assets` on macOS, and `LOCALAPPDATA/agent-assets` on Windows. Provider and normalized-target-path hash partition the selected base. State inside the installed repository is refused. The launcher routes audit, Tool Guardian, scanner, optional trace database/transcripts/registry, and provider-specific observability overrides to this external directory. It also disables bytecode writes. Source scanner temporary Git capture continues to use the OS temporary directory.

The baseline audit found an inconsistent `TOOL_GUARD_LOG_DIR` convention: Codex/Copilot interpret a file while Gemini appends `guard.log` to a directory. The launcher adapts explicitly without changing the established handler APIs. Codex's standalone required-skill audit keeps its existing no-link and owner-only behavior, using the package audit directory only with explicit runtime configuration.

## Ownership and acquired-source boundary

Native JSON files have semantic ownership of exact managed entries. Unrelated settings and handlers remain. Ownership records hash canonical managed entries and Copilot version metadata, not the surrounding settings. Typed JSON comparison distinguishes integer `1` from `true` and `1.0`. Updates preserve unchanged-upstream local edits and report drift; incompatible changes and pruning refuse edited entries or modes. Repetition does not append duplicate handlers. Missing native configuration can be restored from the pinned installation. Hard-linked configurations are replaced atomically without changing the external inode. Malformed/duplicate-key JSON, invalid Codex TOML, linked destinations, and competing inline Codex hooks refuse before writes.

Before mutating ownership, the installer reconstructs the exact owned files and configuration entries from the immutable recorded catalog/source, including retained origins. Journal validation also compares the unowned before/after configuration projection so recovery cannot use a forged journal to overwrite unrelated settings. Offline `status --check` evaluates installed managed entries, ignores unrelated settings, and performs no source acquisition or repair.

Acquisition never imports or executes source Python, catalog code, clients, or hooks. For desired generated hooks, the command checkout supplies trusted manifest/provider/family semantics; source generation inputs must match those supported bytes, and checked-in outputs must match their read-only render. Unsupported inputs refuse with compatible-command-checkout guidance. Source scripts are not executed even when their filename is `scripts/generate-hooks.py`. Old ownership authentication reads and hashes its immutable generation lineage without requiring obsolete family source to equal the current command checkout. Desired installation/update/restore still passes the full freshness gate.

## Trust and acceptance limits

Project and personal hooks may both run. Repository installs leave personal registrations intact and report this additive behavior. Codex hook trust must be reviewed through its native hooks flow. Gemini retains native project hook trust. File presence and offline integrity do not establish discovery, trust approval, or normal event delivery.

Public subprocess tests execute all three installed required-skill packages after committing, cloning to a quoted new path, deleting the source checkout, and starting from a nested directory. An empty disposable home proves the selected skill is repository-local; external state and unchanged Git status prove no payload state writes. Security-handler tests exercise native tool denials for all three packages, and optional Gemini capture proves its helper/database dependency remains external. These are macOS subprocess proofs. Milestone 6 owns normal clients and native Windows/Linux proof. No safe standalone instruction fragment was identified in the broad personal instruction/configuration sources; catalog listing reports that limitation and distributes none of those personal settings.
