# Migrate the canonical agent knowledge base to OKF v0.2 in place

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this document in accordance with the repository's `exec-plans` skill.

Implementation is complete through Gate 6. Gates 1–5 are committed; the Gate 5 rollback checkpoint is `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd`. On 2026-09-16, the user removed the human-started Copilot and Gemini proof sessions from acceptance. Gate 6 now relies on the complete static and simulated final matrix, including both provider envelopes and the corrected Copilot simultaneous-failure seam.

## Purpose / Big Picture

After this change, every canonical agent-facing document under `.agents/instructions/` and `.agents/memory/` will itself be an Open Knowledge Format (OKF) v0.2 concept. Agents will continue to discover those documents through the existing `AGENTS.md` to `.agents/memory/INDEX.md` route; there will be no generated sidecar, prompt-time selector, or second knowledge-loading path. Authors will have a repository skill that teaches the profile, and a single deterministic linter will provide the same findings to humans, GitHub Copilot CLI, and Gemini CLI. A user can see the result by running `./scripts/lint-okf.py`, observing a clean full-corpus scan, and running the provider contract suites to verify both hook envelopes derive from the same normalized diagnostics.

The implementation is one migration unit. It may be built as reviewable commits, but it may merge only after all six gates below pass. The user explicitly removed live Copilot and Gemini capability probes from Gate 6 acceptance; static and simulated provider tests are the release evidence.

## Progress

- [x] (2026-09-09 06:31Z) [milestone-1] Recorded clean baseline commit `b9a1d8a8a0542bec9eb6764cf4b4af3071eefad9`; confirmed 31 concepts, 22 `coverage` headers, 9 verified summaries, and no lowercase reserved paths.
- [x] (2026-09-09 06:31Z) [milestone-1] Confirmed both source-ingest suites and both startup suites exit 0 before fixture changes.
- [x] (2026-09-09 06:47Z) [milestone-1] Added the single valid two-bundle fixture and public-CLI contract suite; confirmed its intentional red is only the absent production linter.
- [x] (2026-09-09 07:04Z) [milestone-1] Recorded the user-created Gate 1 reviewable checkpoint `e0d425972641f1f1a372d7dacd068f73fa7fefee`.
- [x] (2026-09-09 07:29Z) [milestone-2] Vendored and verified PyYAML 6.0.3, implemented the dormant provider-neutral linter, made the expanded public-CLI suite green, and completed independent review without enabling hooks.
- [x] (2026-09-09 13:25Z) [milestone-3] Recorded the user-created final Gate 3 rollback checkpoint `4f64fb8d9156d58d8ecc323ecdf0af16b6aa4735` after the deterministic grader correction and independent approval.
- [x] (2026-09-10 00:00Z) [milestone-4] Recorded final Gate 4 rollback checkpoint `917313a04bb513039ea0a2e596a8c381370766e7` after the quoted/commented YAML scalar correction, Premium follow-up approval, and complete green Gate 4 matrix.
- [x] (2026-09-10 14:03Z) [milestone-5] Rechecked the official Copilot and Gemini hook contracts and the open Gemini `AfterAgent` issue; found no Gate 5 contract change and confirmed neither target CLI is installed.
- [x] (2026-09-10 14:41Z) [milestone-5] Added the two checkout-anchored provider adapters and candidate repo-local registrations, made the complete simulated parity/regression matrix green, and received Premium follow-up approval with no remaining required findings.
- [x] (2026-09-10 15:43Z) [milestone-5] Recorded the user-created Gate 5 rollback checkpoint `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd`; verified it is current `HEAD` and the worktree is clean.
- [x] (2026-09-10 15:43Z) [milestone-6] Ran the Gate 6 environment preflight and confirmed neither `copilot` nor `gemini` is installed.
- [x] (2026-09-10 16:21Z) [milestone-6] Rewrote Gate 6 for sequential human-started Copilot, Gemini, and coordinator sessions; delegated review approved the final runbook with no required findings.
- [x] (2026-09-14 13:26Z) [milestone-6] Verified the Gate 6 runbook commit `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd` and attempted the live Copilot probe in the detached worktree. The attempt was blocked by missing PowerShell-capable Copilot tooling, repo install target permissions, and Tool Guardian denial of destructive cleanup; its human-created evidence commit is `2ee361180c599f7420873d446f7d4e4f05fdf8a0`.
- [x] (2026-09-14) [milestone-6] Re-ran the Copilot Gate 6 session from detached worktree `/tmp/okf-gate6-copilot.YVPdw2/worktree` after confirming `pwsh` 7.6.5 is installed. Bash and edit produced direct `postToolUse` `OKF002` evidence; final full-corpus lint passed in `0.039904s` and the worktree was restored and safely removed. Status: failed because the simultaneous-failure probe lost the source-ingest reason and required ordering; additional blockers were missing provider `powershell`, unobserved `create`, and absent direct `agentStop` and custom-agent `subagentStop` envelopes. Human-created evidence commit: `bb4743f71a7409842347870aa883df4c9ef2ea8a`.
- [x] (2026-09-15) [milestone-6] Recorded the user's decision to defer human-started Copilot and Gemini verification for now. This changes scheduling only: Gate 6 acceptance remains unmet, and no live evidence requirement is waived or treated as passed.
- [x] (2026-09-16 04:30Z) [milestone-6] Recorded the user's decision to skip and no longer require human Copilot and Gemini proof sessions. Historical Copilot evidence remains a failed live record and is not represented as passing evidence; no Gemini evidence file is required.
- [x] (2026-09-16 04:30Z) [milestone-6] Ran the complete static and simulated final matrix. Its first benchmark grading pass exposed that a later `update-agent-docs` refactor had dropped the mandatory one-way `okf-authoring` invocation and reduced both eval-4 scores. Restored that existing contract, reran skill validation and all 16 benchmark grades without artifact drift, and confirmed every final-matrix command exits 0.
- [x] (2026-09-16 04:30Z) [milestone-6] Synchronized the ExecPlan and handoff for final human review and merge readiness.

## Surprises & Discoveries

- Observation: The authoritative OKF source is unchanged from the design handoff.
  Evidence: On 2026-09-09 UTC, `git ls-remote https://github.com/GoogleCloudPlatform/open-knowledge-format.git refs/heads/main` returned `ad30107c31c06aec8a7d5636e0d1058118604e6f`, and the fetched `SPEC.md` SHA-256 remained `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`.
- Observation: The current corpus is a small atomic migration but has two distinct legacy frontmatter shapes.
  Evidence: The baseline contains 31 canonical Markdown files: 6 instruction concepts, 16 non-summary memory concepts, and 9 source summaries. Twenty-two files use `coverage`; nine summaries use `status: verified`; exact lowercase `index.md` and `log.md` do not exist.
- Observation: Provider documentation still does not expose an authoritative changed-file list after a tool call.
  Evidence: Current Copilot `postToolUse` and Gemini `AfterTool` payloads expose the tool name, arguments, result, and working directory, but not a diff or changed-files field. The authoritative final behavior therefore remains a full two-bundle scan.
- Observation: Copilot's current contract supports the chosen events but explicitly bounds enforcement.
  Evidence: GitHub documents ordered execution for same-type hooks, full-match tool-name regexes, `postToolUse` additional context, stop-hook blocking, fail-open timeouts, and a host override after eight consecutive stop blocks.
- Observation: The first complete Copilot simultaneous-failure probe did not preserve both independently blocking reasons.
  Evidence: Evidence commit `bb4743f71a7409842347870aa883df4c9ef2ea8a` records only the OKF `OKF002` continuation message; the source-ingest reason did not appear first or remain visible. Under this plan's acceptance rule, that executed result is `failed`, not an environment-only blocker.
- Observation: The registered-hook public seam reproduces the live lost-reason behavior when it observes the final response from the two ordered Copilot stop registrations.
  Evidence: Before the correction, `rtk test bash scripts/test-hooks-okf-lint.sh` failed because the observed response contained only `OKF validation failed` and `OKF101`. After registering one coordinator, the same test passes and requires both reasons in source-ingest-first order.
- Observation: Gemini documents `AfterTool` and `AfterAgent`, but the final event remains a live release risk.
  Evidence: Gemini's current hook reference documents structured deny/retry behavior and `stop_hook_active`; official issue `google-gemini/gemini-cli#27712` is still open and reports `AfterAgent` not firing in version 0.45.0 and related versions.
- Observation: The final benchmark command can exit 0 while changing accepted scores.
  Evidence: The first 2026-09-16 final run rewrote both eval-4 `grading.json` files because `update-agent-docs` no longer contained its required one-way `okf-authoring` invocation. Restoring the contract returned the accepted scores and eliminated generated-artifact drift.
- Observation: This planning environment cannot run provider capability probes.
  Evidence: Python is 3.12.3, while both `copilot --version` and `gemini --version` return command-not-found. The original Gate 6 plan therefore required separate authenticated sessions; the user later removed those sessions from acceptance.
- Observation: The Gate 5 provider-source recheck found no change to the accepted adapter contract.
  Evidence: On 2026-09-10, GitHub still documented full-match `postToolUse` matchers, `additionalContext`, stop `allow`/`block` responses, and fail-open timeouts; Gemini main commit `ed2ac40df67a319bf348bd7e3d10494696b31b38` still documented regex tool matchers, exact lifecycle matchers, millisecond timeouts, `AfterTool` deny responses, and bounded `AfterAgent` retry/stop responses. Gemini issue `google-gemini/gemini-cli#27712` remained open; this risk is covered by static contract tests after the user removed live proof from acceptance.
- Observation: Payload working directories and raw diagnostic text are security boundaries, not only routing data.
  Evidence: Premium Gate 5 review found that payload `cwd` could select an external `scripts/lint-okf.py`, that native Copilot camelCase payloads omit an event-name discriminator, and that Gemini's raw-text byte count could exceed 8 KiB after JSON escaping. Public regressions now prove checkout-anchored execution, nested-path acceptance, external decoy rejection, realistic Copilot envelopes, and exact serialized Gemini bounds.
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
- Decision: Execute Gate 6 in two sequential, human-started provider sessions with one durable evidence file per provider, followed by a coordinator session.
  Rationale: Copilot and Gemini capabilities are available only inside their respective authenticated environments. Provider-owned evidence files prevent one session from claiming the other provider's result, and sequential human commits give every later session a stable base without shared-file edit collisions.
  Date/Author: 2026-09-10 / Codex
- Decision: Classify the committed Copilot simultaneous-failure result as failed and require the plan's test-first corrective path before another full provider run.
  Rationale: The probe executed and lost the source-ingest reason. Milestone 6 explicitly requires a failed status plus a regression before considering a thin provider-local coordinator; asking only for a different environment would skip the accepted correction sequence.
  Date/Author: 2026-09-14 / Codex
- Decision: Defer all remaining human-started Copilot and Gemini verification until the user explicitly reopens Gate 6.
  Rationale: The user chose to skip provider-native verification for now. Deferral preserves completed implementation and partial evidence without weakening the established acceptance contract or misrepresenting unverified behavior as passed.
  Date/Author: 2026-09-15 / user
- Decision: Replace Copilot's two stop-event registrations with one provider-local coordinator while keeping the source-ingest and OKF validators as separate executables.
  Rationale: The live probe and public regression both show that the later host response can hide the earlier source-ingest reason. One response composed in source-ingest-first order preserves both failures without merging validator logic.
  Date/Author: 2026-09-16 / Codex
- Decision: Remove human-started Copilot and Gemini proof sessions from Gate 6 acceptance and use the complete static and simulated matrix as final evidence.
  Rationale: The user explicitly chose to skip and no longer require those sessions. Historical failed Copilot evidence remains accurate, while absence of Gemini live evidence no longer blocks merge readiness.
  Date/Author: 2026-09-16 / user
- Decision: Restore the one-way `update-agent-docs` to `okf-authoring` workflow step removed by a later refactor.
  Rationale: The closed Gate 3 contract and accepted eval require semantic documentation work to invoke the separate representation pass. Final grading reproduced the regression in both configurations; the focused instruction restored accepted scores without changing the benchmark.
  Date/Author: 2026-09-16 / Codex

## Outcomes & Retrospective

Gates 1–5 are committed, with Gate 5 checkpoint `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd`. Gate 5 added reviewed repo-local Copilot and Gemini OKF adapters, mutation-tool feedback, provider parity/error/truncation coverage, and checkout containment. Gate 6's static Copilot correction replaces the failed two-registration stop path with one tested coordinator that preserves both independent reasons. The user removed provider-native proof from acceptance, and the complete static and simulated final matrix passes. Gate 6 is accepted and ready for human review and merge.

## Context and Orientation

`AGENTS.md` is the mandatory repository entry point. It tells agents to read `.agents/memory/INDEX.md`, which routes them to the canonical documents under `.agents/instructions/` and `.agents/memory/`. An OKF bundle is a directory tree of UTF-8 Markdown concept documents with YAML frontmatter. In this migration, those two canonical roots are separate bundles, and every `.md` file below either root is a concept. A concept's identity is its bundle-relative path without `.md`, so files must not move or change case.

The current 31 concepts have useful bodies that must remain intact. The 22 ordinary canonical documents begin with a `coverage` field. The 9 completed source summaries begin with `status: verified` and are bound to immutable raw inputs by `.agents/memory/sources/source-ingest-manifest.json`. Gate 4 changes only the representation needed by the contract: ordinary files replace `coverage` with `type` and `description`; completed summaries replace the legacy status with `type`, `description`, and one `sources` entry. Body rewriting is out of scope except where a body currently teaches the obsolete frontmatter format, notably `.agents/memory/INDEX.md` and `.agents/skills/update-agent-docs/refs/indexes-frontmatter.md`.

`scripts/lint-okf.py` is the complete validation authority. The future repo-local adapters `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` will read their provider payload, locate the repository from `cwd`, execute the central linter in JSON mode, cap the shared diagnostic text, and emit only the provider-specific JSON envelope. They must not contain document-profile rules.

Source ingestion remains independent. `.github/hooks/scripts/helpers/auto_ingest.py` and `.gemini/hooks/scripts/helpers/source_ingest.py` are intentionally duplicated scaffold producers. Both emit a conforming `Source Summary` with `status: draft` and a file-relative raw-source resource, and both detect unresolved summaries from normalized top-level `type` and `status` scalar values rather than literal YAML lines. The manifest continues to own freshness, hashes, rename/orphan state, and source-to-summary binding. The OKF linter reads that manifest but never updates it.

The authoring workflow has two repository-local homes. `.agents/skills/okf-authoring/` owns the model-invoked representation workflow. `.agents/skills/update-agent-docs/` owns the semantic documentation workflow. Gate 3 adds a one-way instruction from `update-agent-docs` to invoke `okf-authoring` after semantic edits; `okf-authoring` must never call back into `update-agent-docs`.

The normative external sources for implementation are the pinned [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md), the current [GitHub Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference), the current [Gemini hooks reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md), Gemini's [hook writing guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/writing-hooks.md), and the open [Gemini AfterAgent issue](https://github.com/google-gemini/gemini-cli/issues/27712). Recheck them at Gate 5 and record any contract-changing difference in this plan before editing provider code.

## Ownership and Coordination

Use parallel agents only inside one gate and only with the following non-overlapping ownership. Gates 1–5 used the original coordinator ownership below. Gate 6 originally used sequential provider sessions; those rows now document historical ownership if optional provider investigation is explicitly requested. The user owns every commit.

| Workstream | Exclusive paths while active | Transfer point |
| --- | --- | --- |
| Linter and fixture owner | `scripts/lint-okf.py`, `scripts/test-okf-lint.sh`, `scripts/fixtures/okf-valid-repo/**`, `scripts/vendor/**` | Returns ownership after Gate 2 |
| Authoring skill owner | `.agents/skills/okf-authoring/**`, `skills/okf-authoring-workspace/**`, `.agents/skills/update-agent-docs/**` | Returns ownership after Gate 3 |
| Corpus and scaffold owner | `.agents/instructions/**`, `.agents/memory/**`, `.github/hooks/scripts/helpers/auto_ingest.py`, `.gemini/hooks/scripts/helpers/source_ingest.py`, `scripts/test-hooks-auto-ingest.sh`, `scripts/test-gemini-hooks-auto-ingest.sh` | Returns canonical documentation ownership to the coordinator after Gate 4 |
| Provider adapter owner | `.github/hooks/scripts/lint-okf.py`, `.gemini/hooks/scripts/lint-okf.py`, `scripts/test-hooks-okf-lint.sh`, `scripts/test-gemini-hooks-okf-lint.sh` | Returns ownership after Gate 5 |
| Gate 6 Copilot owner | `docs/okf-kb-migration/gate6-copilot-evidence.md`, Copilot Gate 6 lines in this ExecPlan and handoff; when live evidence requires a correction, `.github/hooks/**`, its targeted tests, and required agent docs | Returns ownership after the human commits the session result |
| Gate 6 Gemini owner | `docs/okf-kb-migration/gate6-gemini-evidence.md`, Gemini Gate 6 lines in this ExecPlan and handoff; when live evidence requires a correction, `.gemini/**`, its targeted tests, and required agent docs | Returns ownership after the human commits the session result |
| Coordinating owner | Shared configuration, final integration, final validation, and shared plan/handoff acceptance state | Retains coordination; the user creates every commit |

Gates run sequentially. Within Gates 1–5, agents may work in parallel only when their paths do not overlap. The coordinator integrates and runs final gate checks; the user creates the commits. If optional Gate 6 provider investigation is later requested, its sessions remain sequential with ownership transferred only after human review and commit. No agent enables a hook or migrates part of the canonical corpus early.

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

Status: done
Acceptance: met

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

Status: done
Acceptance: met

Recheck the official provider sources named in `Context and Orientation` and record the installed target CLI versions. If an event, matcher, envelope, exit, timeout, or retry contract changed, stop, document the contradiction in `Surprises & Discoveries` and `Decision Log`, and revise this ExecPlan before editing adapters.

Create `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` as separate thin executable adapters. Reuse only the provider-local common input/output and path-normalization helpers. Each adapter reads one complete JSON payload, finds the repository from `cwd`, runs `sys.executable <repo>/scripts/lint-okf.py --format json` with an 8-second subprocess timeout inside the host's 10-second limit, validates `schema_version` and diagnostic fields, and formats at most the first 20 sorted findings into less than 8 KiB including the omitted count and rerun command. POSIX rerun text is `./scripts/lint-okf.py`; Windows rerun text is `python scripts/lint-okf.py`. Malformed input, missing linter/vendor, subprocess timeout, invalid linter JSON, exit 2, and unexpected exceptions become a synthetic `OKF900` blocking response. Stdout is exactly one provider-valid JSON object and expected control flow exits 0.

The Copilot adapter returns `{}` on clean `postToolUse`, `additionalContext` on invalid `postToolUse`, `decision: allow` on a clean stop, and `decision: block` plus `reason` on an invalid `agentStop` or `subagentStop`. The Gemini adapter returns `{}` on clean events, `decision: deny` plus `reason` on invalid `AfterTool`, `decision: deny` on the first invalid `AfterAgent`, and `continue: false` plus `stopReason` when an invalid `AfterAgent` arrives with `stop_hook_active` true.

Create `scripts/test-hooks-okf-lint.sh` and `scripts/test-gemini-hooks-okf-lint.sh` before adapter implementation. At the adapter stdin/stdout seam, cover clean and invalid corpora, diagnostic parity with central JSON, malformed payloads, missing dependencies, `OKF900`, 20-item/8-KiB truncation, every event envelope, Gemini retry state, Copilot subagent stops, and simultaneous pending-ingest plus OKF failures. Keep source-ingest helpers real in integration cases instead of mocking internal functions.

Update `.github/hooks/hooks.json` only after static adapter tests are green. Keep the existing source-ingest command first in `agentStop` and `subagentStop`, then add the OKF command with `bash: ".github/hooks/scripts/lint-okf.py"`, `powershell: "python \".github/hooks/scripts/lint-okf.py\""`, and `timeoutSec: 10`. Add `postToolUse` with the candidate full-match matcher `bash|powershell|create|edit` and the same OKF command fields. Update `.gemini/settings.json` so `AfterAgent` uses one `sequential: true`, match-all group containing the existing source-ingest command first and an independently named `lint-okf` command second, with `command: "python .gemini/hooks/scripts/lint-okf.py"` and `timeout: 10000`. Add `AfterTool` with matcher `write_file|replace|run_shell_command` and the same OKF command. Set only OKF hook timeouts to 10 seconds.

Run adapter parity tests, both existing source-ingest suites, both startup suites, `python3 scripts/test_helpers.py`, and `bash scripts/test-install.sh`. Verify executable mode 755 for all new Python entry points. Do not add repository-specific OKF registrations to `.copilot/hooks/hooks.json` or `.gemini/global-settings.json`.

Milestone acceptance is green static/simulated behavior with candidate repo-local registrations and identical normalized diagnostics. Gate 6 adds the complete integration matrix and final acceptance record.

### Milestone 6: Finish verification and the migration

Status: done
Acceptance: met
Scheduling: Human-started provider proof sessions skipped and no longer required by user

On 2026-09-16, the user explicitly removed the human-started Copilot and Gemini proof sessions from Gate 6 acceptance. The failed Copilot evidence remains an accurate historical record and is not upgraded to passed. No Gemini evidence file is required. Gate 6 acceptance now requires the complete static and simulated final matrix, active migration-link validation, canonical structure checks, and synchronized planning records.

The provider-session runbook below is retained only as historical, optional diagnostic guidance. It is not an acceptance requirement and must not be scheduled unless the user explicitly requests fresh provider-native investigation.

Before any provider session starts, the human reviews and commits this runbook update, then gives the full commit hash to the Copilot session. That session verifies the commit and records it under `Artifacts and Notes`. Gate 6 then uses three sessions in order: Copilot owner, Gemini owner, then coordinator. A human starts each session inside the named provider environment and supplies the current checkout. Run the provider sessions one at a time. After each provider agent finishes, the human reviews and commits that session's evidence before starting the next session. Agents must leave changes uncommitted because the user creates commits manually. Each later session starts from the latest human-created commit and verifies that `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd` is an ancestor. This preserves the Gate 5 rollback baseline while including reviewed Gate 6 corrections and evidence commits.

Every provider session begins by reading `AGENTS.md`, `.agents/memory/INDEX.md`, this ExecPlan, and `docs/okf-kb-migration/handoff.md`. It verifies a clean main worktree, records the latest human-created implementation commit with `git rev-parse HEAD`, and runs `git merge-base --is-ancestor d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd HEAD`; exit 0 is required. After the Copilot simultaneous-failure correction, the recorded implementation commit must contain `.github/hooks/scripts/validate-stop.py`; probing the original Gate 5 checkpoint would omit the correction and is invalid. The session then records the provider's version and full help relevant to non-interactive prompts, tool permissions, output/debug capture, and custom agents. Help output is runtime authority for command spelling. If a command template below disagrees with the installed CLI, the session records the difference and uses the syntax shown by that CLI. Missing authentication or a missing required platform is a blocker, not permission to narrow acceptance.

On POSIX, run `./scripts/install.sh` from the main checkout before provider installation checks; do not repurpose `HOME`. If the provider environment cannot write the user's install targets, the human must run the installer from a writable user shell and record that fact. Create a provider-specific detached worktree from the latest human-created implementation commit after verifying Gate 5 as its ancestor, so deliberate invalid files cannot contaminate the main checkout and every reviewed correction is present. Use the following pattern, substituting only the provider name:

    gate6_provider=copilot
    gate6_main_root="$(git rev-parse --show-toplevel)"
    cd "$gate6_main_root"
    git status --short
    gate6_probe_commit="$(git rev-parse HEAD)"
    git merge-base --is-ancestor d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd "$gate6_probe_commit"
    ./scripts/install.sh
    gate6_probe_parent="$(mktemp -d "${TMPDIR:-/tmp}/okf-gate6-${gate6_provider}.XXXXXX")"
    gate6_probe_worktree="$gate6_probe_parent/worktree"
    git worktree add --detach "$gate6_probe_worktree" "$gate6_probe_commit"
    cd "$gate6_probe_worktree"

After the POSIX installer, a Copilot session runs `cmp "$gate6_main_root/.copilot/hooks/hooks.json" "$HOME/.copilot/hooks/hooks.json"` and `test -f "$gate6_main_root/.github/hooks/hooks.json"`; both must exit 0. A Gemini session runs `cmp "$gate6_main_root/.gemini/global-settings.json" "$HOME/.gemini/settings.json"` and `cmp "$gate6_main_root/.gemini/hooks/scripts/lint-okf.py" "$HOME/.gemini/hooks/scripts/lint-okf.py"`; both must exit 0. These checks prove the provider's installed global configuration matches the checkout and, for Copilot, that the required OKF registration remains repository-local.

On Windows, open PowerShell in the current repository checkout and use these commands. `scripts/install.ps1` is the Windows installer; do not substitute the POSIX installer.

    $gate6MainRoot = (git rev-parse --show-toplevel).Trim()
    Set-Location $gate6MainRoot
    git status --short
    $gate6ProbeCommit = (git rev-parse HEAD).Trim()
    git merge-base --is-ancestor d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd $gate6ProbeCommit
    if ($LASTEXITCODE -ne 0) { throw "probe commit does not descend from Gate 5" }
    pwsh -NoProfile -File scripts/install.ps1
    $gate6ProbeParent = Join-Path ([System.IO.Path]::GetTempPath()) ("okf-gate6-copilot-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $gate6ProbeParent | Out-Null
    $gate6ProbeWorktree = Join-Path $gate6ProbeParent "worktree"
    git worktree add --detach $gate6ProbeWorktree $gate6ProbeCommit
    Set-Location $gate6ProbeWorktree
    git rev-parse HEAD

After the Windows installer, a Copilot session runs the following checks before entering the disposable worktree. They must print `copilot global hooks: matched` and `copilot repository hooks: present`:

    Set-Location $gate6MainRoot
    if ((Get-FileHash ".copilot/hooks/hooks.json").Hash -ne (Get-FileHash (Join-Path $HOME ".copilot/hooks/hooks.json")).Hash) { throw "installed Copilot hooks differ" }
    "copilot global hooks: matched"
    if (-not (Test-Path ".github/hooks/hooks.json" -PathType Leaf)) { throw "missing repository Copilot hooks" }
    "copilot repository hooks: present"
    Set-Location $gate6ProbeWorktree

For a Windows Gemini session, run these exact commands from `$gate6MainRoot`; they must print both `matched` lines:

    Set-Location $gate6MainRoot
    if ((Get-FileHash ".gemini/global-settings.json").Hash -ne (Get-FileHash (Join-Path $HOME ".gemini/settings.json")).Hash) { throw "installed Gemini settings differ" }
    "gemini settings: matched"
    if ((Get-FileHash ".gemini/hooks/scripts/lint-okf.py").Hash -ne (Get-FileHash (Join-Path $HOME ".gemini/hooks/scripts/lint-okf.py")).Hash) { throw "installed Gemini OKF hook differs" }
    "gemini OKF hook: matched"
    Set-Location $gate6ProbeWorktree

The earlier `git rev-parse HEAD` must print the human-created correction commit, and the ancestry check must prove that Gate 5 is its ancestor. Record the correction commit and both resolved paths. Never point a probe at the main checkout.

The Copilot owner creates `docs/okf-kb-migration/gate6-copilot-evidence.md` in the main checkout. The file must identify the provider, contain `Status: not started|passed|failed|blocked`, and record the UTC date, executor environment and operating system, session base commit, exact probe checkpoint, CLI version, authentication result without secrets, relevant help excerpts, provider installation/configuration checks, disposable worktree path, and every exact command and prompt used. It records one result for each `postToolUse` matcher `bash`, `powershell`, `create`, and `edit`; one result each for `agentStop` and `subagentStop`; the simultaneous pending-ingest plus invalid-OKF case; measured full-corpus lint duration; final lint output; and cleanup result. Each result names the observed event, expected and observed diagnostic IDs, whether the agent received actionable feedback, the command exit status, and a short redacted transcript excerpt or durable transcript reference. Use a repository-local custom agent that actually emits `subagentStop`; the built-in `general-purpose` agent is invalid evidence. Run the `powershell` matcher on a supported Windows target. A missing Windows observation leaves Copilot status `blocked`.

Use the exact invalid content `# Gate 6 invalid probe` followed by one newline. At a new `.agents/memory/*.md` path this must produce `OKF002` for missing frontmatter delimiters. The repaired content is the following, with only the title's tool name changed:

    ---
    type: Agent Memory
    description: Temporary Gate 6 provider hook probe
    ---

    # Gate 6 <tool> probe

On POSIX, pre-seed the Copilot `edit` and `agentStop` inputs with this exact command from the disposable worktree:

    python3 - <<'PY'
    from pathlib import Path

    valid = "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 edit probe\n"
    Path(".agents/memory/gate6-copilot-edit.md").write_text(valid, encoding="utf-8")
    Path(".agents/memory/gate6-copilot-agent-stop.md").write_text("# Gate 6 invalid probe\n", encoding="utf-8")
    PY

On Windows, pre-seed the same two files with:

    $gate6Utf8 = [System.Text.UTF8Encoding]::new($false)
    $gate6Valid = "---`ntype: Agent Memory`ndescription: Temporary Gate 6 provider hook probe`n---`n`n# Gate 6 edit probe`n"
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/memory/gate6-copilot-edit.md"), $gate6Valid, $gate6Utf8)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/memory/gate6-copilot-agent-stop.md"), "# Gate 6 invalid probe`n", $gate6Utf8)

Use these literal Copilot prompts, changing no filenames or requested tool names:

    bash: Use only the bash tool to create .agents/memory/gate6-copilot-bash.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only bash to replace it with exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 bash probe\n" and report the hook event and diagnostic exactly.

    powershell: Use only the powershell tool to create .agents/memory/gate6-copilot-powershell.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only powershell to replace it with exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 powershell probe\n" and report the hook event and diagnostic exactly.

    create: Use only the create tool to create .agents/memory/gate6-copilot-create.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, stop using tools and report the hook event and diagnostic exactly.

Before the `edit` run, seed `.agents/memory/gate6-copilot-edit.md` with the conforming content. Then use this prompt:

    edit: Use only the edit tool to replace all content in .agents/memory/gate6-copilot-edit.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only edit to restore exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 edit probe\n" and report the hook event and diagnostic exactly.

After the `create` command completes, the outer human-started session replaces its invalid file with the exact conforming create-probe content shown in the preceding prompt, using the same UTF-8 Python or PowerShell write pattern as the seed commands. After every Copilot mutation command, the outer session runs `./scripts/lint-okf.py` on POSIX or `python scripts/lint-okf.py` on Windows and records exit 0. The provider prompt does not ask a non-shell mutation tool to execute that command.

Before `agentStop`, seed `.agents/memory/gate6-copilot-agent-stop.md` with the invalid content and invoke Copilot with edit permission using the literal prompt `Do not call a tool. Reply exactly: probe complete.` Evidence must show `agentStop` returned `decision: block` with `OKF002`, forced a continuation, and gave the agent enough information to repair that exact path.

For `subagentStop`, create `.github/agents/gate6-okf-probe.agent.md` in the disposable worktree with this exact definition. If installed help requires another repository-local custom-agent directory or extension, preserve the frontmatter and body byte-for-byte at that supported path and record the difference.

    ---
    name: gate6-okf-probe
    description: Creates one invalid OKF concept to exercise subagentStop
    ---

    Use the create tool to write .agents/memory/gate6-copilot-subagent-stop.md with the exact UTF-8 content "# Gate 6 invalid probe\n", then try to finish. If the stop hook reports OKF002, use the edit tool to replace it with exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 subagentStop probe\n" before finishing again. Report the hook event and diagnostic exactly.

Use the parent prompt `Delegate the Gate 6 probe to the gate6-okf-probe custom agent and wait for its result.` Evidence must show the custom agent, rather than `general-purpose`, emitted `subagentStop`, received `decision: block` with `OKF002`, repaired the file, and then completed. Use minimally scoped permissions. The starting command shape is:

    copilot --version
    copilot --help
    copilot -p '<literal probe prompt>' -s --allow-tool='<minimal tools from installed help>' --output-format json --share '<durable transcript path>'

The Gemini owner creates `docs/okf-kb-migration/gate6-gemini-evidence.md` in the main checkout with the same header and environment fields. It records one result for each `AfterTool` matcher `write_file`, `replace`, and `run_shell_command`; the two-step `AfterAgent` result; the simultaneous pending-ingest plus invalid-OKF case; measured full-corpus lint duration; final lint output; and cleanup result. Each result names the observed event, expected and observed diagnostic IDs, whether the agent received actionable feedback, the command exit status, and a short redacted debug excerpt or durable output reference.

Use the same exact invalid and repaired content for Gemini. Before running Gemini, pre-seed the `replace` and `AfterAgent` inputs. On POSIX use:

    python3 - <<'PY'
    from pathlib import Path

    valid = "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 replace probe\n"
    Path(".agents/memory/gate6-gemini-replace.md").write_text(valid, encoding="utf-8")
    Path(".agents/memory/gate6-gemini-after-agent.md").write_text("# Gate 6 invalid probe\n", encoding="utf-8")
    PY

On Windows use:

    $gate6Utf8 = [System.Text.UTF8Encoding]::new($false)
    $gate6Valid = "---`ntype: Agent Memory`ndescription: Temporary Gate 6 provider hook probe`n---`n`n# Gate 6 replace probe`n"
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/memory/gate6-gemini-replace.md"), $gate6Valid, $gate6Utf8)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/memory/gate6-gemini-after-agent.md"), "# Gate 6 invalid probe`n", $gate6Utf8)

Use these literal prompts, changing no filenames or requested tool names:

    write_file: Use only write_file to create .agents/memory/gate6-gemini-write-file.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only write_file to replace it with exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 write_file probe\n" and report the hook event and diagnostic exactly.

Before the `replace` run, seed `.agents/memory/gate6-gemini-replace.md` with the conforming content. Then use this prompt:

    replace: Use only replace to replace all content in .agents/memory/gate6-gemini-replace.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only replace to restore exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 replace probe\n" and report the hook event and diagnostic exactly.

    run_shell_command: Use only run_shell_command to create .agents/memory/gate6-gemini-shell.md with the exact UTF-8 content "# Gate 6 invalid probe\n". After the hook reports OKF002 for that path, use only run_shell_command to replace it with exactly "---\ntype: Agent Memory\ndescription: Temporary Gate 6 provider hook probe\n---\n\n# Gate 6 run_shell_command probe\n" and report the hook event and diagnostic exactly.

After each Gemini mutation command completes, the outer human-started session runs `./scripts/lint-okf.py` on POSIX or `python scripts/lint-okf.py` on Windows and records exit 0. The provider prompt does not ask a non-shell mutation tool to execute that command.

Before `AfterAgent`, seed `.agents/memory/gate6-gemini-after-agent.md` with the invalid content and invoke Gemini with the literal prompt `Do not call a tool. Reply exactly: probe complete. If a hook forces a correction turn, do not call a tool and reply exactly: probe complete.` Evidence must show the first `AfterAgent` denies completion with `OKF002` and causes one correction turn, then show the repeated event has `stop_hook_active: true` and returns `continue: false` with the same diagnostic instead of looping. Because issue 27712 remains open, configured settings or documentation are not evidence that the event fired. The starting command shape is:

    gemini --version
    gemini --help
    gemini -p '<literal probe prompt>' --approval-mode=yolo --output-format json --debug > '<durable output path>'

Use this section order for both provider evidence files so the coordinator can review them without inference. Replace every bracketed value; do not leave template text in a `passed` record:

    # Gate 6 <Provider> Evidence

    Status: not started
    Date (UTC): [YYYY-MM-DD]
    Owner environment: [provider, operating system, shell]
    Session base commit: [full hash]
    Gate 5 ancestor checkpoint: d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd
    Probe implementation commit: [full human-created commit containing the current provider correction]
    CLI version: [exact output]
    Authentication: [passed|blocked; no secrets]
    Installed help and command syntax: [relevant excerpts and resulting exact commands]
    Provider installation/configuration check: [required comparison commands, exit, observation]
    Disposable worktree: [resolved path and git worktree list evidence]

    ## Probe Results

    For each required matcher or lifecycle event: [name, literal prompt, exact command, expected observation, actual event and diagnostic, exit status, concise transcript evidence, passed|failed|blocked]

    ## Simultaneous Failure

    [setup commands, source-ingest-first observation, both reasons, exit status, concise transcript evidence, passed|failed|blocked]

    ## Duration and Final State

    [monotonic timing command and elapsed seconds below 10; final ./scripts/lint-okf.py command/output/exit; final disposable status; exact worktree removal commands and verification]

    ## Completion

    [why every provider requirement passed, or the exact retry condition]
    Files left for human commit: [repository-relative paths]

If a Copilot run occurs on a non-Windows host and no executed probe fails, keep the same Copilot evidence file at `Status: blocked` until a human starts a Copilot-on-Windows session and fills the `powershell` result. If any executed probe fails, record the provider status as `failed` even when other observations remain blocked. That follow-up session reuses the committed partial record, creates a new detached worktree from the same Gate 5 checkpoint, and changes status to `passed` only after the missing observation and all final checks succeed.

For the simultaneous-failure probe, use the active provider name, `copilot` or `gemini`. On POSIX, the earlier `gate6_provider` variable must contain that exact name; run:

    printf '%s\n' '# Gate 6 pending source' > ".agents/sources/gate6-${gate6_provider}-pending.md"
    printf '%s\n' '# Gate 6 invalid probe' > ".agents/memory/gate6-${gate6_provider}-simultaneous.md"

On Windows, set `$gate6Provider` to the exact active provider name and run:

    $gate6Provider = "copilot"
    $gate6Utf8 = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/sources/gate6-$gate6Provider-pending.md"), "# Gate 6 pending source`n", $gate6Utf8)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".agents/memory/gate6-$gate6Provider-simultaneous.md"), "# Gate 6 invalid probe`n", $gate6Utf8)

Do not create the source summary manually. Trigger the provider's final event with the literal prompt `Do not call a tool. Reply exactly: simultaneous probe complete.` The source-ingest reason must appear first and identify the pending raw source or its generated draft summary; the independent OKF reason must also appear and contain `OKF002` plus the invalid canonical path. Record the ordered excerpts. If the host drops one reason, mark the provider record `failed`, preserve the exact evidence, and stop provider acceptance. The later corrective work must first add a failing regression and may then introduce a thin provider-local coordinator that runs the unchanged source-ingest and OKF validators and combines their reasons. Repeat all affected static and live probes after such a change. Do not merge validator state or profile logic.

Copy all needed transcript evidence to the main checkout, then restore only the disposable worktree before final timing. On POSIX run:

    git restore --source=HEAD --staged --worktree -- .agents/memory .agents/sources
    git clean -fd -- .agents/memory .agents/sources .github/agents
    git status --short

On Windows run the same three Git commands from `$gate6ProbeWorktree`. If installed help required a custom-agent path outside `.github/agents`, add that exact disposable path to the `git clean` command and record it. `git status --short` must be empty. These destructive commands are authorized only inside the freshly created Gate 6 worktree after transcript evidence is durable; verify `git rev-parse --show-toplevel` equals the recorded probe path immediately before running them.

On POSIX, measure lint duration with this exact monotonic command and record both printed fields:

    python3 - <<'PY'
    import subprocess
    import time

    started = time.monotonic()
    result = subprocess.run(["./scripts/lint-okf.py"], check=False)
    print(f"elapsed_seconds={time.monotonic() - started:.6f}")
    print(f"exit_status={result.returncode}")
    PY

On Windows use `$gate6Timer = [System.Diagnostics.Stopwatch]::StartNew(); python scripts/lint-okf.py; $gate6LintExit = $LASTEXITCODE; $gate6Timer.Stop()` and record `$gate6Timer.Elapsed.TotalSeconds` and `$gate6LintExit`. Before a provider owner writes `Status: passed`, every required event and matcher for that provider must have direct evidence, the simultaneous-failure probe must preserve both reasons in order, the real full-corpus linter must finish below the 10-second hook timeout, and the final lint must be green.

On POSIX, return to the recorded main checkout, run `git worktree list`, remove only the recorded probe with `git worktree remove --force "$gate6_probe_worktree"`, and run `git worktree list` again. On Windows use:

    Set-Location $gate6MainRoot
    git worktree list
    git worktree remove --force $gate6ProbeWorktree
    git worktree list

Record `git status --short` in the disposable worktree immediately before disposal; it must be empty after the authorized restore and scoped clean. If any path remains, mark the provider record `failed` or `blocked` and record the exact path instead of claiming cleanup passed. The force flag is authorized only for the recorded Gate 6 worktree after evidence has been copied to the main checkout; it must never target the main checkout, `$HOME`, or an unresolved variable.

At the end of a provider session, update that provider's evidence file, its own `Progress` and `Artifacts and Notes` lines in this ExecPlan, and the Gate 6 status and next step in `docs/okf-kb-migration/handoff.md`. Record `passed`, `failed`, or `blocked` and write `evidence commit: pending human commit`; do this even when no later session can start. Do not change the other provider's evidence or status and do not mark Milestone 6 accepted. Run `git diff --check`, run the mandatory `update-agent-docs` pass, and include every resulting changed path in the evidence file's `Files left for human commit` field. After the human provides the commit hash, the next session replaces the pending marker with that hash and checks the matching `Progress` item only if the evidence status is `passed`. A `failed` or `blocked` record stays unchecked and names the exact retry condition.

If the user explicitly requests the archived provider workflow, after both provider evidence files are committed with `Status: passed`, a coordinator reads both complete records and verifies their commits descend from the Gate 5 checkpoint. That optional coordinator reruns the complete final matrix and updates the evidence records without changing the already accepted Gate 6 status. After merge, the human supplies the merge or squash hash for one final record-only update; never invent either hash in advance.

Milestone acceptance requires all static tests, skill evaluations, corpus lint modes, install/startup regressions, simulated provider envelope and simultaneous-failure cases, link checks, and diff checks to pass. Human-started provider evidence files and live event/matcher probes are not required. Record the exact merge commit or squash commit as the one rollback unit after merge.

## Concrete Steps

Run all commands from the checkout root returned by `git rev-parse --show-toplevel` unless a disposable worktree path is explicitly recorded. The original coordinator checkout is `/Users/adam/dev/skills`, but provider sessions must use their own resolved root and must not assume that macOS path exists.

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

Each provider evidence file must replace these starting command shapes with the exact commands verified by that installed CLI's `--help`, including literal prompts, output paths, model or agent choice, permissions, and resolved worktree path:

    copilot --version
    copilot -p '<mutation or stop-event probe prompt>' -s --allow-tool='<minimal tools>' --output-format json --share "$gate6_probe_parent/copilot-probe-transcript.md"
    gemini --version
    gemini -p '<mutation or AfterAgent probe prompt>' --approval-mode=yolo --output-format json --debug > "$gate6_probe_parent/gemini-probe.json"

`gate6_probe_parent` is the recorded temporary parent of the disposable worktree, so these raw outputs do not make the worktree dirty. Copy only concise redacted proof into the provider evidence file. On PowerShell use the corresponding `$gate6ProbeParent` path with `Join-Path`.

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

Behavioral acceptance uses the public provider contract suites. They exercise every configured envelope, lifecycle response, retry state, diagnostic parity rule, and simultaneous-failure ordering without requiring installed provider CLIs.

The source-ingest manifest must retain version 1 and its existing state/hash/orphan semantics. All raw files under `.agents/sources/` must be byte-identical to the Gate 3 checkpoint. All 31 canonical paths and bodies must be preserved except the explicitly approved frontmatter-teaching prose. `AGENTS.md` must continue to route to uppercase `.agents/memory/INDEX.md`, and no selector, sidecar, prompt injection, provider runtime, compatibility parser, lint suppression, qualification state, or automatic repair may appear.

An unavailable provider CLI or missing authentication does not block acceptance. A failing static provider contract, lost simulated simultaneous-failure reason, incomplete skill baseline, unreviewed eval output, or any other final-matrix failure means acceptance is not met.

## Idempotence and Recovery

The linter and adapters are read-only and safe to rerun. Fixture tests copy from one pristine source for each case and must remove only their own exact temporary directories through existing `scripts/test-common.sh` patterns. Vendoring is repeatable only after verifying the exact archive hash; never overlay a different PyYAML version. Corpus migration is deterministic from the Gate 3 checkpoint and must not be rerun against partially converted documents without first inventorying their frontmatter.

Each gate ends in a reviewable commit, and its commit hash is recorded below. If a pre-merge gate must be undone, use a normal `git revert <gate-commit>` so the rollback is explicit and does not erase unrelated work. Do not use hard reset or broad checkout. If Gate 4 fails mid-edit, do not enable hooks or claim conformance; finish the atomic conversion in the same worktree or revert the exact Gate 4 commit after it exists.

The merged migration is one rollback unit. If it lands as one squash commit, run `git revert <migration-commit>`. If it lands as one merge commit, run `git revert -m 1 <migration-merge-commit>`. A post-merge enforcement or conformance regression reverts the entire unit: canonical metadata, authoring guidance, linter/vendor, scaffold producers, adapters, and registrations. Re-enablement requires a root cause, a regression test, and the complete green matrix.

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
- Gate 4 final rollback checkpoint: `917313a04bb513039ea0a2e596a8c381370766e7` (implementation checkpoint `d21c4351` plus the approved semantic YAML draft-detection correction). It preserves all 31 canonical paths, changes only the nine expected manifest `summary_hash` fields, and leaves raw sources unchanged. Final validation passes shell/Python syntax, both auto-ingest suites, the linter contract suite, human/JSON full-corpus lint, active migration links, legacy/lowercase searches, and `git diff --check`.
- Gate 5 source recheck: GitHub and Gemini contracts remain compatible with the accepted design; Gemini main was `ed2ac40df67a319bf348bd7e3d10494696b31b38`, issue `google-gemini/gemini-cli#27712` remained open, and neither `copilot` nor `gemini` was installed.
- Gate 5 simulated result: both adapter suites, both source-ingest suites, both startup suites, `scripts/test_helpers.py`, `scripts/test-install.sh`, adapter Python/shell syntax, provider JSON parsing, executable modes, human/JSON corpus lint, and `git diff --check` pass. Premium first review found three required boundary gaps; public regressions and fixes now cover native Copilot eventless payloads, checkout-anchored linter execution with nested/external paths, strict linter schemas, and exact post-escaping Gemini output bounds. Fresh Premium follow-up approved the fixes with no remaining required findings.
- Gate 5 rollback checkpoint: `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd`; verified as current `HEAD` with parent `7767eea03aaeef00f222c28efe9412c1cc294ad3` and a clean worktree.
- Gate 6 checkpoint-recording doc pass: no canonical agent-document update was needed because this session changed migration status only; the Gate 5 public interfaces and durable hook guidance were already synchronized in the checkpoint.
- Gate 5 agent-doc synchronization: `.agents/instructions/hooks.md`, `.agents/memory/testing/hooks.md`, `.agents/memory/FILE_MAP.md`, `.agents/memory/INDEX.md`, and new `.agents/memory/API_MAP.md` describe the shipped entry points, trust boundary, and validation route. The `okf-authoring` profile pass reports clean human and exact empty JSON lint, valid local links, and exactly those five canonical documentation paths in scope.
- Gate 6 historical execution ownership: provider work was assigned to sequential, human-started sessions in the respective authenticated environments. The user later removed those sessions from acceptance; retain the runbook only for optional future diagnostics.
- Gate 6 baseline: `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd` remains the rollback ancestor and the checkpoint used by the failed initial Copilot run. The next Copilot worktree must use the human-created correction commit so `.github/hooks/scripts/validate-stop.py` is present.
- Gate 6 runbook validation: delegated Standard review approved after all required corrections; active migration links, runbook-clause checks, human/JSON canonical lint, and `git diff --check` pass. The mandatory `update-agent-docs` pass found no canonical `.agents/` update because this change only refines the migration-specific execution handoff.
- Gate 6 failed-evidence correction doc pass: no canonical `.agents/` update was needed because the corrections changed only migration-specific status, evidence integrity, and next-step records; hook guidance already records independent source-ingest/OKF behavior.
- Gate 6 Copilot evidence: `docs/okf-kb-migration/gate6-copilot-evidence.md`; status `failed`, human-created evidence commit `bb4743f71a7409842347870aa883df4c9ef2ea8a`. The rerun records direct bash/edit `postToolUse` `OKF002` evidence, missing `powershell`, unobserved `create`, indirect-only `agentStop`, missing custom-agent `subagentStop`, failed simultaneous-failure ordering, final lint `0.039904s`/exit 0, and safe disposable-worktree removal. Its temporary transcripts and some exact command expansions were not retained, so the next run must preserve fully expanded commands and durable redacted excerpts before cleanup.
- Gate 6 Gemini evidence: not created because the user removed human-started Gemini proof from acceptance.
- Simultaneous-failure result and coordinator decision: the public registered-hook regression reproduced the live lost source-ingest reason. `.github/hooks/scripts/validate-stop.py` now runs the unchanged source-ingest validator before the unchanged OKF adapter and combines both block reasons. The affected Copilot OKF, auto-ingest, startup, helper, syntax, and corpus-lint checks pass.
- Gate 6 verification decision: on 2026-09-16, the user removed human-started Copilot and Gemini proof from acceptance. The complete static and simulated final matrix passes, so Gate 6 acceptance is met.
- Gate 6 final acceptance benchmark correction: the first grading run changed both eval-4 scores because commit `2be5d5ba` had removed the mandatory one-way composition step from `.agents/skills/update-agent-docs/SKILL.md`. Restoring that step passed quick validation and regenerated all 16 grading files with no diff.
- Gate 6 final acceptance documentation pass: no canonical `.agents/instructions/` or `.agents/memory/` update is needed. Migration records capture the benchmark regression, while existing canonical hook and skill-testing guidance remains current.
- Gate 6 correction documentation pass: `.agents/instructions/hooks.md`, `.agents/memory/API_MAP.md`, `.agents/memory/FILE_MAP.md`, `.agents/memory/adrs/hooks.md`, `.agents/memory/known-issues/hooks.md`, and `.agents/memory/testing/hooks.md` now describe the coordinator, public seam, and live-provider gotcha.
- Gate 6 coordinator evidence commit: not required under the user-approved static acceptance path. Final acceptance records remain uncommitted pending human review.
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

Revision note (2026-09-10): Recorded the user-created final Gate 4 rollback checkpoint `917313a04bb513039ea0a2e596a8c381370766e7`, marked Milestone 4 accepted, and moved the active frontier to Gate 5's provider-source and installed-CLI-version recheck.

Revision note (2026-09-10): Rechecked current official Copilot and Gemini hook behavior, confirmed the accepted Gate 5 contract is unchanged and both CLIs remain unavailable locally, and opened the adapter test-first implementation work.

Revision note (2026-09-10): Completed Gate 5 adapters, repo-local candidate registrations, parity/security regressions, the full static matrix, and Premium follow-up review; left the approved worktree uncommitted for the user's manual checkpoint before Gate 6.

Revision note (2026-09-10): Completed the mandatory agent-doc and OKF representation pass, recorded its scoped clean-lint evidence, and synchronized the final Gate 5 stopping point with the manual-checkpoint requirement.

Revision note (2026-09-10): Recorded Gate 5 checkpoint `d40c2d5df5b9432f5d0e4d8e48eb32ad22e478cd`, verified clean `HEAD`, opened Gate 6 preflight, and recorded that both required provider CLIs remain unavailable locally.

Revision note (2026-09-10): Recast Gate 6 as two sequential, human-started provider sessions plus final coordinator acceptance; added provider-specific ownership, durable evidence paths and required fields, safe worktree lifecycle, human-commit recording, and pass/fail/block completion rules.

Revision note (2026-09-10): Resolved delegated runbook-review findings by requiring a human runbook checkpoint before provider work, provider-owned stopping-point updates, exact Windows setup and cleanup commands, fixed probe contents/prompts/expected `OKF002` observations, explicit installation checks, and post-coordinator commit recording.

Revision note (2026-09-14): Reviewed human-created Copilot evidence commit `bb4743f71a7409842347870aa883df4c9ef2ea8a`, corrected the executed simultaneous-failure result from blocked/not-started to failed, recorded incomplete reproducibility artifacts, and moved the active step to the required test-first Copilot correction before any provider rerun.

Revision note (2026-09-15): Recorded the user's decision to defer human-started Copilot and Gemini verification for now, moved Milestone 6 from active work to open/deferred without weakening acceptance, and preserved the existing provider runbook as the dormant resume path.

Revision note (2026-09-16): Reopened only the Copilot correction, reproduced the live lost-reason behavior at the registered-hook public seam, added the permitted thin stop coordinator, synchronized agent documentation, and left live Copilot, Gemini, and final coordinator acceptance open.

Revision note (2026-09-16): Recorded the user's decision to skip and no longer require human Copilot and Gemini proof sessions, ran the complete static and simulated final matrix successfully, and marked Gate 6 accepted for human review and merge.
