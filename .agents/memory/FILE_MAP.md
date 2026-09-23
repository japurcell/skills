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
| `.codex/` | hooks | Inactive source for user-global Codex startup, scanner, and Markdown hooks plus install-time configuration template. |
| `hooks/` | hooks | Canonical build-time renderers, provider metadata, and explicit generated-output ownership manifest. |
| `hooks/families/markdown_health.py` | hooks | Canonical Markdown checker and self-contained Copilot, Gemini, and Codex adapter renderer. |
| `skills/` | skills | One directory per skill, centered on `SKILL.md`; may include scripts, references, assets, evals, and grader tests (see skills instructions). |
| `agents/` | agents | Canonical Markdown custom-agent prompt files for Copilot, Gemini, and generated Codex TOML. |
| `docs/<effort>/` | repo docs | Active research and execution plans that need version history while work is in progress. |
| `docs/adr/` | repo docs | Human-facing ADRs that complement `.agents/` canonical guidance. |
| `scripts/` | scripts | Installers, importers, the aggregate test runner, validation helpers, and shared shell utilities. |
| `scripts/test-markdown-health.py`, `scripts/test-markdown-health-windows.ps1` | scripts | Public provider-hook checks and native Windows path coverage for Markdown health. |
| `references/` | references | Optional shared reference material shipped with installs. |

## Knowledge and top-level docs

| Path | Status | Purpose |
| --- | --- | --- |
| `.agents/instructions/` | canonical | Agent-facing workflow rules and area conventions. |
| `.agents/memory/` | canonical | Durable repo facts, file maps, testing routes, and known issues. |
| `docs/ideas.md` | companion | Lightweight inbox for one-line ideas that are not ready for research or planning. |
| `README.md` | companion | Repo overview and install entry point. |
| `AGENTS.md` | companion | Quickstart, loading contract, and top-level links for agents. |

## Key files

| Path | Why it matters |
| --- | --- |
| `scripts/install.sh` | Installs repo assets into `~/.agents`, `~/.copilot`, `~/.gemini`, and `~/.codex` targets, including generated Codex agents at `${CODEX_HOME:-$HOME/.codex}/agents`. |
| `scripts/install.ps1` | PowerShell 7 port of `scripts/install.sh`; same sources, destinations, exclusions, and installed layout, including `$CODEX_HOME/agents` when set (run with `pwsh scripts/install.ps1`). |
| `scripts/install-codex-agents.py` | Strict, transactional converter from top-level `agents/*.md` sources to manifest-managed personal Codex TOML agents. |
| `scripts/install-codex-hooks.py` | Atomically and idempotently merges exact maintained Codex `SessionStart`, `PreToolUse`, and `Stop` handlers into user-global `hooks.json`. |
| `scripts/test-codex-hooks-startup.sh` | Public-process contract and security regressions for the Codex required-skills hook. |
| `scripts/test-security-banners.py` | Public block, warning, excerpt, redaction, and fallback envelopes across three provider Tool Guardian adapters. |
| `.codex/hooks/tool-guard.py` | Generated Codex Tool Guardian adapter installed through the maintained hook merger. |
| `scripts/test-scan-secrets-capture.py` | Public generated-hook capture regressions shared by the three provider scanner suites. |
| `hooks/families/repository_state.py` | Canonical Git metadata and work-discard guard, rendered into provider-local pre-tool hooks. |
| `scripts/test-repository-state.py` | Public Copilot, Gemini, and Codex guard-envelope and registration tests. |
| `scripts/test-repository-state-windows.ps1` | Native Windows path, linked-worktree, PowerShell, and guard-envelope tests. |
| `scripts/test-scan-secrets-windows.ps1` | Native Windows generated-scanner capture suite used by the focused Windows workflow. |
| `scripts/test-install.ps1` | Fixture-repo test for `scripts/install.ps1` (run with `pwsh -NoProfile -File scripts/test-install.ps1`). |
| `scripts/import-skill-repos.sh` | Human-run multi-source importer that refreshes selected upstream skills, including the `web-*` quality skills. |
| `scripts/common.sh` | Shared shell helper for resolving repo root in small shell tests and utilities. |
| `scripts/test-all.py` | Executable aggregate test runner with an explicit maintained-suite registry; CLI contract is in `API_MAP.md`. |
| `scripts/generate-hooks.py` | Read-only freshness checker and transactional writer for the explicit `hooks/manifest.py` output set. |
| `scripts/test_test_all.py` | Public-process regressions for the aggregate runner, including streams, exit codes, preflight, and descendant cleanup. |
| `scripts/lint-okf.py` | Provider-neutral full-corpus OKF profile linter with human/JSON output and `0`/`1`/`2` exit semantics. |
| `scripts/test-okf-lint.sh` | Public-CLI contract suite for the OKF linter; copies the valid two-bundle fixture under `scripts/fixtures/okf-valid-repo/` for isolated mutation cases. |
| `.github/hooks/scripts/lint-okf.py` | Repo-local Copilot adapter for central OKF diagnostics on mutation and stop hooks. |
| `.github/hooks/scripts/validate-stop.py` | Repo-local Copilot stop coordinator that preserves source-ingest-first blocking reasons while running the independent OKF adapter. |
| `.gemini/hooks/scripts/lint-okf.py` | Repo-local Gemini adapter for central OKF diagnostics on mutation and final-response hooks. |
| `scripts/test-hooks-okf-lint.sh` | Copilot adapter contract, parity, failure, output-bound, and checkout-containment suite. |
| `scripts/test-gemini-hooks-okf-lint.sh` | Gemini adapter contract, parity, retry, failure, output-bound, and checkout-containment suite. |
| `scripts/vendor/` | Checked-in PyYAML 6.0.3 pure-Python runtime, source record, and license used only by the offline OKF linter. |
| `scripts/addy-install.sh` | Imports selected upstream addy skills, agents, and references into this repo. |
| `.agents/memory/sources/source-ingest-manifest.json` | Shared source-summary state file for Copilot and Gemini auto-ingest hooks plus pending-ingest gating. |
| `.agents/skills/okf-authoring/SKILL.md` | Repository-local representation workflow for canonical Markdown under `.agents/instructions/` and `.agents/memory/`; invoked one-way after `update-agent-docs` semantic changes. |
| `.copilot/hooks/rtk-rewrite.json` | Automatic RTK forwarder and explicit-command rewrite registrations for Copilot; generated adapters and launchers come from `hooks/families/rtk.py`. |
| `scripts/install-rtk-prerelease.py` | Checksum-verifies and installs the pinned RTK prerelease beside stable RTK, with a receipt used by explicit-command adapters. |
| `scripts/test-rtk-explicit-windows.ps1` | Native Windows archive, PowerShell rewrite, and diagnostic proof in the dedicated Windows workflow. |
| `docs/generated-provider-hooks/handoff.md` | Feature-scoped resume instructions for remaining deployed Gemini `AfterAgent` validation. |
| `docs/adr/0001-auto-ingest-runtime-shape.md` | Records why source auto-ingest uses runtime-local hook code with one committed repo manifest. |
| `docs/adr/0002-pending-ingest-gate.md` | Records why the pending-ingest gate blocks normal work until summaries resolve. |
| `docs/adr/0003-sqlite-backed-hook-observability.md` | Records why hook observability uses SQLite as source of truth with NDJSON fallback. |
| `docs/adr/0004-generated-provider-hooks.md` | Records why shared hook behavior will use canonical build-time sources while runtime scripts remain provider-local. |
| `.nvmrc` | Node version hint for local tooling. |
| `skills/skill-creator/scripts/quick_validate.py` | Narrow validation entry point for skill definitions. |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill directory into a distributable `.skill` archive. |
| `.agents/skills/ingest-source/SKILL.md` | The canonical repo-local `/ingest-source` recovery skill used by the pending-ingest gate. |
