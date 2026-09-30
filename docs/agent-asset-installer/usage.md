---
type: Agent Usage Guide
description: Public commands, scope choices, prerequisites, and support limits for selected agent assets
---

# Selected agent assets

The selective installer copies committed catalog assets into client-native paths and records the chosen source, selection, ownership, and rendered baseline. Team members receive actual skill, agent, and hook files in a normal clone. They do not need to acquire or cache this source repository just to load the committed payloads. Running installer commands, checking records, updating, or restoring requires Python 3.11 or newer, Git, and a compatible command checkout containing `scripts/agent-assets.py` and its package. Python 3.11 is the required baseline; this work has not executed the suite on Python 3.11. The 100-case public run is on Python 3.14.6.

Start by inspecting catalog availability and previewing a selection:

```bash
python3 scripts/agent-assets.py list --client codex
python3 scripts/agent-assets.py install --repo /path/to/project \
  --client codex --asset skill:caveman --preview
```

`list` distinguishes source availability and missing dependency chains from client installability and restrictions. Use `--format json` for automation. The `review` bundle is currently unavailable because its required dependency chain includes a missing source; listing reports the reason. `caveman` is an available skill for all six catalog clients. Current maintained hook choices are `required-skills`, `tool-guard`, and `scan-secrets`; there is no selectable RTK hook renderer.

## Choose an installation scope

Repository team mode is the default. It writes payloads and records into the project so they can be committed and reviewed:

```bash
python3 scripts/agent-assets.py install --repo /path/to/project \
  --client codex --asset skill:caveman
```

Repository local mode keeps the selected files untracked. Its records live in `.agent-assets/local/`, and private paths receive exact entries in the worktree-resolved Git exclude file. It refuses the operation with `ASSET_LOCAL_TRACKED_CONFLICT` if native files would be changed while tracked. It also refuses effective ignore rules that would expose private paths. Local mode does not invent a client-specific settings overlay:

```bash
python3 scripts/agent-assets.py install --repo /path/to/project \
  --client codex --asset skill:caveman --mode local
```

Personal mode writes under the selected home and stores records in that home's `.agent-assets/` directory. `--home` is valid only with `--scope user`; personal scope cannot be combined with `--repo` or local mode. Repeat the same `--home` and `--scope user` for later status, update, or restore commands. Adoption is optional and accepts only exact, verified existing bytes, modes, and native registration groups. Modified, linked, partial, or ambiguous installations stop with an adoption conflict:

```bash
mkdir -p /tmp/agent-home
python3 scripts/agent-assets.py install --scope user --home /tmp/agent-home \
  --client codex --asset skill:caveman --adopt
```

An explicit `--codex-home PATH` controls personal Codex agent outputs. Repeat the same value for every lifecycle command that targets those records. Inherited `CODEX_HOME` supplies this authority only when the command targets the actual process home. When `--home` names a disposable or other explicit home, inherited `CODEX_HOME` is ignored; pass `--codex-home` again on status, update, or restore if installation used it. A different authority is rejected instead of silently switching destinations.

The existing `scripts/install.sh` and `scripts/install.ps1` remain the broader legacy personal-copy workflow. With explicit selective-installer arguments, they forward to `scripts/agent-assets.py`; after managed personal records exist, their no-argument path uses saved-selection update. They do not replace the selective install scope choices.

## Selection, source, and lifecycle commands

Pass one or more repeatable `--client`, `--asset`, and `--bundle` options to `install`. At least one asset or bundle is required. Required catalog dependencies and supporting references/notices are included automatically. Clients are `codex`, `copilot`, `gemini`, `claude`, `cursor`, and `opencode`. The command's default source is its own checkout. `--source PATH_OR_GIT_URL` selects another source. `--branch NAME` and `--revision TAG_OR_COMMIT` are mutually exclusive. A branch is resolved to an immutable commit and recorded; an explicit tag or commit pins the selected source revision. For detached local sources, provide a reference.

```bash
python3 scripts/agent-assets.py install --repo /path/to/project \
  --client codex --client copilot --asset skill:caveman \
  --source /path/to/skills --branch main --format json
```

To select the currently available security hook bundle for a supported client,
use `--bundle security-hooks`. Check the requested client's `list` output first;
availability and installability can differ, and declared runtime tools remain
the consumer's responsibility.

`update` re-evaluates the saved selection at its configured branch, or at an explicit `--branch` or `--revision`, and prunes only unchanged files that are still owned and no longer selected. Preview first when the source changes:

```bash
python3 scripts/agent-assets.py update --repo /path/to/project --preview
python3 scripts/agent-assets.py update --repo /path/to/project
```

`restore` fills missing files from the exact recorded source commit and digest. It verifies the saved rendered baselines and does not follow a moving branch. There is no rollback command or installation history. `status` is offline and read-only. Informational status may describe drift while exiting successfully; `--check` is strict for CI, exiting `1` for recorded-content drift and `2` for invalid or unsupported records or a pending interrupted operation. It never repairs, fetches, runs a hook/client, refreshes an index, or recovers a journal.

```bash
python3 scripts/agent-assets.py status --repo . --check
```

### Audit committed payloads in CI

Run the audit before any job step that might restore or install files:

```yaml
- name: Verify committed agent assets
  env:
    AGENT_ASSETS_CHECKOUT: /path/to/agent-assets-command-checkout
  run: python3 "$AGENT_ASSETS_CHECKOUT/scripts/agent-assets.py" status --repo "$GITHUB_WORKSPACE" --check
```

Provide a compatible checkout of this repository's command at `AGENT_ASSETS_CHECKOUT`. The project clone contains payload files and their records, so this check validates that the checked-out bytes, selection, and effective checkout policy still match those records. It does not compare against the newest upstream branch, repair drift, or establish native client trust. The runner needs Python, Git, and the command checkout. It treats committed records as the expected authority; it does not cryptographically authenticate them or detect a coordinated rewrite of both records and payloads. Review record changes alongside payload changes. If a maintainer chooses to repair content, make that a later explicit step after reviewing the audit result; do not let the audit step modify the checkout.

## Conflicts, pruning, and recovery

Installation planning checks the whole operation before destination writes. When an upstream change conflicts with a locally edited managed file or owned checkout rule, the command stops and preserves local content. Review the reported paths, resolve the conflict in the working tree, then rerun the original update. There is no automatic merge or backup-based overwrite. Team mode leaves edits visible for ordinary Git review.

Updates remove a managed file only if the current bytes and mode still match its recorded baseline, it is no longer required, and its ownership is authenticated. Files shared by selected assets remain. For a path used by both team and local records, the installer authenticates the other scope and borrows only identical bytes, mode, and configuration entries. Borrowed metadata does not replace authentication of the immutable source. Shared ignore rules are retained while another private selection needs them. Reconcile explicit cross-scope changes only after reviewing both records and Git's effective ignore behavior.

A killed operation can leave one recorded pending journal. Read-only status reports it but never recovers it. A subsequent write command validates the journal and recovers only exact recorded staging files and empty created directories. External edits, altered preimages, or substituted parent paths stop recovery for manual resolution. The installer does not keep rollback history.

## Checkout policy

Team mode owns only exact new path rules in its marked `.gitattributes` block. It adds the `".gitattributes" text eol=lf` rule only when no compatible effective LF rule can be borrowed. A borrowed rule may come from outside the marked block; the lock records the requirement without claiming that rule. The owned rule keeps the block markers in LF checkout bytes and unrelated attributes remain untouched. Declared text files use the catalog's line-ending policy, including LF where specified; binary files remain binary. The installer checks effective Git attributes and refuses filters, encoding transformations, or higher-precedence rules that would change managed bytes. Private mode does not add `.gitattributes` rules. `status --check` audits the effective policy, including borrowed rules, and reports drift when it changes.

The paired `selection.json` and `lock.json` records use schema version 2. The lock always carries `attribute_file_policy`: `null` when no team metadata policy applies, or `["text", "eol=lf"]` when the team installation needs LF checkout for managed `.gitattributes` metadata. This requirement is recorded even when a compatible LF rule is borrowed. A genuine matching version-1 pair is still accepted and migrates to version 2 on update or restore. Mixed versions, malformed records, or a missing or invalid version-2 policy fail before writes. The audit is offline and treats the committed pair as trusted input; it cannot prove the pair's source authenticity, and a coordinated edit to both records can imitate a legacy pair. Review the record history and payload diff when crossing that trust boundary.

## Clients, runtime, and trust

The catalog currently offers native skill, agent, and hook rendering for Codex, Copilot CLI/VS Code, and Gemini CLI. Claude Code, Cursor, and OpenCode are skills-only. This is an installer rendering boundary, not proof that a client discovered an installed skill or agent, accepted a hook, or delivered an event. A normal runtime may require the user to trust the repository or review a hook definition. Use the client's own trust flow and inspect the installed command before enabling executable hooks. Project and personal settings can both apply according to each client's precedence.

The installer checks only declared supported runtime prerequisites and does not provision external tools. Hook assets may require Python, `jq`, or other catalog-declared tools. RTK hook selection is not available in this catalog. Client trust, model behavior, IDE delivery, and hosted/cloud behavior remain separate from file-format and subprocess tests.

| Surface | Installer rendering | Current evidence and limit |
| --- | --- | --- |
| Codex | Skills, agents, and hooks | Public file/protocol checks; CLI 0.159.0 displayed the normal trust screen, but continuing failed during managed-preferences synchronization. Skill discovery and native hook-event delivery remain unproven. See [client validation](client-validation.md). |
| Copilot CLI and VS Code | Skills, agents, and hooks | Documented separate surfaces; no normal client discovery or event run is claimed. |
| Gemini CLI | Skills, agents, and hooks | Public file/protocol checks; trust and normal event delivery remain unverified. |
| Claude Code, Cursor | Skills only | Native verification deferred for initial release; loading remains unverified. Do not select agent or hook assets. |
| OpenCode | Skills only | Native skill/reference verification remains required on an authorized non-Windows host. Do not select agent or hook assets. |
| macOS | POSIX mutation path | Public installer suite passes 100 cases on Python 3.14.6; normal client behavior is separate. |
| Linux | Intended POSIX target | Native OS acceptance and Python 3.11 validation remain incomplete. |
| Windows | Preview/status available; mutation and recovery fail closed | Native Windows backend and acceptance remain incomplete. PowerShell on macOS is not Windows proof. |

The final public 100-case run passed on Python 3.14.6. Separate clone checks covered two clone cases; a genuine prior paired-record migration and malformed-format refusal also passed. These checks cover file and protocol behavior. They do not replace native OS jobs, an actual Python 3.11 run, or normal client trust, discovery, and event acceptance. Milestones 6 and 7 remain in progress until those gates are met.

The available native Windows validation host has only Copilot CLI and Gemini CLI; installing other providers there is prohibited. Windows native client acceptance is limited to those two clients and has not yet run. Codex CLI, Copilot VS Code, and OpenCode require native proof on authorized non-Windows hosts; their Windows loading remains unverified. Claude Code and Cursor native verification is explicitly deferred for the initial release on every OS, with skills-only rendering and automated file tests retained. All Windows installer, recovery, clone, and direct launcher tests remain required; those tests do not require installing provider clients. This validation allocation does not make the unfinished Windows mutation backend supported.

The [catalog audit](catalog-audit.md) is the historical milestone-2 dependency inventory; use `list` against the current source for current availability and installability. See [current client validation](client-validation.md) for measured rendering/protocol evidence and [the ExecPlan](ExecPlan.md) for remaining acceptance gates.
