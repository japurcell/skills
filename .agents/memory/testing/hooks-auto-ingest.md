---
type: Testing Guidance
description: Auto-ingest hook tests; load only for source scanners, prompt injectors, pending gates, summaries, or manifest behavior
---

# Hook Auto-Ingest Testing

Run both suites for shared contract changes:

- `bash scripts/test-hooks-auto-ingest.sh`
- `bash scripts/test-gemini-hooks-auto-ingest.sh`

For canonical auto-ingest renderer changes, also run `python3 scripts/test-generate-hooks.py` and a read-only `python3 scripts/generate-hooks.py --check` after regeneration. The six generated engine/wrapper targets remain runtime-local; `.github/hooks/scripts/validate-stop.py` is not generated.

The suites cover new-source scaffolding, stale summaries, renames, deleted-source prompts, committed manifest updates, pending-ingest gates, missing-skill recovery, and final-response backstops. They also verify exact OKF draft frontmatter, semantic quoted or commented draft scalars, body-marker exclusion, safe manifest summary paths, and encoded resources for nested paths containing spaces, `#`, or `?`.

Configured agent-brain source integration also uses `PYTHONWARNINGS=error::ResourceWarning python3 scripts/test-agent-brain-compatibility.py`; [scripts testing](scripts.md) owns its joined foreground semantics, public artifact/inverse, drift, linked-path and damaged-input assertions. Both legacy suites remain mandatory to preserve basename sanitization and global/inactive behavior. Simulated Windows byte-lock tests are offline branch proof only.

Copilot-specific coverage includes repo-local `userPromptTransformed` rewriting and the registered final-response coordinator. After injector or ordering changes, smoke-test `.github/hooks/scripts/inject-auto-ingest-context.py` directly.

Gemini-specific coverage includes `SessionStart` scanning, `BeforeAgent` injection, `AfterAgent` denial, missing-`cwd` fallback, and workspace-relative commands in `.gemini/settings.json`. Installed global settings continue to use quoted `$HOME/.gemini/hooks/scripts/...` paths.
