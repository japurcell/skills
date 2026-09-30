# Agent-brain Pilot Workload Facts

Read-only inventory of existing representative fixtures and validators. No validator was run during this inspection.

## Read-only KB answer and Tool Guardian qualification

- `.agents/memory/known-issues/hooks.md`, heading **Active guards can block their own maintenance**, records scoped observations: guard false positives against documentation wording and quoted identifiers; small focused patches and equivalent wording worked in those observed cases. The broader Tool Guardian note is an observed 128-command-segment limit and explicitly distinguishes it from structured byte and scan-text limits. `.agents/memory/known-issues/hooks.md`, heading **Structured input can reach its byte limit before text scanning**, records the `write_file.content` case as `structured_bytes`, 32768-byte threshold, and measured UTF-8 bytes; it says not to conflate this with later scan-text limits. These are qualified observations and must not be presented as exhaustive rules or replayable proof.
- More public-envelope examples are in `scripts/test-codex-hooks-tool-guard.sh` and `scripts/test-security-banners.py`: limit denial identifies rule, field, threshold/count and matching log entry without allowlist advice; other cases cover provider envelopes, dangerous-operation rule IDs, redaction, bounded excerpts, and warnings. `scripts/test-security-banners.py` class `SecurityBannerTests` is the cross-provider fixture source.
- Candidate focused check commands (not run): `bash scripts/test-codex-hooks-tool-guard.sh`; `python3 scripts/test-security-banners.py`.

## Skill documentation/help and validation

- The existing skill-definition shape and validation implementation are `skills/skill-creator/scripts/quick_validate.py` and `.agents/instructions/skills.md`. The validator requires a skill directory containing `SKILL.md`, checks frontmatter keys including required `description`, and has a public usage form `python quick_validate.py <skill_directory>`.
- `.agents/skills/okf-authoring/SKILL.md`, `.agents/skills/okf-authoring/references/profile.md`, and `source-summaries.md` are a concrete skill-plus-progressive-reference example. `.agents/skills/okf-authoring/evals/evals.json` supplies cases for in-scope authoring, outside-root handling, evidence, exact output sets, clean lint, and no-op behavior; existing iteration artifacts are under `skills/okf-authoring-workspace/iteration-1/`.
- Targeted command: `python3 skills/skill-creator/scripts/quick_validate.py <skill-directory>`. For an OKF-authoring-like fixture, the repository's prescribed check is `python3 scripts/lint-okf.py` (the skill's eval artifacts are fixtures, not a second validator).

## Canonical hook-family change and generated freshness

- `hooks/families/tool_guard.py` is the canonical Tool Guardian family source. `hooks/manifest.py` explicitly maps that family to `.copilot/hooks/scripts/tool-guard.py`, `.gemini/hooks/scripts/tool-guard.py`, and `.codex/hooks/tool-guard.py`; generated outputs identify their source in the ownership header. `scripts/generate-hooks.py` owns rendering, `--write`, and no-write `--check`.
- `scripts/test-generate-hooks.py` covers deterministic rendering, explicit family targets/runtime boundaries, freshness/ownership and executable modes, plus transactional write failure/interrupt rollback (`GenerateHooksTests.test_lock_and_injected_write_failure_leave_outputs_unchanged`). Its tearDown restores checked-in outputs, so do not run it in a read-only planning pass.
- Targeted commands when execution is authorized: `python3 scripts/test-generate-hooks.py`; `python3 scripts/generate-hooks.py --check`. Public behavior of the generated Tool Guardian adapters is separately covered by `bash scripts/test-codex-hooks-tool-guard.sh` and `python3 scripts/test-security-banners.py`.

## Source-summary/manifest freshness and ingestion

- Canonical state/schema location is `.agents/memory/sources/source-ingest-manifest.json`; source summaries accompany it in `.agents/memory/sources/`. `.agents/memory/INDEX.md` routes readers to summaries and says raw inputs under `.agents/sources/` are authoritative for exact source details. `.agents/memory/sources/llm-wiki-md.summary.md` is one existing summary example.
- `hooks/families/auto_ingest.py` is the canonical renderer; it loads the engine from `hooks/families/auto_ingest_engine.py` and provider wrapper sources. Target paths are the six `auto_ingest` entries in `hooks/manifest.py`. `scripts/test-hooks-auto-ingest.sh` covers new/modified/renamed/deleted sources, pending gates, draft frontmatter versus body markers, sanitized summary paths, audit output, and Copilot startup/prompt/stop entry points. `scripts/test-gemini-hooks-auto-ingest.sh` covers Gemini startup/BeforeAgent injection/AfterAgent gate and source changes. These public suites assert manifest state and preserved existing summaries in stale cases.
- Relevant commands: `bash scripts/test-hooks-auto-ingest.sh`; `bash scripts/test-gemini-hooks-auto-ingest.sh`; for family-rendered source changes also `python3 scripts/test-generate-hooks.py` and `python3 scripts/generate-hooks.py --check`. Recovery workflow source is `.agents/skills/ingest-source/SKILL.md`.

## Installer managed-registration preservation and rollback

- `scripts/install-provider-hooks.py` contains the managed-name reconciliation: preserved registrations and remaining handlers are retained before maintained entries are added. `scripts/test-install.sh` functions `test_provider_refresh_preserves_retired_and_user_entries`, `test_provider_malformed_json_stops_before_mutation`, `test_stale_generated_hooks_stop_before_destination_mutation`, and `test_generator_failure_stops_before_destination_mutation` check preservation, byte/tree fingerprints, and preflight failures. The Codex hook merger has a separate public suite `scripts/test-install-codex-hooks.py`; the installer suite also has `test_preserves_unrelated_codex_configuration_and_replaces_owned_handler`.
- Targeted commands: `bash -n scripts/install.sh && bash scripts/test-install.sh`; `python3 scripts/test-install-codex-hooks.py`. The installer tests use disposable homes and have fingerprint/backup/idempotence assertions. `scripts/test-generate-hooks.py` is the explicit generator rollback fixture, not an installer rollback claim.

## Knowledge index, OKF, and references

- Authoritative index/routing examples: `.agents/memory/INDEX.md`, `.agents/memory/FILE_MAP.md`, `.agents/instructions/skills.md`, and `.agents/skills/okf-authoring/references/profile.md`. Source-specific provenance examples are in `.agents/memory/sources/*.summary.md` and `source-ingest-manifest.json`; raw source inputs are under `.agents/sources/`.
- `scripts/lint-okf.py` is the offline canonical-document validator. `scripts/test-okf-lint.sh` copies `scripts/fixtures/okf-valid-repo/` for isolated public-CLI cases and includes manifest/source-summary binding cases (`test_okf104_manifest_binding`) among other profile diagnostics. Copilot/Gemini/Codex wrappers have focused suites `scripts/test-hooks-okf-lint.sh`, `scripts/test-gemini-hooks-okf-lint.sh`, and `scripts/test-codex-repository-okf.sh`.
- Targeted commands: `bash -n scripts/test-okf-lint.sh && bash scripts/test-okf-lint.sh`; `python3 scripts/lint-okf.py`; for adapter behavior use the matching suite above. No general local-Markdown-link validator was identified in this inspection; OKF lint establishes the documented profile and manifest-binding checks, not comprehensive reference-link resolution.

## Scope note

This inventory supplies source anchors and existing validation seams only. It does not select workload cases, repetitions, providers, or an implementation sequence. Commands above are recorded from repository guidance and test entry points; they were not executed here.
