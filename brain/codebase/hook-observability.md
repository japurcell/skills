# Hook observability

- SQLite is the trace source of truth; NDJSON is a best-effort compatibility fallback. Session and subagent finalization are distinct.
- Observability failures must not block agent work. Keep payload/command contents out of generic error messages.
- Database, WAL, SHM, locks, and rotated files require private permissions and link-safe handling.
- Keep bounded rotation and lock waits. Do not copy runtime logs during installation; preserve existing destination logs.
- Respect provider-specific environment precedence and stale-session cleanup.
- Remove stale active-session/transcript directories and registry entries only after 24 hours and when SQLite reports the session terminal or absent. The current helper also removes entries older than seven days even when SQLite reports an active session; this pre-existing implementation/policy conflict needs a separately scoped runtime repair, not silent policy retirement.
- When changing configuration, preserve emitter registration for every supported Copilot/Gemini event, including lifecycle events with no operational handler. Check the [Copilot config](../../.copilot/hooks/hooks.json) and [Gemini template](../../.gemini/global-settings.json); provider event support remains version-specific.
- Test copied provider-local scripts, retained stdin, trailing data, and UTF-8 output under Windows codepages.
- Rotation tests that exclude maintenance need the existing stale-maintenance sentinel fixture; avoid accidental maintenance changing their premise.
- For shared observability changes run both [Copilot observability tests](../../scripts/test-hooks-observability.sh) and [Gemini observability tests](../../scripts/test-gemini-hooks-observability.sh).

Evidence: [observability ADR](../../docs/adr/0003-sqlite-backed-hook-observability.md), `hooks/families/observability.py`, checked 2026-10-20. Recheck log lifecycle or maintenance changes. See [hook-testing](hook-testing.md).
