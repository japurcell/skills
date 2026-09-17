# Install shared custom agents for Codex

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must stay current as work proceeds. Maintain this document according to the repository's `exec-plans` skill.

## Purpose / Big Picture

The repository currently maintains each custom agent once in `agents/*.md`, then copies those Markdown files into the personal GitHub Copilot and Gemini agent directories. Codex local clients cannot read that Markdown format directly. Codex personal custom agents are standalone TOML files under the personal Codex agents directory, and each file must contain `name`, `description`, and `developer_instructions`.

After this work, running either `./scripts/install.sh` or `pwsh scripts/install.ps1` will convert every valid top-level `agents/*.md` file into a managed Codex TOML file. By default, outputs will appear under `~/.codex/agents`; when `CODEX_HOME` is set, the installer will use `$CODEX_HOME/agents`. The same Markdown files will remain the only authored instruction source for Copilot, Gemini, and Codex. A user can verify the result by parsing an installed TOML file, asking Codex CLI to spawn one of its named custom agents, and repeating that check in the desktop app.

## Progress

- [x] (2026-09-17) [milestone-0] Researched current OpenAI custom-agent requirements and existing repository installer structure.
- [x] (2026-09-17) [milestone-0] Settled format, ownership, safety, transaction, compatibility, and validation decisions with the user.
- [x] (2026-09-17 03:30Z) [milestone-1] Add failing converter tests for valid conversion, strict parsing, exact body preservation, collisions, ownership, cleanup, locking, links, and rollback.
- [x] (2026-09-17 03:30Z) [milestone-1] Implement `scripts/install-codex-agents.py` with no third-party dependencies.
- [x] (2026-09-17 03:30Z) [milestone-1] Run direct converter tests and Python syntax checks successfully.
- [x] (2026-09-17 03:42Z) [milestone-2] Add failing Bash and PowerShell installer integration assertions.
- [x] (2026-09-17 03:42Z) [milestone-2] Integrate converter into `scripts/install.sh` and `scripts/install.ps1` before existing copy operations.
- [x] (2026-09-17 03:42Z) [milestone-2] Register the direct converter suite in `scripts/test-all.py` and update runner-registry expectations.
- [x] (2026-09-17 03:42Z) [milestone-2] Pass Bash, PowerShell, aggregate-runner, and full maintained test suites.
- [x] (2026-09-17 03:53Z) [milestone-3] Update human documentation and canonical agent memory for the new install flow, ownership boundary, and validation commands.
- [x] (2026-09-17 03:53Z) [milestone-3] Run real installation through Codex conversion; parse all 19 generated TOML files with exact decoded instruction comparisons and record CLI version `codex-cli 0.154.0`.
- [ ] [milestone-3] Run the manual fresh CLI-session `code-reviewer` spawn smoke check and inspect `/agent`; it requires an interactive paid-model session and was not automated.
- [ ] [milestone-3] Run the manual desktop-app `code-reviewer` spawn smoke check; `/Applications/Codex.app/Contents/Resources/codex` is unavailable in this environment, so no bundled desktop version or discovery result exists.
- [x] (2026-09-17 03:53Z) [milestone-3] Run the mandatory `update-agent-docs` and OKF passes and synchronize this plan's progress, evidence, and retrospective.

## Surprises & Discoveries

- Observation: Codex does not document a per-agent Markdown include or `developer_instructions_file` setting. Its `config_file` setting also points to TOML, so copying or symlinking existing Markdown agents cannot provide direct reuse.
  Evidence: Current OpenAI custom-agent documentation requires standalone TOML with `name`, `description`, and `developer_instructions`.

- Observation: Personal custom agents are documented at `~/.codex/agents`, while official environment documentation says `CODEX_HOME` is a root used by Codex installers without explicitly stating that agent discovery follows `$CODEX_HOME/agents`.
  Evidence: The implementation will use `${CODEX_HOME:-$HOME/.codex}/agents`, but live desktop behavior with an overridden `CODEX_HOME` remains an environment-specific verification item.

- Observation: The desktop app and CLI can bundle different Codex versions.
  Evidence: OpenAI troubleshooting guidance provides separate version commands for `codex` and `/Applications/Codex.app/Contents/Resources/codex`.

- Observation: Existing Copilot and Gemini agent installation copies whole trees and does not remove stale installed agents. This plan intentionally does not change that behavior.
  Evidence: `copy_agents` in `scripts/install.sh` and `Copy-Agents` in `scripts/install.ps1` copy `agents/` recursively without an ownership manifest.

- Observation: The real Bash installer completes Codex conversion before it reaches the read-only global skills target.
  Evidence: `./scripts/install.sh` reported `Codex agents: 19 installed, 0 updated, 0 unchanged, 0 removed.` and then failed copying `/root/.agents/skills/addy-code-review-and-quality/SKILL.md` with `Read-only file system`.

- Observation: This environment has CLI Codex but no desktop bundle executable.
  Evidence: `codex --version` returned `codex-cli 0.154.0`; `/Applications/Codex.app/Contents/Resources/codex` was unavailable.

- Observation: Repository installer tests already use isolated fixture repositories and redirected home directories. The Codex hook merger already demonstrates same-directory temporary files, `fsync`, `os.replace`, owner-only modes, and link refusal.
  Evidence: `scripts/test-install.sh`, `scripts/test-install.ps1`, and `scripts/install-codex-hooks.py` provide patterns to follow.

- Observation: This environment provides `python3` but no `python` executable, and the RTK Python wrapper cannot execute the plan's `python` spelling.
  Evidence: `rtk proxy python scripts/test-codex-agents.py` reported `python: No such file or directory`; `rtk proxy python3 scripts/test-codex-agents.py` ran the suite successfully.

## Decision Log

- Decision: Keep `agents/*.md` as the only authored custom-agent source and generate Codex TOML during installation.
  Rationale: Codex requires TOML, but generated adapters avoid maintaining duplicate instruction bodies.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Install personal agents only; do not commit generated project agents under `.codex/agents`.
  Rationale: Personal installation matches current Copilot and Gemini behavior and avoids committed generated duplicates plus trusted-project requirements.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Use `${CODEX_HOME:-$HOME/.codex}/agents` as the destination and never install duplicate copies into both roots.
  Rationale: This follows the documented default while respecting the environment root used by Codex installers. Desktop behavior with a nondefault root must remain labeled unverified until smoke-tested.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Convert every top-level `agents/*.md` regular file, ignore non-Markdown entries and nested directories, reject source symlinks and other non-regular Markdown entries, and preserve hard-linked regular files as readable sources.
  Rationale: The repository's current authored agents are flat. Refusing links prevents instruction import from outside the repository without inventing recursive output rules.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Copy each instruction body exactly as UTF-8 text after the closing frontmatter delimiter, including leading blank lines, LF or CRLF sequences, and the final newline. Reject UTF-8 BOM and whitespace-only bodies.
  Rationale: Exact decoded content provides maximum provider reuse and prevents silent instruction changes.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Parse a strict dependency-free frontmatter subset containing exactly one single-line `name` and one single-line `description`.
  Rationale: The repository only needs these fields, and adding a YAML dependency is prohibited without approval. Plain scalars, JSON-style double-quoted strings, and YAML-style single-quoted strings with doubled apostrophes are supported. Inline comments, block values, arrays, tags, aliases, duplicates, unknown keys, empty values, and malformed delimiters are rejected. `#` remains literal in a plain scalar.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Reject case-folded duplicate source output filenames and agent names. Reject names equal to Codex built-ins `default`, `worker`, or `explorer`, case-insensitively.
  Rationale: This produces the same behavior on case-sensitive and case-insensitive filesystems and prevents accidental global shadowing.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Do not generate model, reasoning, sandbox, MCP, skill, or provider-specific overlay settings.
  Rationale: Omitting optional settings lets agents inherit parent runtime policy and keeps the canonical Markdown portable.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Manage generated files with a versioned owner-only JSON manifest containing source filename, generated filename, and agent name.
  Rationale: The manifest permits safe stale cleanup without deleting unrelated personal agents. Unknown or malformed manifest state causes a no-mutation failure.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Refuse conflicts with unmanaged output paths or case-folded agent names discovered by recursively parsing unmanaged TOML below the destination. Malformed unmanaged TOML also blocks installation.
  Rationale: Codex recursively discovers agent TOML. Continuing when ownership or identity cannot be proven could overwrite user work or create ambiguous routing.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Refuse symlinked destination root, manifest, lock, managed output, and conflicting unmanaged TOML paths.
  Rationale: Installation must not write through links to paths outside the intended Codex directory.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Validate all sources and destinations before changing managed output. Stage new files, back up affected managed files, apply atomic per-file replacements, write the manifest last, and restore on caught failures.
  Rationale: A malformed source must never create a partial Codex update. Per-file atomic replacement plus rollback gives all-or-nothing behavior for handled errors while preserving unmanaged files.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Use an owner-only lock file containing process ID and creation time. Existing lock state blocks installation and includes manual recovery guidance.
  Rationale: Cross-platform automatic process-liveness detection is unreliable. Safe refusal is preferable to concurrent mutation or blind stale-lock deletion.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Scope transaction guarantees to Codex agent generation. Run the converter before existing copy and hook operations, but do not redesign the entire multi-provider installer as one transaction.
  Rationale: Early conversion catches invalid agents before unrelated copying. Whole-installer rollback is a separate architectural change.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Leave stale Copilot and Gemini cleanup outside this change.
  Rationale: Changing existing providers expands behavior beyond the requested Codex support.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Do not add an ADR.
  Rationale: Generated format adapters are isolated and reversible; the ExecPlan and durable installer documentation adequately explain the trade-off.
  Date/Author: 2026-09-17, user and Codex.

## Outcomes & Retrospective

Milestone 1 added a dependency-free converter and public-subprocess unittest suite. The converter accepts strict two-field Markdown frontmatter, preserves decoded instruction bodies exactly in TOML, protects unmanaged destination files through manifest ownership and collision checks, and uses same-directory staging, an exclusive lock, fsync-backed replacement, and caught-error rollback. Direct validation completed with `python3 -m py_compile scripts/install-codex-agents.py scripts/test-codex-agents.py` and `python3 scripts/test-codex-agents.py` (13 passing tests). A separate temporary-destination run converted all 19 current top-level agents and parsed each generated TOML document with an exact instruction-body comparison. Milestones 2 and 3 remain open.

Milestone 2 invokes the converter before either installer creates or copies existing provider assets. Both installer suites now validate generated TOML, manifest ownership, Unix modes where applicable, idempotence, malformed-source early failure, and the `CODEX_HOME` destination override. The direct converter suite is registered in the aggregate runner. Validation passed with Bash and PowerShell syntax checks, direct converter and runner tests, `./scripts/test-all.py --list`, and the full maintained suite. Milestone 3 remains open.

Milestone 3 documents the canonical Markdown source, provider-specific destinations, strict converter contract, manifest ownership, no-manual-edit rule, stale-cleanup boundary, and targeted validation. The documentation and knowledge-base pass updated `README.md`, the non-protected `AGENTS.md` introduction, architecture/file/API maps, agent and installer conventions, targeted testing guidance, and the read-only installer recovery note. `python3 -m py_compile scripts/install-codex-agents.py scripts/test-codex-agents.py`, the 13-test converter suite, Bash syntax check, Bash and PowerShell installer suites, the 14-test aggregate-runner suite, `./scripts/lint-okf.py`, and `./scripts/test-all.py` all passed; the full aggregate result was 25 passed and 0 failed in 85.9 seconds. The real Bash installation created 19 managed TOML agents under `/root/.codex/agents`, and a direct parse compared every decoded `developer_instructions` value with its source body exactly. The subsequent skill copy stopped at a read-only path under `/root/.agents/skills`; a direct byte comparison nevertheless confirms that `skills/execplan-implement/SKILL.md` matches its installed copy. CLI version evidence is `codex-cli 0.154.0`; the desktop executable is unavailable. The remaining CLI and desktop agent-spawn checks are intentionally pending because they require interactive client sessions and must not be automated through paid model calls. Milestone 3 is in progress and its acceptance remains unmet pending those manual checks.

## Context and Orientation

`agents/` contains the canonical Markdown custom agents. Each top-level file starts with YAML-like frontmatter containing `name` and `description`; the remaining Markdown is the agent's instructions. `scripts/install.sh` currently copies the entire directory into `~/.gemini/agents` and `~/.copilot/agents`. `scripts/install.ps1` is the PowerShell 7 equivalent and must retain behavioral parity.

`scripts/install-codex-hooks.py` is an existing standard-library Python installer helper. It is not an agent converter and must not be repurposed, but its safe-write approach is the local model for `mkstemp`, owner-only file permissions, flushing, `fsync`, `os.replace`, directory synchronization where available, and cleanup.

`scripts/test-install.sh` and `scripts/test-install.ps1` create temporary repository fixtures, redirect the user's home directory, invoke their corresponding installer as a child process, and assert installed output. Both fixtures must copy any new helper script into the temporary repository. `scripts/test-all.py` holds an explicit `SUITES` tuple rather than discovering tests. Adding a maintained suite therefore requires both registering it and updating `scripts/test_test_all.py` if its registry-count or expected-command assertions change.

Codex calls a delegated worker a custom agent or subagent. A personal custom agent is a TOML file under the personal Codex agents directory. The generated filename is only a filesystem convention; the TOML `name` value is the runtime identity. This plan maps `agents/foo.md` to `foo.toml` while preserving the frontmatter `name` independently.

The new ownership manifest will be named `.skills-repo-agents.json`. It is not TOML, so Codex will not discover it as an agent. Schema version 1 will contain an `agents` array. Each entry will contain `source`, `output`, and `name`, all as relative basenames. The new lock will be `.skills-repo-agents.lock`. Generated agent files will begin with a comment stating that `agents/*.md` is canonical, followed by deterministic `name`, `description`, and `developer_instructions` assignments. Use JSON-compatible TOML basic-string escaping and validate every rendered document with Python's `tomllib` before staging it.

The lock prevents concurrent installer runs, but no portable collection of file replacements is atomic across a process crash or power loss. The implementation must provide no partial change for validation failures and must roll back caught apply failures. It must write the manifest last so an interrupted run remains safe to retry after the user confirms no installer is active and follows the diagnostic recovery steps. Document this precise boundary instead of claiming impossible crash-level atomicity.

## Plan of Work

### Milestone 1: Specify and implement the converter
Status: done
Acceptance: met

Create `scripts/test-codex-agents.py` first using `unittest`, temporary directories, and only the Python standard library. Exercise the converter as a public subprocess, not only imported functions, so exit codes and stream placement remain covered. Initial tests must fail because `scripts/install-codex-agents.py` does not exist.

Cover valid plain, double-quoted, and single-quoted frontmatter. Include Unicode, quotes, backslashes, dollar signs, a literal triple-quote sequence, leading blank lines, final-newline presence and absence, LF, and CRLF bodies. Parse emitted TOML with `tomllib` and assert that `developer_instructions` equals the exact source body. Assert deterministic bytes and owner-only mode where Unix modes are available.

Cover missing or duplicate fields, unknown metadata, unsupported YAML forms, bad delimiters, UTF-8 BOM, invalid UTF-8, empty body, reserved built-in names, duplicate and case-folded duplicate names, case-folded output filenames, source symlinks, non-directory arguments, and inaccessible paths. Each validation failure must return nonzero, explain the exact source or destination on stderr, produce no success summary on stdout, and leave destination content unchanged.

Cover first install, idempotent reinstall, source update, source deletion, empty source set, recreation of a missing managed output, preservation of unrelated files, stale removal limited to manifest-owned files, and deterministic manifest bytes. Cover malformed and unknown-version manifests, manifest path links, lock path links, active lock refusal, output links, destination-root links, unmanaged path collisions, unmanaged name collisions in nested TOML, malformed unmanaged TOML, and case-folded unmanaged collisions. Inject an apply failure after at least one replacement through a test seam and prove rollback restores managed files and manifest.

Then create executable `scripts/install-codex-agents.py`. Its command line requires `--source-dir` and `--destination-dir`; `-h` and `--help` are reserved for help. Successful installation prints one concise stdout summary containing installed, updated, unchanged, and removed counts. Status, warnings, and errors go to stderr. Normal success returns 0, expected validation or installation failure returns 1, and argparse usage failures retain exit 2.

Use small explicit data structures such as frozen `AgentDefinition`, `ManifestEntry`, and `InstallPlan` dataclasses. Provide functions with responsibilities equivalent to:

    parse_agent(path: Path) -> AgentDefinition
    discover_sources(source_dir: Path) -> list[AgentDefinition]
    read_manifest(destination_dir: Path) -> Manifest
    inspect_unmanaged_agents(destination_dir: Path, managed_outputs: set[str]) -> dict[str, Path]
    build_install_plan(source_dir: Path, destination_dir: Path) -> InstallPlan
    apply_install_plan(plan: InstallPlan) -> InstallSummary
    main(argv: Sequence[str] | None = None) -> int

Names may differ from this outline if tests show a clearer interface, but parsing, planning, and mutation must remain separated. Open source files with UTF-8 and newline preservation. Detect BOM before parsing. Locate the first closing delimiter line after the required opening delimiter and treat all following text as the body. Do not normalize line endings or trailing newlines.

Render TOML in stable key order. Encode strings with a helper whose output is valid both as a TOML basic string and for arbitrary accepted instruction text. Immediately parse each rendered file with `tomllib` and compare all three decoded fields with the source definition. Do not copy optional Codex settings.

Create the destination directory only after source preflight succeeds. Before mutation, reject exact and case-folded collisions, unsafe relative paths in manifest data, links, malformed unmanaged agent files, or existing lock state. Create the lock with exclusive file creation and mode `0600`, record PID plus UTC creation time, and remove it only when the current process created it. Stage files and backup affected managed paths under a temporary directory on the same filesystem. Use `os.replace`, file `fsync`, and directory `fsync` where supported. Apply stale removals and replacements, atomically publish the manifest last, then remove backups. If an exception occurs during apply, restore prior managed files and manifest before surfacing the error. Leave the lock and recovery evidence only when abrupt process termination prevents `finally` cleanup.

Run direct tests until all converter cases pass. Do not weaken or skip safety cases to make the suite green.

### Milestone 2: Integrate both installers and aggregate validation
Status: done
Acceptance: met

Extend `scripts/test-install.sh` and `scripts/test-install.ps1` before editing installers. Their fixture agent needs both `name` and `description`, because the new strict Codex schema requires both. Keep the nested Markdown fixture to prove Copilot and Gemini still receive nested files while Codex converts top-level files only. Copy `scripts/install-codex-agents.py` into each temporary fixture repository.

Add end-to-end assertions that the Bash and PowerShell installers create the expected `helper.toml`, manifest, and modes; parse the TOML; and compare the decoded body exactly. Run each installer twice to prove idempotence. Add focused malformed-source cases proving Codex agent conversion fails before existing Copilot, Gemini, skill, or hook copy operations begin. Add a `CODEX_HOME` override case proving the selected destination changes without duplicate output under the default home path. Keep link cases host-aware only where the host genuinely cannot create the needed link.

Modify `scripts/install.sh` to define the Codex agent helper and destination paths without repurposing `HOME`, `CODEX_HOME`, or another common system variable. Validate that the helper exists. After validating all required repository sources and creating only necessary safe parent directories, invoke:

    python3 "$CODEX_AGENT_INSTALLER" --source-dir "$AGENTS_SRC" --destination-dir "$CODEX_AGENTS_DEST"

This call must occur before `copy_skills`, `copy_agents`, hook installation, or other existing copy operations. Do not use `rtk` inside repository scripts.

Modify `scripts/install.ps1` with the same source and destination behavior. Reuse its existing explicit Python resolution pattern: select `python3` first, fall back to `py -3`, and fail clearly if neither exists. Resolve Python once and use the same executable plus prefix arguments for both agent conversion and hook merging. Invoke the converter before existing copy functions. Preserve `-NoProfile` compatibility and avoid external modules.

Add `("python3", "scripts/test-codex-agents.py")` to the maintained suite registry in `scripts/test-all.py`. Update `scripts/test_test_all.py` assertions that encode suite count or registry membership. The aggregate runner itself must remain behaviorally unchanged beyond registering the suite.

Run syntax checks, direct tests, both installer suites, and runner tests. Then run `./scripts/test-all.py --list` to confirm registration and the full aggregate suite when prerequisites are available.

### Milestone 3: Document, install, and verify local clients
Status: in progress
Acceptance: not met

Update `README.md` to say that `agents/*.md` is canonical for all three providers, Copilot and Gemini receive Markdown copies, and Codex receives generated personal TOML. Document default and `CODEX_HOME` destinations, generated-file ownership, the no-manual-edit rule, strict source requirements, stale cleanup boundary, and targeted validation commands.

Update the non-protected introductory repository summary in `AGENTS.md` only if needed to state that `.codex/` is not the source of generated custom agents. Never modify the protected `ExecPlans`, `Agent Orientation`, `End of Work Session Defined`, or `Validation Checklist` sections.

Run the mandatory `update-agent-docs` skill after implementation and tests. At minimum, reconcile `.agents/memory/ARCHITECTURE.md`, `.agents/memory/FILE_MAP.md`, `.agents/instructions/agents.md`, `.agents/instructions/scripts.md`, `.agents/instructions/powershell.md`, `.agents/memory/testing/scripts.md`, and `.agents/memory/testing/powershell.md`. Update `.agents/memory/API_MAP.md` if the converter's command-line interface qualifies as a public repository validation or installer entry point. Apply the repository's `okf-authoring` workflow to semantic changes under `.agents/instructions/` and `.agents/memory/`.

Run `./scripts/install.sh` to install real generated agents after automated tests pass. Record `codex --version`. On macOS, also record `/Applications/Codex.app/Contents/Resources/codex --version` when that executable exists. Start a fresh CLI session, ask Codex to spawn a distinct existing agent such as `code-reviewer`, and use `/agent` to confirm the named thread. Start a fresh desktop-app chat for the same checkout, request the same named agent, and inspect its subagent thread. Do not automate these smoke checks through paid model calls.

If CLI discovery succeeds but desktop discovery fails on an older bundled version, document exact versions and behavior as an environment limitation rather than changing the generated format away from current official documentation. If a nondefault `CODEX_HOME` is used, explicitly report whether each local client discovers that root; do not claim desktop support without evidence.

Finish by updating every section of this living plan. Mark each completed milestone's status and acceptance at the same time as its Progress entries. Record exact test results and smoke evidence in `Outcomes & Retrospective`.

## Concrete Steps

Run all commands from `/Users/adam/dev/skills`. Prefix interactive commands with `rtk` as required by repository instructions; commands shown below use that form where a supported wrapper exists.

First create failing direct tests, then run:

    rtk python scripts/test-codex-agents.py

Expect nonzero before the converter exists. After implementation, expect the unittest summary to report all cases passing.

Check Python syntax and direct behavior:

    rtk python -m py_compile scripts/install-codex-agents.py scripts/test-codex-agents.py
    rtk python scripts/test-codex-agents.py

Check Bash integration:

    rtk test bash -n scripts/install.sh
    rtk test bash scripts/test-install.sh

If `rtk test` does not preserve syntax-check semantics on the local RTK version, use `rtk proxy bash -n scripts/install.sh` and record why.

Check PowerShell integration:

    rtk test pwsh -NoProfile -File scripts/test-install.ps1

Check aggregate-runner changes and registry:

    rtk python scripts/test_test_all.py
    rtk python scripts/test-all.py --list

Run the full maintained suite:

    rtk test ./scripts/test-all.py

Install and inspect generated output:

    rtk ./scripts/install.sh
    rtk codex --version
    rtk read "${CODEX_HOME:-$HOME/.codex}/agents/code-reviewer.toml"

Do not use `$HOME` or `CODEX_HOME` as a shell assignment target. The final `rtk read` command only expands their existing values to inspect the resolved destination.

For manual client smoke checks, start a new CLI session in this checkout, ask it to spawn `code-reviewer` for a read-only review task, and inspect the thread with `/agent`. Repeat in a new desktop-app chat. Record versions and outcomes in this plan without copying private prompt or repository content into external systems.

## Validation and Acceptance

Milestone 1 is accepted when direct tests prove that every current top-level Markdown agent converts to parseable TOML with exact decoded instructions; strict invalid inputs fail without mutation; managed updates and removals are deterministic; unmanaged agents remain untouched; unsafe links and collisions fail; concurrent lock state fails; and injected apply failure restores prior state.

Milestone 2 is accepted when both public installers generate equivalent Codex outputs in redirected environments, nested sources remain Copilot/Gemini-only, malformed agent input stops installation before unrelated copy operations, `CODEX_HOME` selects one destination, direct converter tests appear in `scripts/test-all.py --list`, and all targeted suites pass.

Milestone 3 is accepted when docs identify one canonical source and all installed destinations, the mandatory agent-doc pass is complete, real installation produces the expected managed TOML, CLI discovery succeeds on the current client, and desktop behavior is either verified or recorded with exact version evidence as an environment limitation.

No acceptance claim may rely only on file existence. At least one test must parse generated TOML and compare decoded `developer_instructions` with exact source body text. No automated test may invoke a paid model run.

## Idempotence and Recovery

Running either installer repeatedly with unchanged sources must leave generated TOML and manifest bytes unchanged, apart from lock creation and removal during execution. Updating one source changes only its managed TOML plus manifest data if identity changed. Removing one source removes only its manifest-owned output. An empty source directory removes every manifest-owned output and preserves all unmanaged files.

Validation failures, ownership conflicts, malformed user TOML, malformed manifests, and active locks must occur before destination mutation. Caught apply errors must restore prior managed outputs and manifest. Same-directory temporary files and backups must be removed after success and after successful rollback.

An abrupt process termination may leave `.skills-repo-agents.lock` and staged or backup evidence. The diagnostic must tell the user to confirm no installer process is active before removing the lock. After resolving any partial state, rerun the same installer; manifest-last publication and deterministic generation make retries convergent. Never advise deleting the whole agents directory because it can contain unmanaged personal agents.

If a generated file needs manual correction, edit its canonical `agents/*.md` source and rerun installation. Manual edits inside manifest-owned TOML are overwritten by design.

## Artifacts and Notes

Expected generated shape, shown with abbreviated instructions:

    # Generated from agents/code-reviewer.md by scripts/install-codex-agents.py. Do not edit.
    name = "code-reviewer"
    description = "Senior code reviewer that evaluates changes..."
    developer_instructions = "\n# Senior Code Reviewer\n\nYou are...\n"

Expected manifest shape:

    {
      "version": 1,
      "agents": [
        {
          "source": "code-reviewer.md",
          "output": "code-reviewer.toml",
          "name": "code-reviewer"
        }
      ]
    }

Expected successful converter summary:

    Codex agents: 18 installed, 0 updated, 0 unchanged, 0 removed.

Exact counts may differ as repository agents change. Tests should assert structured meaning or fixture-specific counts, not freeze the live repository count.

## Interfaces and Dependencies

The implementation may use only Python standard-library modules, including `argparse`, `dataclasses`, `datetime`, `json`, `os`, `pathlib`, `shutil`, `stat`, `tempfile`, `tomllib`, and `typing`. Do not install or add dependencies.

`scripts/install-codex-agents.py` exposes this CLI:

    install-codex-agents.py --source-dir PATH --destination-dir PATH

`--source-dir` is the flat canonical Markdown directory. `--destination-dir` is the personal Codex agent directory. The helper owns only paths listed in `.skills-repo-agents.json`; all other destination entries are user-owned.

`scripts/install.sh` and `scripts/install.ps1` remain the public cross-provider installation entry points. They must resolve the destination from existing environment state without assigning to or repurposing `HOME` or `CODEX_HOME`. Their existing Copilot, Gemini, skill, reference, and hook behavior must remain unchanged.

No database, network service, schema migration, or new package is involved.

Revision note (2026-09-17): Initial ExecPlan created after official documentation research and seven grilling rounds. It records all confirmed design decisions and leaves implementation milestones open.

Revision note (2026-09-17): Milestone 1 completed with strict source conversion, manifest-owned transactional installation, and direct public-CLI tests. The `python3` interpreter spelling was used for local validation because this environment has no `python` executable.

Revision note (2026-09-17): Milestone 2 completed by placing conversion before every existing copy operation in both installers and registering its direct suite in the maintained aggregate runner.

Revision note (2026-09-17): Milestone 3 documented and validated the converter path, refreshed and exactly parsed 19 real Codex agents, and recorded CLI/desktop availability. It remains in progress because interactive CLI and desktop smoke checks were not automated. A later byte comparison confirmed that `skills/execplan-implement/SKILL.md` matches its installed copy despite the installer stopping at another read-only skill path.
