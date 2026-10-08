---
type: Agent Memory
description: Top-level overview; per-layer directory detail lives in the instruction files
---

# File Map

This file is a **top-level map only**. For area detail and working rules, read the matching instruction file:

- repo docs and root workflow → `.agents/instructions/repo.md`
- general provider hooks → `.agents/instructions/hooks.md`
- source auto-ingest hooks → `.agents/instructions/hooks-auto-ingest.md`
- hook observability and trace storage → `.agents/instructions/hooks-observability.md`
- skills areas → `.agents/instructions/skills.md`
- custom agents → `.agents/instructions/agents.md`
- shell helper scripts → `.agents/instructions/scripts.md`
- PowerShell installer/test scripts → `.agents/instructions/powershell.md`

## Source Areas

| Path | Layer | Purpose |
| --- | --- | --- |
| `.github/hooks/` | hooks | Repo-local Copilot hook config, auto-ingest wiring, and final-response validation coordination. |
| `.copilot/` | hooks | Copilot instructions and local hook runtime sources. |
| `.gemini/` | hooks | Gemini instructions and local hook runtime sources. |
| `.codex/` | hooks | Project-local OKF Stop registration and adapter, plus separate inactive user-global hook sources and install-time configuration template. |
| `hooks/` | hooks | Canonical build-time renderers, provider metadata, and explicit generated-output ownership manifest. |
| `skills/` | skills | One directory per skill, centered on `SKILL.md`; may include scripts, references, assets, evals, and grader tests (see skills instructions). |
| `skills/handoff/` | skills | Independent handoff maintenance skill, creation/update/resume grader, and supplemental [guidance scenarios](../../skills/handoff/evals/guidance-scenarios.json). |
| `.agents/skills/exec-plans/` | repo-local skills | Independent execution-plan workflow, creation/resume/recovery grader, and qualitative prototype/migration [authoring scenario](../skills/exec-plans/evals/authoring-scenarios.md). |
| `skills/execplan-implement/` | skills | ExecPlan consumer with tasks, integrated acceptance, and document-only orchestration scenarios; dependency boundaries live in [skills instructions](../instructions/skills.md#planning-and-task-execution). |
| `skills/spec-to-tasks/`, `skills/prd-ralph/`, `skills/prd-ralph-loop/` | skills | Task producer, single-task worker and blind loop, with the current schema/intake contract, consumer scenarios, and public grader suites routed by [skills testing](testing/skills.md#task-workflow-graders). |
| `skills/dotnet-upgrade/` | skills | Explicitly invoked .NET upgrade source bundle with standalone templates, dated route research and provenance; its document-only acceptance record is [references/document-review.md](../../skills/dotnet-upgrade/references/document-review.md). Use [skills instructions](../instructions/skills.md#dotnet-upgrade) for approval and review boundaries. |
| `agents/` | agents | Canonical Markdown custom-agent prompt files for Copilot, Gemini, and generated Codex TOML. |
| `docs/<effort>/` | repo docs | Active research and execution plans that need version history while work is in progress. |
| `docs/adr/` | repo docs | Human-facing ADRs that complement `.agents/` canonical guidance. |
| `scripts/` | scripts | Installers, importers, the aggregate test runner, validation helpers, and shared shell utilities. |
| `references/` | references | Optional shared reference material shipped with installs. |

## Knowledge and top-level docs

| Path | Status | Purpose |
| --- | --- | --- |
| `.agents/instructions/` | canonical | Agent-facing workflow rules and area conventions. |
| `.agents/memory/` | canonical | Durable repo facts, file maps, testing routes, and known issues. |
| `docs/ideas.md` | companion | Lightweight inbox for one-line ideas that are not ready for research or planning. |
| [docs/exec-plan-tasks-improvements.md](../../docs/exec-plan-tasks-improvements.md), [docs/handoff.md](../../docs/handoff.md) | retained skill effort | Requested plan and sibling handoff for planning/task skill revisions; acceptance evidence, comparison limits and review pointers live in these artifacts. |
| [docs/tool-guardian-tuning/ExecPlan.md](../../docs/tool-guardian-tuning/ExecPlan.md) | retained effort | Reconciled Guardian plan with completed code and pending owner review, installation, and platform/provider proof. The [handoff](../../docs/tool-guardian-tuning/handoff.md) gives the current action; the [prior plan](../../docs/tool-guardian-tuning/history/2026-10-07-plan-before-reconciliation.md), [prior handoff](../../docs/tool-guardian-tuning/history/2026-10-07-handoff-before-reconciliation.md), [repair logs and audit](../../docs/tool-guardian-tuning/repair-logs/orchestration.md), and [verified repair evidence](../../docs/tool-guardian-tuning/evidence/review-repair-root-verification.json) preserve historical evidence. Retention was explicitly requested. |
| `README.md` | companion | Repo overview and install entry point. |
| `AGENTS.md` | companion | Quickstart, loading contract, and top-level links for agents. |

## Key files

| Path | Why it matters |
| --- | --- |
| `scripts/install.sh` | Installs repo assets into `~/.agents`, `~/.copilot`, `~/.gemini`, and `~/.codex` targets, including generated Codex agents at `${CODEX_HOME:-$HOME/.codex}/agents`. |
| `scripts/install.ps1` | PowerShell 7 port of `scripts/install.sh`; same sources, destinations, exclusions, and installed layout, including `$CODEX_HOME/agents` when set (run with `pwsh scripts/install.ps1`). |
| `scripts/install-codex-agents.py` | Strict, transactional converter from top-level `agents/*.md` sources to manifest-managed personal Codex TOML agents. |
| `scripts/install-codex-hooks.py` | Atomically and idempotently merges exact maintained Codex `SessionStart`, `PreToolUse`, and `Stop` handlers into user-global `hooks.json`. |
| `scripts/install-provider-hooks.py` | Preflights and merges maintained Copilot/Gemini configuration while retaining unrelated user settings and retired installed hook registrations. |
| `scripts/test-codex-hooks-startup.sh` | Public-process contract and security regressions for the Codex required-skills hook. |
| `scripts/test-security-banners.py` | Public block, warning, excerpt, redaction, and fallback envelopes across three provider Tool Guardian adapters. |
| `scripts/test-codex-hooks-tool-guard.sh` | Focused Codex Tool Guardian envelope, limit-advice, warning, and guard-log checks. |
| `.codex/hooks/tool-guard.py` | Generated Codex Tool Guardian adapter installed through the maintained hook merger. |
| `hooks/families/tool_guard.py` and provider-local `helpers/tool_guard_policy.py` | Canonical renderer and identical generated local policy helpers, delivered with each adapter. |
| `scripts/tool_guard_corpus.py`, `scripts/fixtures/tool_guard_vectors.py` | Shared sanitized incident corpus, native provider fixtures, and baseline/candidate decision expectations. |
| `scripts/test-tool-guard-false-positives.py` | Public three-provider corpus check with an optional frozen baseline root. |
| `scripts/test-tool-guard-native-data.py`, `scripts/test-tool-guard-shell-data.py`, `scripts/test-tool-guard-limits.py` | Native-schema/data, executable-role/security, and truthful input-bound suites. |
| `scripts/test-benchmark-high-rate-hooks.py` | Public benchmark CLI contract with isolated fixture entrypoints. |
| `scripts/test-scan-secrets-capture.py` | Public generated-hook capture regressions shared by the three provider scanner suites. |
| `scripts/benchmark-high-rate-hooks.py` | Direct macOS subprocess benchmark for retained per-tool and model-chunk hook handlers using disposable Git repositories and homes. |
| `scripts/benchmark-tool-guard-resources.py`, `scripts/benchmark-tool-guard-optimizations.py` | Native macOS finite-case timing/RSS and isolated whole-hook optimization ablations; interfaces are in [API Map](API_MAP.md#tool-guardian-benchmark-tools). |
| `scripts/test-scan-secrets-windows.ps1` | Native Windows generated-scanner capture suite used by the focused Windows workflow. |
| `scripts/test-lifecycle-messages-windows.ps1` | Native Windows lifecycle message envelopes for startup, turn-end, and scanner hooks in disposable fixtures. |
| `scripts/test-install.ps1` | Fixture-repo test for `scripts/install.ps1` (run with `pwsh -NoProfile -File scripts/test-install.ps1`). |
| `scripts/import-skill-repos.sh` | Human-run multi-source importer that refreshes selected upstream skills, including the `web-*` quality skills. |
| `scripts/common.sh` | Shared shell helper for resolving repo root in small shell tests and utilities. |
| `scripts/test-all.py` | Executable aggregate test runner with an explicit maintained-suite registry; CLI contract is in `API_MAP.md`. |
| `scripts/generate-hooks.py` | Read-only freshness checker and transactional writer for the explicit `hooks/manifest.py` output set. |
| `scripts/test_test_all.py` | Public-process regressions for the aggregate runner, including streams, exit codes, preflight, and descendant cleanup. |
| `scripts/lint-okf.py` | Provider-neutral full-corpus OKF profile linter with human/JSON output and `0`/`1`/`2` exit semantics. |
| `scripts/test-okf-lint.sh` | Public-CLI contract suite for the OKF linter; copies the valid two-bundle fixture under `scripts/fixtures/okf-valid-repo/` for isolated mutation cases. |
| `.github/hooks/scripts/lint-okf.py` | Repo-local Copilot turn-end adapter for central OKF diagnostics and bounded audit. |
| `.github/hooks/scripts/validate-stop.py` | Repo-local Copilot stop coordinator that preserves source-ingest-first blocking reasons while running the independent OKF adapter. |
| `.gemini/hooks/scripts/lint-okf.py` | Repo-local Gemini `AfterAgent` adapter for central OKF diagnostics and bounded audit. |
| `.codex/hooks.json`, `.codex/hooks/repository-okf.py` | Project-local Codex `Stop` registration and central OKF adapter; excluded from user-global hook installation. |
| `scripts/test-hooks-okf-lint.sh` | Copilot adapter contract, parity, failure, output-bound, and checkout-containment suite. |
| `scripts/test-gemini-hooks-okf-lint.sh` | Gemini adapter contract, parity, retry, failure, output-bound, and checkout-containment suite. |
| `scripts/test-codex-repository-okf.sh`, `scripts/test-repository-okf-windows.ps1` | Codex public Stop and audit suite plus native Windows provider-envelope and command-resolution checks. |
| `scripts/vendor/` | Checked-in PyYAML 6.0.3 pure-Python runtime, source record, and license used only by the offline OKF linter. |
| `scripts/addy-install.sh` | Imports selected upstream addy skills, agents, and references into this repo. |
| `.agents/memory/sources/source-ingest-manifest.json` | Shared source-summary state file for Copilot and Gemini auto-ingest hooks plus pending-ingest gating. |
| `.agents/skills/okf-authoring/SKILL.md` | Repository-local representation workflow for canonical Markdown under `.agents/instructions/` and `.agents/memory/`; invoked one-way after `update-agent-docs` semantic changes. |
| `.copilot/hooks/rtk-rewrite.json` | Automatic RTK forwarding registration for Copilot; its generated adapter comes from `hooks/families/rtk.py`. |
| `scripts/configure-rtk.py` | Validates stable RTK and safely sets the persistent hook-warning option in user TOML; retires only verified old prerelease files. |
| `scripts/test-rtk-stable.py`, `scripts/test-rtk-stable-windows.ps1` | Disposable-home stable RTK config and installer tests, plus native Windows diagnostic proof. |
| `docs/adr/0001-auto-ingest-runtime-shape.md` | Records why source auto-ingest uses runtime-local hook code with one committed repo manifest. |
| `docs/adr/0002-pending-ingest-gate.md` | Records why the pending-ingest gate blocks normal work until summaries resolve. |
| `docs/adr/0003-sqlite-backed-hook-observability.md` | Records why hook observability uses SQLite as source of truth with NDJSON fallback. |
| `docs/adr/0004-generated-provider-hooks.md` | Records why shared hook behavior will use canonical build-time sources while runtime scripts remain provider-local. |
| `.nvmrc` | Node version hint for local tooling. |
| `skills/skill-creator/scripts/quick_validate.py` | Narrow validation entry point for skill definitions. |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill directory into a distributable `.skill` archive. |
| `skills/handoff/evals/grade_benchmark.py`, `.agents/skills/exec-plans/evals/grade_benchmark.py` | Independent document-maintenance graders; public CLI contracts are in [API Map](API_MAP.md#document-maintenance-graders), and their `test_grade_benchmark.py` suites are routed by [skills testing](testing/skills.md#document-maintenance-graders). |
| `.agents/skills/ingest-source/SKILL.md` | The canonical repo-local `/ingest-source` recovery skill used by the pending-ingest gate. |
