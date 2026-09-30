# Install and update selected agent assets at repository scope


This ExecPlan is a living document. Maintain `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` as work proceeds. Its repository path is `docs/agent-asset-installer/ExecPlan.md`. Follow `.agents/skills/exec-plans/SKILL.md`, including synchronized milestone status and progress checkboxes.

Planning and the six-repository review are complete. On 2026-09-29 the user accepted retaining the current architecture, strict read-only verification, and declared checkout line-ending policy. All three test seams are already accepted. The user explicitly requested implementation through `execplan-implement` on 2026-09-29, lifting the earlier hold. Implement all milestones on `codex/research-agent-distribution-options` using isolated private worktrees and serialized fast-forward integration. Native package publication remains a separate future effort.

## Purpose / Big Picture


Let a developer install selected skills, custom agents, and hooks into a project, commit actual files for teammates, and refresh them with one explicit update command. A developer can instead keep a repository installation untracked or use a personal installation. Updates remember selections, show changes, preserve unrelated files, and stop before destination writes when they would replace conflicting local edits.

Team maintainers can verify committed assets offline before CI repairs anything. Declared checkout policy keeps exact managed bytes and hashes stable across supported operating systems, so normal Git line-ending conversion does not masquerade as an intentional edit.

Success is observable from a disposable project: install a review workflow, see its skill and dependency files at native discovery paths, commit and clone the project, and discover those skills without the source checkout. Updating from source revision A to B produces a reviewable Git diff and provenance record. Editing a managed file before an incompatible update causes a conflict and leaves installation destinations unchanged.

## Progress


- [x] (2026-09-29 21:27Z) [planning] Read the closed contract, source inventory, current installer entry points, configuration merger, generated-hook manifest, and area guidance. Create this self-contained implementation plan.
- [x] (2026-09-29 21:46Z) [planning] Complete canonical routing/documentation pass. OKF lint, whitespace, 15 Markdown documents, 69 local links, seven synchronized open milestones, and four closed decisions pass.
- [x] (2026-09-29 21:50Z) [planning] User accepts public CLI/file effects, Bash/PowerShell entry points, and native discovery/hook execution as test seams.
- [x] (2026-09-29 21:50Z) [planning] Record the user's explicit instruction not to start implementation yet. All seven implementation milestones remain open.
- [x] (2026-09-29 23:47Z) [planning] Complete the six-repository comparison and record the evidence-backed recommendation without changing the approved design.
- [x] (2026-09-30 00:01Z) [planning] User accepts retaining the architecture, strict verification, and declared checkout line-ending policy on 2026-09-29 local time. Incorporate the agreed refinements; implementation remains on hold.
- [x] (2026-09-30 00:25Z) [orchestration] User explicitly requests full implementation. Lift the prior hold and start isolated milestone worktrees.
- [ ] [milestone-1] Deliver one committed, pinned skill installation through the public CLI.
- [ ] [milestone-2] Deliver asset selection, required dependencies, and curated bundles.
- [ ] [milestone-3] Deliver preview, update, recorded restoration, strict read-only verification, conflict protection, and safe pruning.
- [ ] [milestone-4] Deliver native repository adapters for Codex, Copilot CLI/VS Code, and Gemini CLI.
- [ ] [milestone-5] Deliver local and personal installations, verified adoption, and legacy entry-point integration.
- [ ] [milestone-6] Prove Windows, Linux, macOS, and installed client behavior.
- [ ] [milestone-7] Publish usage documentation, synchronize canonical knowledge, and finish acceptance.

## Surprises & Discoveries


The Bash installer derives destinations from `HOME` at `scripts/install.sh:26`. PowerShell has an empty parameter declaration at `scripts/install.ps1:29`. Neither implements selection or repository scope. Preserve personal entry points while adding one lifecycle engine.

`scripts/install-provider-hooks.py:82` recognizes maintained hooks by script names in home-relative commands. Its recursive settings merge replaces template values. Neither proves ownership for selective updates. Ownership must identify exact files and configuration entries, not basenames or directory placement.

`scripts/install.sh:163` preflights RTK and generated-hook freshness before provider JSON checks. Mutations start at `scripts/install.sh:186`, before agent conversion and copies. The new engine needs whole-operation preflight rather than a sequence of mutating helpers. Existing personal tests remain acceptance requirements.

`hooks/manifest.py:19` lists generated files. Keep renderers under `hooks/families/` and separate installed provider trees without cross-provider imports. `scripts/generate-hooks.py --check` remains a read-only installation gate.

`.codex/hooks/load-required-skills.py:232` reads only personal skills. Copilot and Gemini support skill-root overrides with different precedence. Explicit runtime configuration must select repository skills and work after a teammate relocates a clone.

The interview encountered missing `domain-modeling`. Catalog entries can describe unavailable dependencies so listing remains useful. Selecting an affected workflow must fail before writes with its dependency chain. The user's interview fallback does not authorize silently dropping distribution dependencies.

Native local configuration is uneven. Codex adds matching hooks across sources and skips untrusted project layers. Gemini documents project `.gemini/settings.json`, without project `settings.local.json`. Git excludes cannot hide tracked changes. Local mode must refuse tracked configuration writes unless a verified native local override expresses the selection. Never substitute a system layer to bypass project trust. [Official OpenAI documentation: hooks](https://learn.chatgpt.com/docs/hooks), [OpenAI project trust](https://learn.chatgpt.com/docs/config-file/config-basic), [Gemini configuration](https://geminicli.com/docs/reference/configuration/).

Two initial plan patches were blocked before mutation by Tool Guardian input limits: `46899 bytes exceeds limit 32768 bytes` and `129 segments exceeds limit 128 segments`. Write long documents with smaller independent patches below both limits. Do not disable the guard or raise its limits.

The existing-repository review found that APM supports committing generated payloads, but ordinary install overwrites managed files; ECC's tagged release also retains replacement of managed files during successful upgrades. Their ownership/configuration examples remain useful, but they do not satisfy this plan's edit/conflict contract as drop-in engines. APM's audit-only CI pattern motivates the accepted read-only `status --check`. Its line-ending normalization also exposed a design detail: Git checkout conversion can change exact payload hashes across operating systems. The accepted declared line-ending policy and narrow owned attributes preserve exact hashes. Both refinements are approved but unimplemented. Evidence and source-review limits are in [the existing-repository comparison](../agent-asset-distribution/existing-repos-review.md), [APM's audit-only guidance](https://microsoft.github.io/apm/enterprise/enforce-in-ci/#audit-only-ci-pattern), [ECC's release notes](https://github.com/affaan-m/ECC/releases/tag/v2.2.1), and [Git's attribute documentation](https://git-scm.com/docs/gitattributes).

## Decision Log


Decision: Preserve the closed contract. Full repository setup initially targets Codex, Copilot CLI/VS Code, and Gemini CLI. Claude Code, Cursor, and OpenCode initially receive skills only. Committed team setup is default. Local untracked and personal setups remain available. Support bundles and individual assets with dependencies, actual committed payloads, immutable commits/digests, explicit updates/preview, ownership-based pruning, preservation of edits, native precedence, and macOS/Linux/Windows. Hosted/cloud support and native packages require separate validation. No rollback command or retained installation history is authorized.

Rationale: These are settled user requirements, not questions to reopen. Date/author: 2026-09-29, user decisions recorded by Codex.

Decision: Use Python 3.11+ standard-library lifecycle code and retain Bash/PowerShell compatibility entry points. Expose `scripts/agent-assets.py` as the installer/updater. Git supplies acquisition and revisions. No package-manager bootstrap, remote service, marketplace, or symlink team delivery is required.

Rationale: Python already implements TOML conversion and configuration helpers. Python 3.11 provides `tomllib`. One engine concentrates safety across operating systems. Windows users can invoke `py -3` or their configured Python. Date/author: 2026-09-29, Codex planning.

Decision: Keep research at `docs/agent-asset-distribution/` and implementation planning at `docs/agent-asset-installer/`. Store new exploration findings here instead of recreating the promoted scratchpad effort.

Rationale: Preserve the closed record and the user's requested `docs/` location. Date/author: 2026-09-29, Codex planning.

Decision: Use native discovery paths, copies, and two records: desired selection and resolved ownership. Reconcile team/local records before removal. Shared files remain while another selection needs them.

Rationale: Clones carry working assets. Updating bundles preserves requested identity while recalculating membership/dependencies. Date/author: 2026-09-29, Codex planning.

Decision: Local mode writes only untracked files or verified native local overrides. Tracked shared configuration is a conflict. Offer team mode, assets without that configuration requirement, or explicit resolution of the existing target. Never use Git index flags to conceal tracked changes.

Rationale: Preserve local semantics, trust, and team policy. The contract does not promise universal personal/team isolation. Date/author: 2026-09-29, Codex planning.

Decision: Distinguish interrupted-operation recovery from version rollback. A temporary journal retains pre-write bytes only for one incomplete operation. Delete it after successful application or recovery. Expose no historical version selector.

Rationale: Recovering incomplete writes protects integrity without the excluded rollback feature. Date/author: 2026-09-29, Codex planning.

Decision: All three public test seams are accepted, but implementation remains on hold until an explicit user request. Do not write tests, source, or scaffolding yet.

Rationale: The user accepted test boundaries and separately instructed, "Don't start implementation yet." Test-scope acceptance does not authorize execution. Date/author: 2026-09-29, user instruction recorded by Codex.

Decision: Revisit the design only through evidence and a live user decision after the requested comparison with ECC, Microsoft APM, skills-lock, superpowers, wshobson/agents, and skillet. Existing implementation choices remain the baseline during research.

Rationale: The user supplied another agent's research and requested help deciding whether its discoveries justify changes before implementation. That request authorizes research and planning, not product execution or automatic contract changes. Date/author: 2026-09-29, user request recorded by Codex.

Decision: Retain the existing engine and delivery architecture after the repository comparison. Add offline, read-only `status --check` that detects selection/lock disagreement, missing files, changed file hashes, and changed owned config values without installing or fetching. Declare expected line endings for managed payloads and own narrow Git attribute entries so cross-platform clones preserve exact hashes. Preserve unrelated attributes and reject conflicting rules before writes. Do not normalize arbitrary whitespace or renormalize the repository.

Rationale: The user accepted the architecture and strict verification, then accepted the remaining checkout policy. APM/ECC lifecycle semantics differ from the approved edit/conflict rules. Checking committed files before repair exposes drift; declaring checkout policy prevents Git conversion from producing false edit conflicts. These are planning amendments, and the explicit implementation hold remains in effect. Date/author: 2026-09-29, user decisions recorded by Codex.

Decision: Execute the entire plan after the user's explicit `execplan-implement` request. Each milestone gets a fresh implementer in its own unpushed worktree. Integrate clean tested branches one at a time by rebase and fast-forward. The milestone graph is 1 -> 2 -> 3; milestone 4 depends on 2 and 3; milestone 5 depends on 3 and 4; milestone 6 depends on 4 and 5; milestone 7 depends on 6. Exploration can run beside implementation without source ownership. Live-client and native OS gates remain evidence requirements, not assumptions.

Rationale: Later explicit execution authorization lifts the prior hold. Lifecycle, provider, and scope changes share public interfaces, so their dependency order prevents incompatible independent edits. Date/author: 2026-09-29, user request recorded by Codex.

Decision: Route milestone 1 to Standard tier, `gpt-6.1-sol`, effort `high`. Connected Git acquisition, safe filesystem writes, ownership records, attributes, and public TDD require general agentic coding rather than bounded low-risk work. Exact runtime ID is available and applied. Copilot pricing is not treated as this platform's billing. Escalate after repeated safety or integration failures; fallback is `gpt-6-sol` at the same effort if unavailable.

Rationale: Standard meets the task's connected-code requirements; Premium is not justified before evidence of failure. Task-specific capability is provisional and checked through subprocess acceptance. Date/author: 2026-09-29, Codex orchestration.

## Outcomes & Retrospective


Planning, test-seam approval, and the six-repository review are complete. The user accepted retaining the architecture, strict read-only verification, and declared checkout line-ending policy. No planning question remains. Implementation is now authorized by the user's explicit execution request. Milestone 1 is in progress; milestones 2 through 7 remain open. Seven verifiable milestones cover commands, catalog/dependencies, ownership, provider constraints, personal adoption, and OS/client acceptance. No installer, installed home, runtime, or workflow has changed. Planning does not establish live support.

Planning validation on 2026-09-29: `rtk proxy ./scripts/lint-okf.py` exits `0`, `rtk git diff --check` passes, and a read-only validator checks 15 Markdown documents, 69 local links, all required plan sections, seven open milestones with matching unchecked progress, and four closed decision resolutions. Canonical edits are limited to the existing repository-instruction and file-map routing entries. No implementation test command has run.

Comparison validation on 2026-09-29: OKF lint and whitespace checks pass; a read-only validator checks 23 Markdown documents, 92 local links, seven closed ticket resolutions, the live decision's exact closed dependencies, seven open milestones, preserved canonical frontmatter, and the explicit hold. Three research agents completed their assigned files. No implementation or third-party installer/client test ran.

Accepted-refinement validation on 2026-09-29 local date: OKF lint and whitespace checks pass. A read-only validator checks 23 Markdown files, 93 local links, eight closed resolutions, no remaining planning question, seven open implementation milestones, and the exact six-document change scope. No source, test, scaffolding, or installed-state change occurred.

## Context and Orientation


Run repository commands from the root containing `AGENTS.md`, `skills/`, `agents/`, and `scripts/`. Planning starts at HEAD `6424adf06f5c08577e7848e4c63cc0bd421e73d0` on `codex/research-agent-distribution-options`. Before edits, read `.agents/memory/INDEX.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, and affected-area instructions, known issues, and testing guidance. Load `tdd` before source design or implementation. Use one failing public test, minimal implementation, and next test. Do not write all milestone tests first.

Canonical skills are `skills/<name>/` with `SKILL.md`. Canonical agents are regular top-level `agents/*.md` with `name` and `description` frontmatter. `scripts/install-codex-agents.py` converts them to TOML containing `name`, `description`, and `developer_instructions`. `hooks/manifest.py` maps renderers to generated scripts in `.codex/`, `.copilot/`, `.gemini/`, and `.github/`. Shell installers currently copy personal setups. `scripts/test-all.py` registers maintained suites. `.github/workflows/ready-ideas-windows.yml` runs native Windows acceptance.

A catalog describes assets, bundles, dependencies, clients, and runtime requirements. An asset ID uses a type prefix, such as `skill:code-review` or `hook:tool-guard`. A bundle names a curated selection. Required dependency closure means every asset needed directly or indirectly. A provider adapter translates selected source into native paths/configuration. A seam is the interface used by callers and tests. Accepted seams are command processes and native execution, not private helpers.

Provenance describes repository, full commit, digest, and renderer version. Ownership identifies the file or configuration entry the installer may change. A baseline digest describes last verified managed content. Compare current content with that baseline before replacement/removal. A lock record stores the current resolved installation. It is separate from the mutex preventing concurrent writers.

Committed records are `.agent-assets/selection.json` and `.agent-assets/lock.json`. Local records are `.agent-assets/local/selection.json` and `.agent-assets/local/lock.json`, excluded through Git's resolved `info/exclude`. Personal records are `<home>/.agent-assets/selection.json` and `<home>/.agent-assets/lock.json`. Repository records contain relative destinations and no developer-specific absolute paths. Payloads live at native discovery paths.

The closed authority is `docs/agent-asset-distribution/tickets/choose-distribution-contract.md`. Its research reports preserve comparisons. This plan embeds execution requirements. Verify native documentation and actual versions during adapter acceptance because discovery/event behavior changes independently of this code.

## Interfaces and Dependencies


Create executable `scripts/agent-assets.py` with `main(argv: Sequence[str] | None = None) -> int`, delegating to `scripts/agent_assets/cli.py`. Put selection/lifecycle behavior in `core.py`, Git acquisition in `sources.py`, and varying renderers in `providers.py` beneath the same package. Add a package initializer. These are internal modules. Avoid a generic plugin framework and private-method tests.

Commands are `list`, `install`, `update`, `restore`, and `status`, with `--help` and `--format human|json`. `list` reports client-filtered assets, availability, and dependencies without destination writes. `install` requires a client and repeatable `--asset` or `--bundle`. Defaults are `--scope repo --mode team` and current Git root, with `--repo PATH` available. `--scope user --home PATH` selects personal destinations. `--mode` is repository-only. `--home` routes tests explicitly without repurposing `HOME` or `CODEX_HOME`. Ordinary use honors native home and the existing Codex agent override. Explicit test homes must contain or reject external Codex overrides.

`install` accepts `--source PATH_OR_GIT_URL` and mutually exclusive `--branch BRANCH` or `--revision TAG_OR_COMMIT`. Default source is the command's checkout. For a local source, initially install its committed HEAD and record its named current branch for updates. An explicit branch/revision overrides that choice. For a Git URL, resolve its remote default branch. A detached local source needs an explicit branch or revision. Record a credential-free fetch URL or clearly local-only path, source policy, full commit, and digest. Acquisition never changes, resets, stashes, or commits the caller's checkout. Reject credential-bearing URLs and use Git credential handling.

Acquire revisions through argument-list Git subprocesses in disposable directories. Resolve a full commit, read catalog and selected paths from that committed tree, and materialize only validated regular files. Reject traversal and escaping links rather than extracting an unchecked archive. Reuse the existing generator's read-only check for the selected source snapshot, never generator write mode. Do not import arbitrary catalog paths as Python or execute installed hooks during installation. Renderer/schema compatibility is preflighted before destination mutation.

`update` uses saved clients, assets/bundles, source policy, and ownership. `--preview` shares planning but changes no installation files, configuration, records, or Git excludes. Disposable acquisition files outside the target are allowed. Explicit updates follow the configured branch. Pins stay pinned. `--revision` changes policy to a pin. `--branch` resumes branch following. Persist policy only after success. `restore` materializes the currently recorded full commit and verifies its digest, never follows a branch or silently upgrades. `status` reports missing/unchanged/modified assets, unmanaged overlaps, native precedence, and trust/runtime uncertainty without writes.

`status --check` strictly verifies the recorded installation offline. Validate selection/lock agreement, record schemas/renderer compatibility, owned file presence/type/content hashes, and owned configuration values, including managed attribute entries. Report every observed drift using `ASSET_DRIFT` and exit `1`; malformed or unsupported records exit `2`. Informational status remains available without `--check`. Retained deliberate edits still count as drift. Ignore unrelated files/settings. Use local records and installed files only: no remote access, ref updates, source acquisition, installs, repairs, client/hook execution, journal recovery, or target changes. A pending interrupted operation produces an error without being recovered by this read-only command. A clean result proves agreement with recorded content, not source freshness or native client trust. CI runs this command on the checked-out payload before any install or restore.

Human output includes clients, requested/required assets, commit/policy, added/updated/retained/removed counts, conflicts, and trust actions. JSON emits one stdout document containing `schema_version`, `command`, `source`, `selection`, `changes`, `conflicts`, and `warnings`; strict status also supplies a `verification` object with boolean `passed` and a `drift` list. Diagnostics/progress go to stderr. Exit `0` means success, successful preview, or clean strict verification. Exit `1` means conflict, unavailable dependency, or strict verification drift. Exit `2` means malformed input/schema, missing prerequisites, acquisition failure, or an interrupted-operation error. Stable codes include `ASSET_CONFLICT`, `ASSET_DEPENDENCY_MISSING`, `ASSET_LOCAL_TRACKED_TARGET`, and `ASSET_DRIFT`, with safe paths and resolution advice.

Add `distribution/catalog.json`, schema version `1`, with assets keyed by ID and bundles by name. Each asset specifies source paths, required IDs, clients, OS/runtime restrictions, and rendering kind. Include maintained skills/agents and selectable hook families with explicit helper/launcher files. Exclude archives, benchmark workspaces, ignored runtime state, and eval output. Preserve licenses and runtime references instead of blanket README/license removal. Maintain dependencies explicitly, not through install-time prose inference. Reject cycles, invalid paths, case-folded output collisions, and undeclared runtime files. Known missing dependencies are unavailable entries with reasons.

Selection records store installation ID, scope/mode, clients, requested assets/bundles, and source policy. Lock records store schema/renderer version, full commit/digest, resolved assets, owned items, and `selection_digest`. Compute that SHA-256 from canonical UTF-8 JSON selection data with sorted keys, stable encoding, and normalized ordering for unordered selections. It detects desired-selection changes without fetching source. File items store destination, type/mode, owners, baseline digest, and declared payload/line-ending policy. Configuration items store destination, stable semantic locator, owners, last managed value, and digest. Identify a named handler or uniquely matching exact value. Git attribute ownership uses exact payload path and attribute values in a marked block rather than a line number. Ambiguous matches conflict. Validate records before trusting ownership or destinations.

SHA-256 covers a sorted, unambiguous sequence of selected source paths, file types, executable intent, and content hashes. Include catalog and rendering inputs affecting output, excluding target paths/timestamps. Record rendered hashes separately. Reject source links escaping the tree and unrepresented submodules. Materialize regular copies on every platform. Validate Windows reserved/case-colliding names before writes. POSIX mode checks do not establish Windows ACL safety.

Declare text/binary content and expected line endings for every delivered file in the catalog/rendering inputs. Maintained text defaults to LF, with explicit CRLF where an asset requires it, including applicable `.bat`/`.cmd` files. Binary files retain their bytes. Render the declared representation and hash those exact bytes; do not normalize whitespace or line endings while comparing local edits. Team installation owns only narrowly scoped `.gitattributes` entries for delivered paths: appropriate `text eol=lf`, `text eol=crlf`, or `-text`. Quote/escape paths correctly; never add repository-wide wildcard policy. Preserve surrounding entries and compatible existing policy without claiming it. Preflight incompatible existing rules, higher-precedence overrides, and unsupported content transforms before any destination mutation. Do not execute Git filters for verification. Apply the normal config ownership and pruning rules to owned attribute entries. Never renormalize unrelated files or change personal Git configuration. Local/user scopes do not write tracked team attributes.

## Plan of Work


### Milestone 1: Install one pinned skill into a team repository


Status: in progress

Acceptance: not met

Add subprocess suite `scripts/test-agent-assets.py` using disposable source/target Git repositories. The test seams are already accepted. First invoke the new CLI for `skill:caveman` and Codex. Assert native content, requested selection, immutable commit, and SHA-256. Observe failure, then add only the CLI/catalog/acquisition/copying slice needed to pass. Add repetition behavior after the first case passes.

Write `.agents/skills/caveman/`, both team records with matching selection identity, and narrowly owned LF attributes for delivered text. Preserve an existing attribute file and refuse incompatible rules before writes. Do not invoke hooks/clients, alter the target index, commit output, or configure personal RTK. Acquire committed content only. Dirty selected source paths fail before installation. Unrelated uncommitted docs need not prevent it. Register the suite in `scripts/test-all.py`.

Run `rtk proxy python3 scripts/test-agent-assets.py --group team-install` and `rtk proxy python3 scripts/test_test_all.py`. Acceptance is one selected skill without other trees, provenance, unchanged index, and repetition reporting no changes. These commands/behaviors are future work, not planning verification.

### Milestone 2: Resolve bundles and required assets


Status: open

Acceptance: not met

Extend catalog and commands one behavioral slice at a time. Audit workflow calls/imports before declaring dependencies. Initial bundles are `review`, rooted in `skill:code-review`, `security-hooks`, containing `hook:tool-guard` and `hook:scan-secrets`, and `required-context`, containing `hook:required-skills` and its declared skill files. Include all audited required dependencies. A curated bundle is not every repository asset.

`list` reports unavailable workflows and full missing-dependency chains. Selecting one fails before copies. Agents/hooks for Claude Code, Cursor, or OpenCode produce the initial skills-only restriction. Use shared `.agents/skills` after verification and dedicated documented paths where supported versions lack shared discovery. Do not make one client discover duplicate named copies.

Run `rtk proxy python3 scripts/test-agent-assets.py --group selection`. Prove individual assets, transitive/shared dependencies, missing requirements without writes, and case-folded collision refusal. Expected membership comes from literal fixture data, not the resolver being tested.

### Milestone 3: Update, restore, and prune owned content safely


Status: open

Acceptance: not met

Resolve source, recalculate closure, render desired files/configuration, validate destinations, and compare baselines before applying any part. Recheck observations under the mutex immediately before replacements. Concurrent changes conflict. Preview and application share planning, but application revalidates current targets.

Use a local Git remote with commits A and B. Bundle B adds/removes assets and changes a dependency. Preview reports changes without altering the target. Update applies them and advances only the current lock. Restore reconstructs missing unchanged owned files from the recorded commit after another branch advancement. Missing commits/digest mismatches fail rather than following a branch.

Current content different from baseline and desired upstream content different from baseline conflicts, unless current content already equals the desired result. Stop the whole operation before destination writes. If upstream is unchanged, retain/report local edits without adopting them as upstream. Preserve each retained item's baseline and origin commit in the current lock so overall revision advancement does not erase edit detection. Compare owned configuration values, not unrelated settings. Edited removals stop the whole operation. Require explicit resolution/rerun without automatic merging or backup replacement.

Prune only owned, unchanged items required by no remaining selection/dependency closure. Reconcile relevant team/local records. Never recursively delete an installation directory. Remove managed empty directories only after verifying no unrelated entries.

Apply the same preflight and pruning rules to owned Git attribute entries. Preserve unrelated rules and do not claim an identical unowned rule. An edited obsolete managed rule conflicts before writes. Recalculate desired path-specific policy with the selection so adding/removing payloads adds/removes only appropriate owned entries.

Use the resolved per-worktree Git directory for repository mutexes/journals, and personal state for user scope. Stage bytes, verify observations, atomically replace files, and write selection/lock records with payload/configuration success. Recover one failed/interrupted operation to its pre-operation state before another operation. Delete preimages/journal after success or recovery. Preview/conflict exits create no installation history or rollback command.

Implement strict `status --check` through the accepted public subprocess seam. Prove a clean recorded installation exits `0`, while a missing/edited payload, changed owned config or attribute entry, or selection/lock disagreement exits `1` with `ASSET_DRIFT`. A malformed/unsupported record or pending interrupted operation exits `2` without repair. Altering unrelated settings does not fail. Verify complete target fingerprints stay unchanged on every check. Point the saved source at an unavailable location to prove strict verification needs no source fetch. Check deliberate retained edits after an otherwise valid update and report drift without overwriting them.

Run `rtk proxy python3 scripts/test-agent-assets.py --group lifecycle`. Prove branch updates, pinning, restoration, strict offline verification, whole-operation conflict refusal, safe payload/attribute pruning, unrelated preservation, concurrency refusal, and interrupted-write recovery. Exercise failure through disposable process/filesystem conditions. Do not assert private helpers or add test-only product switches without justification.

### Milestone 4: Materialize native repository setups


Status: open

Acceptance: not met

Implement rendering in `scripts/agent_assets/providers.py`. Codex uses `.agents/skills`, `.codex/agents/*.toml`, and project `.codex/hooks.json`. Preserve strict canonical serialization from `scripts/install-codex-agents.py`. Reuse a side-effect-free renderer instead of invoking its mutating installer. Copilot uses shared skills where supported, `.github/agents/*.agent.md`, and installer-owned `.github/hooks/agent-assets.json`. Gemini uses shared or verified native skills, `.gemini/agents/*.md`, and a selective merge into `.gemini/settings.json`.

Package hooks in separate runtime trees such as `.codex/hooks/agent-assets/`, `.github/hooks/agent-assets/`, and `.gemini/hooks/agent-assets/`, preserving provider-local helper layout. Per-provider launchers locate their own root and explicit runtime configuration. Registration commands locate the Git root when clients start in nested directories. Quote POSIX and Windows paths separately. Copilot needs `bash` and `powershell` commands. Codex uses its documented Windows override. Reuse maintained event names, envelopes, timeout units, and bounded stdin behavior. Installation does not redesign hook protocols.

Introduce `AGENT_ASSETS_RUNTIME_CONFIG`, passed by the launcher to the selected provider process. The configuration contains package-relative skill/reference paths, required skill files, and installation ID. Required-skill loaders prefer this validated configuration, then existing personal defaults. Change canonical `hooks/families/` sources for generated files and regenerate outputs. Never hand-edit generated Python. Clones must work without the source checkout or installer user's home. Never choose skill roots from untrusted hook input.

Keep writable state outside payloads. Use explicit `AGENT_ASSETS_STATE_DIR`, otherwise per-user state under `XDG_STATE_HOME` or `~/.local/state` on Linux, `~/Library/Application Support/agent-assets` on macOS, and `LOCALAPPDATA/agent-assets` on Windows. Partition by provider and normalized-target-path hash so independent clones do not share sessions. Do not commit personal absolute paths. Before changing audit/trace or auto-ingest integration, load the focused observability/auto-ingest instructions and raw source references.

Extract selected registrations and reviewed repository-relevant instruction fragments. Never copy all `.gemini/global-settings.json` or personal instructions into a teammate's project. Make fragments explicit selectable catalog assets. Use owned marked blocks only in native-loaded instruction files and preserve surrounding text. If no meaningful repository-safe fragment exists, report it unavailable. Do not distribute unrelated authentication, account MCP, UI/model, or LSP settings.

Preflight duplicate-key/malformed JSON, invalid TOML, linked/reparse-point destination parents, and hard links. Replace with independent atomic files rather than chmod through external links. Preserve unowned settings. Avoid duplicate managed registrations within a native layer. Do not add inline Codex hooks alongside managed `hooks.json`. Report additive personal/project hooks when no documented deduplication exists. Repository operations never rewrite/suppress personal hooks. Status reports observed configuration and expected precedence while separating file presence from trust/runtime proof.

Run `rtk proxy python3 scripts/test-agent-assets.py --group providers`, `rtk proxy python3 scripts/generate-hooks.py --check`, and `rtk proxy python3 scripts/test-generate-hooks.py`. Run existing `bash scripts/test-codex-hooks-startup.sh`, `bash scripts/test-hooks-startup.sh`, and `bash scripts/test-gemini-hooks-startup.sh` through RTK for changed loaders. Run security suites for changed families. Acceptance includes strict conversion, all selected runtime dependencies, relocation/nested-directory execution, settings preservation, correct provider envelopes, and required native trust. Prove installed hook subprocess execution for all three complete adapters before marking this milestone done. Normal client delivery remains milestone 6.

### Milestone 5: Add private repository and personal lifecycle support


Status: open

Acceptance: not met

Implement local mode with untracked native files and exact Git excludes. Resolve Git directories/excludes through Git so linked worktrees work. Preserve existing text and other worktrees' entries. Refuse excludes concealing tracked changes or broad unrelated trees. Copilot CLI's `.github/copilot/settings.local.json` can express appropriate local configuration. Verify VS Code independently before relying on that overlay for its hooks. Without a native local override, use ordinary native paths only when no tracked file must change. Detect the whole operation's tracked-target conflict before copying assets.

When team/local selections need identical bytes at one path, record local borrowing of the team-owned file. Local operations never overwrite or claim team ownership. Different required bytes conflict. Reconcile records before pruning. A remaining borrower keeps the item required. Changing mode requires an explicit selection operation and ownership validation, never hiding team files silently.

Add personal destinations matching the current workflow and Codex agent override. Add `install --scope user --adopt` for selected copies. Compare regular files and exact known configuration values with verified repository outputs, including legacy rendering. Existing `.skills-repo-agents.json` proves names were managed, not that bytes are unchanged. Refuse ambiguous, edited, unknown-revision, or merely similarly named copies. Preserve unowned personal files and old backups. Tests never mutate the real home.

Forward explicit scoped arguments from `scripts/install.sh` and `scripts/install.ps1` to Python. Before adoption, preserve no-argument legacy personal behavior. Once managed personal records exist, route no-argument refresh through saved selection so legacy copying cannot bypass conflict protection. Test and document the transition. Legacy copying can include old workflows with undeclared dependencies. The selective managed path must not advertise these workflows as complete. Preserve required freshness/prerequisite checks and error streams.

Repository installs never change account-wide RTK settings. For selected RTK hooks, check supported RTK availability and report the existing personal setup command when needed. Keep personal RTK configuration within the explicitly personal workflow. Skill-only installs do not require RTK. Git/Python are installer prerequisites. Client runtimes/tools are checked according to selected asset requirements and reported per client.

Run `rtk proxy python3 scripts/test-agent-assets.py --group scopes`, `rtk proxy bash scripts/test-install.sh`, `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`, `rtk proxy python3 scripts/test-codex-agents.py`, and `rtk proxy python3 scripts/test-rtk-stable.py`. Acceptance includes private files absent from `git status`, no tracked changes, team/local ownership coexistence, saved-selection updates, verified adoption, edited-copy refusal, and both wrappers. Native local limitations appear in help/diagnostics rather than accidental Git changes.

### Milestone 6: Validate operating systems and native loading


Status: open

Acceptance: not met

Add `.github/workflows/agent-assets.yml` for public subprocess tests on macOS/Linux/native Windows with Python 3.11 and the supported newer Python. Resolve action versions against conventions/official sources during implementation. Register the suite in existing native Windows coverage as appropriate, without replacing current tests. Prove path quoting, reserved/case-colliding names, reparse refusal where supported, replacement/recovery, and PowerShell forwarding on native Windows. PowerShell on macOS is not Windows acceptance.

Commit a disposable team installation, clone it with `core.autocrlf` enabled and disabled on each target OS, and run strict verification before any installation/restoration in the clone. Assert exact recorded hashes, declared LF/CRLF bytes, intact binary references, and functioning installed launchers. Cover existing compatible/incompatible attribute rules and paths needing quoting. Obtain the command checkout separately without regenerating the clone's payload. An intentionally modified committed payload must fail the CI check rather than be repaired first. Keep source freshness and native discovery as separate evidence.

During implementation create `docs/agent-asset-installer/client-validation.md` with exact versions, OS, discovery, hook evidence, trust steps, and unsupported cases. For Codex local clients, Copilot CLI, Copilot VS Code, and Gemini CLI, install a disposable project, select a skill/agent, and run a harmless hook through normal client operation. Clone to another path and repeat without source checkout. For Claude Code, Cursor, and OpenCode, prove skills/supporting-reference access only. Use distinctive fixture responses so discovery cannot be mistaken for a personal copy.

Complete setup means assets the approved native surface supports, not identical hook events everywhere. Never infer IDE plugin support or hosted/cloud behavior. Missing clients/credentials are unmet live gates, not passing tests. Use disposable profiles where supported and native trust. Do not bypass trust or change real-home state. Verify current official instructions and the actual installed source before live checks.

Run `rtk proxy python3 scripts/test-agent-assets.py` on every OS, targeted native PowerShell suites on Windows, and `rtk proxy ./scripts/test-all.py` with full prerequisites. Record actual counts/failing names. Acceptance requires green automated OS jobs and discovery/event proof for advertised surfaces. Keep unverified surfaces visibly limited until evidence exists.

### Milestone 7: Document usage and close acceptance


Status: open

Acceptance: not met

Update `README.md` with short team/local/personal examples, preview/update, strict `status --check`, and recorded-revision restoration. Add `docs/agent-asset-installer/usage.md` for flags, catalog/selection, trust/runtime requirements, explicit conflict resolution, pruning, owned checkout policy, tracked-local limitations, and supported client/OS matrix. Include an audit-only CI example that checks committed payloads before any restore/install. Explain that clones contain working payloads and the check validates recorded content, not upstream freshness or client trust. Updating/checking requires Python, Git, and this repository's command checkout. This delivery channel does not require teammates to bootstrap package caches.

Run `update-agent-docs` once at session end after implementation/review. Update `FILE_MAP.md`, script/hook/provider instructions, `API_MAP.md`, and testing/known-issue guidance for implemented behavior only. Apply `okf-authoring`, run `rtk proxy ./scripts/lint-okf.py` and `rtk git diff --check`, and preserve protected `AGENTS.md` sections. Synchronize milestone statuses/checkboxes, capture measured outcomes, and update the feature handoff. Commit synchronized docs with source changes. Never automatically commit installed team changes.

Acceptance is help matching documentation, earlier milestone gates met, no stale generated outputs/ownership conflicts, clean worktree after scoped commits, and a supported/limited matrix backed by evidence. Native publication remains separate.

## Concrete Steps


Commands below describe future implementation/validation unless explicitly recorded otherwise. Work from this source repository root. Use disposable targets outside the checkout. Never test against real home. Native Windows can use `py -3` or `python` where `python3` is unavailable, and `pwsh -NoProfile -File scripts/install.ps1` for wrapper cases.

The user accepted three seams: the public `scripts/agent-assets.py` subprocess CLI and its filesystem/configuration effects, existing Bash/PowerShell entry points, and installed native discovery plus registered hook processes. Do not ask for that acceptance again. Private helper calls/internal collaborator mocks are outside the test surface. Implementation is authorized. Implement milestone 1 one red/green behavior at a time.

After those commands exist, a skill-only example needs no client authentication:

    rtk proxy git init /tmp/agent-assets-demo
    rtk proxy python3 scripts/agent-assets.py install --repo /tmp/agent-assets-demo --client codex --asset skill:caveman --source .
    rtk proxy python3 scripts/agent-assets.py status --repo /tmp/agent-assets-demo --format json
    rtk git -C /tmp/agent-assets-demo status --short

Expect `.agents/skills/caveman/SKILL.md` and both `.agent-assets/` team records. The index is untouched. The lock shows a full commit/SHA-256, not only a branch. Automated tests use unique temporary paths rather than this example. Repeat with target paths containing spaces.

After dependency resolution and complete adapters exist:

    rtk proxy python3 scripts/agent-assets.py list --client codex --format json
    rtk proxy python3 scripts/agent-assets.py install --repo /tmp/agent-assets-demo --client codex --client copilot --client gemini --bundle review --bundle security-hooks
    rtk proxy python3 scripts/agent-assets.py update --repo /tmp/agent-assets-demo --preview
    rtk proxy python3 scripts/agent-assets.py update --repo /tmp/agent-assets-demo
    rtk git -C /tmp/agent-assets-demo diff --stat

The second install explicitly replaces desired selection in that scope. Support `install --preview` through the same planner so the developer can inspect resulting removals first. Do not alter other scopes. Team updates remain uncommitted. A conflict prints its code/path, exits `1`, and leaves the complete target fingerprint unchanged.

After milestone 3 adds strict verification, check an existing committed installation directly:

    rtk proxy python3 scripts/agent-assets.py status --repo /tmp/agent-assets-demo --check --format json

Expect exit `0` and passing verification for unchanged recorded content. Removing/changing a managed file or owned setting produces exit `1` with `ASSET_DRIFT` and no target changes. Editing desired selection without installing also fails. Do not run install/restore before this check in a committed-payload CI job. The command does not fetch or repair.

Private/personal examples use new disposable targets:

    rtk proxy git init /tmp/agent-assets-private
    rtk proxy python3 scripts/agent-assets.py install --repo /tmp/agent-assets-private --mode local --client cursor --asset skill:caveman
    rtk proxy python3 scripts/agent-assets.py update --repo /tmp/agent-assets-private --mode local --preview
    rtk proxy python3 scripts/agent-assets.py install --scope user --home /tmp/agent-assets-home --client codex --asset skill:caveman
    rtk proxy python3 scripts/agent-assets.py update --scope user --home /tmp/agent-assets-home
    rtk proxy python3 scripts/agent-assets.py restore --scope user --home /tmp/agent-assets-home

Private `git status` shows no new files. Exact native payload paths and local records are excluded. A clone does not carry private selection. Personal commands remember selection at the specified disposable home, leaving real home untouched.

## Validation and Acceptance


The first accepted seam exercises lifecycle end to end with real disposable Git repositories/remotes. Assert literal fixture content, independent known hashes, semantic settings, exits, streams, and complete target fingerprints on refusal. Cover install/repetition, branch advancement, pins, acquisition failure, digest mismatch, dependency/selection changes, restoration, edited retained/updated/pruned items, borrowed files, malformed records/settings, and interruptions. Do not merely assert operations inside a private plan.

Strict verification uses that same seam, without source access or writes. Cover selection fingerprints, missing/modified payloads, semantic owned values, attributes, unrelated settings, unsupported records, and pending interrupted operations. Cross-platform clone cases use literal expected LF/CRLF/binary bytes and known hashes, not the renderer's own output as the expected result. Native launchers must run after cloning with different `core.autocrlf` settings. Hash checks alone do not replace that execution evidence.

The second seam proves both entry points implement equivalent selected behavior and preserve legacy refresh before adoption. Continue existing installer/converter/configuration suites. A failing targeted suite is a real failure to reproduce/fix. Never delete, skip, weaken, or rename it to obtain green results. Do not add regression tests for feature deletions.

The third seam proves files are used. Clients discover distinctive repository skills/agents, and registered hooks run through native events with provider-valid output. Direct installed-script checks prove protocol behavior but cannot replace event delivery. Record version, OS, trigger, output, and trust. Skills-only compatibility is not full adapter support.

The public suite supports `--group team-install|selection|lifecycle|providers|scopes`, with no group running all. Add cases when their vertical slices are implemented, not as a bulk imagined suite. Tests use and clean only unique temporary source/target roots. Automated groups need no client/network credentials. Native evidence is separate. Documentation validation does not satisfy implementation acceptance.

## Idempotence and Recovery


Repeat operations produce zero payload/configuration writes. Acquisition failure, missing dependencies, malformed settings, tracked-local targets, and conflicting managed edits stop before destination mutation. Record mismatch is an error, not permission to infer ownership. An unowned preexisting destination is a conflict, even if similarly named. Claim it only through the explicit verified adoption operation. Preserve unrelated settings/logs. Records contain no secrets.

Strict verification never performs repair or interrupted-operation recovery. Run a separate authorized restoration/update only after diagnosing its result. Exact rendered digests remain the baseline across declared checkout policies; do not make hashes accept arbitrary whitespace changes. Preserve unrelated Git attributes, never perform repository-wide renormalization, and apply edited-entry conflict protection to managed checkout rules.

Resolve a conflict by explicitly restoring known baseline content or incorporating edits into maintained source, then rerun. Removing an edited obsolete item still requires explicit resolution. Do not suggest dropping it from selection as a way to bypass that check. Never auto-merge or replace edited assets with backups.

Retry after an interrupted write to recover only that pending operation before calculating a new plan. Recovery refuses ambiguous external changes. Keep an unresolved journal only for that incomplete operation and report its recovery error. Delete it after recovery. There is no rollback command/history. Restore uses the current record and the same edit policy. Unsupported record/renderer versions fail with the recorded source revision and instructions to use that compatible command checkout instead of silently changing output.

## Artifacts and Notes


`scripts/install.sh:40` strips eval/README/license files. New packaging preserves required supporting files/notices. `scripts/install-provider-hooks.py:51` validates hook shape. Retain schema and duplicate-key checks without basename-based ownership. `scripts/install-codex-agents.py:280` renders strict TOML. Preserve canonical text. `hooks/manifest.py:19` defines generated ownership. Installation never runs generator write mode.

Adapter snapshots/live versions are not pinned by planning. Record versions/evidence in milestone 6 and distinguish documented from installed behavior. No stable release channel is assumed. Earlier source inspection found no local tags and did not inspect remote releases.

Revision note, 2026-09-29: Created a separate implementation ExecPlan from the closed contract. Added concrete lifecycle/data design and seven acceptance milestones. Kept test seams pending confirmation and source untouched. Recorded tracked-local limits and tool input limits rather than inventing uniform settings or bypassing checks.

Revision note, 2026-09-29 21:50Z: Recorded acceptance of all three test seams and the subsequent explicit instruction not to start implementation. Updated the resume gate, progress, and outcome. No source or tests were created.

Revision note, 2026-09-29 23:21Z: Recorded the user's requested review of six existing distribution repositories. Kept all implementation choices as the baseline, pending evidence and a live decision. All implementation milestones remain open and implementation remains on hold.

Revision note, 2026-09-29 23:47Z: Completed the comparison, recorded incompatible managed-edit semantics in APM/ECC, and proposed read-only verification plus explicit checkout line-ending policy. These are pending proposals; the existing public interface and milestone requirements remain unchanged until the user decides. Implementation remains on hold.

Revision note, 2026-09-29 local date (2026-09-30 00:01Z): Recorded the user's acceptance of retaining the architecture, strict verification, and checkout line-ending policy. Incorporated the command flag/diagnostic, selection fingerprint, exact-byte attribute ownership, milestone 1/3/6/7 behavior, clone/CI examples, and acceptance conditions. The decision map is closed with no remaining question. All implementation milestones remain open and the explicit implementation hold remains in effect.


Revision note, 2026-09-30 00:25Z: The user requests full implementation through `execplan-implement`. Lift the hold, record task dependencies and model routing, and begin milestone 1 in an isolated private worktree. Historical hold decisions remain as history.
