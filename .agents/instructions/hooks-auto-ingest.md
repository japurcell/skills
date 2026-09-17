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
- Use `.agents/skills/ingest-source/SKILL.md` as the only canonical recovery path; it must process every blocking entry in one run.
- Audit failures, injected findings with path/state/reason, and non-injection causes to the runtime-local audit log. Distinguish all-summaries-current from no-sources-found.

For architecture decisions, read [hooks ADRs](../memory/adrs/hooks.md). For failures and recovery, read [auto-ingest known issues](../memory/known-issues/hooks-auto-ingest.md). For tests, read [auto-ingest hook testing](../memory/testing/hooks-auto-ingest.md).
