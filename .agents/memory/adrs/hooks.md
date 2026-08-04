---
coverage: Architectural Decision Records (ADRs) for `{.copilot,.gemini}/hooks`.
---

# Hooks - Architectural Decisions

This document records the architectural decision records (ADRs) for `{.copilot,.gemini}/hooks`.

## ADR-001: Python-first operational hook surface

- **Decision:** Wired hook entrypoints live in runtime-local Python files under `.copilot/hooks/scripts/` and `.gemini/hooks/scripts/`.
- **Rationale:** The PRD ports retained hook behavior to Python so the installed surface can be validated directly.
- **Consequences:** Tests and config assertions target Python entrypoints; shell files are not the supported implementation surface.

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
