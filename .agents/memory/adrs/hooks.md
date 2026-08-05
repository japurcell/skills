---
coverage: Architectural Decision Records (ADRs) for `{.copilot,.gemini}/hooks`.
---

# Hooks - Architectural Decisions

This document records the architectural decision records (ADRs) for `{.copilot,.gemini}/hooks`.

## ADR-001: Python-first operational hook surface

- **Decision:** Wired operational hook entrypoints live in Python files owned by each runtime surface: Copilot auto-ingest lives entirely under `.github/hooks/scripts/`, installed Copilot hooks stay under `.copilot/hooks/scripts/` for the non-auto-ingest surface, and Gemini hook entrypoints live under `.gemini/hooks/scripts/`.
- **Rationale:** The PRD ports retained hook behavior to Python while moving all Copilot auto-ingest wiring into repo-local hook config instead of installed global hooks.
- **Consequences:** Tests and config assertions target Python entrypoints at their active runtime locations; shell files are not the supported implementation surface.

## ADR-002: Local structured observability via NDJSON emitter

- **Decision:** Each runtime owns a local `send-event.py` emitter plus append-only NDJSON logs under `$HOME/.copilot/hooks/logs/observability.ndjson` and `$HOME/.gemini/hooks/logs/observability.ndjson`.
- **Rationale:** The PRD requires local-only observability that does not alter control flow and stays best-effort.
- **Consequences:** Observability uses bounded-lock, fail-open writes, redaction, size caps, and a runtime kill-switch without affecting operational hooks.

## ADR-003: Hot-path hook subprocess safety

- **Decision:** Hot-path hooks use list-based subprocess calls only; `shell=True` is prohibited.
- **Rationale:** The port must preserve runtime behavior while avoiding shell interpolation risk and keeping hook execution bounded.
- **Consequences:** Python entrypoints forward stdin payloads in memory and tests cover invalid-input and failure fallback paths.

## ADR-004: Parser strategy for required skills and diff scanning

- **Decision:** Required-skill blocks and diff-based secret scans use line-oriented parsing/state machines instead of large multi-line regexes.
- **Rationale:** The PRD calls out exact delimiters, diff-only suppression, and predictable performance on hook hot paths.
- **Consequences:** Parsers stay narrow and deterministic, and tests assert delimiter handling plus unchanged-secret suppression.

## ADR-005: Hot-path latency budget

- **Decision:** Hot-path hooks such as Copilot `preToolUse` and Gemini `BeforeTool` must stay under a 40ms startup budget on a normal local machine.
- **Rationale:** The PRD sets an explicit performance target for the safety hooks that run on every tool invocation.
- **Consequences:** Benchmark the installed surface, keep imports lean, and prefer the fastest supported invocation path even if it differs from direct repo execution.

## ADR-006: Runtime-local auto-ingest scanners with prompt-time injectors and one shared repo manifest

- **Decision:** Source auto-ingest keeps dedicated startup scanners per runtime surface, but pairs them with prompt-time injectors that target the first planning turn and final-response backstops that block unresolved pending entries. Copilot keeps all three pieces repo-local under `.github/hooks/hooks.json` plus `.github/hooks/scripts/auto-ingest-source.py` and `.github/hooks/scripts/inject-auto-ingest-context.py`; Gemini keeps both repo-local under `.gemini/hooks/scripts/auto-ingest.py` and `.gemini/hooks/scripts/inject-auto-ingest-context.py`. Both runtimes still read and write the same committed manifest at `.agents/memory/sources/source-ingest-manifest.json`.
- **Rationale:** Startup scanning alone materializes scaffolds and the manifest, but it does not reliably reach the first model-facing turn or block the final answer across both runtimes. The user wanted no cross-runtime shared executable hook code and no globally installed Copilot auto-ingest wiring.
- **Consequences:** Copilot repo-local and Gemini runtime-local implementations stay separate, yet their manifest schema, summary naming contract, and embedded `/ingest-source` workflow text must stay aligned.

### Current auto-ingest flow

```text
Raw source changes under .agents/sources/*
                |
                v
Startup scanner runs
- Copilot: .github/hooks/scripts/auto-ingest-source.py
- Gemini:  .gemini/hooks/scripts/auto-ingest.py
                |
                v
Reconcile state
- detect new / modified / renamed / deleted sources
- scaffold missing summaries
- preserve orphan summaries
                |
                v
Persist shared repo state
.agents/memory/sources/source-ingest-manifest.json
                |
                +-------------------------------+
                |                               |
                v                               v
      scaffold summaries              audit / observability logs
                |
                v
First real planning turn
                |
                +-------------------------------+
                |                               |
                v                               v
Copilot prompt-time/backstop hook    Gemini prompt-time injector
userPromptTransformed/agentStop/subagentStop  BeforeAgent/AfterModel
.github/hooks/scripts/               .gemini/hooks/scripts/
inject-auto-ingest-context.py        inject-auto-ingest-context.py
                |                               |
                +---------------+---------------+
                                |
                                v
Inject current /ingest-source workflow + stale-source list
into model-facing context
                                |
                                v
Agent performs ingest work and updates summaries/docs
                                |
                                v
Manifest entries return to active / up-to-date state
```

- **Stage split:** startup scanners perform persistent state work; prompt-time injectors ensure the first planning turn actually sees that work; final-response backstops block unresolved work if steering is bypassed.
- **Copilot ordering constraint:** `userPromptTransformed` can run before `sessionStart`, so `sessionStart` output alone is not enough to guarantee first-turn ingest context.
- **Gemini pairing rule:** keep `SessionStart` scanning and `BeforeAgent` injection aligned so Gemini sees the same current stale-source list that the scanner persisted, and `AfterModel` keeps the gate closed when pending entries remain.

## ADR-007: Pending-ingest gate blocks normal work until summaries are truly resolved

- **Decision:** When the shared source-ingest manifest contains `needs_summary` or `stale` entries, both runtimes must block normal work on every applicable turn until those entries clear and their summaries are no longer scaffolds. Hooks should steer early with a short `/ingest-source` directive plus a pending-entry list, then backstop at final-response time so advisory prompt injection cannot be bypassed by normal answers.
- **Rationale:** Live evidence showed startup scanning and prompt injection already worked, but the model could still answer the user first. A manifest-derived gate gives one source of truth, preserves cross-runtime parity, and keeps the recovery path deterministic.
- **Consequences:** `/ingest-source` must become a real skill that processes all blocking entries in one run. User-facing bypasses stay disallowed, while test and debug-only bypass configuration remains available. If the skill is unavailable, the gate stays active and falls back to an inline recovery checklist rather than silently allowing unrelated work.
