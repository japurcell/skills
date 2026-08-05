---
coverage: Architectural Decision Records (ADRs) for `{.copilot,.gemini}/hooks`.
---

# Hooks - Architectural Decisions

This document records the architectural decision records (ADRs) for `{.copilot,.gemini}/hooks`.

## ADR-001: Python-first operational hook surface

- **Decision:** Wired operational hook entrypoints live in Python files owned by each runtime surface: installed Copilot hooks under `.copilot/hooks/scripts/`, repo-local Copilot startup auto-ingest under `.github/hooks/scripts/`, and Gemini hook entrypoints under `.gemini/hooks/scripts/`.
- **Rationale:** The PRD ports retained hook behavior to Python while letting Copilot startup auto-ingest run from repo-local hook config instead of installed global hooks.
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

## ADR-006: Runtime-local auto-ingest hooks with a shared repo manifest

- **Decision:** Source auto-ingest runs through dedicated startup hook scripts per runtime surface: Copilot repo-local startup auto-ingest under `.github/hooks/scripts/auto-ingest-source.py` and Gemini startup auto-ingest under `.gemini/hooks/scripts/auto-ingest.py`, while both runtimes read and write the same committed manifest at `.agents/memory/sources/source-ingest-manifest.json`.
- **Rationale:** The user wanted no cross-runtime shared executable hook code and no globally installed Copilot auto-ingest hook.
- **Consequences:** Copilot repo-local and Gemini runtime-local implementations stay separate, yet their manifest schema, summary naming contract, and embedded ingest prompt must stay aligned.
