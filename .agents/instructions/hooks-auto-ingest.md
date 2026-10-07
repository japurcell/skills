---
type: Agent Instruction
description: Source auto-ingest hook rules; load only when changing scanners, injectors, pending gates, summaries, or the manifest
---

# Hook Auto-Ingest Rules

Load this file only for source auto-ingest work. General hook contracts remain in [hooks.md](hooks.md).

- Keep startup scanners separate from required-skill loading. Copilot owns `.github/hooks/scripts/auto-ingest-source.py`, `.github/hooks/scripts/inject-auto-ingest-context.py`, and `.github/hooks/scripts/validate-stop.py`. Gemini owns `.gemini/hooks/scripts/auto-ingest.py` and `.gemini/hooks/scripts/inject-auto-ingest-context.py`; install still copies `.gemini/global-settings.json` to `~/.gemini/settings.json`.
- The generated auto-ingest engine and its GitHub/Gemini wrappers are maintained in `hooks/families/`; refresh their explicit manifest-owned outputs with `python3 scripts/generate-hooks.py --write` rather than editing runtime files directly. `validate-stop.py` remains a handwritten provider-local coordinator.
- Keep source state in `.agents/memory/sources/source-ingest-manifest.json`; keep executable helpers inside each runtime tree.
- Scaffold conforming draft `Source Summary` concepts. Quote dynamic YAML scalars and percent-encode `sources[].resource` paths while preserving `/`.
- Detect unresolved summaries from normalized top-level `type` and `status` scalar values. Ignore matching body text.
- Hold one platform-neutral `ManifestLock` across the complete read, reconcile, and save sequence.
- Stream source hashing in 64 KiB chunks.
- Catch scaffold `OSError` failures. Clean manifest `.tmp` files in `finally` after write or replace failures.
- Keep scanners, prompt-time injectors, and final-response backstops aligned on manifest schema, summary naming, pending-entry text, and source-ingest-first ordering.
- Keep startup summaries visible through the provider's native message envelope while leaving source paths and manifest detail in agent context or audit only. The Gemini `AfterAgent` pending gate reports pass, denial, and its allowed retry independently of the OKF adapter; its retry says the pending state was not rechecked.
- Use `.agents/skills/ingest-source/SKILL.md` as the only canonical recovery path; it must process every blocking entry in one run.
- Audit failures, injected findings with path/state/reason, and non-injection causes to the runtime-local audit log. Distinguish all-summaries-current from no-sources-found.

- Treat manifest `summary_path` as untrusted; reduce previous paths to `Path(summary_name).name` before joining below the summary directory.
- Preserve startup scanning, prompt injection, and final-response denial as distinct stages. Copilot prompt transformation may precede startup; use one stop coordinator to retain source-ingest-first reasons when OKF also fails.
- Gemini final-response enforcement belongs at `AfterAgent`; reserve `AfterModel` for per-output work. Keep the pending gate closed when recovery is unavailable, with the inline checklist as fallback.
- Apply [knowledge admission](knowledge-base.md) before promoting source material into the KB. A source summary may be complete without adding another policy or memory file.

For rationale, read the retained [runtime-shape decision](../../docs/adr/0001-auto-ingest-runtime-shape.md) or [pending-gate decision](../../docs/adr/0002-pending-ingest-gate.md) only when reconsidering those boundaries. Use [source-ingestion tests](testing/hooks-auto-ingest.md) for validation.
