# Generate checked-in provider-local hook scripts

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept current as work proceeds. Maintain this document according to the repository-local `exec-plans` skill at `.agents/skills/exec-plans/SKILL.md`.

## Purpose / Big Picture

Copilot, Gemini, and repository-local GitHub hooks currently contain large copies of the same Python logic. A maintainer must repeat changes across provider trees, and security or reliability fixes can drift. After this plan, maintainers edit one canonical source for each selected hook family, run one explicit generator command, and commit readable provider-local outputs. Each provider still executes an independent local Python file, so installation and runtime isolation do not change.

The observable workflow will be:

    python3 scripts/generate-hooks.py --write
    python3 scripts/generate-hooks.py --check

The first command renders all declared hook families through an all-or-nothing write transaction. The second performs no filesystem writes and exits successfully only when every checked-in output is current. Running `python3 scripts/test-all.py` will include the freshness and generator test suite. Existing provider hook suites will continue proving provider-specific envelopes, failure modes, event handling, installation, and security behavior.

This plan covers a low-risk pilot followed by the high-value duplicate families: shared common and audit helpers, observability, Tool Guardian, secret scanning, and source auto-ingest. It does not migrate Codex or provider required-skill loaders, RTK forwarders, OKF adapters, audit-versus-observability primitives, YAML parser variants, `.github/hooks/scripts/validate-stop.py`, or `.copilot/hooks/scripts/bell.py`. The final milestone reassesses those deferred candidates using evidence from the completed generator.

## Progress

- [x] (2026-09-17 05:25Z) [milestone-1] Add generator architecture, CLI, tests, documentation, and the `send-event.py` pilot.
- [ ] [milestone-2] Generate Copilot, Gemini, and GitHub common and audit helpers without changing runtime behavior.
- [ ] [milestone-3] Generate Copilot and Gemini observability helpers without changing runtime behavior or latency expectations.
- [ ] [milestone-4] Generate Copilot and Gemini Tool Guardian scripts, remove owned local duplicates, and complete independent security review.
- [ ] [milestone-5] Generate Copilot and Gemini secret scanners, remove owned local duplicates, and complete independent security review.
- [ ] [milestone-6] Generate GitHub and Gemini auto-ingest engines and wrappers while preserving manifest and gate behavior.
- [ ] [milestone-7] Finish repository-wide validation, classify drift, update durable documentation, and publish the Phase 2 recommendation.

## Surprises & Discoveries

- Observation: No checked-in hook generator or freshness checker exists today.
  Evidence: Provider hook trees contain independently maintained scripts. The closest precedent is `scripts/install-codex-agents.py`, which emits generated headers, compares bytes, validates rendered TOML, uses atomic writes, and tests idempotence, but its generated files live in an installation target rather than this repository.

- Observation: Runtime isolation is an intentional architecture constraint, not accidental duplication.
  Evidence: `docs/adr/0001-auto-ingest-runtime-shape.md` and `.agents/instructions/hooks.md` require provider-local executable logic and prohibit cross-runtime imports. This plan shares build-time source only; generated runtime files remain local and self-contained.

- Observation: CLI guidance has one stream-placement disagreement.
  Evidence: `.agents/sources/12-factor-cli-apps.md` and `.agents/sources/clig-dev.md` put warnings and progress on standard error, while `.agents/sources/cli-design-guidelines.md` suggests warnings on standard output. This plan chooses standard error for warnings and progress so redirected standard output remains automation-safe.

- Observation: A real-home installer smoke test cannot run in this agent environment.
  Evidence: `./scripts/install.sh` stopped while copying to `/root/.agents/skills/addy-code-review-and-quality/SKILL.md` with `Read-only file system`. The targeted installer fixture and both observability suites passed, including installed-copy execution in their temporary homes.

## Decision Log

- Decision: Maintain canonical hook-family sources under top-level `hooks/` and commit generated provider-local outputs.
  Rationale: This removes duplicate human maintenance without weakening provider runtime isolation or making installation depend on generation.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Use small Python family renderers and explicit provider adapter blocks, not a general template language, runtime shared library, or textual search-and-replace.
  Rationale: Family renderers use only the standard library, keep provider differences visible, and can produce complete readable Python files deterministically.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Generated outputs are never edited directly and carry a source path plus do-not-edit header immediately after the shebang.
  Rationale: Ownership must be visible in ordinary diffs. The added comment is an accepted formatting-only change during initial migration.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Require one explicit CLI action, `--write` or `--check`; bare invocation prints help and exits `2` without mutation.
  Rationale: State changes must be explicit and automation must have a zero-write verification mode.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Preserve every current provider behavior during extraction. Evaluate observed drift immediately after each family migration, but implement confirmed fixes in separate tasks or diffs.
  Rationale: Structural equivalence and behavior correction need independent proof and rollback boundaries. Confirmed security or correctness defects block the next milestone; documented intentional or low-risk differences do not.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Migrate one independently verifiable family group at a time, beginning with byte-identical `send-event.py` as the generator pilot.
  Rationale: The pilot proves CLI, generation, freshness, headers, modes, and transactional writes before large or security-sensitive modules move.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Never delete stale generated outputs automatically.
  Rationale: Provider directories also contain handwritten scripts. The generator may report a previously generated but undeclared output, but removal requires an explicit reviewed repository edit.
  Date/Author: 2026-09-17, user and Codex.

- Decision: Record the architecture in `docs/adr/0004-generated-provider-hooks.md`.
  Rationale: Build-time canonical sharing beside a strict runtime-isolation rule is consequential and surprising without context.
  Date/Author: 2026-09-17, user and Codex.

- Decision: The milestone-one manifest declares only the two `send_event` outputs.
  Rationale: The generator must never claim ownership of a future family's handwritten files. Subsequent milestones extend the explicit manifest at the same time as they add a renderer and generated output.
  Date/Author: 2026-09-17, Codex.

## Outcomes & Retrospective

Milestone 1 introduced a deterministic standard-library generator, its two-file explicit manifest, transactional write/check behavior, and the `send-event.py` pilot. Both generated scripts retain their previous runtime body with only the ownership header added. Generator CLI and transaction tests, aggregate-registry tests, both observability suites, and the shell installer fixture passed. A direct real-home install remains unverified because this environment's `/root/.agents/skills` destination is read-only; temporary-home installed-copy tests passed. At completion, summarize the number of maintained duplicate lines removed, generated outputs owned, drift defects fixed separately, validation results, generator usability, and the disposition of every deferred candidate. Compare renderer complexity against maintenance savings before recommending Phase 2.

## Context and Orientation

Repository root is `/Users/adam/dev/skills`. Run every command in this plan from that directory unless a step says otherwise.

A hook family is one logical behavior emitted for multiple providers. A provider adapter is the small provider-specific portion of that behavior, such as Copilot's `permissionDecision` response versus Gemini's `decision` response. A generated output is a checked-in Python script under a provider directory. It is executable runtime source, but humans change its canonical family renderer rather than the output itself. Freshness means the bytes produced from canonical sources exactly match the checked-in output bytes.

Current provider areas are:

- `.copilot/hooks/scripts/` for installed Copilot hooks.
- `.gemini/hooks/scripts/` for Gemini hooks.
- `.github/hooks/scripts/` for repository-local Copilot and GitHub hook behavior.
- `.codex/hooks/` for Codex hooks. Codex is outside this phase.

General hook contracts live in `.agents/instructions/hooks.md`. Source auto-ingest contracts live in `.agents/instructions/hooks-auto-ingest.md`. Observability contracts live in `.agents/instructions/hooks-observability.md`. CLI and helper-script rules live in `.agents/instructions/scripts.md`. Test commands live in `.agents/memory/testing/hooks.md`, `.agents/memory/testing/scripts.md`, and focused sibling files. `scripts/install.sh` copies maintained provider hooks into installed locations, while `.github/hooks/` executes from the checkout. Generated outputs must therefore stay checked in and keep their present paths.

The canonical tree to add is:

    hooks/
      families/
        __init__.py
        send_event.py
        common.py
        audit.py
        observability.py
        tool_guard.py
        scan_secrets.py
        auto_ingest.py
      __init__.py
      manifest.py
      providers.py

The generator and its tests will be:

    scripts/generate-hooks.py
    scripts/test-generate-hooks.py

`hooks/providers.py` defines immutable provider data and adapter source blocks. `hooks/manifest.py` defines the complete owned output map and executable modes. Each `hooks/families/*.py` module exposes a deterministic renderer for one family. `scripts/generate-hooks.py` is a thin CLI and transaction boundary; business rendering rules stay in family modules.

The exact Phase 1 target matrix is:

- `send_event`: `.copilot/hooks/scripts/send-event.py` and `.gemini/hooks/scripts/send-event.py`.
- `common`: `.copilot/hooks/scripts/helpers/common.py`, `.gemini/hooks/scripts/helpers/common.py`, and `.github/hooks/scripts/helpers/common.py`.
- `audit`: `.copilot/hooks/scripts/helpers/audit.py`, `.gemini/hooks/scripts/helpers/audit.py`, and `.github/hooks/scripts/helpers/audit.py`.
- `observability`: `.copilot/hooks/scripts/helpers/observability.py` and `.gemini/hooks/scripts/helpers/observability.py`.
- `tool_guard`: `.copilot/hooks/scripts/tool-guard.py` and `.gemini/hooks/scripts/tool-guard.py`.
- `scan_secrets`: `.copilot/hooks/scripts/scan-secrets.py` and `.gemini/hooks/scripts/scan-secrets.py`.
- `auto_ingest`: `.github/hooks/scripts/helpers/auto_ingest.py`, `.gemini/hooks/scripts/helpers/source_ingest.py`, `.github/hooks/scripts/auto-ingest-source.py`, `.gemini/hooks/scripts/auto-ingest.py`, `.github/hooks/scripts/inject-auto-ingest-context.py`, and `.gemini/hooks/scripts/inject-auto-ingest-context.py`.

The owning family migration also removes small duplication inside that boundary: repeated allowlist parsing in Tool Guardian and secret scanning, repeated Copilot secret-scanner denial construction, repeated auto-ingest manifest refresh sequences, and repeated auto-ingest audit wrappers. These removals happen in canonical sources and generated results, not through handwritten output edits.

Implementation is large enough to require subagent orchestration. The coordinator owns `hooks/providers.py`, `hooks/manifest.py`, `scripts/generate-hooks.py`, `scripts/test-generate-hooks.py`, `scripts/test-all.py`, this ExecPlan, the ADR, and final documentation. A family worker owns only its assigned `hooks/families/<family>.py`, the generated provider outputs listed for that family, and that family's targeted test edits. Family migrations run sequentially because they share provider outputs and behavior contracts. A separate validation or security-review agent remains read-only and reports findings before the coordinator accepts a milestone. Workers must be told that other agents share the worktree and must not revert others' edits.

## Plan of Work

All implementation follows test-first development. Before changing a family, add or identify characterization tests that fail when the current provider-specific behavior changes. First prove generator behavior with failing tests, then implement the smallest generator behavior to pass, then refactor canonical sources without weakening provider tests.

### Milestone 1: Build the generator and prove it with `send-event.py`
Status: done
Acceptance: met (repository and temporary-home installed-copy proof; real-home install unavailable in this environment)

Add `hooks/providers.py` with immutable provider identifiers and explicit adapter data. Add `hooks/manifest.py` with a `GeneratedTarget` record containing family name, provider name, repository-relative output path, and mode `0o755`. Reject duplicate output paths and paths outside the declared provider hook trees. Add `hooks/families/send_event.py` as the first renderer.

Add `scripts/generate-hooks.py` using `argparse` with abbreviation disabled and a required mutually exclusive `--write` or `--check` action. Both `-h` and `--help` exit `0`. Put examples near the start of help. Bare invocation prints concise help, performs no writes, and exits `2`. Do not add prompts, color, animation, configuration files, environment-controlled behavior, JSON mode, version output, family selection, or new dependencies.

The CLI uses these stable exits: `0` for a successful write or a fresh check, `1` when `--check` finds stale or missing outputs, `2` for usage, invalid canonical source, rendering, validation, lock, or filesystem failures, and `130` for Ctrl-C. Standard output contains concise primary results and changed or stale paths. Standard error contains warnings, progress, and errors. Error text names the affected path or input and states remediation when known. The CLI never accepts secrets.

Render all declared outputs into memory before any write. Validate UTF-8, LF line endings, the shebang, the exact generated header, Python syntax with `compile`, unique contained output paths, executable mode, and absence of undeclared provider paths. Resolve repository root from `Path(__file__)`, not caller working directory. Refuse output files or parent components that are symbolic links, Windows junctions, or reparse points. Do not follow paths outside the repository.

`--check` must not create files, directories, locks, or metadata. It compares expected bytes and modes against disk, reports every stale or missing path, and reports any file carrying this generator's ownership header that is no longer declared. It never deletes such a file.

`--write` takes a bounded exclusive lock. Stage every file beside its destination, flush and sync staged content, then replace outputs atomically. Preserve original bytes and modes until every replacement succeeds. On replacement failure or Ctrl-C, restore every replaced output atomically and remove all stage and lock artifacts. Validate all sources and targets before taking the first mutating step. A second write must report no changes and leave bytes and metadata stable.

Generated files place this shape immediately after the shebang, with the concrete canonical source path substituted:

    # Generated from hooks/families/send_event.py by scripts/generate-hooks.py. Do not edit.

Add `scripts/test-generate-hooks.py`. Test `-h`, `--help`, bare invocation, mutually exclusive actions, exit codes, stream separation, no ANSI escapes, path containment, link and reparse rejection where supported, no-write checking, missing and stale outputs, undeclared owned outputs, syntax rejection before writes, exact generated headers, executable modes, deterministic rendering, idempotent writes, lock timeout, transaction rollback, Ctrl-C cleanup, and invocation from a directory outside the checkout. Tests must prove `--check` leaves a recursive filesystem snapshot unchanged.

Register `("python3", "scripts/test-generate-hooks.py")` in `scripts/test-all.py`. Generate both `send-event.py` outputs. Apart from the ownership header, their runtime code must match current bytes. Run the generator suite, both provider observability suites because `send-event.py` enters observability capture, and installer tests.

This milestone is accepted when `--check` detects a manually stale pilot output without writing, `--write` repairs it transactionally, a second write is a no-op, existing provider and installer tests pass, and a direct installed-copy smoke test still consumes JSON and emits `{}`.

### Milestone 2: Generate common and audit helpers
Status: open
Acceptance: not met

Add `hooks/families/common.py` and `hooks/families/audit.py`. Preserve all current differences explicitly in `hooks/providers.py` or named adapter blocks. Important differences include GitHub's bounded incomplete-input wait, Copilot and Gemini observability capture integration, passive logging behavior, Windows path conversion, provider environment names, default audit paths, shadow log semantics, permissions, locking, and rotation.

Before replacing outputs, add characterization cases for open stdin, multiline JSON, malformed and incomplete prefixes, buffered trailing input, UTF-8 output under non-UTF-8 host encodings, Windows path conversion, command lookup, audit lock timeouts, rotations, passive shadow modes, and `0o600` audit files. Generate the six target helper files and keep all public function names required by current imports.

Run startup, RTK, observability, auto-ingest, OKF, Tool Guardian, secret-scanner, and installer suites for all affected provider surfaces. Run mypy on same-named provider modules separately if type checking is part of the current suite; never pass duplicate module names in one mypy command.

After behavior-preserving migration, record every provider difference discovered. If evidence proves a security or correctness defect, add a failing regression test and fix it in a separate task or diff before Milestone 3. Record intentional and low-risk differences without blocking progress.

Acceptance requires byte-equivalent behavior at public stdin/stdout seams, current executable and audit modes, all targeted suites passing, and no direct edits needed in generated outputs.

### Milestone 3: Generate observability helpers
Status: open
Acceptance: not met

Add `hooks/families/observability.py` and render Copilot and Gemini helpers. Preserve runtime name, environment-variable precedence, default paths, event normalization, transcript behavior, SQLite schema and WAL use, session and span finalization, maintenance, NDJSON fallback, retention, locking, corruption recovery, and fail-open control-flow behavior. The current files align almost completely; represent the small runtime differences as named provider data rather than hidden conditionals.

Add a regression test that renders both outputs and asserts the allowed difference set. An unexpected new difference must fail with a useful message. Preserve the hot-path latency expectations documented in `.agents/instructions/hooks-observability.md`; generation must not introduce runtime template loading or new imports.

Run `bash scripts/test-hooks-observability.sh`, `bash scripts/test-gemini-hooks-observability.sh`, `bash scripts/test-hooks-startup.sh`, `bash scripts/test-gemini-hooks-startup.sh`, `bash scripts/test-install.sh`, and PowerShell installer tests when `pwsh` is available. Perform installed-copy smoke tests only after `./scripts/install.sh`, because live runtimes do not execute repository source copies.

Classify drift and handle confirmed defects separately as defined above. Acceptance requires matching database, transcript, fallback, maintenance, and installed behavior with no regression in measured hot-path budgets.

### Milestone 4: Generate Tool Guardian and remove owned policy duplication
Status: open
Acceptance: not met

Add `hooks/families/tool_guard.py`. Put shared threat detectors, encoded pattern definitions, threat aggregation, and allowlist behavior in one canonical source. Keep Copilot and Gemini payload extraction, decision envelopes, audit behavior, default paths, and fail-closed top-level handling in explicit provider adapters. Move the duplicated `parse_allowlist_csv` and `allowlist_contains` behavior into one canonical definition used in both generated scripts; generated files remain self-contained.

Before extraction, add provider-neutral matcher vectors covering every current positive, negative, boundary, multiline, encoded-threat, allowlist, malformed-input, and unexpected-exception case. Keep provider-envelope assertions separate. Avoid placing raw dangerous command strings directly in maintenance tool payloads; construct exact threat fixtures dynamically as required by `.agents/memory/known-issues/hooks.md`.

Run `bash scripts/test-hooks-tool-guard.sh`, `bash scripts/test-gemini-hooks-tool-guard.sh`, startup suites, installer suites, generator tests, and existing latency checks. Then assign an independent security reviewer read-only ownership of canonical policy, rendered outputs, failure paths, allowlist boundaries, and tests. Resolve every high-confidence security finding before acceptance. A confirmed behavior defect receives its own regression test and separate follow-up diff.

Acceptance requires identical detector outcomes across providers for shared vectors, correct provider-specific responses, fail-closed malformed and exception paths, unchanged latency compliance, and approved security review.

### Milestone 5: Generate secret scanners and remove owned response duplication
Status: open
Acceptance: not met

Add `hooks/families/scan_secrets.py`. Canonicalize Git probing, repository and candidate-file discovery, diff-added-line scanning, credential path rules, binary/text checks, redaction, allowlists, log rotation, findings construction, and mode normalization. Preserve provider-specific denial envelopes, payload keys, session fields, log paths, and audit behavior. Use the same canonical allowlist implementation chosen in Milestone 4 without creating a runtime cross-provider import.

Replace Copilot's inline missing-Git and audit-initialization denial dictionaries with the canonical response renderer so one maintained definition owns the envelope. Preserve reason text and exit `0` for expected block decisions.

Add shared detection vectors plus provider-specific public stdin/stdout tests. Retain stalling POSIX `git` and Windows `git.cmd` cases, prompt-disabled Git environment, warn-mode no-op behavior, block-mode fail-closed behavior, and sanitized logs. Use unmistakably fake credentials in fixtures.

Run `bash scripts/test-hooks-secrets-scanner.sh`, `bash scripts/test-gemini-hooks-secrets-scanner.sh`, startup suites, installer suites, and generator tests. Assign an independent security reviewer to the canonical patterns, Git subprocess boundary, output envelopes, logging, timeouts, and rendered files. Resolve high-confidence findings before acceptance, with behavior fixes separated from extraction.

Acceptance requires shared findings for equivalent inputs, provider-correct output, bounded Git operations, fail-closed block mode, warn-mode compatibility, stable log behavior, and approved security review.

### Milestone 6: Generate auto-ingest engines and wrappers
Status: open
Acceptance: not met

Add `hooks/families/auto_ingest.py`. Canonicalize source records, source hashing, frontmatter parsing, scaffold detection, blocking state, manifest reconciliation, rename and orphan handling, summary scaffolding, locking, atomic persistence, block-reason construction, and context rendering. Preserve GitHub's repository-root APIs and Gemini's payload-derived roots as provider adapters. Keep existing filenames even though GitHub uses `helpers/auto_ingest.py` and Gemini uses `helpers/source_ingest.py`.

Generate startup and prompt/final-response wrappers from canonical orchestration plus explicit provider adapters. Consolidate each repeated lock-scan-load-reconcile-save sequence into one generated helper operation. Consolidate repeated fail-open audit wrappers without changing failure policy. Preserve Gemini startup-only filtering, `BeforeAgent` and `AfterAgent` responses, stop-loop handling, GitHub transformed-prompt preservation, dynamic helper loading, stop coordination, source-ingest-first ordering, manifest location, and missing-skill recovery.

Before migration, strengthen characterization around safe previous `summary_path` handling, exact draft frontmatter semantics, body-text marker exclusion, paths containing spaces, `#`, or `?`, startup-before-prompt ordering, missing `cwd`, pending gates, simultaneous source-ingest and OKF failure reasons, and final-response backstops.

Run `bash scripts/test-hooks-auto-ingest.sh`, `bash scripts/test-gemini-hooks-auto-ingest.sh`, both OKF suites, both startup suites, installer suites, and generator tests. Because Gemini `AfterAgent` delivery is version-sensitive, repository tests prove envelopes only; retain the documented requirement for a live deployed-version probe before claiming live enforcement.

Classify drift and fix confirmed defects separately. Acceptance requires unchanged manifest bytes for equivalent inputs, matching pending-state decisions, preserved provider envelopes and ordering, safe path handling, and no cross-provider runtime imports.

### Milestone 7: Complete validation, documentation, and Phase 2 reassessment
Status: open
Acceptance: not met

Run the full maintained suite through `python3 scripts/test-all.py`. Run `python3 scripts/generate-hooks.py --check` before and after the full suite and confirm both return `0` without changing `git status`. Run `./scripts/install.sh` before live smoke tests, then verify installed scripts match checked-in generated sources and remain executable. Run `pwsh -NoProfile -File scripts/test-install.ps1` on a host with PowerShell 7; document any platform check that cannot run locally.

Update `README.md` with generator write/check commands and generated-file ownership. Update `.agents/memory/ARCHITECTURE.md` and `.agents/memory/FILE_MAP.md` for the new top-level `hooks/` source area. Update `.agents/instructions/hooks.md`, `.agents/instructions/scripts.md`, focused auto-ingest and observability instructions, `.agents/memory/API_MAP.md`, `.agents/memory/TESTING_STRATEGY.md`, and focused testing files with verified final behavior. Use `update-agent-docs` once after all code and delegated work finishes, then apply `okf-authoring` to changed `.agents/instructions/` and `.agents/memory/` Markdown. Keep `.agents/memory/INDEX.md` synchronized if a memory file is added, removed, or renamed.

Produce a Phase 2 recommendation for required-skill loaders, RTK forwarders, OKF adapters, audit-versus-observability primitives, YAML parser variants, and any newly observed candidates. Apply this admission test: at least two runtime outputs; meaningful shared logic rather than boilerplate; provider differences fit explicit adapters; runtime-local files remain necessary; and canonical generation removes more maintained complexity than the renderer adds. Do not automatically schedule every deferred candidate.

Record final duplicate-line reduction, generator source size, number of provider adapters, stale-output incidents caught, behavior defects separated and fixed, validation results, and any usability friction. Acceptance requires every approved family generated, no manual output edits, all available suites and security reviews passing, current documentation, classified drift, and a reasoned Phase 2 recommendation.

## Concrete Steps

Run commands from `/Users/adam/dev/skills`. Prefix shell commands with `rtk` unless the command must mutate files and RTK would change its behavior. The generator's write mode is itself the intended mutation, so run it directly; use RTK for reads, checks, tests, Git, and summaries.

Start each milestone by checking state:

    rtk git status --short
    rtk proxy python3 scripts/generate-hooks.py --check

During Milestone 1, the second command is expected to be unavailable until the CLI exists. After its tests fail for the intended missing behavior, implement the generator and run:

    python3 scripts/generate-hooks.py --write
    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-generate-hooks.py

Expected successful check output is concise and stable, for example:

    Generated hooks are current (2 files).

A stale check prints affected repository-relative paths to standard output and exits `1` without changing them. Usage or validation failure prints an actionable diagnostic to standard error and exits `2`.

After each family migration, run its commands from the milestone plus:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk git diff --check
    rtk git status --short

Before live installed validation:

    ./scripts/install.sh

At Phase 1 completion:

    rtk proxy python3 scripts/generate-hooks.py --check
    rtk proxy python3 scripts/test-all.py
    rtk git diff --check
    rtk git status --short

If `rtk` is unavailable, stop and report it instead of silently running raw alternatives. If PowerShell 7 or a supported live Gemini CLI is unavailable, record that exact unverified platform evidence in this plan and the final handoff.

## Validation and Acceptance

Generator CLI acceptance follows the applicable local source guidance in `.agents/sources/12-factor-cli-apps.md`, `.agents/sources/cli-design-guidelines.md`, and `.agents/sources/clig-dev.md`:

- Use `argparse`; disable ambiguous abbreviations.
- `-h` and `--help` exit `0` and describe purpose, flags, outputs, exit codes, and common examples near the beginning.
- Bare invocation explains both actions, performs no writes, and exits `2`.
- Exactly one of `--write` and `--check` is required.
- Success exits `0`; stale check exits `1`; usage or execution failure exits `2`; Ctrl-C exits `130`.
- Standard output contains primary results. Standard error contains warnings, progress, and diagnostics.
- No prompts, ANSI colors, animations, secrets, hidden configuration, or network access exist.
- Validate every render and output path before writes.
- `--check` creates, modifies, and deletes nothing, including temporary files and locks.
- Write mode reports changed paths, is deterministic, and is idempotent.
- Errors identify the problem and affected path and give remediation where known.

Family acceptance requires more than syntax. For every generated script, compare behavior through its public JSON stdin/stdout seam, provider-specific event and decision envelope, expected exit status, stderr discipline, file modes, install result, failure policy, and documented latency boundary. Existing provider suites remain authoritative unless characterization exposes an undocumented contradiction; resolve contradictions in the Decision Log before changing behavior.

Security-family acceptance additionally requires provider-neutral threat or secret-detection vectors, provider-specific envelope tests, malformed-input and unexpected-exception coverage, fail-closed block behavior, bounded subprocesses, safe logs, and independent security review with no unresolved high-confidence finding.

Phase 1 is complete only when all seven milestones show `Status: done` and `Acceptance: met`, their Progress entries are checked with timestamps, generator freshness passes, the full available suite passes, generated outputs need no manual edits, all drift is classified, confirmed blocking defects are resolved separately, documentation is current, and deferred candidates have a Phase 2 recommendation.

## Idempotence and Recovery

Rendering is deterministic. Repeated `--check` calls are read-only. Repeated `--write` calls produce no byte or mode changes after the first successful run. Family renderers depend only on checked-in canonical modules and explicit provider data; they do not read environment configuration or caller working directory.

Write mode stages and validates the complete output set before replacement. Preserve original bytes and modes until transaction completion. If staging fails, remove stages and leave outputs unchanged. If replacement fails, restore every already replaced file atomically, remove stages, release the bounded lock, print the failed path and recovery status, and exit `2`. If Ctrl-C arrives, report interruption immediately, perform bounded rollback and cleanup, and exit `130`; a repeated interrupt may skip slow cleanup, so the next run must detect and safely remove only generator-owned stale stage artifacts.

The generator never deletes a checked-in output. If `--check` reports an undeclared file with this generator's ownership marker, inspect its Git history and remove it through an explicit reviewed patch only when intended. Never broaden cleanup to a provider directory.

If a family migration fails validation, keep canonical and generated changes scoped to that family and restore the last known-good family diff. Do not weaken, delete, skip, or disable failing tests. Do not mix a behavior correction into the extraction retry. Record the failed approach and evidence in `Surprises & Discoveries` before trying a materially different renderer shape.

## Artifacts and Notes

The technical-debt audit measured these aligned-line baselines:

- Observability: 2,069 aligned lines out of 2,077 in each provider file.
- Secret scanning: 567 aligned lines across 595 Copilot and 577 Gemini lines.
- Tool Guardian: 312 aligned lines across 372 Copilot and 347 Gemini lines.
- Common helpers: 282 aligned Copilot/Gemini lines, with about 260 shared with GitHub.
- Audit helpers: 157 aligned Copilot/Gemini lines.
- Auto-ingest engine: 641 aligned lines across 678 GitHub and 698 Gemini lines.
- `send-event.py`: 21 byte-identical lines.

Use these numbers only as baseline evidence. Completion is based on maintained-source reduction and behavior proof, not maximizing deleted lines.

The architecture decision is recorded in `docs/adr/0004-generated-provider-hooks.md`. Do not supersede `docs/adr/0001-auto-ingest-runtime-shape.md`; generated canonical inputs preserve its runtime-local executable boundary.

## Interfaces and Dependencies

Use Python's standard library only. Do not add packages. The generator supports the Python versions already supported by repository scripts and Windows installer tests.

In `hooks/providers.py`, define an immutable provider record with stable fields needed by renderers. Keep fields semantic rather than exposing arbitrary textual replacements. A representative interface is:

    @dataclass(frozen=True)
    class Provider:
        name: str
        hook_root: PurePosixPath
        runtime_home_name: str

Provider-specific source blocks may use additional typed records per family when one generic record would become a bag of optional values.

In `hooks/manifest.py`, define:

    @dataclass(frozen=True)
    class GeneratedTarget:
        family: str
        provider: str
        output_path: PurePosixPath
        mode: int = 0o755

    def targets() -> tuple[GeneratedTarget, ...]: ...

The manifest owns only the explicit Phase 1 paths listed in Context and Orientation. It does not discover whole directories and does not delete anything.

Each module in `hooks/families/` exposes:

    def render(provider: Provider, target: GeneratedTarget) -> str: ...

`render` returns a complete Python file with LF endings, terminal newline, shebang, generated header, and readable provider-local implementation. It performs no I/O and reads no environment variables. If a family emits several distinct entrypoint shapes, expose named pure render functions and dispatch explicitly from the family module rather than using hidden mode flags.

In `scripts/generate-hooks.py`, keep rendering and validation callable from tests. Define interfaces equivalent to:

    def render_all(repo_root: Path) -> tuple[RenderedOutput, ...]: ...
    def check_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> CheckResult: ...
    def write_outputs(repo_root: Path, outputs: tuple[RenderedOutput, ...]) -> WriteResult: ...
    def main(argv: Sequence[str] | None = None) -> int: ...

Use immutable result records so the CLI layer formats output without mixing stream decisions into rendering or transactions. `render_all` and `check_outputs` are non-mutating. `write_outputs` is the only mutation boundary.

Do not make installers generate repository sources. `scripts/install.sh` and `scripts/install.ps1` continue copying checked-in provider-local files. Their tests must prove generated files install unchanged with executable modes.

Revision note, 2026-09-17: Initial ExecPlan created from the confirmed grilling design. It records canonical generation, explicit CLI behavior, transactional safety, migration order, validation, drift separation, security review, and Phase 2 reassessment.

Revision note, 2026-09-17: Completed Milestone 1. The pilot now renders the two provider-local `send-event.py` scripts; the generator test suite covers CLI, freshness, headers, output modes, path defenses, lock timeout, rollback, interruption cleanup, and external working directories. Targeted provider and installer fixture suites passed; the real-home install attempt is recorded above because its destination is read-only.
