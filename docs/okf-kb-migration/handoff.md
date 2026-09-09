# OKF Agent-KB Migration Handoff

## Goal

Execute the six-gate in-place OKF v0.2 migration for the canonical documents under `.agents/instructions/` and `.agents/memory/`. Preserve the existing `AGENTS.md` → `.agents/memory/INDEX.md` loading path, teach OKF authoring through a repository skill, and enforce conformance through blocking GitHub Copilot CLI and Gemini CLI lint hooks.

## Status

- On 2026-09-09, the user explicitly authorized implementation. Gate 1 is complete and was manually committed by the user as `e0d425972641f1f1a372d7dacd068f73fa7fefee` from baseline `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9`.

- **OKF Authoring Skill Contract** is closed after three accepted grilling rounds and explicit shared-understanding confirmation. Its Gate 3 implementation has not started.
- The user found a charter-level flaw in the closed map: its `.agents/okf/` sidecar and prompt-time selector would inject knowledge already discoverable through the mandatory `AGENTS.md` → `.agents/memory/INDEX.md` path.
- **In-Place OKF Migration Charter** records the corrected source-of-truth and enforcement model and is closed.
- All 18 tickets derived from the old sidecar/selector/provider-runtime design are `obsolete`. Their research may be reused as evidence, but their decisions are not authoritative.
- **In-Place OKF Document Contract** is closed after three accepted grilling rounds and explicit shared-understanding confirmation. Its resolution defines the two-bundle, standard-metadata, stable-path, link, source-summary, lifecycle, and no-extension contract.
- **OKF Linter and Provider Hooks Contract** is closed after three accepted grilling rounds and explicit shared-understanding confirmation. Its resolution fixes the complete lint surface, diagnostics, commands, dependency packaging, provider envelopes, failure behavior, and acceptance gates.
- **In-Place Migration Sequencing and Verification** is closed after three accepted grilling rounds and explicit shared-understanding confirmation. Its resolution fixes six implementation gates, validation scope, ownership, live capability proof, and rollback.
- The 18 obsolete tickets are archived under `tickets/obsolete/`; the direct `tickets/` directory contains exactly five closed authoritative tickets.
- `map.md` and `implementation-overview.md` describe the completed corrected design.
- `implementation-execplan.md` translates the five closed contracts into six implementation gates with public test seams, non-overlapping path ownership, exact stable validation commands, live provider evidence requirements, and whole-migration rollback. Gates 1 and 2 are complete; Gate 2 awaits only its user-created checkpoint, and Gates 3–6 remain open.
- Gate 1 added `scripts/fixtures/okf-valid-repo/` and `scripts/test-okf-lint.sh`.
- Gate 2 added the offline provider-neutral `scripts/lint-okf.py`, pinned PyYAML 6.0.3 under `scripts/vendor/`, and review-driven public-CLI regressions. No skill, canonical-corpus migration, adapter, or hook registration exists yet.

## Next Focus

Wait for the user's manual Gate 2 checkpoint, then record its SHA. Do not begin Gate 3 before that checkpoint exists.

## Exact Next Step

After the user manually commits the current Gate 2 scope, record its SHA in `implementation-execplan.md`. Then Gate 3 may begin with the existing-skill search and `okf-authoring` evaluation baseline.

## Decisions and Constraints

- Canonical `.agents/instructions/` and `.agents/memory/` documents become OKF documents in place; there is no generated knowledge sidecar.
- `AGENTS.md` and `.agents/memory/INDEX.md` remain the knowledge entry and routing path.
- No prompt-time selector, context injection, provider runtime, fallback path, qualification state, or promotion ladder belongs to this migration.
- A repository skill teaches OKF authoring. A linter validates authored documents and blocks failures through both providers' validation hooks.
- The model-invoked skill is named `okf-authoring`; it triggers for canonical-document create, modify, migrate, and review work, while ordinary reads and documents outside the two canonical roots do not trigger it.
- `update-agent-docs` remains the semantic owner and invokes `okf-authoring` after its semantic pass. `okf-authoring` never invokes back; `ingest-source` reaches it indirectly through `update-agent-docs`.
- Keep the short workflow and completion contract in `SKILL.md`, the shared repository profile in `references/profile.md`, and source-summary rules/examples in `references/source-summaries.md`. Add further references only when evaluation evidence justifies them.
- Canonical-document review remains read-only without change authorization. Completion requires successful canonical lint across both bundles plus a scoped-diff check; unavailable lint must be reported as unverified and cannot support a completion claim.
- Lint hooks do not replace or duplicate current source-ingest freshness behavior. Immutable `.agents/sources/` remains out of bounds.
- Planning only: close the four replacement decisions before creating an implementation ExecPlan.
- Use two physical OKF bundles rooted at `.agents/memory/` and `.agents/instructions/`; do not define `.agents/` as a bundle with exclusions.
- Every canonical concept requires the standard `type` and `description` fields. Translate the current `coverage` values into `description`; do not preserve `coverage` as a required extension.
- Enforce the path-derived type vocabulary `Agent Instruction`, `Agent Memory`, `Knowledge Index`, `Source Ingestion Log`, `Known Issue`, `Testing Guidance`, `Architecture Decision`, and `Source Summary`.
- Preserve uppercase `.agents/memory/INDEX.md` and `.agents/memory/LOG.md` as ordinary `Knowledge Index` and `Source Ingestion Log` concepts. Create no lowercase siblings, and pin the target OKF version in migration tooling rather than reserved-file frontmatter.
- Use file-relative local links. They may cross the two bundle roots or point to other repository files, but must stay within the repository and resolve; external URLs remain allowed.
- Give every completed source summary one `sources` entry pointing to its matching immutable raw source, omit unsupported `verified` metadata and lifecycle `status`, and use `status: draft` for unresolved scaffolds until integration removes it. Per-claim source footnotes remain optional.
- Do not synthesize provenance, trust, or freshness metadata during migration. When used, `generated` requires `by` and `at`; `verified` uses a list of `{ by, at }` events; timestamps require explicit UTC offsets; stable status is omitted; and draft/deprecated/stale states require genuine semantics.
- Forbid exact lowercase `index.md` and `log.md` throughout both initial bundles. The profile defines no required repository extension fields, tolerates unknown fields as OKF requires, and pins OKF v0.2 in authoring/lint tooling rather than document metadata.
- Use one full-corpus `scripts/lint-okf.py` authority with human and JSON output, stable `OKF001`–`OKF105` plus `OKF900` diagnostics, and `0`/`1`/`2` exit semantics. Vendor pinned pure-Python PyYAML 6.0.3 under `scripts/vendor/yaml/`; hooks perform no runtime installation.
- Validate both bundles, exact path-derived types, standard metadata, known legacy fields, file-relative Markdown/resource targets, and manifest-backed source-summary provenance. The linter reads but never reconciles or writes source-ingest state.
- Use thin repository-local Copilot and Gemini adapters for immediate mutation feedback and unconditional final full-corpus gates. Keep source-ingest hooks first and separate, capability-test mutation matchers and final events, cap hook diagnostics, and block enablement if required live behavior is absent.
- Implement through six gates: baseline/failing fixtures; dormant linter and vendored parser; authoring skill and one-way composition; atomic canonical-corpus plus scaffold-producer migration; provider adapters/configuration/regressions; then disposable-worktree live probes and final evidence.
- Use one checked-in valid two-bundle fixture copied and mutated in temporary repositories. Merge only after both providers pass all required live probes; treat the merged migration as one rollback unit.
- Keep source-ingest and OKF lint as independent ordered hooks unless simultaneous-failure evidence requires a thin coordinator. Record commands, CLI versions, event observations, normalized diagnostics, lint duration, and rollback checkpoints in the version-controlled ExecPlan.
- Assign non-overlapping ownership for linter/fixtures, authoring skill/evaluations, canonical migration/scaffold producers, and dual-provider adapters/tests; one coordinator owns shared configuration and final integration.

## Relevant Files

- `docs/okf-kb-migration/map.md` — corrected destination, authoritative decision index, and dependency graph.
- `docs/okf-kb-migration/tickets/in-place-okf-migration-charter.md` — closed source-of-truth and enforcement charter.
- `docs/okf-kb-migration/tickets/in-place-okf-document-contract.md` — closed in-place bundle and concept contract.
- `docs/okf-kb-migration/tickets/okf-authoring-skill-contract.md` — closed authoring-skill design.
- `docs/okf-kb-migration/tickets/okf-linter-and-provider-hooks-contract.md` — closed linter, diagnostics, provider-hook, and capability-gate design.
- `docs/okf-kb-migration/tickets/in-place-migration-sequencing-and-verification.md` — closed six-gate sequencing and verification contract.
- `docs/okf-kb-migration/implementation-overview.md` — concise corrected architecture for novice readers.
- `docs/okf-kb-migration/implementation-execplan.md` — implementation authority; Gate 1 code/tests are complete but its checkpoint remains open, and Gates 2–6 have not started.
- `scripts/test-okf-lint.sh` — Gate 1 public-CLI contract suite; intentionally red until Gate 2 creates `scripts/lint-okf.py` and the pinned vendor record.
- `scripts/fixtures/okf-valid-repo/` — pristine two-bundle fixture copied into a fresh temporary repository for every mutation case.
- `.agents/scratchpad/explore-okf-in-place-correction.md` — local evidence tracing the duplicate-context flaw.
- `.agents/scratchpad/explore-okf-authoring-skill-contract.md` — local code map for current skill conventions and the `update-agent-docs` responsibility seam.
- `docs/okf-kb-migration/research/okf-primary-sources.md` — prior OKF v0.2 research; its sidecar recommendation is obsolete, but specification facts remain reusable after verification.
- `docs/okf-kb-migration/research/copilot-lint-hook-surfaces.md` — current official Copilot post-tool and stop-hook facts and limitations.
- `docs/okf-kb-migration/research/gemini-lint-hook-surfaces.md` — current official Gemini AfterTool/AfterAgent facts, including the open reliability issue.
- `.agents/scratchpad/explore-okf-lint-hooks.md` — local source-ingest boundaries and likely lint integration seams.

## Verification State

- Ticket validation now shows five closed authoritative tickets directly under `tickets/`, 18 obsolete tickets under `tickets/obsolete/`, no open tickets, and no active claims.
- All relative Markdown links in `map.md`, `implementation-overview.md`, `handoff.md`, and the closed authoring-skill ticket resolve. Active-document searches found old runtime terms only where the rejected design is explicitly identified as obsolete.
- A delegated repository-wide stale-document audit found no other active references presenting the rejected design as current and no migration-relevant broken links. It identified `relocation-execplan.md` as the sole stale artifact; that completed plan now labels its counts as a 2026-09-03 relocation snapshot and routes current status to `map.md` and this handoff.
- `git diff --check` passed after closing and indexing the authoring-skill ticket.
- No code, hook, skill, canonical KB document, or configuration was implemented or changed.
- Rechecked canonical OKF v0.2 at `GoogleCloudPlatform/open-knowledge-format` main commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`; the local research remains version-current. The upstream `SPEC.md` SHA-256 is `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Corpus inventory: 31 canonical Markdown documents (6 instructions, 16 non-summary memory documents, 9 source summaries). Exact lowercase `index.md`/`log.md` do not exist; uppercase `INDEX.md` and `LOG.md` are current ordinary concept candidates and exact loading/history paths.
- Corrected `research/okf-primary-sources.md` so it no longer overstates `generated.at` as explicitly required by OKF minimum conformance. The spec explicitly requires `generated.by` and specifies `generated.at`; requiring both is a repository-profile decision.
- The confirmed document contract is recorded in `tickets/in-place-okf-document-contract.md`; its new map link resolves, and the ticket has no remaining claim.
- The confirmed authoring-skill contract is recorded in `tickets/okf-authoring-skill-contract.md`; its map link resolves, and the ticket has no remaining claim.
- The current end-of-session `update-agent-docs` pass found no canonical KB update was needed: only ordinary migration planning documents changed, `.agents/memory/FILE_MAP.md` already describes the effort without volatile counts, and `.agents/instructions/repo.md` already records the authoritative-versus-obsolete ticket convention.
- The confirmed linter/provider-hook contract is recorded in `tickets/okf-linter-and-provider-hooks-contract.md`; its map link resolves, and the ticket has no remaining claim.
- Official-source research confirms neither provider exposes an authoritative changed-file list after tools. Copilot `postToolUse` cannot block/undo writes; `agentStop`/`subagentStop` force bounded continuation but timeouts fail open and the host overrides after eight blocks. Gemini `AfterTool` does not roll back writes; `AfterAgent` can retry, but an official open issue reports it not firing in at least one build, so live capability proof is required.
- Local exploration confirms repository-specific Copilot lint belongs under `.github/hooks/`, Gemini lint under `.gemini/settings.json`, and source-ingest scripts/state must remain separate. The canonical corpus remains small enough for a full two-bundle scan.
- The accepted parser pin is PyYAML 6.0.3. PyPI reports the source archive SHA-256 `d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f`; the contract vendors its pure-Python package and license rather than installing at hook runtime.
- Final validation checked all 15 active migration Markdown documents outside `tickets/obsolete/`; every relative link resolves. All five direct tickets are closed, no stale frontier or claim language remains in active documents, and `git diff --check` passes.
- The end-of-session `update-agent-docs` pass found no canonical KB edit was needed: this session changed only ordinary migration planning documents, and the existing repo workflow already describes their location and authority.
- Rechecked canonical OKF v0.2 on 2026-09-09: `main` remains commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`, and `SPEC.md` retains SHA-256 `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Rechecked current provider documentation: Copilot still documents ordered same-event hooks, full-match mutation-tool matchers, stop blocking, fail-open timeouts, and the eight-block override; Gemini still documents `AfterTool`/`AfterAgent`, while official issue `google-gemini/gemini-cli#27712` remains open.
- The current environment has Python 3.12.3 but no `copilot` or `gemini` executable, so live provider proof remains an explicit Gate 6 release requirement rather than planning-session evidence.
- The implementation ExecPlan contains all six required gates, path ownership, TDD seams, stable command matrix, version/source pins, provider probe templates, evidence slots, and rollback checkpoints. Gate 1 baseline, prerequisite, fixture, and test items are checked; only its commit item remains open.
- Current validation covers all active migration Markdown documents outside `tickets/obsolete/`; every relative link resolves, required ExecPlan sections remain present, and `git diff --check` passes.
- The current end-of-session `update-agent-docs` pass updated `.agents/instructions/scripts.md`, `.agents/memory/testing/scripts.md`, and `.agents/memory/FILE_MAP.md` for safe temporary cleanup and the new OKF fixture/test entry point.
- Gate 1 baseline inventory matched 31 canonical Markdown files, 22 `coverage` headers, 9 verified summaries, and no lowercase reserved paths. Both source-ingest suites and both startup suites exited 0.
- `bash -n scripts/test-okf-lint.sh` exits 0. `bash scripts/test-okf-lint.sh` intentionally exits 1 with exactly `intentional red: missing executable scripts/lint-okf.py`; fixture preflight runs before that guard. `git diff --check` is clean.
- Commit preflight found the repository on `main` with empty repository Git author name/email. Per the user's direction, no commit, branch, push, or PR was created; the reviewed worktree is ready for manual commit.
- Gate 2 final verification passed Python compilation, shell syntax, `PYTHONDONTWRITEBYTECODE=1 bash scripts/test-okf-lint.sh`, executable-mode validation, repeated deterministic JSON, and `git diff --check`. The live pre-migration corpus exited 1 with 104 expected conformance diagnostics and no `OKF900`.
- Independent Gate 2 review verified all 17 vendored Python sources and the license byte-for-byte against the accepted PyYAML 6.0.3 archive, but required fixes for vendor-origin enforcement, non-string lifecycle values, per-file read errors, offset-preserving code masking, balanced Markdown destinations, and nested YAML key locations.
- Targeted follow-up review confirmed those six findings plus unclosed/invalid fence handling and isolated vendor-failure testing are resolved; it found no new high-confidence regression.

## Errors and Durable Learnings

- The old map optimized a second retrieval system without first reconciling it with the repository's mandatory loading contract. Before designing context injection, trace all always-loaded and progressively loaded entry points; migrate the canonical source in place when the goal is a format migration.
- Loading `improve-skill` first used an incorrect repo-local path and failed without changing files; use the configured skill-root map (`r0` → `/root/.agents/skills`) instead of assuming `.agents/skills/` is repo-local.
- One combined patch tried to delete and add the same path in a single `apply_patch` input and was rejected before changing files. Replace content with an update patch or use separate delete/add operations.
- A shell search placed Markdown backticks inside a double-quoted command string, causing harmless command-substitution attempts and two `command not found` messages. No files changed. Use a single-quoted search pattern or otherwise keep backticks out of shell-interpreted strings.
- Status-recording patches failed when handoff wording or an anchor was stale; one malformed no-op also omitted wrapper result reporting. Reread short targets, use small fresh anchors, always print patch results, and verify the target after an unexpected empty result.
- One delegated Copilot research check first tried unavailable `python`, then succeeded with `python3`; do not assume a single interpreter command is portable across the repository's POSIX and Windows surfaces.
- The delegated Gemini researcher could not satisfy the `research` skill's nested-background-agent instruction because no spawn tool was exposed in that subagent. It completed the primary-source research directly; a future `research` skill revision should explicitly permit that fallback.
- Two `functions.exec` wrappers failed before shell execution because malformed JavaScript included an invalid variable and stray text. No files changed. Keep orchestration wrappers minimal (`const r = await ...; text(r.output);`) and avoid decorative or non-ASCII variable names.
- A repository search named nonexistent `skills/update-agent-docs`; `rg` reported the missing path and made no changes. The canonical repository-local skill is `.agents/skills/update-agent-docs/`; verify paths with `rg --files` before combining search roots.
- This resumed session first tried the global path `/root/.agents/skills/exec-plans/SKILL.md`; the read failed without changing files because `exec-plans` is repository-local at `.agents/skills/exec-plans/SKILL.md`. Expand each skill's declared root alias instead of assuming all skills share the global root.
- A temporary PyYAML archive inspection was rejected before execution because its cleanup trap contained a blocked recursive removal command. No files were created. Streaming the archive directly through `tar -tzf -` produced the needed package/license inventory without cleanup state.
- Gate 1 review found that incrementing a shell counter inside command substitution runs in a subshell and can reuse case directories. The harness now creates every case with its own `mktemp -d` template.
- Gate 1 review also found that interpolating a `TMPDIR`-influenced path into an EXIT trap can reparse metacharacters as shell code. Use a named cleanup function with a quoted exact path and `rm -rf -- "$path"`.
- A combined verification wrapper was rejected before execution because it included a temporary-file cleanup command. No tests or files were affected. Validate JSON through an in-memory Python subprocess when no persistent artifact is needed.
- A combined Gate 2 completion patch was rejected because one handoff anchor was stale; no file changed. Split status synchronization into fresh file-scoped patches after rereading short targets.
- Six unrelated untracked `skills/*/agents/openai.yaml` files appeared briefly while delegated review was running and disappeared again before final status without agent action. They were never part of Gate 2; recheck status rather than assuming transient concurrent files belong to the task.

## Suggested Skills

- Resume with `handoff`, then use `exec-plans` to record the user's Gate 2 checkpoint; use `skill-creator`, `tdd`, and the closed authoring-skill contract when Gate 3 begins.
- End every repository-changing session with `update-agent-docs`.
