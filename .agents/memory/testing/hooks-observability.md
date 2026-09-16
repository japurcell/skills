---
type: Testing Guidance
description: Observability hook tests; load only for emitters, trace storage, transcript finalization, audit logs, rotation, or maintenance
---

# Hook Observability Testing

Run both suites for shared observability changes:

- `bash scripts/test-hooks-observability.sh`
- `bash scripts/test-gemini-hooks-observability.sh`

The suites exercise installed hook copies and validate event capture, span records, transcript rollup, lock-wait fail-open behavior, redaction and capping, rotation, and the kill switch. They keep stdin open after compact or multiline JSON, require prompt exit, reject buffered trailing data, verify owner-only primary and shadow logs, test runtime-specific variable precedence over generic fallbacks, and keep stale-backup pruning active when a zero-byte maximum disables rotation.

Use installed-path benchmarks for Gemini Tool Guardian; direct repo invocation can miss the `<40ms` target even when installed behavior passes.

For shared Python helpers, run `python scripts/test_helpers.py`. The tests cover path conversion, UTF-8 `emit_json`, path merging, frontmatter stripping, log sanitization, audit timeout and rotation, and payload-capping parity. Load modules with isolated `importlib.util.spec_from_file_location` objects to avoid `sys.modules` leakage. For stdout reconfiguration tests, wrap `io.BytesIO` in `io.TextIOWrapper` so `reconfigure(encoding="utf-8")` remains available under a simulated CP1252 stream.
