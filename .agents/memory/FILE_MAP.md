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
| `agents/` | agents | Canonical Markdown custom-agent prompt files for Copilot, Gemini, and generated Codex TOML. |
| `docs/<effort>/` | repo docs | Active research, Wayfinder decision maps, and execution plans that need version history while work is in progress. |
| `docs/adr/` | repo docs | Human-facing ADRs that complement `.agents/` canonical guidance. |
| `scripts/` | scripts | Installers, importers, the aggregate test runner, validation helpers, and shared shell utilities. |
| `references/` | references | Optional shared reference material shipped with installs. |

## Knowledge and top-level docs

| Path | Status | Purpose |
| --- | --- | --- |
| `.agents/instructions/` | canonical | Agent-facing workflow rules and area conventions. |
| `.agents/memory/` | canonical | Durable repo facts, file maps, testing routes, and known issues. |
| `docs/ideas.md` | companion | Lightweight idea inbox and links to ideas promoted into active planning. |
| `README.md` | companion | Repo overview and install entry point. |
| `AGENTS.md` | companion | Quickstart, loading contract, and top-level links for agents. |

## Key files

| Path | Why it matters |
| --- | --- |
| `docs/just-in-time-context/map.md` | Closed context management decision map; its `tickets/` own accepted contracts. Read [execplan.md](../../docs/just-in-time-context/execplan.md) for implementation milestones and offline/live boundaries, or [the visual explanation](../../docs/just-in-time-context/agent-brain-execplan.html) for human review. |
| `scripts/install.sh` | Installs repo assets into `~/.agents`, `~/.copilot`, `~/.gemini`, and `~/.codex` targets, including generated Codex agents at `${CODEX_HOME:-$HOME/.codex}/agents`. |
| `scripts/install.ps1` | PowerShell 7 port of `scripts/install.sh`; same sources, destinations, exclusions, and installed layout, including `$CODEX_HOME/agents` when set (run with `pwsh scripts/install.ps1`). |
| `scripts/install-codex-agents.py` | Strict, transactional converter from top-level `agents/*.md` sources to manifest-managed personal Codex TOML agents. |
| `scripts/install-codex-hooks.py` | Atomically and idempotently merges exact maintained Codex `SessionStart`, `PreToolUse`, and `Stop` handlers into user-global `hooks.json`. |
| `scripts/install-provider-hooks.py` | Preflights and merges maintained Copilot/Gemini configuration while retaining unrelated user settings and retired installed hook registrations. |
| `scripts/test-codex-hooks-startup.sh` | Public-process contract and security regressions for the Codex required-skills hook. |
| `scripts/test-security-banners.py` | Public block, warning, excerpt, redaction, and fallback envelopes across three provider Tool Guardian adapters. |
| `scripts/test-codex-hooks-tool-guard.sh` | Focused Codex Tool Guardian envelope, limit-advice, warning, and guard-log checks. |
| `.codex/hooks/tool-guard.py` | Generated Codex Tool Guardian adapter installed through the maintained hook merger. |
| `scripts/test-scan-secrets-capture.py` | Public generated-hook capture regressions shared by the three provider scanner suites. |
| `scripts/benchmark-high-rate-hooks.py` | Direct macOS subprocess benchmark for retained per-tool and model-chunk hook handlers using disposable Git repositories and homes. |
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
| `docs/ready-ideas-execplan/windows-live-check.md` | Manual Windows provider check procedure accompanying the automated Windows workflow; records versions, tool results, audit evidence, and unverified cases. |
| `docs/ready-ideas-execplan/high-rate-hooks-performance.md` | Milestone 23 high-rate registration inventory, direct macOS benchmark method, distributions, budgets, and remaining cost. |
| `docs/ready-ideas-execplan/handoff.md` | Final acceptance summary, remaining limitations, and follow-up route for the completed hook plan. |
| `docs/adr/0001-auto-ingest-runtime-shape.md` | Records why source auto-ingest uses runtime-local hook code with one committed repo manifest. |
| `docs/adr/0002-pending-ingest-gate.md` | Records why the pending-ingest gate blocks normal work until summaries resolve. |
| `docs/adr/0003-sqlite-backed-hook-observability.md` | Records why hook observability uses SQLite as source of truth with NDJSON fallback. |
| `docs/adr/0004-generated-provider-hooks.md` | Records why shared hook behavior will use canonical build-time sources while runtime scripts remain provider-local. |
| `.nvmrc` | Node version hint for local tooling. |
| `skills/skill-creator/scripts/quick_validate.py` | Narrow validation entry point for skill definitions. |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill directory into a distributable `.skill` archive. |
| `.agents/skills/ingest-source/SKILL.md` | The canonical repo-local `/ingest-source` recovery skill used by the pending-ingest gate. |
| `skills/agent-brain/SKILL.md` | Staged source-checkout skill, bundled Python CLI, progressive references, typed v1 schemas, examples, and evals. |
| `skills/agent-brain/scripts/agent_brain/metadata.py`, `retrieval.py` | Standard-library annotation parser, stable unit records, conservative scope matching, transitive required-reference closure, and read-only section/document delivery. |
| `skills/agent-brain/schemas/metadata-v1.schema.json`, `examples/metadata-authoring-v1.md` | Namespaced Markdown metadata schema and authoring examples for defaults, policies, facts, exceptions, and references. |
| `scripts/test-agent-brain-cli.py` | Public subprocess tests for CLI presentation, read-only commands, guarded inputs, config validation, streams, and whole-artifact recall. |
| `scripts/test-agent-brain-retrieval.py` | Public subprocess tests for metadata parsing, scoped retrieval, closure, evidence disclosure, revisions, gaps, and external read-only mappings. |
| `skills/agent-brain/scripts/integration-bridge.py`, `skills/agent-brain/scripts/agent_brain/lifecycle.py` | Normalized integration events, finite registrations, scoped delivery/checkpoints, joined obligations, child settlement, guarded foreground learn, and durable output settlement. |
| `skills/agent-brain/scripts/agent_brain/state.py`, `skills/agent-brain/scripts/agent_brain/checks.py` | Worktree-local durable SQLite coordination and bounded actual trusted checks; no semantic executor. |
| `skills/agent-brain/scripts/agent_brain/stages.py`, `publication.py`, `history.py` | Foreground proposal validation, exact-set publication, exclusive recovery, portable raw-byte inverse history, and managed affected gaps. |
| `skills/agent-brain/scripts/agent_brain/maintenance.py` | Finite UTC review targets, complete bounded batches, current checked dispositions/credits, and reference-aware operational cleanup. |
| `skills/agent-brain/schemas/` lifecycle schemas | `integration-event-v1.schema.json`, `review-v1.schema.json`, `proposal-v1.schema.json`, `fixture-support-v1.schema.json`, and `lifecycle-result-v1.schema.json` define common event/review/proposal/result shapes; illustrative examples and procedure are bundled beside them. |
| `scripts/test-agent-brain-lifecycle.py` | Public-process lifecycle proof using disposable common-protocol registrations; includes binding, output, ownership, generations, children, interruption, and bounded checks/contention. |
| `scripts/test-agent-brain-publication.py` | Public-process/file proof for evidence, policy protection, relocation, source notes, raw inverse history, interrupted recovery, exclusive ownership, and incomplete output. |
| `skills/agent-brain/schemas/maintenance-v1.schema.json`, `examples/dream-review-v1.json` | Cycle/target/credit/batch/disposition records and an illustrative exact assigned review. |
| `scripts/test-agent-brain-maintenance.py` | Public-process/file proof for UTC cadence, finite current coverage, quiet progress, candidates, cleanup references, and recovery delivery. |
| `skills/agent-brain/scripts/agent_brain/source_ingestion.py` | Optional pinned canonical-engine boundary, current source evidence, semantic pre-pass bases, isolated proposal validation and checked mechanical settlement. No second freshness detector. |
| `skills/agent-brain/schemas/source-ingestion-v1.schema.json`, `examples/source-ingestion-v1.json` | Optional configured engine/bridge pins and current source/summary/knowledge plus orphan-review evidence shapes. |
| `scripts/test-agent-brain-compatibility.py` | Public bridge/CLI/generated-gate proof for joined source learning, reversible summary/KB publication, early delivery, drift, unavailable access and inactive legacy behavior. |
