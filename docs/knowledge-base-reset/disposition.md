# Agent KB reset - disposition

Completed 2026-10-07 for this repository under the user-approved claim-level rubric. The authoring model's age or identity was not a retention criterion.

## Result

| Surface | Before | After |
| --- | ---: | ---: |
| Memory files, including the operational manifest | 31 | 13 |
| Memory words | 17,259 | 1,717 |
| Instruction files | 8 | 24 |
| Instruction words | 5,160 | 10,702 |
| Combined KB words | 22,419 | 12,419 |
| Required general routing words before area-specific reading | 1,947 | 213 |

Counts use whitespace-delimited words, including frontmatter and the unchanged manifest. Memory is about 90% smaller; the combined KB is about 45% smaller. Instruction growth comes from recovered rules and conditional testing/provider branches. The previous general read path loaded memory INDEX, ARCHITECTURE, and CONVENTIONS; the new path loads the [instruction index](../../.agents/instructions/INDEX.md).

## All 31 original memory files accounted for

Paths in the first column are relative to `.agents/memory/`.

| Original files | Count | Disposition and current owner |
| --- | ---: | --- |
| `ARCHITECTURE.md`, `CONVENTIONS.md` | 2 | Removed source/layout descriptions and repeated formatting rules. Preserved edit boundaries, archive scope, installation ownership, and retention in [repository workflow](../../.agents/instructions/repo.md), [skill conventions](../../.agents/instructions/skills.md), and [knowledge admission](../../.agents/instructions/knowledge-base.md). Formatting points to `.editorconfig`. |
| `FILE_MAP.md`, `API_MAP.md` | 2 | Removed caches of discoverable files, CLIs, schemas, and limits. Routes now point to source, tests, CLI help, and retained ADRs. Unique safety/evidence constraints remain in [security rules](../../.agents/instructions/hooks-security.md), [security testing](../../.agents/instructions/testing/hooks-security.md), and [skill testing](../../.agents/instructions/testing/skills.md). |
| `KNOWN_ISSUES.md`, `TESTING_STRATEGY.md` | 2 | Removed duplicate routes/whitespace advice; recovered validation selection and evidence discipline in [testing guidance](../../.agents/instructions/testing.md). |
| `testing/hooks.md`, `testing/hooks-auto-ingest.md`, `testing/hooks-observability.md`, `testing/scripts.md`, `testing/powershell.md`, `testing/skills.md` | 6 | Moved requirements into `instructions/testing/`. Split general hooks from security/performance and live delivery. Dropped historical results, duplicated coverage narration, and superseded timing advice. |
| `known-issues/hooks.md`, `known-issues/hooks-auto-ingest.md`, `known-issues/hooks-observability.md`, `known-issues/scripts.md`, `known-issues/powershell.md` | 5 | Recovered applicable runtime, cleanup, parser, fixture, and deployment constraints in focused instructions. Removed generic language advice, repeated implementation descriptions, and unsupported/version-specific incident narration. |
| `known-issues/skills.md` | 1 | Retained two checked cross-tool limitations: invocation-control validation and benchmark metric proxies. Added evidence scope and recheck triggers. Fixture rules and validation commands live in test instructions. |
| `adrs/hooks.md` | 1 | Removed duplicate decisions and flow narration. Preserved current constraints and routed rationale to existing `docs/adr/` records. The current Tool Guardian contract owns its accepted performance budgets. |
| All nine `sources/*.summary.md` files | 9 | Rewrote as concise, attributed references checked against saved raw text. Removed stale “new file” labels, completed checklists, and automatic policy-promotion language. Each names its evidence and recheck condition. |
| `INDEX.md`, `LOG.md` | 2 | Kept optional evidence/source routing and concise ingestion provenance. Ordinary tasks no longer load the log or entire memory corpus. |
| `sources/source-ingest-manifest.json` | 1 | Kept byte-identical. Both runtime consumers still accept the rewritten summaries. |

## Decisions resolved by the rubric

- The saved CLI-design article sends warnings to stdout; established repository instructions send them to stderr. The summary now attributes the difference without adopting it as project policy.
- The old Tool Guardian `<40ms` guidance conflicted with the user-approved [current acceptance contract](../tool-guardian-tuning/ExecPlan.md#validation-and-acceptance). The current warm/cold allowances and finite-case ceiling remain authoritative.
- Cleanup advice involving interpolated trap commands conflicted with the existing instruction to register named cleanup functions. The established script instruction remains canonical.
- Code and tests verified behavior; they were not treated as proof that a model-authored recommendation expressed user intent. Current explicit constraints were retained, while generic and obsolete guidance failed admission.

No consequential authority conflicts remain unresolved.

## Preventing renewed accumulation

[Knowledge admission](../../.agents/instructions/knowledge-base.md) owns the retention gates. The root entry point and local `update-agent-docs` and `ingest-source` workflows now use it. A documentation pass can conclude that no memory should be added. File/API changes and source ingestion do not automatically create more KB prose. The representation profile still accepts legacy paths in isolated test fixtures; those fixtures do not instruct agents to recreate deleted maps.

## Verification

All checks passed:

- Full-corpus `rtk proxy python3 scripts/lint-okf.py`, including JSON output with zero diagnostics. The OKF `profile` and `source-summaries` branches were applied; moved test documents use `Agent Instruction`.
- `rtk proxy bash scripts/test-okf-lint.sh`.
- `scripts/test-hooks-startup.sh`, using a disposable Copilot observability-log path. The original assertion passed before relocation, failed on the missing old file, and passed after changing only its path to `instructions/testing/hooks-live.md`.
- `scripts/test-hooks-auto-ingest.sh` and `scripts/test-gemini-hooks-auto-ingest.sh`, using disposable provider observability-log paths. Their invalid-input diagnostics were expected negative cases; both exited 0.
- The existing skill validator for `.agents/skills/update-agent-docs` and `.agents/skills/ingest-source`, using `PYTHONPATH=scripts/vendor`.
- Both public startup scanners against isolated copies of all nine rewritten summaries, their raw sources, and the original manifest: nine active sources and zero pending sources for each provider.
- SHA-256 comparison: all nine raw inputs and the original manifest remained byte-identical.
- Changed-link checks, scoped diff review, plain-dash checks, and `rtk git diff --check`.

Link repair also corrected stale relative paths in the existing task-decomposition proposal. Its two unavailable historical installer examples are now labeled as unavailable evidence rather than linked as current files; this reset does not execute that proposal.

The only test-code edit changes the existing documentation path. Runtime hook code, public skills, installed copies, and user-global settings were outside this reset.
