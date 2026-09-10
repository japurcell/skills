# Migrate the canonical agent knowledge base to OKF v0.2 in place

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this document in accordance with the repository's `exec-plans` skill.

Implementation is active. Gates 1–3 are committed; the final Gate 3 rollback checkpoint is `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735`. Gate 4 was committed at `d21c4351`, but resumed review found a quoted-YAML draft-detection bypass; its red-green correction is approved, fully validated, and awaiting the user's manual checkpoint. Gates 5–6 remain open. Do not begin a later gate before recording the preceding checkpoint.

## Purpose / Big Picture

After this change, every canonical agent-facing document under `.agents/instructions/` and `.agents/memory/` will itself be an Open Knowledge Format (OKF) v0.2 concept. Agents will continue to discover those documents through the existing `AGENTS.md` to `.agents/memory/INDEX.md` route; there will be no generated sidecar, prompt-time selector, or second knowledge-loading path. Authors will have a repository skill that teaches the profile, and a single deterministic linter will provide the same findings to humans, GitHub Copilot CLI, and Gemini CLI. A user can see the result by running `./scripts/lint-okf.py`, observing a clean full-corpus scan, deliberately introducing an invalid canonical document in a disposable worktree, and observing both provider hooks return the same `OKF...` diagnostic and prevent a normal invalid completion through their supported lifecycle behavior.

The implementation is one migration unit. It may be built as reviewable commits, but it may merge only after all six gates below pass, including live Copilot and Gemini capability probes. If a required provider event does not fire, the branch remains diagnostic work and the migration does not merge.

## Progress

- [x] (2026-09-09 06:31Z) [milestone-1] Recorded clean baseline commit `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9`; confirmed 31 concepts, 22 `coverage` headers, 9 verified summaries, and no lowercase reserved paths.
- [x] (2026-09-09 06:31Z) [milestone-1] Confirmed both source-ingest suites and both startup suites exit 0 before fixture changes.
- [x] (2026-09-09 06:47Z) [milestone-1] Added the single valid two-bundle fixture and public-CLI contract suite; confirmed its intentional red is only the absent production linter.
- [x] (2026-09-09 07:04Z) [milestone-1] Recorded the user-created Gate 1 reviewable checkpoint `e0d425972641f1f1a372d7dacd068f73fa7fefee`.
- [x] (2026-09-09 07:29Z) [milestone-2] Vendored and verified PyYAML 6.0.3, implemented the dormant provider-neutral linter, made the expanded public-CLI suite green, and completed independent review without enabling hooks.
- [x] (2026-09-09 13:25Z) [milestone-3] Recorded the user-created final Gate 3 rollback checkpoint `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735` after the deterministic grader correction and independent approval.
- [ ] (2026-09-10 00:00Z) [milestone-4] Gate 4 implementation is committed at `d21c4351`; resumed review found that literal-line draft detection misclassified valid quoted/commented YAML as resolved. Symmetric public-hook regressions failed before and pass after the parser-independent scalar normalization, Premium follow-up review approved the correction, and the complete Gate 4 matrix is green. Remaining work is the user-created correction checkpoint.
- [ ] [milestone-5] Add thin Copilot and Gemini adapters, register them after source-ingest validation, and make parity and provider regression suites green.
- [ ] [milestone-6] Run disposable-worktree live provider probes, record versions/events/diagnostics/duration, complete documentation synchronization, and establish merge readiness.

## Surprises & Discoveries

- Observation: The authoritative OKF source is unchanged from the design handoff.
  Evidence: On 2026-09-09 UTC, `git ls-remote https://github.com/GoogleCloudPlatform/open-knowledge-format.git refs/heads/main` returned `ad30107c31c06aec8a7d5636e0d1058118604e6f`, and the fetched `SPEC.md` SHA-256 remained `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Observation: The current corpus is a small atomic migration but has two distinct legacy frontmatter shapes.
  Evidence: The baseline contains 31 canonical Markdown files: 6 instruction concepts, 16 non-summary memory concepts, and 9 source summaries. Twenty-two files use `coverage`; nine summaries use `status: verified`; exact lowercase `index.md` and `log.md` do not exist.
- Observation: Provider documentation still does not expose an authoritative changed-file list after a tool call.
  Evidence: Current Copilot `postToolUse` and Gemini `AfterTool` payloads expose the tool name, arguments, result, and working directory, but not a diff or changed-files field. The authoritative final behavior therefore remains a full two-bundle scan.
- Observation: Copilot's current contract supports the chosen events but explicitly bounds enforcement.
  Evidence: GitHub documents ordered execution for same-type hooks, full-match tool-name regexes, `postToolUse` additional context, stop-hook blocking, fail-open timeouts, and a host override after eight consecutive stop blocks.
- Observation: Gemini documents `AfterTool` and `AfterAgent`, but the final event remains a live release risk.
  Evidence: Gemini's current hook reference documents structured deny/retry behavior and `stop_hook_active`; official issue `google-gemini/gemini-cli#27712` is still open and reports `AfterAgent` not firing in version 0.45.0 and related versions.
- Observation: This planning environment cannot run provider capability probes.
  Evidence: Python is 3.12.3, while both `copilot --version` and `gemini --version` return command-not-found. Gate 6 must run in an authenticated environment with both target CLIs installed.
- Observation: A shell counter incremented inside command substitution does not provide persistent case-directory uniqueness, and interpolating a `TMPDIR`-influenced path into a trap string reparses that path as shell code.
  Evidence: Gate 1 review found every `case_repo="$(new_case_repo ...)"` call ran the helper in a subshell and found the original interpolated EXIT trap vulnerable to metacharacters in `TMPDIR`. The accepted harness now uses a fresh `mktemp -d` directory per case and `trap cleanup EXIT` with a quoted exact path.
- Observation: The user will create the Gate 1 checkpoint manually.
  Evidence: Commit preflight found branch `main` and empty repository Git author name/email; the user explicitly asked Codex to leave the reviewed worktree uncommitted.
- Observation: The first green Gate 2 fixture run did not cover six important failure boundaries.
  Evidence: Independent review found that a matching site-package PyYAML could mask a missing vendor, non-string `status` could raise `TypeError`, per-file read errors lost their path, code masking shifted link locations, regex-only Markdown parsing missed balanced forms, and nested YAML diagnostics used parent-key locations. Targeted public-CLI regressions and fixes are in progress before Gate 2 acceptance.
- Observation: Gate 3 has no external model CLI in this environment, but independent task agents are available.
  Evidence: `copilot`, `gemini`, and `claude` are absent from `PATH`; the collaboration runtime exposes exact model `gpt-5.6-luna`, so Gate 3 will use paired task-agent runs and record the missing token telemetry instead of inventing it.
- Observation: Gate 3's first synthetic grader could pass unsafe model behavior.
  Evidence: Independent review found incomplete path-type precedence, ambiguous lint-failure reporting, four prompts without deterministic inputs, permissive output-file/provenance checks, keyword-only completion checks, and no assertion against reverse orchestration. Nine public-CLI synthetic regressions now pass after requiring the complete eight-eval/two-configuration workspace, saved artifacts, timing schema, exact output files, reference and scoped-diff evidence, response claim safety, and every path-derived type branch.
- Observation: A live benchmark agent briefly wrote shared eval metadata outside its assigned run directory before removing it.
  Evidence: The agent reported the mistake; the coordinator rechecked that all eight coordinator-owned `eval_metadata.json` files remained present. Subsequent prompts repeat the exact run-root boundary and forbid shared metadata writes.
- Observation: Collaboration-agent benchmark timing uses multiple schemas and can explicitly report unavailable telemetry.
  Evidence: Runs emitted `total_duration_seconds`, `duration_ms`, or `duration_seconds`, while token counts were unavailable. The public grader now accepts a nonnegative value from any supported duration field or an explicit `null`, but still rejects missing, empty, negative, boolean, or malformed timing data. Aggregation normalized the generated artifacts to numeric `total_duration_seconds` without inventing token counts.
- Observation: The repository benchmark aggregator hard-codes placeholder model/path metadata and three runs per configuration.
  Evidence: The first aggregate produced `<model-name>`, `<path/to/skill>`, and `runs_per_configuration: 3` for a one-run collaboration batch. Generated metadata was corrected to `gpt-5.6-luna`, `.agents/skills/okf-authoring`, and one run before regenerating `review.html`; the shared aggregator source was left unchanged.
- Observation: The first completed Gate 3 benchmark was a false pass because the grader trusted model-authored lint claims.
  Evidence: The run `outputs/repo` trees intentionally contained only scenario output files and no executable linter or complete two-bundle fixture, yet with-skill responses and outcomes claimed clean full-corpus lint. Independent review traced `scripts/lint-okf.py` repository discovery at lines 80-85 and 567-571 and rejected the 58/58 result. The generated workspace was discarded. The replacement grader copies the checked-in valid fixture, applies scenario output, executes the real linter, records harness-owned evidence, and compares the actual scoped diff.
- Observation: A fresh Gate 3 rereview found two executor-model contradictions and unusable reviewer metadata in the first replacement aggregate.
  Evidence: Eval 3 named `gpt-5.6-sol`, eval 6 named `gpt-6`, and `review.html` lacked prompts and eval IDs. Both runs were replaced through explicit `gpt-5.6-luna` routing; every run now records that routing in `timing.json` and `execution-manifest.json`, and run-local eval metadata supplies all prompts and IDs to the regenerated viewer.
- Observation: Gate 3 timing and token telemetry is incomplete and cannot support comparisons.
  Evidence: Duration is observed for 5 of 16 runs and tokens for 3 of 16. `benchmark.json` and `benchmark.md` omit timing/token statistics and deltas and report coverage instead of treating normalized aggregation placeholders as observations.
- Observation: Gate 3's grader emitted expectation arrays in Python set iteration order, so identical reruns could rewrite accepted artifacts without changing scores.
  Evidence: A resumed acceptance run changed both eval-0 `grading.json` files. A public-CLI regression failed under `PYTHONHASHSEED=1` versus `2`; sorting expected output paths made the grader deterministic across seeds `1`, `2`, `42`, and `random`, with scores unchanged at 72/72 with-skill and 52/72 without-skill. The shared aggregator exits 1 at `aggregate_benchmark.py:51` because it cannot add explicit `null` timing values. The tested score-preserving synchronizer now refreshes grading payloads while refusing score changes, after which the standard viewer generator refreshes `review.html` without fabricating telemetry.
- Observation: Raw source paths cannot be interpolated into plain YAML or unescaped URI references in generated summary metadata.
  Evidence: A source named `nested/source #1?.md` truncated at `#` under YAML/URI parsing. Both producers now JSON-quote dynamic YAML scalars and percent-encode the resource path while preserving `/`; both provider suites cover the special path.
- Observation: Metadata-only corpus migration exposed stale body instructions and two directory-valued index links that the OKF profile rejects.
  Evidence: Initial full-corpus lint reported `OKF103` for the two `INDEX.md` directory links, and review found body text still teaching `coverage:` and `status: scaffold`. The approved semantic corrections now point to regular files and teach path-derived type/description plus exact draft-summary frontmatter semantics.
- Observation: Literal frontmatter-line matching is not equivalent to YAML scalar comparison.
  Evidence: Both provider hooks classified `type: "Source Summary" # quoted scalar` plus `status: "draft" # unresolved lifecycle` as active. Symmetric public-hook tests reproduced the bypass before the correction and pass after top-level scalar normalization.

## Decision Log

- Decision: Treat `.agents/instructions/` and `.agents/memory/` as two physical OKF bundles while preserving every existing canonical path.
  Rationale: This changes representation in place without pulling immutable sources, scratchpad state, or repo-local skills into a broad `.agents/` bundle and without creating duplicate knowledge.
  Date/Author: 2026-09-09 / closed migration contracts
- Decision: Require repository-profile `type` and `description` fields, use path-derived types, omit stable `status`, and tolerate unknown fields.
  Rationale: `type` is the OKF minimum; the repository additionally needs descriptions for routing and a deterministic local taxonomy while preserving OKF extension tolerance.
  Date/Author: 2026-09-09 / closed document contract
- Decision: Use `scripts/lint-okf.py` as the only profile authority and provider adapters as subprocess envelopes around its JSON result.
  Rationale: One full-corpus implementation prevents Copilot/Gemini drift and avoids inferring correctness from incomplete tool arguments or Git state.
  Date/Author: 2026-09-09 / closed linter contract
- Decision: The linter's machine output is an object with `schema_version: 1` and a `diagnostics` list. Each diagnostic has exactly `id`, `path`, `line`, `column`, and `message`; line and column are one-based.
  Rationale: A small versioned envelope gives adapters a stable parse target while retaining the contract's required diagnostic fields. Human output renders each item as `path:line:column: ID message` in the same order.
  Date/Author: 2026-09-09 / Codex
- Decision: Use `scripts/fixtures/okf-valid-repo/` as the single checked-in valid fixture and copy it into a temporary directory for every negative test.
  Rationale: One valid source fixture plus one mutation per test prevents fixture drift and false passes caused by unrelated invalid data.
  Date/Author: 2026-09-09 / closed sequencing contract, path selected by Codex
- Decision: The pre-agreed TDD seams are the linter CLI, provider adapter stdin/stdout/exit behavior, source-summary scaffold output, and model-observable `okf-authoring` behavior. Do not test private helper functions directly.
  Rationale: The closed contracts already confirm these externally meaningful boundaries; testing private parsing helpers would couple the suite to implementation structure.
  Date/Author: 2026-09-09 / Codex
- Decision: Start Gemini `AfterAgent` with the existing source-ingest validator and the OKF validator as two commands in one `sequential: true` group, in that order. Start Copilot with two ordered entries, source ingest first. Add a coordinator only if a live simultaneous-failure probe proves the host loses a blocking reason.
  Rationale: This preserves independent responsibilities and follows the provider's ordering mechanisms without speculatively adding orchestration code.
  Date/Author: 2026-09-09 / closed hook and sequencing contracts
- Decision: Pin PyYAML to the upstream 6.0.3 source distribution and vendor only `lib/yaml/`, its license, and a source record under `scripts/vendor/`.
  Rationale: Hooks must not install dependencies at runtime, and the accepted pure-Python parser must remain auditable and reproducible.
  Date/Author: 2026-09-09 / closed linter contract
- Decision: Treat fixture-case isolation and stdout/stderr behavior as part of the public CLI test contract.
  Rationale: Per-case `mktemp` repositories prevent mutation leakage, while separate stream capture enforces the repository rule that primary human and JSON output uses stdout and unexpected errors use stderr.
  Date/Author: 2026-09-09 / Codex
- Decision: Use runtime task agents with `gpt-5.6-luna` for both `with_skill` and `without_skill` Gate 3 runs.
  Rationale: No external evaluation CLI is installed; the ExecPlan permits independent task agents, and using the same Fast model on both sides gives a fair weaker-model comparison. The runtime does not expose token totals, so timing artifacts must mark token telemetry unavailable rather than fabricate values.
  Date/Author: 2026-09-09 / Codex
- Decision: Detect unresolved source summaries by normalized top-level `type` and `status` scalar values instead of exact frontmatter lines.
  Rationale: YAML permits quoted scalars and comments without changing their values. The source-ingest hooks remain standard-library-only, so the narrow parser normalizes the two contract fields while malformed values fail safely as non-matches.
  Date/Author: 2026-09-10 / Codex

## Outcomes & Retrospective

Gates 1–3 are committed, with Gate 3's final rollback checkpoint at `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735`. Gate 4's corpus and scaffold cutover is committed at `d21c4351`; all 31 canonical paths are preserved, full-corpus lint is clean, and raw sources are unchanged. A resumed review found and reproduced one semantic YAML draft-detection bypass; its symmetric correction is green but remains outside that checkpoint pending follow-up review and the user's manual commit. No provider lint hooks are enabled.

## Context and Orientation

`AGENTS.md` is the mandatory repository entry point. It tells agents to read `.agents/memory/INDEX.md`, which routes them to the canonical documents under `.agents/instructions/` and `.agents/memory/`. An OKF bundle is a directory tree of UTF-8 Markdown concept documents with YAML frontmatter. In this migration, those two canonical roots are separate bundles, and every `.md` file below either root is a concept. A concept's identity is its bundle-relative path without `.md`, so files must not move or change case.

The current 31 concepts have useful bodies that must remain intact. The 22 ordinary canonical documents begin with a `coverage` field. The 9 completed source summaries begin with `status: verified` and are bound to immutable raw inputs by `.agents/memory/sources/source-ingest-manifest.json`. Gate 4 changes only the representation needed by the contract: ordinary files replace `coverage` with `type` and `description`; completed summaries replace the legacy status with `type`, `description`, and one `sources` entry. Body rewriting is out of scope except where a body currently teaches the obsolete frontmatter format, notably `.agents/memory/INDEX.md` and `.agents/skills/update-agent-docs/refs/indexes-frontmatter.md`.

`scripts/lint-okf.py` is the complete validation authority. The future repo-local adapters `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` will read their provider payload, locate the repository from `cwd`, execute the central linter in JSON mode, cap the shared diagnostic text, and emit only the provider-specific JSON envelope. They must not contain document-profile rules.

Source ingestion remains independent. `.github/hooks/scripts/helpers/auto_ingest.py` and `.gemini/hooks/scripts/helpers/source_ingest.py` are intentionally duplicated scaffold producers. Both emit a conforming `Source Summary` with `status: draft` and a file-relative raw-source resource, and both detect unresolved summaries from normalized top-level `type` and `status` scalar values rather than literal YAML lines. The manifest continues to own freshness, hashes, rename/orphan state, and source-to-summary binding. The OKF linter reads that manifest but never updates it.

The authoring workflow has two repository-local homes. `.agents/skills/okf-authoring/` owns the model-invoked representation workflow. `.agents/skills/update-agent-docs/` owns the semantic documentation workflow. Gate 3 adds a one-way instruction from `update-agent-docs` to invoke `okf-authoring` after semantic edits; `okf-authoring` must never call back into `update-agent-docs`.

The normative external sources for implementation are the pinned [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md), the current [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), the current [Gemini hooks reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md), Gemini's [hook writing guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/writing-hooks.md), and the open [Gemini AfterAgent issue](https://github.com/google-gemini/gemini-cli/issues/27712). Recheck them at Gate 5 and record any contract-changing difference in this plan before editing provider code.

## Ownership and Coordination

Use parallel agents only inside one gate and only with the following non-overlapping ownership. The coordinating owner retains this ExecPlan, shared configuration, integration, final validation, and all commits. An agent must not edit outside its assigned paths.

| Workstream | Exclusive paths while active | Transfer point |
| --- | --- | --- |
| Linter and fixture owner | `scripts/lint-okf.py`, `scripts/test-okf-lint.sh`, `scripts/fixtures/okf-valid-repo/**`, `scripts/vendor/**` | Returns ownership after Gate 2 |
| Authoring skill owner | `.agents/skills/okf-authoring/**`, `skills/okf-authoring-workspace/**`, `.agents/skills/update-agent-docs/**` | Returns ownership after Gate 3 |
| Corpus and scaffold owner | `.agents/instructions/**`, `.agents/memory/**`, `.github/hooks/scripts/helpers/auto_ingest.py`, `.gemini/hooks/scripts/helpers/source_ingest.py`, `scripts/test-hooks-auto-ingest.sh`, `scripts/test-gemini-hooks-auto-ingest.sh` | Returns canonical documentation ownership to the coordinator after Gate 4 |
| Provider adapter owner | `.github/hooks/scripts/lint-okf.py`, `.gemini/hooks/scripts/lint-okf.py`, `scripts/test-hooks-okf-lint.sh`, `scripts/test-gemini-hooks-okf-lint.sh` | Returns ownership after Gate 5 |
| Coordinating owner | `docs/okf-kb-migration/implementation-execplan.md`, `.github/hooks/hooks.json`, `.gemini/settings.json`, `scripts/install.sh`, `scripts/test-install.sh`, repo-wide documentation integration and commits | Never delegated |

Gates run sequentially. Within a gate, agents may work in parallel only when their paths do not overlap. Shared-path ownership transfers only after the prior owner has stopped and the coordinator has reviewed its diff. The coordinator integrates, runs gate checks, records evidence here, and then commits the gate. No agent enables a hook or migrates part of the canonical corpus early.

## Plan of Work

### Milestone 1: Establish the baseline and red tests

Status: done
Acceptance: met

Record the starting commit and inventory in `Artifacts and Notes`. Confirm that the corpus still has 31 Markdown concepts, 22 `coverage` frontmatter blocks, 9 `status: verified` summaries, and no exact lowercase reserved paths. Confirm the existing source-ingest and startup suites are green before changing their fixtures.

Create `scripts/fixtures/okf-valid-repo/` as the one valid fixture repository. It must contain both `.agents/instructions/` and `.agents/memory/`, a minimal `.agents/sources/example.md`, a matching manifest, and enough concepts to exercise every path-derived type: `Agent Instruction`, `Agent Memory`, `Knowledge Index`, `Source Ingestion Log`, `Known Issue`, `Testing Guidance`, `Architecture Decision`, and `Source Summary`. Include one valid cross-bundle Markdown link, one valid link to a repository file outside both bundles, one external URL, one fragment-only link, one image/resource target, one unknown frontmatter field, one completed source-summary binding, and no lowercase `index.md` or `log.md`.

Create `scripts/test-okf-lint.sh`. Each case copies the valid fixture to a fresh `mktemp -d` repository and mutates exactly one condition. Tests invoke the public command from the fixture root, never a private helper. Cover clean human and JSON output, stable ordering, exit codes 0/1/2, every `OKF001` through `OKF007`, every `OKF101` through `OKF105`, `OKF900`, all path-derived types, standard metadata shapes, unknown-field acceptance, explicit-offset timestamps, local links/resources, ignored links in code/comments, lifecycle rules, and manifest-backed summary provenance. Assert one-based locations and the exact JSON envelope. Add an initial vendor-record assertion for the accepted version, URL, license, and source hash.

Run the new suite before creating production code. Its first red state must be the missing `scripts/lint-okf.py` entry point, not malformed test setup. Record the short failing transcript. This is a horizontal inventory only; subsequent work proceeds in vertical red-to-green slices by diagnostic family.

Milestone acceptance is the checked-in fixture and test suite with a documented, intentional red result, plus green pre-existing source-ingest/startup tests. No linter, vendor files, skill, migration, adapter, or hook registration exists yet.

### Milestone 2: Implement the dormant linter in vertical slices

Status: done
Acceptance: met

Vendor PyYAML 6.0.3 from the official source archive. Verify the archive SHA-256 before copying `pyyaml-6.0.3/lib/yaml/` to `scripts/vendor/yaml/`. Copy the upstream license to `scripts/vendor/PyYAML-6.0.3.LICENSE` and add `scripts/vendor/PyYAML-6.0.3.SOURCE` containing the version, source URL, and SHA-256. `scripts/lint-okf.py` must prepend only `scripts/vendor/` to its import path, require `yaml.__version__ == "6.0.3"`, and emit `OKF900` with exit 2 if the pinned package cannot be loaded. It must never install or fetch at runtime.

Implement `scripts/lint-okf.py` one diagnostic family at a time, running the focused test after every red-to-green slice. The CLI has only `--format human|json`, defaulting to human. Starting at the current directory, it walks upward to the nearest directory containing both `.agents/instructions/` and `.agents/memory/`; failure to establish that root is `OKF900`. It recursively scans every `.md` file in both bundles. Exact lowercase `index.md` and `log.md` yield `OKF007` and are not treated as ordinary concepts. All diagnostics are sorted by normalized repository-relative path, line, column, then ID.

Use a frozen `Diagnostic` data value internally with string `id`, POSIX-style repository-relative string `path`, positive integer `line`, positive integer `column`, and string `message`. Use a copied `yaml.SafeLoader` with implicit timestamp resolution disabled so timestamp text can be validated without automatic coercion. A concept must begin at byte zero with a `---` delimiter, end its frontmatter with a second exact delimiter line, decode as UTF-8, and parse to a mapping. Do not cascade field/type/link diagnostics from a file whose bytes or frontmatter cannot be trusted.

Locations are deterministic. Byte/decoding, missing-delimiter, forbidden-path, missing-field, manifest-level, and internal failures use line 1, column 1 of the affected repository-relative path. YAML syntax uses the parser's one-based problem mark. A present frontmatter key uses that key's one-based start location. A body link uses the first character of its destination. Tests assert these rules rather than incidental helper positions.

Enforce these metadata shapes. `type` and `description` are non-empty strings. Optional `title` and top-level `resource` are non-empty strings. `tags` is a list of non-empty strings. `sources` is a list of mappings, each with non-empty string `resource`; optional `id`, `title`, and `author` are non-empty strings; optional `usage_count` is a non-negative integer but not a Boolean; optional `last_modified` is an explicit-offset ISO 8601 datetime; and optional per-source or top-level `usage_window` is a mapping with explicit-offset `from` and `to` datetimes. `generated` is a mapping with non-empty `by` and explicit-offset `at`. `verified` is a list of mappings, each with non-empty `by` and explicit-offset `at`; a bare mapping is rejected by the repository profile. `stale_after` is an explicit-offset ISO 8601 datetime. `status` may be `draft` or `deprecated`; omission means stable. Exact `status: stable`, `status: scaffold`, `status: verified`, and any `coverage` field are `OKF105`; other status values or malformed standard fields are `OKF005`. Unknown keys remain accepted.

Derive `type` in this precedence order: every instruction document is `Agent Instruction`; memory `INDEX.md` is `Knowledge Index`; memory `LOG.md` is `Source Ingestion Log`; memory root `KNOWN_ISSUES.md` and `known-issues/**` are `Known Issue`; memory root `TESTING_STRATEGY.md` and `testing/**` are `Testing Guidance`; `adrs/**` are `Architecture Decision`; `sources/**/*.summary.md` are `Source Summary`; remaining memory documents are `Agent Memory`. A mismatch is `OKF101`.

Validate Markdown inline links, images, reference-definition destinations, top-level `resource`, and each `sources[].resource`. Mask fenced code, inline code, and HTML comments before scanning body links. Allow fragment-only targets and any syntactically valid external URI scheme. For local targets, remove query and fragment components, percent-decode, reject filesystem-absolute and leading-slash bundle-root forms, resolve from the owning document's directory, require the normalized target to remain below the repository root, and require it to be a regular file. Escape is `OKF102`; missing/non-file destination is `OKF103`. Do not validate renderer-specific heading slugs.

For every source-summary concept, load `.agents/memory/sources/source-ingest-manifest.json` as read-only JSON. Match exactly one manifest entry by the summary's path relative to `.agents/memory/sources/`. Require exactly one `sources` entry and require its resolved target to equal `.agents/sources/<manifest source_path>`. A missing, duplicate, or mismatched binding is `OKF104`. Link existence and manifest binding are independent checks, so a missing raw file may also yield `OKF103`. Never modify hashes, states, reasons, paths, or the manifest itself.

Human mode prints every finding as `path:line:column: ID message`; clean output may be silent. JSON mode always emits one JSON object with `schema_version: 1` and `diagnostics`, including on internal failure. Exit 0 means no diagnostics, exit 1 means only conformance/profile findings, and exit 2 means at least one `OKF900`. Set executable mode 755 on the linter.

Milestone acceptance is a green `bash scripts/test-okf-lint.sh`, syntax-valid linter and vendored modules, deterministic repeated JSON output apart from no timing field, and proof that no provider hook is registered and the current canonical corpus is still allowed to remain nonconforming until Gate 4.

### Milestone 3: Add and evaluate the authoring skill

Status: done
Acceptance: met

Before creating the skill, search both `.agents/skills/` and `skills/` descriptions and names for an existing equivalent; record that no existing skill owns the OKF representation contract or refine the existing owner instead of creating a duplicate. For the expected new repository-local skill, create `.agents/skills/okf-authoring/SKILL.md`, `.agents/skills/okf-authoring/references/profile.md`, `.agents/skills/okf-authoring/references/source-summaries.md`, `.agents/skills/okf-authoring/evals/evals.json`, and a deterministic `.agents/skills/okf-authoring/evals/grade_benchmark.py`. Keep invocation, the six-step workflow, one-way orchestration, read-only review behavior, and completion reporting in `SKILL.md`. Put shared type/metadata/link/lifecycle rules in `profile.md`; put only draft/completed summary provenance and scaffold examples in `source-summaries.md`. Do not add a general examples file unless evaluation evidence justifies it.

The description must trigger on creating, modifying, migrating, or reviewing Markdown under `.agents/instructions/` or `.agents/memory/`, including work initiated by `update-agent-docs` or `ingest-source`. It must not trigger for ordinary reads, files outside those roots, or immutable `.agents/sources/`. The workflow identifies affected bundles and path-derived types, loads the profile and only the needed branch reference, preserves paths and unrelated body text, checks routing/index implications, runs the full linter, inspects the scoped diff, and refuses a completion claim when lint is unavailable.

Update `.agents/skills/update-agent-docs/SKILL.md` so its semantic pass invokes `okf-authoring` after it has made canonical-document changes and before it reports completion. Update `.agents/skills/update-agent-docs/refs/indexes-frontmatter.md` to teach path-derived `type` plus `description` instead of coverage-only frontmatter. Preserve `update-agent-docs` as the owner of durability, placement, deduplication, indexes, and routing. Do not add any reverse invocation to `okf-authoring`; `.agents/skills/ingest-source/SKILL.md` continues to reach it through its existing final `update-agent-docs` step.

Create eight realistic evaluations: ordinary concept creation; metadata-only migration with byte-preserved body and stable path; draft summary; completed summary; `update-agent-docs` composition; read-only conformance review; an outside-root negative case; and unavailable-linter refusal. Each eval must have deterministic expectations in `evals.json`; the grader checks produced files, path/body preservation, frontmatter, reference loading, report contents, absence of out-of-scope edits, and refusal of false completion. Compare the new skill with a no-skill baseline in `skills/okf-authoring-workspace/iteration-1/`.

Before the first live eval, record the available evaluation runner and model in this ExecPlan. Run every eval with and without the exact local skill path in the same batch, save `response.md`, `transcript.md`, and `timing.json` under the canonical per-eval directory, then grade and generate the reviewer:

    python3 .agents/skills/okf-authoring/evals/grade_benchmark.py skills/okf-authoring-workspace/iteration-1
    python3 .agents/skills/okf-authoring/evals/sync_benchmark.py skills/okf-authoring-workspace/iteration-1
    python3 skills/skill-creator/eval-viewer/generate_review.py skills/okf-authoring-workspace/iteration-1 --skill-name okf-authoring --benchmark skills/okf-authoring-workspace/iteration-1/benchmark.json --static skills/okf-authoring-workspace/iteration-1/review.html

The checked-in `.agents/skills/okf-authoring/evals/sync_benchmark.py` is the accepted Gate 3 aggregation path for this benchmark. It refreshes every run's expectations from the grader, verifies that all score summaries remain unchanged, and preserves the accepted incomplete-telemetry aggregate instead of passing explicit `null` durations to the generic aggregator. If any score changes, it exits nonzero and requires a separately supported full aggregation rather than silently leaving stale summary metrics.
If `copilot` is the runner, use its documented non-interactive form for each recorded prompt and grant only the write/shell tools required inside the eval sandbox:

    copilot -p '<exact eval prompt>' -s --allow-tool='write, shell(python3:*), shell(git:*), shell(bash:*)' --output-format json --share '<run-dir>/transcript.md'

Do not assume the response JSON schema: run `copilot --version` and `copilot --help`, capture one smoke result, then record the exact extraction command in this ExecPlan before the batch starts. If the runtime instead provides independent task agents, follow the loaded `skill-creator` workflow: start with-skill and no-skill runs together, save completion timing immediately, and use the same workspace schema. Human review of `review.html` occurs before revising the skill.

Milestone acceptance requires a green quick validation, valid grader syntax, a completed no-skill comparison, generated benchmark/reviewer artifacts, user-reviewed outputs or explicit recorded acceptance, and tests showing that invocation remains one-way and read-only reviews make no edits. The canonical corpus still has not migrated and hooks remain disabled.

### Milestone 4: Perform the atomic corpus and scaffold cutover

Status: in progress
Acceptance: not met

Record the Gate 3 commit hash as the rollback checkpoint. Migrate all canonical documents and both scaffold producers in one gate; do not commit or hand off a partially converted corpus. For each of the 22 coverage-based files, preserve path and body and replace the frontmatter with the exact path-derived `type` followed by `description` containing the prior `coverage` value. Do not synthesize `generated`, `verified`, `stale_after`, tags, titles, or lifecycle status.

For each of the nine completed summaries, preserve the body, remove `status: verified`, add `type: Source Summary`, use the corresponding current `.agents/memory/INDEX.md` routing phrase as the description, and add exactly one source resource `../../sources/<source_path>` using the manifest's `source_path`. The nine routing descriptions are:

- `12-factor-cli-apps-md.summary.md`: CLI UX guidance for help text, stream discipline, prompts, tables, or XDG path conventions.
- `cli-design-guidelines-md.summary.md`: Concise CLI UX defaults such as naming, prompts, errors, progress, or expressive flags.
- `clig-dev-md.summary.md`: Broader CLI interaction design, configuration precedence, output conventions, or future-proofing decisions.
- `copilot-hooks-ref-md.summary.md`: Copilot hook events, cross-surface behavior, matcher semantics, or exit-code handling.
- `gemini-hooks-best-practices-md.summary.md`: Gemini hook performance, debugging, threat-model, privacy, or hardening guidance.
- `gemini-hooks-writing-md.summary.md`: Gemini hook authoring patterns, tool filtering, or multi-event workflow composition.
- `gemini-hooks-md.summary.md`: Gemini hook event coverage, config precedence, trust behavior, or `/hooks` operations.
- `llm-wiki-md.summary.md`: Source-ingest workflow, wiki/log/index structure, or compiled-knowledge maintenance patterns.
- `vscode-agent-hooks-md.summary.md`: VS Code hook compatibility, hook locations, or agent-scoped hook behavior.

Change both `.github/hooks/scripts/helpers/auto_ingest.py` and `.gemini/hooks/scripts/helpers/source_ingest.py` in lockstep. Their scaffold frontmatter becomes `type: Source Summary`, a pending routing description naming the raw source, `sources: [{resource: ../../sources/<source_relpath>}]` in normal YAML list form, and `status: draft`. Update scaffold detection to parse only the frontmatter and recognize exact draft summary semantics rather than searching the body for a marker. Preserve lock scope, streaming hashes, path sanitization, manifest schema, orphan behavior, write failure handling, and raw-source immutability. Update both existing auto-ingest suites first so the old scaffold fails and the new shape passes; then make the minimal producer changes.

Because converting each completed summary changes its bytes, refresh only the nine `summary_hash` values in `.agents/memory/sources/source-ingest-manifest.json` after the summary edits. Keep `version`, `source_path`, `summary_path`, `content_hash`, `size`, `state`, and `reason` unchanged. Use one existing source-ingest reconciler against the real repository or compute the SHA-256 values directly, then inspect the manifest diff. Without this step, the next startup scan would rewrite the committed manifest even though no source became stale.

Run `./scripts/lint-okf.py` and its JSON mode against the real corpus. The expected result is exit 0 and an empty diagnostics list. Compare every canonical body before and after the migration, allowing body differences only in documents that explicitly teach frontmatter and require semantic correction. Verify no canonical path moved, no lowercase reserved file appeared, every summary resource matches its manifest entry, and `AGENTS.md` still routes first to uppercase `.agents/memory/INDEX.md`.

Milestone acceptance is the indivisible green two-bundle corpus, both green source-ingest suites, unchanged immutable raw sources and manifest behavior, and a scoped diff containing only the approved canonical metadata/body-teaching changes and both scaffold producer/test pairs. No provider adapter is registered yet.

### Milestone 5: Add provider adapters and candidate registrations

Status: open
Acceptance: not met

Recheck the official provider sources named in `Context and Orientation` and record the installed target CLI versions. If an event, matcher, envelope, exit, timeout, or retry contract changed, stop, document the contradiction in `Surprises & Discoveries` and `Decision Log`, and revise this ExecPlan before editing adapters.

Create `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` as separate thin executable adapters. Reuse only the provider-local common input/output and path-normalization helpers. Each adapter reads one complete JSON payload, finds the repository from `cwd`, runs `sys.executable <repo>/scripts/lint-okf.py --format json` with an 8-second subprocess timeout inside the host's 10-second limit, validates `schema_version` and diagnostic fields, and formats at most the first 20 sorted findings into less than 8 KiB including the omitted count and rerun command. POSIX rerun text is `./scripts/lint-okf.py`; Windows rerun text is `python scripts/lint-okf.py`. Malformed input, missing linter/vendor, subprocess timeout, invalid linter JSON, exit 2, and unexpected exceptions become a synthetic `OKF900` blocking response. Stdout is exactly one provider-valid JSON object and expected control flow exits 0.

The Copilot adapter returns `{}` on clean `postToolUse`, `additionalContext` on invalid `postToolUse`, `decision: allow` on a clean stop, and `decision: block` plus `reason` on an invalid `agentStop` or `subagentStop`. The Gemini adapter returns `{}` on clean events, `decision: deny` plus `reason` on invalid `AfterTool`, `decision: deny` on the first invalid `AfterAgent`, and `continue: false` plus `stopReason` when an invalid `AfterAgent` arrives with `stop_hook_active` true.

Create `scripts/test-hooks-okf-lint.sh` and `scripts/test-gemini-hooks-okf-lint.sh` before adapter implementation. At the adapter stdin/stdout seam, cover clean and invalid corpora, diagnostic parity with central JSON, malformed payloads, missing dependencies, `OKF900`, 20-item/8-KiB truncation, every event envelope, Gemini retry state, Copilot subagent stops, and simultaneous pending-ingest plus OKF failures. Keep source-ingest helpers real in integration cases instead of mocking internal functions.

Update `.github/hooks/hooks.json` only after static adapter tests are green. Keep the existing source-ingest command first in `agentStop` and `subagentStop`, then add the OKF command with `bash: ".github/hooks/scripts/lint-okf.py"`, `powershell: "python \".github/hooks/scripts/lint-okf.py\""`, and `timeoutSec: 10`. Add `postToolUse` with the candidate full-match matcher `bash|powershell|create|edit` and the same OKF command fields. Update `.gemini/settings.json` so `AfterAgent` uses one `sequential: true`, match-all group containing the existing source-ingest command first and an independently named `lint-okf` command second, with `command: "python .gemini/hooks/scripts/lint-okf.py"` and `timeout: 10000`. Add `AfterTool` with matcher `write_file|replace|run_shell_command` and the same OKF command. Set only OKF hook timeouts to 10 seconds.

Run adapter parity tests, both existing source-ingest suites, both startup suites, `python3 scripts/test_helpers.py`, and `bash scripts/test-install.sh`. Verify executable mode 755 for all new Python entry points. Do not add repository-specific OKF registrations to `.copilot/hooks/hooks.json` or `.gemini/global-settings.json`.

Milestone acceptance is green static/simulated behavior with candidate repo-local registrations and identical normalized diagnostics. This gate does not establish release readiness; hook enablement remains unshippable until Gate 6 proves the deployed CLIs actually fire every required event and matcher.

### Milestone 6: Prove live behavior and finish the migration

Status: open
Acceptance: not met

Commit the Gate 5 candidate so disposable worktrees contain the exact configuration under test. Run `./scripts/install.sh` from the main candidate worktree before installed-skill checks; do not repurpose `HOME`. If the current agent environment cannot write the user's install targets, record the limitation and run installation from a writable user shell before continuing. Create a fresh detached worktree for each provider and remove it with `git worktree remove <exact-path>` only after recording evidence.

Record `copilot --version`, `copilot --help`, `gemini --version`, and `gemini --help`. For Copilot, run non-interactive `copilot -p` probes with minimally scoped tool permissions and `--share` transcripts. Prove each configured mutation matcher on a deliberately invalid canonical document, then prove `agentStop` correction and a YAML/custom task subagent that emits `subagentStop`; the built-in `general-purpose` agent is not acceptable because GitHub documents that it omits subagent lifecycle events. Inspect the transcript for the expected `OKF` diagnostic, verify the agent received immediate feedback, and verify the final full-corpus lint is green before treating the probe as passed. Run the PowerShell matcher probe on a supported Windows target; if that surface is in the configuration but cannot be observed, the gate remains incomplete.

For Gemini, run non-interactive probes with `gemini -p '<prompt>' --approval-mode=yolo --output-format json --debug`. Prove `write_file`, `replace`, and `run_shell_command` each fire `AfterTool` and surface the expected diagnostic. Seed an invalid canonical concept before a no-tool response probe to prove `AfterAgent` fires, denies the first completion, and honors `stop_hook_active` without an unbounded loop. Because issue 27712 remains open, documentation alone is not evidence. Inspect debug output or the provider's hook listing/logs and retain a concise event transcript in this plan.

In both providers, create simultaneous pending-ingest and invalid-OKF state in the disposable worktree. Prove source-ingest runs first and the agent receives both actionable reasons. If either host drops one reason, record the failure, add a new failing regression, and only then introduce a thin provider-local final-validation coordinator that runs the unchanged source-ingest and OKF validators and combines their reasons. Repeat every static and live probe after that change. Do not merge validator state or profile logic.

Measure the real full-corpus linter with a monotonic wall-clock command available on the target system and record elapsed time here. It must finish safely within the 10-second host timeout; there is no sub-second release requirement. Run the complete final matrix in `Concrete Steps`, the active migration-document relative-link check, canonical body/path checks, and `git diff --check`. Run the mandatory `update-agent-docs` pass after all implementation and provider work is complete, then update this plan's living sections and the migration handoff.

Milestone acceptance requires all static tests, skill evaluations, corpus lint modes, install/startup regressions, provider event/matcher probes, simultaneous-failure probes, link checks, and diff checks to pass. Record the exact merge commit or squash commit as the one rollback unit. If any required live capability is unavailable or fails, do not merge and do not claim the migration complete.

## Concrete Steps

Run all commands from `/Users/adam/dev/skills` unless a disposable worktree path is explicitly recorded.

Baseline and Gate 1:

    git status --short
    rg --files .agents/instructions .agents/memory -g '*.md' | wc -l
    rg -l '^coverage:' .agents/instructions .agents/memory -g '*.md' | wc -l
    rg -l '^status: verified$' .agents/memory/sources -g '*.summary.md' | wc -l
    rg --files .agents/instructions .agents/memory | rg '(^|/)(index|log)\.md$'
    bash scripts/test-hooks-auto-ingest.sh
    bash scripts/test-gemini-hooks-auto-ingest.sh
    bash scripts/test-hooks-startup.sh
    bash scripts/test-gemini-hooks-startup.sh
    bash scripts/test-okf-lint.sh

The first four inventory results should be 31, 22, 9, and no paths. The first Gate 1 linter-suite run must fail because `scripts/lint-okf.py` is absent.

Vendoring and Gate 2:

    okf_vendor_dir="$(mktemp -d)"
    curl -fsSL -o "$okf_vendor_dir/pyyaml-6.0.3.tar.gz" https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz
    printf '%s  %s\n' d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f "$okf_vendor_dir/pyyaml-6.0.3.tar.gz" | sha256sum -c -
    tar -xzf "$okf_vendor_dir/pyyaml-6.0.3.tar.gz" -C "$okf_vendor_dir"
    mkdir -p scripts/vendor
    cp -R "$okf_vendor_dir/pyyaml-6.0.3/lib/yaml" scripts/vendor/yaml
    cp "$okf_vendor_dir/pyyaml-6.0.3/LICENSE" scripts/vendor/PyYAML-6.0.3.LICENSE
    python3 -m py_compile scripts/lint-okf.py scripts/vendor/yaml/*.py
    bash scripts/test-okf-lint.sh
    ./scripts/lint-okf.py --format json

Gate 3:

    rg -n 'OKF|open knowledge|canonical document|frontmatter' skills/*/SKILL.md
    PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py .agents/skills/okf-authoring
    python3 -m py_compile .agents/skills/okf-authoring/evals/grade_benchmark.py
    python3 .agents/skills/okf-authoring/evals/grade_benchmark.py skills/okf-authoring-workspace/iteration-1
    python3 .agents/skills/okf-authoring/evals/sync_benchmark.py skills/okf-authoring-workspace/iteration-1
    python3 skills/skill-creator/eval-viewer/generate_review.py skills/okf-authoring-workspace/iteration-1 --skill-name okf-authoring --benchmark skills/okf-authoring-workspace/iteration-1/benchmark.json --static skills/okf-authoring-workspace/iteration-1/review.html

Gate 4:

    bash scripts/test-hooks-auto-ingest.sh
    bash scripts/test-gemini-hooks-auto-ingest.sh
    python3 - <<'PY'
    import hashlib
    import json
    from pathlib import Path

    manifest_path = Path('.agents/memory/sources/source-ingest-manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for entry in manifest['entries']:
        summary = manifest_path.parent / entry['summary_path']
        entry['summary_hash'] = hashlib.sha256(summary.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    PY
    ./scripts/lint-okf.py
    ./scripts/lint-okf.py --format json
    rg -n '^coverage:|^status: (scaffold|verified|stable)$' .agents/instructions .agents/memory .github/hooks/scripts/helpers/auto_ingest.py .gemini/hooks/scripts/helpers/source_ingest.py
    rg --files .agents/instructions .agents/memory | rg '(^|/)(index|log)\.md$'
    git diff --name-status <recorded-gate-3-commit>...HEAD

The two `rg` commands should return no legacy metadata and no lowercase reserved paths. JSON lint should be exactly a schema-versioned empty diagnostic list.

Gate 5:

    bash scripts/test-hooks-okf-lint.sh
    bash scripts/test-gemini-hooks-okf-lint.sh
    bash scripts/test-hooks-auto-ingest.sh
    bash scripts/test-gemini-hooks-auto-ingest.sh
    bash scripts/test-hooks-startup.sh
    bash scripts/test-gemini-hooks-startup.sh
    python3 scripts/test_helpers.py
    bash scripts/test-install.sh
    git diff --check

Gate 6 final matrix:

    bash scripts/test-okf-lint.sh
    ./scripts/lint-okf.py
    ./scripts/lint-okf.py --format json
    bash scripts/test-hooks-okf-lint.sh
    bash scripts/test-gemini-hooks-okf-lint.sh
    bash scripts/test-hooks-auto-ingest.sh
    bash scripts/test-gemini-hooks-auto-ingest.sh
    bash scripts/test-hooks-startup.sh
    bash scripts/test-gemini-hooks-startup.sh
    bash scripts/test-install.sh
    python3 scripts/test_helpers.py
    PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py .agents/skills/okf-authoring
    python3 -m py_compile .agents/skills/okf-authoring/evals/grade_benchmark.py
    python3 .agents/skills/okf-authoring/evals/grade_benchmark.py skills/okf-authoring-workspace/iteration-1
    git diff --check

Before Gate 6 begins, replace these live-command templates in this document with exact commands verified by each installed CLI's `--help`, including exact prompt files, output paths, model/agent choice, permissions, and worktree path:

    copilot --version
    copilot -p '<mutation or stop-event probe prompt>' -s --allow-tool='<minimal tools>' --output-format json --share '<worktree>/copilot-probe-transcript.md'
    gemini --version
    gemini -p '<mutation or AfterAgent probe prompt>' --approval-mode=yolo --output-format json --debug > '<worktree>/gemini-probe.json'

Use this exact repository-local link checker for active migration documents outside `tickets/obsolete/`; canonical documents are checked separately by the OKF linter:

    python3 - <<'PY'
    import re
    from pathlib import Path
    from urllib.parse import unquote, urlsplit

    root = Path.cwd().resolve()
    docs = root / "docs" / "okf-kb-migration"
    failures = []
    for path in sorted(docs.rglob("*.md")):
        if "obsolete" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().split()[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if root not in resolved.parents and resolved != root:
                failures.append(f"{path.relative_to(root)} escapes: {target}")
            elif not resolved.exists():
                failures.append(f"{path.relative_to(root)} missing: {target}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("active migration links: ok")
    PY

## Validation and Acceptance

The implementation is accepted only when a clean checkout produces no diagnostics in human mode, JSON mode returns `{"schema_version": 1, "diagnostics": []}`, every targeted shell/Python/skill check in the final matrix exits 0, the active migration-document link checker prints `active migration links: ok`, and `git diff --check` is silent. Tests must prove all diagnostic IDs and both provider envelopes are derived from identical normalized findings.

Behavioral acceptance requires more than static configuration. In disposable worktrees, every configured Copilot and Gemini mutation matcher must visibly fire after a deliberate invalid canonical write, Copilot `agentStop` and `subagentStop` must return correction feedback, Gemini `AfterAgent` must reject an invalid completion and stop safely on a repeated active hook, and simultaneous source-ingest/OKF failures must preserve both reasons in the documented order. Every probe ends with the disposable worktree's full corpus green or with the worktree discarded; never leave a deliberate invalid concept in the main worktree.

The source-ingest manifest must retain version 1 and its existing state/hash/orphan semantics. All raw files under `.agents/sources/` must be byte-identical to the Gate 3 checkpoint. All 31 canonical paths and bodies must be preserved except the explicitly approved frontmatter-teaching prose. `AGENTS.md` must continue to route to uppercase `.agents/memory/INDEX.md`, and no selector, sidecar, prompt injection, provider runtime, compatibility parser, lint suppression, qualification state, or automatic repair may appear.

An unavailable CLI, missing authentication, unobserved matcher, non-firing final event, timeout at or above 10 seconds, lost simultaneous-failure reason, incomplete skill baseline, or unreviewed eval output means acceptance is not met. Record it as an open blocker; do not weaken the matrix or claim partial migration completion.

## Idempotence and Recovery

The linter and adapters are read-only and safe to rerun. Fixture tests copy from one pristine source for each case and must remove only their own exact temporary directories through existing `scripts/test-common.sh` patterns. Vendoring is repeatable only after verifying the exact archive hash; never overlay a different PyYAML version. Corpus migration is deterministic from the Gate 3 checkpoint and must not be rerun against partially converted documents without first inventorying their frontmatter.

Each gate ends in a reviewable commit, and its commit hash is recorded below. If a pre-merge gate must be undone, use a normal `git revert <gate-commit>` so the rollback is explicit and does not erase unrelated work. Do not use hard reset or broad checkout. If Gate 4 fails mid-edit, do not enable hooks or claim conformance; finish the atomic conversion in the same worktree or revert the exact Gate 4 commit after it exists.

The merged migration is one rollback unit. If it lands as one squash commit, run `git revert <migration-commit>`. If it lands as one merge commit, run `git revert -m 1 <migration-merge-commit>`. A post-merge enforcement or conformance regression reverts the entire unit: canonical metadata, authoring guidance, linter/vendor, scaffold producers, adapters, and registrations. Re-enablement requires a root cause, a regression test, the complete green matrix, and fresh live provider evidence.

Disposable worktrees must be created from the committed candidate and named explicitly in `Artifacts and Notes`. Before removal, verify the path with `git worktree list`; remove only that exact path with `git worktree remove <exact-path>`. Never point cleanup at the repository root, `$HOME`, or an unresolved variable.

## Artifacts and Notes

Record evidence here as implementation proceeds. Keep transcripts concise and link to generated benchmark artifacts instead of pasting them.

- Planning baseline commit: `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9` (recorded at Gate 1 start; worktree clean).
- Gate 1 baseline inventory: 31 canonical Markdown concepts, 22 `coverage` headers, 9 `status: verified` summaries, and no exact lowercase `index.md` or `log.md` paths.
- Gate 1 prerequisite suites: `test-hooks-auto-ingest.sh`, `test-gemini-hooks-auto-ingest.sh`, `test-hooks-startup.sh`, and `test-gemini-hooks-startup.sh` all exited 0.
- Gate 1 implementation commit: `e0d425972641f1f1a372d7dacd068f73fa7fefee`.
- Gate 1 intentional red transcript: `bash -n scripts/test-okf-lint.sh` exited 0; `bash scripts/test-okf-lint.sh` exited 1 with exactly `intentional red: missing executable scripts/lint-okf.py` on stderr.
- Gate 2 commit: `817f2881393235f8b6abb4d7a08df28570262715`. Linter fixture result: `python3 -m py_compile scripts/lint-okf.py scripts/vendor/yaml/*.py`, `bash -n scripts/test-okf-lint.sh`, and `PYTHONDONTWRITEBYTECODE=1 bash scripts/test-okf-lint.sh` all exited 0; the suite printed `PASSED: OKF linter CLI contract`.
- Gate 2 review result: six first-pass contract gaps and two follow-up gaps received public-CLI regressions and fixes; final targeted re-review found all required findings resolved and no new high-confidence regression. The live pre-migration corpus is deterministic at 104 conformance diagnostics, exit 1, with no `OKF900`.
- Gate 3 runner/model: collaboration task agents using exact model `gpt-5.6-luna` for paired `with_skill` and `without_skill` runs; no external `copilot`, `gemini`, or `claude` executable is available, and collaboration notifications do not expose token totals.
- Gate 3 grader and skill validation: `PYTHONDONTWRITEBYTECODE=1 python3 .agents/skills/okf-authoring/evals/test_grade_benchmark.py` passes 17 tests, including hash-seed determinism and score-preserving benchmark synchronization; grader/test/synchronizer compilation, vendored-PyYAML quick validation, `PYTHONDONTWRITEBYTECODE=1 bash scripts/test-okf-lint.sh`, and `git diff --check` pass.
- Gate 3 paired benchmark: the corrected 16-run result uses exact `gpt-5.6-luna` routing for both configurations and harness-owned real-linter/scoped-diff evidence. With-skill passes 72/72 expectations (100%); without-skill passes 52/72 (72.2%), with a 71.5% mean per-eval pass rate. Duration coverage is 5/16 and token coverage is 3/16, so those comparisons are omitted. Human review is generated at `skills/okf-authoring-workspace/iteration-1/review.html` with all prompts and eval IDs.
- Gate 3 resumed acceptance review: found nondeterministic eval-0 expectation ordering after the initial implementation commit. The correction sorts the grader's expected paths, adds a cross-hash-seed regression, uses a tested score-preserving synchronizer for the incomplete-telemetry aggregate, and regenerates `review.html`. Independent review confirmed all 16 grading files, the aggregate, and the reviewer are synchronized; all prompts and eval IDs are present; scores remain 72/72 versus 52/72; and no skill, harness, model-evidence, or stray-workspace blocker remains.
- Gate 3 final rollback checkpoint: `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735`.
- Gate 4 implementation checkpoint: `d21c4351`. It preserves all 31 canonical paths, changes only the nine expected manifest `summary_hash` fields, and leaves raw sources unchanged. Resumed review found one quoted/commented YAML draft-detection bypass; symmetric public-hook regressions failed before and pass after the current uncommitted scalar-normalization correction, and Premium follow-up review approved the fix. Final validation passes shell/Python syntax, both auto-ingest suites, the linter contract suite, human/JSON full-corpus lint, active migration links, legacy/lowercase searches, and `git diff --check`. The user's correction checkpoint remains pending.
- Gate 5 commit, provider versions/source recheck, and simulated parity results: not started.
- Gate 6 Copilot worktree/commands/events/diagnostics: not started.
- Gate 6 Gemini worktree/commands/events/diagnostics: not started.
- Simultaneous-failure result and coordinator decision: not started; default is no coordinator.
- Merge or squash commit forming the rollback unit: not started.

The accepted PyYAML source archive is `https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz` with SHA-256 `d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f`. The archive contains `pyyaml-6.0.3/LICENSE` and the pure-Python package under `pyyaml-6.0.3/lib/yaml/`.

## Interfaces and Dependencies

At completion, `scripts/lint-okf.py` is an executable Python 3 CLI with this public interface:

    ./scripts/lint-okf.py [--format human|json]

It has no network behavior and no runtime package installation. Its only non-standard-library dependency is the checked-in pure-Python PyYAML 6.0.3 package under `scripts/vendor/yaml/`. The default human output is sorted `path:line:column: ID message`; JSON output is `{"schema_version": 1, "diagnostics": [...]}`. Exit 0 is clean, exit 1 is a conformance/profile failure, and exit 2 is an untrustworthy/internal result containing `OKF900`.

The two adapter entry points are executable Python scripts that accept one provider JSON object on stdin and emit exactly one provider JSON object on stdout:

    .github/hooks/scripts/lint-okf.py
    .gemini/hooks/scripts/lint-okf.py

They invoke the central CLI with the payload repository as the working directory and do not expose a single-file or changed-file validation mode. Their only policy is envelope translation, diagnostic truncation, and failure-to-`OKF900` conversion.

`.agents/skills/okf-authoring/SKILL.md` is model-invoked and progressively loads:

    .agents/skills/okf-authoring/references/profile.md
    .agents/skills/okf-authoring/references/source-summaries.md

Its completion report names affected canonical paths and derived types, loaded branch references, routing/index implications, the exact full-corpus lint command/result, and the scoped-diff result. It cannot report completion when lint is unavailable.

The linter diagnostic namespace is fixed by the closed contract: `OKF001` unreadable/non-UTF-8 concept, `OKF002` missing/malformed delimiters, `OKF003` invalid YAML/non-mapping frontmatter, `OKF004` missing/empty/wrong required field, `OKF005` invalid standard metadata shape/value, `OKF006` invalid timestamp or missing offset, `OKF007` lowercase reserved path, `OKF101` path/type mismatch, `OKF102` repository escape, `OKF103` unresolved/non-file local target, `OKF104` manifest/source-summary mismatch, `OKF105` legacy field/lifecycle representation, and `OKF900` parser/dependency/configuration/internal failure.

Revision note (2026-09-09): Completed Gate 1 implementation work from baseline `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9`; added the valid two-bundle fixture and intentional-red public-CLI suite, recorded delegated review corrections and validation evidence, and left the reviewed worktree uncommitted for the user's manual checkpoint.

Revision note (2026-09-09): Recorded the user's Gate 1 commit, completed Gate 2's pinned vendor and provider-neutral linter, expanded regressions from independent review, synchronized script-area agent documentation, and stopped before Gate 3 for the user's manual Gate 2 checkpoint.

Revision note (2026-09-09): Recorded the user's Gate 2 checkpoint `817f2881393235f8b6abb4d7a08df28570262715` and opened Gate 3 implementation.

Revision note (2026-09-09): Hardened Gate 3's public benchmark seam after independent review and moved the active step to paired `gpt-5.6-luna` live runs.

Revision note (2026-09-09): Corrected Gate 3's skill location to the repository-local `.agents/skills/okf-authoring/` path after user review; discarded contaminated live runs and restarted the benchmark from the corrected source.

Revision note (2026-09-09): Replaced the false-pass grader seam with fixture-backed real lint/diff evidence, completed the corrected paired benchmark, repaired executor-model and reviewer metadata found by fresh rereview, omitted incomplete telemetry comparisons, and moved Gate 3 to user review.

Revision note (2026-09-09): Recorded Gate 3 implementation commit `6f7d2be1e040415d91026d828d4e70f59c110269`, corrected nondeterministic grader expectation ordering found during resumed acceptance, synchronized generated review artifacts, and kept Gate 4 closed pending the user's manual correction checkpoint.

Revision note (2026-09-09): Recorded the user-created final Gate 3 checkpoint `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735`, marked Milestone 3 accepted, and opened Gate 4's atomic corpus and scaffold cutover.

Revision note (2026-09-09): Completed and validated Gate 4's atomic corpus/scaffold migration, added special source-path regressions, repaired stale canonical teaching text and index links found by review, and stopped before Gate 5 for the user's manual checkpoint.

Revision note (2026-09-10): Recorded Gate 4 implementation checkpoint `d21c4351`, reproduced a resumed-review finding where quoted/commented YAML draft metadata bypassed pending ingest, added symmetric public-hook regressions, and implemented the standard-library scalar-normalization correction without opening Gate 5.
