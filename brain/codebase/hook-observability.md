# Hook observability

- Shared RTK/startup helpers retain hook capture after removal of the standalone event emitter. SQLite is the trace source of truth; NDJSON is a best-effort compatibility fallback. Session and subagent finalization are distinct.
- Observability failures must not block agent work. Keep payload/command contents out of generic error messages.
- Database, WAL, SHM, locks, and rotated files require private permissions and link-safe handling.
- Keep bounded rotation and lock waits. Do not copy runtime logs during installation; preserve existing destination logs.
- Respect provider-specific environment precedence and stale-session cleanup.
- Remove stale active-session/transcript directories and registry entries only after 24 hours and when SQLite reports the session terminal or absent. The current helper also removes entries older than seven days even when SQLite reports an active session; this pre-existing implementation/policy conflict needs a separately scoped runtime repair, not silent policy retirement.
- Test copied provider-local scripts, retained stdin, trailing data, and UTF-8 output under Windows codepages.
- Rotation tests that exclude maintenance need the existing stale-maintenance sentinel fixture; avoid accidental maintenance changing their premise.

Evidence: [observability ADR](../../docs/adr/0003-sqlite-backed-hook-observability.md), `hooks/families/observability.py`, checked 2026-10-20. Recheck log lifecycle or maintenance changes. See [hook-testing](hook-testing.md).

- Verify retained hook capture through the [Copilot RTK suite](../../scripts/tests/hooks/test-hooks-rtk.sh) and [Gemini RTK suite](../../scripts/tests/hooks/test-gemini-hooks-rtk.sh). Standalone emitter registrations and their suites were removed.
